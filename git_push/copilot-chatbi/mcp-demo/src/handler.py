import os
from abs import ThreadCorsHandler
import json
import requests
import traceback
from LAC import LAC
# 装载LAC模型
lac = LAC(mode='rank')
# import jieba
from rouge import Rouge


rouger = Rouge()
# jieba.initialize()


def get_query_from_response(response, query):

    # 批量样本输入, 输入为多个句子组成的list，平均速率更快
    texts = [u"{response}".format(response=response), u"{query}".format(query=query)]
    lac_result = lac.run(texts)
    scores = rouger.get_scores(" ".join(lac_result[0][0]), " ".join(lac_result[1][0]))  
    if scores[0]["rouge-l"]["f"] > 0.4:
        return response
    else:
        return query


    


    
class MCPIntensionHandler(ThreadCorsHandler):
    
    def initialize(self, mcpclient):
        self.mcpclient = mcpclient

    async def process_func(self,session_id, request_id, messages):
        await self.mcpclient.connect_to_server(os.path.dirname(os.path.abspath(__file__)) + "/intension_mcp_tools.py")

        messages = self.mcpclient.process_messages(messages)

        answer = await self.mcpclient.process_query(messages)
        response_data = {
            "session_id": session_id,
            "request_id": request_id,
            "answer": answer
        }
        return response_data

    async def post(self):
        try:
            data = json.loads(self.request.body)
            session_id = data.get("session_id")
            request_id = data.get("request_id")
            # query = data.get("query")

            # 这里采用连续对话的形式
            messages = data.get("messages")

            if not messages:
                self.set_status(400)
                self.write({"error": "Missing 'messages' in request data"})
                return
            
            # 检查最后一位是否是query 如果是query需要进行指标检索
            # if messages[-1].get("role") == "user" and messages[-1].get("type") == "query":
            #     # 此时进行api检索 但实际上实现也是把api检索包装成mcp函数
            #     pass

            try:
                response_data = await self.process_func(session_id, request_id, messages)
                self.set_status(200)
                self.write(response_data)
            except Exception as e:
                self.set_status(500)
                print(traceback.format_exc())
                self.write({"error": str(e)})
            finally:
                await self.mcpclient.cleanup()
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON data in request"})