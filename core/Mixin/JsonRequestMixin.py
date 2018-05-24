# coding=utf-8

import json


class JsonRequestMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            json_data = json.load(request.body)
            setattr(request, 'POST', json_data)
        except Exception as e:
            pass
        return super(JsonRequestMixin, self).dispatch(request, *args, **kwargs)
