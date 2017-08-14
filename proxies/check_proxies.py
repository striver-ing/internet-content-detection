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
    # proxies = {'https': 'https://210.35.171.5:8080', 'http': 'http://210.35.171.5:8080'}

    # headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    # import random
    # headers['User-Agent'] = random.choice(Constance.USER_AGENTS)
    # html, request = tools.get_html_by_requests('http://weixin.sogou.com/weixin?type=1&s_from=input&query=jljg89&ie=utf8&_sug_=n&_sug_type_=', headers = headers, proxies = proxies)
    # print(html)


    # main()
    proxies, r = tools.get_html_by_requests('http://127.0.0.1:8000/?types=0&count=200')
    proxies_info = eval(proxies)
    print(proxies_info)

    for proxie in proxies_info:
        ip = proxie[0]
        port = proxie[1]
        print(ip)
        print(port)
        print(proxie)
        is_proxies_available(ip, port)

        # headers = {
        #     "Cache-Control": "max-age=0",
        #     "Host": "weixin.sogou.com",
        #     "Accept-Encoding": "gzip, deflate",
        #     "Accept-Language": "zh-CN,zh;q=0.8",
        #     "Connection": "keep-alive",
        #     "Cookie": "SUID=72780CD23D148B0A59688B0C0002AD65; wuid=AAGPF/32GQAAAAqLFD2BdAAAGwY=; CXID=A468F618D67D4868DC83E6061B1B3CCC; ad=QZllllllll2Bzw7GlllllVOoAZ1lllll1kectkllllylllllROxlw@@@@@@@@@@@; ABTEST=0|1500285612|v1; IPLOC=CN1100; weixinIndexVisited=1; SUV=006317867B7CC4C5596C8AAD6B089707; SNUID=0A14ACB4D0CA9B50A8ABB33CD0CA69FA; JSESSIONID=aaaAhmO07JCzF5I8fVf1v; sct=1",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        #     "Upgrade-Insecure-Requests": "1",
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        # }
        # import random
        # headers['User-Agent'] = random.choice(Constance.USER_AGENTS)

        # proxies = {'http':"http://{ip}:{port}".format(ip = ip, port = port), 'https':"https://{ip}:{port}".format(ip = ip, port = port)}
        # html, request = tools.get_html_by_requests('http://weixin.sogou.com/weixin?type=1&s_from=input&query=jljg89&ie=utf8&_sug_=n&_sug_type_=', headers = headers, proxies = proxies)

        # # print(html)
        # regex = '<input type=text name="c" value="" placeholder="(.*?)" id="seccodeInput">'
        # check_info = tools.get_info(html, regex, fetch_one = True)
        # log.debug('取文章链接' + check_info)
        # break



