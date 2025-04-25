import os

# PORT
PORT = int(os.getenv("PORT", 8000))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))

# 模型路径
MODEL_PATH = str(os.getenv("MODEL_PATH", '/home/kas/kas_workspace/maoyanyu/embedding_models/bge-small-zh-v1.5'))

# function召回的阈值Top-K与Top-P
RAG_THRESHOLD_TOPK = int(os.getenv("RAG_THRESHOLD_TOPK", 10))
RAG_THRESHOLD_TOPP = float(os.getenv("RAG_THRESHOLD_TOPP", 0.6))
ROUGE_L_RECALL_SCORE_THRESHOLD = float(os.getenv("ROUGE_L_RECALL_SCORE_THRESHOLD", 0.2))

# 错误类型
ERROR_CODE_DICT = {"SUCCESS":(0, "请求成功"), "LACK_FIELD":(1, "字段缺失"), "ERROR_REQUEST":(2, "请求失败")}


# 数据库信息
INDEX_DB_INFO = {
                    "host": str(os.getenv("INDEX_DB_HOST", "")),
                    "port": str(os.getenv("INDEX_DB_PORT", "")),
                    "user": str(os.getenv("INDEX_DB_USER", "")),
                    "password": str(os.getenv("INDEX_DB_PASSWORD", "")),
                    "database": str(os.getenv("INDEX_DB_DATABASE", "metrics_meta")),
                    "tables": list(os.getenv("INDEX_DB_TABLES", ["metrics_meta_info", "metrics_dimension"]))
                }



# 检索类型限制
RETRIEVE_LIMIT_KEYWORD = int(os.getenv("RETRIEVE_LIMIT_KEYWORD", -1)) # -1表示不限制
RETRIEVE_LIMIT_SEMANTIC = int(os.getenv("RETRIEVE_LIMIT_SEMANTIC", -1)) # -1表示不限制


# 数据库更新频率
RETRY_TIMES = int(os.getenv("RETRY_TIMES", 5))
INDEX_DB_UPDATE_INTERVAL = int(os.getenv("INDEX_DB_UPDATE_INTERVAL", 5))
DB_CONNECT_TIME = int(os.getenv("DB_CONNECT_TIME", 5))

# LOG
LOG_LEVEL = str(os.getenv("LOG_LEVEL", "INFO"))


SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(SRC_DIR)
health_check_dir = os.path.join(PROJECT_DIR, "check")

