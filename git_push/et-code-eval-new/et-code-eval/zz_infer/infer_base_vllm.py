import argparse
from utils import *


def infer_base_vllm_func(args):
    model_path, local_eval_data_path, infer_result_save_path, BASE_URL, data_mapping_dict = args.model_path, args.local_data_path, args.infer_result_save_path, args.base_url, args.data_mapping_dict
    time_infer = get_infer_result(model_path, local_eval_data_path, infer_result_save_path, BASE_URL, data_mapping_dict)

    print(f"总耗时: {time_infer}s | 模型生成样张: {time_infer}s")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--model_path', type=str, help='model_path', default='/home/kas/kas_workspace/open_source_llm/Qwen2.5-3B-Instruct')
    parser.add_argument('--base_url', type=str, help='server_URL', default='http://127.0.0.1:8005')
    parser.add_argument('--local_data_path', type=str, help='json_data_path', default=r"C:\Users\Bolt\PycharmProjects\TelunXuptTry\et-code-eval\gen_sheets\val_all_2k\run_code_result\val_all_2k_test_eval.json")
    parser.add_argument('--infer_result_save_path', type=str, help='infer_result_save_path', default=r"C:\Users\Bolt\PycharmProjects\et-code-eval\case\data0906-0815cot-prompt-clean_result.json")
    parser.add_argument('--data_mapping_dict', type=str, help='data_mapping_dict', default='{"input": "prompt", "target": "answer"}')

    parser.add_argument('--number_worker', type=int, help='number_worker', default=16)
    args = parser.parse_args()

    infer_base_vllm_func(args)

