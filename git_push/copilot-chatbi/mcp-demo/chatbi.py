from client import MCPClient
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
# from retrieve import Retriever
import sys
import openai

class MCPClientV2(MCPClient):
    def __init__(self):
        super().__init__()
        # Initialize OpenAI client with Aliyun BaiLian API Key and base URL
        api_key = ["sk-1ff31057e07e4e639f08221fe958ec5e"]
        self.openai_client = openai.OpenAI(
            api_key=api_key[0],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        # self.retriver = Retriever(model_path='/home/kas/kas_workspace/maoyanyu/embedding_models/bge-small-zh-v1.5', function_db=["add", "multiply", "cal_cirlcle_area"])
        
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
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema  # Convert JSON schema to dict
        } for tool in response.tools]

        # Initial OpenAI API call
        response =  self.openai_client.chat.completions.create(
            model="qwen2.5-7b-instruct",  # Replace with the desired model
            messages=messages,
            functions=available_tools,  # Provide tools as functions
            function_call="auto"  # Let the model decide when to call a function
        )

        # Process response and handle tool calls
        final_text = []

        while True:
            choice = response.choices[0]
            if choice.finish_reason == "stop":
                final_text.append(choice.message.content)
                break
            elif choice.finish_reason == "function_call":
                function_name = choice.message.function_call.name
                function_args = json.loads(choice.message.function_call.arguments)

                # Execute tool call
                result = await self.session.call_tool(function_name, function_args)
                final_text.append(f"[Calling tool {function_name} with args {function_args}]")

                # Continue conversation with tool results
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": json.dumps(function_args)
                    }
                })
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": result.content
                })

                # Get next response from OpenAI
                response =  self.openai_client.chat.completions.create(
                    model="qwen2.5-7b-instruct",
                    messages=messages,
                    functions=available_tools,
                    function_call="auto"
                )

        return "\n".join(final_text)
    

class chatBI:
    def __init__(self):
        pass

    async def main():
        sys.argv =["/home/kas/chatBI/client.py", "/home/kas/chatBI/math_server.py"]
        if len(sys.argv) < 2:
            print("Usage: python client.py <path_to_server_script>")
            sys.exit(1)
            
        client = MCPClientV2()
        try:
            await client.connect_to_server(sys.argv[1])
            await client.chat_loop()
        finally:
            await client.cleanup()




if __name__ == "__main__":
    task = chatBI()
    asyncio.run(task.main())