import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10002
NAME = 'bt磁力链'
search_type = 104

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'http://www.bturls.net/'
    domain = 'bturls.net'
    ip = '163.44.175.163'
    address = '日本 东京都'

    base_parser.add_website_info(table, site_id, url, name, domain, ip, address)

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

    n = 100
    for j in search_keywords:
        if not j.strip():
            continue
        for i in range(1, n + 1):
            url = 'http://www.bturls.net/search/%s_ctime_%d.html' % (j, i)
            if not base_parser.add_url('VA_urls', SITE_ID, url, remark=remark):
                base_parser.update_url('VA_urls', url, Constance.TODO)

# @tools.run_safe_model(__name__) # 移到parser_control
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html, requests = tools.get_html_by_requests(root_url)
    titles = tools.get_tag(html, 'h3')
    video_infos = tools.get_tag(html, 'dt')
    for i in range(0, len(titles)):
        title = tools.get_text(titles[i])
        title = tools.del_html_tag(title)
        try:
            url = titles[i].a['href']
        except:
            continue
        url = 'http://www.bturls.net' + url

        release_time = video_infos[i].span
        release_time = tools.get_text(release_time)

        file_size = video_infos[i].span.next_sibling.next_sibling
        file_size = tools.get_text(file_size)

        watched_count = video_infos[i].span.next_sibling.next_sibling.next_sibling.next_sibling
        watched_count = tools.get_text(watched_count)

        regexs = ['t/(.+?)\.']
        magnet_link = 'magnet:?xt=urn:btih:'+''.join(tools.get_info(url,regexs))

        log.debug('''
            标题：    %s
            文件大小：%s
            原文url： %s
            观看数量：%s
            磁力链接：%s
            日期：    %s
               ''' % (title, file_size, url, watched_count, magnet_link, release_time))

        contained_key, contained_key_count = base_parser.get_contained_key(title, '',remark['search_keyword1'],
                                                            remark['search_keyword2'], remark['search_keyword3'])
        if not contained_key:
            continue

        base_parser.add_content_info('VA_content_info', SITE_ID, url, title, file_size = file_size,
                                     release_time = release_time,watched_count = watched_count,
                                     magnet_link = magnet_link, search_type = search_type,
                                     keyword = contained_key, keyword_count = contained_key_count, task_id = remark['task_id'])
    base_parser.update_url('VA_urls', root_url, Constance.DONE)

