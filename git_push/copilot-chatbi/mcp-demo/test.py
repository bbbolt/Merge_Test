import requests

def query_service(query, topk, topp):
    """
    向 Tornado 服务发送查询请求并获取结果。
    
    :param query: 用户输入的查询字符串
    :param topk: 返回的 top-k 结果数量
    :param topp: 相似度阈值
    :return: 查询结果
    """
    url = "http://localhost:8100//chat_bi/chat"
    headers = {"Content-Type": "application/json"}
    data = {
    "session_id": "session_id",
    "request_id": "session_id",
    "messages": [
        {
            "role": "user",
            "content": "我想查一下得谱的相关指标",
            "type": "query"
        }
    ]
}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 检查 HTTP 响应状态码
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error while querying the service: {e}")
        return None

if __name__ == "__main__":
    # 示例查询
    query = "日活跃用户数"
    topk = 5
    topp = 0.6

    # 调用服务
    results = query_service(query, topk=topk, topp=topp)

    # 打印结果
    if results:
        print("Query Results:")
        print(results)