# -- coding: utf-8 --
import logging
import os
import sys


class Logger(object):
    def __init__(self, path, cmd_level=logging.DEBUG, file_level=logging.INFO):
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        # 设置CMD日志
        self.sh = logging.StreamHandler()
        self.sh.setFormatter(fmt)
        self.sh.setLevel(cmd_level)
        
        # 设置文件日志
        self.fh = logging.FileHandler(path, "a", "utf-8")
        self.fh.setFormatter(fmt)
        self.fh.setLevel(file_level)
        self.logger.addHandler(self.sh)
        self.logger.addHandler(self.fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def cri(self, message):
        self.logger.critical(message)

    def set_cmd_level(self, level):
        self.sh.setLevel(level)

    def set_file_level(self, level):
        self.fh.setLevel(level)

if __name__=="__main__":
    # 自动创建logs目录
    log_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'logs')
    os.makedirs(log_path, exist_ok=True)

    file_path = log_path + "/run.log"

    if not os.path.exists(file_path):
        f = open(file_path, "a+")
        f.close()

    logger = Logger(file_path)
