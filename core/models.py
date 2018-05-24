# coding=utf-8
from django.db import models


# Create your models here.
class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# 式神model
class Hellspawn(BaseModel):
    rarity_choice = [(1, 'SSR'),
                     (2, 'SR'),
                     (3, 'R'),
                     (4, 'N')]

    name = models.CharField('名字', max_length=20)
    name_pinyin = models.CharField(max_length=128, default='')
    name_abbr = models.CharField(max_length=10, default='')
    rarity = models.IntegerField('稀有度', choices=rarity_choice, default=4)
    picture = models.CharField(max_length=128, null=True, blank=True)
    icon = models.CharField(max_length=128, null=True, blank=True)
    clue1 = models.CharField(max_length=30, null=True, blank=True)
    clue2 = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return '{0}-{1}'.format(self.name, self.rarity_choice[self.rarity-1][1])

    class Meta:
        verbose_name = '英雄'
        verbose_name_plural = '英雄'


# 式神出现的场景model
class Scene(BaseModel):
    name = models.CharField('场景', max_length=20)
    icon = models.CharField(max_length=128, null=True, blank=True)
    disable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '场景信息'
        verbose_name_plural = '场景信息'


class Team(BaseModel):
    name = models.CharField('小队名称', max_length=20)
    monsters = models.ManyToManyField(Hellspawn, related_name='hellspawn_teams', through='Membership',
                                      through_fields=('team', 'hellspawn'))
    belong = models.ForeignKey(Scene, related_name='scene_teams', on_delete=models.CASCADE)
    index = models.IntegerField(default=0)

    def __str__(self):
        return '{0}: {1}'.format(self.belong.name, self.name)

    class Meta:
        verbose_name = '小队信息'
        verbose_name_plural = '小队信息'


class Secret(BaseModel):
    secret = models.CharField(max_length=255, unique=True)
    remark = models.CharField(default='web', max_length=10)

    def __str__(self):
        return self.remark


class Membership(BaseModel):
    team = models.ForeignKey(Team, verbose_name='小队', on_delete=models.CASCADE, null=True, blank=True)
    hellspawn = models.ForeignKey(Hellspawn, verbose_name='英雄', on_delete=models.CASCADE)
    count = models.IntegerField('数量', default=1)

    def __str__(self):
        return '{0}X{1} - {2}{3}'.format(self.hellspawn.name, self.count, self.team.belong.name, self.team.name)

    class Meta:
        verbose_name = '英雄小队关系表'
        verbose_name_plural = '英雄小队关系表'


class WeUser(BaseModel):
    openid = models.CharField(max_length=128, unique=True)
    session = models.CharField(max_length=255, unique=True)
    weapp_session = models.CharField(max_length=255, unique=True)
    nick = models.CharField(max_length=50, default='')
    avatar = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.nick or self.openid


class Feedback(BaseModel):
    feed_choices = [(1, '数据有误'),
                   (2, '修改建议')]

    content = models.TextField()
    feed_type = models.IntegerField(choices=feed_choices, default=1)
    scene = models.ForeignKey(Scene, null=True, blank=True, on_delete=models.CASCADE)
    form_id = models.CharField(max_length=128, default='')
    handle = models.BooleanField(default=False)
    send = models.BooleanField(default=False)
    reply = models.CharField(max_length=128, default='您的反馈我们已经收到,及时为您处理')
    author = models.ForeignKey(WeUser, related_name='my_feedbacks', null=True, blank=True,
                               on_delete=models.CASCADE)

    def __str__(self):
        if self.scene:
            return '{0}-{1}-{2}'.format(self.feed_choices[self.feed_choices-1][1], self.scene.name, self.handle)
        return '{0}-{1}'.format(self.feed_choices[self.feed_type-1][1], self.handle)
