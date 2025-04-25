# -*- coding: utf-8 -*-
# @Time : 2024/4/1 下午3:37
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : crypt.py

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

from const.env import aes_key


class PrpCrypt(object):
    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        text = text.encode('utf-8')
        self.iv = get_random_bytes(16)
        cryptor = AES.new(self.key, self.mode, self.iv)
        ciphertext = self.iv + cryptor.encrypt(pad(text, AES.block_size))
        return str(base64.b64encode(ciphertext), 'utf-8')

    def decrypt(self, text):
        encry_text = base64.b64decode(text)
        iv = encry_text[:16]
        text = encry_text[16:]
        cryptor = AES.new(self.key, self.mode, iv)
        text = cryptor.decrypt(text)
        plain_text = unpad(text, AES.block_size)
        return str(plain_text, 'utf-8')


prpcrypt = PrpCrypt(aes_key)

