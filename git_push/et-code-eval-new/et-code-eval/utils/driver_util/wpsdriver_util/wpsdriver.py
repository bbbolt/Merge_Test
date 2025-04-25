# -- coding: utf-8 --
from utils.common_util.exceptions import ParameterIncorrectError, ExecuteFailedError
from utils.common_util.log_util import logger
from utils.common_util.request_util import RequestUtils
from utils.driver_util.wpsdriver_util.action_list import ActionInfo, PoActionList
from utils.driver_util.wpsdriver_util.enums import AppType, WpsDriverPort


class WpsDriver:
    def __init__(self, server_url, app_type, instance_index=0):
        if instance_index == 1:
            app_type = AppType.WPS_INSTANCE_ONE.value
        elif instance_index == 2:
            app_type = AppType.WPS_INSTANCE_TWO.value
        elif instance_index == 3:
            app_type = AppType.WPS_INSTANCE_THREE.value

        self.__driver_url = server_url + ":" + WpsDriverPort.port_dict[app_type]
        self.__session_id = None

    @property
    def session_id(self):
        self.__session_id = self.__remote()
        return self.__session_id

    @property
    def driver_url(self):
        return self.__driver_url

    @property
    def __get_session_url(self) -> str:
        session_url = self.driver_url + '/session/' + self.session_id

        return session_url

    def __remote(self):
        if self.driver_url is None:
            return None

        url = self.driver_url + '/session'
        data = RequestUtils.requests_no_data_post(url)
        if data is None:
            raise ParameterIncorrectError('连接wps driver异常，url:[{}]'.format(self.driver_url))

        return data.get('value').get("sessionId")

    def call_action(self, action_name: str, args=None):
        if args is None:
            args = {}
        try:
            action_info = PoActionList.get_action(action_name)
            if action_info is None:
                raise ParameterIncorrectError(f'{action_name}动作不存在')

            url = self.__get_session_url + action_info.url_suffix
            res_data = self.request_po_wps_driver(args, url, action_info.request_method)
        except ValueError:
            res_data = None

        return res_data

    @staticmethod
    def request_po_wps_driver(args, url, request_method):
        try:
            if request_method == "POST":
                res_data = RequestUtils.requests_json_post(url, args)
            elif request_method == "GET":
                res_data = RequestUtils.requests_json_get(url, args)
            elif request_method == "DELETE":
                res_data = RequestUtils.requests_delete(url)
            elif request_method == "PUT":
                res_data = RequestUtils.requests_json_put(url, args)
            else:
                raise ExecuteFailedError('调用Http异常[{}]'.format(url))

        except ValueError:
            raise ExecuteFailedError('调用Http异常[{}]'.format(url))
        return res_data


if __name__ == '__main__':
    print(PoActionList.get_action("QuitWps"))
    WpsDriver("http://127.0.0.1", 'ET').call_action("QuitWps", args={})
