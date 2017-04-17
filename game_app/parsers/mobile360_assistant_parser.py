import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import base.constance as Constance
import utils.tools as tools
from utils.log import log
import time

# 必须定义 网站id
SITE_ID = 3
# 必须定义 网站名
NAME = '360手机助手'

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'GameApp_site_info'
    url = 'http://zhushou.360.cn/'
    address = '北京市 北京奇虎科技有限公司电信CDN节点'
    ip = '101.199.103.203'
    base_parser.add_website_info(table, site_id, url, name, address = address, ip = ip)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    def inner_add_url(base_url, url, remark):
        html = tools.get_html_by_urllib(base_url)
        regex = 'pg.pageCount = (.*?);'
        page_count = tools.get_info(html, regex, allow_repeat=True)
        page_count = ''.join(page_count)
        page_count = round(float(page_count))
        page_count = int(page_count)
        for i in range(0, page_count+1):
            url = url % i
            if not base_parser.add_url('GameApp_urls', SITE_ID, url, remark=remark):
                base_parser.update_url('GameApp_urls', url, Constance.TODO)

    base_url = 'http://zhushou.360.cn/list/index/cid/100451/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/100451/?page=%d', Constance.网络游戏)

    base_url = 'http://zhushou.360.cn/list/index/cid/101587/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/101587/?page=%d', Constance.角色扮演)

    base_url = 'http://zhushou.360.cn/list/index/cid/19/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/19/?page=%d', Constance.休闲益智)

    base_url = 'http://zhushou.360.cn/list/index/cid/20/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/20/?page=%d', Constance.动作冒险)

    base_url = 'http://zhushou.360.cn/list/index/cid/51/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/51/?page=%d', Constance.体育竞技)

    base_url = 'http://zhushou.360.cn/list/index/cid/52/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/52/?page=%d', Constance.飞行射击)

    base_url = 'http://zhushou.360.cn/list/index/cid/53/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/53/?page=%d', Constance.经营策略)

    base_url = 'http://zhushou.360.cn/list/index/cid/54/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/54/?page=%d', Constance.棋牌中心)

    base_url = 'http://zhushou.360.cn/list/index/cid/102238/?page=1'
    inner_add_url(base_url, 'http://zhushou.360.cn/list/index/cid/102238/?page=%d', Constance.儿童游戏)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_urllib(root_url)
    regex = '<a sid=.*?><img src=.*?></a>(.*?)</li>'
    infos = tools.get_info(html, regex)
    for info in infos:
        title = '<h3>.*?<a sid=".*?" href=".*?">(.*?)</a>.*?</h3>'
        title = tools.get_info(info, title, allow_repeat= True)
        title = ''.join(title)

        url = '<h3><a sid=".*?" href="(.*?)">.*?</a></h3>'
        url = tools.get_info(info, url)
        url = ''.join(url)
        url = 'http://zhushou.360.cn' + url

        app_html = tools.get_html_by_urllib(url)

        summary = '<div class="sdesc clearfix" id="sdesc">(.*?)<div class="base-info">'
        summary = tools.get_info(app_html, summary)
        summary = ''.join(summary)
        # summary = tools.del_html_tag(summary)

        update_info = '<b>【更新内容】</b>(.*?)</div>'
        update_info = tools.get_info(app_html, update_info)
        update_info = ''.join(update_info)
        update_info = tools.del_html_tag(update_info)

        score = '<span class="s-1 js-votepanel">(.*?)<em>分</em></span>'
        score = tools.get_info(app_html, score)
        score = float(''.join(score))
        score = round(score / 2, 1)

        image_url = '<dt><img src="(.*?)".*?</dt>'
        image_url = tools.get_info(app_html, image_url)
        image_urls = '<div id="scrollbar" data-snaps="(.*?)">'
        image_urls = tools.get_info(app_html, image_urls)
        image_url = ','.join(image_url + image_urls)

        author = '<td width="50%"><strong>作者：</strong>(.*?)</td>'
        author = tools.get_info(app_html, author)
        author = ''.join(author)

        app_url = '<a sid=".*?" href=".*?url=(.*?)" class=".*?"></a>'
        app_url = tools.get_info(info, app_url)
        app_url = ''.join(app_url)

        classify_id = remark

        software_size = '<span class="s-3">.*?</span>.*?<span class="s-3">(.*?)</span>'
        software_size = tools.get_info(app_html, software_size)
        software_size = ''.join(software_size)

        tag = '<td><strong>版本：</strong>(.*?)<'
        tag = tools.get_info(app_html, tag)
        tag = ''.join(tag)

        platform = '<td><strong>系统：</strong>(.*?)</td>'
        platform = tools.get_info(app_html, platform)
        platform = ''.join(platform)

        download_count= '<span>(.*?)次下载</span>'
        download_count = tools.get_info(info, download_count)
        download_count = ''.join(download_count)

        release_time = '<td width="50%"><strong>更新时间：</strong>(.*?)</td>'
        release_time = tools.get_info(app_html, release_time)
        release_time = ''.join(release_time)

        language = '<td colspan="2"><strong>语言：</strong>(.*?)</td>'
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

        base_parser.add_game_app_info('GameApp_content_info', site_id, url, title=title,update_info = update_info,
                                     summary=summary, score=score, author=author, app_url=app_url, image_url=image_url,
                                     classify_id=classify_id, software_size=software_size, tag=tag, platform=platform,
                                     download_count=download_count, release_time=release_time, language=language,
                                     sensitive_id=''
                                     )

        base_parser.update_url('GameApp_urls', root_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    url = 'http://zhushou.360.cn/list/index/cid/100451/?page=1'
    html = tools.get_html_by_urllib(url)
    regex = 'pg.pageCount = (.*?);'
    page_count = tools.get_info(html, regex, allow_repeat= True)
    page_count = ''.join(page_count)
    page_count = round(float(page_count))
    page_count = int(page_count)
    for page in range(0,page_count):
        url = 'http://zhushou.360.cn/list/index/cid/102238/?page=%d'% (page+1)
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
            "_id": "58a2cec55344652a48ab2f5asdsf"
        }
        parser(url_info)

