import openpyxl
import json
import re
from openpyxl.worksheet.views import Selection
import argparse
from tqdm import tqdm
import os
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


class UpdateSheet:
    def __init__(self, original_sheet_path, conclusion_data, save_sheet_path):
        self.save_sheet_path = save_sheet_path
        self.conclusion_data = conclusion_data
        self.original_sheet_path = original_sheet_path

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

    def update_sheet_with_json(self, original_sheet_path, json_data, save_path):
        # 打开现有的 Excel 文件
        workbook = openpyxl.load_workbook(original_sheet_path)
        sheet = workbook.active

        # 创建一个字典，用于快速查找 md5 对应的 code_flag
        md5_to_code_flag = {item['md5']: item['code_flag'] for item in json_data}

        # 确定新列的位置
        new_column_index = sheet.max_column + 1

        # 在第一行添加列标题
        # 定义字体和填充颜色
        font = Font(name='微软雅黑', size=10, bold=True)
        fill = PatternFill(start_color='D8E4BC', end_color='D8E4BC', fill_type='solid')
        
        head1 = sheet.cell(row=1, column=new_column_index, value='模型初步裁决')
        head2 = sheet.cell(row=1, column=new_column_index+1, value='解释')

        head1.font = font
        head2.font = font
        head1.fill = fill
        head2.fill = fill
        head1.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        head2.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)


        sheet.column_dimensions[get_column_letter(new_column_index)].width = 20
        sheet.column_dimensions[get_column_letter(new_column_index+1)].width = 20

        # 遍历表格的行，匹配 md5 并填充 code_flag
        for row in range(2, sheet.max_row + 1):
            md5_value = sheet.cell(row=row, column=1).value
            if md5_value in md5_to_code_flag:
                info = md5_to_code_flag[md5_value]
                code_flag = re.findall(r'"FLAG":\s*(true|false|null|True|False)', info)[0]
                code_flag = self.convert_string_to_bool(code_flag)
                cell1 = sheet.cell(row=row, column=new_column_index, value=code_flag)
                cell2 = sheet.cell(row=row, column=new_column_index+1, value=md5_to_code_flag[md5_value])
                cell1.alignment = Alignment(wrap_text=True)
                cell1.font = Font(name='微软雅黑', size=10)  # 设置字体样式
                cell2.alignment = Alignment(wrap_text=True)
                cell2.font = Font(name='微软雅黑', size=10)  # 设置字体样式


        # 保存修改后的文件
        workbook.save(save_path)


    def convert_string_to_bool(self, value):
        if value in ["true", "True"]:
            return True
        elif value in ["false", "False"]:
            return False
        elif value == "null":
            return "NULL"
        else:
            raise ValueError(f"Cannot convert {value} to bool")

    def run(self):
        self.check_path_and_create(self.save_sheet_path)
        self.update_sheet_with_json(self.original_sheet_path, self.conclusion_data, f"{os.path.dirname(self.save_sheet_path)}\\updated_sheet.xlsx")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gen sheet')
    parser.add_argument('--save_sheet_path', type=str, help='save_sheet_path', default="/home/kas/x_gen_code_sheet/filter_label_code/final_update_sheet")
    parser.add_argument('--conclusion_data', type=str, help='conclusion_data')
    parser.add_argument('--original_sheet_path', type=str, help='original_sheet_path', default="/home/kas/x_gen_code_sheet/filter_label_code/input_xlsx/测评_241225_code.xlsx")
    args = parser.parse_args()
    tosheet = UpdateSheet(args.original_sheet_path, args.conclusion_data, args.save_sheet_path)
    tosheet.run()
