import base64
import os
import platform
import signal
import subprocess
import time

import requests
from PIL import ImageGrab

from business.common.enums import OSType
from utils.common_util.log_util import logger
from utils.driver_util.wpsdriver_util.wpsdriver import WpsDriver

if platform.system() == OSType.PC_WINDOWS.value:
    import winreg


class ProductCommon:
    def __init__(self, component_name, url='http://127.0.0.1'):
        self.component_name = component_name
        self.url = url
        self.driver = WpsDriver(self.url, self.component_name)

    @staticmethod
    def get_wps_root_path():
        """win获取wps安装路径"""
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\kingsoft\Office\6.0\Common")
            value, _type = winreg.QueryValueEx(key, "InstallRoot")
            return value
        except FileNotFoundError:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\kingsoft\Office\6.0\Common")
            value, _type = winreg.QueryValueEx(key, "InstallRoot")
            return value

    @staticmethod
    def __get_win_wps_office6_path():
        access_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\kingsoft\Office\6.0\Common', 0,
                                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        install_root, _ = winreg.QueryValueEx(access_key, 'InstallRoot')
        winreg.CloseKey(access_key)

        return '{}\\office6'.format(install_root)

    @staticmethod
    def __get_linux_wps_office6_path():
        return '/opt/kingsoft/wps-office/office6'

    @staticmethod
    def __get_mac_wps_offie6_path():
        return 'com.kingsoft.wpsoffice.mac'

    def get_app_path(self) -> str:
        """获取应用类型获取应用安装目录"""
        wps_env_path = os.environ.get('WPS_ROOT', '')
        if os.path.exists(wps_env_path):
            return wps_env_path

        if platform.system() == OSType.PC_WINDOWS.value:
            return self.__get_win_wps_office6_path()
        elif platform.system() == OSType.PC_LINUX.value:
            return self.__get_linux_wps_office6_path()
        elif platform.system() == OSType.PC_MAC.value:
            return self.__get_mac_wps_offie6_path()
        else:
            print('CurrentSystem Not Support wps path:' + platform.system())
            return ''

    def get_wps_office6_path(self):
        wps_env_path = os.environ.get('WPS_ROOT', '')
        if os.path.exists(wps_env_path):
            return wps_env_path

        if platform.system() == OSType.PC_WINDOWS.value:
            return self.__get_win_wps_office6_path()
        elif platform.system() == OSType.PC_LINUX.value:
            return self.__get_linux_wps_office6_path()
        elif platform.system() == OSType.PC_MAC.value:
            return self.__get_mac_wps_offie6_path()
        else:
            print('CurrentSystem Not Support wps path:' + platform.system())
            return ''

    def __get_wps_full_path(self, wps_path):
        component_name = self.component_name.lower()
        if component_name == 'pdf':
            component_name = 'wpspdf'
        if platform.system() == OSType.PC_WINDOWS.value:
            full_path = os.path.join(wps_path, component_name + '.exe')
        elif platform.system() == 'Linux':
            full_path = os.path.join(wps_path, component_name)
        else:
            full_path = self.get_wps_office6_path()

        return full_path

    def set_hide_alerts(self):
        """设置关闭弹框"""
        hide_alerts_script = f'Application.DisplayAlerts=0'
        return self.driver.call_action(action_name='ExecuteJsapiV8', args={'script': hide_alerts_script})

    def launch_wps_component(self, cmd_array=''):
        if platform.system() != 'Darwin':
            if not os.path.exists(self.get_wps_office6_path()):
                print('ExeFile[{}]NotExist!'.format(self.get_wps_office6_path()))
                return False

        print('Start:{}'.format(self.get_wps_office6_path()))
        start_status = False
        if platform.system() == OSType.PC_WINDOWS.value:
            start_status = self.__open_windows_wps_process(self.get_wps_office6_path(), cmd_array)
        # elif platform.system() == OSType.PC_MAC.value:
        #     start_status = __open_mac_wps_process(ProductUtil.get_wps_office6_path(), component_name, cmd_array)
        # elif platform.system() == '':
        #     start_status = __open_linux_wps_process(ProductUtil.get_wps_office6_path(), component_name, cmd_array)
        else:
            print("UnSupport System:" + platform.system())

        if not start_status:
            return start_status
        return self.__check_wpsdriver()

    @staticmethod
    def check_et_status():
        """检查et wpsdriver是否启动"""
        try:
            requests.get('http://127.0.0.1:2022/status')
            return True
        except Exception:
            return False

    def __check_wpsdriver(self):
        component_name = self.component_name.lower()
        wps_url = ''
        if platform.system() == 'Darwin' or platform.system() == 'Windows':
            if 'wps' in component_name:
                wps_url = 'http://127.0.0.1:2021/status'
            elif 'pdf' in component_name:
                wps_url = 'http://127.0.0.1:2024/status'
            elif 'prome' in component_name:
                wps_url = 'http://127.0.0.1:2020/status'
            elif 'et' in component_name:
                wps_url = 'http://127.0.0.1:2022/status'
            elif 'wpp' in component_name:
                wps_url = 'http://127.0.0.1:2023/status'
        elif platform.system() == 'Linux':
            print('UnSupport Platform')

        print(wps_url)
        if wps_url == '':
            return False
        else:
            return self.__check_server_status(wps_url)

    def __check_server_status(self, str_url):
        bSuccess = False
        nWait = 0
        MAX_WAIT = 45
        while (not bSuccess) and nWait < MAX_WAIT:
            try:
                r = requests.get(str_url)
                if r.status_code == 200:
                    bSuccess = True
                else:
                    nWait = nWait + 1
                    time.sleep(1)
            except Exception as e:
                logger.warning('Wait 1 second for component to start', True)
                nWait = nWait + 1
                time.sleep(1)

        return bSuccess

    def __open_windows_wps_process(self, wps_path, cmd_array='') -> bool:
        full_path = self.__get_wps_full_path(wps_path)

        if cmd_array == '':
            if self.component_name == 'wps':
                execute_array = [full_path, '/wps']
            else:
                execute_array = [full_path]
        else:
            if self.component_name == 'wps':
                execute_array = [full_path, '/wps', cmd_array]
            else:
                execute_array = [full_path, cmd_array]
        sp = subprocess.Popen(args=execute_array, bufsize=0)
        if sp.pid is not None:
            self._pid = sp.pid
            return True
        else:
            return False

    def open_document(self, document_file):
        self.driver.call_action("OpenDocument", args={'url': document_file})

    def new_document(self):
        self.driver.call_action("NewDocument",args={})

    def _get_format_enum(self, file_format, map_name):
        if self.component_name in map_name:
            return map_name[self.component_name].get(file_format, None)
        return None

    SAVEAS_FORMAT_MAP = {
        'WPS': {
            'docx': 12, 'doc': 0, 'pdf': 17, 'txt': 4, 'rtf': 6, 'html': 8, 'mhtml': 9, 'xml': 11,
            'wps_xml': 7, 'wps_html': 10
        },
        'ET': {
            'xls': -4143, 'xlsx': 51, 'pdf': 57, 'csv': 6, 'txt': -4158, 'html': 44, 'xml': 46,
            'prn': 36, 'et_xml': 55, 'et_html': 54, 'dbf': 11
        },
        'WPP': {
            'pptx': 24, 'ppt': 1, 'pdf': 32, 'wmf': 2, 'jpg': 17, 'bmp': 18, 'png': 19, 'tif': 20,
            'gif': 21, 'emf': 23, 'rtf': 26, 'html': 27, 'xml': 28
        },
    }

    def save_as(self, file_format, save_path):
        """另存文件"""
        file_format_enum = self._get_format_enum(file_format, self.SAVEAS_FORMAT_MAP)
        dest_path = (save_path + '.' + file_format).replace('\\', '/')

        if self.component_name == 'WPS':
            return self.driver.call_action("ExecuteJsapiV8", args={
                'script': f'Application.ActiveDocument.SaveAs(\"{dest_path}\", {file_format_enum})'})
        elif self.component_name == 'ET':
            return self.driver.call_action("ExecuteJsapiV8", args={
                'script': f'Application.ActiveWorkbook.SaveAs(\"{dest_path}\", {file_format_enum})'})
        elif self.component_name == 'WPP':
            return self.driver.call_action("ExecuteJsapiV8", args={
                'script': f'Application.ActivePresentation.SaveAs(\"{dest_path}\", {file_format_enum})'})
        else:
            logger.waring(f"不支持{self.component_name}组件")
    
    def save(self):
        """保存文件"""
        if self.component_name == 'WPS':
            return self.driver.call_action("ExecuteJsapiV8", args={'script': f'Application.ActiveDocument.Save()'})
        elif self.component_name == 'ET':
            return self.driver.call_action("ExecuteJsapiV8", args={'script': f'Application.ActiveWorkbook.Save()'})
        elif self.component_name == 'WPP':
            return self.driver.call_action("ExecuteJsapiV8", args={'script': f'Application.ActivePresentation.Save()'})
        else:
            logger.waring(f"不支持{self.component_name}组件")

    def close_active_file(self, save_changes=False):
        """关闭当前活动文档"""
        close_fun = "Close()" if save_changes else "Close(false)"
        if self.component_name == 'WPS':
            return self.driver.call_action("ExecuteJsapiV8", args={'script': f'Application.ActiveDocument.{close_fun}'})
        elif self.component_name == 'ET':
            return self.driver.call_action("ExecuteJsapiV8", args={'script': f'Application.ActiveWorkbook.{close_fun}'})
        elif self.component_name == 'WPP':
            return self.driver.call_action("ExecuteJsapiV8", args={'script': f'Application.ActivePresentation.{close_fun}'})
        else:
            logger.waring(f"不支持{self.component_name}组件")

    def quit_wps(self):
        try:
            self.driver.call_action("QuitWps", args={})
        except Exception as e:
            logger.warning("退出进程失败:{}".format(e))

    @staticmethod
    def run_cmd(cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        res_list = p.stdout.readlines()
        return res_list

    def kill(self):
        if not self._pid:
            os.kill(self._pid, signal.SIGTERM)
            return

    def kill_et(self):
        cmd = 'taskkill /f /im et.exe /t'
        self.run_cmd(cmd)

    def kill_wps(self):
        cmd = 'taskkill /f /im wps.exe /t'
        self.run_cmd(cmd)

    def run_js_file(self, js_file, function_name, arg_list=None, out_times=60):
        args = {'jsFile': js_file,
                'runFunctionName': function_name,
                'SecondTimeout': out_times
                }
        if arg_list:
            for i, arg in enumerate(arg_list):
                args['arg{}'.format(i + 1)] = arg
        logger.info(f"运行js的args：\n {args}")
        return self.driver.call_action('ExecuteJsFile', args)

    def run_js_code(self, script):
        return self.driver.call_action('ExecuteJsapiV8', args={"script": script})

    def dump(self, checkpoint_xml_path, dict_xml_path, dump_save_path):
        result = self.driver.call_action("IoDump", args={'checkpointFileContent': checkpoint_xml_path,
                                                "specCollectionObjectContent": dict_xml_path,
                                                "resultXml": dump_save_path, 'limitConditionFileContent': '',
                                                         'originalFilePath': ''
                                                })
        # result = self.driver.call_action('IoDump', args={'checkpointFileContent': checkpoint_xml_path,
        #                             'specCollectionObjectContent': dict_xml_path,
        #                             'resultXml': dump_save_path, 'limitConditionFileContent': '',
        #                             'originalFilePath': ''})
        print(result)

    def screenshot_by_widget_name(self, save_path, widget_name='rootWidget'):
        save_path = save_path.replace('\\', '/')
        args = {'widgetName': widget_name,
                'ancestorWidgetName': '',
                'picture_path': save_path
                }
        res_data = self.driver.call_action("ScreenShot", args=args)
        picture_base64 = res_data.get('value')
        if isinstance(picture_base64, dict):
            return
        picture_data = base64.b64decode(picture_base64)
        with open(save_path, 'wb') as f:
            f.write(picture_data)

    def save_view_screenshot(self, save_path):
        save_path = save_path.replace('\\', '/')
        if self.component_name == 'ET':
            self.driver.call_action("ExportViewToPic",
                                    args={'range': 'A1:Z50',
                                          'file': save_path,
                                          'opt': 1,
                                          })
        elif self.component_name == 'WPP':
            self.driver.call_action("ExportViewToPic",
                                    args={"coords": "0,0:20000,11000", "picName": save_path,
                                          "viewName": "Normal1", "uilLayer": "ShapeTreeLayer"})

        elif self.component_name == 'WPS':
            self.driver.call_action("ExportViewToPic",
                                    args={"coords": "0,0:12000,17000", "picName": save_path})


    @staticmethod
    def take_screenshot():
        # 获取屏幕截图
        screenshot = ImageGrab.grab()
        return screenshot

    @staticmethod
    def save_screensot(save_path):
        # 获取屏幕截图
        screenshot = ImageGrab.grab()
        screenshot.save(save_path, format='PNG')


if __name__ == '__main__':
    pc = ProductCommon('ET')
    pc.launch_wps_component()
