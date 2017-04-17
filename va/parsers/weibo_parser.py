import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10004
search_type = 102
NAME = '新浪微博'

def get_video_url(mblog):
    try:
        page_info = mblog['page_info']
    except:
        page_info = ''
    finally:
        try:
            media_info = page_info['media_info']
        except:
            media_info = ''
        finally:
            try:
                stream_url = media_info['stream_url']
            except:
                stream_url = ''
            finally:
                return stream_url

def get_page_url(mblog):
    try:
        page_info = mblog['page_info']
    except:
        page_info = ''
    finally:
        try:
            page_url = page_info['page_url']
        except:
            page_url = ''
        finally:
            return page_url

def get_author(mblog):
    try:
        user = mblog['user']
    except:
        user = ''
    finally:
        try:
            author = user['screen_name']
        except:
            author = ''
        finally:
            return author

def get_url(mblog):
    try:
        user = mblog['user']
    except:
        user = ''
    finally:
        try:
            url = user['profile_url']
        except:
            url = ''
        finally:
            return url

def get_origin(mblog):
    try:
        origin = mblog['source']
    except:
        origin = ''
    finally:
        return origin

def get_reposts_count(mblog):
    try:
        reposts_count = mblog['reposts_count']  # 转发数
    except:
        reposts_count = 0
    finally:
        return reposts_count

def get_comments_count(mblog):
    try:
        comments_count = mblog['comments_count']  # 评论数
    except:
        comments_count = 0
    finally:
        return comments_count

def get_attitudes_count(mblog):
    try:
        attitudes_count = mblog['attitudes_count']  # 点赞数
    except:
        attitudes_count = 0
    finally:
        return attitudes_count

def get_content(mblog):
    try:
        content = tools.del_html_tag(mblog['text'])  # 正文
    except:
        content = ''
    finally:
        return content

def get_release_time(mblog):
    try:
        release_time = mblog['created_at']
        data = tools.time.time()
        ltime = tools.time.localtime(data)
        timeStr = tools.time.strftime("%Y-%m-%d", ltime)
        if tools.re.compile('今天').findall(release_time):
            release_time = release_time.replace('今天','%s'%timeStr)
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

def get_image_url(mblog):
    try:
        page_info = mblog['page_info']
    except:
        page_info = ''
    finally:
        try:
            page_pic = page_info['page_pic']
        except:
            page_pic = ''
        finally:
            try:
                url = page_pic['url']
            except:
                url = ''
            finally:
                return url



@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'https://m.weibo.cn/'
    domain = 'weibo.cn'
    ip = '180.149.153.216'
    address = '中国 北京'
    base_parser.add_website_info(table, site_id, url, name, domain, ip, address)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    search_keyword1 = parser_params['search_keyword1']
    search_keyword2 = parser_params['search_keyword2']
    search_keyword3 = parser_params['search_keyword3']

    remark = parser_params

    search_keywords = []
    for str_key1 in search_keyword1:
        for str_key2 in search_keyword2:
            search_keywords.append((str_key1 + str_key2).strip())
    else:
        if not search_keyword1:
            search_keywords = search_keyword2
        if not search_keyword2:
            search_keywords = search_keyword1

    for j in search_keywords:
        if not j.strip():
            continue

        for i in range(1, 109):
            url = 'https://m.weibo.cn/container/getIndex?type=all&queryVal=%s&luicode=10000011' % j + \
                  '&lfid=106003type%3D1&' + 'title=%s&containerid=100103type' % j + '%3D1%26q%3D' + '%s&' % j + \
                  'page=%d' % i
            url = tools.quote(url, safe='/:?=&%')
            if not base_parser.add_url('VA_urls', SITE_ID, url, remark=remark):
                base_parser.update_url('VA_urls', url, Constance.TODO)


# @tools.run_safe_model(__name__) # 移到parser_control
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
        'Cookie': '_T_WM=6f2675cab22ec5e018673192b46dd73b; SUB=_2A251adqIDeRxGeNO7FER8ivPyziIHXVWlebArDV6PUJbkdANLXHjkW2Eu3heWA8h0QMZFxI0_fe7-s2Isw..; SUHB=0HThVFDsKbumHU; SCF=AvoSYQqv89TMIxx4YQUcoIdBp2-sjJbx28qHTTnKAHOymGxToTyDJijAZJl_Nqe3ve0x2U-Yk5poeuVn7bSqyt0.; M_WEIBOCN_PARAMS=featurecode%3D20000180%26oid%3D4060829337409043%26luicode%3D10000011%26lfid%3D106003type%253D1%26fid%3D100103type%253D1%2526q%253D%25E5%25A5%25B3%25E4%25B8%25BB%25E6%2592%25AD%26uicode%3D10000011',
        'Host': 'm.weibo.cn',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://m.weibo.cn/p/100103type%3D1%26q%3D%E5%A5%B3%E4%B8%BB%E6%92%AD?type=all&queryVal=%E5%A5%B3%E4%B8%BB%E6%92%AD&luicode=10000011&lfid=106003type%3D1&title=%E5%A5%B3%E4%B8%BB%E6%92%AD'
        }
    resp = tools.requests.get('%s'%root_url, headers=headers)
    infos = resp.json()
    try:
        cards = infos['cards']
    except:
        base_parser.update_url('VA_urls', root_url, Constance.DONE)
        return

    for i in cards:
        try:
            card_group = i['card_group']
            # print(card_group)
            # print('****************************')
            # print('****************************')
            for group in card_group:
                if group['mblog']:
                    mblog = group['mblog']
                else:
                    continue
                if not get_video_url(mblog):
                    continue
                url = get_url(mblog)
                page_url = get_page_url(mblog)
                origin = get_origin(mblog)
                content = get_content(mblog)
                reposts_count = get_reposts_count(mblog)
                comment_count = get_comments_count(mblog)
                attitudes_count = get_attitudes_count(mblog)
                author = get_author(mblog)
                image_url = get_image_url(mblog)
                release_time = get_release_time(mblog)
                video_url = get_video_url(mblog)

                log.debug('''
                    内容：   %s
                    原文url：%s
                    作者：   %s
                    来源：   %s
                    视频封面:%s
                    视频地址:%s
                    日期：   %s
                    转发数： %s
                    评论数： %s
                    点赞数： %s
                         ''' % (content, url, author, origin, image_url, video_url, release_time,
                                str(reposts_count), str(comment_count), str(attitudes_count)))

                contained_key, contained_key_count = base_parser.get_contained_key('', content,remark['search_keyword1'],
                                                    remark['search_keyword2'],remark['search_keyword3'])
                if not contained_key:
                    continue

                base_parser.add_content_info('VA_content_info', SITE_ID, url = video_url, release_time = release_time,
                                             origin = origin, title = content, reposts_count = reposts_count,
                                             comment_count = comment_count, attitudes_count = attitudes_count,
                                             author = author, image_url = image_url, video_url = video_url,
                                             search_type = search_type, keyword = contained_key,
                                             keyword_count = contained_key_count, task_id = remark['task_id'])
        except:
            pass
    base_parser.update_url('VA_urls', root_url, Constance.DONE)
    # # 解析
    # html, request = tools.get_html_by_requests(root_url)
    # if not html:
    #     base_parser.update_url('urls', root_url, Constance.EXCEPTION)

