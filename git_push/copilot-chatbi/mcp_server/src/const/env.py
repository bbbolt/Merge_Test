import os

# PORT
MCP_PORT = int(os.getenv("MCP_PORT", 8100))
MCP_MAX_WORKERS = int(os.getenv("MCP_MAX_WORKERS", 4))

# LLM API 配置
MCP_API_KEY = str(os.getenv("MCP_API_KEY", "sk-1ff31057e07e4e639f08221fe958ec5e"))
MCP_API_BASE_URL = str(os.getenv("MCP_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"))
MCP_API_MODEL_NAME = str(os.getenv("MCP_API_MODEL_NAME", "qwen2.5-7b-instruct"))

# Retriever API配置
RETRIEVER_URL = str(os.getenv("MCP_API_KEY", "http://kmd-api.kas.wps.cn/api/11286-v2/nn3ihw/query"))

# 错误类型
ERROR_CODE_DICT = {"SUCESS":(0, "请求成功"), "LACK_FIELD":(1, "字段缺失"), "ERROR_REQUEST":(2, "请求失败")}


# LOG
MCP_LOG_LEVEL = str(os.getenv("MCP_LOG_LEVEL", "INFO"))