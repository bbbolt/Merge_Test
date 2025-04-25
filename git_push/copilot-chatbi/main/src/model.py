# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
# import deepspeed
import time
import requests
import json

from const.env import URL_DATA_ANALYSIS

# def init_process():

#     deepspeed.init_distributed("nccl")

#     world_size = torch.cuda.device_count()  # 获取 GPU 数量
#     local_rank = torch.cuda.current_device()  # 当前 GPU 设备号

#     print("****** world_size: {}, local_rank: {} ******".format(world_size, local_rank))


# class DeepSeekV3Model:
#     def __init__(self, model_path):
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.tokenizer = AutoTokenizer.from_pretrained(model_path)
#         self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)
#         self.template = """<｜begin▁of▁sentence｜><｜User｜>你是一名专业的数据分析师，擅长从表格数据中提取信息、进行统计分析，并生成可执行的代码或有价值的建议。  
# 现在，我将提供一份表格数据（Markdown 格式），请你根据用户的需求进行分析。  

# ### 表格数据如下（仅截取前10行和前5列）：  
# {markdown_table}  

# ### 用户需求：  
# {user_query}  

# 请根据以上信息，完成以下任务之一（根据需求自动选择最合适的方式）：  
# 1. **数据摘要**：如果用户希望获取数据概览，请提供数据的基本统计信息，如均值、中位数、最大/最小值、数据分布等。  
# 2. **趋势分析**：如果用户想要了解数据的变化趋势，请分析关键数据指标，并提供可视化建议（如折线图、直方图）。  
# 3. **代码生成**：如果用户需要对数据进行操作，请输出相应的 Python 代码（使用 Pandas 进行数据处理）。  
# 4. **决策建议**：如果用户希望得到业务层面的见解，请基于数据提供合理的分析结论，并附上具体建议。  

# 请确保回答清晰、逻辑严谨，并附上必要的代码或计算公式。<｜Assistant｜><think>\n"""
    
#     def generate_response(self, md_table, query):
#         try:
#             input_text = self.template.format(markdown_table=md_table, user_query=query)
#             inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
#             output = self.model.generate(**inputs, max_length=4096)
#             return self.tokenizer.decode(output[0], skip_special_tokens=True)[len(input_text):]
#         except Exception as e:
#             print("inference failed: ", e)
#             return "failed"



# def init_ds_model(model_path):
#     init_process()
#     # 初始化 DeepSeek V3 模型
#     # model_path = "/home/kas/kas_workspace/open_source_llm/Qwen2-0.5B-Instruct"
#     deepseek_model = DeepSeekV3Model(model_path)

#     ds_model, *_ = deepspeed.initialize(
#         model=deepseek_model.model,
#         model_parameters=deepseek_model.model.parameters(),
#         config_params={
#                         "train_micro_batch_size_per_gpu": 1,
#                         "fp16": {
#                             "enabled": True
#                         },
#                         "zero_optimization": {
#                             "stage": 3,
#                             "offload_param": {
#                             "device": "cpu"
#                             },
#                             "offload_optimizer": {
#                             "device": "cpu"
#                             }
#                         }
#                         },  # 只做推理，不训练
#     )
#     ds_model.eval()
#     deepseek_model.model = ds_model
#     return deepseek_model

template = """<｜begin▁of▁sentence｜><｜User｜>你是一名专业的数据分析师，擅长从表格数据中提取信息、进行统计分析，并生成可执行的代码或有价值的建议。  
现在，我将提供一份表格数据（Markdown 格式），请你根据用户的需求进行分析。  

表格数据如下（仅截取前10行和前5列）：
{markdown_table}  

用户需求：
{user_query}  

请根据以上信息，完成以下任务之一（根据需求自动选择最合适的方式）：  
1. **数据摘要**：如果用户希望获取数据概览，请提供数据的基本统计信息，如均值、中位数、最大/最小值、数据分布等。  
2. **趋势分析**：如果用户想要了解数据的变化趋势，请分析关键数据指标，并提供可视化建议（如折线图、直方图）。  
3. **代码生成**：如果用户需要对数据进行操作，请输出相应的 Python 代码（使用 Pandas 进行数据处理）。  
4. **决策建议**：如果用户希望得到业务层面的见解，请基于数据提供合理的分析结论，并附上具体建议。  

请确保回答清晰、逻辑严谨，并附上必要的代码或计算公式。<｜Assistant｜><think>\n"""


# 配合openai的数据结构 获取template_v3对应的表格内容和提问
template_start = """<｜begin▁of▁sentence｜><｜User｜>你是一名专业的数据分析师，擅长从表格数据中提取信息、进行统计分析，并生成可执行的代码或有价值的建议。  
现在，我将提供一份表格数据，请你根据用户的需求编写python代码进行数据分析。  

请根据以上信息，完成以下任务之一（根据需求自动选择最合适的方式）：  
1. **数据摘要**：如果用户希望获取数据概览，请提供数据的基本统计信息，如均值、中位数、最大/最小值、数据分布等。  
2. **趋势分析**：如果用户想要了解数据的变化趋势，请分析关键数据指标，并提供可视化建议（如折线图、直方图）。  
3. **代码生成**：如果用户需要对数据进行操作，请输出相应的 Python 代码（使用 Pandas 进行数据处理）。  
4. **决策建议**：如果用户希望得到业务层面的见解，请基于数据提供合理的分析结论，并附上具体建议。  

请确保回答清晰、逻辑严谨，并附上必要的代码或计算公式。

如果是代码，请在返回结果前加上<code>标签，并不要返回其他内容，只返回纯代码;
如果是文本，请在返回结果前加上<text>标签;
如果是总结摘要，请在返回结果前加上<summary>标签.
"""


template_file = """
<｜User｜> 表格名称：
{}
"""

template_content = """
<｜User｜> 表格部分摘要数据如下：
{}  
"""

template_query = """
<｜User｜> 用户需求：
{}  
"""

template_assistant = """
<｜Asssistant｜> ：
{}  
"""

template_code = """
<｜Asssistant｜> 生成代码如下：
{}  
"""

template_exec = """
<｜Asssistant｜> 代码执行后结果如下：
{}
请判断是否需要修改代码，如需修改请继续生成新的代码，如果已经满足用户需求，请对上述对话进行简单总结摘要。
"""

template_user_general = """
<｜User｜> ：
{}
"""

template_assistant_general = """
<｜Asssistant｜> ：
{}
"""


template_end = """
<｜Assistant｜> <think>\n
"""

def parse_messages(messages):
    messages = messages["messages"]
    if not messages:
        return ""
    
    base_str = template_start

    for element in messages:
        if element["role"] == "user" and element["type"] == "file":
            base_str += template_file.format(element["content"])
        elif element["role"] == "user" and element["type"] == "description":
            base_str += template_content.format(element["content"])
        elif element["role"] == "user" and element["type"] == "text":
            base_str += template_query.format(element["content"])
        elif element["role"] == "assistant" and element["type"] == "text":
            base_str += template_query.format(element["content"])
        elif element["role"] == "assistant" and element["type"] == "code":
            base_str += template_code.format(element["content"])
        elif element["role"] == "assistant" and element["type"] == "execution":
            base_str += template_exec.format(element["content"])
        elif element["role"] == "assistant":
            base_str += template_assistant_general.format(element["content"])
        elif element["role"] == "user":
            base_str += template_user_general.format(element["content"])
        else:
            pass
    
    base_str += template_end
    return base_str


def r1(text, temperature=0.6, max_new_tokens=16000, not_reason=False):
    """
    调用生成API并返回响应。

    :param text: 要发送的文本内容
    :param temperature: 采样参数中的温度值
    :param max_new_tokens: 采样参数中的最大新标记数
    :return: API响应的JSON内容
    """

    # url = 'http://kmd-api.kas.wps.cn/api/11173/qFZUVy/infer'
    # url = "deepseek-r1-v3.ai-nlp-llm-test.svc.cluster.local/infer"
    url = URL_DATA_ANALYSIS

    # 请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    if not_reason:  text+="\n</think>"
    # print(text)
    # 请求体
    data = {
        "inputs": text,
        "stream": False,
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
            "details": True,
            "timeout": 3600
        }
    }
    start_time = time.time()

    # 发送POST请求
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=3600)

    print("ds response: ", response.text)

    end_time = time.time()

    # 计算耗时
    elapsed_time = end_time - start_time
    print(f"代码执行耗时: {elapsed_time} 秒")
    
    result = response.json()['generated_text']
    
    
    # 返回响应的JSON内容
    return result


def process_result(response, stop=""):
    think = ""
    finish_reason = "stop"
    response = response.replace("<｜end▁of▁sentence｜>", "")

    type_r = ""
    if "<code>" in response:
        type_r = "code"
        finish_reason = "code"
        response = response.replace("<code>", "").replace("</code>", "")
    elif "<text>" in response:
        type_r = "text"
        finish_reason = "text"
        response = response.replace("<text>", "").replace("</text>", "")
    elif "<summary>" in response:
        type_r = "summary"
        response = response.replace("<summary>", "").replace("</summary>", "")
        finish_reason = "stop"
    else:
        finish_reason = "stop"

    for s_word in ["<code>", "</code>", "<text>", "</text>", "<summary>", "</summary>"]:
        response = response.replace(s_word, "")

    idx = response.find("</think>")
    if idx != -1:
        think = response[:idx]
        response = response[idx + 8:]

    if stop:
        finish_reason = stop

    print(response)
    res = {
                "id": "test","usage": {
                    "prompt_tokens": -1,
                    "completion_tokens": -1,"total_tokens": -1
                    },
                "choices": [
                    {
                        "index": 0,
                        "role": "assistant",
                        "think": think,
                        "delta": response,
                        "finish_reason": finish_reason,
                        "type": type_r
                    }
                ]
            }
    
    return res