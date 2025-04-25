# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
import traceback
import tornado
from const.env import RAG_THRESHOLD_TOPP, RAG_THRESHOLD_TOPK, ERROR_CODE_DICT, health_check_dir
from log import log_warning
import log
from tornado.concurrent import run_on_executor
from abs import ThreadCorsHandler
from abc import ABC

import json

# 定义 QueryHandler
class QueryHandler(ThreadCorsHandler, ABC):

    def resp(self, session_id, request_id, code, msg="", query="", results=[]):
        return {"session_id":session_id, "request_id":request_id,"code": code, "msg": msg, "query":query, "data": results}

    def initialize(self, retriever):
        """
        初始化 QueryHandler，传入 Retriever 实例。
        """
        # log.app_logger.info("sadasd")
        self.retriever = retriever
        
    @run_on_executor
    def post(self):
        """
        处理 POST 请求，接收查询并返回检索结果。
        """

        try:
            x_rid = self.request.headers.get("Jm-Reqid", self.request_id)
            # 从请求体中获取 JSON 数据
            request_id = ""
            session_id = ""
            data = json.loads(self.request.body, strict=False)
            query = data.get("query", "")
            session_id = data.get("session_id", "")
            request_id = data.get("request_id", "")

            if not query:
                result_body = self.resp(session_id=session_id,request_id=request_id, code=ERROR_CODE_DICT["LACK_FIELD"][0], msg=ERROR_CODE_DICT["LACK_FIELD"][1])
                log_warning(self.request_id, x_rid, round(self.request.request_time() * 1000), data)
            else:
                # 调用 Retriever 进行处理
                results = self.retriever.run(query, topk=RAG_THRESHOLD_TOPK, topp=RAG_THRESHOLD_TOPP)
                result_body = self.resp(session_id=session_id,request_id=request_id,code=ERROR_CODE_DICT["SUCCESS"][0], msg=ERROR_CODE_DICT["SUCCESS"][1], query=query, results=results)
                log.app_logger.info(result_body)

        except Exception as e:
            result_body = self.resp(session_id=session_id, request_id=request_id,
                                    code=ERROR_CODE_DICT["ERROR_REQUEST"][0],
                                    msg=ERROR_CODE_DICT["ERROR_REQUEST"][1] + str(e))
            log.app_logger.warning(str(request_id) + ": " + traceback.format_exc().replace("\n", ""))
            return self.write(result_body)
        self.write(result_body,request_id=self.request_id, x_rid=x_rid)


class HealthHandler(ThreadCorsHandler, ABC):

    def initialize(self, retriever):
        """
        初始化 QueryHandler，传入 Retriever 实例。
        """
        # log.app_logger.info("sadasd")
        self.retriever = retriever

    def _check_fs(self) -> bool:
        """
        检查当前实例是否可以正常读FS

        :returns:   FS是否可以正常读写
        :rtype:     bool
        """
        try:
            if not os.path.exists(health_check_dir):
                os.mkdir(health_check_dir)

            # 读检查
            os.listdir(health_check_dir)
            # 写检查
            with open(os.path.join(health_check_dir, 'health_check.txt'), 'w') as f:
                f.write('1')
            # if self.settings['redis_tool']:
            #     return True
            # else:
            #     log.app_logger.error("Failed connected to Redis cluster")
            #     return False
        except BrokenPipeError as e:
            log.app_logger.error(f'FS error occurred, will restart instance: {e}')
            return False
        except Exception as e:
            log.app_logger.error(f'unknown error occurred, will restart instance: {e}')
            return False
        return True

    def get(self, *args, **kwargs):
        if self._check_fs():
            self.write('<h1>ok<h1>')
        else:
            self.write_error(500)

    def post(self, *args, **kwargs):
        if self._check_fs():
            self.write('<h1>ok<h1>')
        else:
            self.write_error(500)