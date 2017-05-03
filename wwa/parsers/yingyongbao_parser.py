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
    table = 'WWA_search_app_site_info'
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

    keywords = parser_params['keyword']

    def inner_add_url(url, keyword):
        while url:
            html_json = tools.get_json_by_requests(url)
            json_value = tools.get_json_value(html_json, 'obj.pageNumberStack')
            hasNext = tools.get_json_value(html_json, 'obj.hasNext')
            if hasNext:
                url = 'http://sj.qq.com/myapp/searchAjax.htm?kw=%s&pns='%keyword + json_value +'&sid=0'
                base_parser.add_url('WWA_search_app_urls', SITE_ID, url)
                continue
            else:
                break

    for keyword in keywords:
        url = 'http://sj.qq.com/myapp/searchAjax.htm?kw=%s&pns=0=&sid=0' % keyword
        inner_add_url(url, keyword)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html_json = tools.get_json_by_requests(root_url)
    html_json = tools.dumps_json(html_json)
    json_values = tools.get_json_value(html_json, 'obj.items')
    for json_value in json_values:
        try:
            url = tools.get_json_value(json_value, 'pkgName')
            url = 'http://sj.qq.com/myapp/detail.htm?apkName=' + url

            title = tools.get_json_value(json_value, 'appDetail.appName')

            author = tools.get_json_value(json_value, 'appDetail.authorName')

            icon_url = tools.get_json_value(json_value, 'appDetail.iconUrl')
            icon_url = icon_url.split()
            image_url = tools.get_json_value(json_value, 'appDetail.images')
            image_url = ','.join(icon_url + image_url)

            update_info = tools.get_json_value(json_value, 'appDetail.newFeature')

            tag = tools.get_json_value(json_value, 'appDetail.versionName')

            summary = tools.get_json_value(json_value, 'appDetail.description')

            app_url = tools.get_json_value(json_value, 'appDetail.apkUrl')

            release_time = tools.get_json_value(json_value, 'appDetail.apkPublishTime')
            release_time = int(release_time)
            release_time = tools.timestamp_to_date(release_time)

            score = tools.get_json_value(json_value, 'appDetail.averageRating')
            score = round(float(score), 1)

            software_size = tools.get_json_value(json_value, 'appDetail.fileSize')
            software_size = str(round(float(software_size) / 1024 / 1024, 1))+'MB'

            download_count = tools.get_json_value(json_value, 'appDetail.appDownCount')

            platform = 'android'

            language = '中文'

            log.debug('''
                       标题:            %s
                       原文url:         %s
                       简介:            %s
                       更新:            %s
                       评分:            %.1f
                       作者:            %s
                       app下载的url:    %s
                       图片url:         %s
                       大小:            %s
                       版本:            %s
                       平台:            %s
                       下载次数:        %s
                       发布时间:        %s
                       语言             %s
                       ''' % (
                title, url, summary, update_info, score, author, app_url, image_url, software_size, tag, platform,
                download_count, release_time, language))

        except Exception as e:
            log.error(e)

        base_parser.add_WWA_search_app_info('WWA_search_app_content_info', site_id, url, title = title,
                         summary = summary, update_info = update_info, score = score, author=author, app_url = app_url, image_url = image_url,
                         software_size = software_size, tag = tag, platform = platform,
                         download_count = download_count, release_time = release_time, language = language, sensitive_id = '')

    base_parser.update_url('WWA_search_app_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    # url = 'http://sj.qq.com/myapp/searchAjax.htm?kw=重庆&pns=0=&sid=0'
    # html_json = tools.get_json_by_requests(url)
    # html_json = tools.dumps_json(html_json)
    # json_values = tools.get_json_value(html_json, 'obj.items')
    # for json_value in json_values:
    #
    #     url = tools.get_json_value(json_value, 'pkgName')
    #     url = 'http://sj.qq.com/myapp/detail.htm?apkName='+url
    #
    #     title = tools.get_json_value(json_value, 'appDetail.appName')
    #
    #     author = tools.get_json_value(json_value, 'appDetail.authorName')
    #
    #     images_url = tools.get_json_value(json_value, 'appDetail.iconUrl')
    #     images_url = images_url.split()
    #     image_url = tools.get_json_value(json_value, 'appDetail.images')
    #     image_url = images_url + image_url
    #
    #     update_info = tools.get_json_value(json_value, 'appDetail.newFeature')
    #
    #     tag = tools.get_json_value(json_value, 'appDetail.versionName')
    #
    #     summary = tools.get_json_value(json_value, 'appDetail.description')
    #
    #     app_url = tools.get_json_value(json_value, 'appDetail.apkUrl')
    #
    #     release_time = tools.get_json_value(json_value, 'appDetail.apkPublishTime')
    #     release_time = int(release_time)
    #     release_time = tools.timestamp_to_date(release_time)
    #
    #     score = tools.get_json_value(json_value, 'appDetail.averageRating')
    #     score = round(float(score), 1)
    #
    #     software_size = tools.get_json_value(json_value, 'appDetail.fileSize')
    #     software_size = round(float(software_size)/1024/1024, 1)
    #
    #     download_count = tools.get_json_value(json_value, 'appDetail.appDownCount')
    #
    #     platform = 'android'
    #
    #     language = '中文'
    #
    #     log.debug('''
    #                        标题:            %s
    #                        原文url:         %s
    #                        简介:            %s
    #                        更新:            %s
    #                        评分:            %.1f
    #                        作者:            %s
    #                        app下载的url:    %s
    #                        图片url:         %s
    #                        大小:            %s
    #                        版本:            %s
    #                        平台:            %s
    #                        下载次数:        %s
    #                        发布时间:        %s
    #                        语言             %s
    #                        ''' % (
    #         title, url, summary, update_info, score, author, app_url, image_url, software_size, tag, platform,
    #         download_count, release_time, language))
    keyword = '重庆'


    def inner_add_url(url, keyword):
        while url:
            html_json = tools.get_json_by_requests(url)
            print('************')
            json_value = tools.get_json_value(html_json, 'obj.pageNumberStack')
            hasNext = tools.get_json_value(html_json, 'obj.hasNext')
            if hasNext:
                url = 'http://sj.qq.com/myapp/searchAjax.htm?kw=%s&pns='%keyword + json_value +'&sid=0'
                print(url)
                #base_parser.add_url('WWA_search_app_urls', SITE_ID, url)
                continue
            else:
                break


    url1 = 'http://sj.qq.com/myapp/searchAjax.htm?kw=%s&pns=0=&sid=0' % keyword

    inner_add_url(url1, keyword)