import os
import shutil


def exists(path: str):
    return os.path.exists(path)


def delete_file(path: str):
    os.remove(path)


def move_file(src: str, dst: str):
    shutil.move(src, dst)


def write_file(path: str, content: str):
    with open(path, 'w', encoding="utf-8") as f:
        f.write(content)


def read_file(path: str):
    if not exists(path):
        return ""
    with open(path, 'r', encoding="utf-8") as f:
        return f.read()


# 获取文件绝对路径
def get_abs_path(path: str):
    return os.path.abspath(path)


# 获取文件名
def get_file_name(path: str):
    return os.path.basename(path)


# 文件拷贝
def copy_file(src: str, dst: str):
    shutil.copy(src, dst)


# 从共享拷贝文件
def copy_folder_from_lan(source_path, destination_path):
    # 检查源路径是否存在
    if not os.path.exists(source_path):
        print(f"源路径不存在: {source_path}")
        return

    # 检查目标路径是否存在，如果不存在，则创建
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # 遍历源路径下的所有文件和文件夹
    for item in os.listdir(source_path):
        item_path = os.path.join(source_path, item)

        # 如果是文件，则复制到目标路径
        if os.path.isfile(item_path):
            shutil.copy(item_path, destination_path)

        # 如果是文件夹，则递归复制
        elif os.path.isdir(item_path):
            new_destination = os.path.join(destination_path, item)
            copy_folder_from_lan(item_path, new_destination)


def get_md5(file_path):
    """
    获取文件的md5值
    :param file_path:
    """
    import hashlib
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    return md5


def get_file_size(file_path):
    """
    获取文件大小，单位：B
    :param file_path:
    :return:
    """
    file_size_bytes = os.path.getsize(file_path)
    return file_size_bytes