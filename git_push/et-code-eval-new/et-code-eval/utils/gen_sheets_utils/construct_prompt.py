from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
from tqdm import tqdm
import json
import torch
import re
import argparse
import os
import hashlib

def generate_md5(text):
    # 创建一个MD5哈希对象
    md5_hash = hashlib.md5()

    # 更新哈希对象以包含要哈希的文本
    md5_hash.update(text.encode('utf-8'))

    # 获取十六进制表示的哈希值
    md5_hex = md5_hash.hexdigest()

    return md5_hex


def distill_sample_item(data_path):
    res = []
    file_json_dict = []
    with open(data_path, mode="r", encoding="utf-8") as f:
        for line in f: file_json_dict.append(json.loads(line))

    for json_dict in tqdm(file_json_dict, desc="提取表格描述 ---> Prompts"):
        cols = re.findall(r"\{[\"']*([A-Za-z\d]+)[\"']*,\s*[\"']*(.*?)[\"']*,\s*[\"']*(.*?)[\"']*\}", json_dict["input"], re.DOTALL)
        try:
            stt_row, end_row = re.findall(r"内容起始行号为(\d+).*?终止行号为(\d+)", json_dict["input"], re.DOTALL)[0]
            question = re.findall(r"需求“(.*?)”", json_dict["input"], re.DOTALL)[0]
        except: 
            stt_row, end_row = "2", "20"
            cols = [["A","",""], ["B","",""], ["C","",""], ["D","",""], ["E","",""]]
            question = re.findall(r"需求“(.*?)”", json_dict["input"], re.DOTALL)[0]

        sheet = []
        num_gen = eval(end_row)-eval(stt_row)+1
        for col in cols:
            col_idx = col[0]
            if col[2]=="":
                input = f"""我现在想生成一列一列的生成表格数据，请根据以下用户问题，当前列列名生成10个质量较高的新样例值，新样例值之间用$$分隔，不包含任何额外内容。
用户问题: {question}
当前列{col_idx}列列名：{col[1]}

要求：
生成的值结构和逻辑需与列名和样例值一致。
仅输出生成的结果，数据之间用$$分隔。
避免重复和乱码，确保生成数据合理。
如果没有具体列名和样例值，请生成符合逻辑和常识的数据样例。
如果用户问题中对某列中数值有特殊要求，如果与当前列无关，则忽略并正常生成数据即可，如果相关，则需要按照用户说明的类型来生成样例值。"""
            else:
                input = f"""我现在想生成一列一列的生成表格数据，请根据以下用户问题，当前列列名和样例值生成10个质量较高的新样例值，新样例值之间用$$分隔，不包含任何额外内容。
用户问题: {question}
当前列{col_idx}列列名：{col[1]}
样例值：{col[2]}

要求：

生成的值结构和逻辑需与列名和样例值一致。
仅输出生成的结果，数据之间用$$分隔。
避免重复和乱码，确保生成数据合理。
如果没有具体列名和样例值，请生成符合逻辑和常识的数据样例。
如果用户问题中对某列中数值有特殊要求，如果与当前列无关，则忽略并正常生成数据即可，如果相关，则需要按照用户说明的类型来生成样例值。"""
            sheet.append([col[0], col[1], input])
        if "md5" in json_dict.keys():
            res.append({json_dict["input"]:sheet, "md5":json_dict["md5"]})
        else:
            res.append({json_dict["input"]:sheet, "md5":generate_md5(json_dict["input"])})


    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--data_path', type=str, help='data_path', default="/home/kas/x_gen_code_sheet/JS_train_1121_13c_new_1k.json")

    args = parser.parse_args()
    distill_sample_item(args)

