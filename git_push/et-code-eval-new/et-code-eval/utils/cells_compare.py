import time

import numpy as np
from tqdm import tqdm
from utils.keyword_ignore_map.mapping_dict import SKIP_CELL_ATTR


class DeepSearchCells:
    def __init__(self, skip_attr=SKIP_CELL_ATTR):
        self.SKIP_ATTR = skip_attr

    def get_all_attributes(self, obj):
        attributes = {}
        stack = [(obj, '')]

        while stack:
            current_obj, path = stack.pop()

            ### 判断list, tuple, set, dict都要逐个取出来重新放到队列，并记录该属性轨迹 ###
            ### 判断如果是值，直接记录路径并添加到属性 ###
            ### 既不是值也不是list, tuple, set, dict，说明是对象，所以需要遍历属性attr_name ###
            if isinstance(current_obj, (list, tuple, set)):
                for index, item in enumerate(current_obj):
                    stack.append((item, f"{path}[{index}]"))
            elif isinstance(current_obj, dict):
                for key, value in current_obj.items():
                    stack.append((value, f"{path}[{key}]"))
            elif isinstance(current_obj, (int, float, str, bool)):
                attributes[path] = current_obj
            else:
                for attr_name in dir(current_obj):
                    if attr_name.startswith('__') and attr_name.endswith('__'):
                        continue
                    ### 自定义跳过的属性 ###
                    if attr_name in self.SKIP_ATTR:
                        continue

                    ### 避免无定义属性 ###
                    try:
                        attr_value = getattr(current_obj, attr_name)
                    except:
                        continue
                    ### 跳过方法功能函数 ###
                    if callable(attr_value): continue

                    ### 记录当前属性轨迹 ###
                    full_path = f"{path}.{attr_name}" if path else attr_name

                    # print(full_path)
                    ### 判断list, tuple, set, dict都要重新放到队列，并记录该属性轨迹 ###
                    ### 如果含有__dict__属性，说明是对象，同样需要继续放回队列，下次轮到后近一步深入遍历这个新的子对象的属性 ###
                    ### 直到最后没有这些属性，都成了值，说明搜索完成，记录到attributes字典中 ###
                    if isinstance(attr_value, (list, tuple, set, dict)):
                        stack.append((attr_value, full_path))
                    elif hasattr(attr_value, '__dict__'):
                        stack.append((attr_value, full_path))
                    else:
                        if full_path is not None:
                            attributes[full_path] = attr_value

        return attributes

    def compare_dicts(self, dict1, dict2, cell_name, miss_dict):
        different_values=[]
        # 找出两个字典中都有的键，但值不同的键值对
        for elem in dict1:
            cell1_elem, cell2_elem = dict1[elem], dict2[elem]
            if cell1_elem != cell2_elem and elem not in miss_dict:
                different_values.append(f"*{cell_name}.{elem}*: ({cell1_elem}) -> ({cell2_elem})")

        return different_values


    def compare_cell(self, in_cell1, in_cell2):
        if in_cell1 == None and in_cell2 == None: return []
        if in_cell1 == None:
            if in_cell2.value==None: return []
            else: return [f"*{in_cell2.coordinate}.value*: (None) -> ({in_cell2.value})"]
        elif in_cell2 == None:
            if in_cell1.value==None: return []
            else: return [f"*{in_cell1.coordinate}.value*: ({in_cell1.value}) -> (None)"]

        all_attributes1 = self.get_all_attributes(in_cell1)
        all_attributes2 = self.get_all_attributes(in_cell2)

        all_attributes1, all_attributes2, miss_dict=self.merge_dicts_mutually(all_attributes1, all_attributes2)
        # b = time.time()
        # print("ETA: ", b-a)

        return self.compare_dicts(all_attributes1, all_attributes2, in_cell1.coordinate, miss_dict)

    def merge_dicts_mutually(self, dict1, dict2):
        # 找出 dict1 中缺失的键
        missing_in_dict1 = set(dict2.keys()) - set(dict1.keys())
        # 找出 dict2 中缺失的键
        missing_in_dict2 = set(dict1.keys()) - set(dict2.keys())

        # 更新 dict1
        dict1.update({key: None for key in missing_in_dict1})
        # 更新 dict2
        dict2.update({key: None for key in missing_in_dict2})

        return dict1, dict2, missing_in_dict1|missing_in_dict2

    def run_compare_cells(self, file1, file2, cur_index):
        file1, file2, miss_dict= self.merge_dicts_mutually(file1, file2)

        results = [self.compare_cell(file1[i], file2[i]) for i in tqdm(file1.keys(), f"对比单元格属性：{cur_index}")]

        return results

if __name__=="__main__":
    file1 = r"C:\Users\Bolt\Downloads\sheet1.npy"
    file2 = r"C:\Users\Bolt\Downloads\sheet1-processed.npy"

    dsc = DeepSearchCells()
    differences = dsc.run_compare_cells(np.load(file1, allow_pickle=True), np.load(file2, allow_pickle=True))

    for diff in differences:
        if diff[1]:
            print(diff)
