# coding=utf-8

import requests
import json

APP_KEY = 'wx99046f3d695da344'
APP_SECRET = 'ba05f96a4e3109df23b8a75c755325ed'


def get_access_token():
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}".format(
        APP_KEY, APP_SECRET)
    res = requests.get(url).content
    json_data = json.load(res)
    access_token = json_data.get("access_token", None)
    return access_token


def send_template_message(access_token):
    url = "https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={0}".format(access_token)



def get_session_key(code):
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code".format(
        APP_KEY, APP_SECRET, code)
    res = requests.get(url).content
    json_data = json.load(res)
    openid = json_data.get('openid', None)
    session = json_data.get('session_key', None)
    if openid and session:
        return True, openid, session
    return False, None, None