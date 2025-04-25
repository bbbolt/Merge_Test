import os
import sys


# 工具路径
def get_path():
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    elif __file__:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(file_dir, "..", '..'))
    else:
        path = ""
    return path

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


