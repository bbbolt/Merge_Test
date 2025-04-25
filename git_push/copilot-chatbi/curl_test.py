import requests

url = 'http://semantic.demo.can.aloudata.com/semantic/api/v1.1/metrics/query'
headers = {
    'tenant-id': 'tn_27436',
    'auth-type': 'UID',
    'auth-value': '564782443979083776'

}
data = {
    "metrics": [
        ""
    ],
    "dimensions": [
        ""
    ],
    "timeConstraint": "(DateTrunc(['metric_time'], \"MONTH\")= DateTrunc(Today(),\"MONTH\"))",
    "filters": [],
    "limit": 30,
    "offset": 1
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