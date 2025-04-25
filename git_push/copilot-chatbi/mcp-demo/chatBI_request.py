import requests

url = 'http://10.7.148.54:8085/semantic/api/v1.1/metrics/query'
headers = {
    'tenant-id': 'tn_31',
    'auth-type': 'UID',
    'auth-value': '562938154093379584'
}

data = {
    "metrics": [
        "delper_per_click_uv"
    ],
    "dimensions": [
        "",
    ],
    "filters": [],
    "limit": 10,
    "queryResultType":"SQL_AND_DATA",
    "offset": 1,
    "orders": [
    ]
}
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print("请求成功，响应内容如下：")
    print(response.json())
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP 错误发生: {http_err}")
except requests.exceptions.RequestException as req_err:
    print(f"请求发生错误: {req_err}")
