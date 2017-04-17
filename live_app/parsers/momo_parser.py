import sys
sys.path.append('../../')

import init
import base.base_parser as base_parser
import base.constance as Constance
import utils.tools as tools
from utils.log import log

SITE_ID = 3
# 必须定义 网站名
NAME = '陌陌直播'

lists_headers = {
    'Cookie': 'MMID=8a15a5674fa198503dcac35dff04bee0; __v3_c_sesslist_10052=en6hk7g5wo_da5; __v3_c_review_10052=1; __v3_c_last_10052=1487233333348; __v3_c_visitor=1486539373375345; Hm_lvt_96a25bfd79bc4377847ba1e9d5dfbe8a=1486539374,1487233333; cId=23443128402874; L_V_T=db9ad5b0-800d-4f43-b6fa-33aa5e32afbc; L_V_T.sig=jOJ6vGu87WNyc-iYOuqGG0O75do; s_id=ddf326335bc77c8095eaa12f264fa341; webmomo=w5YTIqFi6W-HyyRmFvdQtzjKCj4B-23U; webmomo.sig=NFyjonOVMB_tQD5wFTUut8-58sE; Hm_lvt_c391e69b0f7798b6e990aecbd611a3d4=1487235867,1487235873,1487235973,1487555012; Hm_lpvt_c391e69b0f7798b6e990aecbd611a3d4=1487557821; web-imi-bew=s%3A434904554.1rDSKSZKt%2B0YDpAAi%2B2B3XBLPWR8s4QItn0tZZlA4aA; web-imi-bew.sig=J4cE69g51WFdUOxLDC--7QO8_mE',
    'Host': 'web.immomo.com',
    'Origin': 'https://web.immomo.com',
    'Referer': 'https://web.immomo.com/live',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'LiveApp_site_info'
    url = 'https://web.immomo.com/live'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    for page_num in range(1, 21):
        lists_params = {
            'page': page_num,
        }
        resp = tools.requests.post('https://web.immomo.com/webmomo/api/scene/recommend/lists', data=lists_params,
                                   headers=lists_headers)
        info = resp.json()
        data = info['data']
        r_infos = data['r_infos']
        for r_info in r_infos:
            stid = r_info['stid']
            room_url = 'https://web.immomo.com/live/%s' % stid
            base_parser.add_url('LiveApp_urls', SITE_ID, room_url, remark = r_info)

def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    stid = remark['stid']
    title = remark['title']
    room_url = root_url
    image_url = remark['cover']


    infosv2_headers = {
        'Cookie': 'MMID=8a15a5674fa198503dcac35dff04bee0; __v3_c_review_10052=1; __v3_c_last_10052=1487233333348; __v3_c_visitor=1486539373375345; Hm_lvt_96a25bfd79bc4377847ba1e9d5dfbe8a=1486539374,1487233333; cId=23443128402874; L_V_T=db9ad5b0-800d-4f43-b6fa-33aa5e32afbc; L_V_T.sig=jOJ6vGu87WNyc-iYOuqGG0O75do; s_id=a68f007aa8644cc112f2b026a915e5c4; webmomo.sig=k0F5PIijTCK14gJvogLq-fqt978; web-imi-bew=s%3A434904554.1rDSKSZKt%2B0YDpAAi%2B2B3XBLPWR8s4QItn0tZZlA4aA; web-imi-bew.sig=J4cE69g51WFdUOxLDC--7QO8_mE; io=XTckP8nk8qE9G3U3AW1E; Hm_lvt_c391e69b0f7798b6e990aecbd611a3d4=1487664000,1487664487,1487667595,1487668109; Hm_lpvt_c391e69b0f7798b6e990aecbd611a3d4=1487668223',
        'Host': 'web.immomo.com',
        'Origin': 'https://web.immomo.com',
        'Referer': 'https://web.immomo.com/live/%s'%stid,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    infosv2_params = {
        'stid': stid,
        'src': 'url'
    }

    infosv2 = tools.requests.post('https://web.immomo.com/webmomo/api/scene/profile/infosv2', data=infosv2_params,
                         headers=infosv2_headers)
    infosv2 = infosv2.json()
    infosv2_data = infosv2['data']
    # print(infosv2_data)
    watched_count = infosv2_data['on']
    rid = infosv2_data['rid']
    name = infosv2_data['name']
    token = infosv2_data['token']
    video_path = infosv2_data['url']
    watched_count_url = {
        'url': 'https://web.immomo.com/webmomo/api/scene/profile/userinfo',
        'header': infosv2_headers,
        'data': infosv2_params
    }

    userinfo_params = {
        'dmid': stid,
        'rd': rid,
        'token': token,
        'source': 'profile'
    }

    userinfo = tools.requests.post('https://web.immomo.com/webmomo/api/scene/profile/userinfo', data=userinfo_params,
                                   headers=infosv2_headers)
    userinfo = userinfo.json()
    userinfo_data =userinfo['data']
    sex = userinfo_data['sex']
    sex = 1 if sex == 'F' else  0 #0 男 1女
    age = userinfo_data['age']

    fanscount_headers = {
        'Host': 'live-api.immomo.com',
        'Accept':'*/*',
        'X-PTOKEN':'',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'X-LV': '1',
        'Content-Length': '176',
        'User-Agent': 'MomoChat/7.5.6 ios/664 (iPhone 7 Plus; iOS 10.2.1; zh_CN; iPhone9,2; S1)',
        'Connection': 'keep-alive',
        'X-KV': '88e95f44',
        'Cookie': 'SESSIONID=9C3DF7F1-C39D-06F7-EC1F-9DBE56DDBF15',
    }
    fanscount_date = {
        '_idfa_':'D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB',
        '_net_':'wifi',
        '_uid_':'e3bb287c00673c9a701c60bf79ca24b7',
        'lat': 39.90266719310277,
        'lng': 116.348690083085,
        'remoteid': stid,
        'roomid': rid,
    }

    fans_count_data = tools.requests.post('https://live-api.immomo.com/v3/user/card/lite',data=fanscount_date,
                                          headers=fanscount_headers)
    fans_count_data = fans_count_data.json()
    # print(fans_count_data)
    fans_count = tools.get_json_value(fans_count_data, 'data.fansCount')
    city = tools.get_json_value(fans_count_data, 'data.city')
    log.debug('''
                房间名：     %s
                主播名：     %s
                贴图：       %s
                主播id：     %s
                城市：       %s
                房间url：    %s
                视频流地址： %s
                观看数：     %s
                粉丝数：     %s
                性别：       %s
                年龄：       %s
                ''' % (
    title, name, image_url, stid, city, room_url, video_path, watched_count, fans_count, sex, age))

    base_parser.add_anchor_info('LiveApp_anchor_info', SITE_ID, title = title, name = name, image_url = image_url,
                                room_id = stid, room_url = room_url, video_path = video_path, watched_count = watched_count,
                                fans_count = fans_count, sex = sex, age = age, address = city, watched_count_url = watched_count_url)
    base_parser.update_url('LiveApp_urls', root_url, Constance.DONE)
# import threading
# threads = []
# for x in range(20):
#     x=threading.Thread(target = parser)
#     threads.append(x)
# for t in threads:
#     t.start()




# data = {
#     'momoid':'18201117718',
#     'password':'f5cccd3389edafdba1f57eea75b3d16d',
#     'imgv':'',
#     'symbol':'/?rf='
# }
# resp = requests.post('https://web.immomo.com/sendCode', data)
# print(resp.headers)

