'''
Author: lwhe helongwang@wps.cn
Date: 2024-11-15 16:07:22
LastEditors: lwhe helongwang@wps.cn
LastEditTime: 2024-12-16 17:07:31
FilePath: \\wps-copilot\\copilot-instruction-server\\core\\util\\multi_sheet\\functions.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# -*- coding: utf-8 -*-
# @Time : 2024/6/18 上午10:12
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : functions.py.py
import re


def GetMultiSheetHeadRange(tables, code):
    code_template = '''function GetMultiSheetHeadRange(){{
    return ActiveSheet.Range("{headrange}")
}}'''
    headrange = ''
    for single_sheet in tables:
        headrange += single_sheet[4][0][0] + str(single_sheet[0]) + ':' + single_sheet[4][-1][0] + str(single_sheet[1]) + ','
    return code_template.format(headrange=headrange.rstrip(','))

def GetMultiSheetUsedRange(tables, code):
    code_template = '''function GetMultiSheetUsedRange(){{
    return ActiveSheet.Range("{usedrange}")
}}'''
    usedrange = tables[0][4][0][0] + str(tables[0][0]) + ':' + tables[-1][4][-1][0] + str(tables[-1][0])

    return code_template.format(usedrange=usedrange)

def GetMultiSheetColDataRange(tables, code):
    code_template = '''function GetMultiSheetColDataRange(ColName, Header=xlNo){{
    let header = Header
    let colName = ColName
    let finalrange
    if (header === xlYes){{
        {xlYesCode}
    }}else {{
        {xlNoCode}
    }}
    return finalrange
}}'''
    xlYesCode = ''
    xlNoCode = ''
    xlYesDict = {}
    xlNoDict = {}
    for single_sheet in tables:
        for cols in single_sheet[4]:
            xlYesDict.setdefault(cols[1], [])
            xlYesDict[cols[1]].append(cols[0] + str(single_sheet[0]) + ':' + cols[0] + str(single_sheet[3]))
            xlNoDict.setdefault(cols[1], [])
            xlNoDict[cols[1]].append(cols[0] + str(single_sheet[2]) + ':' + cols[0] + str(single_sheet[3]))

    index = 0
    for col_name in list(xlYesDict.keys()):
        if '"' + col_name + '"' in code or "'" + col_name + "'" in code:
            if index == 0:
                xlYesCode += '''if (colName === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col_name, value=','.join(xlYesDict[col_name]).rstrip(','))
            else:
                xlYesCode += '''else if (colName === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col_name, value=','.join(xlYesDict[col_name]).rstrip(','))
            
            if index == 0:
                xlNoCode += '''if (colName === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col_name, value=','.join(xlNoDict[col_name]).rstrip(','))
            else:
                xlNoCode += '''else if (colName === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col_name, value=','.join(xlNoDict[col_name]).rstrip(','))
            
            index += 1
                    
    return code_template.format(xlYesCode=xlYesCode, xlNoCode=xlNoCode)

def GetMultiSheetDataRange(tables, code):
    code_template = '''function GetMultiSheetDataRange(Header=xlNo){{
    let header = Header
    let finalrange
    if (header === xlYes){{
        finalrange = ActiveSheet.Range("{xlYesrange}")
    }}else {{
        finalrange = ActiveSheet.Range("{xlNorange}")
    }}
    return finalrange
}}'''
    xlYesrange = ''
    xlNorange = ''
    for single_sheet in tables:
        xlYesrange += single_sheet[4][0][0] + str(single_sheet[0]) + ':' + single_sheet[4][-1][0] + str(single_sheet[3]) + ','
        xlNorange += single_sheet[4][0][0] + str(single_sheet[2]) + ':' + single_sheet[4][-1][0] + str(single_sheet[3]) + ','
    xlYesrange = xlYesrange.rstrip(',')
    xlNorange = xlNorange.rstrip(',')
    return code_template.format(xlYesrange=xlYesrange, xlNorange=xlNorange)

def GetMultiSheetColAllDataRange(tables, code):
    code_template = '''function GetMultiSheetColAllDataRange(Col, Header=xlNo){{
    let header = Header
    let col = Col
    let finalrange
    if (header === xlYes){{
        {xlYesCode}
    }}else {{
        {xlNoCode}
    }}
    return finalrange
}}'''
    xlYesCode = ''
    xlNoCode = ''
    xlYesDict = {}
    xlNoDict = {}
    for single_sheet in tables:
        for cols in single_sheet[4]:
            xlYesDict.setdefault(cols[0], [])
            xlYesDict[cols[0]].append(cols[0] + str(single_sheet[0]) + ':' + cols[0] + str(single_sheet[3]))
            xlNoDict.setdefault(cols[0], [])
            xlNoDict[cols[0]].append(cols[0] + str(single_sheet[2]) + ':' + cols[0] + str(single_sheet[3]))
            
    index = 0
    for col in list(xlYesDict.keys()):
        if '"' + col + '"' in code or "'" + col + "'" in code:
            if index == 0:
                xlYesCode += '''if (col === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col, value=','.join(xlYesDict[col]).rstrip(','))
            else:
                xlYesCode += '''else if (col === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col, value=','.join(xlYesDict[col]).rstrip(','))
            
            if index == 0:
                xlNoCode += '''if (col === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col, value=','.join(xlNoDict[col]).rstrip(','))
            else:
                xlNoCode += '''else if (col === "{key}"){{
        finalrange = ActiveSheet.Range("{value}")
    }}'''.format(key=col, value=','.join(xlNoDict[col]).rstrip(','))
            index += 1
        
    return code_template.format(xlYesCode=xlYesCode, xlNoCode=xlNoCode)

def SplitMultiRangeIntoList(ori_table, code):
    return '''
function SplitMultiRangeIntoList(range)
{
    let addressStrList  = []
    let rangeList  = []
    addressStr = range.Address().split(",")
    addressStrList = [...addressStr]
    for (let i = 0; i < addressStrList.length; i++) {
        rangeList.push(Range(`${addressStrList[i]}`));
    }
    return rangeList
}'''

def get_tables(ori_table):
    pattern = r"""表单区域\d+：\n表头起始行号为(\d+)，终止行号为(\d+)，内容起始行号为(\d+)，终止行号为(\d+)，同时每一列的列索引、列名及示例内容为：(.*?)。?\n(?=请根据需求|表单区域)"""
    sanyuanzu_pattern = r'\{"([^"]+)",\s?"(.*?)",\s?"?(.*?)"\}'

    # 使用 re.findall 获取所有匹配的表单区域信息
    matches = re.findall(pattern, ori_table, flags=re.DOTALL)
    # print(matches)
    result_table = []

    for single_sheet in matches:
        sanyuanzu = re.findall(sanyuanzu_pattern, single_sheet[4], flags=re.DOTALL)
        new_single_sheet = [int(single_sheet[0]),int(single_sheet[1]),int(single_sheet[2]),int(single_sheet[3]),sanyuanzu]
        result_table.append(new_single_sheet)
    return result_table

MULTI_SHEET_FUNCTIONS = {
    "GetMultiSheetHeadRange": GetMultiSheetHeadRange,
    "GetMultiSheetUsedRange": GetMultiSheetUsedRange,
    "GetMultiSheetColDataRange": GetMultiSheetColDataRange,
    "GetMultiSheetDataRange": GetMultiSheetDataRange,
    "GetMultiSheetColAllDataRange": GetMultiSheetColAllDataRange,
    'SplitMultiRangeIntoList': SplitMultiRangeIntoList,
    "get_tables": get_tables
}

MULTI_SHEET_MAP = {
    "GetMultiSheetHeadRange": ["GetMultiSheetHeadRange"],
    "GetMultiSheetUsedRange": ["GetMultiSheetUsedRange"],
    "GetMultiSheetColDataRange": ["GetMultiSheetColDataRange"],
    "GetMultiSheetDataRange": ["GetMultiSheetDataRange"],
    "GetMultiSheetColAllDataRange": ["GetMultiSheetColAllDataRange"],
    'SplitMultiRangeIntoList': ["SplitMultiRangeIntoList"],
    "get_tables": ["get_tables"]
}