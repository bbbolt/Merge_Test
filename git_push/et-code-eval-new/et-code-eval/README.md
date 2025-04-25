# 基于openpyxl及LLM的JSAPI校验工具
- 分为本地和服务端，整体思路：
- ![Snipaste_2025-02-18_14-25-52.png](img_src%2FSnipaste_2025-02-18_14-25-52.png)

### 数据评测pipeline
```commandline
### 先在远端启动服务（必须）###
python /home/kas/kas_workspace/maoyanyu/et_code_eval/start_server.py

### 再在本地执行zz_check_data/check_code_and_gen_trainset_llm.py ###
# json和xlsx文件为这次需要评测的数据，只需要填写一种即可 #
# 注意数据格式为{"input": 表格描述} #
python zz_check_data/check_code_and_gen_trainset_llm.py --client_path <内核工具路径> --input_data_path <json|xlsx数据文件> --xlsx_map_dict <默认值为{"input":"表格描述","target":"代码"}> --base_url <服务端的接口地址> --number_worker 16 --data_mapping_dict {"input": "input", "target": "target", "md5":"md5"} --gen_dataset <是否生成对应训练测试集，True|False> --mode <数据格式是否采用r1，default|r1>
```

# 模型推理pipeline
### 仅推理！
```commandline
### 先在远端启动服务（必须）###
python /home/kas/kas_workspace/maoyanyu/et_code_eval/start_server.py

### 再在本地执行zz_infer\infer_base_vllm.py ###
# json和xlsx文件为这次需要评测的数据，只需要填写一种即可 #
python zz_infer/infer_base_vllm.py --model_path <kas模型路径> --local_data_path <本地评测集数据路径> --base_url <服务端的接口地址> --number_worker 16 --data_mapping_dict {"input": "prompt", "target": "answer"} --infer_result_save_path <推理结果存放路径>
```

### 推理+评测！
- 对于使用zz_check_data生成的训练集和测试集，可使用zz_validation/custom_eval_compare.py评测
```commandline
### 先在远端启动服务（必须）###
python /home/kas/kas_workspace/maoyanyu/et_code_eval/start_server.py

### 再在本地执行zz_validation/custom_eval_compare.py ###
python zz_validation/custom_eval_compare.py --base_url <服务端的接口地址> --client_path <内核工具路径> --kas_checkpoint_path <kas上的模型路径> --src_path <使用check_code_and_gen_trainset_llm.py生成的数据根目录（因为需要用到模型生成的样张）> --data_mapping_dict {"input": "prompt", "target": "answer", "md5": "md5"}
```
- 对于2k评测集，可直接使用zz_validation/data2k_compare.py评测
```commandline
### 先在远端启动服务（必须）###
python /home/kas/kas_workspace/maoyanyu/et_code_eval/start_server.py

### 再在本地执行zz_validation/custom_eval_compare.py ###
python zz_validation/custom_eval_compare.py --base_url <服务端的接口地址> --client_path <内核工具路径> --excel_file_path <excel映射文件路径> --kas_checkpoint_path <kas上的模型路径> --device_default_change <第一次执行需要跑一下，True|False> --data_mapping_dict {"input": "prompt", "target": "answer"}
```
