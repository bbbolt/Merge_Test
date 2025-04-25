# -*- coding: utf-8 -*-
# @Time : 2025/2/10 上午11:36
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : chat_with_gateway.py
# -*- coding: utf-8 -*-
# @Time : 2024/9/11 下午3:23
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : chat_t.py
# -*- coding: utf-8 -*-
import os
import random
import time

import json
import re

import openpyxl
import requests
import time
import sys
from const.prompt_text import FORMATCONDITION

# from wpsdriverserv import WpsdriverClient, Product

# sys.path.append("/mnt/DATA/workspace/ks_code/copilot-instruction/const")
# sys.path.append('/home/kas/sunyuzhao/copilot-instruction')
# from const import const

score_pattern = r"回答\d+：\d+分"
rank_pattern = r"回答\d+(?:>[回答\d]+)*"

AZURE_API = "https://ai-proxy-test.ksord.com/wps.openai.azure.com/openai/deployments/35/chat/completions?api-version=2023-07-01-preview"
AZURE_API_2 = 'http://aigc-gateway-test.ksord.com/api/v2/llm/chat'
# AZURE_API_2 = 'http://aigc-gateway-test.ksord.com/api/v2/llm/multimodal'
# AZURE_API_2 = 'https://ai-copilot-gateway.ksord.com/api/v2/llm/multimodal'
# AZURE_API_2 = 'https://ai-copilot-gateway.ksord.com/api/v2/llm/chat'

TIMEOUT_CONVERT = 500


class ChatGptService_v2():
    """
    chatgpt封装
    model_name可选: ['gpt-35-turbo', 'gpt-4']
                       ↕                ↕
    version可选:    ['0125',         '1106-Preview']

    """

    # def __init__(self, url=AZURE_API_2, model_name="claude-3-5-sonnet", stream=False, provider="aws",
    #              version="20240620-v1:0",
    #              temperature=0.7, frequency_penalty=1, presence_penalty=0, max_tokens=2048, top_p=1):
    def __init__(self, url=AZURE_API_2, model_name="deepseek-reasoner", stream=False, provider="deepseek",
                 version="",
                 temperature=0.6, frequency_penalty=1, presence_penalty=0, max_tokens=2048, top_p=1):

        # def __init__(self, url=AZURE_API_2, model_name="gpt-35-turbo", stream=False, provider="zure",
        #                  version="0125",
        #                  temperature=0.7, frequency_penalty=1, presence_penalty=0, max_tokens=2048, top_p=1):
        self.url = url
        self.api_key = "Bearer ILAeolU2HbRNxiSOlc1m8L3jNkFWib1y"
        # self.api_key = "Bearer n0JiI8I3sr67qWt36ZSM1jlvrIfDaIKN"
        self.provider = provider
        self.version = version
        # print("api_key:", self.api_key)
        self.model = model_name
        self.stream = stream
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.max_tokens = max_tokens
        self.top_p = top_p
        req_id = str(int(time.time())) + "_" +str(random.randint(100000,999999)) + "_"+str(random.randint(10,99))
        self.__headers = {
            "Authorization": self.api_key,
            "AI-Gateway-Uid": "9055",
            "AI-Gateway-Product-Name": "wps_aigctest_ainlp",
            "AI-Gateway-Intention-Code": "aigctest",
            "Content-Type": "application/json",
            "Client-Request-Id":req_id
        }
        print(req_id)

    def __gpt_request_data(self, query):
        """
        model_name可选: ['gpt-35-turbo', 'gpt-4']
                           ↕                ↕
        version可选:    ['0125',         '1106-Preview']

        """

        return {
            "stream": True,
            "context": "",
            "messages": [
                {
                    "role": "user",
                    # "content": [
                    #     {
                    #         "type": "text",
                    #         "content": "{}".format(query),
                    #     }
                    # ]
                    "content": "{}".format(query)

                }
            ],
            "model": "deepseek-reasoner",
            "provider": "deepseek",
            "version": "",
            "base_llm_arguments": {
                "temperature": 0.6,
                "top_p": 0.9,
                "top_k": 50,
                "max_tokens": 10000,
                "stop": []
            },
            "sec_text": {
                "from": "",
                "scene": ""
            },
            "retry_strategy": {
                "retry_count": 2,
                "timeout": 60
            }
        }

    def __send_ask_without_stream(self, data):
        retry_count = 0
        while retry_count <= 3:
            try:
                s = requests.Session()
                s.mount(
                    "https://",
                    requests.adapters.HTTPAdapter(max_retries=3),
                )

                res = s.request(
                    'POST',
                    url=self.url,
                    json=data,
                    timeout=TIMEOUT_CONVERT,
                    headers=self.__headers,
                    stream=True
                )
                re_js = json.loads(res.text)
                print(re_js)
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc()
                retry_count += 1
                re_js = None

        return re_js

    def __send_ask_with_stream(self, data):
        retry_count = 0
        completion_tokens = 0
        p_tokens = 0
        while retry_count <= 3:
            text = ""
            reasoning_content = ""
            try:
                s = requests.Session()
                s.mount(
                    "https://",
                    requests.adapters.HTTPAdapter(max_retries=3),
                )

                res = s.request(
                    'POST',
                    url=self.url,
                    json=data,
                    timeout=TIMEOUT_CONVERT,
                    headers=self.__headers,
                    stream=True
                )
                for line in res.iter_lines():
                    if len(line) < 2:
                        continue

                    line = line.decode('UTF-8')
                    index = line.find("data:")
                    key = line[:index]
                    # if not key == "data":
                    #     log.app_logger.warning(
                    #         "request_id:%s receive non data message, key:%s", request_id, key)
                    #     continue
                    output = json.loads(line[index + 5:])
                    text += output["choices"][0]["text"]
                    completion_tokens += output['usage']['completion_tokens']
                    p_tokens = output['usage']['prompt_tokens']
                    reasoning_content += output["choices"][0].get("reasoning_content", "")
                    print(output)

                # if res:
                print(reasoning_content)
                print(p_tokens)
                print(completion_tokens)
                return text, reasoning_content
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc()
                retry_count += 1
                re_js = None

        return text, reasoning_content

    def complete(self, prompt='你好吗?'):
        data = self.__gpt_request_data(prompt)
        print(data)
        completion = self.__send_ask_with_stream(data)
        try:
            completion_text = completion['choices'][0]['text']
            reasoning_content = completion['choices'][0].get('reasoning_content', "")
        except:
            print("1111")
            import traceback
            traceback.print_exc()
            return None

        return completion_text, reasoning_content, completion['usage']['prompt_tokens'], completion['usage']['completion_tokens']

    def complete_stream(self, prompt='你好吗?'):
        data = self.__gpt_request_data(prompt)
        print(data)
        text, reasoning_content = self.__send_ask_with_stream(data)

        return text, reasoning_content

    def get_completion(self, prompts):
        # 调用示例
        results = []
        for prompt in prompts:
            raw_res = self.complete(prompt=prompt)
            if not raw_res: continue
            results.append(raw_res)
        return results

    @staticmethod
    def split_list(cls, lst, num_splits):
        """
        将一个 list 切分为 num_splits 份
        :param lst: 要切分的 list
        :param num_splits: 切分成的份数
        :return: 切分后的 list 列表
        """
        if not lst:
            return []

        # 计算每份的大小
        size = (len(lst) + num_splits - 1) // num_splits

        # 将 list 按照每份大小切分成若干份
        return [lst[i:i + size] for i in range(0, len(lst), size)]


def gen_labeld_xlsx(text, xlsx_filename):
    try:
        sheet_names = re.search("所有工作表的名称如下：(.*?)，当前", text).group(1)
    except:
        print(text)
        return None
    sheet_names = eval(sheet_names)
    cur_sheet_name = re.search(r'当前工作表名称为：(.*?)，', text).group(1)

    # 使用正则表达式提取表头信息
    headers_match = re.findall(r'\{"([A-Z]+)\d*",\s*"([^,]+)",\s*"([^,]*)"\}', text)

    header_start_row = int(re.search(r'表头起始行号为(\d+)', text).group(1))
    start_row = int(re.search(r'内容起始行号为(\d+)', text).group(1))
    end_row = int(re.search(r'内容起始行号为\d+，终止行号为(\d+)', text).group(1))
    # print(end_row)

    # 创建一个新的Excel工作簿
    workbook = openpyxl.Workbook()

    # 获取当前活动的工作表
    # workbook.active.title = cur_sheet_name
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    for sheet_name in sheet_names:
        workbook.create_sheet(title=sheet_name)
    try:
        workbook.active = workbook[cur_sheet_name]
    except:
        print("cur 不存在")
        raise Exception("当前工作表不存在")
    sheet = workbook.active
    # 写入表头信息
    col_start_num = openpyxl.utils.column_index_from_string(headers_match[0][0])
    for col_index, header_name, data in headers_match:
        col_num = openpyxl.utils.column_index_from_string(col_index)
        sheet.cell(row=header_start_row, column=col_num, value=header_name)

    # end_row = min(int(end_row), 15)
    end_row = min(int(end_row), 15)
    for row_num in range(int(start_row), int(end_row) + 1):  # 从第3行到第6行写入示例数据
        for col_num in range(col_start_num, len(headers_match) + 1):
            sheet.cell(row=row_num, column=col_num, value=random.choice(range(1, 1000)))
    # 保存Excel文件
    workbook.save(xlsx_filename)
    return True


def get_code(output):
    data = output
    if "function Macro" not in output:
        data = "function Macro(){\n" + output + "}"
        # f.write(data)
    # data += "\nMacro()"
    return data


import time

common_error_lst = """
请注意，代码中不要出现以下常见错误：
1. 不要使用wps. 这种用法
2. "Error: "Value" Readonly,修改和读取单元格内容，请使用Value2，不要使用Value和Formula，除非明确说明使用公式"
3. "Error: "Text" Readonly"
4. TypeError: range.Cell is not a function
5. TypeError: Cannot read properties of undefined
6. 调用内置函数时，不要出现参数名称，例如range.Replace(What: "1991")这种用法就是错误的，不应当出现What
7. 颜色设置请使用RGB的格式，例如红色：RGB(255, 0, 0)，黄色: RGB(255, 255, 0)
8. 不要使用try catch语句和alert语句
9. PivotTables使用方法为：PivotTables(index), index可选，可以传索引或者透视表名称
10. 不要使用某个数值代表常量，使用具体的常量名称，比如-4108就是xlHAlignCenter，在代码中使用xlHAlignCenter，不要用-4108
"""



if __name__ == "__main__":
    # eval_custom()

    # x = """所有工作表的名称如下：[\"学生成绩表\", \"学生成绩表 (2)\"]，当前工作表名称为：学生成绩表，选中区域为：\"F2:F21\"，活动单元格为：F2。\n工作表包含1个表单区域：\n表单区域1：\n表头起始行号为1，终止行号为1，内容起始行号为2，终止行号为21，同时每一列的列索引、列名及示例内容为：{\"A\",\"学号\",\"2023081101\"},{\"B\",\"姓名\",\"金小妹\"},{\"C\",\"性别\",\"男\"},{\"D\",\"班级\",\"1班\"},{\"E\",\"总分\",\"611\"},{\"F\",\"语文\",\"130\"},{\"G\",\"数学\",\"130\"},{\"H\",\"英语\",\"130\"},{\"I\",\"文综\",\"230\"},{\"J\",\"电话\",\"13888888890\"},{\"K\",\"地址\",\"XX市XX区XX路XX号XX栋210\"}。\n请根据需求“除G列大于130的单元格设置红色填充”编写一个JavaScript宏函数。"""
    q = """你是一个 wps 表格专家，并且精通使用JavaScript语言操作 wps 表格，现有一个工作簿，{x}输出要求如下：

1. 只能返回代码，只能返回代码，只能返回代码；
2. 函数名称为Macro

参考开发文档如下：
{FORMATCONDITION}

请直接输出符合条件的宏函数:
        """


    cs = ChatGptService_v2()

    from openai import OpenAI
    #
    # client = OpenAI(api_key="sk-1beff05651ca42eb8bf868664aa9ae96", base_url="https://api.deepseek.com")
    # client = OpenAI(
    #     api_key="sk-e2iCtazEb7jJMvwBQwH65PVV7QllmxWak2AJmdgnODRSY5M3",  # 知识引擎原子能力 APIKey
    #     base_url="https://api.lkeap.cloud.tencent.com/v1",
    # )

    fw = open("../../../Downloads/deepseek_r1_0207.json", 'w', encoding="utf-8")
    import time
    s = time.time()
    with open("badcase/data0906-0815cot-prompt-clean.json") as f:
        for line in f:
            data = json.loads(line)
            # if data['icode'] not in ["RANGE_FORMAT", "FORMATCONDITION"]:
            if data['icode'] not in ["FORMATCONDITION"]:
                continue
            prompt = q.format(x=data['prompt'], FORMATCONDITION=FORMATCONDITION)
            # prompt = q.format(x="""所有工作表的名称如下：[\"04-8-10月住院数据（删除中草药颗粒药外药耗）\"]，当前工作表名称为：04-8-10月住院数据（删除中草药颗粒药外药耗），选中区域为：\"A1:A1\"，活动单元格为：A1。\n工作表包含1个表单区域：\n表单区域1：\n表头起始行号为1，终止行号为1，内容起始行号为2，终止行号为100，同时每一列的列索引、列名及示例内容为：{\"A\",\"结算时间\",\"2017-12-24 20:59:54\"},{\"B\",\"开单科室编码\",\"同步\"},{\"C\",\"开单科室名称\",\"反相器\"},{\"D\",\"开单科室所属核算单元名称\",\"等相面\"},{\"E\",\"执行科室编码\",\"调相\"},{\"F\",\"执行科室名称\",\"同步带\"},{\"G\",\"执行科室所属核算单元名称\",\"相位抖动\"},{\"H\",\"执行科室所属核算单元矫正\",\"驻波比\"},{\"I\",\"费用类别编码\",\"等相面\"},{\"J\",\"费用类别名称\",\"驻波比\"},{\"K\",\"PF分类\",\"相移\"},{\"L\",\"医护项目拆分标识\",\"衬底\"},{\"M\",\"项目编码\",\"衬底\"},{\"N\",\"项目名称\",\"检相\"},{\"O\",\"数量\",\"76161\"},{\"P\",\"单价\",\"9618\"},{\"Q\",\"总金额\",\"291\"},{\"R\",\"开单费率\",\"44923\"},{\"S\",\"开单点数\",\"97360\"},{\"T\",\"开单绩效点数合计\",\"25369\"},{\"U\",\"执行费率\",\"6311\"},{\"V\",\"执行点数\",\"5827\"},{\"W\",\"执行绩效点数总合计\",\"45594\"}。\n请根据需求“对比G、H两列，若有不相同的，请ai实现将此格填充为黄底”编写一个JavaScript宏函数。""")
            try:
                result = None
                while not result:
                    print("start request")
                    try:
                        # result,reasoning_content,  prompt_tokens, completion_tokens = cs.complete(prompt)
                        result,reasoning_content = cs.complete_stream(prompt)
                    except:
                        result = None
                    print(result)
                    if result:
                        break
                    time.sleep(5)

                print(prompt)
                print(result)
                reasoning_content = reasoning_content
                result = result

                code = result[result.find('```') + 3:result.rfind('```')].replace("javascript", "").strip()
            except:
                code = ""
            code = get_code(code)
            data['answer'] = code
            data['reasoning_content'] = reasoning_content
            data['src_output'] = result
            fw.write(json.dumps(data, ensure_ascii=False) + "\n")
    fw.close()
    print(time.time() - s)



