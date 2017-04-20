import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re

# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = 'luzhou'


# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'op_site_info'
    url = "http://www.luzhou.gov.cn/"

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.luzhou.gov.cn/"
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
        elif re.match("&#xD;&#xA", url):
            regex = '.*?(/GovPublicInfo.+?000)'
            new_url = tools.get_info(url, regex)
            new_url = new_url[0]
            new_url = 'http://www.luzhou.gov.cn' + new_url
        else:
            new_url = 'http://www.luzhou.gov.cn' + url
        base_parser.add_url('op_urls', website_id, new_url, depth + 1)

    # 取当前页的文章信息
    # 标题
    regexs = '<h2 class="title">(.*?)</h2>'
    title = tools.get_info(html, regexs)
    title = title and title[0] or ''
    title = tools.del_html_tag(title)

    #时间
    regexs = '<span>发布时间：(.*?)</span>'
    release_time = tools.get_info(html, regexs)
    release_time = release_time and release_time[0] or ''
    release_time = tools.del_html_tag(release_time)

    #文章来源
    regexs = '<span>文章来源：(.*?)</span>'
    origin = tools.get_info(html, regexs)
    origin = origin and origin[0] or ''
    origin = tools.del_html_tag(origin)

    #点击数
    regexs = '<span>点击数.*?src="(.*?)"></script>'
    times_script_url = tools.get_info(html, regexs)
    times_script_url = ''.join(times_script_url)
    times_script_url = 'http://www.luzhou.gov.cn' + times_script_url
    watched_count_html, request = tools.get_html_by_requests(times_script_url)
    regexs = '\'(\d*?)\''
    watched_count = tools.get_info(watched_count_html, regexs)
    watched_count = watched_count and watched_count[0] or ''
    watched_count = tools.del_html_tag(watched_count)

    # 内容
    regexs = ['<div class="conTxt">(.*?)</div>']
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
             ''' % (depth+1, title, source_url, release_time, origin, watched_count, content))

    if content and title:
        base_parser.add_op_info('op_content_info', website_id, url=source_url, title=title, release_time=release_time, origin=origin,
                                watched_count=watched_count, content=content)

    # 更新source_url为done
    base_parser.update_url('op_urls', source_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    depth = 1
    url = 'http://www.luzhou.gov.cn/'
    html, request =tools.get_html_by_requests(url)
    urls = tools.get_urls(html)
    #print(urls)
    for url in urls:
        if not re.match("luzhou", url):
            print(url)
        #     base_parser.add_url('op_urls', 1, url, depth + 1)
        # if re.match("&#xD;&#xA", url):
        #     regex = '.*?(/GovPublicInfo.+?000)'
        #     url = tools.get_info(url, regex)
        #     url = url[0]
        #     url = 'http://www.luzhou.gov.cn' + url
        #     base_parser.add_url('op_urls', 1, url, depth + 1)
        # else:
        #     url = 'http://www.luzhou.gov.cn' + url
        #     base_parser.add_url('op_urls', 1, url, depth + 1)

        #     url = 'http://www.luzhou.gov.cn'+url
        # if url.find('luzhou'):
        #     print(url)






