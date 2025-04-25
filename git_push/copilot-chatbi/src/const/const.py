# -*- coding: utf-8 -*-
# @Time : 2023/10/31 下午2:16
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : const.py

# 错误码
ERROR_CODE_PARAM = 1  # 字段缺失
ERROR_CODE_FUNCTION_TYPE = 2  # 请求参数错误
ERROR_CODE_QUESTION = 3  # 请求参数错误
ERROR_CODE_LACK_FIELD = 4  # 请求字段缺失
ERROR_CODE_TABLE = 5  # 表格结构数据处理异常
ERROR_CODE_RA = 6  # 表格结构数据处理异常
ERROR_CODE_LLM = 7  # 调用大语言模型超时或报错
ERROR_CODE_LLM_RESULT = 8  # 大语言模型推理结果错误
ERROR_CODE_RATE_LIMIT = 9  # 限流

# 功能函数列表
FUNCTION_TYPE_LST = ["PIVOTTABLE","FORMATCONDITION","SHEET_OPS","VALIDATION","SORT","AUTOFILTER","RANGE_OPS","HYPERLINK","DATASERIES","RANGE_FORMAT","DISAGGREGATION","VIEW","MERGE_OPS"]

# 原始starcoder的常规prompt
FULL_PROMPT = """以下是描述任务的说明。编写适当地完成请求的响应。

### 指令：
假如你是一个Excel专家，并且精通使用JavaScript语言操作Excel，现有一个excel工作簿，所有工作表的名称如下：{ALL_SHEET_NAME}，当前工作表名称为：{CUR_SHEET_NAME}，选中区域为：\"{selected_start_col}{selected_start_row}:{selected_end_col}{selected_end_row}\"，活动单元格为：{active_cell}。
工作表包含{num}个表单区域：
{table_area}
请根据需求“{demand}”编写一个JavaScript宏函数。

### 回复："""

# QWEN的prompt
QWEN_PROMPT = """所有工作表的名称如下：{ALL_SHEET_NAME}，当前工作表名称为：{CUR_SHEET_NAME}，选中区域为：\"{selected_start_col}{selected_start_row}:{selected_end_col}{selected_end_row}\"，活动单元格为：{active_cell}。\n工作表包含{num}个表单区域：
{table_area}
请根据需求“{demand}”编写一个JavaScript宏函数。"""

NO_SELECTION_QWEN_PROMPT = """所有工作表的名称如下：{ALL_SHEET_NAME}，当前工作表名称为：{CUR_SHEET_NAME}。
工作表包含{num}个表单区域：
{table_area}
请根据需求“{demand}”编写一个JavaScript宏函数。"""

DEFAULT_QWEN_PROMPT = """所有工作表的名称如下：{ALL_SHEET_NAME}，当前工作表名称为：{CUR_SHEET_NAME}，选中区域为：\"{selected_start_col}{selected_start_row}:{selected_end_col}{selected_end_row}\"，活动单元格为：{active_cell}。
请根据需求“{demand}”编写一个JavaScript宏函数。"""


# starcoder无选中区域的prompt
NO_SELECTION_FULL_PROMPT = """以下是描述任务的说明。编写适当地完成请求的响应。

### 指令：
假如你是一个Excel专家，并且精通使用JavaScript语言操作Excel，现有一个excel工作簿，所有工作表的名称如下：{ALL_SHEET_NAME}，当前工作表名称为：{CUR_SHEET_NAME}，活动单元格为：{active_cell}。
工作表包含{num}个表单区域：
{table_area}
请根据需求“{demand}”编写一个JavaScript宏函数。

### 回复："""

# starcoder空表的prompt
DEFAULT_JS_TABLE_STRUCTURE = """以下是描述任务的说明。编写适当地完成请求的响应。

### 指令：
假如你是一个Excel专家，并且精通使用JavaScript语言操作Excel，现有一个excel工作簿，所有工作表的名称如下：{ALL_SHEET_NAME}，当前工作表名称为：{CUR_SHEET_NAME}，选中区域为：\"{selected_start_col}{selected_start_row}:{selected_end_col}{selected_end_row}\"，活动单元格为：{active_cell}。
请根据需求“{demand}”编写一个JavaScript宏函数。

### 回复："""


# RAG 修复case 用的
PROMPT_DICT = {
    "1": """以下是一个参考示例：
<文档结构>：{table_structure}
<用户需求>：{case_question}
示例代码：
``` javascript
{case_answer}
```
参考示例代码，但不要直接复制，完成下面任务：
所有工作表的名称如下：{ALL_SHEET_NAME}，当前工作表名称为：{CUR_SHEET_NAME}，选中区域为：\"{selected_start_col}{selected_start_row}:{selected_end_col}{selected_end_row}\"，活动单元格为：{active_cell}。
工作表包含{num}个表单区域：
{table_area}
请根据需求“{demand}”编写一个JavaScript宏函数。"""
}

NUM_1 = 1
NUM_2 = 2

