'''
-*- coding: utf-8 -*-
@File  : check_label_data_base_api.py
@author: Maoyanyu
@Time  : 2025/01/16 11:37
'''
import argparse
import hashlib
import json
import os

import yaml
import time
from utils.gen_sheets import get_sheets
from tools.apply_code import runCode as apply_code_func
from utils.llm_filter_label import llm_filter

def generate_md5(text):
    # 创建一个MD5哈希对象
    md5_hash = hashlib.md5()

    # 更新哈希对象以包含要哈希的文本
    md5_hash.update(text.encode('utf-8'))

    # 获取十六进制表示的哈希值
    md5_hex = md5_hash.hexdigest()

    return md5_hex


def main(args):

    # 生成样张并执行

    file_json_dict = []
    with open(args.data_path, mode="r", encoding="utf-8") as f:
        for line in f: file_json_dict.append(json.loads(line))
    for json_dict in file_json_dict:
        if "md5" in json_dict.keys():
            continue
        else:
            json_dict["md5"] = generate_md5(json_dict["input"])

    # 如果需要将JSON数据保存到文件中
    with open(args.data_path, 'w', encoding='utf-8') as json_file:
        for line in file_json_dict:
            json_file.write(json.dumps(line, ensure_ascii=False) + "\n")



    start = time.time()
    get_sheets(args)
    gen_time = time.time() - start

    # 获取样张路径 + 数据路径 ---> 执行样张

    # 读取 YAML 文件
    with open(args.apply_code_config, 'rb') as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(e)

    data["base_path"] = os.path.dirname(args.sheets_output_path)
    data["dataset"]["cases_root_path"] = os.path.basename(args.sheets_output_path)
    data["val"]["json_file_path"] = args.data_path


    # 将修改后的数据写回 YAML 文件
    with open(args.apply_code_config, 'w') as file:
        yaml.safe_dump(data, file)

    start = time.time()
    apply = apply_code_func(config_path=args.apply_code_config)
    apply.run_all(worker_number=1)
    apply_code_time = time.time() - start


    start = time.time()
    run_code_xlsx_path = apply.xlsx_save_path
    llm_filter(run_code_xlsx_path, args.judge_model_type)
    llm_filter_time = time.time() - start

    print(f"执行总耗时: {gen_time} s | 执行总耗时: {apply_code_time} s | 模型裁决总耗时: {llm_filter_time} s | 共计耗时: {gen_time+apply_code_time+llm_filter_time} s")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='gen sheet')

    parser.add_argument('--data_path', type=str, help='data_path',default=r"C:\Users\Bolt\PycharmProjects\et-code-eval\case\1216_online_train_data_x.json")
    parser.add_argument('--sheets_output_path', type=str, help='sheets_output_path',default=r"C:\Users\Bolt\PycharmProjects\et-code-eval\gen_sheets\1216_online_train_data_x\1216_online_train_data_x")
    parser.add_argument('--apply_code_config', type=str, help='apply_code_config',default=r"configs\config_run_code.yaml")

    parser.add_argument('--gen_sheet_model_type', type=str, help='model_type',default=r"")
    parser.add_argument('--judge_model_type', type=str, help='model_type',default=r"")
    args = parser.parse_args()

    main(args)
