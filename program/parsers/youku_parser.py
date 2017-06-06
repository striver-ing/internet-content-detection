import sys
sys.path.append('../../')

import init
import base.base_parser as base_parser
import base.constance as Constance
import utils.tools as tools
from utils.log import log



SITE_ID = 1
NAME = '优酷'

layer = 1  #设置视频清晰度(0/1/2/3)


@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = 'http://www.youku.com/'

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

    for page_num in range(1, 14):
        urls = [
                'http://list.youku.com/category/show/c_85_g_热门网综_s_1_d_1_p_%d.html' % page_num,
                'http://list.youku.com/category/show/c_97_g_优酷出品_s_1_d_1_p_%d.html' % page_num,
                'http://list.youku.com/category/show/c_96_g_优酷出品_s_1_d_1_p_%d.html' % page_num,
                ]
        for url in urls:
            print(url)
            print('********************************************************')
            html = tools.get_html_by_urllib(url)
            if tools.get_info(html, ['小酷没有筛选到相关视频']):
                continue
            links = tools.get_tag(html, 'div', {'class': 'p-thumb'})
            for link in links:
                try:
                    link = link.a['href']
                    link = tools.get_full_url('http:', link)
                    link_html = tools.get_html_by_urllib(link)
                    link = tools.get_tag(link_html, 'a', {'class': 'desc-link'}, find_all=False)
                    link = link['href']
                    link = tools.get_full_url('http:', link)
                    base_parser.add_url('PROGRAM_urls', SITE_ID, link, depth=0)
                except Exception as e:
                    log.error(e)
                    print(link_html)

# 必须定义 解析网址
def parser(url_info):
    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    # root_url = 'http://list.youku.com/show/id_ze7cc3b8ed96711e68ce4.html'
    # depth = 0
    # headers = {'Host': 'cmstool.youku.com',
    #            'Referer': 'http://v.youku.com/v_show/id_XMjY2NzY3MTE4NA.html',
    #            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    #            'Cookie': '__ysuid=1491380613750xxD; __yscnt=1; juid=01bg7f56tqm9e; __aryft=1495434329; yseid=1495503610725JmZw8d; yseidcount=11; seid=01bgpfc8rb2vm6; ykss=fe922359521ce2d462cbda53; cna=Y5NrEThaR2MCAdOcjEogCug8; __ayvstp=6; __aysvstp=110; l=AmdnSHROpJU3344cDsaqhZhFd5Ex5jvO; isg=AlZW_barEwKJtiefqvOnVZcapwzSXpoxTdXpV8C_SDnUg_YdKIfqQbwzbaiV; __ayft=1495503611023; __aysid=1495416942598jZ1; __arpvid=1495504158930FOANHy-1495504158944; __arycid=; __ayscnt=1; __arcms=; __aypstp=5; __ayspstp=140; ypvid=1495504161820uZFGHk; ysestep=5; yseidtimeout=1495511361821; ycid=0; ystep=237; referhost=; seidtimeout=1495505961826'}

    if depth == 0:
        html = tools.get_html_by_urllib(root_url)

        header_info = tools.get_tag(html, 'div', {'class': 'p-thumb'}, find_all=False)
        program_name = header_info.a['title']

        recent_video_url = header_info.a['href']
        recent_video_url = 'http:'+recent_video_url

        recent_video_id = tools.get_info(recent_video_url, ['id_(.+?)='], fetch_one=True)
        if not recent_video_id:
            recent_video_id = tools.get_info(recent_video_url, ['id_(.+?)\.h'], fetch_one=True)

        actors = tools.get_tag(html, 'li', {'class': 'p-row'})[2].get_text()
        actors = ''.join(tools.re.compile('主持人：(.+)').findall(actors))

        summary = tools.get_tag(html, 'span', {'class': 'text'}, find_all=False).get_text()
        summary = ''.join(tools.re.compile('简介：(.+)').findall(summary))

        image_url = tools.get_tag(html, 'div', {'class': 'p-thumb'}, find_all=False)
        image_url = image_url.img['src']

        list_url = 'https://ups.youku.com/ups/get.json?vid=%s==&ccode=0401&client_ip=&utid=Y5NrEThaR2MCAdOcjEogCug8&client_ts=' % recent_video_id
        list_json = tools.get_json_by_requests(list_url)
        video_list = tools.get_json_value(list_json, 'data.videos.list')
        # print(video_list)

        episode = tools.get_json_value(list_json, 'data.show.episode_total')

        log.debug('''
                      recent_video_url:  %s
                      recent_video_id:   %s
                      集数:              %s
                      主持人:            %s
                      封面地址:          %s
                      专辑地址:          %s
                      简介:              %s
                      节目名称:          %s
                      视频列表:          %s
                      list_url:          %s
                      ''' % (recent_video_url, recent_video_id, episode, actors, image_url, root_url, summary, program_name, video_list, list_url))

        program_id = base_parser.add_program_info('PROGRAM_info', SITE_ID, actors=actors, image_url=image_url, program_url=root_url,
                                     summary=summary, program_name=program_name, episode=episode)

        for vl in video_list:
            vl_id = tools.get_json_value(vl, 'encodevid')
            vl_url = 'http://v.youku.com/v_show/id_%s.html' % vl_id
            base_parser.add_url('PROGRAM_urls', SITE_ID, vl_url, depth=1, remark=program_id)

        base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)
    elif depth == 1:
        program_id = remark
        html, res = tools.get_html_by_requests(root_url)
        episode_name = tools.get_tag(html, 'h1', find_all=False)
        episode_name = episode_name.get_text()

        videoId = tools.get_info(html, ['videoId:"(.+?)"'], fetch_one=True)
        play_count, res = tools.get_html_by_requests('http://v.youku.com/action/getVideoPlayInfo?vid=%s&callback=tuijsonp5'% videoId)
        if not play_count:
            print(1)
        play_count = tools.get_info(play_count, ['"vv":"(.+?)"'], fetch_one=True)
        play_count = play_count.replace(',', '')

        # info_html, info_res = tools.get_html_by_requests('http://cmstool.youku.com/cms/playlog/get?callback=tuijsonp7', headers)
        # # print(info_html)
        # image_url = tools.get_info(info_html, ['"thumburl":"(.+?)",'], fetch_one=True)
        # image_url = image_url.replace('\\', '')
        # print(image_url)
        # episode_num = tools.get_info(info_html, ['"watchStage":"(.+?)",'], fetch_one=True)
        # episode_num = tools.to_chinese(episode_num)
        # print(episode_num)

        recent_video_id = tools.get_info(root_url, ['id_(.+?)='], fetch_one=True)
        if not recent_video_id:
            recent_video_id = tools.get_info(root_url, ['id_(.+?)\.h'], fetch_one=True)
        list_url = 'https://ups.youku.com/ups/get.json?vid=%s==&ccode=0401&client_ip=&utid=Y5NrEThaR2MCAdOcjEogCug8&client_ts=' % recent_video_id
        list_info = tools.get_json_by_requests(list_url)
        stream = tools.get_json_value(list_info, "data.stream")
        download_url = stream[layer]['m3u8_url']

        time_length = tools.get_json_value(list_info, "data.video.seconds")

        episode_num = tools.get_json_value(list_info, "data.show.stage")

        image_url = tools.get_json_value(list_info, "data.video.logo")

        segs = stream[layer]['segs']
        cdn_url = []
        for video_url in segs:
            cdn_url.append(video_url['cdn_url'])
        # print(cdn_url)

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
                 program_id, episode_num, time_length, play_count, episode_name, download_url, root_url, image_url))

        base_parser.add_program_episode_info('PROGRAM_EPISODE_info', SITE_ID, program_id=program_id, episode_num=episode_num,
                                            time_length=time_length, episode_name=episode_name, download_url=download_url,
                                            episode_url=root_url, image_url=image_url, play_count=play_count)

        base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)


# parser({})


