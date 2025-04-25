'''
-*- coding: utf-8 -*-
@File  : gen_sheets.py
@author: Maoyanyu
@Time  : 2025/01/16 10:38
'''
import argparse

from utils.gen_sheets_utils.construct_prompt import distill_sample_item
from utils.gen_sheets_utils.get_sample_value import get_sheet_table
from utils.gen_sheets_utils.sample_value_postprocess import postprocess_func
from utils.gen_sheets_utils.to_sheet import ToSheet


def get_args():
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--data_path', type=str, help='data_path', default=r"C:\Users\Bolt\PycharmProjects\et-code-eval\case\JS_train_1121_13c_new_5.json")
    parser.add_argument('--output', type=str, help='output', default=r"C:\Users\Bolt\PycharmProjects\et-code-eval\gen_sheets")

    args = parser.parse_args()
    return args


def get_sheets(args):
    prompt = distill_sample_item(args.data_path)
    sample_value = get_sheet_table(prompt, args.gen_sheet_model_type)
    postprocess_sample_value = postprocess_func(sample_value)
    ToSheet(args.sheets_output_path).run(postprocess_sample_value)
    return args.sheets_output_path


if __name__=="__main__":
    args = get_args()
    get_sheets(args)