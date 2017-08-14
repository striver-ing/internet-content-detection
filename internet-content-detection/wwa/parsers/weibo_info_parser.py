import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log
from db.mongodb import MongoDB
from db.oracledb import OracleDB

SITE_ID = 10004
search_type = 102
NAME = '新浪微博'

db = MongoDB()
oracledb = OracleDB()
FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'wwa_save_path') + 'weibo/'

def get_release_time(mblog):
    try:
        release_time = mblog['created_at']
        data = tools.time.time()
        ltime = tools.time.localtime(data)
        timeStr = tools.time.strftime("%Y-%m-%d", ltime)
        if tools.re.compile('今天').findall(release_time):
            release_time = release_time.replace('今天', '%s' % timeStr)
        # if re.compile('小时前').findall(release_time):
        #     nhours = re.compile('(\d+)小时前').findall(release_time)
        #     hours_ago = (datetime.datetime.now() - datetime.timedelta(hours=int(nhours[0])))
        #     release_time = hours_ago.strftime("%Y-%m-%d %H:%M")
        elif tools.re.compile('分钟前').findall(release_time):
            nminutes = tools.re.compile('(\d+)分钟前').findall(release_time)
            minutes_ago = (tools.datetime.datetime.now() - tools.datetime.timedelta(minutes=int(nminutes[0])))
            release_time = minutes_ago.strftime("%Y-%m-%d %H:%M")
        else:
            if len(release_time)<=14:
                release_time = '%s-%s'%(timeStr[0:4],release_time)
    except:
        release_time = ''
    finally:
        return release_time



@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WWA_site_info'
    url = 'https://m.weibo.cn/'
    domain = 'weibo.cn'
    ip = '180.149.153.216'
    address = '中国 北京'
    base_parser.add_website_info(table, site_id, url, name, domain, ip, address)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))
    for search_keyword in parser_params:
        remark = search_keyword
        if not search_keyword:
            continue
        containerid = '230413'+search_keyword

        weibo_content_url = 'http://m.weibo.cn/api/container/getIndex?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO&page_type=03'% containerid
        base_parser.add_url('WWA_weibo_info_urls', SITE_ID, weibo_content_url, remark=remark)

def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    weibo_id = url_info['remark']

    for i in range(1, 100):
        weibo_content_url = root_url + '&page=%d' % i

        # 代理
        headers = {
            "Cache-Control": "max-age=0",
            "Cookie": "_T_WM=e0a91a3ed6286a67e649ce567fbbd17a; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D2304131560851875_-_WEIBO_SECOND_PROFILE_WEIBO%26fid%3D100103type%253D401%2526q%253D%26uicode%3D10000011",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Host": "m.weibo.cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
        ip, port, user_agent = base_parser.get_proxies()
        headers["User-Agent"] = user_agent
        # proxies = {'http':"http://{ip}:{port}".format(ip = ip, port = port), 'https':"https://{ip}:{port}".format(ip = ip, port = port)}
        proxies = {}
        html = tools.get_json_by_requests(weibo_content_url, headers = headers, proxies = proxies)

        cards = tools.get_json_value(html, 'cards')
        if len(cards) < 2:
            base_parser.update_url('WWA_weibo_info_urls', root_url, Constance.DONE)
            return

        tools.delay_time(10)
        for card in cards:
            mblog = tools.get_json_value(card, 'mblog')
            if not mblog:
                continue

            url = tools.get_json_value(card, 'scheme')

            # 代理
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cookie": "_T_WM=e0a91a3ed6286a67e649ce567fbbd17a; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D100103type%253D401%2526q%253D%26fid%3D2304131560851875_-_WEIBO_SECOND_PROFILE_WEIBO%26uicode%3D10000011",
                "Host": "m.weibo.cn",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "Connection": "keep-alive"
            }
            ip, port, user_agent = base_parser.get_proxies()
            headers["User-Agent"] = user_agent
            # proxies = {'http':"http://{ip}:{port}".format(ip = ip, port = port), 'https':"https://{ip}:{port}".format(ip = ip, port = port)}
            proxies = {}
            origin_html, r = tools.get_html_by_requests(url, headers = headers, proxies = proxies)
            if not origin_html:
                continue

            release_time = get_release_time(mblog)
            come_from = tools.get_json_value(mblog, 'source')
            regexs = ['"text": "(.+?)",']
            content = ''.join(tools.get_info(origin_html, regexs))
            # content = tools.del_html_tag(content)
            content = content.replace('\\', '')

            sexy_image_url = []

            regexs = ['"pic_ids": \[(.*?)\],']
            image_url = ''.join(tools.get_info(origin_html, regexs))
            image_url = tools.del_html_tag(image_url).replace('\"', '').replace('\\n', '')
            if image_url:
                image_url = image_url.split(',')
                for i in range(len(image_url)):
                    image_url[i] = 'http://wx2.sinaimg.cn/large/' + image_url[i] + '.jpg'

                sexy_image_url = image_url
                image_url = ','.join(image_url)
            regexs = ['"stream_url": "(.*?)"']
            video_url = ''.join(tools.get_info(origin_html, regexs))
            transpond_count = tools.get_json_value(mblog, 'reposts_count')
            praise_count = tools.get_json_value(mblog, 'attitudes_count')

            # 敏感事件
            sensitive_id = ''
            sensitive_event_infos = oracledb.find('select * from tab_mvms_sensitive_event')
            for sensitive_event_info in sensitive_event_infos:
                _id = sensitive_event_info[0]
                keyword1 = sensitive_event_info[3].split(',') if sensitive_event_info[3] else []
                keyword2 = sensitive_event_info[4].split(',') if sensitive_event_info[4] else []
                keyword3 = sensitive_event_info[5].split(',') if sensitive_event_info[5] else []

                if base_parser.is_violate(content, key1 = keyword1, key2 = keyword2, key3 = keyword3):
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

                if base_parser.is_violate(content, key1=keyword1, key2=keyword2, key3=keyword3):
                    violate_id = _id
                    break

            # 下载视频
            is_mp4 = tools.is_file(video_url, 'mp4')
            if is_mp4:
                local_video_path = FILE_LOCAL_PATH + 'videos/' + tools.get_current_date(date_format = '%Y-%m-%d') + "/" + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.mp4'
                is_download = tools.download_file(video_url, local_video_path)
                video_url = local_video_path if is_download else ''
            else:
                video_url = ''

            log.debug('''
                      原文地址：     %s
                      微博ID：       %s
                      发布时间：     %s
                      来自：         %s
                      内容：         %s
                      图片地址：     %s
                      视频地址：     %s
                      转发数：       %s
                      点赞数：       %s
                      违规id：       %s
                      敏感事件       %s
                      图像鉴别地址   %s
                     ''' % (url, weibo_id, release_time, come_from, content, image_url, video_url,
                            transpond_count, praise_count, violate_id, sensitive_id, sexy_image_url))

            if content:
                base_parser.add_wwa_weibo_info_info('WWA_weibo_info_info', SITE_ID, url, weibo_id, release_time, come_from,
                                                    content, image_url, video_url, transpond_count, praise_count, violate_id, sensitive_id = sensitive_id, sexy_image_url =sexy_image_url)
        tools.delay_time()

    base_parser.update_url('WWA_weibo_info_urls', root_url, Constance.DONE)