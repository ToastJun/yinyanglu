# coding=utf-8

from django.http import HttpResponse

# Info Code
ERROR_UNKNOWN = 0
INFO_SUCCESS = 1
ERROR_PERMISSION_DENIED = 2
ERROR_ACCOUNT_NO_EXIST = 3
ERROR_TOKEN = 3
ERROR_DATA = 4
ERROR_PASSWORD = 5
INFO_EXISTED = 6
INFO_NO_EXIST = 7
INFO_EXPIRE = 8
INFO_NO_VERIFY = 10
ERROR_VERIFY = 11
INFO_NO_MATCH = 20
INFO_ROOM_DESTROY = 21


class StatusWrapMixin(object):
    status_code = INFO_SUCCESS
    message = 'success'

    def render_to_response(self, context, **response_kwargs):
        print("StatusWrapMixin_render_to_response......")
        context_dict = self.context_serialize(context)
        json_context = self.json_serializer(self.wrapper(context_dict))
        return HttpResponse(json_context, content_type='application/json', **response_kwargs)

    def wrapper(self, context):
        return_data = dict()
        return_data['data'] = context
        return_data['status'] = self.status_code
        return_data['msg'] = self.message
        if self.status_code != INFO_SUCCESS and self.status_code != INFO_NO_MATCH:
            return_data['data'] = {}
        return return_data


class AdminStatusWrapMixin(StatusWrapMixin):
    def wrapper(self, context):
        data = super(AdminStatusWrapMixin, self).wrapper(context)
        if isinstance(self.message, str):
            data['msg'] = {'message': self.message}
            return data
        error_data = {}
        if isinstance(self.message, list):
            for item in self.message:
                error_data[item[0]] = item[1]
        if isinstance(self.message, dict):
            for key, value in self.message.items():
                error_data[key] = value
        data['msg'] = error_data
        return data
