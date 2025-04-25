# -- coding: utf-8 --

import json
import re
import requests
from utils.common_util.log_util import logger


class RequestUtils:
    @staticmethod
    def requests_get(url, data=None, headers=None):
        logger.debug("发起get请求,URL[{}],参数:{}".format(url, data))
        if headers is not None:
            response = requests.get(url=url, data=data, headers=headers, timeout=RequestUtils.get_timeout({}))
        else:
            response = requests.get(url=url, data=data, timeout=RequestUtils.get_timeout({}))
        logger.debug("响应:" + response.text)

        return json.loads(response.text).get('data')

    @staticmethod
    def requests_json_get(url, data):
        logger.debug("发起get请求,URL[{}],参数:{}".format(url, data))
        response = requests.get(url=url, data=json.dumps(data), headers={
                                "Content-Type": "application/json"}, timeout=RequestUtils.get_timeout(data))

        response_test = response.content.decode(response.apparent_encoding)
        logger.debug("响应:" + response_test)
        return json.loads(response_test)

    @staticmethod
    def requests_no_data_get(url):
        logger.debug("发起get请求,URL[{}]".format(url))
        response = requests.get(url=url, timeout=RequestUtils.get_timeout({}))
        logger.debug("响应:" + response.text)
        return json.loads(response.text)

    @staticmethod
    def requests_data_cookies_get(url, data, cookies):
        logger.debug("发起post请求,URL[{}],参数:None".format(url))
        if data:
            response = requests.get(url=url, data=json.dumps(data), headers={
                                    "Content-Type": "application/json"}, cookies=cookies, timeout=RequestUtils.get_timeout(data))
        else:
            response = requests.get(url=url, cookies=cookies, timeout=RequestUtils.get_timeout(data))
        logger.debug("响应:" + response.text)
        return json.loads(response.text)

    @staticmethod
    def get_timeout(data: dict):
        http_timeout = 120
        if 'args' in data.keys():
            args_value = dict(data['args'])
            if 'SyncTimeOut' in args_value.keys():
                http_timeout = args_value['SyncTimeOut']

        return http_timeout

    @staticmethod
    def requests_post(url, data: dict, headers=None):
        logger.debug("发起post请求,URL[{}],参数:{}".format(url, data))
        http_timeout = RequestUtils.get_timeout(data)
        if headers is not None:
            response = requests.post(url=url, data=json.dumps(data), timeout=http_timeout, headers=headers)
        else:
            response = requests.post(url=url, data=json.dumps(data), timeout=http_timeout,
                                     headers={"Content-Type": "application/json"})
        logger.debug("响应:" + response.text)
        return json.loads(response.text).get('data')

    @staticmethod
    def requests_delete(url):
        logger.debug('发起Delete请求,URL[{}]'.format(url))
        response = requests.delete(url=url, timeout=120)

        response_test = response.content.decode(response.apparent_encoding)
        logger.debug("响应:" + response_test)
        return json.loads(response_test)

    @staticmethod
    def requests_no_data_post(url):
        logger.debug("发起post请求,URL[{}],参数:None".format(url))
        response = requests.post(url=url, timeout=120, headers={"Content-Type": "application/json"})
        logger.debug("响应:" + response.text)
        return json.loads(response.text)

    @staticmethod
    def requests_data_cookies_post(url, data, cookies):
        logger.debug("发起post请求,URL[{}],参数:None".format(url))
        response = requests.post(url=url, data=json.dumps(data), timeout=120, headers={
                                 "Content-Type": "application/json"}, cookies=cookies)
        logger.debug("响应:" + response.text)
        return json.loads(response.text)

    @staticmethod
    def requests_json_post(url, data, headers=None):
        if headers is None:
            headers = {"Content-Type": "application/json"}

        http_timeout = RequestUtils.get_timeout(data)
        logger.debug("发起post请求,URL[{}],参数:{}".format(url, data))
        response = requests.post(url=url, data=json.dumps(data), timeout=http_timeout, headers=headers)

        response_test = response.content.decode(response.apparent_encoding)
        logger.debug("响应:" + response_test)
        return json.loads(response_test)

    @staticmethod
    def requests_json_put(url, data):
        logger.debug("发起put请求,URL[{}],参数:{}".format(url, data))
        response = requests.put(url=url, data=json.dumps(data), headers={"Content-Type": "application/json"}, timeout=120)

        response_test = response.content.decode(response.apparent_encoding)
        logger.debug("响应:" + response_test)
        return json.loads(response_test)

    @staticmethod
    def get_json_from_url(url: str) -> str:
        """从URL文件中获取json"""
        return json.loads(RequestUtils.get_content_from_url(url))

    @staticmethod
    def get_content_from_url(url: str) -> str:
        """从URL文件中获取文本内容"""
        if re.match(r'^https?:/{2}\w.+$', url):
            s = requests.get(url, timeout=120)
            return s.content.decode(s.apparent_encoding)
        else:
            raise RuntimeError("args不合法，请填写正确的URL")
