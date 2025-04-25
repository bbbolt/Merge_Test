# -- coding: utf-8 --
from utils.common_util.log_util import logger


class ActionInfo(object):
    def __init__(self, action_name: str, desc: str, url_suffix: str, request_method: str):
        self.__action_name = action_name
        self.__desc = desc
        self.__url_suffix = url_suffix
        self.__request_method = request_method

    @property
    def action_name(self):
        """
        获取名称
        """
        return self.__action_name

    @property
    def desc(self):
        """
        获取备注
        """
        return self.__desc

    @property
    def url_suffix(self):
        """
        获取url后缀
        """
        return self.__url_suffix

    @property
    def request_method(self):
        """
        获取request_method
        """
        return self.__request_method


class PoActionList(ActionInfo):
    """
    pc office提供的动作清单及对应的url路径
    """
    NEW_SESSION_ACTION = ActionInfo("NewSession", "创建wps session", "/session", "POST")
    DEL_SESSION_ACTION = ActionInfo("DelSession", "移除wps session", "", "DELETE")
    EXECUTE_SCRIPT_ACTION = ActionInfo("ExecuteScript", "执行wps-js-api", "/execute/sync", "POST")
    EXECUTE_JSAPI_ACTION = ActionInfo("ExecuteJsapi", "执行wps-js-api(new)", "/execute/jsapi", "POST")
    EXECUTE_JSFILE_ACTION = ActionInfo("ExecuteJsFile", "执行wps-js-file(v8)", "/execute/jsfile", "POST")
    RUN_EXTEND_API_ACTION = ActionInfo("RunExtendApi", "执行wps-extend-api", "/runextendapi", "POST")
    START_STATISTICS = ActionInfo("StartStatistics", "执行StartStatistics", "/statistics/start", "POST")
    END_STATISTICS = ActionInfo("EndStatistics", "执行EndStatistics", "/statistics/end", "POST")
    GET_STATISTICS_RESULT = ActionInfo("GetStatisticsResult", "执行GetStatisticsResult", "/statistics/result", "POST")
    REPLAY_FILE_ACTION = ActionInfo("ReplayFile", "回放录制文件", "/qtspy/replay_file", "POST")
    START_RECORD_ACTION = ActionInfo("StartRecord", "开始录制", "/qtspy/start_record", "POST")
    STOP_RECORD_ACTION = ActionInfo("StopRecord", "停止录制", "/qtspy/stop_record", "POST")
    REPLAY_ACTION = ActionInfo("Replay", "回放", "/qtspy/replay", "POST")
    SCREENSHOT_ACTION = ActionInfo("ScreenShot", "截屏", "/widget/screenshot", "GET")
    GET_WIDGET_ACTION = ActionInfo("GetWidget", "获取控件属性", "/widget/property", "GET")
    QT_SPY_ENTRY_UIR = ActionInfo("QTSpyEntryUir", "执行入口动作", "/qtspy/replay_file", "POST")
    NEW_DOCUMENT = ActionInfo("NewDocument", "新建空白文档", "/window/new", "POST")
    OPEN_DOCUMENT = ActionInfo("OpenDocument", "打开文档", "/url", "POST")
    CHECK_WIDGET_EXIST = ActionInfo("CheckWidgetExist", "检查控件是否存在", "/widget/exist", "POST")
    EXPORT_VIEW_TO_PIC = ActionInfo("ExportViewToPic", "导出视图区坐标区域截图", "/exportviewpic", "POST")
    QUIT_WPS = ActionInfo("QuitWps", "退出WPS程序", "/quit", "POST")
    CHECK_WIDGET_PROPERTY = ActionInfo("CheckWidgetProperty", "检查控件属性", "/widget/checkproperty", "GET")
    EXECUTE_SCRIPT_V8_ACTION = ActionInfo("ExecuteJsapiV8", "执行wps-js-api-v8", "/execute/script/evaluate", "POST")
    CLOSE_ACTIVE_WINDOW = ActionInfo("CloseActiveWindow", "执行调用关闭当前活动文档的接口", "/window/closeactive", "POST")
    CHECK_APP_NAME = ActionInfo("CheckAppName", "检查当前激活的进程名", "/getActiveAppName", "GET")
    CHECK_OPENED_FILE_COUNT = ActionInfo("CheckOpenedFileCount", "检查当前App打开的文档个数", "/getOpenedFileCount", "GET")
    SET_SHOW_PLAYER_TOOLBAR = ActionInfo("SetShowPlayerToolbar", "显示放映视图的左下角工具栏", "/wpp/setShowPlayerToolBar", "POST")
    CLICK_WIDGET_BY_NAME = ActionInfo('ClickWidgetByName', "根据控件名称点击控件", '/qtspy/clickWidgetByName', 'POST')
    EXPORT_UI_COMMAND = ActionInfo('ExportUiCommand', "导出ui控件信息", '/exportUiCommand', 'POST')
    EXPORT_WIDGET_VIEW = ActionInfo('ExportWidgetView', "导出widget view到xml", '/qtspy/exportItemViewByName', 'POST')
    WPP_TRAVERSE = ActionInfo('WppTraverse', "Wpp浏览幻灯片", '/wppTraverse', 'GET')
    ET_SHEET_EXIST = ActionInfo("EtSheetExist", "检查sheet是否存在", "/checkIsSheetExist", "POST")
    IO_DUMP = ActionInfo("IoDump", "导出IO Dump数据", "/io_dump", "POST")

    @staticmethod
    def get_action(action_name):
        for key, action in vars(PoActionList).items():

            if ActionInfo.__instancecheck__(action) and action.action_name == action_name:
                return action

        logger.error("event类型不存在:{}".format(action_name))

    @staticmethod
    def get_url_suffix(action_name):
        action = PoActionList.get_action(action_name)
        if action is None:
            return None

        return action.url_suffix

    @staticmethod
    def get_request_method(action_name):
        action = PoActionList.get_action(action_name)
        if action is None:
            return None

        return action.request_method