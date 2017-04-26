import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re

# 必须定义 网站id
SITE_ID = 9
# 必须定义 网站名
NAME = 'sichuanpolice'


# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'op_site_info'
    url = "http://www.scpolicec.edu.cn/"

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.scpolicec.edu.cn/"
    base_parser.add_url('op_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    website_id = url_info['site_id']
    description = url_info['remark']

    html, request = tools.get_html_by_requests(source_url, code='gb2312')

    regexs = 'charset=(.*?)"'
    code = tools.get_info(html, regexs)
    code = code and code[0] or 'gb2312'
    html, request = tools.get_html_by_requests(source_url, code=code)
    if html == None:
        base_parser.update_url('op_urls', source_url, Constance.EXCEPTION)
        return

    urls = tools.get_urls(html)

    for url in urls:
        if re.match("http", url):
            new_url = url
        elif re.match('/', url):
            new_url = 'http://www.scpolicec.edu.cn' + url
        else:
            new_url = 'http://www.scpolicec.edu.cn/' + url
        base_parser.add_url('op_urls', website_id, new_url, depth + 1)


    # 取当前页的文章信息
    # 标题

    regexs = ['<div class="main_title">(.*?)<div class="top_about">', '<h1>(.*?)</h1>', '<title>(.*?)</title>',
              '<div class="contentPageTitle">(.*?)</div>']
    title = tools.get_info(html, regexs)
    title = title and title[0] or ''
    title = tools.del_html_tag(title)

    #时间
    regexs = ['<div class="top_about"><a editurl=\'.*?\'>(.*?)</a>','<small>时间:</small>(.*?)<small>',
              '<h2><span>更新时间：(.*?)</span>']
    release_time = tools.get_info(html, regexs)
    release_time = release_time and release_time[0] or ''
    if not release_time:
            regexs = '</a> 发布时间：(.*?) 点击数'
            release_time = tools.get_info(html, regexs)
            release_time = release_time and release_time[0] or ''
            release_time = tools.format_date(release_time)


    # #作者
    regexs = ['作者:(.*?) 【']
    author = tools.get_info(html, regexs)
    author = author and author[0] or ''
    #author = tools.del_html_tag(author)

    #文章来源
    regexs = '来源:(.*?)</a>'
    origin = tools.get_info(html, regexs)
    origin = origin and origin[0] or ''
    origin = tools.del_html_tag(origin)

    # #点击数
    regexs = ['浏览:<font id="hits">(\d*?)</font>次', '点击数：(\d*?)&#xA;发表时间']
    watched_count = tools.get_info(html, regexs)
    watched_count = watched_count and watched_count[0] or ''
    watched_count = tools.del_html_tag(watched_count)

    # 内容
    regexs = ['<p style="text-align: center;">(.*?)</table>', '<div class="contentPageContent">(.*?)</table>'
              '<div id="endtext" style="width:900px;">(.*?)<div id="pages"></div>',
              '<div id="articleContnet">(.*?)<div class="page_css">']
    content = tools.get_info(html, regexs)
    content = content and content[0] or ''
    content = tools.del_html_tag(content)

    log.debug('''
                    depth               = %s
                    url                 = %s
                    title               = %s
                    release_time        = %s
                    author              = %s
                    origin              = %s
                    watched_count       = %s
                    content             = %s
                 ''' % (depth, source_url, title, release_time, author, origin, watched_count, content))

    if content and title:
        base_parser.add_op_info('op_content_info', website_id,url=source_url, title=title, release_time=release_time, author=author,
                                origin=origin, watched_count=watched_count, content=content)
    # 更新source_url为done
    base_parser.update_url('op_urls', source_url, Constance.DONE)

if __name__ == '__main__':
    # depth=1
    url = "http://scjyzsjy.ncss.org.cn/job/index"
    html, request = tools.get_html_by_requests(url, code='gb2312')

    regexs = 'charset=(.*?)"'
    code = tools.get_info(html, regexs)
    code = code and code[0] or 'gb2312'
    html, request = tools.get_html_by_requests(url, code=code)
    print(code)

    regexs = '<div class="main_title">(.*?)<div class="top_about">'
    title = tools.get_info(html, regexs)
    title = title and title[0] or ''
    title = tools.del_html_tag(title)

    # 时间
    regexs = ['<div class="top_about"><a editurl=\'.*?\'>(.*?)</a>']
    release_time = tools.get_info(html, regexs)
    release_time = release_time and release_time[0] or ''
    if not release_time:
        regexs = '<small>时间:</small>(.*?)<small>'
        release_time = tools.get_info(html, regexs)
        release_time = release_time and release_time[0] or ''
        if not release_time:
            regexs = '</a> 发布时间：(.*?) 点击数'
            release_time = tools.get_info(html, regexs)
            release_time = release_time and release_time[0] or ''
            release_time = tools.format_date(release_time)
    #
    # #作者
    regexs = ['作者:(.*?) 【', '作者：(.*?) 来源']
    author = tools.get_info(html, regexs)
    author = author and author[0] or ''
    # author = tools.del_html_tag(author)

    # # 文章来源
    # regexs = '来源:(.*?)</a>'
    # origin = tools.get_info(html, regexs)
    # origin = origin and origin[0] or ''
    # origin = tools.del_html_tag(origin)
    # #
    # # #点击数
    regexs = ['浏览:<font id="hits">(\d*?)</font>次', '点击数：(\d*?)&#xA;发表时间']
    watched_count = tools.get_info(html, regexs)
    watched_count = watched_count and watched_count[0] or ''
    watched_count = tools.del_html_tag(watched_count)

    # 内容
    regexs = ['<p style="text-align: center;">(.*?)</table>', '<div id="articleContnet">(.*?)<div class="page_css">',
              '<div id="endtext" style="width:900px;">(.*?)<div id="pages"></div>']
    content = tools.get_info(html, regexs)
    content = content and content[0] or ''
    content = tools.del_html_tag(content)

    log.debug('''
                       depth               = %s
                       url                 = %s
                       title               = %s
                       release_time        = %s
                       author              = %s
                       watched_count       = %s
                       content             = %s
                    ''' % (1 + 1, url, title, release_time, author, watched_count, content))
   #  urls = tools.get_urls(html)
   # #print(urls)
   #  for url in urls:
   #      print(url)
        #base_parser.add_url('article_urls', SITE_ID, url)





