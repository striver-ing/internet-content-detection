import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re

# 必须定义 网站id
SITE_ID = 9
# 必须定义 网站名
NAME = '第一视频'

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

    url = "http://news.v1.cn/V1make.shtml"
    base_parser.add_url('PROGRAM_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    description = url_info['remark']

    html, request = tools.get_html_by_requests(source_url)
    regexs = '<ul node-type="listWrap" class="lastUl">(.*?)<div class="bottom_more">'
    lis = tools.get_info(html, regexs)
    regexs = '<li>(.*?)</li>'
    html_lis = tools.get_info(lis, regexs)
    for html_li in html_lis:
        url_regex = '<a href="(.*?)">'
        url = tools.get_info(html_li, url_regex)
        url = url and url[0] or ''
        if url:
            base_parser.add_url('PROGRAM_urls', site_id, url, depth+1)


        # 取当前页的文章信息
        # 标题

        regexs_program_name = '<a href=".*?">(.*?)</a>'
        program_name = tools.get_info(html_li, regexs_program_name)
        program_name = program_name and program_name[0] or ''

        program_url = url

        #时间
        regexs_image_url = 'data-src="(.*?)"'
        image_url = tools.get_info(html_li, regexs_image_url)
        image_url = image_url and image_url[0] or ''

        episode = 1

        everyone_html = tools.get_html_by_requests(program_url)

        regexs_directors = '<span class="editor" style="color:#333;">(.*?)</span>'
        directors = tools.get_info(everyone_html, regexs_directors)
        directors = directors and directors[0] or ''

        # 摘要
        regexs_summary = '<p class="summaryList_long">(.*?)</p>'
        summary = tools.get_info(everyone_html, regexs_summary)
        summary = summary and summary[0] or ''

        # 更新时间
        regexs_release_time = ' <dt>发布时间：</dt>.*?<dd>(.*?)</dd>'
        release_time = tools.get_info(everyone_html, regexs_release_time)
        release_time = release_time and release_time[0] or ''

        # 下载地址
        regexs_download_url = 'videoUrl=(.*?)"'
        download_url = tools.get_info(everyone_html, regexs_download_url)
        download_url = download_url and download_url[0] or ''

        download_status = 102
        time_length = ''

        log.debug('''
                depth                       = %s
                program_name                = %s
                program_url                 = %s
                image_url                   = %s
                episode                     = %s
                directors                   = %s
                summary                     = %s
                release_time                = %s
             ''' % (depth, program_name, program_url, image_url, episode, directors, summary, release_time))
        if download_url:
            program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url, image_url = image_url,
                                 episode = episode, directors = directors, actors = '', summary = summary,
                                 release_time = release_time)

            # sto_path = '/videos/' + program_name + '.mp4'
            # is_download = tools.download_file(download_url, FILE_LOCAL_PATH, sto_path)
            # download_status = 101 if is_download else 102
            sto_path = ''

            base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode, time_length, program_name, download_status,
                             download_url, program_url, summary, image_url, sto_path)


    # 更新source_url为done
    base_parser.update_url('PROGRAM_urls', source_url, Constance.DONE)

if __name__ == '__main__':
    url_info = {
        "_id": "591bb22bea18a91f200aad10",
        "remark": "",
        "site_id": 9,
        "status": 3,
        "depth": 0,
        "url": "http://news.v1.cn/V1make.shtml"
    }

    parser(url_info)





