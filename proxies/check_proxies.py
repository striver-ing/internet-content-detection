# -*- coding: utf-8 -*-
'''
Created on 2017-07-05 13:58
---------
@summary: 检测代理是否可用
---------
@author: Boris
'''

import sys
sys.path.append('../')

import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
from db.mongodb import MongoDB
import requests

db = MongoDB()

@tools.run_safe_model(__name__)
def is_proxies_available(ip, port):
    # 检测代理是否可用
    proxies = {'http':"http://{ip}:{port}".format(ip = ip, port = port), 'https':"https://{ip}:{port}".format(ip = ip, port = port)}

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    res = requests.get("http://ip.chinaz.com/getip.aspx", proxies=proxies, headers = headers, timeout = 10)
    print(res.text)

    return True


def main():
    datas = db.find('proxies_content_info')

    for data in datas:
        ip = data['ip']
        port = data['port']
        if is_proxies_available(ip, port):
            db.update('proxies_content_info', data, {"is_available" : True})
        else:
            db.delete('proxies_content_info', data)


if __name__ == '__main__':
    main()



