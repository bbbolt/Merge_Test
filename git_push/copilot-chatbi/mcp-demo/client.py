import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()  # Load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        # Initialize OpenAI client with Aliyun BaiLian API Key and base URL
        api_key = ["sk-1ff31057e07e4e639f08221fe958ec5e"]
        self.openai_client = openai.OpenAI(
            api_key=api_key[0],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
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

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            # try:
            query = input("\nQuery: ").strip()
            
            if query.lower() == 'quit':
                break
                
            response = await self.process_query(query)
            print("\n" + response)
                    
            # except Exception as e:
            #     print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    sys.argv =["/Users/cerax/Downloads/copilot-chatbi/client.py", "/Users/cerax/Downloads/copilot-chatbi/math_server.py"]
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())