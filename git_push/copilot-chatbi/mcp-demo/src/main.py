import tornado
import tornado.ioloop
import tornado.web
import os
from handler import MCPIntensionHandler
# from bussiness_mcp_client import BussinessMCPClient
from intension_mcp_client import IntensionMCPClient

from const.env import MCP_LOG_LEVEL, MCP_PORT
import log


# 初始化 Retriever
intension_mcp_client = IntensionMCPClient()
# bussiness_mcp_client = BussinessMCPClient()


def make_app():
    return tornado.web.Application([
        # (r"/bussiness_mcp_request", MCPQueryHandler,  dict(mcpclient=bussiness_mcp_client)),
        (r"/chat_bi/chat", MCPIntensionHandler,  dict(mcpclient=intension_mcp_client)),
    ])

if __name__ == "__main__":
    os.makedirs('logs', exist_ok=True)
    log.init(MCP_LOG_LEVEL, "logs/app.log")
    app = make_app()
    app.listen(MCP_PORT)
    tornado.ioloop.IOLoop.current().start()
    log.app_logger.info("start")
    