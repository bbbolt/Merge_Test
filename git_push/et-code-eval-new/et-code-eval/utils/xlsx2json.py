import argparse
import os

import openpyxl
import json

def xlsx2json(xlsx_path, json_out_path, input_header, target_header):

    # 打开Excel文件
    workbook = openpyxl.load_workbook(xlsx_path)
    sheet = workbook.active

    # 获取列名所在的行
    header = [cell.value for cell in sheet[1]]

    # 找到列名对应的列索引
    prompt_index = header.index(input_header)
    code_index = header.index(target_header)

    # 初始化一个空列表来存储字典
    data_list = []

    # 遍历每一行（从第二行开始，因为第一行是列名）
    for row in sheet.iter_rows(min_row=2, values_only=True):
        prompt = row[prompt_index]
        code = row[code_index]
        if not code: continue
        if not code.strip(): continue
        # 创建字典并添加到列表中
        data_dict = {
            "input": prompt,
            "target": code
        }
        data_list.append(data_dict)

    # 如果需要将JSON数据保存到文件中
    # 如果目标目录不存在，则创建目标目录
    if not os.path.exists(os.path.dirname(json_out_path)):
        os.makedirs(os.path.dirname(json_out_path))
    with open(json_out_path, 'w', encoding='utf-8') as json_file:
        for line in data_list:
            json_file.write(json.dumps(line, ensure_ascii=False) + "\n")

    return json_out_path

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='gen sheet')

    parser.add_argument('--xlsx_path', type=str, help='xlsx_path')
    parser.add_argument('--json_out_path', type=str, help='json_out_path')
    args = parser.parse_args()

    xlsx2json(args.xlsx_path, args.json_out_path)