import sys
sys.path.append('../../')

import init
import base.base_parser as base_parser
import base.constance as Constance
import utils.tools as tools
from utils.log import log



SITE_ID = 2
NAME = '爱奇艺'

layer = 1  #设置视频清晰度(0/1/2/3)

download_header = {
    'Host': 'iface2.iqiyi.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    't': '446513656',
    'Connection': 'keep-alive',
    'Cookie': 'P00001=53igk5Vn7X1xpazWBjzW2HUN4XGjNSP4aQypF7affdnBUaC6rknOS4dzvIcU1pMm2m2Qfb; QC005=63505c6afe3861f5e3f89adb3b33c7e8; P00002=%7B%22uid%22%3A%221229289410%22%2C%22user_name%22%3A%22564773807%40qq.com%22%2C%22email%22%3A%22564773807%40qq.com%22%2C%22nickname%22%3A%22BorisLiu%22%2C%22pru%22%3A1229289410%2C%22type%22%3A10%2C%22pnickname%22%3A%22BorisLiu%22%7D; P00004=1992744720.1484365089.92d0523466; T00404=5d08312eeb25b464ea9e424b74bc5aea; Hm_lvt_53b7374a63c37483e5dd97d78d9bb36e=1483756029; QC006=1296d3c47c29d816dff47d0916cbc288; QC008=1483756029.1483756029.1483756029.2; QC118=%7B%22color%22%3A%22FFFFFF%22%2C%22size%22%3A20%2C%22channelConfig%22%3A0%7D',
    'User-Agent': 'QIYIVideo/8.1 (iOS;com.qiyi.iphone;iOS10.2.1;iPhone9,2) Corejar',
    'sign': 'be218f97f09752dd6999ec86a22dbf6f',
    'Accept-Encoding':'gzip',
    'Connection': 'keep-alive'
}

def zhuanji_parser(url, remark):
    image_url = remark
    html, res = tools.get_html_by_requests(url)
    program_name = tools.get_info(html, ['<title>(.+?)-.+?</title>'], fetch_one=True)
    if not program_name:
        base_parser.update_url('PROGRAM_urls', url, Constance.EXCEPTION)
        return
    ablum_list_id = tools.get_info(html, ['data-bodansubid="(.+?)"'], fetch_one=True)
    if ablum_list_id:
        video_list_url = 'http://cache.video.qiyi.com/jp/plst/%s/' % ablum_list_id
        list_json, res = tools.get_html_by_requests(video_list_url)
        video_list = tools.get_info(list_json, ['http://www.iqiyi.com/v_.+?.html'])
    else:
        ablum_list_id = tools.get_info(html, ['sourceId: (.+?),'], fetch_one=True)
        video_list_url = 'http://cache.video.qiyi.com/jp/sdvlst/6/%s/' % ablum_list_id
        list_json, res = tools.get_html_by_requests(video_list_url)
        # video_list = tools.get_info(list_json, ['http://www.iqiyi.com/v_.+?.html'])
        video_list = tools.get_info(list_json, ['http://www.iqiyi.com/.+?.html'])
    if ablum_list_id == '0':
        video_list = []

    if not video_list:
        video_list = tools.get_tag(html, 'div', {'class': 'wrapper-piclist'}, find_all=False)
        video_list = tools.get_info(str(video_list), ['(http://www.iqiyi.com/v_.+?.html)'])
        video_list = list(set(video_list))

    if not video_list:
        video_list = tools.get_tag(html, 'div', {'class': 'piclist-wrapper'}, find_all=False)
        video_list = tools.get_info(str(video_list), ['(http://www.iqiyi.com/v_.+?.html)'])
        video_list = list(set(video_list))

    if not video_list:
        video_list = tools.get_tag(html, 'ul', {'class': 'juji-list'}, find_all=False)
        video_list = tools.get_info(str(video_list), ['(http://www.iqiyi.com/v_.+?.html)'])
        video_list = list(set(video_list))

    if not video_list:
        video_list = tools.get_tag(html, 'div', {'class': 'videoList'}, find_all=False)
        video_list = tools.get_info(str(video_list), ['(http://www.iqiyi.com/v_.+?.html)'])
        video_list = list(set(video_list))

    summary = tools.get_tag(html, 'span', {'class': 'showMoreText'}, find_all=False)
    if summary:
        summary = summary.get_text().replace('简介：', '')
    if not summary:
        summary = tools.get_tag(html, 'div', {'data-moreorless': 'moreinfo'}, find_all=False)
        if summary:
            summary = summary.get_text()

    log.debug('''
                          封面地址:          %s
                          专辑地址:          %s
                          简介:              %s
                          节目名称:          %s
                          视频列表:          %s
                          ''' % (
    image_url, url, summary, program_name, video_list))

    program_id = base_parser.add_program_info('PROGRAM_info', SITE_ID, image_url=image_url, program_url=url,
                                                  summary=summary, program_name=program_name)
    for link in video_list:
        base_parser.add_url('PROGRAM_urls', SITE_ID, link, depth=1, remark=program_id)

    base_parser.update_url('PROGRAM_urls', url, Constance.DONE)

# zhuanji_parser('http://www.iqiyi.com/a_19rrhal04x.html#vfrm=2-4-0-1')

def juji_parser(url, remark):
    program_id = remark

    html, res = tools.get_html_by_requests(url)

    tvid = tools.get_info(html, ['player-tvid="(\d{4,11})"', 'list-tvid="(\d{4,11})"'], fetch_one=True)
    pcInfo_url = "http://mixer.video.iqiyi.com/jp/mixin/videos/" + str(tvid)
    # print(pcInfo_url)
    html2, res = tools.get_html_by_requests(pcInfo_url)

    album_id = tools.get_info(html, ['player-albumid="(\d{4,11})', 'list-albumid="(\d{4,11})"',
                                     'albumId: ?(\d{4,11}),', 'param\[\'albumId\'\] ?= ?"(\d{4,11})"'] ,fetch_one=True)

    episode_name = tools.get_info(html, ['meta.+?"irTitle" content="(.+?)"'], fetch_one=True)

    image_url = tools.get_info(html, ['<meta property="og:image" content="(.+?)"/>'], fetch_one=True)
    image_url = image_url.replace('.jpg', '_160_90.jpg')

    play_count = tools.get_info(html2 , ['"playCount":(.+?),'], fetch_one=True)
    time_length = tools.get_info(html2, ['"duration":\s*(.+?),'], fetch_one=True)
    episode_num = tools.get_info(html2, ['"order":\s*(.+?),'], fetch_one=True)

    current_time = tools.get_current_timestamp() * 1000
    current_time = str(current_time)

    download_json_url = 'http://iface2.iqiyi.com/video/3.0/v_download?app_k=8e48946f144759d86a50075555fd5862&app_v=8.1&qyid=D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB&secure_p=iPhone&secure_v=1&dev_hw=%7B%22cpu%22:%22%22,%22mem%22:%222802%22%7D&net_sts=1&device_id=D2E02B97-0F35-486F-9CD4-A2EC13BBC8FB&dev_os=10.2.1&dev_ua=iPhone9,2&net_ip=%7B%22country%22:%22%E4%B8%AD%E5%9B%BD%22,%22province%22:%22%E5%8C%97%E4%BA%AC%22,%22city%22:%22%E5%8C%97%E4%BA%AC%22,%22cc%22:%22%E5%9B%BD%E5%86%85%E5%85%B6%E4%BB%96%22,%22area%22:%22%E5%8D%8E%E5%8C%97%22,%22timeout%22:0,%22respcode%22:0%7D&album_id=' + album_id + '&tvid=' + tvid + '&req_times=1&play_core=0&platform_id=12&app_p=iphone&app_t=0&usr_res=16&ppid=1229289410&cookie=53igk5Vn7X1xpazWBjzW2HUN4XGjNSP4aQypF7affdnBUaC6rknOS4dzvIcU1pMm2m2Qfb&lang=zh_CN&app_lm=cn&pps=0&req_sn=' + current_time
    json_ = tools.get_json_by_requests(download_json_url, headers=download_header)
    download_url = tools.get_json_value(json_, 'video.mp4_res.1.url')
    download_url, res = tools.get_html_by_requests(download_url)
    download_url = tools.get_info(download_url, ['"l":"(.+?)"'], fetch_one=True)


    log.debug('''
                                        节目id:            %s
                                        当前集数:          %s
                                        本集时长:          %s
                                        播放次数:          %s
                                        节目名称:          %s
                                        下载地址:          %s
                                        节目链接:          %s
                                        图片地址:          %s
                                        ''' % (
        program_id, episode_num, time_length, play_count, episode_name, download_url, url, image_url))

    base_parser.add_program_episode_info('PROGRAM_EPISODE_info', SITE_ID, program_id=program_id,
                                         episode_num=episode_num,time_length=time_length, episode_name=episode_name, download_url=download_url,
                                         episode_url=url, image_url=image_url, play_count=play_count)

    base_parser.update_url('PROGRAM_urls', url, Constance.DONE)


# juji_parser('http://www.iqiyi.com/v_19rrb2ascs.html')

@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = 'http://www.iqiyi.com/'

    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
# @tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''% str(parser_params))

    _db = base_parser.MongoDB()
    _db.set_unique_key('PROGRAM_EPISODE_info', 'episode_url')
    _db.update('PROGRAM_urls', {'depth': 0, 'site_id': SITE_ID}, {'status': 0}, multi=True)

    urls_zongyi = [
         'http://list.iqiyi.com/www/6/-30279------------11-1-1-iqiyi--.html',
         'http://list.iqiyi.com/www/6/-30279------------11-2-1-iqiyi--.html',
         'http://list.iqiyi.com/www/6/-30279------------11-3-1-iqiyi--.html']
    for urls in urls_zongyi:
        html, res = tools.get_html_by_requests(urls)
        list_infos = tools.get_tag(html, 'div', {'class': 'site-piclist_pic'}, find_all=True)
        for list_info in list_infos:
            link = list_info.a['href']
            image_url = list_info.a.img['src']
            print(link + ' '+image_url)
            base_parser.add_url('PROGRAM_urls', SITE_ID, link, remark=image_url)


    urls_juji = 'http://www.iqiyi.com/kszt/iqiyizzj.html'
    html, res = tools.get_html_by_requests(urls_juji)

    list_part_A = tools.get_tag(html, 'div', {'class': 'pro-pic'})
    for i in list_part_A:
        url = i.a['href']
        image_url = i.a.img['src']
        print(url+ ' '+image_url)
        base_parser.add_url('PROGRAM_urls', SITE_ID, url, remark=image_url)

    list_part_B = tools.get_tag(html, 'div', {'class': 'partB'}, find_all=False)
    part_B_url = tools.get_info(list_part_B, '<a href="([^>]*?)"><img.*?src="(.*?)"')
    for pb in part_B_url:
        base_parser.add_url('PROGRAM_urls', SITE_ID, pb[0], remark=pb[1])

# 必须定义 解析网址
def parser(url_info):
    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    if depth == 0:
        zhuanji_parser(root_url, remark)
    elif depth == 1:
        juji_parser(root_url, remark)



