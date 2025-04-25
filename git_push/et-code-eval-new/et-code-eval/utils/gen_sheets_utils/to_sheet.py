import openpyxl
import json
import re
from openpyxl.worksheet.views import Selection
import argparse
from tqdm import tqdm
import os


class ToSheet:
    def __init__(self, save_sheet_path):
        self.save_sheet_path = save_sheet_path

    def check_path_and_create(self, dst_dir):
        # 如果目标目录不存在，则创建目标目录
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

    def is_float(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False



    def generate_dataframe(self, prompt, description, save_path):
        # 初始化一个空的字典来存储列数据
        data = description
        
        try:
            # 定义内容起始行和终止行
            head_start, head_end, start_row, end_row = re.findall(r"表头起始行号为(\d+)，终止行号为(\d+)，内容起始行号为(\d+).*?终止行号为(\d+)", prompt, re.DOTALL)[0]
            head_start, head_end, start_row, end_row = int(head_start), int(head_end), int(start_row), int(end_row)
            all_sheets, cur_sheet = re.findall(r"所有工作表的名称如下：(.*?)，当前工作表名称为：(.*?)，选中区域", prompt, re.DOTALL)[0]
            cur_sheet = cur_sheet.strip("\"' ")
        except:
            head_start, head_end, start_row, end_row = 1,1,2,20
            all_sheets, cur_sheet = re.findall(r"所有工作表的名称如下：(.*?)，当前工作表名称为：(.*?)，选中区域", prompt, re.DOTALL)[0]
            cur_sheet = cur_sheet.strip("\"' ")
        
        selRange, activeCell = re.findall(r'选中区域为："(.*?)"，活动单元格为：(.*?)。', prompt, re.DOTALL)[0]


        # 创建一个新的工作簿
        wb = openpyxl.Workbook()
        # 新增表单
        for i in eval(all_sheets.replace("\"，\"", "\",\"")):

            wb.create_sheet(title=i.strip())
        # 获取默认的工作表
        try:
            ws = wb[cur_sheet]
        except:
            return

        # 
        
        # 填充数据
        for item in data:
            col = item[0]
            col_index = openpyxl.utils.column_index_from_string(re.findall(r"[A-Za-z]+", col)[0])
            ws.cell(row=head_start, column=col_index, value=item[1])  # 填充标题

            items=[float(i) if self.is_float(i) else int(i) if self.is_int(i) else i for i in item[2]]
            for row_index, value in enumerate(items):
                ws.cell(row=row_index+start_row, column=col_index, value=value)


        # 保存工作簿
        # 创建一个 Selection 对象
        # 设置默认工作表
        wb.active = ws  # 设置 Sheet2 为默认工作表
        selection = Selection()
        selection.sqref = selRange
        # selection.pane = "bottomRight"
        selection.activeCell = activeCell

        # 将 Selection 对象添加到工作表视图
        ws.views.sheetView[0].selection = [selection]
        wb.save(save_path)


    def run(self, all_sheet_list):
        self.check_path_and_create(self.save_sheet_path)
        for sheet_list in tqdm(all_sheet_list, desc="表格样例值描述转化表格"):
            # 示例数据描述
            description = sheet_list    

            # 将DataFrame保存为Excel文件
            filename=sheet_list["md5"]
            # 生成DataFrame
            self.generate_dataframe(list(description.keys())[0],list(description.values())[0], f"{self.save_sheet_path}/{filename}.xlsx")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--save_sheet_path', type=str, help='save_sheet_path', default="/home/kas/x_gen_code_sheet/gen_sheet_final/2024-12-25_gen_sheet_Qwen2.5-3B-Instruct")
    args = parser.parse_args()
    tosheet = ToSheet(args)

