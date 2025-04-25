import pandas as pd
import os
import uuid
from model import r1, template, parse_messages, process_result
import tornado
from report import async_report_log
import time
import json

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_PATH, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_ROWS = 10
MAX_COLUMNS = 10


# # model_path = "/home/kas/kas_workspace/open_source_llm/DeepSeek-R1-Distill-Qwen-7B"
# model_path = "/home/kas/kas_workspace/open_source_llm/Qwen2-0.5B-Instruct"
# deepseek_model = init_ds_model(model_path)
# print("load model down")


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            file = self.request.files['file'][0]
            filename = file['filename'].split("/")[-1]
            file_uuid = str(uuid.uuid4())
            file_dir = os.path.join(UPLOAD_DIR, file_uuid)
            os.makedirs(file_dir, exist_ok=True)
            filepath = os.path.join(file_dir, filename)

            with open(filepath, "wb") as f:
                f.write(file['body'])
            
            self.write({"is_success": True, "file_uuid": file_uuid, "filename": filename, "message": "File uploaded successfully."})
        except Exception as e:
            print("File uploaded failed: ", e)
            self.write({"is_success": False, "file_uuid": file_uuid, "filename": filename, "message": "File uploaded failed."})
 
from abc import ABC


from abs import ThreadCorsHandler
from tornado.concurrent import run_on_executor

class QueryHandler(ThreadCorsHandler, ABC):

    @run_on_executor
    def post(self):
        response = ""
        stop = ""
        messages = []
        try:
            # file_uuid = self.get_argument("file_uuid")
            # filename = self.get_argument("filename")
            # query = self.get_argument("query")
            # filepath = os.path.join(UPLOAD_DIR, file_uuid, filename)
            
            # if not os.path.exists(filepath):
            #     self.write({"error": "File not found."})
            #     return
            
            # df = pd.read_excel(filepath)
            # df = df.iloc[:MAX_ROWS, :MAX_COLUMNS]  # 限制最大行列数
            # md_table = df.to_markdown()

            # input_text = template.format(markdown_table=md_table, user_query=query)

            messages = json.loads(self.request.body)
            if not messages:
                return ""
            
            if messages["messages"] and messages["messages"][-1].get("type") == "execution":
                stop = "stop"
            
            # 默认使用非流式 其他参数也暂时不用 

            input_text = parse_messages(messages)
            # print("input_text: ", input_text)
            response = r1(input_text)
            # response = "测试"
            # response = deepseek_model.generate_response(md_table, query)
            print("#"*30)
            print("messages: ", messages)
            print("input_text: ", input_text)
            print("*"*30)

            res = process_result(response=response, stop=stop)

            async_report_log(
                ori_input=str(messages),
                prompt=input_text,
                ori_output=str(response),
                output="",
                infer_cost_ms=0.0,
                t_start=0.0,
                t_end=0.0,
                business_key='copilot-data-analysis-' + str(self.request_id),
                batch_size=1,
                infer_args={},
                scene_args={}
            )

            self.write(json.dumps({"is_success": True, "data": res, "status": {"code": 0, "message": "ok"}}, ensure_ascii=False))
        except Exception as e:
            print("get ans failed: ", e)
            self.write(json.dumps({"is_success": False, "data": {}, "status": {"code": -1, "message": "fail"}}, ensure_ascii=False))
