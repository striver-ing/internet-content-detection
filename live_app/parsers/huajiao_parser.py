import sys
sys.path.append('../../')

import init
import base.base_parser as base_parser
import base.constance as Constance
import utils.tools as tools
from utils.log import log

SITE_ID = 2
NAME = '花椒直播'

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'LiveApp_site_info'
    url = 'http://www.huajiao.com/'

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    for pageno in range(1, 3):
        url = 'http://www.huajiao.com/category/1000?pageno=%d' % (pageno)
        base_parser.add_url('LiveApp_urls', SITE_ID, url)

    # 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_urllib(root_url)
    regex = '<div class="g-feed2">(.*?)</li>'
    infos = tools.get_info(html, regex)
    for info in infos:
        image_url = '<img src="(.*?)" alt="" />'
        image_url = tools.get_info(info, image_url, allow_repeat = True)
        image_url = ''.join(image_url)
        image_url = tools.del_html_tag(image_url)

        name = '<div class="nickname">(.*?)</div>'
        name = tools.get_info(info, name, allow_repeat = True)
        name = ''.join(name)
        name = tools.del_html_tag(name)

        room_url = '<a href="(.*?)">'
        room_url = tools.get_info(info, room_url, allow_repeat = True)
        room_url = ''.join(room_url)
        room_url = 'http://www.huajiao.com'+room_url

        watched_count_url = room_url

        room_html = tools.get_html_by_urllib(room_url)
        del_html_tag = tools.del_html_tag(room_html)
        # print(room_html)

        fans_count = '(\d*?)粉丝'
        fans_count = tools.get_info(del_html_tag, fans_count, allow_repeat= True)
        fans_count = ''.join(fans_count)
        fans_count = int(fans_count)

        watched_count = '观看数(\d*?)\D'
        watched_count = tools.get_info(del_html_tag, watched_count)
        watched_count = ''.join(watched_count)
        watched_count = int(watched_count)

        room_id = '<p class="author-id">ID (\d*?)</p>'
        room_id = tools.get_info(room_html, room_id, allow_repeat=True)
        room_id = ''.join(room_id)
        room_id = int(room_id)

        regex = '"sn":"(.*?)"'
        video_path = ''.join(tools.get_info(room_html, regex))
        if video_path.startswith('_LC_RE'):
            video_path = 'http://ws1-pflv.live.huajiao.com/live_huajiao_v2/%s.flv'%video_path
        elif video_path.startswith('_LC_XY'):
            regex = '_LC_XY(\d*?)_non'
            video_path_num = tools.get_info(video_path,regex)[0]
            video_path = 'http://xy%s-flv.live.huajiao.com/live_huajiao_v2/%s.flv'%(video_path_num,video_path)
        else:
            regex = '_LC_ps(\d*?)_non'
            video_path_num = tools.get_info(video_path, regex)[0]
            # print(video_path_num)
            video_path = 'http://pl%s.live.huajiao.com/live_huajiao_v2/%s.flv'%(video_path_num, video_path)

        log.debug('''
               贴图:            %s
               主播名:          %s
               房间连接:         %s
               直播视频流记录:    %s
               粉丝数:          %d
               观看数:          %d
               房间号:          %d
               观看数url:       %s
               ''' % (image_url, name, room_url, video_path, fans_count, watched_count, room_id, watched_count_url))

        base_parser.add_anchor_info('LiveApp_anchor_info', SITE_ID, name=name, image_url=image_url, room_id=room_id, room_url=room_url, video_path=video_path, watched_count=watched_count, fans_count=fans_count, watched_count_url=watched_count_url)

    base_parser.update_url('LiveApp_urls', root_url, Constance.DONE)

    # |name||||主播名|
    # |sex||||性别|
    # |image_url||||贴图|
    # |age||||年龄|
    # |address||||地区|
    # |fans_count||||粉丝数|
    # |watched_count||||观众数 |
    # |ranklist_day||||日排行榜|
    # |ranklist_week||||周排行榜|
    # |ranklist_month||||月排行榜|
    # |room||||房间号|
    # |room_url||||房间连接|
    # |video_path||||直播视频流路径|
    # |record_time||||记录时间|
    # |site_id||||网站id|
    # |read_status||||读取状态（0 没读， 1读取）|
        #name = tools.get_json_value(feed, 'author.medal.nickname')
        # image_url = tools.get_json_value(feed, 'creator.portrait')
        # room = tools.get_json_value(feed, 'creator.id')
        # room_url = tools.get_json_value(feed, 'share_addr')
        # video_path = tools.get_json_value(feed, 'stream_addr')
        # watched_count = tools.get_json_value(feed, 'online_users')
        # address = tools.get_json_value(feed, 'city')

        # print(tools.dumps_json(feed))
        # break

if __name__ == '__main__':
    for pageno in range(1, 3):
        url = 'http://www.huajiao.com/category/1000?pageno=%d' % (pageno)
        url_info = {
            "status": 0,
            "site_id": 2,
            'url': url,
            "remark": {
                "search_keyword3": [],
                "search_keyword2": [],
                "search_keyword1": []
            },
            "depth": 0,
            "_id": "58a2cec55344652a48ab2f5a"
        }
        parser(url_info)



