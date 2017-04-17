import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance

# 必须定义 网站id
SITE_ID = 5
# 必须定义 网站名
NAME = '搜狐'

FIT_URLS = [
    'news.sohu.com', 'mil.sohu.com', 'cul.sohu.com', 'view.sohu.com',
    'sport.sohu.com', 'bussiness.sohu.com', 'it.sohu.com'
]

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'article_site_info'
    url = "http://www.cctv.com/"

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.sohu.com/"
    base_parser.add_url('article_urls', SITE_ID, url)

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
        base_parser.update_url('article_urls', source_url, Constance.EXCEPTION)
        return

    # 判断中英文
    regex = '[\u4e00-\u9fa5]+'
    chinese_word = tools.get_info(html, regex)
    if not chinese_word:
        base_parser.update_url('article_urls', source_url, Constance.EXCEPTION)
        return

    urls = tools.get_urls(html)
    fit_url = tools.fit_url(urls, FIT_URLS)
    for url in fit_url:
        # log.debug('url = ' + url)
        base_parser.add_url('article_urls', website_id, url, depth + 1)


    # 取当前页的文章信息
    # 标题

    regexs = '<h1.*?>(.*?)</h1>'
    title = tools.get_info(html, regexs)
    title = title and title[0] or ''
    title = tools.del_html_tag(title)
    # 内容
    regexs = ['<div class="content clear clearfix".*?>(.*?)</div>',
              '<div class="box_con".*?>(.*?)<div class="edit clearfix"',
              '<div class="show_text">(.*?)</div>',
              '<div class="text">.*?<hr class="nonehr">',
              '<div itemprop="article_body">(.*?)<div style="display:none;">',
              '<article>(.*?)</article>']

    content = tools.get_info(html, regexs)
    content = content and content[0] or ''
    content = tools.del_html_tag(content)

    log.debug('''
                depth     = %d
                url       = %s
                title     = %s
                content   = %s
             '''%(depth+1, source_url, title, content))

    if content and title:
        base_parser.add_article_info('article_text_info', website_id, source_url, title, content)

    # 更新source_url为done
    base_parser.update_url('article_urls', source_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    url = "http://www.cctv.com/"
    html = tools.get_html_by_urllib(url)
    regex = '<ul class="nav gwnav2">(.*?)</tbody></table></li>'
    urls_html = tools.get_info(html, regex)
    urls = tools.get_urls(urls_html)
    for url in urls:
        print(url)
    #pass




