import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10004
search_type = 102
NAME = '新浪微博'

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WWA_site_info'
    url = 'https://m.weibo.cn/'
    domain = 'weibo.cn'
    ip = '180.149.153.216'
    address = '中国 北京'
    base_parser.add_website_info(table, site_id, url, name, domain, ip, address)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params):
    log.debug('''
        添加根url
        parser_params : %s
        ''' % str(parser_params))
    for search_keyword in parser_params:
        remark = search_keyword
        if not search_keyword:
            continue
        search_keyword = tools.quote(search_keyword, safe='/:?=&%')
        url = 'http://m.weibo.cn/api/container/getIndex?type=user&containerid=100103type%3D3%26q%3D' + search_keyword
        base_parser.add_url('WWA_weibo_user_urls', SITE_ID, url, remark=remark)


def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    for i in range(2, 100):
        list_url = root_url + '&page=%d' % i
        html = tools.get_json_by_requests(list_url)

        cards = tools.get_json_value(html, 'cards')
        card_group = []
        for i in cards:
            card_group = tools.get_json_value(i, 'card_group')
            if card_group:
                break
        if not card_group:
            break

        for info in card_group:
            user_info = tools.get_json_value(info, 'user')
            _id = tools.get_json_value(user_info, 'id')

            user_url = 'http://m.weibo.cn/api/container/getIndex?containerid=230283%s_-_INFO' % _id
            user_url_html = tools.get_json_by_requests(user_url)
            user_url_cards = tools.get_json_value(user_url_html, 'cards')
            user_url_card_group = tools.get_json_value(user_url_cards[0], 'card_group')
            area = ''
            for i in user_url_card_group:
                if tools.get_json_value(i, 'item_name') == '所在地':
                    area = tools.get_json_value(i, 'item_content')
                else:
                    continue

            name = tools.get_json_value(user_info, 'screen_name')
            is_verified_reason = 101
            verified_reason = tools.get_json_value(user_info, 'verified_reason')
            if verified_reason:
                is_verified_reason = 102
            sex = tools.get_json_value(user_info, 'gender')
            if sex == 'f':
                sex = 1
            elif sex == 'm':
                sex = 0
            else:
                sex = ''
            image_url = tools.get_json_value(user_info, 'profile_image_url')
            url = tools.get_json_value(user_info, 'profile_url')
            summary = tools.get_json_value(user_info, 'description')
            user_url_2 = 'http://m.weibo.cn/api/container/getIndex?containerid=100505%s' % _id
            user_url_html_2 = tools.get_json_by_requests(user_url_2)
            fans_count = tools.get_json_value(user_url_html_2, 'userInfo.followers_count')
            follow_count = tools.get_json_value(user_url_html_2, 'userInfo.follow_count')

            log.debug('''
                         用户id：     %s
                         微博昵称：   %s
                         微博地址：   %s
                         头像地址：   %s
                         微博认证：   %s
                         是否认证：   %s
                         所在地：     %s
                         性别：       %s
                         简介：       %s
                         粉丝数：     %s
                         关注数：     %s
                        ''' % (_id, name, url, image_url, verified_reason, is_verified_reason, area, sex,
                               summary, fans_count, follow_count))
            base_parser.add_wwa_weibo_user_info('WWA_weibo_user_info', SITE_ID, _id, name, url, image_url, verified_reason,
                                                is_verified_reason, area, sex, summary, fans_count, follow_count)
        tools.delay_time()
    base_parser.update_url('WWA_weibo_user_urls', root_url, Constance.DONE)
    tools.delay_time()

# parser({'url': 'http://m.weibo.cn/api/container/getIndex?type=user&containerid=100103type%3D3%26q%3D%E9%87%8D%E5%BA%86%E7%94%B5%E8%A7%86%E5%8F%B0'})