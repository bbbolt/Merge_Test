import re
import time



from utils.util.disaggregation.functions import FUNCTIONS as FUNCTIONS_DISAGGREGATION
from utils.util.pvt.functions import FUNCTIONS as FUNCTIONS_PVT
from utils.util.pvt.functions import CONTEXT_CODE as CONTEXT_CODE_PVT
from utils.util.sort.functions import FUNCTIONS as FUNCTIONS_SORT
from utils.util.hyperlink.functions import FUNCTIONS as FUNCTIONS_HYPERLINK
from utils.util.range_ops.functions import FUNCTIONS as FUNCTIONS_RANGE_OPS
from utils.util.range_ops.functions import CONTEXT_CODE as CONTEXT_CODE_RANGE_OPS
from utils.util.merge.functions import FUNCTIONS as FUNCTIONS_MERGE

def get_date_str():
    """获取日期字符串

    以当前时间、本地时区生成形如"2020-08-16"的日期字符串

    Returns:
        str: 日期字符串
    """
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def get_time_str():
    """获取时间字符串

    以当前时间、本地时区生成形如"20200816190324"的时间字符串

    Returns:
        str: 时间字符串
    """
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

ALPHABET = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')


def digit2alphabet(digit):
    """10进制 -> 26进制"""
    mod, remainder = divmod(digit, 26)
    alphabet = ALPHABET[remainder]
    while mod:
        mod, remainder = divmod(mod, 26)
        alphabet = ALPHABET[remainder - 1] + alphabet
    return alphabet

def alphabet2digit(alphabet):
    """26进制 -> 十进制"""
    result = 0
    for char in alphabet:
        result = result * 26 + (ord(char.upper()) - ord('A') + 1)
    return result

def norm_question(question, tables):
    question = modify_question(question, tables)
    new_question = question.replace(",", "，")
    return new_question

def modify_question(question, tables):
    """
    headers若有 平均成本这样的字样，在query中找到相同字样，并在后面加上 列 字
    """
    headers = []
    for item in tables:
        headers.extend(item.get("headers", []))
    if not headers:
        return question
    for item in set(headers):
        # 平均成本
        if '平均' not in item:
            continue
        offset = 0
        for matched_item in re.finditer(item, question):
            end = matched_item.end() + offset
            if end < len(question) and question[end] != '列':
                question = question[:end] + '列' + question[end:]
                offset += 1
    return question

def extra_dataseries(result):
    extra_function = ""
    if "function IsCellAddress" not in result and "IsCellAddress" in result:
        tmp = """
function IsCellAddress(str)
{
try{
    Range(str)
    return true
}
catch(e){return false}
}"""
        result += tmp
        extra_function = tmp
    return result, extra_function

def add_functions(code):
    extra_function_tool = ""
    if "DISAGGREGATION_" in code:
        try:
            pattern = r'以下为工具函数，使用的工具函数列表为\[(.*?)\]'
            functions_used = re.findall(pattern, code)[0]
            pattern = r'"(.*?)"'
            functions_used = re.findall(pattern, functions_used)
            functions = {}
            for function in functions_used:
                if function in FUNCTIONS_DISAGGREGATION:
                    functions[function] = FUNCTIONS_DISAGGREGATION[function]
        except:
            # print(code)
            functions = FUNCTIONS_DISAGGREGATION
        context = ''
    elif "PVT_" in code:
        try:
            pattern = r'以下为工具函数，使用的工具函数列表为\[(.*?)\]'
            functions_used = re.findall(pattern, code)[0]
            pattern = r'"(.*?)"'
            functions_used = re.findall(pattern, functions_used)
            functions = {}
            for function in functions_used:
                if function in FUNCTIONS_PVT:
                    functions[function] = FUNCTIONS_PVT[function]
        except:
            # print(code)
            functions = None
        context = CONTEXT_CODE_PVT
    elif "SORT_" in code:
        try:
            pattern = r'以下为工具函数，使用的工具函数列表为\[(.*?)\]'
            functions_used = re.findall(pattern, code)[0]
            pattern = r'"(.*?)"'
            functions_used = re.findall(pattern, functions_used)
            functions = {}
            for function in functions_used:
                if function in FUNCTIONS_SORT:
                    functions[function] = FUNCTIONS_SORT[function]
        except:
            # print(code)
            functions = FUNCTIONS_SORT
        context = ''
    elif "HYBERLINK_" in code:
        try:
            pattern = r'以下为工具函数，使用的工具函数列表为\[(.*?)\]'
            functions_used = re.findall(pattern, code)[0]
            pattern = r'"(.*?)"'
            functions_used = re.findall(pattern, functions_used)
            functions = {}
            for function in functions_used:
                if function in FUNCTIONS_HYPERLINK:
                    functions[function] = FUNCTIONS_HYPERLINK[function]
        except:
            # print(code)
            functions = FUNCTIONS_HYPERLINK
        context = ''
    elif "CLOP_" in code or "FindReplaceColor" in code:
        context = CONTEXT_CODE_RANGE_OPS
        try:
            pattern = r'以下为工具函数，使用的工具函数列表为\[(.*?)\]'
            functions_used = re.findall(pattern, code)[0]
            pattern = r'"(.*?)"'
            functions_used = re.findall(pattern, functions_used)
            functions = {}
            for function in functions_used:
                if function in FUNCTIONS_RANGE_OPS:
                    functions[function] = FUNCTIONS_RANGE_OPS[function]
                # if "GetUnionTableRange" not in functions:
                #     functions["GetUnionTableRange"] = FUNCTIONS_RANGE_OPS["GetUnionTableRange"]
        except:
            # print(code)
            functions = None
    elif "Merge" in code:
        context = ''
        try:
            pattern = r'以下为工具函数，使用的工具函数列表为\[(.*?)\]'
            functions_used = re.findall(pattern, code)[0]
            pattern = r'"(.*?)"'
            functions_used = re.findall(pattern, functions_used)
            functions = {}
            for function in functions_used:
                if function in FUNCTIONS_MERGE:
                    functions[function] = FUNCTIONS_MERGE[function]
        except:
            # print(code)
            functions = None
    # elif "IsCellAddress" in code:
    #     functions = FUNCTIONS_DATASERIES
    else:
        functions, context = None, ''
    if functions:
        for key, value in functions.items():
            code += '\n' + value
            extra_function_tool += '\n' + value
        code += context
        extra_function_tool += context
    return code, extra_function_tool
