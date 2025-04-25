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

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

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

        choice = response.choices[0]
        if choice.finish_reason == "stop":
            return {"retriever":False, "content":choice.message.content}
        
        elif choice.finish_reason == "function_call":
            function_name = choice.message.function_call.name
            function_args = json.loads(choice.message.function_call.arguments)
            # Execute tool call
            if function_name == "retriever_business_info":
                response = retriever_service(query)
                return {"retriever":True, "content":response["data"]}
            else:
                response = await self.session.call_tool(function_name, function_args)
                return {"retriever":False, "content":response.content[0].text}

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
    
