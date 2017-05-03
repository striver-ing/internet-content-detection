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
        for i in range(1, 100):
            weibo_content_url = 'http://m.weibo.cn/api/container/getIndex?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO&page_type=03&page=%s'% (containerid, i)
            if not base_parser.add_url('WWA_weibo_info_urls', SITE_ID, weibo_content_url, remark=remark):
                base_parser.update_url('WWA_weibo_info_urls', weibo_content_url, Constance.TODO)

def parser(url_info):
    root_url = url_info['url']
    weibo_id = url_info['remark']

    html = tools.get_json_by_requests(root_url)
    cards = tools.get_json_value(html, 'cards')
    for card in cards:
        mblog = tools.get_json_value(card, 'mblog')
        if not mblog:
            continue
        url = tools.get_json_value(card, 'scheme')
        origin_html = tools.get_html_by_requests(url)
        release_time = get_release_time(mblog)
        come_from = tools.get_json_value(mblog, 'source')
        regexs = ['"text": "(.+?)",']
        content = ''.join(tools.get_info(origin_html, regexs))
        regexs = ['"pic_ids": \[(.*?)\],']
        image_url = ''.join(tools.get_info(origin_html, regexs))
        image_url = tools.del_html_tag(image_url).replace('\"', '').replace('\\n', '')
        if image_url:
            image_url = image_url.split(',')
            for i in range(len(image_url)):
                image_url[i] = 'http://wx2.sinaimg.cn/large/' + image_url[i] + '.jpg'
            image_url = ','.join(image_url)
        regexs = ['"stream_url": "(.*?)"']
        video_url = ''.join(tools.get_info(origin_html, regexs))
        transpond_count = tools.get_json_value(mblog, 'reposts_count')
        praise_count = tools.get_json_value(mblog, 'attitudes_count')

        # 违规事件
        violate_id = ''
        vioation_knowledge_infos = oracledb.find('select * from tab_mvms_violation_knowledge')
        for vioation_knowledge_info in vioation_knowledge_infos:
            _id = vioation_knowledge_info[0]
            keyword1 = vioation_knowledge_info[2].split(' ') if vioation_knowledge_info[2] else []
            keyword2 = vioation_knowledge_info[3].split(' ') if vioation_knowledge_info[3] else []
            keyword3 = vioation_knowledge_info[4].split(' ') if vioation_knowledge_info[4] else []

            if base_parser.is_violate(content, key1=keyword1, key2=keyword2, key3=keyword3):
                violate_id = _id

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
                         ''' % (url, weibo_id, release_time, come_from, content, image_url, video_url,
                                transpond_count, praise_count, violate_id))
        base_parser.add_wwa_weibo_info_info('WWA_weibo_info_info', SITE_ID, url, weibo_id, release_time, come_from,
                                            content, image_url, video_url, transpond_count, praise_count, violate_id)
    base_parser.update_url('WWA_weibo_info_urls', root_url, Constance.DONE)
