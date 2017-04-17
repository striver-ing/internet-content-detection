
import sys
sys.path.append('../../')

import init
import base.base_parser as base_parser
import base.constance as Constance
import utils.tools as tools
from utils.log import log

# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '映客'

# 拼參數用
SECRET_KEY="8D2E##1[5$^(38#%#d3z96;]35q#MD28"
CURRENT_TIMESTAMP = tools.get_current_timestamp()
S_SG = tools.get_md5(SECRET_KEY + str(CURRENT_TIMESTAMP)) #Sig由固定密钥

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'LiveApp_site_info'
    url = 'http://www.inke.cn/hotlive_list.html'

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    params = {
        'gender'      :1,
        'gps_info'    :'116.348605,39.902727',
        'loc_info'    :'CN,北京市,北京市',
        'is_new_user' :0,
        'lc'          :'0000000000000048',
        'cc'          :'TG0001',
        'cv'          :'IK3.8.60_Iphone',
        'proto'       :7,
        'idfa'        :'D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB',
        'idfv'        :'5779214D-BC8F-446E-A547-913048F7F935',
        'devi'        :'0a4392f06ab0ff10b44c6f88d95bf4d6db67f0e7',
        'osversion'   :'ios_10.200000',
        'ua'          :'iPhone9_2',
        'imei'        :'',
        'imsi'        :'',
        'uid'         :207821358,
        'sid'         :'20RUXGrYPxpJy75btYQYlVp6lYxi0wj1xV50Ttnls6ty3DcXE5i1',
        'conn'        :'wifi',
        'mtid'        :'987c70ecbcd643998ea6bcd3b8868934',
        'mtxid'       :'b0958e29253f',
        'logid'       :133,
        's_sg'        :S_SG,
        's_sc'        :100,
        's_st'        :CURRENT_TIMESTAMP
    }

    url = tools.joint_url('http://120.55.238.158/api/live/simpleall', params)
    base_parser.add_url('LiveApp_urls', SITE_ID, url)


# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    json = tools.get_json_by_requests(root_url)

    # 主播信息
    lives = tools.get_json_value(json, 'lives')
    # print(tools.dumps_json(lives))

    for live in lives:
        name = tools.get_json_value(live, 'creator.nick')
        image_url = tools.get_json_value(live, 'creator.portrait')
        image_url = tools.get_full_url('http://img2.inke.cn', image_url)

        room_id = tools.get_json_value(live, 'creator.id')
        room_url = tools.get_json_value(live, 'share_addr')
        video_path = tools.get_json_value(live, 'stream_addr')
        watched_count = tools.get_json_value(live, 'online_users')
        address = tools.get_json_value(live, 'city')
        # 取粉丝数
        params = {
            'lc'          :'0000000000000048',
            'cc'          :'TG0001',
            'cv'          :'IK3.8.60_Iphone',
            'proto'       :7,
            'idfa'        :'D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB',
            'idfv'        :'5779214D-BC8F-446E-A547-913048F7F935',
            'devi'        :'0a4392f06ab0ff10b44c6f88d95bf4d6db67f0e7',
            'osversion'   :'ios_10.200000',
            'ua'          :'iPhone9_2',
            'imei'        :'',
            'imsi'        :'',
            'uid'         :207821358,
            'sid'         :'20RUXGrYPxpJy75btYQYlVp6lYxi0wj1xV50Ttnls6ty3DcXE5i1',
            'conn'        :'wifi',
            'mtid'        :'987c70ecbcd643998ea6bcd3b8868934',
            'mtxid'       :'b0958e29253f',
            'logid'       :133,
            'id'          :room_id,
            's_sg'        :S_SG,
            's_sc'        :100,
            's_st'        :CURRENT_TIMESTAMP
        }
        fans_json = tools.get_json_by_requests('http://120.55.238.158/api/user/relation/numrelations', params)
        fans_count = tools.get_json_value(fans_json, 'num_followers')

        #主播观众数请求地址
        params = {
            'lc'          :'0000000000000048',
            'cc'          :'TG0001',
            'cv'          :'IK3.8.60_Iphone',
            'proto'       :7,
            'idfa'        :'D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB',
            'idfv'        :'5779214D-BC8F-446E-A547-913048F7F935',
            'devi'        :'0a4392f06ab0ff10b44c6f88d95bf4d6db67f0e7',
            'osversion'   :'ios_10.200000',
            'ua'          :'iPhone9_2',
            'imei'        :'',
            'imsi'        :'',
            'uid'         :207821358,
            'sid'         :'20RUXGrYPxpJy75btYQYlVp6lYxi0wj1xV50Ttnls6ty3DcXE5i1',
            'conn'        :'wifi',
            'mtid'        :'987c70ecbcd643998ea6bcd3b8868934',
            'mtxid'       :'b0958e29253f',
            'logid'       :133,
            'id'          :tools.get_json_value(live, 'id'),
            'multiaddr'   :1,
            's_sg'        :S_SG,
            's_sc'        :100,
            's_st'        :CURRENT_TIMESTAMP
            }

        watched_count_url = 'http://120.55.238.158/api/live/infos'#?lc=0000000000000048&cc=TG0001&cv=IK3.8.60_Iphone&proto=7&idfa=D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB&idfv=5779214D-BC8F-446E-A547-913048F7F935&devi=0a4392f06ab0ff10b44c6f88d95bf4d6db67f0e7&osversion=ios_10.200000&ua=iPhone9_2&imei=&imsi=&uid=207821358&sid=20RUXGrYPxpJy75btYQYlVp6lYxi0wj1xV50Ttnls6ty3DcXE5i1&conn=wifi&mtid=987c70ecbcd643998ea6bcd3b8868934&mtxid=b0958e29253f&logid=133&id=1487572239333810%2C1487572432485069%2C1487572763094071%2C1487573160678176%2C1487571635332280&multiaddr=1&s_sg=c3493ab9d9b2e19cfc20f98bb75ff72f&s_sc=100&s_st=1487573119'
        watched_count_url = tools.joint_url(watched_count_url, params)

        live_info = tools.get_json_by_requests(watched_count_url)
        sex = live_info['lives'][0]['creator']['sex']
        sex = 0 if sex == '1' else 1  #数据库中 0 男 1女； 映客中 0 和 3是女 1是男
        age = ''

        log.debug('''
            名字：       %s
            贴图：       %s
            主播id：     %s
            房间url：    %s
            视频流地址： %s
            观看数：     %s
            地址：       %s
            粉丝数：     %s
            性别：       %s
            年龄：       %s
            观众数url：  %s
            ''' % (name, image_url, room_id, room_url, video_path, watched_count, address, fans_count, sex, age, watched_count_url))

        base_parser.add_anchor_info('LiveApp_anchor_info', SITE_ID, name = name, image_url = image_url, room_id = room_id, room_url = room_url, video_path = video_path, watched_count = watched_count, address = address, fans_count = fans_count, sex = sex, age = age, watched_count_url = watched_count_url)

    base_parser.update_url('LiveApp_urls', root_url, Constance.DONE)

if __name__ == '__main__1':
    secret_key="8D2E##1[5$^(38#%#d3z96;]35q#MD28"
    current_timestamp = tools.get_current_timestamp()

    s_sg = tools.get_md5(secret_key + str(current_timestamp)) #Sig由固定密钥

    params = {
        'gender'      :1,
        'gps_info'    :'116.348605,39.902727',
        'loc_info'    :'CN,北京市,北京市',
        'is_new_user' :0,
        'lc'          :'0000000000000048',
        'cc'          :'TG0001',
        'cv'          :'IK3.8.60_Iphone',
        'proto'       :7,
        'idfa'        :'D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB',
        'idfv'        :'5779214D-BC8F-446E-A547-913048F7F935',
        'devi'        :'0a4392f06ab0ff10b44c6f88d95bf4d6db67f0e7',
        'osversion'   :'ios_10.200000',
        'ua'          :'iPhone9_2',
        'imei'        :'',
        'imsi'        :'',
        'uid'         :207821358,
        'sid'         :'20RUXGrYPxpJy75btYQYlVp6lYxi0wj1xV50Ttnls6ty3DcXE5i1',
        'conn'        :'wifi',
        'mtid'        :'987c70ecbcd643998ea6bcd3b8868934',
        'mtxid'       :'b0958e29253f',
        'logid'       :133,
        's_sg'        :S_SG,
        's_sc'        :100,
        's_st'        :CURRENT_TIMESTAMP
    }

    url = tools.joint_url('http://120.55.238.158/api/live/simpleall', params)

    url_info = {
        "status": 0,
        "site_id": 1,
        'url':url,
        "remark": {
            "search_keyword3": [],
            "search_keyword2": [],
            "search_keyword1": []
        },
        "depth": 0,
        "_id": "58a2cec55344652a48ab2f5a"
    }

    parser(url_info)