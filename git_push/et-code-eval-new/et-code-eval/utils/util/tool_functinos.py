from .disaggregation.functions import FUNCTIONS as FUNCTIONS_DISAGGREGATION
from .pvt.functions import FUNCTIONS as FUNCTIONS_PVT
from .pvt.functions import CONTEXT_CODE as CONTEXT_CODE_PVT
from .sort.functions import FUNCTIONS as FUNCTIONS_SORT
from .hyperlink.functions import FUNCTIONS as FUNCTIONS_HYPERLINK
from .range_ops.functions import FUNCTIONS as FUNCTIONS_RANGE_OPS
from .range_ops.functions import CONTEXT_CODE as CONTEXT_CODE_RANGE_OPS
from .merge.functions import FUNCTIONS as FUNCTIONS_MERGE
from .multi_sheet.functions import MULTI_SHEET_FUNCTIONS
from .dataseries.functions import FUNCTIONS as FUNCTIONS_DATASERIES

from .dataseries.functions import DATASERIES_DATA_MAPS as DATASERIES_MAPS
from .disaggregation.functions import DISAGGREGATION_MAPS as DISAGGREGATION_MAPS
from .pvt.functions import PVT_DATA_MAPS as PVT_MAPS
from .hyperlink.functions import HYBERLINK_MAPS as HYBERLINK_MAPS
from .sort.functions import SORT_MAPS as SORT_MAPS
from .merge.functions import MERGE_MAPS as MERGE_MAPS
from .multi_sheet.functions import MULTI_SHEET_MAP as MULTI_SHEET_MAPS
from .range_ops.functions import RANGE_OPS_DATA_MAPS as RANGE_OPS_MAPS
# import log

import re

class ToolFunctions():
    def __init__(self, ):
        self.ALL_FUNCTION_ACHIEVE = [FUNCTIONS_DISAGGREGATION, FUNCTIONS_DATASERIES, FUNCTIONS_HYPERLINK, FUNCTIONS_MERGE, FUNCTIONS_RANGE_OPS, FUNCTIONS_SORT, FUNCTIONS_PVT]
        self.index_init()
        
    def index_init(self,):
        self.all_key_lst = []
        self.all_achieve_dict = {}
        self.result_dict = {}
        self.white_lst = ['IsCellAddress', 'GetActiveRange', 'findRangeByContent', 'GetTableRangeFromKey']
        for first_instruction in self.ALL_FUNCTION_ACHIEVE:
            for func_name in first_instruction:    
                self.all_key_lst.append(func_name)
                self.all_achieve_dict[func_name] = first_instruction[func_name]
                
        # 检查是否有重名函数
        if len(self.all_key_lst) - len(set(self.all_key_lst)) > len(self.white_lst):
            duplicate_lst = list(set([item for item in self.all_key_lst if self.all_key_lst.count(item) > 1 and item not in self.white_lst]))
            # log.app_logger.warning("存在重复函数定义", str(duplicate_lst))
                
        self.index_dict = {}
        for item in self.all_key_lst:
            for key in self.all_key_lst:
                if self.is_substring_in_string(key, self.all_achieve_dict[item]):
                    self.index_dict.setdefault(item, []) 
                    self.index_dict[item].append(key)
        self.function_name_call_dict = {}
        for func_name in self.all_key_lst:
            self.function_name_call_dict[func_name] = self.get_all_functions(func_name)
            
    def is_substring_in_string(self, substring, string):
    # 确保前后不是字母和.
        pattern = r'(?<!\w)(?<!\.)' + re.escape(substring) + r'(?!\w)'
        
        # 搜索子串
        if re.search(pattern, string):
            return True
        else:
            return False
        
    def get_all_functions(self, key):
        # 递归体，用来递归查找所有使用到的函数名
        if len(self.index_dict[key]) == 1:
            return [key]
        
        result_lst = [key]
        for item in self.index_dict[key]:
            if item != key:
                result_lst.extend(self.get_all_functions(item))
        return result_lst
        
    def add_functions(self, code, model_input):
        usedfunctions = []
        functions = {}
        
        # 先单独处理一下多表单的工具函数先
        if "GetMultiSheet" in code or 'MultiRange' in code:
            try:
                for function in MULTI_SHEET_FUNCTIONS:
                    if function in code:
                        functions[function] = MULTI_SHEET_FUNCTIONS[function](
                            MULTI_SHEET_FUNCTIONS["get_tables"](model_input), code)
            except:
                pass
        
        for func_name in self.all_key_lst:
            if self.is_substring_in_string(func_name, code):
                usedfunctions.extend(self.function_name_call_dict[func_name])
                
        usedfunctions = list(set(usedfunctions))
        if functions != {}:
            for key, value in functions.items():
                code += '\n' + value
        if usedfunctions != []:
            for key in usedfunctions:
                code += '\n' + self.all_achieve_dict[key]
        return code, None