# coding=utf-8

import random
import string

from django.views.generic import ListView, DetailView
from django.db.models import Q

from core.Mixin.CheckMixin import CheckSecurityMixin
from core.Mixin.JsonRequestMixin import JsonRequestMixin
from core.Mixin.StatusWrapMixin import StatusWrapMixin
from core.Mixin import StatusWrapMixin as SW
from core.dss.Mixin import MultipleJsonResponseMixin, JsonResponseMixin
from core.models import Hellspawn, Scene, Team, Membership, Feedback, WeUser
from django.core.cache import cache
from core.wechat import get_session_key


# Create your views here.
class HellspawnListView(CheckSecurityMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = Hellspawn
    include_attr = ['id', 'name', 'rarity', 'name_pinyin']


class HellspawnListOfRarity(CheckSecurityMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = Hellspawn

    def get(self, request, *args, **kwargs):
        hells = []
        for rarity in Hellspawn.rarity_choice:
            hells_of_rarity = list(Hellspawn.objects.filter(rarity=rarity[0]))
            hells.append(hells_of_rarity)

        return self.render_to_response({'hellspawn_list': hells})


class HellspawnDetailView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    model = Hellspawn
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super(HellspawnDetailView, self).get_object(queryset)
        cache.set(obj.id, obj.name, 60 * 60 * 6)
        return obj


class SceneListView(CheckSecurityMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = Scene
    many = True
    foreign = True
    paginate_by = 10

    def get(self):
        queryset = super(SceneListView, self).get_queryset()
        map(lambda obj: setattr(obj, 'team_list', obj.scene_teams.all()), queryset)
        return queryset


class SceneDetailView(CheckSecurityMixin, StatusWrapMixin, JsonRequestMixin, DetailView):
        model = Scene
        pk_url_kwarg = 'id'


class SearchListView(CheckSecurityMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = Hellspawn

    def get_queryset(self):
        value = self.request.GET.get('value', '')
        queryset = super(SearchListView, self).get_queryset()
        queryset = queryset.filter(Q(name__icontains=value) | Q(clue1__icontains=value) |
                        Q(clue2__icontains=value) | Q(name_pinyin__icontains=value) |
                        Q(name_abbr__icontains=value))
        return queryset


class HellspawnSceneListView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, ListView):
    model = Scene
    many = True

    exclude_attr = ['create_time', 'update_time']

    def get(self, request, *args, **kwargs):
        hellspawns = Hellspawn.objects.filter(id=kwargs.get('id'))
        if not hellspawns.exists():
            self.message = '英雄的id不存在'
            self.status_code = SW.INFO_NO_EXIST
            return self.render_to_response({})
        hellspawn = hellspawns[0]
        print("寻找的英雄是..........", hellspawn.name, hellspawn.id)
        teams = Team.objects.filter(monsters=hellspawn)
        scenes = []
        # find scenes which include teams
        scenes = list(Scene.objects.filter(scene_teams__in=teams, disable=False).distinct())
        # for team in teams:
        #     if not team.belong.disable:
        #         scenes.append(team.belong)
        # scenes = set(scenes)
        for scene in scenes:
            team_list = Team.objects.filter(belong=scene)
            setattr(scene, 'team_list', team_list)
            hellspawn_count_of_scene = 0
            for team in team_list:
                mems = Membership.objects.filter(team=team, hellspawn=hellspawn)
                if mems.exists():
                    mem = mems[0]
                    hellspawn_count_of_scene += mem.count
            setattr(scene, 'hellspawn_info', {'name': hellspawn.name, 'count': hellspawn_count_of_scene})
        return self.render_to_response(
            {'scene_list': sorted(scenes, key=lambda x: x.hellspawn_info['count'], reverse=True)}
        )


class FeedbackView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, JsonRequestMixin, DetailView):
    model = Feedback
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        # if not self.wrap_check_sign_result():
        #     return self.render_to_response({})

        content = request.POST.get('content')
        session = request.POST.get('session', None)
        user = WeUser.objects.filter(session=session)
        if content:
            is_advice = True if request.POST.get('is_advice') == 'true' else False
            scene_id = request.POST.get('scene_id')
            form_id = request.POST.get('form_id', '')
            new_feedback = Feedback(content=content)
            new_feedback.form_id = form_id
            new_feedback.feed_type = 2 if is_advice else 1
            if user.exists():
                new_feedback.author = user[0]
            if scene_id:
                scenes = Scene.objects.filter(id=scene_id)
                if scenes.exists():
                    new_feedback.scene = scenes[0]
            new_feedback.save()
            return self.render_to_response({})
        self.message = '参数缺失'
        self.status_code = SW.ERROR_DATA
        return self.render_to_response({})


class PopularListView(CheckSecurityMixin, StatusWrapMixin, MultipleJsonResponseMixin, ListView):
    model = Hellspawn
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        key_list = cache.keys('*')
        if 'access_token' in key_list:
            key_list.remove('access_token')
        if key_list:
            if len(key_list) > 8:
                key_list = key_list[:8]
            popular_list = []
            for itm in key_list:
                key_dict = {'id': itm, 'name': cache.get(itm)}
                popular_list.append(key_dict)
            return self.render_to_response({'popular_list': popular_list})
        return self.render_to_response({'popular_list': []})


class UserAuthView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, JsonRequestMixin, DetailView):
    model = WeUser
    http_method_names = ['post', 'get']

    def generate_session(self, count=64):
        letter = string.ascii_letters + string.digits + string.ascii_lowercase
        ran = string.join(random.sample(letter, count)).replace(" ", "")
        return ran

    def get(self, request, *args, **kwargs):
        session = request.GET.get('session')
        user = WeUser.objects.filter(session=session)
        if user.exists():
            return self.render_to_response({})
        self.message = 'session 已过期或不存在'
        self.status_code = SW.ERROR_PERMISSION_DENIED
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code', None)
        if code:
            status, openid, session = get_session_key(code)
            if status:
                my_session = self.generate_session()
                user = WeUser.objects.filter(openid=openid)
                if user.exists():
                    user = user[0]
                    user.weapp_session = session
                    user.session = my_session
                    user.save()
                else:
                    WeUser(openid=openid, weapp_session=session, session=my_session).save()
                return self.render_to_response({'session': my_session})
            self.message = 'code 错误'
            self.status_code = SW.ERROR_VERIFY
            return self.render_to_response({})
        self.message = 'code 缺失'
        self.status_code = SW.INFO_NO_EXIST
        return self.render_to_response({})


class UserView(CheckSecurityMixin, StatusWrapMixin, JsonRequestMixin, JsonResponseMixin, DetailView):
    model = WeUser
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        session = request.POST.get('session')
        user = WeUser.objects.filter(session=session)
        if user.exists():
            user = user[0]
            if not user.nick:
                user.nick = request.POST.get('nick')
                user.avatar = request.POST.get('avatar')
                user.save()
            return self.render_to_response({})
        self.message = 'session 已过期或不存在'
        self.status_code = SW.ERROR_PERMISSION_DENIED
        return self.render_to_response({})
