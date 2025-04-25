# -*- coding: utf-8 -*-
# @Author: zhangyipeng1
# @Date:   2023-03-28 19:31:56
# @Last Modified by:   zhangyipeng1
# @Last Modified time: 2023-08-15 17:12:57
"""异步数据上报逻辑实现
业务数据异步存储到KS3的逻辑实现。
"""
import asyncio
import json
import logging
import re
import threading
import traceback

from datetime import datetime
from random import random
from typing import Any
from typing import Dict
import time

try:
    from ks3.connection import Connection
    KS3_AVAILABLE = True
except ImportError:
    KS3_AVAILABLE = False

from const import env

logger = logging.getLogger()


def get_date_str():
    """获取日期字符串

    以当前时间、本地时区生成形如"2020-08-16"的日期字符串

    Returns:
        str: 日期字符串
    """
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))



class AsyncReportThread(threading.Thread):
    """独立的异步数据上报线程，专门用于上报业务数据到KS3
    """

    def __init__(self):
        super().__init__()
        self._loop = None
        self._ks3_conn = None

    @property
    def cls_name(self):
        return self.__class__.__name__

    def run(self):
        """初始化线程资源，如事件循环和KS3连接"""
        logger.info(f"starting {self.cls_name} and run asyncio loop")
        # 创建loop并初始化对象
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        # 创建KS3连接
        if KS3_AVAILABLE:
            try:
                self._ks3_conn = Connection(env.KS3_AK, env.KS3_SK, host=env.KS3_ENDPOINT)
            except Exception as e:
                logger.error(logger.warning(f'ks3 connecting failed: {e}'))
        # 启动
        self._loop.run_forever()

    async def _upload_ks3(self, data_id: str, dumps_data: str, file_suffix: str = ''):
        """上传数据到KS3

        异步上传字符串数据到KS3，存储为文件形式

        Args:
            data_id (str): 数据ID，将作为KS3文件名
            dumps_data (str): 数据内容，dict对象的json序列化结果
            file_suffix (str): KS3文件后缀
        """
        if not KS3_AVAILABLE:
            logger.warning('ks3 library not available')
            return
        if self._ks3_conn is None:
            logger.warning('ks3 connecting failed')
            return
        if not isinstance(dumps_data, str):
            logger.error('dumps_data not str')
            return
        # 获取桶实例
        try:
            bucket = self._ks3_conn.get_bucket(env.KS3_BUCKET)
            assert bucket is not None
        except Exception as e:
            logger.warning(f'get ks3 bucket failed: {e}')
            return
        # 上传数据
        prefix = env.KS3_PREFIX.strip('/')
        date_str = get_date_str()
        key_path = f'{prefix}/{date_str}/{data_id}{file_suffix}'
        # print(key_path)
        # print(dumps_data)
        try:
            key = bucket.new_key(key_path)
            assert key is not None
            key.set_contents_from_string(dumps_data, headers=None)
        except Exception as e:
            logger.warning(f'upload to ks3 failed: {e}')
            return

    def async_upload_ks3(self, data_id: str, dumps_data: str, file_suffix: str = ''):
        """_upload_ks3()异步方法的同步封装

        在协程中调用异步方法_upload_ks3()上传字符串数据到KS3，非阻塞，忽略异常和返回

        Args:
            data_id (str): 数据ID，将作为KS3文件名
            dumps_data (str): 数据内容，dict对象的json序列化结果
            file_suffix (str): KS3文件后缀
        """
        if KS3_AVAILABLE:
            asyncio.run_coroutine_threadsafe(
                self._upload_ks3(data_id, dumps_data, file_suffix),
                self._loop
            )
        else:
            logger.info('ks3 library not available, skipping upload')


# import module时实例化
glo_asyn_report_thread = AsyncReportThread()


def async_report_log(
    ori_input: str,
    prompt: str,
    ori_output: str,
    output: str,
    infer_cost_ms: float,
    t_start: float,
    t_end: float,
    business_key: str = "",
    batch_size: str = "",
    infer_args: Dict[str, Any] = {},
    scene_args: Dict[str, Any] = {}
):
    """异步日志上报

    按配置做随机采样。
    将忽略任何异常，不影响其他代码逻辑。

    Args:
        ori_input (str): 当前文本对应输入（前处理之前），即用户原始输入文本
        prompt (str): 当前文本对应输入（前处理之后），即拼接了场景辅助文本的用户原始输入文本
        ori_output (str): 当前文本对应输出（后处理之前），即模型原始输出文本
        output (str): 当前文本对应输出（后处理之后），即去除不必要杂质的精简的模型输出
        infer_cost_ms (float): 当前文本所在推理的耗时，单位ms
        t_start (float): 推理开始时间的时间戳（前处理之前）
        t_end (float): 推理结束时间的时间戳（后处理之后）
        business_key (str): 业务场景标识，为空时从输入文本前缀中获取 (default: ``)
        batch_size (int): 当前文本所在推理的batch_size (default: `1`)
        infer_args (Dict[str, Any]): 用于传递推理参数，经过校验过滤后透传到模型推理函数 (default: `{}`)
        scene_args (Dict[str, Any]): 场景参数，可选，其中的每个字段将透传给预处理函数 (default: `{}`)
    """
    # 按配置做随机采样后上报日志
    if random() > env.LOG_REPORT_RATIO:
        return
    try:
        if business_key == '':
            business_key = re.search(r"(?<=^<)(.*?)(?=>)", ori_input)
            business_key = 'invalid' if business_key is None else business_key.group(0)
        log_id = f'{business_key}'
        # 在上报数据字段中，只在ori_input字段里保留用户原始输入文本，减少冗余存储，减轻数据脱敏压力
        if re.search(r"^<(.*?)>", ori_input) is not None:
            prompt_parts = prompt.rsplit(re.sub(r"^<(.*?)>", "", ori_input), 1)
            assert len(prompt_parts) == 2
            _prompt = prompt_parts[0]
        else:
            _prompt = prompt[:]
        str_t_start = datetime.fromtimestamp(t_start).strftime("%Y-%m-%d %H:%M:%S")
        str_t_end = datetime.fromtimestamp(t_end).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        traceback.print_exc()
        return
    report_log = {
        "business_key": business_key,           # 业务场景标识
        "model_version": env.MODEL_VERSION,     # 模型版本
        "model_type": env.MODEL_TYPE,           # 模型配置类型
        "model_path": "",                       # 模型文件路径
        "ori_input": ori_input,                 # 用户原始输入文本
        "prompt": _prompt,                      # 不含用户输入的场景辅助文本
        "ori_output": ori_output,               # 模型原始输出
        "output": output,                       # 经过后处理的精简模型输出
        "infer_cost_ms": infer_cost_ms,         # 当前输入文本的推理耗时
        "t_start": str_t_start,                 # 推理开始时间（前处理之前）
        "t_end": str_t_end,                     # 推理结束时间（后处理之后）
        "batch_size": batch_size,               # 当前推理的batch_size
        "infer_args": infer_args,               # 推理参数
        "scene_args": scene_args,               # 业务场景参数
    }
    dumps_data = json.dumps(report_log, ensure_ascii=False)
    glo_asyn_report_thread.async_upload_ks3(
        data_id=log_id,
        dumps_data=dumps_data,
        file_suffix='.json',
    )

