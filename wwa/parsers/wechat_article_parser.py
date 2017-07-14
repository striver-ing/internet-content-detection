# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
from db.mongodb import MongoDB
import base.constance as Constance
from db.oracledb import OracleDB
import time

# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '微信'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'wwa_save_path') + 'wechat/'

oracledb = OracleDB()
mongodb = MongoDB()

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WWA_wechat_site_info'
    url = 'http://weixin.sogou.com/'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    keywords = parser_params['keywords']

    for keyword in keywords:
        if keyword:
            url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_='%keyword
            base_parser.add_url('WWA_wechat_article_url', SITE_ID, url, remark = keyword)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    official_accounts_id = remark

    headers =  {
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Host": "weixin.sogou.com",
        "Cookie": "SUV=1493992505819275; SMYUV=1493992505820875; UM_distinctid=15bd8e481e362-01a3df9ec0e7c3-62101875-ffc00-15bd8e481e41a7; ABTEST=6|1494142883|v1; SNUID=35798DEB8581CA6EBB507B9A8549C894; SUID=B0FC096F2A30990A00000000590ECFA3; JSESSIONID=aaa3JllZJGZGTf7mN4UUv; SUID=9DFC19703108990A00000000590ECFA4; IPLOC=CN5000; weixinIndexVisited=1; sct=2",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "http://weixin.sogou.com/weixin?type=1&s_from=input&query=chongqing&ie=utf8&_sug_=n&_sug_type_="
    }

    # 解析
    html, request = tools.get_html_by_requests(root_url, headers = headers)
    if not html:
        base_parser.update_url('urls', root_url, Constance.EXCEPTION)
        return

    # print(html)
    regex = '<input type=text name="c" value="" placeholder="(.*?)" id="seccodeInput">'
    check_info = tools.get_info(html, regex, fetch_one = True)
    log.debug('取文章链接' + check_info)

    # 公众号信息块
    regex = '<!-- a -->(.*?)<!-- z -->'
    account_block = tools.get_info(html, regex, fetch_one = True)
    # url
    regex = '<a.*?account_name.*?href="(.*?)">'
    account_url = tools.get_info(account_block, regex, fetch_one = True)
    account_url = account_url.replace('&amp;',"&")
    log.debug('account_url = ' + account_url)

    if not account_url:
        base_parser.update_url('urls', root_url, Constance.EXCEPTION)
        return

    headers = {
        "Cache-Control": "max-age=0",
        "Cookie": "sig=h0103501987bd47456233d89945ec9344c0874df4623269ab6dc12a8ec675a0291dcf19d6043325766e",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "http://mp.weixin.qq.com/profile?src=3&timestamp=1494380748&ver=1&signature=fGdbGg2AtWpVljuVN2Gao7KWjc0*v7x97PoqrIsVtzfRn5Zu9zneTBdwP-b7kEdKB*bGRj-TmI*TAPvxy-nVKA==",
        "Upgrade-Insecure-Requests": "1",
        "Host": "mp.weixin.qq.com",
        "If-Modified-Since": "Wed, 10 May 2017 09:45:54 +0800",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch"
    }

    html, request = tools.get_html_by_requests(account_url, headers = headers)
    regex = '<input class="weui_input frm_input" id="input" placeholder="(.*?)" maxlength="4">'
    check_info = tools.get_info(html, regex, fetch_one = True)
    log.debug("取文章详细内容 " + check_info)
    # print(html)

    regex = 'var msgList = (.*?});'
    article_json = tools.get_info(html, regex, fetch_one = True)
    article_json = tools.get_json(article_json)

    article_list = article_json.get('list', {})
    for article in article_list:
        title = tools.get_json_value(article, 'app_msg_ext_info.title')
        is_have = mongodb.find('WWA_wechat_article', {'title' : title})
        if is_have:
            log.debug(title + " 已存在")
            continue

        summary = tools.get_json_value(article, 'app_msg_ext_info.digest')
        image_url = tools.get_json_value(article, 'app_msg_ext_info.cover')

        sexy_image_url = []

        # 下载图片
        local_image_url = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.jpg'
        is_download = tools.download_file(image_url, local_image_url)
        local_image_url = local_image_url if is_download else ''
        sexy_image_url.append(local_image_url)

        article_url = tools.get_json_value(article, 'app_msg_ext_info.content_url')
        article_url = tools.get_full_url('http://mp.weixin.qq.com', article_url)
        article_url = article_url.replace('&amp;',"&")

        release_time = tools.get_json_value(article, 'comm_msg_info.datetime')
        release_time = tools.timestamp_to_date(int(release_time)) if release_time else ''

        content_html, request = tools.get_html_by_requests(article_url, headers = headers)
        regex = '(<div class="rich_media_content " id="js_content">.*?)<script nonce'
        content = tools.get_info(content_html, regex, fetch_one = True)

        # # 取content里的图片 下载图片 然后替换内容中原来的图片地址
        regex = '<img.*?data-src="(.*?)"'
        images = tools.get_info(content, regex)
        for image in images:
            local_image_path = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.' + (image[image.rfind('=') + len('='):] if '=' in image else 'png')
            is_download = tools.download_file(image, local_image_path)
            if is_download:
                content = content.replace(image, local_image_path)
                sexy_image_url.append(local_image_path)
            tools.delay_time(5)

        # 敏感事件
        sensitive_id = ''
        sensitive_event_infos = oracledb.find('select * from tab_mvms_sensitive_event')
        for sensitive_event_info in sensitive_event_infos:
            _id = sensitive_event_info[0]
            keyword1 = sensitive_event_info[3].split(',') if sensitive_event_info[3] else []
            keyword2 = sensitive_event_info[4].split(',') if sensitive_event_info[4] else []
            keyword3 = sensitive_event_info[5].split(',') if sensitive_event_info[5] else []

            if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
                sensitive_id = _id
                break

        # 违规事件
        violate_id = ''
        vioation_knowledge_infos = oracledb.find('select * from tab_mvms_violation_knowledge')
        for vioation_knowledge_info in vioation_knowledge_infos:
            _id = vioation_knowledge_info[0]
            keyword1 = vioation_knowledge_info[2].split(',') if vioation_knowledge_info[2] else []
            keyword2 = vioation_knowledge_info[3].split(',') if vioation_knowledge_info[3] else []
            keyword3 = vioation_knowledge_info[4].split(',') if vioation_knowledge_info[4] else []

            if base_parser.is_violate(title + tools.del_html_tag(content), key1=keyword1, key2=keyword2, key3=keyword3):
                violate_id = _id
                break

        log.debug('''
            标题         %s
            简介         %s
            图片地址     %s
            文章地址     %s
            发布时间     %s
            内容         %s
            本地贴图地址 %s
            违规状态     %s
            敏感事件     %s
            图片鉴别地址 %s
            '''%(title, summary, image_url, article_url, release_time, content, local_image_url, violate_id, sensitive_id, sexy_image_url))

        base_parser.add_wechat_content_info('WWA_wechat_article', site_id, official_accounts_id, title, summary, image_url, article_url, release_time, content, video_url = '', local_image_url = local_image_url, violate_status = violate_id, sensitive_id = sensitive_id, sexy_image_url = sexy_image_url)

        # 同一天发布的
        oneday_article_list = article.get('app_msg_ext_info', {}).get('multi_app_msg_item_list', [])
        for article in oneday_article_list:
            title = tools.get_json_value(article, 'title')
            summary = tools.get_json_value(article, 'digest')
            image_url = tools.get_json_value(article, 'cover')

            sexy_image_url = []

            # 下载图片
            local_image_url = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.jpg'
            is_download = tools.download_file(image_url, local_image_url)
            local_image_url = local_image_url if is_download else ''
            sexy_image_url.append(local_image_url)

            article_url = tools.get_json_value(article, 'content_url')
            article_url = tools.get_full_url('http://mp.weixin.qq.com', article_url)
            article_url = article_url.replace('&amp;',"&")

            content_html, request = tools.get_html_by_requests(article_url, headers = headers)
            regex = '(<div class="rich_media_content " id="js_content">.*?)<script nonce'
            content = tools.get_info(content_html, regex, fetch_one = True)

            # 取content里的图片 下载图片 然后替换内容中原来的图片地址
            regex = '<img.*?data-src="(.*?)"'
            images = tools.get_info(content, regex)
            for image in images:
                local_image_path = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.' + (image[image.rfind('=') + len('='):] if '=' in image else 'png')
                is_download = tools.download_file(image, local_image_path)
                if is_download:
                    content = content.replace(image, local_image_path)
                    sexy_image_url.append(local_image_path)
                tools.delay_time(5)

            # 敏感事件
            sensitive_id = ''
            sensitive_event_infos = oracledb.find('select * from tab_mvms_sensitive_event')
            for sensitive_event_info in sensitive_event_infos:
                _id = sensitive_event_info[0]
                keyword1 = sensitive_event_info[3].split(',') if sensitive_event_info[3] else []
                keyword2 = sensitive_event_info[4].split(',') if sensitive_event_info[4] else []
                keyword3 = sensitive_event_info[5].split(',') if sensitive_event_info[5] else []

                if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
                    sensitive_id = _id
                    break

            # 违规事件
            violate_id = ''
            vioation_knowledge_infos = oracledb.find('select * from tab_mvms_violation_knowledge')
            for vioation_knowledge_info in vioation_knowledge_infos:
                _id = vioation_knowledge_info[0]
                keyword1 = vioation_knowledge_info[2].split(',') if vioation_knowledge_info[2] else []
                keyword2 = vioation_knowledge_info[3].split(',') if vioation_knowledge_info[3] else []
                keyword3 = vioation_knowledge_info[4].split(',') if vioation_knowledge_info[4] else []

                if base_parser.is_violate(title + tools.del_html_tag(content), key1=keyword1, key2=keyword2, key3=keyword3):
                    violate_id = _id
                    break

            log.debug('''
            标题         %s
            简介         %s
            图片地址     %s
            文章地址     %s
            发布时间     %s
            内容         %s
            本地贴图地址 %s
            违规状态     %s
            敏感事件     %s
            图片鉴别地址 %s
            '''%(title, summary, image_url, article_url, release_time, content, local_image_url, violate_id, sensitive_id, sexy_image_url))

            base_parser.add_wechat_content_info('WWA_wechat_article', site_id, official_accounts_id, title, summary, image_url, article_url, release_time, content, video_url = '', local_image_url = local_image_url, violate_status = violate_id, sensitive_id = sensitive_id, sexy_image_url = sexy_image_url)

    base_parser.update_url('WWA_wechat_article_url', root_url, Constance.DONE)
    tools.delay_time()


if __name__ == '__main__':
    url_info = {
            "_id" : "58c8a09b53446519a80d2ac6",
            "status" : 2,
            "site_id" : 3,
            "url" : 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_='%'cqcq110',
            "depth" : 0,
            "remark" : ''
        }

    parser(url_info)
