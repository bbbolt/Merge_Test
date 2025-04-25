import argparse
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from tools.apply_code import runCode as apply_code_func
from utils import *


def main(args):
    # 检查输入文件类型，xlsx需要转化成json文件，默认对应关系为{"input":"表格描述","target":"代码"}，如需变更可在check_xlsx中修改映射值
    if args.input_data_path.endswith("xlsx"):
        args.input_data_path = check_xlsx(args)

    ## 判断是否有md5标识，并添加
    check_md5(args.input_data_path, eval(args.data_mapping_dict))

    # 读取 YAML 文件
    gen_configs = load_yaml(r".\configs\config_run_code.yaml")

    if not os.path.exists(".\gen_sheets"): os.makedirs(".\gen_sheets")
    cur_file_name = os.path.basename(args.input_data_path).split(".json")[0]
    sheets_output_path = os.path.join(r".\gen_sheets", cur_file_name, "cases")

    # # 生成样张数据
    time_gen_sheets = gen_sheets(args.input_data_path, sheets_output_path, args.base_url, args.data_mapping_dict)

    # 生成配置文件（为了适配原先的接口）
    new_config_file = gen_config_file(gen_configs, sheets_output_path, args.input_data_path, args.client_path)

    # 代码执行生成执行样张
    apply = apply_code_func(config_path=new_config_file, data_mapping_dict=eval(args.data_mapping_dict), mode=args.mode)
    xlsx_path, time_apply_code = apply.run_all(worker_number=args.number_worker)

    # 调用大模型生成数据结论
    time_gen_conclusion = gen_conclusion(xlsx_path, args.base_url)
    xlsx_path   = r"C:\Users\Bolt\PycharmProjects\TelunXuptTry\et-code-eval\gen_sheets\jsapi0225_n7w_l5k\run_code_result\jsapi0225_n7w_l5k.xlsx"

    if args.gen_dataset:
        conclusion_path, gen_trainset_path, gen_evalset_path = xlsx_path.replace(".xlsx", "_conclusion.xlsx"), xlsx_path.replace(".xlsx", "_train.json"), xlsx_path.replace(".xlsx", "_eval.json")
        # 生成训练集和验证集
        conclusion2json(conclusion_path, gen_trainset_path, gen_evalset_path, args)
        # 上传训练集到kas服务端（或者自己手动传输也可以）
        # upload_train_data(gen_trainset_path, args.base_url)

    time_total = time_gen_sheets+time_apply_code+time_gen_conclusion
    print(f"总耗时: {time_total}s | 模型生成样张: {time_gen_sheets}s | 代码执行: {time_apply_code}s | 模型生成结论: {time_gen_conclusion}s")


if __name__=="__main__":
    ### 注意xlsx默认对应关系为{"input":"表格描述","target":"代码"} ###
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--client_path', type=str, help='client_path', default=r'C:\Users\Bolt\Downloads\office6\office6')
    parser.add_argument('--base_url', type=str, help='server_URL', default='http://127.0.0.1:8005')
    parser.add_argument('--input_data_path', type=str, help='datapath, json|xlsx', default=r"C:\Users\Bolt\Downloads\jsapi0225_n7w_l5k.json")
    parser.add_argument('--number_worker', type=int, help='number_worker', default=16)
    parser.add_argument('--xlsx_map_dict', type=str, help='xlsx_map_dict', default='{"input": "表格描述", "target": "代码"}')
    parser.add_argument('--data_mapping_dict', type=str, help='data_mapping_dict', default='{"input": "input", "target": "target", "md5":"md5"}')

    # 配置生成数据，且格式是不是采用r1形式（前提是原数据code本身就是r1格式）
    parser.add_argument('--gen_dataset', type=bool, help='gen_dataset', default=True)
    parser.add_argument('--mode', type=str, help='mode, (default|r1)', default="r1")
    args = parser.parse_args()

    main(args)

