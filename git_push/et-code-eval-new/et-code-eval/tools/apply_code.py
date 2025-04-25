'''
-*- coding: utf-8 -*-
@File  : apply_code.py
@author: Maoyanyu
@Time  : 2024/12/27 15:59
'''
import argparse
import glob

from tqdm import tqdm
from openpyxl.styles import PatternFill, Alignment, Font
from openpyxl.utils import get_column_letter
from utils.keyword_ignore_map.mapping_dict_gen_code import SKIP_SHEET_ATTR, SKIP_CELL_ATTR
from utils.common_util.log_util import Logger
from utils.util.utils import add_functions, extra_dataseries
from utils.util.tool_functinos import ToolFunctions
import requests
import urllib3
from multiprocessing import Process, Queue, Manager

from utils.main_compare import BatchCompare
from utils.sheet_compare import DeepSearch as DeepSearchSheet
from utils.cells_compare import DeepSearchCells
from utils import *
import functools

from func_timeout import func_timeout, FunctionTimedOut


def timer_decorator(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 记录开始时间
        value = func(*args, **kwargs)  # 执行被装饰的函数
        end_time = time.perf_counter()  # 记录结束时间
        run_time = end_time - start_time  # 计算执行时间

        # 如果函数有返回值，返回一个包含返回值和执行时间的元组
        if value is not None:
            return value, run_time
        else:
            # 如果函数没有返回值，只返回执行时间
            return run_time
    return wrapper_timer

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

    def run(self, all_pair_path, log_path=None, worker_number=0, code_dict=None):
        manager = Manager()
        # 创建任务队列和结果队列
        task_queue = Queue()
        result_queue = manager.list()
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
        except TimeoutError as timeerror:
            return ([f"样张读取超时:{timeerror}"], [])

        diff_ws = self.compare_dict(all_attributes1, all_attributes2, "AutoFit")

        diff_cells = self.dsc.run_compare_cells(cellsList1, cellsList2, basename)

        return (diff_ws, diff_cells)






class runCode:
    def __init__(self, config_path, data_mapping_dict, mode):
        self.client_path, self.cases_root_path, self.target_root_path, self.json_file_path, self.log_path, self.xlsx_save_path = self.load_yaml(config_path)
        self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
        self.compare_client = Custom_BatchCompare()
        self.logger = Logger(self.log_path)
        self.data_mapping_dict = data_mapping_dict
        self.mode = mode
        self.tool_function = ToolFunctions()

    def load_workbook_with_timeout(self, file_path, timeout):

        try:
            ws = func_timeout(timeout, openpyxl.load_workbook, (file_path,))
            return ws
        except FunctionTimedOut:
            print(f'读取样张{file_path}超时')
            raise TimeoutError




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
        json_file_path = os.path.join(base_path, data["val"]["json_file_path"])
        log_path = os.path.join(base_path, data["log"]["log_path"])
        self.check_path_and_create(os.path.dirname(log_path))

        basename = os.path.basename(json_file_path).split(".json")[0]
        xlsx_save_path = os.path.join(base_path, data["log"]["xlsx_save_path"], basename + ".xlsx")
        self.check_path_and_create(os.path.dirname(xlsx_save_path))

        return client_path, cases_path, cases_save_path, json_file_path, log_path, xlsx_save_path


    def check_path_and_create(self, dst_dir):
        # 如果目标目录不存在，则创建目标目录
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

    def run_paired_data(self, code, case_path_o, case_save_path_o, case_run_save_path_o):
        case_save_path = case_save_path_o.replace("\\", "\\\\")
        case_run_save_path = case_run_save_path_o.replace("\\", "\\\\")
        case_path = case_path_o.replace("\\", "\\\\")
        # code, _ = add_functions(code[0], code[1])
        # code, _ = extra_dataseries(code)
        code, _ = self.tool_function.add_functions(code[0], code[1])



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
                                body={'script': f'Application.Workbooks.Open("{case_save_path}")'})
            response = self.client.request(method="execute/script/evaluate", body={'script': code})

            # 如果有异常，需要析构内核工具
            if (response["value"] != 'null'):
                self.client.request(method="execute/script/evaluate",
                                    body={'script': f'Application.Workbooks.Close("{case_save_path}")'})
                del self.client
                self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
                # raise ValueError
            else:
                self.client.request(method="execute/script/evaluate",
                                    body={'script': f'Application.ActiveWorkbook.SaveAs("{case_run_save_path}")'})
                self.client.request(method="execute/script/evaluate",
                                    body={'script': f'Application.Workbooks.Close("{case_save_path}")'})

        except requests.exceptions.ReadTimeout as e:
            print("样张执行超时")
            del self.client
            time.sleep(3)
            self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Close("{case_save_path}")'})
            shutil.copy(case_save_path_o, case_run_save_path_o)
            response = {"isSuccess": False, "value":"样张执行超时"}

        except ValueError as e:
            print("代码执行失败")
            del self.client
            self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
            self.client.request(method="execute/script/evaluate",
                                body={'script': f'Application.Workbooks.Close("{case_save_path}")'})
            shutil.copy(case_save_path_o, case_run_save_path_o)
            response = {"isSuccess": False, "value":"代码执行失败"}



        try:
            ws1 = self.load_workbook_with_timeout(case_save_path_o, 5).active
            sheet_name = ws1.title
            ws2 = self.load_workbook_with_timeout(case_run_save_path_o, 5)[sheet_name]
        except:
            return (False, "执行样张读取异常（可能超长或存在异常值）") if (response["value"] == 'null') else (False, response["value"])
        # 获取最大行和最大列
        max_row = max(ws1.max_row, ws2.max_row)
        max_column = get_column_letter(ws1.max_column) if ws1.max_column>ws2.max_column else get_column_letter(ws2.max_column)
        # 获取最小行和最小列
        min_row = min(ws1.min_row, ws2.min_row)
        min_column = get_column_letter(ws1.min_column) if ws1.min_column>ws2.min_column else get_column_letter(ws2.min_column)

        range_column = f"{min_column}:{max_column}"
        range_row = f"{min_row}:{max_row}"

        case_set_code = f"""function Macro() {{
            Application.Workbooks.Open("{case_save_path}")
            col_table1 = Range("{range_column}")
            col_table1.ColumnWidth = col_table1.ColumnWidth
            row_table1 = Range("{range_row}")
            row_table1.RowHeight = row_table1.RowHeight
            Application.ActiveWorkbook.SaveAs("{case_save_path}")
            Application.Workbooks.Close("{case_save_path}")
            
            Application.Workbooks.Open("{case_run_save_path}")
            Sheets.Item("{sheet_name}").Activate()
            col_table2 = Range("{range_column}")
            col_table2.ColumnWidth = col_table2.ColumnWidth
            row_table2 = Range("{range_row}")
            row_table2.RowHeight = row_table2.RowHeight
            Application.ActiveWorkbook.SaveAs("{case_run_save_path}")
            Application.Workbooks.Close("{case_run_save_path}")
}} Macro()"""
        try:
            self.client.request(method="execute/script/evaluate", body={'script': case_set_code})
        except:
            self.client = WpsdriverClient(executablePath=self.client_path, product=Product.ET)
            self.client.request(method="execute/script/evaluate", body={'script': case_set_code})


        run_flag = (True, "") if (response["value"] == 'null') else (False, response["value"])

        return run_flag

    def list_subdirectories(self, root_dir):
        res = {}
        # 使用 glob 模块匹配所有子文件夹
        pattern = os.path.join(root_dir, '**')
        subdirectories = glob.glob(pattern)

        # 过滤掉根目录本身
        subdirectories = [d for d in subdirectories if d != root_dir and not os.path.basename(d).startswith("~$")]
        for path in subdirectories:
            name = os.path.basename(path).split(".xlsx")[0]
            res[name] = path
        return res

    def get_code(self, all_pair_path_dict):
        code_dict = {}
        with open(self.json_file_path, "r", encoding='utf-8') as f:
            for line in f:
                json_dict = json.loads(line)

                input = json_dict[self.data_mapping_dict["input"]]
                code = json_dict[self.data_mapping_dict["target"]]
                if self.mode=="r1":
                    if "</think>" not in code:
                        print("mode为r1，但是数据中并不包含</think>")
                        continue
                    code = code.split("</think>")[-1]
                    try:
                        code = re.findall(r"```javascript(.*?)```", code, re.DOTALL)[-1]
                    except:
                        code = code[code.rfind("function Macro"):code.rfind("}") + 1]


                if code:
                    code, _ = add_functions(code, input)
                    code, _ = extra_dataseries(code)
                try:
                    case_path = all_pair_path_dict[str(json_dict[self.data_mapping_dict["md5"]])]
                    code_dict[case_path] = (code, input)
                except:
                    case = str(json_dict[self.data_mapping_dict["md5"]])
                    print(f"样张生成失败: {case}")
                    continue
        return code_dict


    def collection_result(self):
        self.collection_wb = openpyxl.Workbook()
        # 选择一个工作表（例如，第一个工作表）
        self.collection_sheet = self.collection_wb.active
        self.collection_sheet.title = "样张执行结果"
        header = ["表格名(md5)", "表格描述", "代码", "原始样张路径", "结果样张路径", "运行是否成功", "运行信息", "执行前后差异信息", "执行前后是否有变化"]
        header_fill = {"1-2": "DAEEF3", "3-3": "FDE9D9", "4-9": "DA9694"}
        column_width = [20, 50, 80, 20,20,20,20, 20,20]
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
        del self.client

    @timer_decorator
    def run_all(self, worker_number):
        all_pair_path = self.list_subdirectories(self.cases_root_path)
        code_dict = self.get_code(all_pair_path)
        self.collection_dict_gen_sheet = {}
        for case_path in tqdm(code_dict, desc="执行样张中..."):
            basename = os.path.basename(case_path).split(".xlsx")[0]
            code, table = code_dict[case_path]
            case_path = case_path.replace("\\", "\\\\")
            case_save_path = os.path.join(self.target_root_path, basename,basename+"_原始样张.xlsx")
            case_run_save_path = os.path.join(self.target_root_path, basename,basename+"_执行样张.xlsx")
            self.check_path_and_create(os.path.join(self.target_root_path, basename))
            if code:
                run_flag, run_info = self.run_paired_data((code, table), case_path, case_save_path, case_run_save_path)
            else:
                run_flag, run_info = False, "代码缺失"
            # ["表格名(md5)", "表格描述", "代码", "原始样张路径", "结果样张路径", "执行前后是否有变化", "运行是否成功", "运行信息"]
            self.collection_dict_gen_sheet[basename] = [basename, table, code, case_save_path, case_run_save_path, run_flag, run_info]
        all_pair_path = self.compare_client.list_subdirectories(self.target_root_path)
        for key in self.collection_dict_gen_sheet:
            if self.collection_dict_gen_sheet[key][-2]==False:
                all_pair_path.pop(key)
        _,_,results = self.compare_client.run(all_pair_path, worker_number=worker_number)

        for res in results:
            try:
                name = res["compare_sheets"][0].split("\\")[-2]
            except:
                print("缺少样张")
                continue
            if not res["sheet_format"]: diff_res = ",   ".join([",   ".join(i) for i in res["cells_diff"]])
            elif not res["cells_diff"]: diff_res = ",   ".join(res["sheet_format"])
            else: diff_res = ",   ".join(res["sheet_format"]) + ",   "+",   ".join([",   ".join(i) for i in res["cells_diff"]])
            diff_flag = True if diff_res else False

            if "校验样张解析错误" in diff_res or "表格缺少样张" in diff_res or not diff_res or "样张读取超时" in diff_res or not diff_res or "表格样张数量异常，请见审查核对" in diff_res:
                diff_out_res = diff_res
            else:
                diff_out_res = nested_dict_from_string(diff_res)


            self.collection_dict_gen_sheet[name] = self.collection_dict_gen_sheet[name]+ [diff_out_res]+[diff_flag]


        self.result_to_xlsx(self.collection_dict_gen_sheet)

        return self.xlsx_save_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser("执行样张配置")
    parser.add_argument("--config", type=str, help="Add your case path", default=r"configs\config_run_code.yaml")
    args = parser.parse_args()
    main = runCode(config_path=args.config, data_mapping_dict=None)
    main.run_all(worker_number=16)