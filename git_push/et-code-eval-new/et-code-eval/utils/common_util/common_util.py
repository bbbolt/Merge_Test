def sort_dict_list(dict_list, order_list):
    sorted_dict_list = []
    for d in dict_list:
        sorted_dict = {k: d.get(k) if d.get(k) is not None else '' for k in order_list}
        sorted_dict_list.append(sorted_dict)
    return sorted_dict_list
