'''
-*- coding: utf-8 -*-
@File  : apply_code.py
@author: Maoyanyu
@Time  : 2024/12/27 15:59
'''
import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import time
import re
import openpyxl
import yaml
from tqdm import tqdm
from openpyxl.styles import PatternFill, Alignment, Font
from openpyxl.utils import get_column_letter

from utils import nested_dict_from_string
from utils.keyword_ignore_map.mapping_dict_gen_code import SKIP_SHEET_ATTR, SKIP_CELL_ATTR
from utils.common_util.log_util import Logger
from utils.util.utils import add_functions, extra_dataseries
import requests
import urllib3
from multiprocessing import Process, Queue, Manager

from utils.main_compare import BatchCompare
from utils.sheet_compare import DeepSearch as DeepSearchSheet
from utils.cells_compare import DeepSearchCells



class WebDriverFactory:
    __headers = {'Accept': 'application/json', 'Content-Type': 'application/json;charset=UTF-8',
                      'User-Agent': 'selenium/4.1.0 (python windows)', 'Connection': 'keep-alive'}

    def __init__(self, executablePath, product):
        self.__wpsdriver_minishell_process = subprocess.Popen(executablePath + "/shell_initiator.exe wpsdriver_minishell_" + product)
        count = 100
        while count > 0:
            time.sleep(0.2) #等待200ms
            self.__local_port = self.getProcessPort(str(self.__wpsdriver_minishell_process.pid))
            if self.__local_port:
                self.__root_url = f"http://127.0.0.1:{self.__local_port}"
                break
            count = count - 1

    def __del__(self):
        self.__wpsdriver_minishell_process.terminate()

    def getProcessPort(self, strPid):
        netstat_output = subprocess.check_output(["netstat", "-ano"]).decode('gbk')
        for line in netstat_output.splitlines():
            if line.endswith(strPid):
                parts = line.split()
                protocol = parts[0]
                if protocol.lower() == "tcp":
                    local_address = parts[1]
                    return local_address.split(":")[-1]
        return None

    @property
    def root_url(self):
        return self.__root_url

    @property
    def session_id(self):
        self.__session_id = self.remote()
        return self.__session_id

    @property
    def headers(self):
        return WebDriverFactory.__headers

    def remote(self):
        if self.__root_url is None:
            return None

        url = self.__root_url + '/session'
        response = requests.post(url=url, timeout=20, headers=self.__headers)
        data = json.loads(response.text)
        if data is None:
            raise OSError('连接wps driver异常，url:[{}]'.format(self.__root_url))

        return data.get('value').get("sessionId")

class Product:
    WPS = "wps"
    ET = "et"
    WPP = "wpp"


class WpsdriverClient:

    def __init__(self, executablePath, product=Product.WPS):
        self.__driver_factory = WebDriverFactory(executablePath, product)
        self.__root_url = self.__driver_factory.root_url
        self.__headers = {"Content-Type": "application/json"}

    def __del__(self):
        pass

    def request(self, method, body={}):
        url = f'{self.__root_url}/session/{self.__driver_factory.session_id}/' + method
        try:
            response = requests.post(url=url, data=json.dumps(body), timeout=20, headers={"Content-Type": "application/json"})
        except (requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError, ConnectionResetError) as e:
            response = requests.post(url=url, data=json.dumps(body), timeout=20, headers=self.__headers)

        return json.loads(response.text)


class Custom_BatchCompare(BatchCompare):
    def __init__(self):
        super().__init__()
        self.ds = DeepSearchV2()
        self.code_dict=None

    def list_subdirectories(self, root_dir):
        result = {}
        # 使用 glob 模块匹配所有子文件夹
        pattern = os.path.join(root_dir, '**')
        subdirectories = [i for i in glob.glob(pattern) if os.path.isdir(i)]
        for path in subdirectories:
            name = os.path.basename(path)
            result[name] = glob.glob(os.path.join(path, '*.xlsx'))
        return result

    def run(self, all_pair_path, log_path=None, worker_number=16, code_dict=None):
        manager = Manager()
        # 创建任务队列和结果队列
        task_queue = Queue()
        result_queue = manager.list()

        all_pair_path = self.list_subdirectories(all_pair_path)
        all_pair_path_keys = list(all_pair_path.keys())

        # batchsize=256
        results = []
        # for stt_idx in tqdm(range(0, len(all_pair_path_keys), batchsize), desc=f"当前批次："):
        for index, key in enumerate(all_pair_path_keys):
            task_queue.put((all_pair_path[key], all_pair_path[key]))  # 把要处理的样品加入队列
        a = time.time()
        workers = []
        for i in range(worker_number):  # 任何时间三个任务并行
            task_queue.put(None)  # 在队列queue最后加上None，使样品处理完后程序结束运行。
            worker = Process(target=self.worker, args=(task_queue, result_queue))
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()  # 进程阻塞，保证任务全部完成后再处理后续命令
        for worker in workers:
            worker.close()  # 进程阻塞，保证任务全部完成后再处理后续命令

        # 收集所有结果并保存到文件
        print("收集结果数据中...")
        while result_queue:
            cur_res = {}
            index, result = result_queue.pop()
            # result_queue.get()
            sheet_format, cells_diff = result
            cur_res["compare_sheets"] = index
            cur_res["sheet_format"] = [i for i in sheet_format if i]
            cur_res["cells_diff"] = [i for i in cells_diff if i]
            results.append(cur_res)

        ### Get Wrong/Right ###
        right, wrong = 0, 0
        for json_dict in results:
            sheet_format = json_dict["sheet_format"]
            cells_diff = json_dict["cells_diff"]
            if (not sheet_format and not cells_diff) or "表格缺少样张" in sheet_format:
                right += 1
            elif any([True for i in sheet_format if "校验样张解析错误" in i]):
                continue
            else:
                wrong += 1
        return right, wrong, results


class GenCode_BatchCompare(BatchCompare):
    def __init__(self):
        super().__init__()
        self.ds = DeepSearchV2()
        self.code_dict=None

    def list_subdirectories(self, root_dir):
        result = {}
        # 使用 glob 模块匹配所有子文件夹
        pattern = os.path.join(root_dir, '**')
        subdirectories = glob.glob(pattern)

        # 过滤掉根目录本身
        subdirectories = [d for d in subdirectories if d != root_dir]
        for subpath in subdirectories:
            # 分别获取 .xlsx 和 .xls 文件
            xlsx_files = glob.glob(os.path.join(subpath, '*.xlsx'))

            # 过滤掉包含 "##" 的路径
            filtered_subdirectories = [d for d in xlsx_files if '原始样张' not in d]
            result[subpath] = filtered_subdirectories

        return result

    def run(self, all_pair_path, log_path=None, worker_number=16, code_dict=None):
        manager = Manager()
        # 创建任务队列和结果队列
        task_queue = Queue()
        result_queue = manager.list()

        all_pair_path = self.list_subdirectories(all_pair_path)
        all_pair_path_keys = list(all_pair_path.keys())

        # batchsize=256
        results = []
        # for stt_idx in tqdm(range(0, len(all_pair_path_keys), batchsize), desc=f"当前批次："):
        for index, key in enumerate(all_pair_path_keys):
            task_queue.put((all_pair_path[key], all_pair_path[key]))  # 把要处理的样品加入队列
        workers = []
        for i in range(worker_number):  # 任何时间三个任务并行
            task_queue.put(None)  # 在队列queue最后加上None，使样品处理完后程序结束运行。
            worker = Process(target=self.worker, args=(task_queue, result_queue))
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()  # 进程阻塞，保证任务全部完成后再处理后续命令
        for worker in workers:
            worker.close()  # 进程阻塞，保证任务全部完成后再处理后续命令

        # 收集所有结果并保存到文件
        print("收集结果数据中...")
        while result_queue:
            cur_res = {}
            index, result = result_queue.pop()
            # result_queue.get()
            sheet_format, cells_diff = result
            cur_res["compare_sheets"] = index
            cur_res["sheet_format"] = [i for i in sheet_format if i]
            cur_res["cells_diff"] = [i for i in cells_diff if i]
            results.append(cur_res)

        ### Get Wrong/Right ###
        right, wrong = 0, 0
        for json_dict in results:
            sheet_format = json_dict["sheet_format"]
            cells_diff = json_dict["cells_diff"]
            if (not sheet_format and not cells_diff) or "表格缺少样张" in sheet_format:
                right += 1
            elif any([True for i in sheet_format if "校验样张解析错误" in i]):
                continue
            else:
                wrong += 1
        return right, wrong, results



class DeepSearchCellsV2(DeepSearchCells):
    def __init__(self):
        super().__init__()
        self.SKIP_ATTR = SKIP_CELL_ATTR


class DeepSearchV2(DeepSearchSheet):
    def __init__(self):
        super().__init__()
        self.SKIP_ATTR = SKIP_SHEET_ATTR
        self.strict = True

    def run_compare(self, excel_file1, excel_file2, code_dict):
        basename = os.path.basename(excel_file1.split(".xlsx")[0])
        try:
            all_attributes1, cellsList1, sheet_name = self.excel_to_attribution_dict(excel_file1)
            all_attributes2, cellsList2, _ = self.excel_to_attribution_dict(excel_file2, sheet_name)
        except TypeError as typeerror:
            return ([f"校验样张解析错误 (超长 | openpyxl读取失败) :{typeerror}"], [])
        except KeyError as keyerror:
            return ([f"校验样张解析错误:{keyerror}"], [])
        except ValueError as valueerror:
            return ([f"校验样张解析错误:{valueerror}"], [])

        diff_ws = self.compare_dict(all_attributes1, all_attributes2, "AutoFit")

        diff_cells = self.dsc.run_compare_cells(cellsList1, cellsList2, basename)

        return (diff_ws, diff_cells)



class runCode:
    def __init__(self, config_path):
        self.client_path, self.cases_root_path, self.target_root_path,self.gen_code_cases_save_root_path, self.orig_json_file_path, self.gencode_json_file_path, self.log_path, self.xlsx_save_path, self.gen_code_xlsx_save_path = self.load_yaml(config_path)
        self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
        self.compare_client = Custom_BatchCompare()
        self.verify_code_client = GenCode_BatchCompare()

        self.logger = Logger(self.log_path)

    def load_yaml(self, file_path):
        with open(file_path, 'rb') as file:
            try:
                data = yaml.safe_load(file)
            except yaml.YAMLError as e:
                print(e)

        # 获取基础路径
        base_path = data["base_path"]

        # 获取配置信息并拼接路径
        client_path = data["client_path"]
        cases_path = os.path.join(base_path, data["dataset"]["cases_root_path"])
        cases_save_path = os.path.join(base_path, data["dataset"]["cases_save_root_path"])
        gen_code_cases_save_root_path = os.path.join(base_path, data["dataset"]["gen_code_cases_save_root_path"])
        orig_json_file_path = os.path.join(base_path, data["val"]["orig_json_file_path"])
        gencode_json_file_path = os.path.join(base_path, data["val"]["gencode_json_file_path"])
        log_path = os.path.join(base_path, data["log"]["log_path"])
        self.check_path_and_create(os.path.dirname(log_path))

        basename = os.path.basename(orig_json_file_path).split(".json")[0]
        xlsx_save_path = os.path.join(base_path, data["log"]["xlsx_save_path"], basename + ".xlsx")
        gen_code_xlsx_save_path = os.path.join(base_path, data["log"]["gen_code_xlsx_save_path"], basename + ".xlsx")

        return client_path, cases_path, cases_save_path,gen_code_cases_save_root_path, orig_json_file_path, gencode_json_file_path, log_path, xlsx_save_path, gen_code_xlsx_save_path

    def check_path_and_create(self, dst_dir):
        # 如果目标目录不存在，则创建目标目录
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

    def run_paired_data(self, code, case_path, case_save_path, case_run_save_path):
        case_save_path = case_save_path.replace("\\", "\\\\")
        case_run_save_path = case_run_save_path.replace("\\", "\\\\")
        code, _ = add_functions(code[0])
        code, _ = extra_dataseries(code)

        if "function Macro()" not in code:
            code = f"""function Macro() {{
                {code}
            }} Macro()"""
        else:
            code = code + " Macro()"

        case_save_code = f"""function Macro() {{
            Application.Workbooks.Open("{case_path}")
            Application.ActiveWorkbook.SaveAs("{case_save_path}")
            Application.Workbooks.Close("{case_path}")
        }} Macro()"""

        try:
            self.client.request(method="execute/script/evaluate", body={'script': case_save_code})
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Open("{case_path}")'})
            response = self.client.request(method="execute/script/evaluate", body={'script': code})
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.ActiveWorkbook.SaveAs("{case_run_save_path}")'})
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Close("{case_path}")'})

        except requests.exceptions.ReadTimeout as e:
            response = {"value": "执行超时"}
            shutil.copy(case_path, case_save_path)
            shutil.copy(case_path, case_run_save_path)
            self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)


        run_flag = (True, "", code) if (response["value"] == 'null') else (False, response["value"], code)

        return run_flag


    def run_gen_code_data(self, code, case_path, case_label_path, md5):
        code, _ = add_functions(code)
        code, _ = extra_dataseries(code)


        save_case_root_path = os.path.join(self.gen_code_cases_save_root_path, md5)
        self.check_path_and_create(save_case_root_path)


        orig_file = os.path.basename(case_path)
        label_file = os.path.basename(case_label_path)

        target_orig_file_path = os.path.join(save_case_root_path, orig_file)
        target_label_file_path = os.path.join(save_case_root_path, label_file)
        target_run_file_path = os.path.join(save_case_root_path, orig_file.replace("原始", "执行"))

        shutil.copy(case_path, target_orig_file_path)
        shutil.copy(case_label_path, target_label_file_path)

        target_orig_file_path_x = target_orig_file_path.replace("\\", "\\\\")
        target_run_file_path = target_run_file_path.replace("\\", "\\\\")
        if "function Macro()" not in code:
            code = f"""function Macro() {{
                {code}
            }} Macro()"""
        else:
            code = code + " Macro()"

        try:
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Open("{target_orig_file_path_x}")'})
            response = self.client.request(method="execute/script/evaluate", body={'script': code})
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.ActiveWorkbook.SaveAs("{target_run_file_path}")'})
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Close("{target_orig_file_path_x}")'})
        except requests.exceptions.ReadTimeout as e:
            shutil.copy(target_orig_file_path, target_run_file_path)
            response = {"value": "执行超时"}
            self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)

        run_flag = (True, "") if (response["value"] == 'null') else (False, response["value"])

        return run_flag

    def list_subdirectories(self, root_dir):
        # 使用 glob 模块匹配所有子文件夹
        pattern = os.path.join(root_dir, '**')
        subdirectories = glob.glob(pattern)

        # 过滤掉根目录本身
        subdirectories = [d for d in subdirectories if d != root_dir and not os.path.basename(d).startswith("~$")]
        return subdirectories

    def get_code(self):
        code_dict = {}
        with open(self.orig_json_file_path, "r", encoding='utf-8') as f:
            for line in f:
                json_dict = json.loads(line)
                code = json_dict["target"]
                input = json_dict["input"]
                if code:
                    code, _ = add_functions(code)
                    code, _ = extra_dataseries(code)
                code_dict[json_dict["md5"]] = (code, input)
        return code_dict

    def get_gen_codes(self):
        code_dict = []
        with open(self.gencode_json_file_path, "r", encoding='utf-8') as f:
            for line in f:
                json_dict = json.loads(line)
                code = json_dict["target"]
                md5 = json_dict["md5"]
                input = json_dict["input"]

                if code:
                    code, _ = add_functions(code)
                    code, _ = extra_dataseries(code)
                code_dict.append((code, md5, input))
        return code_dict

    def collection_result(self):
        self.collection_wb = openpyxl.Workbook()
        # 选择一个工作表（例如，第一个工作表）
        self.collection_sheet = self.collection_wb.active
        self.collection_sheet.title = "样张执行结果"
        header = ["表格名(md5)", "表格描述", "代码", "原始样张路径", "结果样张路径", "运行是否成功", "运行报错", "执行前后差异信息", "执行前后是否有变化"]
        header_fill = {"1-2": "DAEEF3", "3-3": "FDE9D9", "4-9": "DA9694"}
        column_width = [20, 50, 80, 20,20,20,20, 20, 20]
        # 写入表头
        for col_num, col_name in enumerate(header, 1):
            cell = self.collection_sheet.cell(row=1, column=col_num, value=col_name)
            cell.font = Font(name='微软雅黑', size=10, bold=True)  # 设置字体样式
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)  # 设置对齐方式

            # 设置表头颜色填充
            if header_fill:
                for fill_range, fill_color in header_fill.items():
                    start_col, end_col = [int(x) for x in fill_range.split('-')]
                    if start_col <= col_num <= end_col:
                        cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type='solid')
                        break

            # 设置列宽
            if column_width:
                try:
                    self.collection_sheet.column_dimensions[get_column_letter(col_num)].width = column_width[col_num - 1]
                except Exception:
                    pass
        self.collection_sheet.row_dimensions[self.collection_sheet.max_row].height = 300

    def result_to_xlsx(self, collection_dict_gen_sheet):
        self.collection_result()
        # ["表格名(md5)", "表格描述", "代码", "原始样张路径", "结果样张路径", "执行前后是否有变化", "运行是否成功"]
        for cur_pair in tqdm(collection_dict_gen_sheet, desc="Check中......"):
            self.collection_sheet.append(collection_dict_gen_sheet[cur_pair])
            # 设置整行单元格的自动换行
            for cell in self.collection_sheet[self.collection_sheet.max_row]:
                cell.alignment = Alignment(wrap_text=True)
                cell.font = Font(name='微软雅黑', size=10)  # 设置字体样式
                self.collection_sheet.row_dimensions[self.collection_sheet.max_row].height = 300

            # 获取最新追加的行号
            row_number = self.collection_sheet.max_row

            # 创建超链接并应用到相应的单元格
            self.collection_sheet[f'D{row_number}'].hyperlink = os.path.relpath(collection_dict_gen_sheet[cur_pair][3], os.path.dirname(self.xlsx_save_path))
            self.collection_sheet[f'D{row_number}'].value = '原始样张路径'
            self.collection_sheet[f'D{row_number}'].style = 'Hyperlink'

            self.collection_sheet[f'E{row_number}'].hyperlink = os.path.relpath(collection_dict_gen_sheet[cur_pair][4], os.path.dirname(self.xlsx_save_path))
            self.collection_sheet[f'E{row_number}'].value = '结果样张路径'
            self.collection_sheet[f'E{row_number}'].style = 'Hyperlink'
        # 保存文件
        self.collection_wb.save(self.xlsx_save_path)


    def collection_result_gen_code(self):
        self.collection_wb = openpyxl.Workbook()
        # 选择一个工作表（例如，第一个工作表）
        self.collection_sheet = self.collection_wb.active
        self.collection_sheet.title = "结果"
        self.order_list = ['用例编号', '样张路径', '原始样张', '校验样张', '结果样张','Prompt', '问题',  "原始代码", '生成代码', '代码是否执行成功',"执行报错", "表单属性差异", "单元格属性差异",'校验是否通过']
        header_fill = {"1-7": "DAEEF3", "8-9": "FDE9D9", "10-14": "DA9694"}
        column_width = [8, 8, 8, 8, 8, 20, 15, 20, 20,  12,50,50,50, 12]
        # 写入表头
        header = self.order_list
        self.collection_sheet.row_dimensions[1].height = 300
        for col_num, col_name in enumerate(header, 1):
            cell = self.collection_sheet.cell(row=1, column=col_num, value=col_name)
            cell.font = Font(name='微软雅黑', size=10, bold=True)  # 设置字体样式
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)  # 设置对齐方式

            # 设置表头颜色填充
            if header_fill:
                for fill_range, fill_color in header_fill.items():
                    start_col, end_col = [int(x) for x in fill_range.split('-')]
                    if start_col <= col_num <= end_col:
                        cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type='solid')
                        break

            # 设置列宽
            if column_width:
                try:
                    self.collection_sheet.column_dimensions[get_column_letter(col_num)].width = column_width[col_num - 1]
                except Exception:
                    pass



    def result_to_xlsx_gen_code(self, collection_dict_gen_code):
        self.collection_result_gen_code()
        # ['用例编号', '样张路径', '原始样张', '校验样张', '结果样张', '问题', 'Prompt', 'AI返回JS', "表单属性差异", "单元格属性差异",'代码是否执行成功',"执行报错",'校验是否通过']
        for case_path in tqdm(collection_dict_gen_code, desc="提取数据到xlsx..."):
            case_index, case_path, orig_case_path, right_case_path, result_case_path, table, question, orig_code, code, run_flag, run_error, sheet_diff, cells_diff, flag = collection_dict_gen_code[case_path]
            self.collection_sheet.append([case_index, case_path, orig_case_path, right_case_path, result_case_path, table, question, orig_code, code, run_flag, run_error,  "\n".join(sheet_diff), "\n".join(["\n".join(i) for i in cells_diff]),flag])
            # 获取最新追加的行号
            row_number = self.collection_sheet.max_row

            # 设置整行单元格的自动换行
            for cell in self.collection_sheet[self.collection_sheet.max_row]:
                cell.alignment = Alignment(wrap_text=True)
                cell.font = Font(name='微软雅黑', size=10)  # 设置字体样式
                self.collection_sheet.row_dimensions[self.collection_sheet.max_row].height = 300

            # 创建超链接并应用到相应的单元格
            self.collection_sheet[f'C{row_number}'].hyperlink = os.path.abspath(orig_case_path)
            self.collection_sheet[f'C{row_number}'].value = "原始样张"
            self.collection_sheet[f'C{row_number}'].style = 'Hyperlink'
            self.collection_sheet[f'C{row_number}'].alignment = Alignment(wrap_text=True)
            self.collection_sheet[f'C{row_number}'].font = Font(name='微软雅黑', size=10, color='0000FF',underline='single')

            self.collection_sheet[f'D{row_number}'].hyperlink = os.path.abspath(right_case_path)
            self.collection_sheet[f'D{row_number}'].value = "校验样张" if right_case_path else ""
            self.collection_sheet[f'D{row_number}'].style = 'Hyperlink'
            self.collection_sheet[f'D{row_number}'].alignment = Alignment(wrap_text=True)
            self.collection_sheet[f'D{row_number}'].font = Font(name='微软雅黑', size=10, color='0000FF',underline='single')

            self.collection_sheet[f'E{row_number}'].hyperlink = os.path.abspath(result_case_path)
            self.collection_sheet[f'E{row_number}'].value = "执行样张" if result_case_path else ""
            self.collection_sheet[f'E{row_number}'].style = 'Hyperlink'
            self.collection_sheet[f'E{row_number}'].alignment = Alignment(wrap_text=True)
            self.collection_sheet[f'E{row_number}'].font = Font(name='微软雅黑', size=10, color='0000FF',underline='single')


        # 保存文件
        self.collection_wb.save(self.gen_code_xlsx_save_path)



    def run_all(self):
        ### 生成校验样张 ###
        all_pair_path = self.list_subdirectories(self.cases_root_path)
        code_dict = self.get_code()
        self.collection_dict_gen_sheet = {}
        for case_path in tqdm(all_pair_path, desc="执行样张中..."):
            basename = os.path.basename(case_path).split(".xlsx")[0]
            code, table = code_dict[basename]
            case_path = case_path.replace("\\", "\\\\")
            case_save_path = os.path.join(self.target_root_path, basename, basename + "_原始样张.xlsx")
            case_run_save_path = os.path.join(self.target_root_path, basename, basename + "_校验样张.xlsx")
            self.check_path_and_create(os.path.join(self.target_root_path, basename))
            run_flag, run_error, orig_code = self.run_paired_data((code, table), case_path, case_save_path, case_run_save_path)
            # ["表格名(md5)", "表格描述", "代码", "原始样张路径", "结果样张路径",  "运行是否成功", "报错信息"]
            self.collection_dict_gen_sheet[basename] = [basename, table, orig_code, case_save_path, case_run_save_path,
                                                        run_flag, run_error]
        _, _, results = self.compare_client.run(self.target_root_path, worker_number=16)

        for res in results:
            name = res["compare_sheets"][0].split("\\")[-2]
            diff_res = ",   ".join([",   ".join(i) for i in res["cells_diff"]]) + ",   ".join(res["sheet_format"])
            diff_flag = True if diff_res else False

            if "校验样张解析错误" in diff_res or "表格缺少样张" in diff_res or not diff_res:
                diff_out_res = diff_res
            else:
                diff_out_res = nested_dict_from_string(diff_res)


            self.collection_dict_gen_sheet[name] = self.collection_dict_gen_sheet[name] + [diff_out_res] + [diff_flag]
        self.result_to_xlsx(self.collection_dict_gen_sheet)


        ### 执行新代码 ###
        self.collection_dict_gen_code = {}
        gen_codes_list =  self.get_gen_codes()
        start_time = time.time()
        has_run = {}
        for code, md5, prompt in tqdm(gen_codes_list, desc="RUN GEN Code..."):

            if md5 in has_run:
                has_run[md5]+=1
            else:
                has_run[md5]=1
            label_valid = self.collection_dict_gen_sheet[md5][-1] and self.collection_dict_gen_sheet[md5][-4]
            orig_code = self.collection_dict_gen_sheet[md5][2]

            if label_valid:
                case_path = os.path.join(self.target_root_path, md5, md5 + "_原始样张.xlsx")
                case_label_path = os.path.join(self.target_root_path, md5, md5 + "_校验样张.xlsx")
                self.check_path_and_create(os.path.join(self.target_root_path, md5))
                run_flag, run_error = self.run_gen_code_data(code, case_path, case_label_path, str(has_run[md5])+"_"+md5)
                # ['用例编号', '样张路径', '原始样张', '校验样张', '结果样张', '问题', 'Prompt', 'AI返回JS', "表单属性差异", "单元格属性差异", '校验是否通过']
                file_name = os.path.basename(case_path)
                case_root_path = os.path.join(self.target_root_path, str(has_run[md5])+"_"+md5)
                orig_file_path = os.path.join(self.gen_code_cases_save_root_path, str(has_run[md5])+"_"+md5, file_name)
                label_file_path = os.path.join(self.gen_code_cases_save_root_path, str(has_run[md5])+"_"+md5, file_name.replace("原始", "校验"))
                run_file_path = os.path.join(self.gen_code_cases_save_root_path, str(has_run[md5])+"_"+md5, file_name.replace("原始", "执行"))
                query = re.findall(r"需求“(.*?)”", prompt)[0]
                self.collection_dict_gen_code[str(has_run[md5])+"_"+md5] = [str(has_run[md5])+"_"+md5, case_root_path, orig_file_path, label_file_path, run_file_path, prompt, query, orig_code, code, run_flag, run_error]
            else:
                continue
        time_run = time.time() - start_time

        start_time = time.time()
        right, wrong, collection_compare_dict = self.verify_code_client.run(self.gen_code_cases_save_root_path, worker_number=16)

        for res_compare in collection_compare_dict:
            sheet_format, cells_diff = res_compare["sheet_format"], res_compare["cells_diff"]
            if not sheet_format and not cells_diff: flag=True
            else: flag=False
            self.collection_dict_gen_code[res_compare["compare_sheets"][0].split("\\")[-2]] += [sheet_format, cells_diff, flag]

        time_compare = time.time() - start_time
        self.logger.info(f"通过: {right} | 未通过: {wrong} | 整体通过率: {round(right/(right+wrong+1e-7), 4)}")
        self.logger.info(f"执行总耗时: {time_run} s | 校验总耗时: {time_compare} s")

        self.result_to_xlsx_gen_code(self.collection_dict_gen_code)





if __name__ == "__main__":
    parser = argparse.ArgumentParser("执行样张配置")
    parser.add_argument("--verify_codes_config", type=str, help="Add your case path", default="configs/config_run_code.yaml")
    args = parser.parse_args()
    main = runCode(config_path=args.verify_codes_config)
    main.run_all()