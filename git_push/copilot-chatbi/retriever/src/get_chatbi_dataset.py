import psycopg2
import pandas as pd
import datetime

import asyncio
from concurrent.futures import ThreadPoolExecutor

from retrieve import Retriever
from const.env import INDEX_DB_INFO, INDEX_DB_UPDATE_INTERVAL, DB_CONNECT_TIME, RETRY_TIMES
import log
import time


class DatabaseUpdater:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def update_database(self):
        try:
            function_db = await asyncio.get_running_loop().run_in_executor(
                self.executor, lambda: get_data_from_db(INDEX_DB_INFO)
            )
            log.app_logger.info(f"Latest Database Version: {function_db['latest_time']} get successfully.")
            self.retriever.update_function_db(function_db["function_db"])
            log.app_logger.info("Database updated successfully.")
        except Exception as e:
            log.app_logger.error(f"Error updating database: {e}")


async def _periodic_update(database_updater: DatabaseUpdater):
    while True:
        await database_updater.update_database()
        await asyncio.sleep(INDEX_DB_UPDATE_INTERVAL)


def get_data_from_db(index_db_info):
    max_retries = RETRY_TIMES
    for attempt in range(max_retries):
        connection = None
        try:
            # 建立数据库连接
            connection = psycopg2.connect(
                host=index_db_info["host"],
                port=index_db_info["port"],
                user=index_db_info["user"],
                password=index_db_info["password"],
                database=index_db_info["database"],
                connect_timeout=DB_CONNECT_TIME
            )
            cursor = connection.cursor()
            dataframes = {}
            log.app_logger.info("链接pgsql成功")
            function_db = []
            for table in index_db_info["tables"]:
                try:
                    # 执行查询并将结果存储在 DataFrame 中
                    df = pd.read_sql(f"SELECT * FROM {table}", connection)
                    # cursor.execute(f"SELECT * FROM {table}")
                    # data = cursor.fetchall()
                    # import pdb
                    # pdb.set_trace()
                    dataframes[table] = df
                except (Exception, psycopg2.Error) as table_error:
                    print(f"从表 {table} 获取数据时出错: {table_error}")

            if dataframes:
                for df in dataframes.values():
                    if 'name' in df.columns and 'biz_description' in df.columns and 'url' in df.columns and 'type' in df.columns and 'first_catalog' in df.columns and 'display_name' in df.columns:
                        for index, row in df.iterrows():
                            function_db.append({
                                "name": row['name'],
                                "description": row['biz_description'],
                                "url": row['url'],
                                "type": row['type'],
                                "category": row['first_catalog'],
                                "cn_name": row['display_name']
                            })
            cursor.close()
            
            return {"latest_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "function_db": function_db}
        except (Exception, psycopg2.Error) as db_error:
            if attempt < max_retries - 1:
                print(f"第 {attempt + 1} 次尝试失败，错误信息: {db_error}，即将进行第 {attempt + 2} 次尝试...")
            else:
                print(f"所有 {max_retries} 次尝试均失败，错误信息: {db_error}")
            time.sleep(1)
            continue
        finally:
            if connection:
                connection.close()
    return None

if __name__ == "__main__":
    function_db = get_data_from_db(INDEX_DB_INFO)
    print(function_db["latest_time"])
    