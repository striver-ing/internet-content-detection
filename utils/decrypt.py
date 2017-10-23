# -*- coding: utf-8 -*-
'''
Created on 2017-09-04 11:03
---------
@summary:
---------
@author: Boris
'''
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import base64


class Prpcrypt():
    def __init__(self, key):
        '''
        @summary:
        ---------
        @param key:秘钥 长度需要为16, 过长或不足自动截取或追加
        ---------
        @result:
        '''

        # 支持中文
        key = key.encode('utf8')
        key = base64.b64encode(key)
        key = key.decode('utf8')

        self.append = '\0'
        self.key = (key + (16 - len(key) % 16) * self.append)[:16]
        self.mode = AES.MODE_CBC

    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        try:
            cryptor = AES.new(self.key, self.mode, self.key)
            plain_text = cryptor.decrypt(a2b_hex(text))
            text = plain_text.decode('utf8').rstrip('\0')
            return base64.b64decode(text).decode('utf8')
        except Exception as e:
            print(e)
            return "解密失败"

def main(text):
    keys = 'pattek.com.cn'
    prpcrypt = Prpcrypt(keys)

    content = text
    decrypt_text = prpcrypt.decrypt(content)
    return decrypt_text
    return text

if __name__ == '__main__':
    pass
    # content = sys.argv[1]
    # print(content)
    # # content = '1ccdb60052d4aeb2aa924a98f6e38ec7f5e35dd6fcb456b4af24ef195ca12efe12638a657c389128dbf7e694aa5e4874f701f251ed6b5d2b8bb0b295960b68b4c70cc22bcf83a469c78bfd8fe71b4eac92145e74a9ecf232b63f6f8f75a8f914072867c6a7837854ee3d85224ba2cb32a812241a091af2ed2cbde8d477432303f91c7e9b7b114c7f42e12bfb36fe489ce88fb03a387a4168c72ca416551e7529499bc4f98bc96a58d24e847bd4136a2c6b6a2a3816395c9187e02db7349e66f26ae8ed9fd21ce045d150158cc87d4e7d8f73c2ad18868410321e5d53a2a1e1b9015f55ff6b514046365e377ed6511ef0d3d268300f822f2d3b9328c2ed7f4c0a7b81dff1ffa73e54f22211ecb41f3b7a0b7e82fec63e4e701f3ba185603996a899e6b7d559bd057018ae8e3d7ed2c2c1e554de6b92e791e66862adf947c4d2254a4f61164c3092080315deb4b52737305a03614fdb2cb313107520ac79dc338e'
    # decrypt_text = prpcrypt.decrypt(content)

    # print(decrypt_text)
#     # print(main('1ccdb60052d4aeb2aa924a98f6e38ec7f5e35dd6fcb456b4af24ef195ca12efe12638a657c389128dbf7e694aa5e4874f701f251ed6b5d2b8bb0b295960b68b4c70cc22bcf83a469c78bfd8fe71b4eac92145e74a9ecf232b63f6f8f75a8f914072867c6a7837854ee3d85224ba2cb32a812241a091af2ed2cbde8d477432303f91c7e9b7b114c7f42e12bfb36fe489ce88fb03a387a4168c72ca416551e7529499bc4f98bc96a58d24e847bd4136a2c6b6a2a3816395c9187e02db7349e66f26ae8ed9fd21ce045d150158cc87d4e7d8f73c2ad18868410321e5d53a2a1e1b9015f55ff6b514046365e377ed6511ef0d3d268300f822f2d3b9328c2ed7f4c0a7b81dff1ffa73e54f22211ecb41f3b7a0b7e82fec63e4e701f3ba185603996a899e6b7d559bd057018ae8e3d7ed2c2c1e554de6b92e791e66862adf947c4d2254a4f61164c3092080315deb4b52737305a03614fdb2cb313107520ac79dc338e'))

#     # file_path = input('请拖入需要解密的txt文件\n')
#     # file_content = ''

#     # with open(file_path, mode = 'r', encoding = 'utf-8') as file:
#     #     file_content = file.read()

#     # print('解密中...')
#     # prpcrypt = Prpcrypt(keys)
#     # decrypt_text = prpcrypt.decrypt(file_content)
#     # if not decrypt_text:
#     #     sys.exit()

#     # with open(file_path, mode = 'w', encoding = 'utf-8') as file:
#     #     print(decrypt_text)
#     #     file.write(decrypt_text)

#     # print('解密成功！')

#     # input()