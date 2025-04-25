import os

# 环境变量
USE_TIME_LOG = int(os.getenv("USE_TIME_LOG", 1))
USE_EXAMPLE = int(os.getenv("USE_EXAMPLE", 0))
USE_TRI_EXAMPLE = int(os.getenv("USE_TRI_EXAMPLE", 1))
USE_EXAMPLE_NUM = int(os.getenv("USE_EXAMPLE_NUM", 1))

# 表格结构识别
USE_REQ_TEXT_PARSE = int(os.getenv("USE_REQ_TEXT_PARSE", 0))  # 是否解析客户端传过来的文档结构文本
USE_DEBUG_MATCH_TABLE = int(os.getenv("USE_DEBUG_MATCH_TABLE", 1))
if USE_DEBUG_MATCH_TABLE:
    MATCH_TABLE_HOST = "seti.jimo.wps.cn"
    MATCH_TABLE_ClientType = "model"
    MATCH_TABLE_JmClientEntrance = "jsapi"
    MATCH_TABLE_JmAppid = "base_algo"
    MATCH_TABLE_TOKEN = os.getenv("MATCH_TABLE_TOKEN", "")

    HOST_MATCH_TABLE = "120.92.124.158"
    URL_MATCH_TABLE = os.getenv("URL_MATCH_TABLE", "http://" + HOST_MATCH_TABLE + "/internal/v1/data_ask_asst/structured")
else:
    MATCH_TABLE_HOST = "seti.jimo.wps.cn"
    MATCH_TABLE_ClientType = "model"
    MATCH_TABLE_JmClientEntrance = "jsapi"
    MATCH_TABLE_JmAppid = "base_algo"
    MATCH_TABLE_TOKEN = os.getenv("MATCH_TABLE_TOKEN", "")
    URL_MATCH_TABLE = os.getenv("URL_MATCH_TABLE", "")

USE_DEBUG_MODEL_INFER = int(os.getenv("USE_DEBUG_MODEL_INFER", 1))
if USE_DEBUG_MODEL_INFER:
    MODEL_INFER_HOST = os.getenv("URL_HOST", "qingqiu-test.wps.cn")
    HOST_MODEL_INFER = "172.16.53.133"
    # HOST_MODEL_INFER = "120.92.124.158"


    # URL
    URL_GENERATE_JSON = os.getenv("URL_GENERATE_JSON",
                                  "http://" + HOST_MODEL_INFER + "/v1/jsapi/model/completions")
    URL_STREAM_GENERATE = os.getenv("URL_STREAM_GENERATE",
                                    "http://" + HOST_MODEL_INFER + "/v1/jsapi/model/completions_stream")
else:
    MODEL_INFER_HOST = os.getenv("URL_HOST", "qingqiu.wps.cn")

    URL_GENERATE_JSON = os.getenv("URL_GENERATE_JSON",
                                  "http://" + MODEL_INFER_HOST + "/v1/jsapi/model/completions")
    URL_STREAM_GENERATE = os.getenv("URL_STREAM_GENERATE",
                                    "http://" + MODEL_INFER_HOST + "/v1/jsapi/model/completions_stream")

USE_FEWSHOT = int(os.getenv("USE_FEWSHOT", 1))

# 告警
API_TIME_ALERT_MAX = int(os.getenv("API_TIME_ALERT_MAX", 10))
GENERATE_CONNECT_TIMEOUT = float(os.getenv("GENERATE_CONNECT_TIMEOUT", 1.5))
GENERATE_READ_TIMEOUT = int(os.getenv("GENERATE_READ_TIMEOUT", 30))

TABLE_MATCH_CONNECT_TIMEOUT = float(os.getenv("TABLE_MATCH_CONNECT_TIMEOUT", 2.5))
TABLE_MATCH_READ_TIMEOUT = int(os.getenv("TABLE_MATCH_READ_TIMEOUT", 30))

# alert
ALERT_SWITCH_OPEN = os.getenv("ALERT_SWITCH_OPEN", 0) in ['true', True, 'True', 1, '1']
ALERT_API = os.getenv("ALERT_API", "")
HOSTNAME = os.getenv("HOSTNAME", "")

# 短连接
USE_SHORT_LINK = int(os.getenv("USE_SHORT_LINK", 1))
USE_SHORT_STREAM_LINK = int(os.getenv("USE_SHORT_STREAM_LINK", 0))

# 模型配置
MAX_GEN_TOKENS = int(os.getenv("MAX_GEN_TOKENS", 2048))
GEN_CONFIG_TOP_P = float(os.getenv("GEN_CONFIG_TOP_P", 0.0))
GEN_CONFIG_TEMPERATURE = float(os.getenv("GEN_CONFIG_TEMPERATURE", 0.8))  #0.8
GEN_CONFIG_TOP_K = int(os.getenv("GEN_CONFIG_TOP_K", 0))
MODEL_VERSION = str(os.getenv("MODEL_VERSION", "1.0.0"))
MODEL_TYPE = str(os.getenv("MODEL_TYPE", "COMMONJS"))
if USE_EXAMPLE:
    MODEL_TYPE = "USE_RA"

# 日志上报配置
# KS3_AK
KS3_AK = os.environ.get("KS3_AK", "")
# KS3_SK
KS3_SK = os.environ.get("KS3_SK", "")
# KS3_BUCKET
KS3_BUCKET = os.environ.get("KS3_BUCKET", "develop")
# KS3_ENDPOINT
KS3_ENDPOINT = os.environ.get("KS3_ENDPOINT", "ks3-cn-beijing-internal.ksyuncs.com")
# KS3_PREFIX
KS3_PREFIX = os.environ.get("KS3_PREFIX", "aigc/copilot_jscode_logs/")
# 日志上报的采样比例，浮点数，范围[0, 1]
LOG_REPORT_RATIO = max(0.0, min(1.0, float(os.environ.get("LOG_REPORT_RATIO", "1.0"))))

# tornado 多线程接收请求的线程池
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))

USE_ALL_FUZZY_MATCH = int(os.getenv("USE_ALL_FUZZY_MATCH", 1))

ROUGE_THRESHOLD = float(os.getenv("ROUGE_THRESHOLD", 0.1))

USE_OLD = int(os.getenv("USE_OLD", 1))
aes_key = str(os.getenv("aes_key", ""))

# 是否拼接 Human: Asssitant: 前后缀
USE_HUMAN_PREFIX = int(os.getenv("USE_HUMAN_PREFIX", 0))

MAX_TABLE_AREA = int(os.getenv("MAX_TABLE_AREA", 12))

# prompt中表格长度
SINGLE_TABLE_STRUCTURE_MAX_LEN = int(os.getenv("SINGLE_TABLE_MAX_LEN", 1000))
MULTI_TABLE_STRUCTURE_MAX_LEN = int(os.getenv("MULTI_TABLE_STRUCTURE_MAX_LEN", 1000))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", 0.3))

# case召回的阈值
RAG_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", 0.6))

# LOG
LOG_LEVEL = str(os.getenv("LOG_LEVEL", "INFO"))

# 普罗米修斯配置
PROM_APP_NAME = os.getenv("APP_NAME", "copilot_jsapi")
PROM_PORT = int(os.getenv("PROM_PORT", 8123))
PROM_METRIC_ENABLE = os.getenv("PROM_METRIC_ENABLE", False) in ['true', True, 'True', 1, '1']

RATE_LIMIT_TOKEN = os.getenv("RATE_LIMIT_TOKEN", "default:50")

USE_CACHE = int(os.getenv("USE_CACHE", 0))
OFFLINE_AUTHORATION = os.getenv("OFFLINE_AUTHORATION", "")

# 是否使用千问推理
USE_QWEN = int(os.getenv("USE_QWEN", 0))
# 用于计算相似度的数据长度限制
TABLE_DATA_NUM = int(os.getenv("TABLE_DATA_NUM", 200))
TABLE_COL_NUM = int(os.getenv("TABLE_COL_NUM", 100))
DATA_LENGTH_LIMIT = int(os.getenv("DATA_LENGTH_LIMIT", 20))
QUESTION_LENGTH_LIMIT = int(os.getenv("QUESTION_LENGTH_LIMIT", 200))

# 防止长度过长
PROMPT_COL_NUM = int(os.getenv("PROMPT_COL_NUM", 170))
REMAIN_COL_NUM = int(os.getenv("REMAIN_COL_NUM", 26))
COL_SCORE_THRESHOLD = float(os.getenv("COL_SCORE_THRESHOLD", 0.3))
MODEL_PROMPT_MAX_LENGTH = int(os.getenv("MODEL_PROMPT_MAX_LENGTH", 6500))
MAX_SHEET_LENGTH = int(os.getenv("MAX_SHEET_LENGTH", 5000))

MULTI_TABLE_NUM = int(os.getenv("MULTI_TABLE_NUM", 5))

# 是否要去掉选中区域描述
USE_NO_SELECTION = int(os.getenv("USE_NO_SELECTION", 1))
SELECTION_KEYWORDS = str(os.getenv("SELECTION_KEYWORDS", "选,这,那")).split(",")

URL_DATA_ANALYSIS = str(os.getenv("URL_DATA_ANALYSIS", "http://qy-api.kas.wps.cn/api/11173/qFZUVy/infer"))

