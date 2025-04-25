# -*- coding: utf-8 -*-
# @Time : 2022/2/25 下午2:59
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : log.py

"""
重写日志模块，捕获系统中所有日志
"""

import logging
import logging.handlers

app_logger = logging.getLogger("tornado.application")

KE_LOG_LVL = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def init(level, app_log_path, auto_rotate=True, backup_days=2):
    """日志模块初始化函数.
    Args:
        level: str, 打印日志的级别, 可选值DEBUG/INFO/WARNING/ERROR/CRITICAL
        access_log_path: str, 访问日志输出路径
        app_log_path: str, 应用日志输出路径
        auto_rotate: True/False, 是否需要进行日志切割
        backup_days: int, 需要保存多长时间的日志,默认60天日志
    Return:
        None
    """
    # Set log level
    app_logger.setLevel(KE_LOG_LVL[level])

    ke_fmt = logging.Formatter("%(asctime)s %(levelname)s [%(filename)s.%(lineno)s]: %(message)s")
    sh = logging.StreamHandler()  # 往屏幕上输出
    sh.setFormatter(ke_fmt)  # 设置屏幕上显示的格式
    if auto_rotate:
        app_handler = logging.handlers.TimedRotatingFileHandler(app_log_path, when='MIDNIGHT', backupCount=backup_days)
    else:
        app_handler = logging.handlers.WatchedFileHandler(app_log_path)

    app_handler.setFormatter(ke_fmt)

    app_logger.addHandler(app_handler)

    app_logger.addHandler(sh)

def log_warning(req_id, x_rid, time_, req_body=None, input_dict=None):
    if req_body:
        app_logger.warning("request_id:%s, x-rid: %s, timer:%s, input_dict:%s", req_id, x_rid, time_, str(req_body))
    if input_dict:
        app_logger.warning("request_id:%s, x-rid: %s, timer:%s, input_dict:%s", req_id, x_rid, time_, input_dict)



