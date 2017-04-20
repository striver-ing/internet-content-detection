import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re

# 必须定义 网站id
SITE_ID = 4
# 必须定义 网站名
NAME = 'naxi'


# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'op_site_info'
    url = "http://www.naxi.gov.cn"

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.naxi.gov.cn"
    html, request = tools.get_html_by_requests(url)
    urls = tools.get_urls(html)
    for url in urls:
        base_parser.add_url('op_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    website_id = url_info['site_id']
    description = url_info['remark']

    html = tools.get_html_by_urllib(source_url)
    if html == None:
        base_parser.update_url('op_urls', source_url, Constance.EXCEPTION)
        return

    urls = tools.get_urls(html)

    for url in urls:
        if re.match("http", url):
            new_url = url
        elif re.match("/", url):
            new_url = 'http://www.naxi.gov.cn' + url
        else:
            new_url = 'http://www.naxi.gov.cn/'+url
        base_parser.add_url('op_urls', website_id, new_url, depth + 1)


    # 取当前页的文章信息
    # 标题

    regexs = '<DIV class=news_conent_two_title>(.*?)</DIV>'
    title = tools.get_info(html, regexs)
    title = title and title[0] or ''
    title = tools.del_html_tag(title)

    #时间
    regexs = '<SPAN>日期：(.*?)</SPAN>'
    release_time = tools.get_info(html, regexs)
    release_time = release_time and release_time[0] or ''
    release_time = tools.del_html_tag(release_time)

    # #作者
    # regexs = '<span>作者：(.*?)</span>'
    # author = tools.get_info(html, regexs)
    # author = author and author[0] or ''
    # author = tools.del_html_tag(author)

    #文章来源
    regexs = '<SPAN>来源：(.*?)</SPAN>'
    origin = tools.get_info(html, regexs)
    origin = origin and origin[0] or ''
    origin = tools.del_html_tag(origin)

    # #点击数
    regexs = '<SPAN>点击数：(\d*?)</SPAN>'
    watched_count = tools.get_info(html, regexs)
    watched_count = watched_count and watched_count[0] or ''
    watched_count = tools.del_html_tag(watched_count)

    # 内容
    regexs = ['<DIV id=news_conent_two_text class=news_conent_two_text>(.*?)</DIV>']
    content = tools.get_info(html, regexs)
    content = content and content[0] or ''
    content = tools.del_html_tag(content)

    log.debug('''
                depth               = %s
                url                 = %s
                title               = %s
                release_time        = %s
                origin              = %s
                watched_count       = %s
                content             = %s
             ''' % (depth+1, source_url, title, release_time, origin, watched_count, content))

    if content and title:
        base_parser.add_op_info('op_content_info', website_id, url= source_url, title=title, release_time=release_time,
                                origin=origin, watched_count=watched_count, content=content)

    # 更新source_url为done
    base_parser.update_url('op_urls', source_url, Constance.DONE)

if __name__ == '__main__':
    url = "http://www.naxi.gov.cn/"
    html = tools.get_html_by_urllib(url)
    urls = tools.get_urls(html)
    for url in urls:
        if re.match("http", url):
            new_url = url
        elif re.match("/", url):
            new_url = 'http://www.naxi.gov.cn' + url
        else:
            new_url = 'http://www.naxi.gov.cn/'+url
        print(new_url)
    #urls = tools.get_urls(html)
    #print(urls)
    # for url in urls:
    #     print(url)
        #base_parser.add_url('article_urls', SITE_ID, url)





