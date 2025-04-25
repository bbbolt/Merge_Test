# -*- coding: utf-8 -*-
# @Time : 2024/4/22 下午2:25
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : functions.py
FUNCTIONS_MAP = {
    "IsCellAddress": """
    IsCellAddress(str)
    """
}

FUNCTIONS = {
    "IsCellAddress":"""
function IsCellAddress(str)
{
    try{
        Range(str)
        return true
    }
    catch(e){return false}
}
"""
}