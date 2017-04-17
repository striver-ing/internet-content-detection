import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10005
NAME = '微信'
SEARCH_TYPE = 105

HEADER = {
    # 'Cookie':'usid=_GW9W2q3bS3Gmnt8; IPLOC=CN1100; SUV=004074AAD39C8C4A582E927B4CCD4712; CXID=5D6D9135174B33DFACFC3DF1AD4DD4F8; SUID=4A8C9CD3536C860A584F61EC000B6DF9; ABTEST=3|1484546443|v1; weixinIndexVisited=1; sct=35; td_cookie=18446744071319380747; ad=kMpvFZllll2YFL47lllllVAVuyolllll1ihGvkllllwlllllVZlll5@@@@@@@@@@; SNUID=3CFAEBA47673309C553254F5773632F4; JSESSIONID=aaaf69NvfBER-b6cKSfNv',
    'Host':'weixin.sogou.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
}

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')

    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'http://weixin.sogou.com/'
    ip = '183.36.114.45'
    address = '广东省广州市 电信'
    icp = '050897'
    public_safety = '11000002000025'

    base_parser.add_website_info(table, site_id, url, name, ip = ip, address = address, icp = icp, public_safety = public_safety)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    search_keyword1 = parser_params['search_keyword1']
    search_keyword2 = parser_params['search_keyword2']
    search_keyword3 = parser_params['search_keyword3']

    remark = parser_params

    search_keywords = []
    for str_key1 in search_keyword1:
        for str_key2 in search_keyword2:
            search_keywords.append((str_key1 + str_key2).strip())
    else:
        if not search_keyword1:
            search_keywords = search_keyword2
        if not search_keyword2:
            search_keywords = search_keyword1

    for search_keyword in search_keywords:
        if not search_keyword.strip():
            continue
        # 最多显示10页
        for page in range(1, 11):
            url = 'http://weixin.sogou.com/weixin?type=2&query=' + search_keyword + '&page=%d&ie=utf8'%page
            if not base_parser.add_url('VA_urls', SITE_ID, url, remark = remark):
                base_parser.update_url('VA_urls', url, Constance.TODO)



# @tools.run_safe_model(__name__) # 移到parser_control
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    # 解析
    html, request = tools.get_html_by_requests(root_url, headers = HEADER)

    if not html:
        base_parser.update_url('urls', root_url, Constance.EXCEPTION)
        return

    news_box = tools.get_tag(html, name = 'div', attrs={'class':"news-box"})[0]

    news_list = tools.get_tag(news_box, name = 'li')
    for news in news_list:
        try:
            # 图片
            image = tools.get_tag(news, name = 'img')[0]
            image = tools.get_json_value(image, 'src')

            # url
            url = tools.get_tag(news, name = 'h3')[0]
            try:
                url = tools.get_json_value(url.a, 'href')
            except:
                url = ''

            # 标题
            title = tools.get_tag(news, name = 'h3')[0]
            title = tools.get_text(title)
            title = tools.del_html_tag(title)

            # 内容
            content = tools.get_tag(news, name = 'p', attrs = {'class':"txt-info"})[0]
            content = tools.get_text(content)
            content = tools.del_html_tag(content)

            # 观看数
            watched_count = ''

            # 来源
            origin = tools.get_tag(news, name = 'div', attrs = {'class':"s-p"})[0]
            origin = ''.join(tools.get_info(origin, '<a.*?>(.*?)<'))

            # 日期
            release_time = tools.get_tag(news, name = 'div', attrs = {'class':"s-p"})[0]
            release_time = tools.get_json_value(release_time, 't')
            release_time = tools.timestamp_to_date(int(release_time))

            # 判断是否有视频 根据视频播放图标判断
            regex = '<div class="img-box">.*?<i></i>.*?</div>'
            play_icon = tools.get_info(news, regex)

        except:
            continue

        contained_key, contained_key_count = base_parser.get_contained_key(title, content, remark['search_keyword1'], remark['search_keyword2'], remark['search_keyword3'], task_id = remark['task_id'])

        log.debug('''
            标题：   %s
            内容：   %s
            来源：   %s
            原文url：%s
            图片url：%s
            观看数： %s
            日期：   %s
            有视频： %d
            关键词： %s
            关键词数:%s
                  '''%(title, content, origin, url , image, watched_count, release_time, play_icon and True or False, contained_key, contained_key_count))

        if not contained_key or not play_icon:
            continue

        base_parser.add_content_info('VA_content_info', SITE_ID, url, title, content, image_url = image, release_time = release_time, origin = origin,
                                     watched_count = watched_count, search_type=SEARCH_TYPE, keyword = contained_key, keyword_count = contained_key_count)

    base_parser.update_url('VA_urls', root_url, Constance.DONE)

# url_info = {
#     'remark': {'search_keyword2': [],
#     'search_keyword1': ['世界上最危险的道路'],
#     'search_keyword3': []},
#     '_id': '58996d3fefc81c10d57a250e',
#     'site_id': 10005,
#     'status': 0,
#     'depth': 0,
#     'url': 'http://weixin.sogou.com/weixin?type=2&query=世界上最危险的道路&page=1&ie=utf8',
# }
# print(tools.dumps_json(url_info))
# parser(url_info)

