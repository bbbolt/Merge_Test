# -*- coding: utf-8 -*-
import json
import os

import chardet

from utils.common_util.log_util import logger


class ConfigUtil:

    def __init__(self, config_path):
        self.config_path = config_path

    def get_config_value_by_key(self, key):
        if os.path.exists(self.config_path):
            with open(self.config_path, "rb") as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding']

            with open(self.config_path, encoding=encoding) as f:
                case_conf = json.load(f)
                value = case_conf.get(key)
                if value == '':
                    logger.warning(f"配置{key}为空")
                    return ''
                return value

