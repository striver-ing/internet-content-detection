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

    keyword = parser_params['keyword']

    if keyword:
        for page in range(1, 11):
            url = 'http://weixin.sogou.com/weixin?query=%s&_sug_type_=&s_from=input&_sug_=y&type=1&page=%d&ie=utf8'%(keyword, page)
            base_parser.add_url('WWA_wechat_account_url', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    # 解析
    html, request = tools.get_html_by_requests(root_url)
    if not html:
        base_parser.update_url('urls', root_url, Constance.EXCEPTION)
        return

    # 公众号信息块
    regex = '<!-- a -->(.*?)<!-- z -->'
    account_blocks = tools.get_info(html, regex)

    # 文章数url
    regex = '<script>var account_anti_url = "(.*?)";</script>'
    articles_count_url = tools.get_info(html, regex, fetch_one = True)
    articles_count_url = tools.get_full_url('http://weixin.sogou.com', articles_count_url)
    articles_count_json = tools.get_json_by_requests(articles_count_url).get('msg', {})

    for account_block in account_blocks:
        # print(account_block)
        regex = '<div class="img-box">.*?<img src="(.*?)"'
        image_url = tools.get_info(account_block, regex, fetch_one = True)

        regex = '<a.*?account_name.*?>(.*?)</a>'
        name = tools.get_info(account_block, regex, fetch_one = True)
        name = tools.del_html_tag(name)

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

        regex = '<a.*?account_name.*?href="(.*?)">'
        account_url = tools.get_info(account_block, regex, fetch_one = True)

        log.debug('''
            公众号名称          %s
            公众号账号          %s
            账号url             %s
            贴图                %s
            文章数量            %s
            简介                %s
            微信认证            %s
            是否加V（是否认证） %s
            二维码              %s
            '''%(name, account_id, account_url, image_url, article_count, summary, certification, is_verified, barcode_url))

        base_parser.add_wechat_accout_info('WWA_wechat_official_accounts', site_id, name, account_id, account_url, image_url, article_count, summary, certification, is_verified, barcode_url)

    base_parser.update_url('WWA_wechat_account_url', root_url, Constance.DONE)


if __name__ == '__main__':
    url_info = {
            "_id" : "58c8a09b53446519a80d2ac6",
            "status" : 2,
            "site_id" : 3,
            "url" : "http://weixin.sogou.com/weixin?query=重庆&_sug_type_=&s_from=input&_sug_=y&type=1&page=1&ie=utf8",
            "depth" : 0,
            "remark" : ''
        }

    parser(url_info)
