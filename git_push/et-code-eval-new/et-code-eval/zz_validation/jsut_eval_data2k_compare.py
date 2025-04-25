'''
-*- coding: utf-8 -*-
@File  : data2k_compare.py
@author: Maoyanyu
@Time  : 2024/12/23 00:25
'''
import glob
import json
import os
import random
import shutil
import subprocess
import sys
import time
import re
import openpyxl
import xlwings as xw

import pandas as pd
import requests
import urllib3
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from func_timeout import func_timeout, FunctionTimedOut
from pygments.lexer import default

from utils.common_util.log_util import Logger
from tqdm import tqdm
# from utils.util.utils import add_functions, extra_dataseries
from utils.util.tool_functinos import ToolFunctions
from multiprocessing import Process, Queue, Manager
from zz_infer.infer_base_vllm import infer_base_vllm_func
from utils.main_compare import BatchCompare
from openpyxl.styles import PatternFill, Alignment, Font
from openpyxl.utils import get_column_letter
import yaml
import argparse
from utils import *


class XBatchCompare(BatchCompare):
    def __init__(self):
        super().__init__()

    def list_subdirectories(self, root_dir):
        result = {}
        # 使用 glob 模块匹配所有子文件夹
        pattern = os.path.join(root_dir, '*/')
        subdirectories = glob.glob(pattern)

        # 过滤掉根目录本身
        subdirectories = [d for d in subdirectories if d != root_dir]
        for subpath in subdirectories:
            # 分别获取 .xlsx 和 .xls 文件
            xlsx_files = glob.glob(os.path.join(subpath, '*.xlsx'))
            xls_files = glob.glob(os.path.join(subpath, '*.xls'))

            if len(xls_files) > 2:
                excel_file_paths = xls_files
            else:
                excel_file_paths = xlsx_files

            # 过滤掉包含 "##" 的路径
            val_subdirectories = [d for d in excel_file_paths if '校验样张' in d]
            run_subdirectories = [d for d in excel_file_paths if '执行样张' in d]
            result[subpath] = val_subdirectories+run_subdirectories

        return result

    def run(self, all_pair_path, log_path, worker_number=1, code_dict=None):
        self.code_dict=code_dict
        manager = Manager()
        # 创建任务队列和结果队列
        task_queue = Queue()
        result_queue = manager.list()

        all_pair_path = self.list_subdirectories(all_pair_path)
        all_pair_path_keys = list(all_pair_path.keys())
        all_pair_path_keys = sorted(all_pair_path_keys, key=lambda x: os.path.basename(x))
        # self.refresh_files(all_pair_path)

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
            try:
                cur_res["index"] = os.path.basename(os.path.dirname(index[0]))
            except:
                print(f'错误路径:{index}index')
            cur_res["sheet_format"] = [i for i in sheet_format if i]
            cur_res["cells_diff"] = [i for i in cells_diff if i]
            results.append(cur_res)

        results = sorted(results, key=lambda x: x["index"])
        collection_compare_dict = {}
        res_file = os.path.join(log_path, 'comparison_results.json')
        with open(res_file, 'w', encoding="utf-8") as f:
            for line in tqdm(results, desc="保存数据中..."):
                collection_compare_dict[line["index"]] = (line["sheet_format"], line["cells_diff"])
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
        print(f'详细结果已存到{res_file}')
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
        return right, wrong, collection_compare_dict




class CheckCode():
    def __init__(self, args):

        # 获取当前日期和时间并添加log时间
        time_now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        cur_dataset_name = os.path.basename(args.json_file_path).split(".")[0]
        collection_result_path = os.path.join(args.target_path, f"{time_now}_{cur_dataset_name}.xlsx")
        log_path = os.path.join(args.log_path, time_now , "run.log")
        case_save_path = os.path.join(args.target_path, f"{time_now}_{cur_dataset_name}")

        # Assign arguments to variables
        self.client_path = args.client_path
        self.cases_path = args.cases_path
        self.excel_proj_file = args.excel_file_path
        self.device_default_change = args.device_default_change
        self.code_mode = args.code_mode
        self.xlsx_save_path = case_save_path
        self.json_file_path = args.json_file_path
        self.collection_result_path = collection_result_path
        self.log_path = log_path
        self.worker_number = args.worker_number

        self.check_path_and_create(self.xlsx_save_path)
        self.check_path_and_create(os.path.dirname(self.log_path))
        self.worker_number = args.worker_number

        self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
        self.compare_client = XBatchCompare()
        self.logger = Logger(self.log_path)

        self.tool_function = ToolFunctions()
        self.data_mapping_dict = eval(args.data_mapping_dict)



    def load_workbook_with_timeout(self, file_path, timeout):

        try:
            ws = func_timeout(timeout, openpyxl.load_workbook, (file_path,))
            return ws
        except FunctionTimedOut:
            print(f'读取样张{file_path}超时')
            raise TimeoutError

    def run_ai(self, code, case_path, label_case_path, case_save_path):
        case_path = case_path.replace("\\", "\\\\")
        case_save_path = case_save_path.replace("\\", "\\\\")
        label_case_path = label_case_path.replace("\\", "\\\\")
        self.check_path_and_create(os.path.dirname(case_save_path))

        code, _ = self.tool_function.add_functions(code[0], code[1])
        # code, _ = add_functions(code[0], code[1])
        # code, _ = extra_dataseries(code)

        if "function Macro()" not in code:
            code = f"""function Macro() {{
                   {code}
               }} Macro()"""
        else:
            code = code + " Macro()"

        try:
            self.client.request(method="execute/script/evaluate",
                                body={'script': 'Application.Workbooks.Open("{}")'.format(case_path)})
            response = self.client.request(method="execute/script/evaluate", body={'script': code})
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.ActiveWorkbook.SaveAs("{case_save_path}")'})
            self.client.request(method="execute/script/evaluate",
                                body={'script': 'Application.Workbooks.Close("{}")'.format(case_path)})

        except requests.exceptions.ReadTimeout as e:
            print("样张执行超时")
            del self.client
            response = {"isSuccess": False, "value": "样张执行超时"}
            self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Close("{case_save_path}")'})
            shutil.copy(case_path, case_save_path)
        except ValueError as e:
            print("代码执行失败")
            del self.client
            self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Close("{case_save_path}")'})
            response = {"isSuccess": False, "value": "代码执行失败"}
            shutil.copy(case_path, case_save_path)

        ### 避免不同设备之间默认值差异，需要对校验样张全部更新一次，config文件中可变更标志位，只需换新设备后执行一次 ##
        if self.device_default_change:
            save_label_case_code = f"""function Macro() {{
                Application.Workbooks.Open("{label_case_path}")
                Application.ActiveWorkbook.SaveAs("{label_case_path}")
                Application.Workbooks.Close("{label_case_path}")
            }} Macro()"""
            self.client.request(method="execute/script/evaluate",body={'script': save_label_case_code})

        tgt_dir = os.path.dirname(case_save_path)
        try:
            shutil.copy(self.replace_excel(case_path).replace("\\\\", "\\"), tgt_dir.replace("\\\\", "\\"))
            shutil.copy(self.replace_excel(label_case_path).replace("\\\\", "\\"), tgt_dir.replace("\\\\", "\\"))
        except:
            print()

        run_flag = (True, "") if (response["value"] == 'null' or response["value"] =="true") else (False, response["value"])


        # run_flag = True if (response["isSuccess"] == True) else False

        return run_flag


    def check_path_and_create(self, dst_dir):
        # 如果目标目录不存在，则创建目标目录
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

    def apply_code(self, original_xlsx_file_path,label_xlsx_file_path, code, processed_xlsx_save_path):
        run_flag = self.run_ai(code, original_xlsx_file_path, label_xlsx_file_path, processed_xlsx_save_path.replace("原始样张", "执行样张"))
        return run_flag

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
            xls_files = glob.glob(os.path.join(subpath, '*.xls'))


            excel_file_paths = xlsx_files+xls_files

            # 过滤掉包含 "##" 的路径
            orig_path = [d for d in excel_file_paths if '原始样张' in d and not os.path.basename(d).startswith("~$")]
            val_path = [d for d in excel_file_paths if '校验样张' in d and not os.path.basename(d).startswith("~$")]

            result[subpath] = orig_path+val_path

        return result

    # 读取Excel表格
    def read_excel(self, file_path):
        df = pd.read_excel(file_path, sheet_name="测试-工具模式")
        return df

    # 读取JSON字典
    def read_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            res = []
            for line in file:
                res.append(json.loads(line))
        return res

    # 匹配问题并打包结果
    def match_and_package(self, cases_path, json_data):
        result = {}
        excel_df = self.read_excel(self.excel_proj_file)
        PROJ_DICT = {}
        for index, row in excel_df.iterrows():
            question = row['问题']
            case_number = row['用例编号']
            try:
                PROJ_DICT[question] = str(int(case_number))
            except:
                PROJ_DICT[question] = None
        with open(json_data, "r", encoding='utf-8') as file:
            for line in file:
                json_dict = json.loads(line)

                input = json_dict[self.data_mapping_dict['input']]
                target = json_dict[self.data_mapping_dict['target']]

                if self.code_mode=="default":
                    pass
                elif self.code_mode=="r1":
                    target = target.split("</think>")[-1]

                question = re.findall(r"需求“(.*?)”", input, re.DOTALL)[0]

                if json_dict["question"] in PROJ_DICT.keys():
                    name = PROJ_DICT[json_dict["question"]]
                else:
                    continue

                result[os.path.join(cases_path, name)] = (question, input, target)
        return result

    def replace_excel(self, file_path):
        if file_path.endswith('.xls'):
            print(f"{file_path}文件格式转化 xls --->>> xlsx...")
            app = xw.App(visible=False, add_book=False)
            example = app.books.open(file_path)
            example.save(f"{file_path}x")
            example.close()
            app.quit()
            new_path = f"{file_path}x"
            os.remove(file_path)
            return new_path
        else:
            return file_path

    def collection_result(self):
        self.collection_wb = openpyxl.Workbook()
        # 选择一个工作表（例如，第一个工作表）
        self.collection_sheet = self.collection_wb.active
        self.collection_sheet.title = "结果"
        self.order_list = ['用例编号', '样张路径', '原始样张', '校验样张', '执行样张', '问题', 'Prompt', 'AI返回JS',
                           "表单属性差异", "单元格属性差异", '代码执行成功', '运行信息', '校验是否通过']
        header_fill = {"1-7": "DAEEF3", "8-8": "FDE9D9", "9-13": "DA9694"}
        column_width = [8, 8, 8, 8, 8, 15, 20, 20, 50, 50, 12, 12, 12]
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
                    self.collection_sheet.column_dimensions[get_column_letter(col_num)].width = column_width[
                        col_num - 1]
                except Exception:
                    pass

    def result_to_xlsx(self, collection_dict_gen_sheet, collection_compare_dict):
        self.collection_result()
        # ['用例编号', '样张路径', '原始样张', '校验样张', '结果样张', '问题', 'Prompt', 'AI返回JS', "表单属性差异", "单元格属性差异", '校验是否通过']
        case_paths = list(collection_dict_gen_sheet.keys())
        for case_path in tqdm(case_paths, desc="提取数据到xlsx..."):
            case_index = os.path.basename(case_path)
            case_path = case_path
            orig_case_path, right_case_path, result_case_path = collection_dict_gen_sheet[case_path][1]
            question, table, code = collection_dict_gen_sheet[case_path][2]
            run_flag = collection_dict_gen_sheet[case_path][-1]
            try:
                sheet_diff, cells_diff = collection_compare_dict[case_index]
            except:
                sheet_diff, cells_diff = ["表格缺少样张"], []
            if run_flag[0]:
                if not sheet_diff:
                    if not cells_diff: flag = True
                    else: flag = False
                else:
                    if any(True for i in ["表格缺少样张", "校验样张解析错误"] if i in sheet_diff[0]): flag="NULL"
                    else: flag=False
            else:
                flag = False

            if sheet_diff: sheet_diff = sheet_diff[:50]
            if cells_diff: cells_diff = ["\n".join(i) for i in cells_diff[:5]]
            try:
                self.collection_sheet.append([case_index, case_path, orig_case_path, right_case_path, result_case_path, question, table, code,  "\n".join(sheet_diff), "\n".join(cells_diff),run_flag[0],run_flag[1], flag])
            except:
                pass
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
        self.collection_wb.save(self.collection_result_path)


    def main(self):
        all_pair_path = self.list_subdirectories(self.cases_path)

        # 匹配问题并打包结果
        result = self.match_and_package(self.cases_path, self.json_file_path)
        # 随机抽取两个元素
        keys_to_extract = list(result)
        result = {key: result[key] for key in keys_to_extract}

        total_num, case_right_miss, code_miss, success = len(result), 0,0,0

        self.logger.info("START EXECUTE SUCCESS")
        self.logger.info("*" * 30)

        collection_dict_gen_sheet = {}
        code_dict = {}
        start_time = time.time()
        # 使用tqdm显示进度条
        with tqdm(total=total_num, desc="生成执行样张结果: ") as pbar:
            for key in result:
                index = os.path.basename(key)
                try:
                    orig_case_name = os.path.basename(all_pair_path[key][0])
                except:
                    case_right_miss += 1
                    collection_dict_gen_sheet[key] = ("校验样张丢失", [orig_case_path, "", ""], result[key], ("NULL","NULL"))
                    self.logger.info(f"校验样张丢失: {key}")
                    continue
                orig_case_path, right_case_path, result_case_path = orig_case_name, orig_case_name.replace("原始样张", "校验样张"), orig_case_name.replace("原始样张", "执行样张")

                orig_case_path = os.path.join(self.xlsx_save_path, index, orig_case_path)
                right_case_path = os.path.join(self.xlsx_save_path, index, right_case_path)
                result_case_path = os.path.join(self.xlsx_save_path, index, result_case_path)

                try:
                    prompt = result[key][1]
                    code = result[key][2]
                except:
                    code_miss += 1
                    collection_dict_gen_sheet[key] = ("问题无对应代码", [orig_case_path, right_case_path, ""], ("", "", ""), ("NULL","NULL"))
                    self.logger.info(f"问题无对应代码: {key}")
                    continue
                if len(all_pair_path[key])==1:
                    case_right_miss+=1
                    collection_dict_gen_sheet[key] = ("校验样张丢失", [orig_case_path, "", ""], result[key], ("NULL","NULL"))
                    self.logger.info(f"校验样张丢失: {key}")
                    continue
                else:
                    # 首先转化xls文件为xlsx文件
                    for idx, case_path in enumerate(all_pair_path[key]):
                        if case_path.endswith('.xls'):
                            all_pair_path[key][idx] = self.replace_excel(case_path)

                    run_response = self.apply_code(all_pair_path[key][0],all_pair_path[key][1], (code, prompt), os.path.join(self.xlsx_save_path, os.path.basename(key), os.path.basename(all_pair_path[key][0])))
                    collection_dict_gen_sheet[key] = ("", [orig_case_path, right_case_path, result_case_path], result[key], run_response)
                    success+=1
                    # 更新进度条描述信息
                    pbar.set_postfix(total_num=total_num, success=success, right_case_miss=case_right_miss, code_miss=code_miss)
                    pbar.update(1)
                code_dict[index] = code
        time_run = time.time() - start_time
        self.logger.info(f"总验证: {total_num} | 正确执行: {success} | 校验样张丢失: {case_right_miss} | 问题无对应代码: {code_miss} | 其他错误: {total_num-case_right_miss-success-code_miss}")
        self.logger.info(f"执行总耗时: {time_run} s")

            # except: continue

        ## 比较 ##
        self.logger.info("START COMPARE SUCCESS")
        self.logger.info("*" * 30)
        start_time = time.time()
        right, wrong, collection_compare_dict = self.compare_client.run(self.xlsx_save_path, os.path.dirname(self.log_path), self.worker_number,code_dict)
        time_compare = time.time() - start_time
        self.logger.info(f"通过: {right} | 未通过: {wrong} | 整体通过率: {round(right/(right+wrong+1e-7), 4)}")
        self.logger.info(f"执行总耗时: {time_run} s | 校验总耗时: {time_compare} s")

        self.result_to_xlsx(collection_dict_gen_sheet, collection_compare_dict)
        self.logger.info(f"数据统计到: {self.xlsx_save_path}")

        self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)



def parse_arguments(root_args):
    val_parser = argparse.ArgumentParser(description="Configuration for the application.")
    # Basic configuration
    val_parser.add_argument('--client_path', type=str, default=root_args.client_path, help='Client service path (execution path)')
    # Dataset configuration
    val_parser.add_argument('--cases_path', type=str, default=rf"{root_args.root_path}\cases\run_code_result", help='Test cases path')
    val_parser.add_argument('--excel_file_path', type=str, default=rf"{root_args.root_path}\cases\AI工具测试-minimax-All.xlsx", help='Path to the Mapping Excel file"')
    val_parser.add_argument('--code_mode', type=str, default=root_args.code_mode, help='r1|default')
    val_parser.add_argument('--device_default_change', type=bool, default=root_args.device_default_change, help='Flag to change device defaults.')
    # Validation configuration
    val_parser.add_argument('--worker_number', type=int, help='code_mode', default=root_args.worker_number)
    val_parser.add_argument('--target_path', type=str, default=rf".\gen_sheets\val_all_2k\eval_results", help='Target path for validation results')
    val_parser.add_argument('--json_file_path', type=str, default=rf"{root_args.root_path}\infer_results\{args.src_path}", help='Path to the JSON file')
    val_parser.add_argument('--data_mapping_dict', type=str, help='data_mapping_dict', default=root_args.data_mapping_dict)
    # Log configuration
    val_parser.add_argument('--log_path', type=str, default=rf"{root_args.root_path}\logs", help='Path to the log files')
    val_args = val_parser.parse_args([])


    return val_args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Config')
    # Eval Config
    parser.add_argument('--root_path', type=str, default=r".\gen_sheets\val_all_2k", help='Path to the Mapping Excel file"')
    parser.add_argument('--client_path', type=str, help='client_path', default=r'C:\Users\Bolt\Downloads\office6\office6')
    parser.add_argument('--device_default_change', action='store_true', help='Flag to change device defaults. Just execute once!!')
    parser.add_argument('--data_mapping_dict', type=str, help='data_mapping_dict', default='{"input": "prompt", "target": "answer"}')
    parser.add_argument('--code_mode', type=str, help='code_mode', default='default')
    parser.add_argument('--worker_number', type=int, help='code_mode', default=16)

    # Src Path
    parser.add_argument('--src_path', type=str, help='src_path', default=r"n400_l5k.json")
    args = parser.parse_args()

    val_args = parse_arguments(args)
    check_tool = CheckCode(val_args)
    check_tool.main()

