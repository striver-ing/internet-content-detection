import sys
sys.path.append('../../')
# 访问503
import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re
# 必须定义 网站id
SITE_ID = 13
# 必须定义 网站名
NAME = 'luzhoutianli'


# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'op_site_info'
    url = "http://www.luzhoutianli.com/"

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.luzhoutianli.com/"
    base_parser.add_url('op_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    website_id = url_info['site_id']
    description = url_info['remark']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie':'__cfduid=d17ca6a5def98d8c14f73dcee28042c7f1492065760',
        'Host': 'www.luzhoutianli.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

    }

    html, request = tools.get_html_by_requests(source_url, headers=headers, code='gb2312')
    if html == None:
        base_parser.update_url('op_urls', source_url, Constance.EXCEPTION)
        return
    urls = tools.get_urls(html)
    for url in urls:
        #new_url = tools.get_full_url('http://www.luzhoutianli.com', url)
        if re.match("http", url):
            new_url = url
        elif re.match('/', url):
            new_url = 'http://www.luzhoutianli.com' + url
        else:
            new_url = 'http://www.luzhoutianli.com/' + url
        base_parser.add_url('op_urls', website_id, new_url, depth + 1)



    # 取当前页的文章信息
    # 标题
    #
    # print(html)
    regexs = '<strong class="NameTxt"><a >(.*?)</a></strong>.*?</td>'
    title = tools.get_info(html, regexs)
    if len(title) > 1:
        title = title[1]
    else:
        title = title and title[0] or ''
        title = tools.del_html_tag(title)

    # 时间
    regexs = ' <span class="FC_Time">时间：(.*?)</span>'
    release_time = tools.get_info(html, regexs)
    release_time = release_time and release_time[0] or ''

    # 作者
    regexs = '<span class="FC_Time">作者：(.*?)</span>'
    author = tools.get_info(html, regexs)
    author = release_time and author[0] or ''
    author = tools.del_html_tag(author)
    # #print(author)
    #
    # 文章来源
    regexs = '来源：(.*?)&nbsp'
    origin = tools.get_info(html, regexs)
    origin = origin and origin[0] or ''
    origin = tools.del_html_tag(origin)

    # 点击数
    regexs = '评论：<span class="style1">(\d*?)</span>'
    watched_count = tools.get_info(html, regexs)
    watched_count = watched_count and watched_count[0] or ''
    watched_count = tools.del_html_tag(watched_count)

    # 内容
    regexs = ['<div class="articleDetails">.*?</script>(.*?)<td class="MoBodyR"']
    content = tools.get_info(html, regexs)
    # print(content[0])
    content = content and content[0] or ''
    content = tools.del_html_tag(content)

    log.debug('''
                        depth               = %s
                        url                 = %s
                        title               = %s
                        release_time        = %s
                        author              = %s
                        content             = %s
                     ''' % (depth , source_url, title, release_time, author, content))

    if content and title:
        base_parser.add_op_info('op_content_info', website_id, url=source_url, title=title,
                                release_time=release_time, author=author, content=content)

    # 更新source_url为done
    base_parser.update_url('op_urls', source_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    header={
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	    'Accept-Encoding':'gzip, deflate, sdch',
	    'Accept-Language':'zh-CN,zh;q=0.8',
	    'Cache-Control':'max-age=0',
	    'Connection':'keep-alive',
	    #'Cookie':'__cfduid=d17ca6a5def98d8c14f73dcee28042c7f1492065760',
	    'Host':'www.luzhoutianli.com',
	    'Upgrade-Insecure-Requests':'1',
	    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

    }
    # depth = 1
    # #
    # url = "http://www.luzhoutianli.com/luzhotuianli/item_14830908_709539.html"
    # html = tools.get_html_by_urllib(url, headers=header, code='gb2312')
    # print(html)
    # regexs = '<strong class="NameTxt"><a >(.*?)</a></strong>.*?</td>'
    # title = tools.get_info(html, regexs)
    # if len(title)>1:
    #     title = title[1]
    # else:
    #     title = title and title[0] or ''
    #     title = tools.del_html_tag(title)
    #
    # # 时间
    # regexs = ' <span class="FC_Time">时间：(.*?)</span>'
    # release_time = tools.get_info(html, regexs)
    # release_time = release_time and release_time[0] or ''
    #
    # # 作者
    # regexs = '<span class="FC_Time">作者：(.*?)</span>'
    # author = tools.get_info(html, regexs)
    # author = release_time and author[0] or ''
    # author = tools.del_html_tag(author)
    # # #print(author)
    # #
    # #文章来源
    # regexs = '来源：(.*?)&nbsp'
    # origin = tools.get_info(html, regexs)
    # origin = origin and origin[0] or ''
    # origin = tools.del_html_tag(origin)
    #
    # #点击数
    # regexs = '评论：<span class="style1">(\d*?)</span>'
    # watched_count = tools.get_info(html, regexs)
    # watched_count = watched_count and watched_count[0] or ''
    # watched_count = tools.del_html_tag(watched_count)
    #
    # # 内容
    # regexs = ['<div class="articleDetails">.*?</script>(.*?)<td class="MoBodyR"']
    # content = tools.get_info(html, regexs)
    # #print(content[0])
    # content = content and content[0] or ''
    # content = tools.del_html_tag(content)
    #
    # log.debug('''
    #                 depth               = %s
    #                 url                 = %s
    #                 title               = %s
    #                 release_time        = %s
    #                 author              = %s
    #                 content             = %s
    #              ''' % (depth+1, url, title, release_time, author, content))
    # # #urls = tools.get_urls(html)
    # # #print(urls)
    # # # for url in urls:
    # # #     print(url)
    # #     #base_parser.add_url('article_urls', SITE_ID, url)
    #
    url_info ={
    "_id" : "58f855acea18a92568e3c9bb",
    "remark" : "",
    "status" : 2,
    "depth" : 0,
    "site_id" : 13,
    "url" : "http://www.luzhoutianli.com/luzhotuianli/item_14830908_709539.html"
    }

    parser(url_info)

