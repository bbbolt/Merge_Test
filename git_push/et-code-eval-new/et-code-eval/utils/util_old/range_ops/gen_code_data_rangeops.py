#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/19 下午17:00
# @Author  : ZCX
# @File    : gen_code_data_rangeops_js.py.py
import json
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_process.utils import fullwidth_to_halfwidth
from data_process.change_table import gen_table_structure_js_newtable_from_json
from functions import FUNCTIONS, FUNCTIONS_MAP, COMMON_CODE, TASK2FUNC_MAP, MARCO_FUNC, TASK_CODE, \
    COMMON_FUNC_LST, CONTEXT_CODE
from json_to_js.utils import format_example, add_functions_subtasks, python_dict_to_js_dict
# from data_process.gen_vd_js import gen_table_structure_js

JS_PROMPT = """
以下是描述任务的说明。编写适当地完成请求的响应。\n\n### 指令：\n假如你是一个Excel专家，并且精通使用JavaScript语言操作Excel，{table_info}。请根据需求“{question}”编写一个JavaScript宏函数。\n\n### 
"""




"""
接受一个json列表作参数，生成相应的js代码，其中循环遍历输入的Json列表，对每个对象执行以下操作
"""
def get_js_code(input_json_lst):
    
    
    query_json_code = ""
    final_api_set = set()
    

    for idx, input_json in enumerate(input_json_lst):



        task_para_code = TASK_CODE.replace("<<<PARA_DEF_CODE>>>", python_dict_to_js_dict(input_json))#使用TASK_CODE替换<<<PARA_DEF_CODE>>>部分，得到任务参数的Js
        task_para_code = task_para_code.replace("let task ", "let task_{} ".format(idx))#let task_0 = {"ID": 'CLOP_AUTOFITROW', "rows": '1:3'}
        context_code = "    " + "let [tableRange,targetRange,currentRange] = get_context(task_{})".format(idx) + '\n'#targetRange = get_context(task_0)
        function_api_code = TASK2FUNC_MAP[input_json['ID']] + "(tableRange, targetRange, currentRange, task_{})".format(idx)
        query_json_code += task_para_code + '\n' + context_code + '\n    ' + function_api_code + '\n'

        # print("--------")
        # print(function_api_code)
        # print("--------")

        # 只需要从其中一类递归
        # 起始code用于判断二级分类，不需要加入到最终code文本，用特殊标记方便后面删除
        js_code = "***" + FUNCTIONS_MAP[input_json['ID']] + "***"
        js_api_set = add_functions_subtasks(js_code, FUNCTIONS)
        #print(js_api_set)
        final_api_set = final_api_set | js_api_set
        final_api_set.add("GetUnionTableRange") 
        #print(js_api_set)
        #print(final_api_set)
        
    marco_code = MARCO_FUNC.replace("<<<TASK_CODE_AND_FUNC_CODE>>>", query_json_code)
    # final_api_set.union(js_api_set)
    code = ""
    for js_api in final_api_set:
        if js_api in COMMON_FUNC_LST:
            continue
        code += '\n' + FUNCTIONS[js_api] + '\n'

    total_api_lst = list(set(COMMON_FUNC_LST) | final_api_set) + ['get_context']
    comments = """// 以下为工具函数，使用的工具函数列表为{}""".format(json.dumps(total_api_lst, ensure_ascii=False)) + '\n'
    sep_tok = """//$$$""" + '\n'
    #final_code = marco_code + comments + sep_tok
    final_code = marco_code + comments + sep_tok + CONTEXT_CODE + COMMON_CODE + code
    return final_code


if __name__ == "__main__":
    #读取路径
    folder_path = '/home/kas/kas_workspace/liuyujia/copilot/data/aug_data/ro'  # 替换为你的文件夹路径
      
    #保存路径




     # 遍历指定目录及其所有子目录  
    for subdir, dirs, files in os.walk(folder_path):  
        # 在当前子目录中查找以"CLOP"开头的.json文件  
        for file in files:  
            if file.startswith('clop') and file.endswith('.json') and 'MERGE' not in file:  
                try:
                    #print(file)
                    file_path = os.path.join(subdir, file) 
                    f_path="/home/kas/kas_workspace/zhaochuanxu/os/os/"+file#保存路径
                    fsave_path = f_path.replace(".json", "_js.json")
                    fsave = open(fsave_path, 'w')
                    fsave = open(fsave_path, 'w')
                    with open(file_path, 'r') as f:
                        for line in f:
                                line = json.loads(line)
                                input_json = line["output"]
                                input_json_lst = json.loads(input_json)["subtasks"]
                                code=get_js_code(input_json_lst)
                                print(code)


                                # 获取新的表结构
                                table = line["table_structure"]
                                table = fullwidth_to_halfwidth(table)
                                if not table:
                                    continue
                                
               
                                line["table_structure"] = table
                               
                                table = line["table_structure"]
                                table = gen_table_structure_js_newtable_from_json(table)
                                #print(table)
                                line["table_structure"]=table
                                lines=dict()
                                lines['target'] = code
                                lines["input"] = format_example(line)

                                #print(json.dumps(lines,ensure_ascii=False))
                                fsave.write(json.dumps(lines, ensure_ascii=False) + "\n")
                except:
                    import traceback
                    traceback.print_exc()
                    pass
 

        # with open(file_path, "r") as f:
        #     for line in f:
        #         line = json.loads(line)
        #         command = json.loads(line["target"])

        #         if len(command["subtasks"]) > 1:
        #             # 暂时忽略多个subtask的
        #             continue


        #         task = command["subtasks"][0]
        #         task_name = task["ID"]
        #         task_name = task_name.replace("HYB", "HYP")
        #         if task_name not in class_map:
        #             continue
        #         pipline = class_map[task_name]
        #         # 获取相应代码
        #         code = pipline(task)

        #         # 获取新的表结构
        #         table = line["table_structure"]
        #         table = fullwidth_to_halfwidth(table)
        #         if not table:
        #             continue
        #         line["table_structure"] = table

        #         # line['question'] = line['instruction']
        #         line['target'] = code
        #         # line['json_output'] = line['output']
                
        #         print(code)

        #         # line['input'] = JS_PROMPT.format_map({"table_info": table, "question": line['question']})
        #         line['dirname'] = filename

        #         fsave.writelines(json.dumps(line, ensure_ascii=False) + '\n')

