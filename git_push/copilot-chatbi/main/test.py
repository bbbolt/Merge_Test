import unittest
import requests
import os
import pandas as pd


<<<<<<< HEAD:test.py
"""
curl -X POST "http://kmd-api.kas.wps.cn/api/11281/KFgbo4/query/" \
-H "Content-Type: application/json" \
-d '{"messages": [{"role": "user","type": "file","content": "支出汇总.xlsx" },{"role": "user","type":"description", "content":""},{"role": "user","type": "text","content": "你是谁"}]}'
"""

BASE_URL = "http://kmd-api.kas.wps.cn/api/11281/KFgbo4/query"
# TEST_FILE_PATH = "/Users/cerax/Downloads/copilot-chatbi/output.xlsx"

# def create_test_excel():
#     # """创建一个简单的 Excel 测试文件"""
#     # import pandas as pd
#     # df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
#     # df.to_excel(TEST_FILE_PATH, index=False)
#     pass

# class TestAPIServer(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         create_test_excel()
=======
BASE_URL = "http://localhost:8000"
TEST_FILE_PATH = "/home/kas/cqx/llama_ft/data_analysis/11.xlsx"

def create_test_excel():
    """创建一个简单的 Excel 测试文件"""
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    df.to_excel(TEST_FILE_PATH, index=False)
    pass

class TestAPIServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        create_test_excel()
    
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)
>>>>>>> 576cb4d26093eae3a9067282ad5e084a2cc7e90e:main/test.py
    
#     @classmethod
#     def tearDownClass(cls):
#         if os.path.exists(TEST_FILE_PATH):
#             os.remove(TEST_FILE_PATH)
    
#     def test_upload_file(self):
#         """测试上传接口"""
#         with open(TEST_FILE_PATH, "rb") as f:
#             files = {"file": (TEST_FILE_PATH, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
#             response = requests.post(f"{BASE_URL}/upload/", files=files)
#         print("response: ", response.text)
#         self.assertEqual(response.status_code, 200)
#         json_data = response.json()
#         self.assertIn("file_uuid", json_data)
#         self.assertIn("filename", json_data)
        
#         self.file_uuid = json_data["file_uuid"]
#         self.filename = json_data["filename"]

BASE_URL = "http://127.0.0.1:8000"
import requests
import json
def test_query_file():
    """测试查询接口"""
    # self.test_upload_file()  # 确保上传成功
    query_data = {"messages": [{"role": "user","type": "file","content": "支出汇总.xlsx" },{"role": "user","type":"description", "content":""},{"role": "user","type": "text","content": "帮我写个冒泡排序的代码"},{"role": "assistant","type": "code","content": "\n\n\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr\n\n# 测试示例\nunsorted_list = [64, 34, 25, 12, 22, 11, 90]\nsorted_list = bubble_sort(unsorted_list.copy())\nprint(sorted_list) "},{"role": "assistant","type": "execution","content": "[11,12,22,25,34,64,90]"}]}
    query_data = json.dumps(query_data, ensure_ascii=False)

    response = requests.post(f"{BASE_URL}/query", data=query_data)
    print(response.text)
    # self.assertEqual(response.status_code, 200)
    json_data = response.json()
    # self.assertIn("response", json_data)
    print("Query Response:", json_data)

if __name__ == "__main__":
    test_query_file()