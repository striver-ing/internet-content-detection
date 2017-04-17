import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10007
NAME = '豆瓣网'
search_type = 106

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'https://www.douban.com/'
    ip = '115.182.201.8'
    public_safety = '11010502000728'
    video_license = '0110418'
    icp = '090015'
    address = '北京市 鹏博士长城宽带'

    base_parser.add_website_info(table, site_id, url, name, ip = ip, address = address,video_license = video_license,
                                 icp = icp, public_safety = public_safety)


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
        url = 'https://movie.douban.com/subject_search?start=0&search_text=%s&cat=1002' % search_keyword
        html = tools.get_html_by_urllib(url)
        regex = '<div class="paginator">.*<a href.*?>(.*?)</a><span class="next"'
        page_count = tools.get_info(html, regex)
        page_count = int(page_count[0]) if page_count else 0
        print(page_count)

        for page in range(0, page_count):
            url = 'https://movie.douban.com/subject_search?start=%d&search_text=%s&cat=1002'% (page*15, search_keyword)
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
    regex = '<tr class="item">(.*?)</tr>'
    infos = tools.get_info(html, regex)
    for info in infos:
        title = ['<a href=".*?" onclick=.*?; class="">(.*?)</a>']
        title = tools.get_info(info, title, allow_repeat = True)
        title = ''.join(title)
        title = tools.del_html_tag(title)

        video_url = ['<a href="(.*?)" onclick=.*?; class="">']
        video_url = tools.get_info(info, video_url, allow_repeat = True)
        video_url = ''.join(video_url)

        comment_count = ['<span class="pl">\((\d*?)人评价\)</span>']
        comment_count = tools.get_info(info, comment_count, allow_repeat = True)
        comment_count = ''.join(comment_count)
        comment_count = int(comment_count) if comment_count else 0

        release_time = '<p class="pl">(\d{4}-\d{2}-\d{2}).*?</p>'
        release_time = tools.get_info(info, release_time, allow_repeat=True)
        release_time = ''.join(release_time)

        image_url = '<img src="(.*?)" alt=".*?" class=""/>'
        image_url = tools.get_info(info, image_url, allow_repeat=True)
        image_url = ''.join(image_url)

        content = '<p class="pl">(.*?)</p>'
        content = tools.get_info(info, content, allow_repeat=True)
        content = ''.join(content)

        contained_key, contained_key_count = base_parser.get_contained_key(title, content,
                                                                           remark['search_keyword1'],
                                                                           remark['search_keyword2'], remark['search_keyword3'])
        log.debug('''
        标题:     %s
        内容:     %s
        评论数    %d
        视频地址  %s
        图片地址  %s
        发布时间  %s
        关键字：  %s
        关键字数：%d
        ''' % (title, content, comment_count, video_url, image_url, release_time, contained_key, contained_key_count))

        if not contained_key:
            continue

        base_parser.add_content_info('VA_content_info', SITE_ID, url = video_url, title = title, content = content, image_url = image_url, comment_count = comment_count, release_time = release_time, keyword = contained_key, keyword_count = contained_key_count, task_id = remark['task_id'])

    base_parser.update_url('VA_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    url_info = {
        "_id": "589d621fea18a921b077763b",
        "remark": {
            "search_keyword1": [
                "速度与激情"
            ],
            "search_keyword2": [],
            "search_keyword3": []
        },
        "status": 0,
        "site_id": 10007,
        "depth": 0,
        "url": "https://movie.douban.com/subject_search?start=0&search_text=速度与激情&cat=1002"
    }
    parser(url_info)