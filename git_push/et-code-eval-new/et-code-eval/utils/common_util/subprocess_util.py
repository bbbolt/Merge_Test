import subprocess
import chardet

def run_subprocess(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)
    if process.stdout is None:
        return [],"创建进程异常"

    # 读取标准输出和标准错误输出
    output, error = process.communicate()

    if error:
        # 检测标准错误输出的编码方式
        encoding = chardet.detect(error)['encoding']
        return [], error.decode(encoding)

    encoding = chardet.detect(output)['encoding']
    output = output.decode(encoding)
    # 去掉output末尾的\n或者\r\n
    output = output.rstrip("\r\n")
    # 将output按\n或者\r\n分割
    output_list = output.split("\r\n")
    if output_list[0] != output:
        return output_list, None

    return output.split("\n"), None
