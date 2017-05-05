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
    table = 'WWA_search_app_site_info'
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

    keywords = parser_params['keywords']

    def inner_add_url(url):
        html = tools.get_html_by_urllib(url)
        regex = '<input type="hidden" class="total-page" value="(\d*?)" />'
        pages = tools.get_info(html, regex)
        #print(pages)
        pages = pages[0]
        if pages:
            pages = int(pages)
            for i in range(1, pages + 1):
                new_url = url+'%d' % i
                base_parser.add_url('WWA_search_app_urls', SITE_ID, new_url)

    for keyword in keywords:
        url = 'http://shouji.baidu.com/s?wd=%s' % keyword +'&data_type=app&f=header_software%40input#page'
        inner_add_url(url)


# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_urllib(root_url)
    regex = '<div class="app">(.*?)</li>'
    infos = tools.get_info(html, regex)
    for info in infos:
        try:
            image_url = '<img src="(.*?)" alt=".*?" />'
            image_url = tools.get_info(info, image_url)
            #image_url = ''.join(image_url)

            title = '<div class="top">(.*?)</a>'
            title = tools.get_info(info, title)
            title = ''.join(title)
            title = tools.del_html_tag(title)

            download_count = '<span class="download-num">(.*?)</span>次下载</em>'
            download_count = tools.get_info(info, download_count)
            download_count = ''.join(download_count)

            software_size = '<span class="size">(.*?)</span>'
            software_size = tools.get_info(info, software_size)
            software_size = ''.join(software_size)

            app_url = 'data_url="(.*?)"'
            app_url = tools.get_info(info, app_url)
            app_url = ''.join(app_url)

            url = '<a target="_blank" href="(.*?)">'
            url = tools.get_info(info, url)
            url = ''.join(url)
            url = 'http://shouji.baidu.com'+url
            app_html = tools.get_html_by_urllib(url)

            tag = '<span class="version">版本: (.*?)</span>'
            tag = tools.get_info(app_html, tag)
            tag = ''.join(tag)

            summary = ['<p class="content content_hover">(.*?)<span class="occupied">',
                       '<p class="content">(.*?)</p>' ]
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

            language = '中文'

            log.debug('''
                       标题:            %s
                       原文url:         %s
                       简介:            %s
                       评分:            %.1f
                       app下载的url:    %s
                       图片url:         %s
                       大小:            %s
                       版本:            %s
                       平台:            %s
                       下载次数:         %s
                       语言:            %s
                       ''' % (
                title, url, summary, score, app_url, image_url, software_size, tag, platform,
                download_count, language))
        except Exception as e:
            log.error(e)

        base_parser.add_WWA_search_app_info('WWA_search_app_content_info', site_id, url, title=title,
                                 summary=summary, score=score, app_url=app_url, image_url=image_url,
                                 software_size=software_size, tag=tag, platform=platform,
                                 download_count=download_count, language=language,sensitive_id='')

    base_parser.update_url('WWA_search_app_urls', root_url, Constance.DONE)

    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)
if __name__ == '__main__':
    keyword = '重庆'
    def inner_add_url(url):
        html = tools.get_html_by_urllib(url)
        regex = '<input type="hidden" class="total-page" value="(\d*?)" />'
        pages = tools.get_info(html, regex)
        print(pages)
        pages = pages[0]
        if pages:
            pages = int(pages)
            for i in range(1, pages + 1):
                new_url = url+'%d' % i
                base_parser.add_url('WWA_search_app_urls', SITE_ID, new_url)


    url = 'http://shouji.baidu.com/s?wd=%s' % keyword +'&data_type=app&f=header_software%40input#page'
    inner_add_url(url)


