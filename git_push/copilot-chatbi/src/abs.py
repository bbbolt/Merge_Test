import json
import re
import time
import uuid
from abc import ABC
from concurrent.futures import ThreadPoolExecutor

import tornado.web

import const.env as env
# from const.env import *
# from metric.prom_factory import REQUEST_HISTOGRAM, glo_metric_thread


class AbsHandler(tornado.web.RequestHandler, ABC):

    def prepare(self):
        self.request_id = self.request.headers.get("X-Client-Request-Id", "unknown")
        if self.request_id == "unknown":
            self.request_id = self.request.headers.get("Client-Request-Id", "unknown")
        self.AigcGatewayProductName = self.request.headers.get("Aigc-Gateway-Product-Name", "unknown")
        self.x_client_type = self.request.headers.get("X-Client-Type", "unknown")
        if self.request_id == "unknown":
            self.request_id = self.request.headers.get("Qingqiu-Request-Id", "unknown")
        if self.request_id == "unknown":
            self.request_id = str(uuid.uuid4())
        self.set_header("Qingqiu-Request-Id", self.request_id)
        self.set_header("X-Client-Request-Id", self.request_id)
        self.set_header("X-Client-Type", self.x_client_type)

    def write(self, chunk, request_id="", x_rid="", stream=False):
        timestamp = int(time.time() * 1000)
        self.set_header("Qingqiu-Request-Id", self.request_id)
        self.set_header("X-Request-Id", x_rid)
        self.set_header("Qingqiu-Timestamp", timestamp)
        self.set_header("X-Client-Request-Id", self.request_id)
        self.set_header("X-Client-Type", self.x_client_type)
        if not stream:
            if isinstance(chunk, dict):
                self.set_header(
                    "Content-Type", "application/json; charset=UTF-8")
                chunk = json.dumps(chunk, ensure_ascii=False)
            return super().write(chunk)
        else:
            self.set_header(
                "Content-Type", "text/event-stream; charset=UTF-8")
            if isinstance(chunk, dict):
                chunk = json.dumps(chunk, ensure_ascii=False)
            super().write(chunk)
            super().flush()

    def on_finish(self):
        pass
        # glo_metric_thread.metric_histogram(REQUEST_HISTOGRAM, [glo_metric_thread.local_ip, self.request.path],
        #                                    self.request.request_time())


class ThreadCorsHandler(AbsHandler, ABC):
    reg_allowed_origin = ".*.wps.cn[/]?$"
    executor = ThreadPoolExecutor(max_workers=int(env.MAX_WORKERS))

    def set_default_headers(self):
        origin = self.request.headers.get("Origin") or ""
        if re.match(self.reg_allowed_origin, origin):
            self.add_header("Access-Control-Allow-Origin", origin)
        self.add_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        # 设置模型版本
        self.set_header("model-version", env.MODEL_VERSION)

    def options(self):
        self.set_status(204)
        self.finish()
