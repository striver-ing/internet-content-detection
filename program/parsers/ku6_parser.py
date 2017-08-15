import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re
import time

# 必须定义 网站id
SITE_ID = 6
# 必须定义 网站名
NAME = '酷6视频'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'program_save_path')

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = "http://news.v1.cn/V1make.shtml"
    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    def add_type_url(url):
        base_parser.add_url('PROGRAM_urls', SITE_ID, url)

    add_type_url('http://ent.ku6.com/c2014/3007/s200703046/')
    add_type_url('http://www.ku6.com/c2015/6380/s200876382/')
    add_type_url('http://ent.ku6.com/c2014/1263/s200703016/')
    add_type_url('http://ent.ku6.com/c2014/8911/s200702084/')
    add_type_url('http://www.ku6.com/c2015/6402/s200876426/')

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    description = url_info['remark']

    html, request = tools.get_html_by_requests(source_url,code='GBK')
    episode_list = 'var url = "(.*?)"'
    episode_list_json = tools.get_info(html, episode_list)
    episode_list_json = episode_list_json and episode_list_json[0] or ''

    episode_list_json_url = episode_list_json+'&cb=jsonp'+str(int(time.time()))
    episode_list_json_url = episode_list_json_url.replace("\\","")
    #print(episode_list_json_url)
   # base_parser.add_url('PROGRAM_urls', site_id, url, depth+1)


    # 取类型

    # 标题
    regexs_program_name = '<meta name="keywords" content="(.*?)" />'
    program_name = tools.get_info(html, regexs_program_name)
    program_name = program_name and program_name[0] or ''

    program_url = source_url

    episode_list_json_html, r = tools.get_html_by_requests(episode_list_json_url)

    regexs = 'jsonp\d*?\((.*)\)'
    episode_list_json = tools.get_info(episode_list_json_html, regexs)
    episode_list_json = episode_list_json and episode_list_json[0] or ''
    episode_list_json = tools.dumps_json(episode_list_json)

    episode_list_json_value_list = tools.get_json_value(episode_list_json, 'data.list')

    episode = len(episode_list_json_value_list)

    summary = ''

    log.debug('''
                    depth                       = %s
                    program_name                = %s
                    program_url                 = %s
                    episode                     = %s
                    summary                     = %s

                 ''' % (depth, program_name, program_url, episode, summary))

    program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url, image_url='',
                                              episode=episode, directors='', actors='', summary=summary,
                                              release_time='')

    for episode_info in episode_list_json_value_list:
        episode_name = tools.get_json_value(episode_info, 'title')

        episode_image_url = tools.get_json_value(episode_info, 'picurl')

        episode_url = tools.get_json_value(episode_info, 'podurl')

        episode_summary = tools.get_json_value(episode_info, 'desc')

        episode_num = tools.get_json_value(episode_info, 'title')

        episode_num_regex = '第(\d*?)期'
        episode_num = tools.get_info(episode_num, episode_num_regex)
        episode_num = episode_num and episode_num[0] or ''
        if episode_num:
            episode_num = '第'+episode_num+'期'

        download_url_json_str = tools.get_json_value(episode_info, 'vid')

        download_url_json_url = 'http://v.ku6.com/fetchVideo4Player/'+download_url_json_str+'.html'
        download_url_json = tools.get_json_by_requests(download_url_json_url)
        download_url = tools.get_json_value(download_url_json, 'data.f')

        download_status = 102
        time_length = ''


        if download_url:
        #     sto_path = '/video/' + program_name + '.mp4'
        #     is_download = tools.download_file(download_url, FILE_LOCAL_PATH, sto_path)
        #     download_status = 101 if is_download else 102
            log.debug('''
                                depth                       = %s
                                episode_num                 = %s
                                time_length                 = %s
                                episode_name                = %s
                                episode_url                 = %s
                                download_url                = %s
                                episode_summary             = %s
                                episode_image_url           = %s

                             ''' % (depth+1, episode_num, time_length, episode_name, episode_url, download_url, episode_summary, episode_image_url))
            base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num, time_length, episode_name, download_status,
                                 download_url, episode_url, episode_summary, episode_image_url, '')


        # 更新source_url为done
    base_parser.update_url('PROGRAM_urls', source_url, Constance.DONE)

if __name__ == '__main__':
    url_info = {
        "_id": "591bb22bea18a91f200aad10",
        "remark": "",
        "site_id": 8,
        "status": 3,
        "depth": 0,
        "url": "http://ent.ku6.com/c2014/1263/s200703016/"
    }
    parser(url_info)





