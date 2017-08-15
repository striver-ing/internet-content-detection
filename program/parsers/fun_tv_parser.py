import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re
import you_get

# 必须定义 网站id
SITE_ID = 5
# 必须定义 网站名
NAME = '风行TV'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'program_save_path')

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = "http://best.le.com/"
    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = "http://www.fun.tv/vplay/g-98097/"
    base_parser.add_url('PROGRAM_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    description = url_info['remark']

    def r1(pattern, text):
        m = re.search(pattern, text)
        if m:
            return m.group(1)

    program_name = '风行星风范'
    actors = '姜武,秦海璐,黄海波,柳岩'
    release_time = '2011年07月23日'
    directors = ''
    program_url = 'http://www.fun.tv/vplay/g-98097/'
    summary = ''
    image_url = 'http://img3.funshion.com/sdw?oid=cc09e4ab792d4008d86efcbbbf4c55dc&w=200&h=280'
    id = '98097'
    json_episode_info =  tools.get_json_by_requests('http://pm.funshion.com/v5/media/episode?id='+id+'&cl=aphone&uc=5')
    episode = len(json_episode_info)

    log.debug('''
                    depth                       = %s
                    program_name                = %s
                    program_url                 = %s
                    episode                     = %s
                    summary                     = %s
                    image_url                   = %s

                 ''' % (depth, program_name, program_url, episode, summary, image_url))


    program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url, image_url=image_url,
                                              episode=episode, directors='', actors=actors, summary='',
                                              release_time=release_time)


    if re.match(r'http://www.fun.tv/vplay/.*g-(\w+)', source_url):
        id = r1(r'http://www.fun.tv/vplay/.*g-(\d+)', source_url)
        json_info = tools.get_json_by_requests('http://pm.funshion.com/v5/media/episode?id='+id+'&cl=aphone&uc=5')
        json_episodes_info = tools.get_json_value(json_info, 'episodes')
        for json_episode_info in json_episodes_info:
            vid = tools.get_json_value(json_episode_info, 'id')

            episode_name = tools.get_json_value(json_episode_info, 'name')

            image_episode_info = tools.get_json_value(json_episode_info, 'still')

            episode_url = tools.get_json_value(json_episode_info, 'num')
            episode_url = 'http://pm.funshion.com/v5/media/share?id=98097&num='+episode_url

            episode_num = tools.get_json_value(json_episode_info, 'num')

            #总集数
            episode = len(json_episode_info)

            time_length = ''
            episode_summary = ''
            download_status = ''

            download_url = ''

            log.debug('''
                                    depth                       = %s
                                    episode_num                 = %s
                                    time_length                 = %s
                                    episode_name                = %s
                                    episode_url                 = %s
                                    download_url                = %s
                                    episode_summary             = %s
                                    image_episode_info          = %s

                                 ''' % (
            depth, episode_num, time_length, episode_name, episode_url, download_url, episode_summary,
            image_episode_info))
            base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num, time_length,
                                                episode_name, download_status,
                                                download_url, episode_url, episode_summary, image_episode_info, '')

        # 取当前页的文章信息
        # 标题




    # 更新source_url为done
    base_parser.update_url('PROGRAM_urls', source_url, Constance.DONE)

if __name__ == '__main__':
    # url_info = {
    #     "_id": "591bb22bea18a91f200aad10",
    #     "remark": "",
    #     "site_id": 9,
    #     "status": 3,
    #     "depth": 0,
    #     "url": "http://news.v1.cn/V1make.shtml"
    # }
    #
    # parser(url_info)

    print(you_get.git)
    print(help(you_get))





