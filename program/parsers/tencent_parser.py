import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import you_get.extractors.qq as qq
import requests
import json

# 必须定义 网站id
SITE_ID = 3
# 必须定义 网站名
NAME = '腾讯视频'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'program_save_path')

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = 'http://v.qq.com'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
# @tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    def get_page_count(url):
        html, r = tools.get_html_by_requests(url)
        regex = '<div class="mod_pages" r-notemplate="true">.*>(\d*)</a>.*?</span>'
        page_count = tools.get_info(html, regex, fetch_one = True)
        print(page_count)
        return int(page_count) if page_count else 0

    def inner_add_root_url(root_url, page_url, remark):
        page_count = get_page_count(root_url)
        for page in range(0, page_count + 1):
            url = page_url % (page * 30)
            base_parser.add_url('PROGRAM_urls', SITE_ID, url, remark = remark)

    #首页-综艺-腾讯出品
    root_url = 'http://v.qq.com/x/list/variety?offset=0&isource=2'
    page_url = 'http://v.qq.com/x/list/variety?offset=%d&isource=2'
    # inner_add_root_url(root_url, page_url, remark = {'classify' : '综艺'})

    # 首页-电视剧-腾讯出品（自制剧）
    root_url = 'http://v.qq.com/x/list/tv?sort=4&offset=0&iarea=-1&iyear=-1&itype=843'
    page_url = 'http://v.qq.com/x/list/tv?sort=4&offset=%d&iarea=-1&iyear=-1&itype=843'
    inner_add_root_url(root_url, page_url, remark = {'classify' : '电视剧'})


# 必须定义 解析网址
def parser(url_info):
    depth = url_info['depth']
    if depth == 0:
        parser_program_url(url_info)
    elif depth == 1:
        parser_program_info(url_info)
    elif depth == 2:
        parser_episode_info(url_info)

def parser_program_url(url_info):
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    classify = remark['classify']

    # 解析
    html, request = tools.get_html_by_requests(root_url)
    if not html:
        base_parser.update_url('PROGRAM_urls', root_url, Constance.EXCEPTION)
        return

    program_blocks = tools.get_tag(html, 'li', {'class' : "list_item"})
    for program_block in program_blocks:
        program_block = str(program_block)

        # 地址
        regex = 'r-props="{id: \'(.*?)\''
        program_id = tools.get_info(program_block, regex, fetch_one = True)
        program_url = 'http://v.qq.com/detail/5/%s.html'%program_id
        base_parser.add_url("PROGRAM_urls", site_id, program_url, depth = 1, remark = {'program_id' : program_id, 'classify' : classify})

    base_parser.update_url("PROGRAM_urls", root_url, Constance.DONE)

def parser_program_info(url_info):
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    program_id = remark['program_id']
    classify = remark['classify']

    # 解析
    html, request = tools.get_html_by_requests(root_url)
    if not html:
        base_parser.update_url('PROGRAM_urls', root_url, Constance.EXCEPTION)
        return

    # 标题
    regex = '<h1 class="video_title_cn" >.*?>(.*?)<'
    program_name = tools.get_info(html, regex, fetch_one = True)
    # 地址
    program_url = root_url
    # 图片地址
    regex = '<img src="(.*?)".*?_stat="info:poster"/>'
    image_url = tools.get_info(html, regex, fetch_one = True)
    image_url = tools.get_full_url('http://', image_url)
    # 集数
    regex = ['更新期数:</span>.*?>(.*?)</span>', '总集数:</span>.*?>(.*?)</span>']
    episode = tools.get_info(html, regex, fetch_one = True)
    # 导演
    regex = '<span class="director">导演</span>.*?info:actor_name">(.*?)<'
    directors = tools.get_info(html, regex, split = '/')
    # 演员
    regex = '_stat="info:actor_name">(.*?)</span>' # 包含导演
    actors = tools.get_info(html, regex, split = '/')
    actors = actors.replace(directors + '/', '') if directors else actors
    # 发布时间
    regex = ['首播时间:</span>.*?>(.*?)<', '出品时间:</span>.*?>(.*?)<']
    release_time = tools.get_info(html, regex, fetch_one = True)
    # 简介
    regex = 'desc_txt">(.*?)</span>'
    summary = tools.get_info(html, regex, fetch_one = True)
    summary = tools.del_html_tag(summary)

    log.debug('''
        program_name    %s
        program_url     %s
        image_url       %s
        episode         %s
        directors       %s
        actors          %s
        release_time    %s
        summary         %s
        '''%(program_name, program_url, image_url, episode, directors, actors, release_time, summary))

    program_mongo_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url, image_url, episode, directors, actors = actors, summary = summary, release_time = release_time)

    # 解析分集信息的地址

    # 综艺（json）
    if classify == '综艺':
        # 月份
        regex = '_stat="series:tab".*?>(\d*)月'
        months = tools.get_info(html, regex)
        # print(months)

        # 年
        regex = '<div class="year_slt_list">.*?data-value="(.*?)"'
        years = tools.get_info(html, regex)
        # print(years)

        for year in years:
            for month in months:
                episode_url = 'http://s.video.qq.com/get_playsource?id=%s&plat=2&type=4&data_type=3&video_type=10&year=%s&month=%s&plname=qq&otype=json'%(program_id, year, month)
                log.debug('%s分集json地址:%s'%(program_name, episode_url))
                base_parser.add_url('PROGRAM_urls', site_id, episode_url, depth = 2, remark = {'program_mongo_id' : program_mongo_id, 'classify' : '综艺'})

    # 电视剧（包含第几集， url）
    elif classify == '电视剧':
        regex = 'series:numbtn".*?<a href="(.*?)".*?<span itemprop="episodeNumber">(.*?)</span>'
        episode_msgs = tools.get_info(html, regex)
        for episode_msg in episode_msgs:
            episode_url = episode_msg[0]
            episode_num = episode_msg[1]
            log.debug('''
                episode_url  %s
                episode_num  %s
                '''%(episode_url, episode_num))
            base_parser.add_url('PROGRAM_urls', site_id, episode_url, depth = 2, remark = {'program_mongo_id' : program_mongo_id,'episode_num' : episode_num, 'program_name' : program_name, 'classify' : '电视剧'})

    base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)

def get_download_url(vid):
    '''
    @summary: 取电视剧的下载地址 参考http://www.jianshu.com/p/eae2b7077e04
              vip 的取不了
    ---------
    @param vid: 分集id
    ---------
    @result:
    '''
    urls = []

    definition = 'sd' # 标清 'shd' 超清, 'hd' 高清, 'sd' 标清
    params = {
        'isHLS': False,
        'charge': 0,
        'vid': vid,
        'defn': definition,
        'defnpayver': 1,
        'otype': 'json',
        'platform': 10901,
        'sdtfrom': 'v1010',
        'host': 'v.qq.com',
        'fhdswitch': 0,
        'show1080p': 1,
    }
    r = requests.get('http://h5vv.video.qq.com/getinfo', params=params, timeout = 30).text
    data_json = r[len('QZOutputJson='):-1]

    data = json.loads(data_json)

    url_prefix = data['vl']['vi'][0]['ul']['ui'][0]['url']
    for stream in data['fl']['fi']:
        if stream['name'] != definition:
            continue
        stream_id = stream['id']

        for d in data['vl']['vi'][0]['cl']['ci']:
            keyid = d['keyid']
            filename = keyid.replace('.10', '.p', 1) + '.mp4'
            params = {
                'otype': 'json',
                'vid': vid,
                'format': stream_id,
                'filename': filename,
                'platform': 10901,
                'vt': 217,
                'charge': 0,
            }
            r = requests.get('http://h5vv.video.qq.com/getkey', params=params, timeout = 30)
            html = r.text[len('QZOutputJson='):-1]
            data = json.loads(html)
            url = '%s/%s?sdtfrom=v1010&vkey=%s' % (url_prefix, filename, data['key'])
            urls.append(url)

        # print ('stream:', stream['name'])
        # for url in urls:
        #     print (url)

    return urls


def parser_episode_info(url_info):

    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    program_mongo_id = remark['program_mongo_id']
    classify = remark['classify']

    if classify == '电视剧':
        episode_url = root_url
        episode_name = remark['program_name'] + '_' + remark['episode_num']
        episode_num = remark['episode_num']
        # vid  http://v.qq.com/x/cover/nuijxf6k13t6z9b/u0023ickfto.html
        vid = root_url[root_url.rfind('/') + 1 : root_url.rfind('.')]
        download_url = get_download_url(vid)
        download_url = '^_^'.join(download_url)

        log.debug('''
                episode_name  %s
                episode_num   %s
                episode_url   %s
                download_url  %s
                '''%(episode_name, episode_num, episode_url, download_url))

        base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_mongo_id, episode_num = episode_num, time_length = '', episode_name = episode_name, download_status = '', download_url = download_url, episode_url = episode_url, summary = '', image_url = '', sto_path = '')

    elif classify == '综艺':
        # 用youget 的qq
        html, request = tools.get_html_by_requests(root_url)
        if not html:
            base_parser.update_url('PROGRAM_urls', root_url, Constance.EXCEPTION)
            return

        episodes_json = html[len('QZOutputJson=') : -1]
        # print(episodes_json)
        episodes_json = tools.get_json(episodes_json)
        episodes = episodes_json.get('PlaylistItem', {}).get('videoPlayList', [])
        for episode in episodes:
            try:
                image_url = episode['pic']
                episode_url = episode['playUrl']  # http://v.qq.com/x/cover/3e70vfbgrss48n8/e00237dneke.html
                episode_name = episode['title']
                vid = episode_url[episode_url.rfind('/') + 1 : episode_url.rfind('.html')]
                print('qq_download_by_vid  begin')
                import time
                b = time.time()
                download_url = qq.qq_download_by_vid(vid)
                print('qq_download_by_vid end time = %s'% str(time.time() - b))
                download_url = '^_^'.join(download_url)

                log.debug('''
                    episode_name  %s
                    image_url     %s
                    episode_url   %s
                    download_url  %s
                    '''%(episode_name, image_url, episode_url, download_url))

                base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_mongo_id, episode_num = '', time_length = '', episode_name = episode_name, download_status = '', download_url = download_url, episode_url = episode_url, summary = '', image_url = image_url, sto_path = '')
            except Exception as e:
                log.error(e)

    base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    url_info = {
    "_id":'2322222222',
    "url" : "http://v.qq.com/detail/5/55308.html",
    "status" : 0,
    "site_id" : 5,
    "depth" : 1,
    "remark" : {
        "program_id" : "55308",
        "program_mongo_id" : "program_mongo_id",
        'classify' : '综艺'
    }
    }

    # url_info = {
    #     "_id" : "5927d8cb534465afd92d5efc",
    #     "site_id" : 5,
    #     "url" : "http://v.qq.com/x/cover/kvc22y4k7j3bt5l/p0344jmehks.html",
    #     "depth" : 2,
    #     "status" : 0,
    #     "remark" : {
    #         "classify" : "电视剧",
    #         "program_mongo_id" : "5927d8cb534465afd92d5efb",
    #         "episode_num" : "1",
    #         'program_name' : '择天记'
    #     }
    # }

    url_info = {
        "_id" : "5930df66534465adadbf5594",
        "depth" : 2,
        "site_id" : 3,
        "status" : 1,
        "remark" : {
            "classify" : "综艺",
            "program_mongo_id" : "5930c86b53446538b6f28b3a"
        },
        "url" : "http://s.video.qq.com/get_playsource?id=1206&plat=2&type=4&data_type=3&video_type=10&year=2013&month=1&plname=qq&otype=json"
    }

    url_info = {
        "_id" : "5930f6625344654e52620b22",
        "depth" : 2,
        "remark" : {
            "program_mongo_id" : "5930c87f53446538b6f28bd3",
            "program_name" : "乡村爱情9（下）",
            "episode_num" : "12",
            "classify" : "电视剧"
        },
        "status" : 3,
        "url" : "https://v.qq.com/x/cover/fd7wc830c0q11qb/y0022mrkify.html",
        "site_id" : 3
    }




    parser(url_info)
    # import time
    # b = time.time()
    # # http://v.qq.com/x/cover/buwi5zidaziteon/p0011qe94th.html
    # download_url = qq.qq_download_by_vid('p0011qe94th')
    # print('qq_download_by_vid end time = %s'% str(time.time() - b))
    # download_url = '^_^'.join(download_url)
    # print(download_url)

