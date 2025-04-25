import argparse
import re
from utils.sheet_compare import DeepSearch as DeepSearchSheet
import os

class DeepSearchV2(DeepSearchSheet):
    def __init__(self):
        super().__init__(strict=True)

    def run_compare(self, excel_file1, excel_file2, code_dict):
        basename = os.path.basename(excel_file1.split(".xlsx")[0])
        try:
            all_attributes1, cellsList1, sheet_name = self.excel_to_attribution_dict(excel_file1)
            all_attributes2, cellsList2, _ = self.excel_to_attribution_dict(excel_file2, sheet_name)
        except TypeError as typeerror:
            return ([f"校验样张解析错误 (超长 | openpyxl读取失败) :{typeerror}"], [])
        except KeyError as keyerror:
            return ([f"校验样张解析错误:{keyerror}"], [])

        diff_ws = self.compare_dict(all_attributes1, all_attributes2, "AutoFit")

        diff_cells = self.dsc.run_compare_cells(cellsList1, cellsList2, basename)

        return (diff_ws, diff_cells)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("校验工具配置")
    parser.add_argument("--file1", type=str, help="Add your case1 path", default=r"C:\Users\Bolt\Downloads\工资表自动计算个税和税后工资-执行_原始样张..xlsx")
    parser.add_argument("--file2", type=str, help="Add your case2 path", default=r"C:\Users\Bolt\Downloads\工资表自动计算个税和税后工资-执行_校验样张..xlsx")
    args = parser.parse_args()

    ds = DeepSearchV2()

    res = ds.run_compare(args.file1, args.file2, None)

    print("表格属性差异：")
    for item in res[0]:
        if item:   print("\t", item)
    print("单元格属性差异：")
    for item in res[1]:
        if item:   print("\t", item)