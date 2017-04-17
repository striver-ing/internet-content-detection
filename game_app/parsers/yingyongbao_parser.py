import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import base.constance as Constance
import utils.tools as tools
from utils.log import log
import time

# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '应用宝'

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'GameApp_site_info'
    url = 'http://sj.qq.com'
    address = '广东省广州市 电信'
    ip = '14.17.18.181'
    base_parser.add_website_info(table, site_id, url, name, address = address, ip = ip)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))


    def inner_add_url(url, remark):
        if not base_parser.add_url('GameApp_urls', SITE_ID, url, remark=remark):
            base_parser.update_url('GameApp_urls', url, Constance.TODO)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=147'
    inner_add_url(url, Constance.休闲益智)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=121'
    inner_add_url(url, Constance.网络游戏)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=149'
    inner_add_url(url, Constance.飞行射击)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=144'
    inner_add_url(url, Constance.动作冒险)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=151'
    inner_add_url(url, Constance.体育竞技)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=148'
    inner_add_url(url, Constance.棋牌中心)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=153'
    inner_add_url(url, Constance.经营策略)

    url = 'http://sj.qq.com/myapp/category.htm?orgame=2&categoryId=146'
    inner_add_url(url, Constance.角色扮演)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_urllib(root_url)
    regex = '<div class="app-info clearfix">(.*?)</li>'
    infos = tools.get_info(html, regex)
    for info in infos:
        title = 'target="_blank" class="name ofh">(.*?)</a>'
        title = tools.get_info(info, title, allow_repeat= True)
        title = ''.join(title)

        url = '<a href="(.*?)" target="_blank" class="app-info-icon">'
        url = tools.get_info(info, url)
        url = ''.join(url)
        url = 'http://sj.qq.com/myapp/' + url

        app_html = tools.get_html_by_urllib(url)
        del_app_html_tag = tools.del_html_tag(app_html)

        app_info = '<div class="det-app-data-info">(.*?)</div>'
        app_info = tools.get_info(app_html, app_info, allow_repeat = True)
        summary = app_info[0]

        update_info = app_info[1] if len(app_info) > 1 else ''

        score = '<div class="com-blue-star-num">(.*?)分</div>'
        score = tools.get_info(app_html, score)
        score = float(''.join(score))

        author = '开发商：(.*?)查看权限需'
        author = tools.get_info(del_app_html_tag, author)
        author = ''.join(author)

        app_url = 'ex_url="(.*?)"'
        app_url = tools.get_info(info, app_url)
        app_url = ''.join(app_url)

        image_url = '<img data-original="(.*?)" .*?>'
        image_url = tools.get_info(info, image_url)
        image_urls = '<img data-src=\'(.*?)\' src="" id=\'.*?\'/>'
        image_urls = tools.get_info(app_html, image_urls)
        image_url = ','.join(image_url + image_urls)

        classify_id = remark

        software_size = '<span class="size">(.*?)</span>'
        software_size = tools.get_info(info, software_size)
        software_size = ''.join(software_size)

        tag = '版本号：(.*?)更新时间'
        tag = tools.get_info(del_app_html_tag, tag)
        tag = ''.join(tag)

        platform = 'android'

        download_count= '<div class="det-ins-num">(.*?)下载</div>'
        download_count = tools.get_info(app_html, download_count)
        download_count = ''.join(download_count)

        release_time = '<div class="det-othinfo-data" id="J_ApkPublishTime" data-apkPublishTime="(\d*?)"></div>'
        release_time = tools.get_info(app_html, release_time)
        release_time = int(''.join(release_time))
        x = time.localtime(release_time)
        release_time = time.strftime("%Y-%m-%d", x)

        language = ''

        log.debug('''
                   标题:            %s
                   原文url:         %s
                   简介:            %s
                   更新:            %s
                   评分:            %.1f
                   作者:            %s
                   app下载的url:    %s
                   图片url:         %s
                   分类:            %s
                   大小:            %s
                   版本:            %s
                   平台:            %s
                   下载次数:        %s
                   发布时间:        %s
                   语言             %s
                   ''' % (
            title, url, summary, update_info, score, author, app_url, image_url, classify_id, software_size, tag, platform,
            download_count, release_time, language))

        base_parser.add_game_app_info('GameApp_content_info', site_id, url, title = title,
                     summary = summary, update_info = update_info, score = score, author = author, app_url = app_url, image_url = image_url,
                     classify_id = classify_id , software_size = software_size, tag = tag, platform = platform,
                     download_count = download_count, release_time = release_time, language = language, sensitive_id = ''
        )

    base_parser.update_url('GameApp_urls', root_url, Constance.DONE)

if __name__ == '__main__':

    url = 'http://sj.qq.com/myapp/search.htm?kw=%E4%B8%80%E5%8F%91%E4%B8%8D%E6%AD%A2'
    url_info = {
        "status": 0,
        "site_id": 1,
        'url': url,
        "remark": {
            "search_keyword3": [],
            "search_keyword2": [],
            "search_keyword1": []
        },
        "depth": 0,
        "_id": "58a2cec55344652a48ab2f5a"
    }
    parser(url_info)

