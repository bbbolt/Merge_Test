from mcp.server.fastmcp import FastMCP
from model import openai_client
from const.env import MCP_API_MODEL_NAME, RETRIEVER_URL
import requests

mcp = FastMCP("Intension")


@mcp.tool()
def custom_chat_llm(query: str) -> str:
    """当用户问题与企业信息不相关，不需要使用查询工具，只需要与用户正常交流"""
    messages = [
            {
                "role": "user",
                "content": query
            }
        ]
    try:
        response = openai_client.chat.completions.create(
                        model=MCP_API_MODEL_NAME,  # Replace with the desired model
                        messages=messages
                    ).choices[0].message.content
    except:
        response = "OpenAI API调用错误"

    return response


@mcp.tool()
def retriever_business_info(query: str) -> list:
    """当用户问题与企业信息相关，需要使用查询工具查询相关信息，才能更好的回答用户"""
    # response = retriever_service(query)["data"]
    response = ""
    return response


if __name__ == "__main__":
    mcp.run(transport="stdio")