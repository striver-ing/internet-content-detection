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
# 必须定义 网站名
NAME = '安卓市场'

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME

    table = 'GameApp_site_info'
    url = 'http://apk.hiapk.com/'
    icp = '1101858'
    address = '福建省福州市 电信'
    ip = '59.56.100.22'
    base_parser.add_website_info(table, site_id, url, name, icp = icp, address = address, ip = ip)



# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    def inner_add_url(base_url, remark, page_count):
        for i in range(1, page_count):
            url = base_url % i
            if not base_parser.add_url('GameApp_urls', SITE_ID, url, remark = remark):
                base_parser.update_url('GameApp_urls', url, Constance.TODO)

    inner_add_url('http://apk.hiapk.com/games/Casual?sort=5&pi=%d', Constance.休闲益智, 51)
    inner_add_url('http://apk.hiapk.com/games/BrainAndPuzzle?sort=5&pi=%d', Constance.休闲益智, 51)
    inner_add_url('http://apk.hiapk.com/games/OnlineGames?sort=5&pi=%d', Constance.网络游戏, 51)
    inner_add_url('http://apk.hiapk.com/games/Shooting?sort=5&pi=%d', Constance.飞行射击, 51)
    inner_add_url('http://apk.hiapk.com/games/Racing?sort=5&pi=%d', Constance.动作冒险, 51)
    inner_add_url('http://apk.hiapk.com/games/Sports?sort=5&pi=%d', Constance.体育竞技, 51)
    inner_add_url('http://apk.hiapk.com/games/Chess?sort=5&pi=%d', Constance.棋牌中心, 51)
    inner_add_url('http://apk.hiapk.com/games/Strategy?sort=5&pi=%d', Constance.经营策略, 51)
    inner_add_url('http://apk.hiapk.com/games/RolePlaying?sort=5&pi=%d', Constance.角色扮演, 51)
    inner_add_url('http://apk.hiapk.com/games/Racing?sort=5&pi=%d', Constance.速度激情, 51)
    inner_add_url('http://apk.hiapk.com/games/Simulation?sort=5&pi=%d', Constance.经营养成, 51)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_urllib(root_url)
    regex = '<li class="list_item">(.*?)</li>'
    infos = tools.get_info(html, regex)
    for info in infos:
        title = '<span class="list_title font14_2"><a href=".*?">(.*?)</a>'
        title = tools.get_info(info, title, allow_repeat= True)
        title = ''.join(title)

        url = '<div class="left".*?<a href="(.*?)">'
        url = tools.get_info(info, url)
        url = ''.join(url)
        url = 'http://apk.hiapk.com' + url

        app_html = tools.get_html_by_urllib(url)

        summary = '<pre id="softIntroduce">(.*?)</pre>'
        summary = tools.get_info(app_html, summary)
        summary = ''.join(summary)

        update_info = '<pre class="soft_imprint_font">(.*?)</pre>'
        update_info = tools.get_info(app_html, update_info)
        update_info = ''.join(update_info)

        score = '<div class="star_num">(.*?)</div>'
        score = tools.get_info(app_html, score)
        score = ''.join(score)
        score = tools.del_html_tag(score)
        score = float(score.strip())

        author = '<span class="font14 left">作者：</span>.*?<span class="d_u_line">(.*?)</span>'
        author = tools.get_info(app_html, author)
        author = ''.join(author)

        app_url = 'button_bg button_1 right_mt.*?<a href="(.*?)" rel="nofollow"> '
        app_url = tools.get_info(info, app_url)
        app_url = ''.join(app_url)
        app_url = 'http://apk.hiapk.com' + app_url

        image_url = '<img width="72px" height="72px" src="(.*?)" />'
        image_url = tools.get_info(info, image_url)
        images_url = '<a rel="prettyPhoto\[gallery\]" href="(.*?)">'
        images_url = tools.get_info(app_html, images_url)
        image_url = ','.join(image_url+images_url)

        classify_id = remark

        tag = '<span class="list_version font12">\((.*?)\)</span>'
        tag = tools.get_info(info, tag)
        tag = ''.join(tag)

        platform = '<span class="font14 detailMiniSdk d_gj_line left">(.*?)固件版本</span>'
        platform = tools.get_info(app_html, platform)
        platform = ''.join(platform)
        platform = 'Android'+platform

        software_size = '<span id="appSize" class="font14">(.*?)</span>'
        software_size = tools.get_info(app_html, software_size)
        software_size = ''.join(software_size)

        download_count = '<span class="font14">热度：</span>.*?<span class="font14">(.*?)热度</span>'
        download_count = tools.get_info(app_html, download_count)
        download_count = ''.join(download_count)

        release_time = '<span class="push_time">(.*?)发布</span>'
        release_time = tools.get_info(info, release_time)
        release_time = ''.join(release_time)

        app_html = tools.del_html_tag(app_html)
        language = '语言：(.*?)固件'
        language = tools.get_info(app_html, language)
        language = ''.join(language)

        log.debug('''
                   标题:            %s
                   原文url:         %s
                   简介:            %s
                   更新信息          %s
                   评分:            %.1f
                   作者:            %s
                   app下载的url:    %s
                   图片url:         %s
                   分类:            %s
                   大小:            %s
                   版本:            %s
                   平台:            %s
                   下载次数:         %s
                   发布时间:         %s
                   语言:            %s
                   ''' % (
            title, url, summary, update_info, score, author, app_url, image_url, classify_id, software_size, tag, platform,
            download_count, release_time, language))
        base_parser.add_game_app_info('GameApp_content_info', site_id, url, title = title, update_info = update_info,
                                     summary = summary, score = score, author = author, app_url = app_url, image_url = image_url,
                                     classify_id = classify_id, software_size = software_size, tag = tag, platform = platform,
                                     download_count = download_count, release_time = release_time, language = language,
                                     sensitive_id = ''
                                     )

    base_parser.update_url('GameApp_urls', root_url, Constance.DONE)


    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    # for i in range(1,51):
    #     url = 'http://apk.hiapk.com/games/OnlineGames?sort=5&pi=%d'% i
    #     url_info = {
    #         "status": 0,
    #         "site_id": 1,
    #         'url': url,
    #         "remark": {
    #             "search_keyword3": [],
    #             "search_keyword2": [],
    #             "search_keyword1": []
    #         },
    #         "depth": 0,
    #         "_id": "58a2cec55344652a48ab2f5a"
    #     }
    #     # parser(url_info)

    #     add_root_url()

    ss = ' sd'
    print(ss.strip())