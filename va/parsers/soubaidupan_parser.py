import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10006
NAME = '搜百度盘'
search_type = 103

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'http://www.sobaidupan.com/'
    ip = '124.232.133.79'
    address = '湖南省长沙市 电信IDC机房'

    base_parser.add_website_info(table, site_id, url, name, ip = ip, address = address)


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
        # 取页数
        url = 'http://www.sobaidupan.com/search.asp?r=2&wd=%s&p=0&page=0' % search_keyword
        html = tools.get_html_by_urllib(url)
        regex = ['分页：1/(.*?)页'] # 测试0页
        page_count = tools.get_info(html, regex)
        page_count = int(page_count[0]) if page_count else 0
        print(page_count)

        for page in range(0, page_count):
            url = 'http://www.sobaidupan.com/search.asp?r=2&wd=%s&p=0&page=%d'%(search_keyword, page)
            if not base_parser.add_url('VA_urls', SITE_ID, url, remark=remark):
                base_parser.update_url('VA_urls', url, Constance.TODO)

def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_urllib(root_url)
    title = '<tr height="25"><td><a href=".*?"  title="(.*?)"'
    video_url = ['<tr height="25"><td><a href="(.*?)"']
    author = ['<a href="user-.*?.html" target="_blank">(.*?)</a>']
    watched_count = ['浏览次数: </span>(.*?)&nbsp']
    file_size = ['资料大小: </span>(.*?)&nbsp']
    download_count = ['下载次数: </span>(.*?)&nbsp']

    titles = tools.get_info(html, title, allow_repeat = True)
    video_urls = tools.get_info(html, video_url, allow_repeat = True)
    authors = tools.get_info(html, author, allow_repeat = True)
    watched_counts = tools.get_info(html, watched_count, allow_repeat = True)
    file_sizes = tools.get_info(html, file_size, allow_repeat= True)
    download_counts = tools.get_info(html, download_count, allow_repeat = True)


    for i in range(len(titles)):
        title = titles[i]
        title = tools.del_html_tag(title)

        video_url = video_urls[i]
        video_url = tools.get_full_url('http://www.sobaidupan.com', video_url)

        author = authors[i]
        watched_count = watched_counts[i]
        file_size = file_sizes[i]
        download_count = download_counts[i]

        log.debug('''
            标题：    %s
            视频地址： %s
            作者：    %s
            观看数    %s
            资料大小  %s
            下载次数  %s
        '''%(title, video_url, author, watched_count, file_size, download_count))

        contained_key, contained_key_count = base_parser.get_contained_key(title, '',
                                                            remark['search_keyword1'],
                                                            remark['search_keyword2'], remark['search_keyword3'])
        if not contained_key:
            continue

        base_parser.add_content_info('VA_content_info', SITE_ID, video_url, title, file_size = file_size,
                                     file_name = title, author = author, watched_count = watched_count,
                                     download_count = download_count, search_type = search_type,
                                     keyword = contained_key, keyword_count = contained_key_count, task_id = remark['task_id'])

    base_parser.update_url('VA_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    url_info = {
        "_id": "589d621fea18a921b077763b",
        "remark": {
            "search_keyword1": [
                "树大招风"
            ],
            "search_keyword2": [],
            "search_keyword3": []
        },
        "status": 0,
        "site_id": 10006,
        "depth": 0,
        "url": "http://www.sobaidupan.com/search.asp?r=2&wd=树大招风&p=0&page=0"
    }
    parser(url_info)