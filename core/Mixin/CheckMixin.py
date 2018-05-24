# coding=utf-8

import hashlib
import datetime

from django.utils.timezone import get_current_timezone
from core.Mixin.StatusWrapMixin import INFO_EXPIRE, ERROR_PERMISSION_DENIED
from core.models import Secret


class CheckSecurityMixin(object):
    secret = None
    expire = datetime.timedelta(seconds=30)

    def get_current_secret(self):
        self.secret = Secret.objects.all()[0].secret
        return self.secret

    def check_expire(self):
        timestamp = int(self.request.GET.get('timestamp', 0))
        request_time = datetime.datetime.fromtimestamp(timestamp, tz=get_current_timezone())
        now_time = datetime.datetime.now(tz=get_current_timezone())
        if now_time - request_time > self.expire:
            self.message = '请求超时,请重新验证'
            self.status_code = INFO_EXPIRE
            return False
        else:
            return True

    def check_sign(self):
        timestamp = self.request.GET.get('timestamp', '')
        sign = str(self.request.GET.get('sign', '')).upper()
        check = str(hashlib.md5('{0}{1}'.format(timestamp, self.secret)).hexdigest()).upper()
        if check == sign:
            return True
        return False

    def wrap_check_sign_result(self):
        if not self.check_expire():
            self.message = 'sign 已过期'
            self.status_code = ERROR_PERMISSION_DENIED
            return False
        self.get_current_secret()
        result = self.check_sign()
        if not result:
            self.message = 'sign 验证失败'
            self.status_code = ERROR_PERMISSION_DENIED
            return False
        return True

    def get(self, request, *args, **kwargs):
        print("CheckMixin get.....................")
        # if not self.wrap_check_sign_result():
        #     return self.render_to_response(dict())
        return super(CheckSecurityMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        return super(CheckSecurityMixin, self).post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        return super(CheckSecurityMixin, self).put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        return super(CheckSecurityMixin, self).patch(request, *args, **kwargs)
