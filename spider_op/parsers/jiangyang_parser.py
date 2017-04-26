import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re
# 必须定义 网站id
SITE_ID = 2
# 必须定义 网站名
NAME = 'jiangyang'


# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'op_site_info'
    url = "http://www.jiangyang.gov.cn/"

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.jiangyang.gov.cn/"
    base_parser.add_url('op_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    website_id = url_info['site_id']
    description = url_info['remark']

    html, request = tools.get_html_by_requests(source_url)
    if html == None:
        base_parser.update_url('op_urls', source_url, Constance.EXCEPTION)
        return

    urls = tools.get_urls(html)
    for url in urls:
        if re.match("http", url):
            new_url = url
        else:
            new_url = 'http://www.jiangyang.gov.cn/template/default/'+url
        base_parser.add_url('op_urls', website_id, new_url, depth + 1)

    # 取当前页的文章信息
    # 标题

    regexs = '<div class="tit">(.*?)</div>'
    title = tools.get_info(html, regexs)
    if not title:
        regexs = '<h1>(.*?)</h1>'
        title = tools.get_info(html, regexs)
    title = title and title[0] or ''
    title = tools.del_html_tag(title)

    #时间
    regexs = '<label>(.*?)</label>'
    release_time = tools.get_info(html, regexs)
    release_time = release_time and release_time[0] or ''
    if release_time:
        release_time = tools.format_date(release_time)
    if not release_time:
        regexs = '<span class="time">发布时间：(.*?)</span><span class="source"></span></p>'
        release_time = tools.get_info(html, regexs)
        release_time = release_time and release_time[0] or ''
        #release_time = tools.format_date(release_time)

    #文章来源
    regexs = '<label>来源：(.*?)</label>'
    origin = tools.get_info(html, regexs)
    origin = origin and origin[0] or ''
    origin = tools.del_html_tag(origin)

    # 内容
    regexs = ['<div class="content" id="nr" style="">(.*?)</div>']
    content = tools.get_info(html, regexs)
    content = content and content[0] or ''
    content = tools.del_html_tag(content)
    if not content:
        regexs = '<p style="text-align: center;"(.*?)</div>.*?<div class="content">'
        content = tools.get_info(html, regexs)
        content = content and content[0] or ''
        content = tools.del_html_tag(content)

    log.debug('''
                depth               = %s
                url                 = %s
                title               = %s
                release_time        = %s
                origin              = %s
                content             = %s
             ''' % (depth+1, source_url, title, release_time, origin, content))

    if content and title:
        base_parser.add_op_info('op_content_info', website_id, url=source_url, title=title,
                                release_time=release_time, origin=origin, content=content)

    # 更新source_url为done
    base_parser.update_url('op_urls', source_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    depth=1
    url = "http://www.jiangyang.gov.cn"
    html, request = tools.get_html_by_requests(url)
    # urls = tools.get_urls(html)
    # for url in urls:
    #     if re.match("http", url):
    #         new_url = url
    #     else:
    #         print(url)
    #         new_url = 'http://www.jiangyang.gov.cn/template/default/' + url

    # regexs = '<div class="tit">(.*?)</div>'
    # title = tools.get_info(html, regexs)
    # if not title:
    #     regexs = '<h1>(.*?)</h1>'
    #     title = tools.get_info(html, regexs)
    # title = title and title[0] or ''
    # title = tools.del_html_tag(title)
    #
    # # 时间
    regexs = '<label>(.*?)</label>'
    release_time = tools.get_info(html, regexs)
    release_time = release_time and release_time[0] or ''
    if release_time:
        release_time = tools.format_date(release_time)
    if not release_time:
        regexs = '<span class="time">发布时间：(.*?)</span><span class="source"></span></p>'
        release_time = tools.get_info(html, regexs)
        release_time = release_time and release_time[0] or ''
        #print(release_time)
        release_time = tools.format_date(release_time)
    #
    # # 文章来源
    # regexs = '<label>来源：(.*?)</label>'
    # origin = tools.get_info(html, regexs)
    # origin = origin and origin[0] or ''
    # origin = tools.del_html_tag(origin)
    #
    # # 内容
    # regexs = ['<div class="content" id="nr" style="">(.*?)</div>']
    # content = tools.get_info(html, regexs)
    # content = content and content[0] or ''
    # content = tools.del_html_tag(content)
    # if not content:
    #     regexs = '<p style="text-align: center;">(.*?)</div>.*?<div class="content">'
    #     content = tools.get_info(html, regexs)
    #     content = content and content[0] or ''
    #     content = tools.del_html_tag(content)
    # log.debug('''
    #                depth               = %s
    #                url                 = %s
    #                title               = %s
    #                release_time        = %s
    #                origin              = %s
    #                content             = %s
    #             ''' % (depth + 1, url, title, release_time, origin, content))
    # urls = tools.get_urls(html)
    # for url in urls:
    #     if re.match("http", url):
    #         url = url
    #     else:
    #         url = 'http://www.jiangyang.gov.cn/'+url
    #         print(url)
    #urls = tools.get_urls(html)
    #print(urls)
    # for url in urls:
    #     print(url)
        #base_parser.add_url('article_urls', SITE_ID, url)





