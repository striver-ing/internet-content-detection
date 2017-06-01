import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance

# 必须定义 网站id
SITE_ID = 6
# 必须定义 网站名
NAME = '乐视'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'program_save_path')

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = 'http://list.le.com/listn/cs2_o20_p.html'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    def get_page_count(url):
        html, r = tools.get_html_by_requests(url)
        regex = '<div class="w-pages w-pages-default ">.*>(\d*?)</a>.*?</div>'
        page_count = tools.get_info(html, regex, fetch_one = True)
        return int(page_count) if page_count else 1

    def inner_add_root_url(root_url, page_url):
        page_count = get_page_count(root_url)
        for page in range(1, page_count + 1):
            url = page_url%page
            base_parser.add_url('PROGRAM_urls', SITE_ID, url)
    # 综艺
    root_url = 'http://list.mgtv.com/1/2836094---------2-1---.html'
    page_url = 'http://list.mgtv.com/1/2836094---------2-%d---.html'
    inner_add_root_url(root_url, page_url)

    # 电视剧
    root_url = 'http://list.mgtv.com/2/2836607---------2-1---.html'
    root_url = 'http://list.mgtv.com/2/2836607---------2-%d---.html'
    inner_add_root_url(root_url, page_url)

# 必须定义 解析网址
def parser(url_info):
    depth = url_info['depth']
    if depth == 0:
        parser_program(url_info)
    elif depth == 1:
        parser_episode_detail_url(url_info)
    elif depth == 2:
        parser_episode_info(url_info)

def parser_program(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    # 解析
    html, request = tools.get_html_by_requests(root_url)
    if not html:
        base_parser.update_url('PROGRAM_urls', root_url, Constance.EXCEPTION)
        return

    regex = '<li class="v-item-v5.*?">(.*?)</li>'
    video_blocks = tools.get_info(html, regex)
    for video_block in video_blocks:
        regex = '<a class="u-video" href="(.*?)"'
        program_url = tools.get_info(video_block, regex, fetch_one = True)
        program_id = program_url[program_url.find('b/') + 2 : program_url.rfind('/')]
        program_url = 'http://www.mgtv.com/h/%s.html'%program_id

        regex = '<img class="u-image" src="(.*?)"'
        image_url = tools.get_info(video_block, regex, fetch_one = True)

        regex = 'em class="u-time">(.*?)</em>'
        episode = tools.get_info(video_block, regex, fetch_one = True)

        regex = '<a class="u-title".*?>(.*?)</a>'
        title = tools.get_info(video_block, regex, fetch_one = True)

        regex = '<span class="u-desc">(.*?)</span>'
        actors_block = tools.get_info(video_block, regex, fetch_one = True)
        regex = '<a .*?>(.*?)</a?'
        actors = tools.get_info(actors_block, regex)
        actors = '/'.join(actors) if actors else '暂无'

        detail_html, r = tools.get_html_by_requests(program_url)
        regex = '<em class="label">简介.*?<span>(.*?)</span>'
        summary = tools.get_info(detail_html, regex, fetch_one = True) if detail_html else ''

        log.debug('''
            program_url %s
            image_url   %s
            episode     %s
            title       %s
            actors      %s
            summary     %s
            '''%(program_url, image_url, episode, title, actors, summary))

        program_mongo_id = base_parser.add_program_info('PROGRAM_info', site_id, title, program_url, image_url, episode, directors = '', actors = actors, summary = summary, release_time = '')

        # 获取集信息url  没月份参数默认是最近月份的数据
        episode_detail_url = 'http://pcweb.api.mgtv.com/variety/showlist?collection_id=' + program_id
        base_parser.add_url('PROGRAM_urls', SITE_ID, episode_detail_url, depth = 1, remark = {'program_mongo_id' : program_mongo_id, 'program_id' : program_id})

    base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)

# 解析分集详细信息地址
def parser_episode_detail_url(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    program_id = remark['program_id']
    program_mongo_id = remark['program_mongo_id']

    episode_json = tools.get_json_by_requests(root_url)
    if not episode_json:
        base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)
        return

    code = episode_json.get('code')
    if code is not 200:
        base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)
        return

    episode_data = episode_json.get('data', {})
    # 解析分集详细信息地址
    episode_list = episode_data.get('list', [])
    for episode in episode_list:
        episode_id = episode['video_id']
        episode_detail_url = 'http://pcweb.api.mgtv.com/player/video?video_id=' + episode_id
        base_parser.add_url('PROGRAM_urls', SITE_ID, episode_detail_url, depth = 2, remark = {'program_mongo_id' : program_mongo_id, 'program_id' : program_id})

    # 解析其他年份和月份的url
    episode_years = episode_data.get('tab_y', [])
    episode_months = episode_data.get('tab_m', [])
    for episode_year in episode_years: #
        year = episode_year['t']
        temp_program_id = episode_year['id']
        episode_list_url = 'http://pcweb.api.mgtv.com/variety/showlist?collection_id=%s'%temp_program_id
        # 添加url 没月份参数默认是最近月份的数据
        base_parser.add_url('PROGRAM_urls', SITE_ID, episode_list_url, depth = 1, remark = {'program_mongo_id' : program_mongo_id, 'program_id' : temp_program_id})

    for episode_month in episode_months[1:]: #去掉最近月份的数据
        episode_month = episode_month['m']
        episode_list_url = 'http://pcweb.api.mgtv.com/variety/showlist?collection_id=%s&month=%s'%(program_id, episode_month)
        # 添加url
        base_parser.add_url('PROGRAM_urls', SITE_ID, episode_list_url, depth = 1, remark = {'program_mongo_id' : program_mongo_id, 'program_id' : program_id})

    base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)

def parser_episode_info(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']
    program_id = remark['program_id']
    program_mongo_id = remark['program_mongo_id']

    episode_json = tools.get_json_by_requests(root_url)
    if not episode_json:
        base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)
        return

    code = episode_json.get('code')
    if code is not 200:
        base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)
        return

    episode_data = episode_json.get('data', {})
    episode_info = episode_data.get('info', {})

    name = episode_info.get('title', '')
    url = episode_info.get('url', '')
    image_url = episode_info.get('thumb', '')
    episode_num = episode_info.get('series', '')
    summary = episode_info.get('desc', '')
    time_length = episode_info.get('duration', '')

    episode_download_url = episode_data.get('stream', [{'url':''}])[0].get('url')
    episode_download_url = 'http://disp.titan.mgtv.com' + episode_download_url

    episode_download_info = tools.get_json_by_requests(episode_download_url)
    if episode_download_info:
        episode_download_url = episode_download_info.get('info', '')
    else:
        episode_download_url = ''

    log.debug('''
        program_mongo_id     %s
        name                 %s
        url                  %s
        image_url            %s
        episode_num          %s
        summary              %s
        time_length          %s
        episode_download_url %s
        '''%(program_mongo_id, name, url, image_url, episode_num, summary, time_length, episode_download_url))

    base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_mongo_id, episode_num = episode_num, time_length = time_length, episode_name = name, download_status = '', download_url = episode_download_url, episode_url = url, summary = summary, image_url = image_url, sto_path = '')
    base_parser.update_url('PROGRAM_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    url_info = {
    "_id":'2322222222',
    "url" : "http://pcweb.api.mgtv.com/player/video?video_id=3763506",
    "status" : 0,
    "site_id" : 5,
    "depth" : 2,
    "remark" : {
        "program_id" : "101575",
        "program_mongo_id" : "program_mongo_id"
    }
    }

    parser(url_info)

