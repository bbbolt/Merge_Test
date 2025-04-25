import threading
import time
from functools import wraps

from const.const import ERROR_CODE_RATE_LIMIT
from const.env import RATE_LIMIT_TOKEN
from metric.prom_factory import glo_metric_thread, RATE_LIMIT_FAILED_COUNTER, RATE_LIMIT_TIME

now = time.monotonic if hasattr(time, 'monotonic') else time.time


# 基于自定义map实现的多级并发map
class RateLimit(object):
    def __init__(self, period=1, clock=now):
        self.period = period
        self.clock = clock
        self.token_dict = dict(item.split(':') for item in RATE_LIMIT_TOKEN.split(','))
        self.defualt_token_key = "default"

        self.main_lock = threading.RLock()
        self.map = {}
        self.locks = {}

    def _acquite_lock(self, key):
        if key not in self.locks:
            with self.main_lock:
                if key not in self.locks:
                    self.locks[key] = threading.RLock()
                self._init_map_key(key)

        return self.locks[key]

    def _init_map_key(self, key):
        if key not in self.map:
            self.map[key] = {
                "last_reset": self.clock(),
                "num_calls": 0,
                "clamped_token": int(self.token_dict.get(key) if key in self.token_dict else self.token_dict['default'])
            }

    def trylock(self, key):
        lock = self._acquite_lock(key)
        with lock:
            clock = self.clock()
            elapsed = clock - self.map[key]["last_reset"]

            if (self.period - elapsed) <= 0:
                self.map[key]["num_calls"] = 0
                self.map[key]["last_reset"] = clock

            if self.map[key]["num_calls"] > self.map[key]["clamped_token"]:
                return False
            return True


RateLimitManager = RateLimit()


def rate_limit(name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start = time.time()
            headers = self.request.headers
            product_name = headers.get("AI-Gateway-Product-Name", "unknown") if headers else "unknown"
            if not RateLimitManager.trylock(name + "_" + product_name):
                glo_metric_thread.metric_count(RATE_LIMIT_FAILED_COUNTER,
                                               labels=[glo_metric_thread.local_ip, name, product_name])
                self.set_status(429)
                return self.write({
                    'code': ERROR_CODE_RATE_LIMIT,
                    'msg': "限流异常"
                })
            response = func(self, *args, **kwargs)
            glo_metric_thread.metric_histogram(RATE_LIMIT_TIME, labels=[glo_metric_thread.local_ip, name, product_name],
                                               value=(time.time() - start))
            return response

        return wrapper

    return decorator
