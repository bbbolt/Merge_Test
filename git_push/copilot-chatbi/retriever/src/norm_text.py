# -*- coding: utf-8 -*-
# @Time : 2023/5/16 下午4:27
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : norm_text.py
"""
构建数据清洗pipeline
"""
import os
import platform
import re
import unicodedata


class CleanDataPipeline(object):
    """
    数据清洗流程
    """

    def __init__(self):
        self.t2s_dict = dict()
        path = os.path.join("src/const/t2s.txt")
        if os.path.exists(path):
            with open(path, "rt", encoding="UTF-8") as fin:
                for line in fin:
                    line = line.strip()
                    if line:
                        traditional, simplified = line.split("\t")
                        self.t2s_dict[traditional] = simplified

    def del_special_char(self, text):
        # text = re.sub("[\x00-\x0F\x10-\x1F\x7F\xa0]+", '', text)
        # text = re.sub("[ ]+", '', text)
        # # 注意，这不是空格，这是特殊的obj字符
        # text = re.sub("[￼ˎ]+", '', text)
        text = re.sub("[❶❷❸❹❺_•\u200d\u0001\u3000\uf06c✔▌■◈▶□●❤◆￼ˎ\x00-\x0F\x10-\x1F\x7F\xa0\"\n\r]+", '', text)

        # 把重复出现的标点压缩成一个
        text = re.sub(r'([^\w])\1+', r'\1', text)
        text = text.replace("\xe2\x80\x8b", "")
        # 英文双引号也去掉
        # text = re.sub("\"", '', text)
        # 替换乱码
        text = text.replace("\uffff", "")
        return text

    def _unicode_small_capital_to_ascii(self, text):
        """
        将一些小号的英文字母转换成正常的字母, eg:
            Fʀɪᴇɴᴅ -> FRIEND
            ᴍᴏᴍ -> MOM
        Args:
            text: 待处理字符串

        Returns:
            处理后文本
        """
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if platform.python_version() < '3.7':
            letters = (x for x in ascii_uppercase if x not in ('Q', 'X'))
        else:
            letters = (x for x in ascii_uppercase if x != 'X')
        mapping = {ord(unicodedata.lookup('LATIN LETTER SMALL CAPITAL ' + x)): x for x in letters}
        tt = str.maketrans(mapping)
        text = text.translate(tt)
        return text

    def t2s(self, text):
        """
        繁转简,  opencc耗时长，不好部署到线上环境
        """
        t_lst = list(text)
        for idx in range(len(t_lst)):
            if t_lst[idx] not in self.t2s_dict:
                continue
            t_lst[idx] = self.t2s_dict[t_lst[idx]]
        text = "".join(t_lst)
        return text

    def del_long_non_chinese_text(self, text):
        # 使用正则表达式匹配连续超过8个字符的非中文文本并替换为空字符串
        cleaned_text = re.sub(r'[^\u4e00-\u9fa5]{8,}', '', text)
        return cleaned_text

    def del_html_entity(self, text):
        # 使用正则表达式删除HTML实体符号
        # "This is a string with &nbsp; and &lt;HTML&gt; entities."
        # 输出：This is a string with  and  entities.
        clean_text = re.sub('&[a-zA-Z0-9]+;', '', text)
        return clean_text

    def upper_to_lower(self, text):
        # 将 XjP 规范成 xjp
        return text.lower()

    def norm_unicode(self, text):
        # unicode字符规范化 ① -> 1 ; ㊉㊚ -> 十男 ; ㏴ -> 21日
        return unicodedata.normalize('NFKC', text)

    def norm_text(self, text):
        """
        对文本做规范化，包括：
        1. 繁体转简体
        2. 全角转半角
        3. 大写转小写
        4. html实体符号删除："&lambda;" "&lt;"  "&nbsp;"
        5. unicode字符规范化：① -> 1 ; ㊉㊚ -> 十男 ; ㏴ -> 21日
        6. 拆分字合并：番羽 土啬 -> 翻/墙 (暂无)
        7. 特殊符号过滤, 空格，\x02等特殊空格,连续多个相同标点合并成一个
        8. 抽象字还原：艹心 -> 操心; (暂无)
        9. 异体字 ⻦ -》鸟， 这两个鸟不等 （暂无）
        10. 删除9位以上的长串数字
        """
        pipeline = [
            # 删除操作交由子服务去做
            # self.del_long_non_chinese_text,
            self._unicode_small_capital_to_ascii,
            self.norm_unicode,
            # self.del_special_char,
            # self.del_html_entity,
            self.upper_to_lower,
            # self.t2s
        ]
        for process in pipeline:
            text = process(text)
        return text


clean_pip = CleanDataPipeline()
