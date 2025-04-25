from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import openai
from dotenv import load_dotenv
from const.env import MCP_API_KEY, MCP_API_BASE_URL, MCP_API_MODEL_NAME, RETRIEVER_URL
import json
import requests

load_dotenv()  # Load environment variables from .env

template_start = """<｜begin▁of▁sentence｜><｜System｜>你是一名专业的数据分析师，请你根据用户的需求使用提供的数据指标api或者自定义指标进行数据分析。  
你可能会进行fucntion calling任务，mcp任务，或者问答任务。
请确保回答清晰、逻辑严谨，返回内容尽量简洁。
"""

template_user = """
<｜User｜>: {}\n  
"""

template_assistant = """
<｜Asssistant｜>: {}\n  
"""

template_end = """
<｜Assistant｜>: 
"""


def retriever_service(query):
    """
    向 Tornado 服务发送查询请求并获取结果。
    
    :param query: 用户输入的查询字符串
    :param topk: 返回的 top-k 结果数量
    :param topp: 相似度阈值
    :return: 查询结果
    """
    url = RETRIEVER_URL
    headers = {"Content-Type": "application/json"}
    data = {
    "session_id": "abc123",
    "request_id": "abc123",
    "query": query

}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 检查 HTTP 响应状态码
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error while querying the service: {e}")
        return None


class IntensionMCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        # Initialize OpenAI client with Aliyun BaiLian API Key and base URL
        self.openai_client = openai.OpenAI(
            api_key=MCP_API_KEY,
            base_url=MCP_API_BASE_URL,
        )

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

    async def process_query(self, messages: str) -> str:
        """Process a query using OpenAI and available tools"""
        messages.insert(0, {"role": "system", "content": "你必须第一步先调用extracted_prob_index_from_user_query函数，第二步调用api_execution_after_user_select函数，最后调用chat_summary_after_api_execution进行总结"})  

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to mcp indies", [tool.name for tool in tools])

        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema  # Convert JSON schema to dict
        } for tool in response.tools]
        print("\nRetriever related indies:", [tool["name"] for tool in available_tools])

        # Initial OpenAI API call
        response = self.openai_client.chat.completions.create(
            model=MCP_API_MODEL_NAME,  # Replace with the desired model
            messages=messages,
            functions=available_tools,  # Provide tools as functions
            function_call="auto"  # Let the model decide when to call a function
        )


        # Process response and handle tool calls
        final_text = []

        while True:
            choice = response.choices[0]
            if choice.finish_reason == "stop":
                if messages[-1]["type"] != "summary":
                    final_text.append({"type": "stop", "content": choice.message.content, "role": "assistant"})
                else:
                    final_text.append({"type": "stop", "content": "", "role": "assistant"})
                break
            elif choice.finish_reason == "function_call":
                function_name = choice.message.function_call.name
                
                # 如果用户选择完指标后，需要继续执行
                if function_name == "extracted_prob_index_from_user_query":
                    final_text.append({
                    "type": "text",
                    "role": "assistant",
                    "content": "意图识别+指标检索"
                })
                elif function_name == "api_execution_after_user_select":
                    final_text.append({
                    "type": "text",
                    "role": "assistant",
                    "content": "执行指标"
                })
                # elif function_name == "retriever_api_info_after_extracted_prob_index":
                #     final_text.append({
                #     "type": "text",
                #     "role": "assistant",
                #     "content": "指标检索"
                # })
                
                elif function_name=="chat_summary_after_api_execution":
                    final_text.append({
                    "type": "text",
                    "role": "assistant",
                    "content": "信息总结"
                })
                    
                    
                if function_name=="chat_summary_after_api_execution":
                    filtered_messages = [message for message in  messages if ("name" in message and message["name"] in ["user_select_index",'api_execution_after_user_select']) or ("type" in message and message["type"] in ["query"])]
                    function_args = {"messages":filtered_messages}
                else:
                    function_args = json.loads(choice.message.function_call.arguments)

                    
                # Execute tool call
                result = await self.session.call_tool(function_name, function_args)


                # if function_name=="extracted_prob_index_from_user_query":
                #     result = await self.session.call_tool("retriever_api_info", {"query":result})



                # 如果用户选择完指标后，需要继续执行
                final_text.append({"type": "function_call", "content": f"[Calling tool {function_name} with args {function_args}]", "role": "assistant"})

                # Continue conversation with tool results
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": json.dumps(function_args, ensure_ascii=False)
                    },
                    "type": "function_call",
                })

                try:
                    res = json.loads(result.content[0].text)
                except:
                    res = {"type":"text", "data":"解析错误", "role":""}
                # {"type": "api", "data":{"retriever_query": retriever_query, "retriever_result": retriever_result}}
                if function_name == "extracted_prob_index_from_user_query":
                    retriever_query = res["data"]["retriever_query"]
                    retriever_result = res["data"]["retriever_result"]
                    info_list = [{
                        "role": "function",
                        "name": function_name,
                        "type": res["type"],
                        "content": retriever_query
                    },{
                        "role": "function",
                        "name": function_name,
                        "type": res["type"],
                        "content": retriever_result
                    }]
                    messages.extend(info_list)      
                    final_text.extend(info_list)
                else:
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "type": res["type"],
                        "content": res["data"]
                    })
                    final_text.append({"type": res["type"], "content": res["data"], "role": "assistant"})


                # 在这里判断 如果是调用了检索api需要返回给客户端确认
                # 如果是其它类型的 需要继续执行
                if res["type"] == "api":
                    # 模拟用户选则
                    prob_indies_dict = res["data"]["retriever_result"]["data"]
                    # 
                    messages.append({
                    "role": "user",
                    "name": "user_select_index",
                    "content": prob_indies_dict[0],
                    "type": "select"
                })
                    final_text.append({"type": "select", "content": prob_indies_dict[0], "role": "user"})

                # 如果用户选择完指标后，需要继续执行

                messages = self.process_messages(messages)
                # Get next response from OpenAI
                response =  self.openai_client.chat.completions.create(
                    model=MCP_API_MODEL_NAME,
                    messages=messages,
                    functions=available_tools,
                    function_call="auto"
                )

        return final_text

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


    def process_messages(self, messages):
        for line in messages:
            if not isinstance(line.get("content"), str):
                line["content"] = json.dumps(line["content"], ensure_ascii=False)
        # if not messages:
        #     return ""
    
        # base_str = template_start

        # for element in messages:
        #     if element["role"] == "user":
        #         base_str += template_user.format(element["content"])
        #     elif element["role"] == "assistant":
        #         base_str += template_assistant.format(element["content"])
        #     else:
        #         pass
        
        # base_str += template_end
        return messages