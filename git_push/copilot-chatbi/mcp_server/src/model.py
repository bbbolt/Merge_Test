from const.env import MCP_API_KEY, MCP_API_BASE_URL
import openai

openai_client = openai.OpenAI(
            api_key=MCP_API_KEY,
            base_url=MCP_API_BASE_URL,
        )