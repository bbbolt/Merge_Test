from transformers import AutoTokenizer
import json
from tqdm import tqdm
import re
import argparse
import time
import json
import requests
from pydantic import BaseModel
from typing import Optional

from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)



QINGQIU_URL="http://kmd-api.kas.wps.cn/api/10893-v2/B2RYea/v1/chat/completions"

class OutputMessage(BaseModel):
    text_output: Optional[str] = ''

class UsageInfo(BaseModel):
    completion_tokens: Optional[int] = 0
    prompt_tokens: Optional[int] = 0
    total_tokens: Optional[int] = 0

class QingqiuResponse(BaseModel):
    code: int
    data: Optional[OutputMessage] = None
    msg: Optional[str] = ''
    usage: Optional[UsageInfo] = None



def llm_completion(
        messages,
        functions = None,
        temperature = 0.0,
        top_p = 1,
        top_k = 0,
        max_tokens= 392,
        stop = None,
        do_sample = False,
        stop_words = None,
        model_type="Qwen"
    ):
    if isinstance(messages, str):
        messages = [{"role":"user", "content":messages}]
    url = QINGQIU_URL
    headers = {
        'X-Request-Id': '123',
        'Content-Type': 'application/json; charset=utf-8'
    }

    data = {
        "messages" : messages,
        "infer_args": {
            "temperature" : temperature,
            "top_k": top_k,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "do_sample": do_sample
        },
        stop_words: stop_words
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        answer = QingqiuResponse(**response.json())
        return answer.data.text_output
    return None

def get_sheet_table(eval_file, model_type):

    res = []
    for sheet1_json in tqdm(eval_file, desc="Prompts ---> 表格样例值"):
        table_desc, table_prompts = list(sheet1_json.keys())[0], list(sheet1_json.values())[0]


        outputs = []

        for table_col_prompt in tqdm(table_prompts,desc="遍历所有列"):
            messages = [
                {"role": "system", "content": "你是一个举例子小能手。"},
                {"role": "user", "content": table_col_prompt[2]}
            ]
            for _ in range(3):
                try:
                    result = llm_completion(messages, model_type=model_type)
                    break
                except:
                    time.sleep(1)
            outputs.append(result)
        # Print the outputs.
        for idx, output in enumerate(outputs):
            table_prompts[idx][2] = re.split(r'\$\$', output)
        sheet1_json[table_desc] = table_prompts
        res.append(sheet1_json)
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--eval_file', type=str, help='Path to eval data')
    args = parser.parse_args()
    get_sheet_table(args.eval_file)