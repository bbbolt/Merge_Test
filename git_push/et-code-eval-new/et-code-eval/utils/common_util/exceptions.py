# -- coding: utf-8 --
class ParameterIncorrectError(Exception):
    """
    输入参数错误
    """

    def __init__(self, error_info):
        super().__init__(self)  # 初始化父类
        self.error_info = error_info

    def __str__(self):
        return self.error_info


class ExecuteFailedError(Exception):
    """
    调用Step失败
    """

    def __init__(self, error_info):
        super().__init__(self)  # 初始化父类
        self.error_info = error_info

    def __str__(self):
        return self.error_info


class DoCheckpointFailedError(Exception):
    """
    调用Checkpoint失败
    """

    def __init__(self, error_info):
        super().__init__(self)  # 初始化父类
        self.error_info = error_info

    def __str__(self):
        return self.error_info
