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
        ''' % str(parser_params))
    for search_keyword in parser_params:
        remark = search_keyword
        if not search_keyword:
            continue
        search_keyword = tools.quote(search_keyword, safe='/:?=&%')
        url = 'http://m.weibo.cn/api/container/getIndex?type=user&containerid=100103type%3D3%26q%3D' + search_keyword
        if not base_parser.add_url('WWA_weibo_user_urls', SITE_ID, url, remark=remark):
            base_parser.update_url('WWA_weibo_user_urls', url, Constance.TODO)


def parser(url_info):
    root_url = url_info['url']
    print('1111'+root_url)
    for i in range(2, 100):
        list_url = root_url + '&page=%d' % i
        print(list_url)
        html = tools.get_json_by_requests(list_url)

        cards = tools.get_json_value(html, 'cards')
        for i in cards:
            card_group = tools.get_json_value(i, 'card_group')
            if card_group:
                break
        if not card_group:
            break
        # card_group = tools.get_json_value(cards[1], 'card_group')
        for info in card_group:
            user_info = tools.get_json_value(info, 'user')
            _id = tools.get_json_value(user_info, 'id')
            name = tools.get_json_value(user_info, 'screen_name')
            is_verified_reason = 101
            verified_reason = tools.get_json_value(user_info, 'verified_reason')
            if verified_reason:
                is_verified_reason = 102
            sex = tools.get_json_value(user_info, 'gender')
            if sex == 'f':
                sex = 1
            elif sex == 'm':
                sex = 0
            else:
                sex = ''
            image_url = tools.get_json_value(user_info, 'profile_image_url')
            url = tools.get_json_value(user_info, 'profile_url')
            summary = tools.get_json_value(user_info, 'description')
            follow_count = tools.get_json_value(user_info, 'follow_count')
            fans_count = tools.get_json_value(user_info, 'followers_count')

            log.debug('''
                         用户id：     %s
                         微博昵称：   %s
                         微博地址：   %s
                         头像地址：   %s
                         微博认证：   %s
                         是否认证：   %s
                         性别：       %s
                         简介：       %s
                         粉丝数：     %s
                         关注数：     %s
                        ''' % (_id, name, url, image_url, verified_reason, is_verified_reason, sex,
                               summary, fans_count, follow_count))
            base_parser.add_wwa_weibo_user_info('WWA_weibo_user_info', SITE_ID, _id, name, url, image_url, verified_reason,
                                                is_verified_reason, sex, summary, fans_count, follow_count)
    base_parser.update_url('WWA_weibo_user_urls', root_url, Constance.DONE)