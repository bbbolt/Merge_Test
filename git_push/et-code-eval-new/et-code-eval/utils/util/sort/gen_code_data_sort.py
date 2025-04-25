import sys
import os
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import re
from json_to_js.sort.functions import FUNCTIONS, FUNCTIONS_MAP, MARCO_FUNC, TASK_CODE, CONTEXT_CODE
from json_to_js.utils import format_example, add_functions_subtasks, python_dict_to_js_dict
import json
from data_process.utils import fullwidth_to_halfwidth, gen_table_structure_js


def get_js_code(input_json_lst):

    query_json_code = ""
    final_api_set = set()
    for idx, input_json in enumerate(input_json_lst):
        if input_json.get('filter_type'):
            input_json['filterType'] = input_json['filter_type']
            del input_json['filter_type']
        task_para_code = TASK_CODE.replace("<<<PARA_DEF_CODE>>>", python_dict_to_js_dict(input_json))
        task_para_code = task_para_code.replace("let task ", "let task_{} ".format(idx))
        if idx == 0:
            context_code = "    " + "let [task_{}_{}, targetWorksheet, currentRange, context] = get_context(task_{})".format(idx, idx, idx) + '\n'
        else:
            context_code = "    " + "let [task_{}_{}, targetWorksheet_{}, currentRange_{}, context_{}] = get_context(task_{})".format(idx, idx,idx, idx, idx,idx) + '\n'
        function_api_code = FUNCTIONS_MAP[input_json['ID']].replace("task", "task_{}_{}".format(idx, idx))
        query_json_code += task_para_code + '\n' + context_code + '\n    ' + function_api_code + '\n'
    
        # 只需要从其中一类递归
        # 起始code用于判断二级分类，不需要加入到最终code文本，用特殊标记方便后面删除
        js_code = FUNCTIONS_MAP[input_json['ID']]
        js_api_set = add_functions_subtasks(js_code, FUNCTIONS)
        final_api_set = final_api_set | js_api_set
    
    
    marco_code = MARCO_FUNC.replace("<<<TASK_CODE_AND_FUNC_CODE>>>", query_json_code) 

    code = ""
    for js_api in final_api_set:
        code += '\n' + FUNCTIONS[js_api] + '\n'
    
    total_api_lst = list(final_api_set) + ['GetActiveRange', 'get_context']

    comments = """// 以下为工具函数，使用的工具函数列表为{}""".format(json.dumps(total_api_lst, ensure_ascii=False)) + '\n'
    sep_tok= """//$$$""" + '\n'
    # 长函数的样子
    # final_code = marco_code + comments + sep_tok + CONTEXT_CODE + code
    # 更改为去掉后面完整函数的样子
    final_code = marco_code + comments + sep_tok

    return final_code
                                                          

if __name__ == '__main__':

    file_path = "/home/wps/Desktop/temp/sort"
    for file in os.listdir(file_path):
        if not file.endswith(".json"):
            continue
        file_abs_path = os.path.join(file_path, file)
        fsave_path = os.path.join(file_path, "function_js", file.replace(".json", "_sft_js_test.json"))
        print(fsave_path)
        fsave = open(fsave_path, 'w')
        
        # sft data maker
        with open(file_abs_path, 'r') as f:
            for line in f:
                line = json.loads(line)
                input_json = line["output"]
                input_json_lst = json.loads(input_json)["subtasks"]
                try:
                    table = gen_table_structure_js(fullwidth_to_halfwidth(line["table_structure"]))
                    if not table:
                        # print(line)
                        continue
                    line["table_structure"] = table
                    # table = '/*\n' + table + '\n*/\n'
                    # save_dict = {"text": table + f'// {line["ori_instruction"]}\n' + get_js_code(input_json_lst)}
                    # save_dict = {"input": format_example(line), "target": f'// {line["ori_instruction"]}\n' + get_js_code(input_json_lst)}
                    save_dict = {"input": format_example(line), "target": get_js_code(input_json_lst)}
                    fsave.write(json.dumps(save_dict, ensure_ascii=False) + "\n")
                except:
                    pass

        fsave.close()
