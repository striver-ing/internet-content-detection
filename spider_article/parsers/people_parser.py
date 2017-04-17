import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance

# 必须定义 网站id
SITE_ID = 3
# 必须定义 网站名
NAME = '人民网'
STOP_URLS = [
    'tv.people.com.cn', 'travel.people.com.cn', 'mooc.people.com.cn', 'dengshi.people.com.cn',
    'jiaju.people.com.cn', 't.people.com.cn', 'pic.people.com.cn', 'caipiao.people.com.cn',
    'hongmu.people.com.cn', 'game.people.com.cn' , 'fashion.people.com.cn' ,'shipin.people.com.cn',
    'homea.people.com.cn', 'book.people.com.cn' , 'ent.people.com.cn' ,'health.people.com.cn',
    'auto.people.com.cn', 'art.people.com.cn'
]

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'article_site_info'
    url = "http://www.people.com.cn/"

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.people.com.cn/"
    base_parser.add_url('article_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    website_id = url_info['site_id']
    description = url_info['remark']

    html = tools.get_html_by_urllib(source_url, code = 'GB2312')
    if html == None:
        base_parser.update_url('article_urls', source_url, Constance.EXCEPTION)
        return

    # 判断中英文
    regex = '[\u4e00-\u9fa5]+'
    chinese_word = tools.get_info(html, regex)
    if not chinese_word:
        base_parser.update_url('article_urls', source_url, Constance.EXCEPTION)
        return

    # 取当前页面的全部url
    urls = tools.get_urls(html, STOP_URLS)

    # 过滤掉外链接 添加到数据库
    fit_url = tools.fit_url(urls, "people.com.cn")
    for url in fit_url:
        # log.debug('url = ' + url)
        base_parser.add_url('article_urls', website_id, url, depth + 1)


    # 取当前页的文章信息
    # 标题

    regexs = '<h1>(.*?)</h1>'
    title = tools.get_info(html, regexs)
    title = title and title[0] or ''
    title = tools.replace_str(title, '&.*?;')
    # 内容
    regexs = ['div class="box_pic"></div>(.*?)<div class="box_pic"></div>',
              '<div class="content clear clearfix">(.*?)<div class="edit clearfix">',
              '<div class="show_text">(.*?)<div class="edit">'
              ]

    content = tools.get_info(html, regexs)
    content = content and content[0] or ''

    content = tools.del_html_tag(content)

    log.debug('''
                    depth     =  %d
                    source_url = %s
                    title     =  %s
                    content   =  %s
                 ''' % (depth, source_url, title, content))

    if content and title:
        base_parser.add_article_info('article_text_info', website_id, source_url, title, content)

    # 更新source_url为done
    base_parser.update_url('article_urls', source_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    # url = 'http://www.cctv.com/'
    # url_info = {'_id':'11', 'url': url, 'site_id': '582ea577350b654b67dc855ac8', 'depth': 0, 'remark': ''}
    # parser(url_info)
    pass

