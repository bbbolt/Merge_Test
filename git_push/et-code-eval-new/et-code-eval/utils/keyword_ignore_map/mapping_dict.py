'''
-*- coding: utf-8 -*-
@File  : mapping_dict.py
@author: Maoyanyu
@Time  : 2024/12/25 18:18
'''
STYLE = {
}

VALUE = {"_x001D_": "_x001d_"}
WRAPTEXT = {True: None}

SKIP_SHEET_ATTR = ['parent', '_parent', "values", "rows", "columns", "ws", "activeCell", "sqref", "selected_cell","active_cell","start_cell","_cells","protection","topLeftCell","column_groups","sheet_properties", "_charts", "anchor", "merged_cell_ranges", "style_id", "style","destinations", "cells", "s", "freeze_panes", "max_priority","tabSelected","_StyleProxy__target", 'cache', "cols", "zoomScaleNormal", "zoomScale", "ranges", "customHeight", "ht", "_value", "internal_value"]
SKIP_CELL_ATTR = ['parent', "style_id", "has_style", "_style","_parent","_StyleProxy__target", "_value", "internal_value"]
