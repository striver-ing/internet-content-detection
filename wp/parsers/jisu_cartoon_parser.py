import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import base.constance as Constance
import utils.tools as tools
from utils.log import log
import time

# 必须定义 网站id
SITE_ID = 2
DATA_TYPE = 2
# 必须定义 网站名
NAME = '极速漫画'

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WP_site_info'
    url = 'http://www.1kkk.com'
    icp = '09075556号-4'
    address = '山东省滨州市 电信'
    ip = '222.174.239.197'
    base_parser.add_website_info(table, site_id, url, name, icp, address, ip)


@tools.run_safe_model(__name__)
# 必须定义 添加根url
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))


    url = 'http://www.1kkk.com'
    html = tools.get_html_by_urllib(url)
    regex = '<li class="">.*?href="(.*?)" target="_parent"><span>.*?</span></a></li>'
    infos = tools.get_info(html, regex)
    china_cartoon = ['//manhua-china//']
    infos = infos + china_cartoon
    for info in infos:
        info = info[:-1]
        url = 'http://www.1kkk.com' + info
        url_fenye = url + '-p'
        urls = url + '-p1'
        html = tools.get_html_by_urllib(urls)
        page_count = '\.\.\.<a href=".*?">(.*?)</a><a href=".*?">下一页</a>'
        page_count = tools.get_info(html, page_count)
        if not page_count:
            while url:
                html = tools.get_html_by_urllib(url)
                url = '<div id="search_fy">.*<a href="(.*?)" style=\'padding: 5px 20px; margin: 0 8px;\'> 下一页 </a>'
                url = tools.get_info(html, url)
                url = ''.join(url)
                url = 'http://www.1kkk.com' + url
                base_parser.add_url('WP_urls', SITE_ID, url)
        else:
            page_count = int(''.join(page_count))
            for page in range(1, page_count + 1):
                url = url_fenye + '%d' % page
                base_parser.add_url('WP_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    if depth == 0:
        parser_content_info(url_info)
    elif depth == 1:
        pass
        # parser_episode_info(url_info)

def parser_content_info(url_info):
    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '__AdinAll_SSP_NUID=d4318e92a4dae757b9d4241f57ace4b0; haiyunpmp=HAIYUNX_k7m7ak8t4zddl697hhqq41jor1488864538106; CNZZDATA1258752048=1751527004-1488859919-http%253A%252F%252Fwww.1kkk.com%252F%7C1488876119; CNZZDATA1261430601=459775185-1488863643-http%253A%252F%252Fwww.1kkk.com%252F%7C1488874443; __AdinAll_SSP_OUID=0ba6a4175ae772f4fa049bcdf7fc194b; ComicHistoryitem_zh=History=35432,636244901583363257,463473,3,0,0,0,1|7754,636244977018267071,463269,1,0,0,0,30|2683,636245007578612277,31527,4,0,0,0,1|16665,636245018277285283,463495,1,0,0,0,4|22870,636245022269790825,456706,1,0,0,0,23|15056,636245023943234214,156737,1,0,0,0,1&ViewType=0; DM5_MACHINEKEY=442b1f17-ffdb-46c5-bb99-87db97158318; CNZZDATA30046992=cnzz_eid%3D1290885111-1489023474-http%253A%252F%252Fwww.1kkk.com%252F%26ntime%3D1489023474; CNZZDATA1257133111=2078584318-1489022105-http%253A%252F%252Fwww.1kkk.com%252F%7C1489022105; CNZZDATA1258751996=591455200-1489022085-http%253A%252F%252Fwww.1kkk.com%252F%7C1489022085; CNZZDATA1258880908=661964868-1489022021-http%253A%252F%252Fwww.1kkk.com%252F%7C1489022021; __utmt=1; __utma=1.192736317.1489027059.1489027059.1489027059.1; __utmb=1.1.10.1489027059; __utmc=1; __utmz=1.1489027059.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); isAdult=1',
        'Host': 'www.1kkk.com',
        'If-Modified-Since': tools.get_current_date(),
        'If-None-Match': '636246523187509449-0---0-2_20-10',
        'Referer': 'http://www.1kkk.com/manhua369/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    html = tools.get_html_by_urllib(root_url)
    regex = '<li><p class="cover"><a href="(.*?)">'
    infos = tools.get_info(html, regex)
    for info in infos:
        url = 'http://www.1kkk.com'+info
        cartoon_book_html = tools.get_html_by_requests(url, headers = headers)

        image_url = '<div class="sy_k1 z"><img src="(.*?)" /></div>'
        image_url = tools.get_info(cartoon_book_html, image_url)
        image_url = ''.join(image_url)

        title = '<h1>(.*?)</h1>'
        title = tools.get_info(cartoon_book_html, title)
        title = ''.join(title)

        watched_count = '<li class="z k200">阅读人次： <font class="z075">(.*?)</font></li>'
        watched_count = tools.get_info(cartoon_book_html, watched_count)
        watched_count = ''.join(watched_count)

        author = '<li>漫画作者：<a href=".*?">(.*?)</a>'
        author = tools.get_info(cartoon_book_html, author)
        author = ''.join(author)

        release_time = '<li>更新时间： <font class=".*?">(.*?)</font></li>'
        release_time = tools.get_info(cartoon_book_html, release_time)
        release_time = ''.join(release_time)

        article_type = '<li>漫画类别：<a href=".*?">(.*?)</a> </li>'
        article_type = tools.get_info(cartoon_book_html, article_type)
        article_type = ''.join(article_type)

        #简介
        abstract = '<li class="mt10 z555" style="height:auto;"><b class="z075">.*?</b>(.*?)</li>'
        abstract = tools.get_info(cartoon_book_html, abstract)
        abstract = ''.join(abstract)
        abstract = tools.del_html_tag(abstract)

        episodes = '<ul class="sy_nr1 cplist_ullg">.*?<li><a href=".*?" class="tg">.?(\d*?).?</a>'
        episodes = tools.get_info(cartoon_book_html, episodes)
        episodes = episodes[0] if episodes else ''
        #episodes = episodes and episodes[0] or ''


        is_finished = '<li class=".*?">漫画状态： <font class=".*?">(.*?)</font></li>'
        is_finished = tools.get_info(cartoon_book_html, is_finished)
        is_finished = ''.join(is_finished)

        ever_cartoon_urls = '<ul class="sy_nr1 cplist_ullg">.*?<ul class="sy_nr1 cplist_ullg">(.*?)</ul>'
        ever_cartoon_urls = tools.get_info(cartoon_book_html, ever_cartoon_urls)
        if not ever_cartoon_urls:
            ever_cartoon_urls = '<ul class="sy_nr2 cplist_ullg" id="charpernew_ls">.*?<ul class="sy_nr1 cplist_ullg">(.*?)</ul>'
            ever_cartoon_urls = tools.get_info(cartoon_book_html, ever_cartoon_urls)
        regex = '<a href="(.*?)" class="tg">.*?</a>'
        urls = tools.get_info(ever_cartoon_urls, regex)
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

        base_parser.add_wp_content_info('WP_content_info', SITE_ID, title=title, article_type=article_type, url=url,
                                        episodes=episodes, author=author, release_time=release_time, image_url=image_url,
                                        watched_count=watched_count, is_finished=is_finished, abstract=abstract, data_type=DATA_TYPE)
        #
        # if content_id:
        #     # 解析每集的url 存urls表
        #     for url in urls:
        #         url = 'http://www.1kkk.com'+url
        #         url_info={
        #                 "status": 0,
        #                 "site_id": 1,
        #                 'url': url,
        #                 "remark": content_id,
        #                 "depth": 1
        #         }
        #         parser(url_info)
        #         base_parser.add_url('WP_urls', url, 1, remark = content_id)
    base_parser.update_url('WP_urls', root_url, Constance.DONE)

# def parser_episode_info(url_info):
#     root_url = url_info['url']
#     depth = url_info['depth']
#     site_id = url_info['site_id']
#     remark = url_info['remark']
#     html = tools.get_html_by_urllib(root_url)
#     page_count = '总<span>(\d*?)</span>页'
#     page_count = tools.get_info(html, page_count)
#     page_count = int(''.join(page_count))
#     img_url = []
#     title = []
#     for page in range(1,page_count+1):
#         url = root_url+'#ipg%d' % page
#         img_html = tools.get_html_by_urllib(url)
#         #print('********',img_html)
#         # img_urls = '<img src="(.*?)"'
#         # img_urls = tools.get_info(img_html,img_urls)
#         # img_url = img_urls+img_url
#         # print('--------123',img_url)

        # titles = '<h1>(.*?)<font class="zf40">'
        # titles = tools.get_info(img_html, titles)
        # title = ''.join(title)
#
# if __name__ == '__main__':
        # def inner_add_url(url, page_url):
        #     html = tools.get_html_by_urllib(url)
        #     page_count = '\.\.\.<a href=".*?">(.*?)</a><a href=".*?">下一页</a>'
        #     page_count = tools.get_info(html, page_count)
        #     page_count = int(''.join(page_count))
        #     for page in range(1,page_count+1):
        #         url = 'http://www.1kkk.com/manhua-new-p%d/' % page

        # url = 'http://www.1kkk.com'
        # html = tools.get_html_by_urllib(url)
        # regex = '<li class="">.*?href="(.*?)" target="_parent"><span>.*?</span></a></li>'
        # infos = tools.get_info(html, regex)
        # china_cartoon = ['//manhua-china//']
        # infos = infos+china_cartoon
        # for info in infos:
        #     info = info[:-1]
        #     url = 'http://www.1kkk.com'+info
        #     url_fenye = url+'-p'
        #     urls = url+'-p1'
        #     html = tools.get_html_by_urllib(urls)
        #     page_count = '\.\.\.<a href=".*?">(.*?)</a><a href=".*?">下一页</a>'
        #     page_count = tools.get_info(html, page_count)
        #     if not page_count:
        #         while url:
        #             html = tools.get_html_by_urllib(url)
        #             url = '<div id="search_fy">.*<a href="(.*?)" style=\'padding: 5px 20px; margin: 0 8px;\'> 下一页 </a>'
        #             url = tools.get_info(html, url)
        #             url = ''.join(url)
        #             url = 'http://www.1kkk.com'+url
        #             url_info = {
        #                 "status": 0,
        #                 "site_id": 1,
        #                 'url': url,
        #                 "remark": {
        #                     "search_keyword3": [],
        #                     "search_keyword2": [],
        #                     "search_keyword1": []
        #                 },
        #                 "depth": 0,
        #                 "_id": "58a2cec55344652asd"
        #             }
        #             parser(url_info)
        #     else:
        #         page_count = int(''.join(page_count))
        #         for page in range(1,page_count+1):
        #             url = url_fenye+'%d' % page
        #             #print(url)
        #             url_info = {
        #                 "status": 0,
        #                 "site_id": 1,
        #                 'url': url,
        #                 "remark": {
        #                     "search_keyword3": [],
        #                     "search_keyword2": [],
        #                     "search_keyword1": []
        #                 },
        #                 "depth": 0,
        #                 "_id": "58a2cec55344652asd"
        #             }
        #             parser(url_info)

