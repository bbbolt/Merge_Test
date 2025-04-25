from sentence_transformers import SentenceTransformer
import numpy as np
import log

import psycopg2
import pandas as pd
import datetime

from const.env import INDEX_DB_INFO, DB_CONNECT_TIME, RETRY_TIMES, RETRIEVE_LIMIT_SEMANTIC, RETRIEVE_LIMIT_KEYWORD, ROUGE_L_RECALL_SCORE_THRESHOLD
import time
from norm_text import clean_pip
import jieba


from rouge import Rouge 

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


class Retriever(object):
    def __init__(self, model_path, function_db):
        self.model = SentenceTransformer(model_path)
        self.function_db = function_db
        self.map = {
            "dau": "日活跃用户数",
            "DAU": "日活跃用户数",
            "mau": "月活跃用户数",
            "MAU": "月活跃用户数",
            "uv": "用户数",
            "UV": "用户数",
            "pv": "页面浏览量",
            "PV": "页面浏览量",
            "uvdau": "用户日活跃率",
            "UVDAU": "用户日活跃率",
            "uvmau": "用户月活跃率",
            "UVMAU": "用户月活跃率",
            "uvdau_ratio": "用户日活跃率",
            "UVDAU_RATIO": "用户日活跃率",
            "uvmau_ratio": "用户月活跃率",
            "UVMAU_RATIO": "用户月活跃率",
        }

        log.app_logger.info("初始化数据库..")
        self.embed_cache = self.embedding_layer([i["cn_name"] for i in function_db])
        self.segmented_keyword_cache = [jieba.lcut(clean_pip.norm_text(keyword)) for keyword in [i["name"] for i in function_db] + [i["cn_name"] for i in function_db]]
        self.rouge = Rouge()


    def update_function_db(self, function_db):
        self.function_db = function_db
        self.embed_cache = self.embedding_layer([i["cn_name"] for i in function_db])
        self.segmented_keyword_cache = [jieba.lcut(clean_pip.norm_text(keyword)) for keyword in [i["name"] for i in function_db] + [i["cn_name"] for i in function_db]]

    def embedding_layer(self, text):
        return self.model.encode(text, normalize_embeddings=True)

    def get_similarity(self, text1, db):
        embedding1 = self.embedding_layer(text1)
        return np.dot(embedding1, db.T)

    def get_top_k(self, querys: str, topk: int, topp: float):
        log.app_logger.info("query: " + str(querys))
        for item in self.map:
            querys = querys.replace(item, self.map[item])

        similarity = self.get_similarity([querys], self.embed_cache)
        res = {}
        top_k_indices = None
        for idx, sim in enumerate(similarity):
            # 筛选出相似度大于 topp 的索引
            high_similarity_indices = np.where(sim > topp)[0]
            if len(high_similarity_indices) > topk:
                # 相似度大于 topp 的超过topk个，取前 topk 个
                top_k_indices = high_similarity_indices[sim[high_similarity_indices].argsort()[::-1][:topk]]
            else:
                # 不足 topk 个，按实际数量取
                top_k_indices = high_similarity_indices[sim[high_similarity_indices].argsort()[::-1]]

        retrieve_keys = list(np.array(self.function_db)[top_k_indices])
        top_k_similarities = sim[top_k_indices]
        
        # 构建包含函数名及其对应相似度的字典
        for index in range(len(top_k_indices)):
            retrieve_keys[index]["score"] = round(float(top_k_similarities[index]), 2)
            retrieve_keys[index]["retrieve_type"] = "semantic"
        return retrieve_keys

    def hit_keywords(self, query: str):
        # 用于记录每个 function_dict 的索引及其命中次数
        hit_count = {}
        # 使用 jieba 对查询语句进行分词
        seg_list = jieba.lcut(query)
        for idx, segmented_keyword in enumerate(self.segmented_keyword_cache):
            for keyword_part in segmented_keyword:
                for word in seg_list:
                    if keyword_part == word:
                        func_idx = idx % len(self.function_db)
                        # 如果 func_idx 不在 hit_count 中，初始化命中次数为 0
                        if func_idx not in hit_count:
                            hit_count[func_idx] = 0
                        # 命中次数加 1
                        hit_count[func_idx] += 1

        res = []
        for func_idx, count in hit_count.items():
            function_dict = self.function_db[func_idx].copy()
            # 使用 jieba 进行分词
            hypothesis_seg = " ".join(jieba.cut(function_dict["name"]))
            cn_hypothesis_seg = " ".join(jieba.cut(function_dict["cn_name"]))
            reference_seg_lst = jieba.lcut(query)
            reference_seg = " ".join(reference_seg_lst)
            function_dict["score"] = max(self.rouge.get_scores(hypothesis_seg, reference_seg)[0]['rouge-l']['r'], 
                                         self.rouge.get_scores(cn_hypothesis_seg, reference_seg)[0]['rouge-l']['r'])
            function_dict["retrieve_type"] = "keyword"
            if (len(reference_seg_lst) <3 and function_dict['score'] > 0.9) or function_dict["score"] >= 3 / len(reference_seg_lst) * ROUGE_L_RECALL_SCORE_THRESHOLD:
                res.append(function_dict)

        # 按照命中次数对结果列表进行排序
        res.sort(key=lambda x: x["score"], reverse=True)
        return res

    def rank(self, recall_collection):
        """
        根据分值和其他关键词排序模块
        对召回结果，按照时间和score排序
        """
        def sort_key(item):
            # 定义时间关键词（可根据需求扩展）
            time_keywords = ["次"]
            # 检查 cn_name 和 description 是否包含时间关键词
            cn_has_time = any(kw in item["cn_name"] for kw in time_keywords)
            desc_has_time = any(kw in item["description"] for kw in time_keywords)
            has_time = cn_has_time or desc_has_time
            # 返回排序键值元组：(是否含时间词, -score, 中文名)
            return (-item["score"], has_time, item["cn_name"])

        # 按自定义规则排序
        sorted_data = sorted(recall_collection, key=sort_key)

        # 打印结果（示例输出）
        for item in sorted_data:
            print(f"{item['cn_name']} (Score: {item['score']})")
        return sorted_data



    def run(self, user_input, topk, topp):
        final_collection = []
        has_collected_function = set()

        # log.app_logger.info(f"Retriever Database Version: {self.function_db[0]['latest_time']}")
        user_input = clean_pip.norm_text(user_input)

        semantic_sim_search_res = self.get_top_k(user_input, topk, topp)[:RETRIEVE_LIMIT_SEMANTIC] if RETRIEVE_LIMIT_SEMANTIC > 0 else self.get_top_k(user_input, topk, topp)
        print(semantic_sim_search_res)
        keyword_hit_search_res = self.hit_keywords(user_input)[:RETRIEVE_LIMIT_KEYWORD] if RETRIEVE_LIMIT_KEYWORD > 0 else self.hit_keywords(user_input)

        for item in keyword_hit_search_res + semantic_sim_search_res:
            if item["name"] not in has_collected_function:
                final_collection.append(item)
                has_collected_function.add(item["name"])
            else:
                continue
        final_collection = self.rank(final_collection)
        return final_collection


if __name__ == "__main__":
    function_db = get_data_from_db(INDEX_DB_INFO)["function_db"]

    retriever = Retriever(model_path='/home/kas/kas_workspace/maoyanyu/embedding_models/bge-small-zh-v1.5', function_db=function_db)
    res = retriever.run("AI", topk=10, topp=0.6)
    print(res)
