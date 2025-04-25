# -*- coding: utf-8 -*-
# @Time : 2024/8/26 上午11:46
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : stream_utils.py
"""
为流式生成服务做的后处理操作
"""
import json
import traceback

import log
from app_main import data_error
from const.const import ERROR_CODE_LLM


def replace_result(output, question, is_first):
    """
    将输出结果中开头的 /*  替换成/**
    将中间部分的*/  替换成空
    """
    if is_first:
        output = output.replace("/*", "/**")
    if "*/" in question:
        output = replace_star(output)
    return output

def replace_star(output):
    if output


