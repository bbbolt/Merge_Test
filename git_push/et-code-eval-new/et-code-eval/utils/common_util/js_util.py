import json
import os
import subprocess
from typing import Tuple

import chardet

from utils.common_util import file_util


def run_js(js_code: str, run_method: str, *args) -> Tuple[str, bool]:
    file_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(file_dir, "..", '..'))
    node_path = os.path.join(path, "static", "tools", "node.exe")
    js_template_path = os.path.join(path, "static", "js", "js_template.js")
    js = file_util.read_file(js_template_path)
    args = json.dumps(args)
    run_method = "{identifier}.apply(this, {args})".format(identifier=run_method, args=args)
    js = js.replace("{{js_code}}", js_code).replace("{{run_method}}", run_method)
    process = subprocess.Popen(node_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    if process.stdout is None:
        return "创建进程异常", False

    # 读取标准输出和标准错误输出
    output, error = process.communicate(js.encode("utf-8"))
    status = process.wait()
    if status != 0 or error:
        # 检测标准错误输出的编码方式
        encoding = chardet.detect(error)['encoding']
        return "返回{}状态：{}".format(status, error.decode(encoding)), False

    encoding = chardet.detect(output)['encoding']
    output = output.decode(encoding)
    output = output.replace("\r\n", "\n").replace("\r", "\n")
    output_last_line = output.split("\n")[-2]

    ret = json.loads(output_last_line)
    if len(ret) == 1:
        ret = [ret[0], None]
    status, value = ret

    if status == "ok":
        return value, True

    return value, False
