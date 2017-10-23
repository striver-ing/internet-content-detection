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
    for result in parser_params:
        monitor_type = result[1]
        keyword = result[0]
        if keyword:
            url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_='%keyword
            base_parser.add_url('WWA_wechat_article_url', SITE_ID, url, remark = {'keyword':keyword, 'monitor_type':monitor_type})

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']['keyword']
    monitor_type = url_info['remark']['monitor_type']
    official_accounts_id = remark
    retry_times = url_info['retry_times']

    headers = {
    "Host": "weixin.sogou.com",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Cookie": "ABTEST=8|1506658658|v1; IPLOC=CN1100; SUID=C5C47C7B642E940A0000000059CDC962; SUID=C5C47C7B1508990A0000000059CDC963; weixinIndexVisited=1; SUV=00F95AA57B7CC4C559CDC963CE316529; SNUID=2B2A9295EDE8B7A2BCECB605EE30F1BE; JSESSIONID=aaadcwpP9yaKs-PCMhz6v",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Upgrade-Insecure-Requests": "1"
    }

    # 获取代理
    proxies = base_parser.get_proxies()
    headers["User-Agent"] = base_parser.get_user_agent()

    # 解析
    # print(proxies)
    # html, r = tools.get_html_by_requests('http://ip.chinaz.com/getip.aspx', headers = headers, proxies = proxies)
    # print(html)

    html, request = tools.get_html_by_requests(root_url, headers = headers, proxies = proxies)
    if not html:
        base_parser.update_url('urls', root_url, Constance.TODO, retry_times + 1)
        return

    # print(html)
    regex = '<input type=text name="c" value="" placeholder="(.*?)" id="seccodeInput">'
    check_info = tools.get_info(html, regex, fetch_one = True)
    print(root_url)
    log.debug('取文章链接' + check_info)

    if check_info:
        base_parser.update_url('urls', root_url, Constance.TODO, retry_times + 1)
        return

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
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Host": "mp.weixin.qq.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive"
    }

    # 代理
    proxies = base_parser.get_proxies()
    headers["User-Agent"] = base_parser.get_user_agent()
    proxies = {} #使用代理会出现验证码 暂时不使用

    html, request = tools.get_html_by_requests(account_url, headers = headers, proxies = proxies)
    regex = '<input class="weui_input frm_input" id="input" placeholder="(.*?)" maxlength="4">'
    check_info = tools.get_info(html, regex, fetch_one = True)
    log.debug('''
        取文章详细内容 %s
        url %s
        request.headers %s
        '''%(check_info, account_url, request.headers))
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

        content_html, request = tools.get_html_by_requests(article_url, headers = headers, proxies = proxies)
        regex = '(<div class="rich_media_content " id="js_content">.*?)<script nonce'
        content = tools.get_info(content_html, regex, fetch_one = True)

        # # 取content里的图片 下载图片 然后替换内容中原来的图片地址
        regex = '<img.*?data-src="(.*?)"'
        images = tools.get_info(content, regex)
        for image in images:
            local_image_path = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.' + (image[image.find('wx_fmt=') + len('wx_fmt='):(image.find('&', image.find('wx_fmt=') + len('wx_fmt=')) if image.find('&', image.find('wx_fmt=') + len('wx_fmt=')) != -1 else None)] if 'wx_fmt=' in image else 'jpg')
            is_download = tools.download_file(image, local_image_path)
            if is_download:
                content = content.replace(image, local_image_path)
                sexy_image_url.append(local_image_path)
            tools.delay_time(5)

        # 敏感事件
        sensitive_id = ''
        if monitor_type == 1 or monitor_type == 2:
            sensitive_event_infos = oracledb.find('select t.id, t.keyword1, t.keyword2, t.keyword3 from tab_mvms_sensitive_event t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time')
            for sensitive_event_info in sensitive_event_infos:
                _id = sensitive_event_info[0]
                keyword1 = sensitive_event_info[1].split(',') if sensitive_event_info[1] else []
                keyword2 = sensitive_event_info[2].split(',') if sensitive_event_info[2] else []
                keyword3 = sensitive_event_info[3].split(',') if sensitive_event_info[3] else []

                if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
                    sensitive_id = _id
                    break

        # 违规事件
        violate_id = ''
        if monitor_type == 0 or monitor_type == 2:
            vioation_knowledge_infos = oracledb.find('select t.id, t.keyword1, t.keyword2, t.keyword3 from tab_mvms_violation_knowledge t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time')
            for vioation_knowledge_info in vioation_knowledge_infos:
                _id = vioation_knowledge_info[0]
                keyword1 = vioation_knowledge_info[1].split(',') if vioation_knowledge_info[1] else []
                keyword2 = vioation_knowledge_info[2].split(',') if vioation_knowledge_info[2] else []
                keyword3 = vioation_knowledge_info[3].split(',') if vioation_knowledge_info[3] else []

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

            content_html, request = tools.get_html_by_requests(article_url, headers = headers, proxies = proxies)
            regex = '(<div class="rich_media_content " id="js_content">.*?)<script nonce'
            content = tools.get_info(content_html, regex, fetch_one = True)

            # 取content里的图片 下载图片 然后替换内容中原来的图片地址
            regex = '<img.*?data-src="(.*?)"'
            images = tools.get_info(content, regex)
            for image in images:
                local_image_path = FILE_LOCAL_PATH + 'images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.' + (image[image.find('wx_fmt=') + len('wx_fmt='):(image.find('&', image.find('wx_fmt=') + len('wx_fmt=')) if image.find('&', image.find('wx_fmt=') + len('wx_fmt=')) != -1 else None)] if 'wx_fmt=' in image else 'jpg')
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
