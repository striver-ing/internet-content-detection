# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')
import init

import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log
import random
from db.mongodb import MongoDB
import base.constance as Constance
from db.oracledb import OracleDB
import you_get.extractors.qq as qq
from wwa.config.kuaibao_city import *

db = MongoDB()
oracledb = OracleDB()

# 必须定义 网站id
SITE_ID = 2
# 必须定义 网站名
NAME = '天天快报'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'wwa_save_path')
NEWS_LOCAL =  1
VIDEO      = 2
STORAGE_ID = 2

URL = 'http://r.cnews.qq.com/getSubNewsChlidInterest'

HEADERS = {
    "Referer": "http://r.cnews.qq.com/inews/iphone/",
    "store": "1",
    "User-Agent": "天天快报 2.9.3 qnreading (iPhone9,2; iOS 10.3.1; zh_CN; 2.9.3.23)",
    "deviceToken": "<5e261ba3 017050b4 4ba1c0f5 7021caf9 1aad4448 34c338a6 bd82ee6d 34627784>",
    "activefrom": "icon",
    "screen-width": "414",
    "idfv": "54A77A44-E5CC-4B6A-9BCB-819EA4BA5EA1",
    "startarticleid": "",
    "apptypeExt": "qnreading",
    "Accept": "*/*",
    "devid": "54A77A44-E5CC-4B6A-9BCB-819EA4BA5EA1",
    "mac": "020000000000",
    "omgid": "160bab419500114397491a9d1b550159785a0010111b01",
    "Cookie": "phone_id=;%20phone_token=;%20openid=oijc7uBlMhbSXbb6Kr7OGjYaZSKs;%20appid=wxe90c9765ad00e2cd;%20access_token=ov6TGlnqLNeTMRfSbQFcLte8RlHPnIUM7TTXI7OWfg-qkvNlWYWG-GWLot9s07dP5IGOKTdsiwXJZ4gMVlBW5IdZ67SBUIkmVv7SbwZXZ0w;%20refresh_token=ov6TGlnqLNeTMRfSbQFcLs5FqRS0qEP3JiVEmDwuRvAJz14eSu10LCQkhWuGdtXkOnJBBQzAVz4A9fHTOC9wE_Or2-ANPFOggvPxZST74UU;%20unionid=onCs1uN5BOAu9bLh9TLfB3MiDWrg;%20logintype=1",
    "qqnetwork": "wifi",
    "appversion": "2.9.3",
    "screen-height": "736",
    "logfrom": "2",
    "idft": "03D4F3E7-39E1-4DD9-A69A-3C193EA98BA4",
    "qn-rid": "2DC6FAE4-1D7D-4F76-B8DF-33F2C974020C",
    "--qnr": "1ea9f0eb3be2",
    "appver": "10.3.1_qnreading_2.9.3",
    "Accept-Encoding": "gzip, deflate",
    "apptype": "ios",
    "Content-Length": "539",
    "screen-scale": "3",
    "idfa": "D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB",
    "currentTab": "kuaibao",
    "qn-sig": "FAF8ECC56F07D366CBC1ECAB4290573B",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "r.cnews.qq.com",
    "isJailbreak": "0",
    "Connection": "keep-alive",
    "omgbizid": "00b8f3a388d5b544564aff20044178cf15d20090112314",
    "device-model": "iPhone9,2",
    "Accept-Language": "zh-Hans-CN;q=1, en-CN;q=0.9"
}

PARAMS = {
    "screen_height": "736",
    "currentTab": "kuaibao",
    "appver": "10.3.1_qnreading_2.9.3",
    "idfv": "54A77A44-E5CC-4B6A-9BCB-819EA4BA5EA1",
    "idft": "03D4F3E7-39E1-4DD9-A69A-3C193EA98BA4",
    "__qnr": "1ea9f0ebf343",
    "devid": "54A77A44-E5CC-4B6A-9BCB-819EA4BA5EA1",
    "startarticleid": "",
    "screen_scale": "3",
    "qqnetwork": "wifi",
    "device_model": "iPhone9,2",
    "omgbizid": "00b8f3a388d5b544564aff20044178cf15d20090112314",
    "apptype": "ios",
    "omgid": "160bab419500114397491a9d1b550159785a0010111b01",
    "logfrom": "2",
    "appversion": "2.9.3",
    "activefrom": "icon",
    "mac": "020000000000",
    "screen_width": "414",
    "store": "1",
    "isJailbreak": "0",
    "apptypeExt": "qnreading",
    "idfa": "D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB"
}

data = 泸州

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WWA_app_site_info'
    url = 'http://sj.qq.com/myapp/detail.htm?apkName=com.tencent.reading'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    base_parser.add_url('WWA_app_urls', SITE_ID, URL, remark = NEWS_LOCAL)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    column_id = remark

    while True:
        try:
            json = tools.get_json_by_requests(root_url, headers = HEADERS, data = data, params = PARAMS)
            newslist = tools.get_json_value(json, 'newslist')
            if not newslist:
                break

            data['cachedCount'] += len(newslist)
            data['page'] += 1
            for news in newslist:
                # print(tools.dumps_json(news))
                title = tools.get_json_value(news, 'title')
                release_time = tools.get_json_value(news,'time')
                abstract = tools.get_json_value(news,'abstract')
                original_url = tools.get_json_value(news,'url')
                img_url = tools.get_json_value(news, 'thumbnails_qqnews')[0] if tools.get_json_value(news, 'thumbnails_qqnews') else ''
                video_frame_url = tools.get_json_value(news, 'video_channel.video.playurl')
                # 取content
                html = tools.get_html_by_urllib(original_url)
                content = tools.get_tag(html, name = 'div', attrs = {'class':"main"}, find_all = False)
                content = tools.del_html_tag(str(content))

                # 解析视频真实地址
                video_url = ''
                if video_frame_url:
                    video_vid = tools.get_info(html, 'vid\s*=\s*"\s*([^"]+)"', fetch_one = True)
                    video_url = ''.join(qq.qq_download_by_vid(video_vid))

                # 判断是否违规
                # 敏感事件
                sensitive_id = ''
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
                vioation_knowledge_infos = oracledb.find('select t.id, t.keyword1, t.keyword2, t.keyword3 from tab_mvms_violation_knowledge t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time')
                for vioation_knowledge_info in vioation_knowledge_infos:
                    _id = vioation_knowledge_info[0]
                    keyword1 = vioation_knowledge_info[1].split(',') if vioation_knowledge_info[1] else []
                    keyword2 = vioation_knowledge_info[2].split(',') if vioation_knowledge_info[2] else []
                    keyword3 = vioation_knowledge_info[3].split(',') if vioation_knowledge_info[3] else []


                    if base_parser.is_violate(title + content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
                        violate_id = _id
                        break


                log.debug('''
                title:          %s
                abstract :      %s
                img_url :       %s
                original_url:   %s
                release_time :  %s
                video_url:      %s
                content :       %s
                column_id:      %s
                sensitive_id:   %s
                violate_id:     %s

                '''
                %(title, abstract, img_url, original_url, release_time, video_url, content, column_id, sensitive_id, violate_id)
                )

                # 下载
                base_path = FILE_LOCAL_PATH
                is_download = 0

                # 下载图片
                img_name = ''
                if img_url:
                    img_name = 'kuaibao/images/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.jpg'
                    is_download = tools.download_file(img_url, base_path, img_name)
                    if not is_download:
                        img_name = ''

                sexy_image_url = base_path + img_name if img_name else img_url

                # 下载视频
                video_name = ''
                if video_url:
                    video_name = 'kuaibao/videos/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.mp4'
                    is_download = tools.download_file(video_url, base_path, video_name)
                    if not is_download:
                        video_name = ''

                if original_url:
                    base_parser.add_wwa_app_content_info('WWA_app_content_info', SITE_ID, title, abstract, img_url, img_name, original_url, release_time, video_url, video_name, content, column_id, is_download, sensitive_id, violate_id, STORAGE_ID, sexy_image_url)


        except Exception as e:
            log.debug(e)
            pass

    base_parser.update_url('WWA_app_urls', root_url, Constance.DONE)

if __name__=='__main__':
    ss ={
        "_id": "59084934ea18a923749d0336",
        "remark": '',
        "depth": 0,
        "url": "http://r.cnews.qq.com/getSubNewsChlidInterest",
        "site_id": 2,
        "status": 0
    }
    parser(ss)



