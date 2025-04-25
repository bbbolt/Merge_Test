import requests

def query_service(query):
    """
    向 Tornado 服务发送查询请求并获取结果。
    
    :param query: 用户输入的查询字符串
    :param topk: 返回的 top-k 结果数量
    :param topp: 相似度阈值
    :return: 查询结果
    """
    url = "http://localhost:8100/intension_mcp_request"
    headers = {"Content-Type": "application/json"}
    data = {
        "session_id": "abc123",
        "request_id": "abc123",
        "query": query
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
    query = "WPS日活跃用户数"
    # tools = ["retriever_business_info", "custom_chat_llm", "cal_cirlcle_area", "multiply", "add"]

    # 调用服务
    # results = query_service(query, tools)
    results = query_service(query)


    # 打印结果
    if results:
        print("Query Results:")
        print(results)