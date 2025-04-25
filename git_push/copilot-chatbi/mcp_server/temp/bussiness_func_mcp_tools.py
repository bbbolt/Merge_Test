from mcp.server.fastmcp import FastMCP
import requests
from typing import List, Dict, Any

mcp = FastMCP("Bussiness")

# mcp同时也有 resource 和 prompt资源供agent调用 
# 我们应该也加入一个 不使用工具的 tool函数 然后拼接一个prompt 直接得出结果 这个是比较初级的想法 甚至可能已经包含在openai实现的 stop方法中了 

# 另外 目前没有相关的接口参数文档 未来接口都是通过metrics/query接口实现 

def execute_api(func_name, *args, **kwargs):
    # 包装执行函数
    # 不作为mcp tools
    # return API_CLASS[func_name](*args, **kwargs)

    url = 'http://semantic.demo.can.aloudata.com/semantic/api/v1.1/metrics/query'
    headers = {
        'tenant-id': 'tn_27436',
        'auth-type': 'UID',
        'auth-value': '564782443979083776'

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
        # "limit": 10,
        # "queryResultType":"SQL_AND_DATA",
        # "offset": 1,
        # "orders": [
        # ]
    }

    for k, v in kwargs.items():
        data[k] = v

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("请求成功，响应内容如下：")
        print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误发生: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求发生错误: {req_err}")

    return {"data": {}, "success": False, "code": None, "message": None, "traceId": ""}


@mcp.tool()
def flOrderCount(dimensions: str="", filters: List[str]=[], timeConstraint: str="", limit: int=10, offset:int=1, orders: List[Dict[str, Any]]=""):
    """
    订单量查询接口，可以查询的维度可以是日/月/年，可以添加一些筛选条件如产品ID，时间范围，返回结果数量等
    其中各参数说明如下：
    ·dimensions可的示例数据: [metric_time__day, metric_time__day, metric_time__day] 对应 日/月/年 
    ·filter的示例数据: "IN(['dim_product_id'], 22, 27, 19)" 其中dim_product_id字段代表产品ID 所以这个filter条件代表筛选产品 ID 为 22、27、19的数据
    ·timeConstraint的示例数据: "(['metric_time'] >= DATEADD(DateTrunc(NOW(), \"DAY\"), -(365), \"DAY\")) AND (['metric_time'] < DATEADD(DateTrunc(NOW(), \"DAY\"), 1, \"DAY\"))", 可以看到他是一段对应了过去一年内的每天的sql语句，通过计算当前日期的前365天到前1天来限制查询的数据的时间范围
    ·limit是返回结果的数量限制，一般默认10
    ·offset是返回的数据游标，常用于分页查询，代表了跳过查询结果的多少条后再开始返回
    ·orders的示例数据: [{"metric_time__day": "asc"}]， 代表了对以metric_time__day字段为key，按照正序排序并返回所有整行的结果
    """

    func_name = "flOrderCount"

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

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def cal_cirlcle_area(a: int) -> int:
    """提供半径计算圆形计算面积"""
    return 3.1415926*a*a


if __name__ == "__main__":
    mcp.run(transport="stdio")