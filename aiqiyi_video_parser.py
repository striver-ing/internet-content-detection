import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log
import re

SITE_ID = 10007
NAME = '豆瓣网'
search_type = 106

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'http://www.iqiyi.com/'


    base_parser.add_website_info(table, site_id, url, name, )


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    DOWNLOAD_HEADER = {
        'Host': 'iface2.iqiyi.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        't': '446513656',
        'Connection': 'keep-alive',
        'Cookie': 'P00001=53igk5Vn7X1xpazWBjzW2HUN4XGjNSP4aQypF7affdnBUaC6rknOS4dzvIcU1pMm2m2Qfb; QC005=63505c6afe3861f5e3f89adb3b33c7e8; P00002=%7B%22uid%22%3A%221229289410%22%2C%22user_name%22%3A%22564773807%40qq.com%22%2C%22email%22%3A%22564773807%40qq.com%22%2C%22nickname%22%3A%22BorisLiu%22%2C%22pru%22%3A1229289410%2C%22type%22%3A10%2C%22pnickname%22%3A%22BorisLiu%22%7D; P00004=1992744720.1484365089.92d0523466; T00404=5d08312eeb25b464ea9e424b74bc5aea; Hm_lvt_53b7374a63c37483e5dd97d78d9bb36e=1483756029; QC006=1296d3c47c29d816dff47d0916cbc288; QC008=1483756029.1483756029.1483756029.2; QC118=%7B%22color%22%3A%22FFFFFF%22%2C%22size%22%3A20%2C%22channelConfig%22%3A0%7D',
        'User-Agent': 'QIYIVideo/8.1 (iOS;com.qiyi.iphone;iOS10.2.1;iPhone9,2) Corejar',
        'sign': 'be218f97f09752dd6999ec86a22dbf6f',
        'Accept-Encoding': 'gzip',
        # 'Connection': 'keep-alive'
    }

    def get_download_url(url):
        html, r = tools.get_html_by_requests(url)

        tvid = re.compile('player-tvid="(\d{4,11})"').findall(str(html))
        if not tvid:
            tvid = re.compile('list-tvid="(\d{4,11})"').findall(str(html))
        for i in tvid:
            tvid = i

        album_id = ''.join(re.compile('player-albumid="(\d{4,11})"').findall(str(html)))
        if not album_id:
            album_id = ''.join(re.compile('list-albumid="(\d{4,11})"').findall(str(html)))
            if not album_id:
                album_id = ''.join(re.compile('albumId: ?(\d{4,11}),').findall(str(html)))
                if not album_id:
                    album_id = ''.join(re.compile('param\[\'albumId\'\] ?= ?"(\d{4,11})"').findall(str(html)))

        current_time = tools.get_current_timestamp() * 1000
        current_time = str(current_time)

        url = 'http://iface2.iqiyi.com/video/3.0/v_download?app_k=8e48946f144759d86a50075555fd5862&app_v=8.1&qyid=D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB&secure_p=iPhone&secure_v=1&dev_hw=%7B%22cpu%22:%22%22,%22mem%22:%222802%22%7D&net_sts=1&device_id=D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB&dev_os=10.2.1&dev_ua=iPhone9,2&net_ip=%7B%22country%22:%22%E4%B8%AD%E5%9B%BD%22,%22province%22:%22%E5%8C%97%E4%BA%AC%22,%22city%22:%22%E5%8C%97%E4%BA%AC%22,%22cc%22:%22%E5%9B%BD%E5%86%85%E5%85%B6%E4%BB%96%22,%22area%22:%22%E5%8D%8E%E5%8C%97%22,%22timeout%22:0,%22respcode%22:0%7D&album_id=' + album_id + '&tvid=' + tvid + '&req_times=1&play_core=0&platform_id=12&app_p=iphone&app_t=0&usr_res=16&ppid=1229289410&cookie=53igk5Vn7X1xpazWBjzW2HUN4XGjNSP4aQypF7affdnBUaC6rknOS4dzvIcU1pMm2m2Qfb&lang=zh_CN&app_lm=cn&pps=0&req_sn=' + current_time
        json_ = tools.get_json_by_requests(url, headers=DOWNLOAD_HEADER)

        try:
            video_download_url = ''.join(re.compile('\'1\': {(.+?)},').findall(str(json_)))
            video_download_url = ''.join(re.compile('\'url\': ?\'(.+?)\'').findall(str(video_download_url)))
            video_download_url, r = tools.get_html_by_requests(video_download_url)
            video_download_url = ''.join(re.compile('"l":"(.+?)"').findall(str(video_download_url)))
        except:
            video_download_url = ''
        return video_download_url

    def add_root_urls(url):
        html, r = tools.get_html_by_requests(url)
        # print(html)
        regex = '<div class="site-piclist_pic">(.*?)</li>'
        html_infos = tools.get_info(html, regex)
        s = 0
        for info in html_infos:
            regex = 'href = "(.*?)" class="site-piclist_pic_link"'
            url = tools.get_info(info, regex)
            url = url and url[0] or ''
            regex = 'rseat="bigTitle.*?title="(.*?)"'
            name = tools.get_info(info, regex)
            name = name and name[0] or ''
            name = tools.del_html_tag(name)
            video_download_url = get_download_url(url)
            FILE_LOCAL_PATH = 'd:'
            sto_path = '/videos/' + name + '.mp4'
            tools.download_file(video_download_url, FILE_LOCAL_PATH, sto_path)
            print(video_download_url, name)


    add_root_urls(url)


if __name__ == '__main__':
    url_info = {
        "_id": "591bb22bea18a91f200aad10",
        "remark": "",
        "site_id": 9,
        "status": 3,
        "depth": 0,
        "url": "http://list.iqiyi.com/www/25/-------------4-3-2-iqiyi-1-.html"
    }
    parser(url_info)