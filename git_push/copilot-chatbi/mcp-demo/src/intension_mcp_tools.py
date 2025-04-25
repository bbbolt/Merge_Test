from mcp.server.fastmcp import FastMCP
from model import openai_client
from const.env import MCP_API_MODEL_NAME, RETRIEVER_URL
import requests
from typing import List, Dict, Any
import json
from typing import Literal
from enum import Enum
mcp = FastMCP("Intension")
from handler import get_query_from_response


def execute_api(func_name, *args, **kwargs):
    # 包装执行函数
    # 不作为mcp tools
    # return API_CLASS[func_name](*args, **kwargs)

    # url = 'http://semantic.demo.can.aloudata.com/semantic/api/v1.1/metrics/query'
    # headers = {
    #     'tenant-id': 'tn_27436',
    #     'auth-type': 'UID',
    #     'auth-value': '564782443979083776'
    # }

    url = 'http://10.7.148.54:8085/semantic/api/v1.1/metrics/query'
    headers = {
        'tenant-id': 'tn_31',
        'auth-type': 'UID',
        'auth-value': '562938154093379584'
    }

    data = {
        "metrics": [
            func_name
        ],
        # "dimensions": [
        #     "order_amt",
        #     "user_id"
        # ],
        # "filters": [],
        "limit": 10,
        "queryResultType":"SQL_AND_DATA",
        "offset": 1,
        # "orders": [
        # ]
    }

    for k, v in kwargs.items():
        data[k] = v

    try:
        # response = requests.post(url, headers=headers, json=data)
        # response.raise_for_status()
        # print("请求成功，响应内容如下：")
        # print(response.json())

        # 处理成同样的格式
        # res = response.json()

        # 模拟
        res = {'data': {'queryId': 'b3f0bad544d644f387d07a93a5d9bf06', 'warning': None, 'sql': 'SELECT CASE WHEN COUNT(DISTINCT `tn_31_starrocks__default__delper_click`.`_account_id`) = CAST(0 AS BIGINT) THEN NULL ELSE COALESCE(COUNT(`tn_31_starrocks__default__delper_click`.`_account_id`), 0) / COUNT(DISTINCT `tn_31_starrocks__default__delper_click`.`_account_id`) END AS `delper_per_click_uv`\nFROM `default_catalog`.`aloudatacan`.`tn_31_starrocks__default__delper_click` AS `tn_31_starrocks__default__delper_click`\nLIMIT 10', 'table': {'columns': {'delper_per_click_uv': [{'value': 186.59823008849557, 'flag': None, 'count': 1}]}}, 'metas': [{'id': None, 'uuid': None, 'name': 'delper_per_click_uv', 'dataType': None, 'dataTypeName': 'DOUBLE', 'displaySize': None, 'schemaName': None, 'scale': None, 'precision': None, 'tableName': None, 'type': None}], 'hitMvType': 'NOT_REWRITE', 'containsErrorColumn': False}, 'success': True, 'code': '200', 'message': None, 'traceId': '3eabc850-825c-4df8-8f66-6aaf9a60e1bd'}

        if res.get("code") != "200":
            return {"data": {}, "code": 0, "type": "execution"}
        else:
            return {"data": res["data"], "code": 0, "type": "execution"}
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误发生: {http_err}")
        return {"data": {}, "code": -1004, "type": "execution"}
    except requests.exceptions.RequestException as req_err:
        print(f"请求发生错误: {req_err}")
        return {"data": {}, "code": -1005, "type": "execution"}
    except Exception as e:
        print(f"请求发生错误: {e}")
        return {"data": {}, "code": -1006, "type": "execution"}


@mcp.tool()
def api_execution_after_user_select(func_name: str="", dimensions: str="", filters=None, timeConstraint: str="", limit: int=10, offset:int=1, orders: List[Dict[str, Any]]=""):
    """
    指标查询接口，用户选择完指标后，通过func_name访问定义好的api接口，需要给出对应的查询数据
    其中各参数说明如下：
    ·func_name：已经开发完成的api接口名称
    ·dimensions可的示例数据: [metric_time__day, metric_time__month, metric_time__year] 对应 日/月/年 
    ·filter的示例数据: "IN(['dim_product_id'], 22, 27, 19)" 其中dim_product_id字段代表产品ID 所以这个filter条件代表筛选产品 ID 为 22、27、19的数据
    ·timeConstraint的示例数据: "(['metric_time'] >= DATEADD(DateTrunc(NOW(), \"DAY\"), -(365), \"DAY\")) AND (['metric_time'] < DATEADD(DateTrunc(NOW(), \"DAY\"), 1, \"DAY\"))", 可以看到他是一段对应了过去一年内的每天的sql语句，通过计算当前日期的前365天到前1天来限制查询的数据的时间范围
    ·limit是返回结果的数量限制，一般默认10
    ·offset是返回的数据游标，常用于分页查询，代表了跳过查询结果的多少条后再开始返回
    ·orders的示例数据: [{"metric_time__day": "asc"}]， 代表了对以metric_time__day字段为key，按照正序排序并返回所有整行的结果
    """

    # func_name = "flOrderCount"

    curl_data = {
        "dimensions": dimensions,
        "filters": filters, 
        "timeConstraint": timeConstraint,
        "limit": limit,
        "offset": offset,
        "orders": orders
    }

    response = execute_api(func_name, **curl_data)

    return response



# class Status(Enum):
#     ACTIVE = "metric_time__day"
#     INACTIVE = "metric_time__day"
#     PENDING = "metric_time__day"


# @mcp.tool()
# def flOrderCount(dimensions: Status, filters=None, timeConstraint: str="", limit: int=10, offset:int=1, orders: List[Dict[str, Any]]=""):
#     """-订单量查询接口，可以查询的维度可以是日/月/年，可以添加一些筛选条件如产品ID，时间范围，返回结果数量等
#     Args:
#         dimensions: 查询维度支持使用已经定义的维度支持对日期类型的维度进行快速粒度切换. 例如，metric_time__day, metric_time__day, metric_time__day 对应 日/月/年 
#         filter的示例数据: "IN(['dim_product_id'], 22, 27, 19)" 其中dim_product_id字段代表产品ID 所以这个filter条件代表筛选产品 ID 为 22、27、19的数据
#         ·timeConstraint的示例数据: "(['metric_time'] >= DATEADD(DateTrunc(NOW(), \"DAY\"), -(365), \"DAY\")) AND (['metric_time'] < DATEADD(DateTrunc(NOW(), \"DAY\"), 1, \"DAY\"))", 可以看到他是一段对应了过去一年内的每天的sql语句，通过计算当前日期的前365天到前1天来限制查询的数据的时间范围
#         ·limit是返回结果的数量限制，一般默认10
#         ·offset是返回的数据游标，常用于分页查询，代表了跳过查询结果的多少条后再开始返回
#         ·orders的示例数据: [{"metric_time__day": "asc"}]， 代表了对以metric_time__day字段为key，按照正序排序并返回所有整行的结果
#     """

#     func_name = "flOrderCount"

#     curl_data = {
#         "dimensions": dimensions,
#         "filters": filters, 
#         "timeConstraint": timeConstraint,
#         "limit": limit,
#         "offset": offset,
#         "orders": orders
#     }

#     response = execute_api(func_name, **curl_data)

#     return response


# @mcp.tool()
# def custom_chat_llm(query: str) -> str:
#     """当用户问题与企业信息不相关，不需要使用查询工具，只需要与用户正常交流"""
#     messages = [
#             {
#                 "role": "user",
#                 "content": query
#             }
#         ]
    
#     try:
#         response = openai_client.chat.completions.create(
#                         model=MCP_API_MODEL_NAME,  # Replace with the desired model
#                         messages=messages
#                     ).choices[0].message.content
#     except:
#         response = "OpenAI API调用错误"

#     return {"type": "chat", "data": response}

@mcp.tool()
def chat_summary_after_api_execution(messages: List) -> str:
    """当获取到指标执行结果后，请调用该函数进行总结并回答用户的问题，只需要总结与问题相关的内容，请不要输入其他不相关信息"""
    try:
        template = f"""请根据问题和指标执行结果{messages}，总结出用户想要的信息，并回答用户的问题。
"""
        response = openai_client.chat.completions.create(
                        model=MCP_API_MODEL_NAME,  # Replace with the desired model
                        messages=[{
                                "role": "user",
                                "content": template
                            }]
                    ).choices[0].message.content
    except:
        response = "OpenAI API调用错误"



    return {"type": "summary", "data": response}


# api检索函数
def intension_post(query):
    url = 'http://kmd-api.kas.wps.cn/api/11286-v1/nn3ihw/query'

    data = {"session_id": "test", 
            "request_id": "test", 
            "query": query}

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print("请求成功，响应内容如下：")
        print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误发生: {http_err}")
        return {"code": -1001, "data": []}
    except requests.exceptions.RequestException as req_err:
        print(f"请求发生错误: {req_err}")
        return {"code": -1002, "data": []}
    except Exception as e:
        print(f"请求发生错误: {e}")
        return {"code": -1003, "data": []}

# @mcp.tool()
def retriever_api_info_after_extracted_prob_index(query: str) -> list:
    """
    基于提取出的指标信息，使用查询工具查询对应指标信息接口
    """
    response = intension_post(query)
    return {"type": "api", "data": response["data"]}

@mcp.tool()
def extracted_prob_index_from_user_query(query: str) -> list:
    """
    从用户给定的问题中提取出问题中可能涉及到的指标信息，如果用户没有明确提出指标名称，则返回原问题
    """
    template = """帮我把用户问题中涉及到的指标名称提取出来。仅需要返回指标名称，请不要输出其他多余的内容。如果用户问题比较模糊，请返回原问题。
例如：
- 用户问题：我想知道WPS每天的收入是多少
- 指标名称：WPS每天的收入

- 用户问题：请帮我查一下WPS的第一次AI请求用户
- 指标名称：WPS第一次AI请求用户

- 用户问题：图片新增用户
- 指标名称：图片新增用户

- 用户问题：帮我统计下移动端打开设备数是多少
- 指标名称：移动端打开设备数


新的请求：
- 用户问题：{query}
- 指标名称："""
    try:
        response = openai_client.chat.completions.create(
                        model=MCP_API_MODEL_NAME,  # Replace with the desired model
                        messages=[{
                                "role": "user",
                                "content": template.format(query=query)
                            }]
                    ).choices[0].message.content
    except:
        response = "OpenAI API调用错误"

    retriever_query = get_query_from_response(response, query)
    retriever_result = intension_post(retriever_query)

    return {"type": "api", "data":{"retriever_query": retriever_query, "retriever_result": retriever_result}}


if __name__ == "__main__":
    mcp.run(transport="stdio")