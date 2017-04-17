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
# 必须定义 网站名
NAME = '百度手机助手'

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'GameApp_site_info'
    url = 'http://shouji.baidu.com'
    icp = '030173'
    address = '北京市 百度网讯科技电信节点'
    ip = '180.149.131.211'
    base_parser.add_website_info(table, site_id, url, name,icp = icp, address = address, ip = ip)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    def inner_add_url(url, remark):
        html = tools.get_html_by_urllib(url)
        regex = '<li><span></span><a  href="(.*?)">.*?</a></li>'
        infos = tools.get_info(html, regex)
        for info in infos:
            info = ''.join(info)
            type_url = 'http://shouji.baidu.com' + info
            type_html = tools.get_html_by_urllib(type_url)
            page_count = '<div class="pager">.*">(.*?)</a>.*?<li class="next">'
            page_count = tools.get_info(type_html, page_count)
            page_count = ''.join(page_count)
            if not page_count:
                page_count = '1'
            page_count = int(page_count)
            for page in range(1, page_count + 1):
                url = type_url + 'list_%d.html' % page
                if not base_parser.add_url('GameApp_urls', SITE_ID, url, remark= remark):
                    base_parser.update_url('GameApp_urls', url, Constance.TODO)

    inner_add_url('http://shouji.baidu.com/game/401/', Constance.休闲益智)
    inner_add_url('http://shouji.baidu.com/game/board_102_200/', Constance.网络游戏)
    inner_add_url('http://shouji.baidu.com/game/403/', Constance.飞行射击)
    inner_add_url('http://shouji.baidu.com/game/406/', Constance.赛车竞速)
    inner_add_url('http://shouji.baidu.com/game/405/', Constance.体育竞技)
    inner_add_url('http://shouji.baidu.com/game/407/', Constance.体育竞技)
    inner_add_url('http://shouji.baidu.com/game/408/', Constance.经营策略)
    inner_add_url('http://shouji.baidu.com/game/402/', Constance.角色扮演)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    # html = tools.get_html_by_urllib(root_url)
    # regex = '<li><span></span><a  href="(.*?)">.*?</a></li>'
    # infos = tools.get_info(html, regex)
    # for info in infos:
    #     info = ''.join(info)
    #     type_url ='http://shouji.baidu.com'+info
    #     type_html = tools.get_html_by_urllib(type_url)
    #     page_count = '<div class="pager">.*">(.*?)</a>.*?<li class="next">'
    #     page_count = tools.get_info(type_html, page_count)
    #     page_count = ''.join(page_count)
    #     if not page_count:
    #         page_count = '1'
    #     page_count = int(page_count)
    #     for page in range(1, page_count+1):
    #         logourl = type_url+'list_%d.html'% page
    #       print('***', logourl)

    html = tools.get_html_by_urllib(root_url)
    regex = '<div class="app-detail">(.*?)</li>'
    infos = tools.get_info(html, regex)
    for info in infos:
        image_url = '<img data-default=".*?" class="imagefix" src="(.*?)" alt=".*?">'
        image_url = tools.get_info(info, image_url)
        #image_url = ''.join(image_url)

        title = '<p class="name">(.*?)</p>'
        title = tools.get_info(info, title)
        title = ''.join(title)

        download_count = '<span class="down">(.*?)下载</span>'
        download_count = tools.get_info(info, download_count)
        download_count = ''.join(download_count)

        software_size = '<span class="size">(.*?)</span>'
        software_size = tools.get_info(info, software_size)
        software_size = ''.join(software_size)

        app_url = 'data_url="(.*?)"'
        app_url = tools.get_info(info, app_url)
        app_url = ''.join(app_url)

        url = '<img data-docid="(.*?)"'
        url = tools.get_info(info, url)
        url = ''.join(url)
        url = 'http://shouji.baidu.com/game/'+url+'.html'
        app_html = tools.get_html_by_urllib(url)

        tag = '<span class="version">版本: (.*?)</span>'
        tag = tools.get_info(app_html, tag)
        tag = ''.join(tag)

        summary = '<p class="content">(.*?)</p>'
        summary = tools.get_info(app_html, summary)
        summary = ''.join(summary)
        if not summary:
            summary = '<p class="content content_hover">(.*?)<span class="occupied">'
            summary = tools.get_info(app_html, summary)
            summary = ''.join(summary)

        image_urls = 'class="imagefix" src="(.*?)" alt=".*?-应用截图" /></li>'
        image_urls = tools.get_info(app_html, image_urls)
        image_url = ','.join(image_url+image_urls)

        score = '<span class="star-percent" style="width:(\d*?)%"></span>'
        score = tools.get_info(app_html, score)
        score = float(''.join(score))
        score = round(float(score/20),1)

        platform = 'android'

        classify_id = remark

        language = ''

        log.debug('''
                   标题:            %s
                   原文url:         %s
                   简介:            %s
                   评分:            %.1f
                   app下载的url:    %s
                   图片url:         %s
                   分类:            %s
                   大小:            %s
                   版本:            %s
                   平台:            %s
                   下载次数:         %s
                   语言:            %s
                   ''' % (
            title, url, summary, score, app_url, image_url, classify_id, software_size, tag, platform,
            download_count, language))

        base_parser.add_game_app_info('GameApp_content_info', site_id, url, title=title,
                                     summary=summary, score=score, app_url=app_url, image_url=image_url,
                                     classify_id=classify_id, software_size=software_size, tag=tag, platform=platform,
                                     download_count=download_count, language=language,
                                     sensitive_id=''
                                     )

    base_parser.update_url('GameApp_urls', root_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    url = 'http://shouji.baidu.com/game/401'
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
        "_id": "58a2cec55344652asd"
    }
    parser(url_info)


