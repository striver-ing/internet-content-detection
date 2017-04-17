import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import base.constance as Constance
import utils.tools as tools
from utils.log import log
import time

# 必须定义 网站id
SITE_ID = 4
DATA_TYPE = 2
# 必须定义 网站名
NAME = '动漫啦漫画'

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WP_site_info'
    url = 'www.dongman.la'
    address = '陕西西安 百度云加速节点'
    ip = '117.34.14.232'
    base_parser.add_website_info(table, site_id, url, name, address, ip)


# @tools.run_safe_model(__name__)
# 必须定义 添加根url
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = 'http://www.dongman.la/'
    html = tools.get_html_by_urllib(url)
    regex = '<ul class="home_w">.*?<li class="navbg"><a href="http://www.dongman.la/">首页</a></li>(.*?)<li><a href="http://www.dongman.la/cili/">下载</a></li>'
    type_cartoon = tools.get_info(html, regex)
    regex = '<li ><a href="(.*?)">.*?</a></li>'
    infos = tools.get_info(type_cartoon, regex)
    for info_url in infos:
        page_count = '<a class="end" href=".*?">(\d*?)</a>'
        info_url_html = tools.get_html_by_urllib(info_url)
        page_count = tools.get_info(info_url_html, page_count)
        if not page_count:
            page_count = '<a class="num" href=".*?">(\d*?)</a> <a class="next" href=".*?">'
            page_count = tools.get_info(info_url_html, page_count)
        page_count = int(''.join(page_count))
        for page in range(1, page_count + 1):
            ever_page_url = info_url + '%d.html' % page
            type_cartoon_html = tools.get_html_by_urllib(ever_page_url)
            regex = '<div class="dmbottom">(.*?)</div>'
            ever_cartoon_html = tools.get_info(type_cartoon_html, regex)
            title = '<a target="_blank" title=".*?" href=".*?">(.*?)</a>'
            title = tools.get_info(ever_cartoon_html, title)
            # 原文url
            url = '<a target="_blank" title=".*?" href="(.*?)">.*?</a>'
            url = tools.get_info(ever_cartoon_html, url)
            for i in range(0, min(len(title), len(url))):
                base_parser.add_url('WP_urls', SITE_ID, url[i], remark=title[i], status=Constance.TODO)


# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))
    depth = url_info['depth']

    if depth == 0:
        parser_content_info(url_info)
    elif depth == 1:
        parser_episode_info(url_info)


def parser_content_info(url_info):
    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    cartoon_book_html = tools.get_html_by_urllib(root_url)

    #标题
    title = remark

    #漫画类型
    article_type = '<dd>漫画类型：(.*?)</dd>'
    article_type = tools.get_info(cartoon_book_html, article_type)
    article_type = ''.join(article_type)
    article_type = tools.del_html_tag(article_type)

    # 网站url
    url = root_url

    # 集数
    episodes_html = '<div class="box act">(.*?)</ul>'
    episodes = tools.get_info(cartoon_book_html, episodes_html)
    episodes = '<ul>.*?<li><a href=".*?" target="_blank" title=".*?">第(\d*?)话</a></li>'
    episodes = tools.get_info(cartoon_book_html, episodes)
    episodes = ''.join(episodes)
    if not episodes:
        episodes = '<ul>.*?<li><a href=".*?" target="_blank" title=".*?">全(\d*?)话</a></li>'
        episodes = tools.get_info(cartoon_book_html, episodes)
        episodes = ''.join(episodes)
    if not episodes:
        episodes = '<ul>.*?<li><a href=".*?" target="_blank" title=".*?">全(\d*?)卷</a></li>'
        episodes = tools.get_info(cartoon_book_html, episodes)
        episodes = ''.join(episodes)

    # 作者
    author = '<dd>漫画作者：.*?<span>(.*?)</span>'
    author = tools.get_info(cartoon_book_html, author)
    author = ''.join(author)

    # 最近更新日期
    release_time = '<dd>最近更新：(.*?)</dd>'
    release_time = tools.get_info(cartoon_book_html, release_time)
    release_time = ''.join(release_time)

    # 贴图
    image_url = '<dl>.*?<dt><a href=".*?" title=".*?"><img src="(.*?)" .*?</a><span></span></dt>'
    image_url = tools.get_info(cartoon_book_html, image_url)
    image_url = ''.join(image_url)

    # 播放次数
    watched_count = '<dd>总浏览：<span>(\d*?)次</span></dd>'
    watched_count = tools.get_info(cartoon_book_html, watched_count)
    watched_count = int(''.join(watched_count))

    # 是否完结
    is_finished = '<dd>漫画状态：(.*?)</dd>'
    is_finished = tools.get_info(cartoon_book_html, is_finished)
    is_finished = ''.join(is_finished)
    if is_finished == '完结':
        is_finished = 2 # '完结'
    else:
        is_finished = 0 #'未完结'

    #简介
    abstract = '漫画简介：(.*?)</p>'
    abstract = tools.get_info(cartoon_book_html, abstract)
    abstract = ''.join(abstract)
    abstract = tools.del_html_tag(abstract)

    log.debug('''
            书名:          %s
            作品类型:       %s
            网站url:       %s
            集数:          %s
            作者:          %s
            最近更新日期:    %s
            贴图:          %s
            播放次数:       %s
            是否完结:       %s
            简介:          %s
            ''' % (
            title, article_type, url, episodes, author, release_time,
            image_url, watched_count, is_finished,  abstract))

    content_id = base_parser.add_wp_content_info('WP_content_info', SITE_ID, title=title, article_type=article_type, url=url,
                                        episodes=episodes, author=author, release_time=release_time, image_url=image_url,
                                        watched_count=watched_count, is_finished=is_finished, abstract=abstract, data_type=DATA_TYPE)

    html = tools.get_html_by_urllib(root_url)
    cartoon_catalog = '漫画章节目录(.*?)</ul>'
    cartoon_catalog = tools.get_info(html, cartoon_catalog)
    regex = '<li><a href="(.*?)" target="_blank" title=".*?">.*?</a></li>'
    catalog_counts = tools.get_info(cartoon_catalog, regex)
    for chapter_url in catalog_counts:
        base_parser.add_url('WP_urls', site_id, chapter_url, depth = depth+1, remark = content_id, status=Constance.TODO)

    base_parser.update_url('WP_urls', root_url, status=Constance.DONE)

def parser_episode_info(url_info):
    chapter_url = url_info['url']
    # depth = url_info['depth']
    # site_id = url_info['site_id']
    remark = url_info['remark']

    chapter_html = tools.get_html_by_urllib(chapter_url)
    page_count = '<span>No.1/All.(\d*?)</span>'
    page_count = tools.get_info(chapter_html, page_count)
    page_count = int(''.join(page_count))
    image_url= []
    title = '<p>(.*?)第\d*?页</p>'
    title = tools.get_info(chapter_html, title)
    for page in range(1, page_count+1):
        try:
            ever_page_url = chapter_url[:chapter_url.rfind('-')+1]+'%d.html'%page
            #每一章节漫画的图片
            ever_page_html = tools.get_html_by_urllib(ever_page_url)
            image_urls = '<div class="manhuawrap">.*?<img src="(.*?)"'
            image_urls = tools.get_info(ever_page_html, image_urls)
            image_url = image_url+image_urls
            if not image_url:
                image_urls = '<img src="(.*?)" class="imgbox" alt=".*?">'
                image_urls = tools.get_info(ever_page_html, image_urls)
                image_url = image_url + image_urls
        except Exception as e:
            pass
    image_url = ','.join(image_url)
    title = ''.join(title)

    log.debug('''
        章节名:      %s
        图片地址:     %s
        content_id: %s
        '''% (title, image_url, str(remark)))

    base_parser.add_wp_content_episode_info('WP_content_episode_info', image_url=image_url,title = title, content_id=remark, data_type=DATA_TYPE)
    base_parser.update_url('WP_urls', chapter_url, status=Constance.DONE)
if __name__ == '__main__':
    # chapter_url = 'http://www.dongman.la/manhua/1305/5316/46049-1.html'
    # chapter_html = tools.get_html_by_urllib(chapter_url)
    # page_count = '<span>No.1/All.(\d*?)</span>'
    # page_count = tools.get_info(chapter_html, page_count)
    # page_count = int(''.join(page_count))
    # image_url = []
    # for page in range(1, page_count + 1):
    #     try:
    #         ever_page_url = chapter_url[:chapter_url.rfind('-') + 1] + '%d.html' % page
    #         # 每一章节漫画的图片
    #         ever_page_html = tools.get_html_by_urllib(ever_page_url)
    #         # image_urls = '<div class="manhuawrap">.*?<img src="(.*?)"'
    #         # image_urls = tools.get_info(ever_page_html, image_urls)
    #         # image_url = image_url + image_urls
    #         title = '<p>(.*?)第\d*?页</p>'
    #         title = tools.get_info(ever_page_html, title)
    #         title = ''.join(title)
    #         print(title)
    #         # if not image_url:
    #         #     image_urls = '<img src="(.*?)" class="imgbox" alt=".*?">'
    #         #     image_urls = tools.get_info(ever_page_html, image_urls)
    #         #     image_url = image_url + image_urls
    #     except Exception as e:
    #         pass
    # #image_url = ','.join(image_url)
    # print(title)
    # #            pass

    parser_episode_info(url_info = {'url':'http://www.dongman.la/manhua/1311/7020/126746-1.html', 'remark':1})



