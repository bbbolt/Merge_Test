'''
-*- coding: utf-8 -*-
@File  : main_compare.py
@author: Maoyanyu
@Time  : 2024/12/18 17:02
'''
import argparse
import json
import time
from multiprocessing import Process, Queue, Manager
import re
from tqdm import tqdm
from utils.sheet_compare import DeepSearch
import glob
import os

class BatchCompare():
    def __init__(self):
        self.ds = DeepSearch()
        self.res = []

    def list_subdirectories(self, root_dir):
        result = {}
        # 使用 glob 模块匹配所有子文件夹
        pattern = os.path.join(root_dir, '**')
        subdirectories = glob.glob(pattern)

        # 过滤掉根目录本身
        subdirectories = [d for d in subdirectories if d != root_dir]
        for subpath in subdirectories:
            # 分别获取 .xlsx 和 .xls 文件
            xlsx_files = glob.glob(os.path.join(subpath, 'result_case', '*.xlsx'))
            xls_files = glob.glob(os.path.join(subpath, 'result_case', '*.xls'))

            if len(xls_files) > 2:
                excel_file_paths = xls_files
            else:
                excel_file_paths = xlsx_files

            # 过滤掉包含 "##" 的路径
            filtered_subdirectories = [d for d in excel_file_paths if '原始样张' not in d]
            result[subpath] = filtered_subdirectories

        return result

    def compare_pair(self, files):
        if len(files) < 2:
            return (["表格缺少样张"], [])
        elif len(files) > 2:
            return (["表格样张数量异常，请见审查核对"], [])
        file1, file2 = files
        # print(file1)
        diff = self.ds.run_compare(file1, file2, self.code_dict)
        return diff

    def worker(self, task_queue, result_queue):
        # tbar = tqdm(range(1142))
        while True:
            task = task_queue.get(timeout=5)
            if task is None:
                print("执行完毕...")
                break
            index, files = task
            # print(f"\nIndex: {256+16 - task_queue.qsize()}", end="", flush=True)
            # tbar.update(1)
            result = self.compare_pair(files)
            result_queue.append((index, result))


    def run(self, all_pair_path, log_path, worker_number=1, code_dict=None):
        self.code_dict=code_dict
        manager = Manager()
        # 创建任务队列和结果队列
        task_queue = Queue()
        result_queue = manager.list()

        all_pair_path = self.list_subdirectories(all_pair_path)
        all_pair_path_keys = list(all_pair_path.keys())
        all_pair_path_keys = sorted(all_pair_path_keys, key=lambda x: int(re.findall(r"\\(\d+)", x)[-1]))
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
                cur_res["index"] = int(re.findall(r"\\(\d+)", index[0])[0])
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser("校验工具配置")
    parser.add_argument("--case_path", type=str, help="Add your case path", default="")
    args = parser.parse_args()
    bc = BatchCompare()
    a = time.time()
    right, wrong, _ = bc.run(args.cases_path,"log.log",1)
    b = time.time()
    print("Right: ", right)
    print("Wrong: ", wrong)
    print(f"整体通过率：{right / (right + wrong)}")
    print("ETA: ", b - a)
