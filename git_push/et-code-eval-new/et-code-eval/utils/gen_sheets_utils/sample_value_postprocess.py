from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
from tqdm import tqdm
import json
import torch
import re
import argparse
import os
import random

def postprocess(json_dict):
    prompt = list(json_dict.keys())[0]
    try:
        stt_row, end_row = re.findall(r"内容起始行号为(\d+).*?终止行号为(\d+)", prompt, re.DOTALL)[0]
        question = re.findall(r"需求“(.*?)”", prompt, re.DOTALL)[0]
        num_row = eval(end_row)-eval(stt_row)+1
        max_row = min(num_row,2000)
        sheet_desc = json_dict[prompt]
        for idx, col in enumerate(sheet_desc):
            cur_col_list = col[2]
            # 检查列表长度，如果超过20，则截断
            if len(cur_col_list) > max_row:
                cur_col_list = cur_col_list[:max_row]
            # 检查列表长度，如果不足20，则重复元素直到长度达到20
            while len(cur_col_list) < max_row:
                cur_col_list.extend(cur_col_list[:max_row - len(cur_col_list)])
            # 随机打乱列表
            random.shuffle(cur_col_list)
            col[2] = cur_col_list
            sheet_desc[idx] = col
        json_dict[prompt] = sheet_desc
    except:
        return json_dict
    return json_dict



def postprocess_func(file_json_dict):

    for idx, json_dict in enumerate(tqdm(file_json_dict,desc="样例值后处理")):
        file_json_dict[idx] = postprocess(json_dict)

    return file_json_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--data_path', type=str, help='data_path', default="/home/kas/x_gen_code_sheet/gen_sheets_desc_postprocess/2025-01-02_gen_sheet_Qwen2.5-3B-Instruct.json")
    parser.add_argument('--output', type=str, help='output', default="/home/kas/x_gen_code_sheet/gen_sheets_desc_postprocess/2025-01-02_gen_sheet_Qwen2.5-3B-Instruct")

    args = parser.parse_args()
    postprocess_func(args)

