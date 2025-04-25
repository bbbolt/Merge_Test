import asyncio
import os
import tornado
import tornado.web
from concurrent.futures import ThreadPoolExecutor
from tornado.platform.asyncio import AnyThreadEventLoopPolicy


from handler import QueryHandler, HealthHandler
from retrieve import Retriever
from const.env import MODEL_PATH, LOG_LEVEL, PORT, INDEX_DB_INFO
import log
from get_chatbi_dataset import get_data_from_db, _periodic_update, DatabaseUpdater

async def setup_and_run():
    os.makedirs('logs', exist_ok=True)
    log.init(LOG_LEVEL, "logs/app.log")

    # 初始化数据
    function_db = await asyncio.get_running_loop().run_in_executor(
        ThreadPoolExecutor(max_workers=1), lambda: get_data_from_db(INDEX_DB_INFO)
)
    log.app_logger.info("init data")
    retriever = Retriever(model_path=MODEL_PATH, function_db=function_db["function_db"])

    # 启动服务
    app = tornado.web.Application([
        (r"/query", QueryHandler, dict(retriever=retriever)),
        (r"/health", HealthHandler, dict(retriever=retriever))
    ])
    app.listen(PORT)
    log.app_logger.info("init retriever")
    # 间隔时间更新数据
    database_updater = DatabaseUpdater(retriever)
    asyncio.create_task(_periodic_update(database_updater))

    log.app_logger.info("Retriever start")
    await asyncio.Future()  # 保持主循环运行


if __name__ == "__main__":
    asyncio.run(setup_and_run())

