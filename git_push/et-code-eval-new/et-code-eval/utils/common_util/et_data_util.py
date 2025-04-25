import os
from collections import defaultdict

import openpyxl
import xlrd
from openpyxl.styles import PatternFill, Alignment, Font
from openpyxl.utils import get_column_letter

from utils.common_util.log_util import logger


class ETDataUtil:

    @staticmethod
    def get_et_sheet_data(file_path, sheet_name):
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        except:
            wb = xlrd.open_workbook(file_path)
        sheet = wb[sheet_name]
        rows = sheet.values
        header = next(rows)
        data = [dict(zip(header, row)) for row in rows]
        wb.close()
        return data

    @staticmethod
    def get_et_header(file_path, sheet_name):
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        except:
            wb = xlrd.open_workbook(file_path)
        sheet = wb[sheet_name]
        header = [cell.value for cell in sheet[1]]
        wb.close()
        return header

    @staticmethod
    def read_et_sheet_columns(file_path, sheet_name, columns=None):
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        except:
            wb = xlrd.open_workbook(file_path)
        sheet = wb[sheet_name]
        rows = sheet.values
        header = next(rows)
        if columns is None:
            data = [dict(zip(header, row)) for row in rows]
        else:
            if isinstance(columns, str):
                columns = [columns]
            indexes = [header.index(col) for col in columns]
            if len(indexes) == 1:
                data = [dict(zip([columns[0]], [row[indexes[0]]])) for row in rows]
            else:
                data = [dict(zip(columns, [row[i] for i in indexes])) for row in rows]
        wb.close()
        return data

    @staticmethod
    def insert_one_pic_to_xlsx(xlsx_path, sheet_name, image_path, row, column):
        """row、column从0开始，将单个图片插入到指定行指定列中"""
        from openpyxl import load_workbook
        from openpyxl.drawing.image import Image
        from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor

        wb = load_workbook(xlsx_path)
        ws = wb[sheet_name]

        img = Image(image_path)
        _from = AnchorMarker(column, 0, row, 0)
        to = AnchorMarker(column + 1, 0, row + 1, 0)
        img.anchor = TwoCellAnchor('twoCell', _from, to)

        ws.add_image(img)
        wb.save(xlsx_path)

    @staticmethod
    def insert_batch_pics_to_xlsx(xlsx_path, sheet_name, pic_dict_list, need_insert_path='截图路径',
                                  insert_column_name='截图效果', row_label='用例编号', clear_before_insert=False):
        """image_path_dict_list:{'pic_path':pic_path, 'row':row, 'column':column}"""
        """row、column从0开始，批量将图片插入到指定行指定列中"""
        from openpyxl import load_workbook
        from openpyxl.drawing.image import Image
        from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor

        wb = load_workbook(xlsx_path)
        ws = wb[sheet_name]
        for index, pic_dict in enumerate(pic_dict_list):
            pic_path = pic_dict.get(need_insert_path)
            try:
                if not os.path.exists(pic_path):
                    logger.warning(f"图片路径pic_path：【{pic_path}】不存在")
                else:
                    img = Image(pic_path)
                    column = list(pic_dict.keys()).index(insert_column_name)
                    row = index + 1
                    _from = AnchorMarker(column, 0, row, 0)
                    to = AnchorMarker(column + 1, 0, row + 1, 0)
                    img.anchor = TwoCellAnchor('twoCell', _from, to)
                    if clear_before_insert:
                        ws.cell(row=row + 1, column=column + 1).value = ""
                    ws.add_image(img)
            except Exception as e:
                logger.warning(f"插入图片{pic_path}失败,失败原因：{e}")

        wb.save(xlsx_path)

    @staticmethod
    def write_dict_list_to_excel(dict_list, save_path, sheet_name, header_fill=None, column_width=None,
                                 row_height=None):
        # 检查文件是否已存在，如果存在则打开该文件并在其中添加新的工作表，否则创建新的工作簿
        if os.path.exists(save_path):
            workbook = openpyxl.load_workbook(save_path)
            # 检查要写入的工作表是否已存在，如果存在则删除并重新创建
            if sheet_name in workbook.sheetnames:
                workbook.remove(workbook[sheet_name])

            sheet = workbook.create_sheet(sheet_name)
        else:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = sheet_name

        # 写入表头
        header = dict_list[0].keys()
        for col_num, col_name in enumerate(header, 1):
            cell = sheet.cell(row=1, column=col_num, value=col_name)
            cell.font = Font(name='微软雅黑', size=10, bold=True)  # 设置字体样式
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)  # 设置对齐方式

            # 设置表头颜色填充
            if header_fill:
                for fill_range, fill_color in header_fill.items():
                    start_col, end_col = [int(x) for x in fill_range.split('-')]
                    if start_col <= col_num <= end_col:
                        cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type='solid')
                        break

            # 设置列宽
            if column_width:
                try:
                    sheet.column_dimensions[get_column_letter(col_num)].width = column_width[col_num - 1]
                except Exception:
                    pass

        # 写入数据
        for row_num, row_data in enumerate(dict_list, 2):
            for col_num, col_name in enumerate(header, 1):
                try:
                    cell = sheet.cell(row=row_num, column=col_num, value=str(row_data[col_name]))
                except Exception as e:
                    cell = sheet.cell(row=row_num, column=col_num, value="写入数据失败")
                    logger.warning(f"写入数据失败，失败原因：{e}")
                cell.font = Font(name='微软雅黑', size=10)  # 设置字体样式
                cell.alignment = Alignment(wrap_text=True)  # 设置单元格内容自动换行

                # 设置行高
                if row_height:
                    sheet.row_dimensions[row_num].height = row_height

        # 保存文件
        workbook.save(save_path)

    @staticmethod
    def calculate_summary_data(dict_list, is_ratio_of_completed_scripts=False):
        summary_data = defaultdict(
            lambda: {"total_count": 0, "completed_scripts": 0, "matched_labels": 0, "passed_results": 0})

        for data in dict_list:
            label = data["标签校验"]
            summary_data[label]["total_count"] += 1
            if data["校验是否通过"] != "":
                summary_data[label]["completed_scripts"] += 1
            if data["标签对比是否正确"]:
                summary_data[label]["matched_labels"] += 1
            if data["校验是否通过"]:
                summary_data[label]["passed_results"] += 1

        summary_list = []
        for label, data in summary_data.items():
            if is_ratio_of_completed_scripts:
                ratio_of_completed_scripts = data["passed_results"] / data["completed_scripts"] if data["completed_scripts"] != 0 else 0
                summary_list.append({
                    "标签类型": label,
                    "类型总数": data["total_count"],
                    "完成校验结果数": data["completed_scripts"],
                    "标签匹配数": data["matched_labels"],
                    "标签匹配率": '{:.2%}'.format(data["matched_labels"] / data["total_count"]),
                    "校验结果通过数": data["passed_results"],
                    "校验结果通过率": '{:.2%}'.format(ratio_of_completed_scripts)
                })
            else:
                summary_list.append({
                    "标签类型": label,
                    "类型总数": data["total_count"],
                    "完成校验结果数": data["completed_scripts"],
                    "标签匹配数": data["matched_labels"],
                    "标签匹配率": '{:.2%}'.format(data["matched_labels"] / data["total_count"]),
                    "校验结果通过数": data["passed_results"],
                    "校验结果通过率": '{:.2%}'.format(data["passed_results"] / data["total_count"])
                })

        return summary_list

    @staticmethod
    def convert_xlsx_to_csv(xlsx_path, csv_path):
        """将xlsx文件转换为csv文件"""
        import pandas as pd
        data_xls = pd.read_excel(xlsx_path)
        data_xls.to_csv(csv_path)
