'''
-*- coding: utf-8 -*-
@File  : llm_filter_label.py
@author: Maoyanyu
@Time  : 2025/01/16 14:29
'''
from utils.filter_label_utils.gen_filter_prompt import distill_sample_item as gen_filter_prompt
from utils.filter_label_utils.llm_judge import get_conclusion
from utils.filter_label_utils.update_xlsx import UpdateSheet as updateSheet


def llm_filter(orig_xlsx_path, judge_model_type):
    filter_prompt = gen_filter_prompt(orig_xlsx_path)
    conclusion = get_conclusion(filter_prompt, judge_model_type)
    updateSheet(orig_xlsx_path, conclusion, orig_xlsx_path).run()


if __name__ == "__main__":
    data_path = r"C:\Users\Bolt\PycharmProjects\et-code-eval\gen_sheets\JS_train_1121_13c_new_5\run_code_result\JS_train_1121_13c_new_5.xlsx"
    llm_filter(data_path, "Qwen")

