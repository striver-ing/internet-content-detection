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
        except:
            print("秘钥不符, 解密失败")

if __name__ == '__main__':
    keys = 'pattek.com.cn'

    file_path = input('请拖入需要解密的txt文件\n')
    file_content = ''

    with open(file_path, mode = 'r', encoding = 'utf-8') as file:
        file_content = file.read()

    print('解密中...')
    prpcrypt = Prpcrypt(keys)
    decrypt_text = prpcrypt.decrypt(file_content)
    if not decrypt_text:
        sys.exit()

    with open(file_path, mode = 'w', encoding = 'utf-8') as file:
        print(decrypt_text)
        file.write(decrypt_text)

    print('解密成功！')

    input()