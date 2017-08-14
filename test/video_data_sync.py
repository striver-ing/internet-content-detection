#coding: utf8
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
class prpcrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    #加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        #这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = AES.block_size #16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        print(text)
        print(len(text))
        self.ciphertext = cryptor.encrypt(text)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext).decode('utf8')

    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.decode('utf8').rstrip('\0')

if __name__ == '__main__':
    # import base64

    # text = "你好".encode('utf8')
    # text = base64.b64encode(text)
    # print(1111111111111)
    # print(text)
    # # text = base64.b64decode(text)
    # # print(text.decode('utf8'))
    # pc = prpcrypt('keyskeyskeyskeys')      #初始化密钥
    # e = pc.encrypt(text.decode('utf8'))
    # d = pc.decrypt(e)

    # print(22222222222)
    # print(d)
    # print(text)
    # # d = b'5L2g5aW9'
    # # text = b'5L2g5aW9'
    # d = d.encode('utf8')
    # print(type(d))
    # print(type(text))
    # print(d)
    # print(d == text)
    # # b'5L2g5aW9'
    # d = base64.b64decode(d).decode('utf8')
    # # d = d.decode('utf8')

    # print (e, d)
    # # e = pc.encrypt("年后")
    # # d = pc.decrypt(e)
    # # print (e, d)

    text = '你好aaaaa'
    text = text.encode('utf8')
    print(text)
    print(text[2] - '0')
    print(type(text))
    text = text.decode('utf8')
    print(type(text))
    print(text)