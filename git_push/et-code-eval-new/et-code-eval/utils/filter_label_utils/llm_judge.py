from transformers import AutoTokenizer
import json
from tqdm import tqdm
import re
import argparse

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
        max_tokens= 4096,
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


#
# def llm_completion(
#         messages,
#         temperature=0,
#         top_p=1,
#         top_k=0,
#         max_tokens=1024,
#         model_type="Qwen"
# ):
#     ######
#     ### max_tokens is the max tokens to generate,
#     ### max_model_len is the max length model can process (including prompt and generated tokens).
#     ######
#
#     chat_response = client.chat.completions.create(
#         model=model_type,
#         messages=messages,
#         temperature=temperature,
#         top_p=top_p,
#         max_tokens=max_tokens,
#         extra_body={
#             "repetition_penalty": 1,
#         },
#     )
#     response=chat_response.choices[0].message.content
#
#     return response

def get_conclusion(eval_file, model_type):

    for idx, prompt_json in enumerate(tqdm(eval_file, desc="Prompts ---> 模型裁决结论：")):
        judge_prompt = prompt_json["input"]

        messages = [
            {"role": "system", "content": "你是一个openpyxl专家，同样是WPS JS宏语言专家。"},
            {"role": "user", "content": judge_prompt}
        ]

        result = llm_completion(messages, model_type=model_type)
        eval_file[idx]["code_flag"] = result
    return eval_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--eval_file', type=str, help='Path to eval data')
    args = parser.parse_args()
    get_conclusion(args.eval_file)