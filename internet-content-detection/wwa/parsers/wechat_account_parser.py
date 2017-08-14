# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import random
from db.mongodb import MongoDB
import base.constance as Constance
from db.oracledb import OracleDB

# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '微信'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'wwa_save_path') + 'wechat/'

mongodb = MongoDB()

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WWA_wechat_site_info'
    url = 'http://weixin.sogou.com/'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    keywords = parser_params['keywords']

    for keyword in keywords:
        if keyword:
            url = 'http://weixin.sogou.com/weixin?query=%s&_sug_type_=&s_from=input&_sug_=y&type=1&page=1&ie=utf8'%keyword
            if mongodb.find('WWA_wechat_account_url', {'url': url}):
                continue

            headers = {
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Cookie": "wuid=AAGPF/32GQAAAAqLFD2BdAAAGwY=; CXID=A468F618D67D4868DC83E6061B1B3CCC; ABTEST=0|1500285612|v1; weixinIndexVisited=1; SUV=006317867B7CC4C5596C8AAD6B089707; SUIR=0A14ACB4D0CA9B50A8ABB33CD0CA69FA; ld=ekllllllll2BbH49lllllVOm1tylllll1kecBlllll9lllll9Zlll5@@@@@@@@@@; ad=AZllllllll2Bzw7GlllllVOeQA6lllll1kectkllll9lllllVqxlw@@@@@@@@@@@; SUID=72780CD23D148B0A59688B0C0002AD65; IPLOC=CN1100; sct=11; SNUID=B4B50E097177247B9A6BE55E72153425; JSESSIONID=aaaVCfkabuJQTfaNW5f1v",
                "Host": "weixin.sogou.com"
            }
            ip, port, user_agent = base_parser.get_proxies()
            headers["User-Agent"] = user_agent

            html, r = tools.get_html_by_requests(url, headers = headers, proxies = proxies)
            # 判断是否存在公众号
            not_page_tip = '/new/pc/images/bg_404_2.png'
            if not_page_tip in html:
                continue

            # 取页码
            regex = 'id="pagebar_container">.*>(\d*?)</a>.*?<a id="sogou_next"'
            page_num = tools.get_info(html, regex, fetch_one = True)
            page_num = int(page_num) if page_num else 1

            for page in range(1, page_num + 1):
                url = 'http://weixin.sogou.com/weixin?query=%s&_sug_type_=&s_from=input&_sug_=y&type=1&page=%d&ie=utf8'%(keyword, page)
                base_parser.add_url('WWA_wechat_account_url', SITE_ID, url)

            tools.delay_time()

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    retry_times = url_info['retry_times']

    headers = {
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Cookie": "wuid=AAGPF/32GQAAAAqLFD2BdAAAGwY=; CXID=A468F618D67D4868DC83E6061B1B3CCC; ABTEST=0|1500285612|v1; weixinIndexVisited=1; SUV=006317867B7CC4C5596C8AAD6B089707; SUIR=0A14ACB4D0CA9B50A8ABB33CD0CA69FA; ld=ekllllllll2BbH49lllllVOm1tylllll1kecBlllll9lllll9Zlll5@@@@@@@@@@; ad=AZllllllll2Bzw7GlllllVOeQA6lllll1kectkllll9lllllVqxlw@@@@@@@@@@@; SUID=72780CD23D148B0A59688B0C0002AD65; IPLOC=CN1100; sct=11; SNUID=B4B50E097177247B9A6BE55E72153425; JSESSIONID=aaaVCfkabuJQTfaNW5f1v",
        "Host": "weixin.sogou.com"
    }

    ip, port, user_agent = base_parser.get_proxies()
    headers["User-Agent"] = user_agent
    proxies = {'http':"http://{ip}:{port}".format(ip = ip, port = port), 'https':"https://{ip}:{port}".format(ip = ip, port = port)}
    # 解析
    html, request = tools.get_html_by_requests(root_url, headers = headers, proxies = proxies)
    if not html:
        base_parser.update_url('urls', root_url, Constance.TODO, retry_times + 1)
        return

    regex = '<input type=text name="c" value="" placeholder="(.*?)" id="seccodeInput">'
    check_info = tools.get_info(html, regex, fetch_one = True)
    log.debug('取公众号列表' + check_info)

    # 公众号信息块
    regex = '<!-- a -->(.*?)<!-- z -->'
    account_blocks = tools.get_info(html, regex)

    if not account_blocks:
        base_parser.update_url('urls', root_url, Constance.TODO, retry_times + 1)
        return

    # 文章数url
    regex = '<script>var account_anti_url = "(.*?)";</script>'
    articles_count_url = tools.get_info(html, regex, fetch_one = True)
    articles_count_url = tools.get_full_url('http://weixin.sogou.com', articles_count_url)
    articles_count_json = tools.get_json_by_requests(articles_count_url).get('msg', {})

    for account_block in account_blocks:
        # print(account_block)
        regex = '<a.*?account_name.*?>(.*?)</a>'
        name = tools.get_info(account_block, regex, fetch_one = True)
        name = tools.del_html_tag(name)

        is_have = mongodb.find('WWA_wechat_official_accounts', {'name' : name})
        if is_have:
            log.debug(name + " 已存在")
            continue

        regex = '<div class="img-box">.*?<img src="(.*?)"'
        image_url = tools.get_info(account_block, regex, fetch_one = True)

        # 下载图片
        local_image_url = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.jpg'
        is_download = tools.download_file(image_url, local_image_url)
        local_image_url = local_image_url if is_download else ''


        regex = '<p class="tit">.*?(<i></i>).*?<p class="info">'
        is_verified = 102 if tools.get_info(account_block, regex, fetch_one = True) else 101

        regex = '<label name="em_weixinhao">(.*?)</label>'
        account_id = tools.get_info(account_block, regex, fetch_one = True)

        regex = '<li id="sogou_vr_.*?d="(.*?)">'
        article_count_key = tools.get_info(account_block, regex, fetch_one = True)
        article_count = articles_count_json.get(article_count_key, '')
        article_count = article_count[:article_count.find(',')]

        regex = '<dt>功能介绍.*?<dd>(.*?)</dd>'
        summary = tools.get_info(account_block, regex, fetch_one = True)
        summary = tools.del_html_tag(summary)

        regex = "认证.*?<dd>(.*?)</dd>"
        certification = tools.get_info(account_block, regex, fetch_one = True)

        regex = '微信扫一扫关注.*?<img.*?src="(.*?)"'
        barcode_url = tools.get_info(account_block, regex, fetch_one = True)
        barcode_url = barcode_url.replace('&amp;',"&")

        # 下载图片
        local_barcode_url = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.jpg'
        is_download = tools.download_file(barcode_url, local_barcode_url)
        local_barcode_url = local_barcode_url if is_download else ''

        regex = '<a.*?account_name.*?href="(.*?)">'
        account_url = tools.get_info(account_block, regex, fetch_one = True)
        account_url = account_url.replace('&amp;',"&")

        log.debug('''
            公众号名称          %s
            公众号账号          %s
            账号url             %s
            贴图                %s
            本地贴图            %s
            文章数量            %s
            简介                %s
            微信认证            %s
            是否加V（是否认证） %s
            二维码              %s
            本地二维码          %s
            '''%(name, account_id, account_url, image_url, local_image_url, article_count, summary, certification, is_verified, barcode_url, local_barcode_url))

        base_parser.add_wechat_account_info('WWA_wechat_official_accounts', site_id, name, account_id, account_url, image_url, local_image_url, article_count, summary, certification, is_verified, barcode_url, local_barcode_url)

    base_parser.update_url('WWA_wechat_account_url', root_url, Constance.DONE)
    tools.delay_time()


if __name__ == '__main__':
    url_info = {'remark': '', '_id': '5975b4ed53446557e04bdc45', 'retry_times': 0, 'url': 'http://weixin.sogou.com/weixin?query=环球军事&_sug_type_=&s_from=input&_sug_=y&type=1&page=1&ie=utf8', 'depth': 0, 'status': 0, 'site_id': 1}

    parser(url_info)
