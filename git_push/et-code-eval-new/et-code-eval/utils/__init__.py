import functools
import hashlib
import os
import re
import json
import shutil
import subprocess
import zipfile
from datetime import datetime
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import openpyxl
import requests
import urllib3
import yaml
from tqdm import tqdm

from utils.xlsx2json import xlsx2json
import time


class WebDriverFactory:
    __headers = {'Accept': 'application/json', 'Content-Type': 'application/json;charset=UTF-8',
                      'User-Agent': 'selenium/4.1.0 (python windows)', 'Connection': 'keep-alive'}

    def __init__(self, executablePath, product):
        self.wpsdriver_minishell_process = subprocess.Popen(executablePath + "/shell_initiator.exe wpsdriver_minishell_" + product)
        count = 100
        while count > 0:
            time.sleep(0.2) #等待200ms
            self.__local_port = self.getProcessPort(str(self.wpsdriver_minishell_process.pid))
            if self.__local_port:
                self.__root_url = f"http://127.0.0.1:{self.__local_port}"
                break
            count = count - 1

    def __del__(self):
        self.wpsdriver_minishell_process.terminate()

    def getProcessPort(self, strPid):
        netstat_output = subprocess.check_output(["netstat", "-ano"]).decode('gbk')
        for line in netstat_output.splitlines():
            if line.endswith(strPid):
                parts = line.split()
                protocol = parts[0]
                if protocol.lower() == "tcp":
                    local_address = parts[1]
                    return local_address.split(":")[-1]
        return None

    @property
    def root_url(self):
        return self.__root_url

    @property
    def session_id(self):
        self.__session_id = self.remote()
        return self.__session_id

    @property
    def headers(self):
        return WebDriverFactory.__headers

    def remote(self):
        if self.__root_url is None:
            return None

        url = self.__root_url + '/session'
        response = requests.post(url=url, timeout=10, headers=self.__headers)
        data = json.loads(response.text)
        if data is None:
            raise OSError('连接wps driver异常，url:[{}]'.format(self.__root_url))

        return data.get('value').get("sessionId")

class Product:
    WPS = "wps"
    ET = "et"
    WPP = "wpp"


class WpsdriverClient:

    def __init__(self, executablePath, product=Product.WPS):
        self.__driver_factory = WebDriverFactory(executablePath, product)
        self.__root_url = self.__driver_factory.root_url
        self.__headers = {"Content-Type": "application/json"}

    def __del__(self):
        self.__driver_factory.wpsdriver_minishell_process.terminate()
        del self.__driver_factory

    def request(self, method, body={}):
        url = f'{self.__root_url}/session/{self.__driver_factory.session_id}/' + method
        try:
            response = requests.post(url=url, data=json.dumps(body), timeout=10, headers={"Content-Type": "application/json"})
        except (requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError, ConnectionResetError) as e:
            response = requests.post(url=url, data=json.dumps(body), timeout=10, headers=self.__headers)

        return json.loads(response.text)


def lists_to_custom_nested_dict(lists):
    result = {}
    for lst in lists:
        current_level = result
        for key in lst[:-2]:
            key = key.strip()
            if key not in current_level:
                current_level[key] = {}
            elif not isinstance(current_level[key], dict):
                # If current_level[key] is not a dictionary, convert it to one
                current_level[key] = {}
            current_level = current_level[key]

        second_last, last = lst[-2], lst[-1]

        # Ensure that second_last is a dictionary before assigning a new key-value pair
        if not isinstance(current_level.get(second_last), dict):
            current_level[second_last] = {}

        current_level[second_last] = last

    return result

def nested_dict_from_string(input_str):
    input_list = [i.replace("*", "").strip() for i in input_str.split(",   ") if i]
    res = []

    for item in input_list:
        try:
            parts = item.split(": ")[0].split(".")+[item.split(": ")[1]]
        except:
            print(item)
        parts = [i.strip() for i in parts]
        res.append(parts)

    diff_dict = lists_to_custom_nested_dict(res)

    if diff_dict:
        out_str = json.dumps(diff_dict, ensure_ascii=False)
    else:
        out_str = ""
    # formatted_json = out_str[:out_str.rfind(',')]
    return out_str

def generate_md5(text):
    # 创建一个MD5哈希对象
    md5_hash = hashlib.md5()

    # 更新哈希对象以包含要哈希的文本
    md5_hash.update(text.encode('utf-8'))

    # 获取十六进制表示的哈希值
    md5_hex = md5_hash.hexdigest()

    return md5_hex


def timer_decorator(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 记录开始时间
        value = func(*args, **kwargs)  # 执行被装饰的函数
        end_time = time.perf_counter()  # 记录结束时间
        run_time = end_time - start_time  # 计算执行时间

        # 如果函数有返回值，返回一个包含返回值和执行时间的元组
        if value is not None:
            return value, run_time
        else:
            # 如果函数没有返回值，只返回执行时间
            return run_time
    return wrapper_timer



def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


class ChunkIO:
    def __init__(self, f, size, callback=None):
        self.f = f
        self.size = size
        self.callback = callback

    def __iter__(self):
        count = 0
        for data in iter(lambda: self.f.read(8192), b''):
            count += len(data)
            yield data
            if self.callback:
                self.callback("\r  %.2fM <-- %.2fM 进度：%d%%" % (count/1048576, self.size/1048576, count / self.size * 100), end=" ")

    def read(self, size=-1):
        return self.f.read(size)


# 定义一个回调函数，用于更新进度条
def create_callback(pbar):
    def monitor_callback(monitor):
        # 更新已上传的字节数
        pbar.update(monitor.bytes_read - pbar.n)
    return monitor_callback


def upload_file_with_progress(url, file_path):
    # 打开文件并获取文件大小
    with open(file_path, 'rb') as file:
        total_size = os.path.getsize(file_path)

        # 创建进度条
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc="上传进度")

        # 自定义文件分块生成器
        def generate_chunks(chunk_size=1024):
            while chunk := file.read(chunk_size):
                progress_bar.update(len(chunk))  # 更新进度条
                yield chunk

        try:
            # 使用 requests 的 post 方法上传文件，并监控进度
            response = requests.post(
                f'{url}/upload',
                data=generate_chunks(),
                headers={'Content-Type': 'application/octet-stream'}
            )

        finally:
            # 确保进度条关闭
            progress_bar.close()

        # 检查上传结果
        if response.status_code == 200:
            print('文件上传成功')
        else:
            print(f'文件上传失败，状态码: {response.status_code}')

@timer_decorator
def gen_sheets(file_path, sheets_output_path, BASE_URL, data_mapping_dict):
    # 上传文件
    # with open(file_path, 'rb') as file:
    #     files = {'file': file}
    #     response = requests.post(f'{BASE_URL}/upload', files=files)
    #     if response.status_code == 200:
    #         print('File uploaded successfully')
    #     else:
    #         print(f'Failed to upload file: {response.text}')
    #         exit(1)
    upload_file_with_progress(BASE_URL,file_path)


    # 生成样张
    file_name = os.path.basename(file_path)  # 上传文件的名称
    response = requests.post(f'{BASE_URL}/gen_sheets/{file_name}', json={"data_mapping_dict":eval(data_mapping_dict)})
    if response.status_code == 200:
        print('生成样张成功')
    else:
        print(f'Failed to generate sheets: {response.text}')
        exit(1)

    # 下载生成的文件
    filename = os.path.basename(file_path).replace(".json", ".zip")  # 生成文件的名称
    save_zip_file_path = rf"gen_sheets\{filename}"
    response = requests.get(f'{BASE_URL}/download/{filename}')
    if response.status_code == 200:
        with open(save_zip_file_path, 'wb') as file:
            file.write(response.content)
        print(f'File {filename} downloaded successfully')
    else:
        print(f'Failed to download file: {response.text}')
        exit(1)

    # 解压缩文件
    try:
        unzip_file(save_zip_file_path, sheets_output_path)
        print(f'File {save_zip_file_path} unzip successfully to {sheets_output_path}')
    except:
        print(f'Failed to download file: {save_zip_file_path}')

@timer_decorator
def gen_conclusion(xlsx_file_path, BASE_URL):
    # 上传文件
    upload_file_with_progress(BASE_URL,xlsx_file_path)
    # 生成样张
    file_name = os.path.basename(xlsx_file_path)  # 上传文件的名称
    response = requests.post(f'{BASE_URL}/to_judge/{file_name}')
    if response.status_code == 200:
        print('评判数据成功')
    else:
        print(f'Failed to judge sheets: {response.text}')
        exit(1)

    # 下载生成的文件
    update_xlsx_file_path = os.path.basename(xlsx_file_path).replace(".xlsx", "_conclusion.xlsx")  # 生成文件的名称
    local_save_path = xlsx_file_path.replace(".xlsx", "_conclusion.xlsx")
    response = requests.get(f'{BASE_URL}/download_judge/{update_xlsx_file_path}')
    if response.status_code == 200:
        with open(local_save_path, 'wb') as file:
            file.write(response.content)
        print(f'File {local_save_path} downloaded successfully')
    else:
        print(f'Failed to download file: {response.text}')
        exit(1)

@timer_decorator
def get_infer_result(model_path, local_eval_data_path, eval_result_save_path, BASE_URL, data_mapping_dict):
    # 上传文件
    with open(local_eval_data_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(f'{BASE_URL}/upload_eval_data', files=files)
        if response.status_code == 200:
            print('File upload Eval Data successfully')
        else:
            print(f'Failed to upload Eval Data file: {response.text}')
            exit(1)

    # 调用vllm推理数据
    file_name = os.path.basename(local_eval_data_path)  # 上传文件的名称
    response = requests.post(f'{BASE_URL}/to_eval', json={"filename":file_name, "model_path":model_path, "data_mapping_dict":eval(data_mapping_dict)})
    if response.status_code == 200:
        print('推理数据成功')
    else:
        print(f'Failed to infer the eval data: {response.text}')
        exit(1)

    # 下载vllm推理结果
    response = requests.get(f'{BASE_URL}/download_eval_result/{file_name}')
    if response.status_code == 200:
        with open(eval_result_save_path, 'wb') as file:
            file.write(response.content)
        print(f'File {eval_result_save_path} downloaded successfully')
    else:
        print(f'Failed to download file: {response.text}')
        exit(1)


def conclusion2json(conclusion_xlsx_path, gen_train_json, gen_eval_json, args):
    data_mapping_dict = eval(args.data_mapping_dict)
    if args.mode=="r1":
        r1_code_dict = {}
        with open(args.input_data_path, 'r', encoding='utf-8') as file:
            for line in file:
                json_dict = json.loads(line)
                prompt_input, reason_process = json_dict[data_mapping_dict["input"]], json_dict[data_mapping_dict["target"]]
                think_process, reason_process = reason_process.split("</think>")

                if "function Macro()" not in reason_process:
                    reason_process = f"""function Macro() {{
                        {reason_process}
                    }}"""

                if "```javascript" in reason_process:
                    reason_process = re.findall(r"```javascript(.*?)```", reason_process, re.DOTALL)[-1]
                elif "function Macro" in reason_process:
                    reason_process = reason_process[reason_process.rfind("function Macro"):reason_process.rfind("}") + 1]
                if reason_process=="":
                    print("数据有误：", json_dict[data_mapping_dict["target"]])
                prompt_input = prompt_input.replace("\r\n", "\n").replace("\r", "\n")
                r1_code_dict[prompt_input] = think_process+"</think>"+reason_process

    # 打开Excel文件
    workbook = openpyxl.load_workbook(conclusion_xlsx_path, read_only=True)
    sheet = workbook.active

    # 获取列名所在的行
    header = [cell.value for cell in sheet[1]]

    # 找到列名对应的列索引
    prompt_index = header.index('表格描述')
    instruction_index = header.index('代码')
    id_index = header.index('表格名(md5)')

    run_r = header.index("运行是否成功")
    change_r = header.index("执行前后是否有变化")
    pass_r = header.index("模型初步裁决")

    # 初始化一个空列表来存储字典
    data_list = []
    eval_data_list = []

    # 遍历每一行（从第二行开始，因为第一行是列名）
    for row in sheet.iter_rows(min_row=2, values_only=True):

        if not (row[run_r] and row[change_r] and row[pass_r]):
            continue

        prompt = row[prompt_index].replace("\r\n", "\n").replace("\r", "\n")
        instruction = row[instruction_index]
        id = row[id_index]

        if not instruction: continue
        if not instruction.strip(): continue
        # 创建字典并添加到列表中
        # 获取当前日期并格式化为 "年-月-日"
        current_date = datetime.now().strftime("%Y-%m-%d")
        if "//$$$" in instruction: instruction = instruction.split("//$$$")[0] + "//$$$"

        data_dict = {
            "input": prompt,
            "target": instruction if args.mode!="r1" else r1_code_dict[prompt],
            'path': "R1_GEN",
            "md5": id,
            "time": current_date
        }

        eval_data_dict = {
            "question": re.findall(r"需求“(.*?)”编写", prompt, re.DOTALL)[0],
            "input": prompt,
            "prompt": prompt,
            "md5": id,
            "icode": "ADD_EVAL"
        }

        data_list.append(data_dict)
        eval_data_list.append(eval_data_dict)

    # 如果需要将JSON数据保存到文件中
    with open(gen_train_json,'w', encoding='utf-8') as json_file:
        for line in data_list:
            json_file.write(json.dumps(line, ensure_ascii=False) + "\n")
    # 如果需要将JSON数据保存到文件中
    with open(gen_eval_json,'w', encoding='utf-8') as json_file:
        for line in eval_data_list:
            json_file.write(json.dumps(line, ensure_ascii=False) + "\n")

def upload_train_data(file_path, BASE_URL):
    # 上传文件
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(f'{BASE_URL}/upload_train_data', files=files)
        if response.status_code == 200:
            print('File uploaded successfully')
        else:
            print(f'Failed to upload file: {response.text}')
            exit(1)

def copy_file(src, dst):
    try:
        shutil.copy(src, dst)
        print(f"File copied from {src} to {dst}")
    except Exception as e:
        print(f"Error copying file: {e}")

def gen_config_file(data, sheets_path, json_data_path, client_path):
    data["base_path"] = os.path.dirname(sheets_path)
    data["client_path"] = client_path
    data["dataset"]["cases_root_path"] = os.path.basename(sheets_path)
    copy_file(json_data_path, os.path.join(os.path.dirname(sheets_path), os.path.basename(json_data_path)))
    data["val"]["json_file_path"] = os.path.basename(json_data_path)

    # 将修改后的数据写回 YAML 文件
    new_config_file = os.path.join(os.path.dirname(sheets_path), "run_case_config.yaml")
    with open(new_config_file, 'w') as file:
        yaml.safe_dump(data, file)
    return new_config_file

def check_md5(data_path, data_mapping_dict):
    file_json_dict = []
    with open(data_path, mode="r", encoding="utf-8") as f:
        for line in f: file_json_dict.append(json.loads(line))
    for json_dict in file_json_dict:
        if "md5" in json_dict.keys():
            continue
        else:
            json_dict[data_mapping_dict["md5"]] = generate_md5(json_dict[data_mapping_dict["input"]])


    # 如果需要将JSON数据保存到文件中
    with open(data_path, 'w', encoding='utf-8') as json_file:
        for line in file_json_dict:
            json_file.write(json.dumps(line, ensure_ascii=False) + "\n")

def check_xlsx(args):
    ## 判断数据来源类型 xlsx to json
    if args.input_data_path:
        xlsx_map_dict = eval(args.xlsx_map_dict)
        file_basename = os.path.basename(args.input_data_path).split(".xlsx")[0]
        xlsx2json_path = os.path.join(r"gen_sheets", file_basename, file_basename+".json")
        xlsx2json(args.input_data_path, xlsx2json_path, xlsx_map_dict["input"], xlsx_map_dict["target"])
        return xlsx2json_path
    else: pass

def load_yaml(config_path):
    ## 数据保存路径和配置文件模板，默认固定值一般不需要更改
    with open(config_path, 'rb') as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(e)
    return data
