import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance

# 必须定义 网站id
SITE_ID = 5
# 必须定义 网站名
NAME = '芒果TV'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'program_save_path')

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = 'http://list.mgtv.com'

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

    # 综艺
    url = 'http://list.mgtv.com/1/2836094---------2-1-0--.html'
    base_parser.add_url('PROGRAM_urls', SITE_ID, url)

    # 电视剧
    url = 'http://list.mgtv.com/2/2836607---------2-1-0--.html'
    base_parser.add_url('PROGRAM_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    # 解析
    html, request = tools.get_html_by_requests(root_url)
    if not html:
        base_parser.update_url('urls', root_url, Constance.EXCEPTION)
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

        base_parser.add_program_info('PROGRAM_info', site_id, title, program_url, image_url, episode, directors = '', actors = actors, summary = summary, release_time = '')

    base_parser.update_url('urls', root_url, Constance.DONE)

if __name__ == '__main__':
    url_info = {
    "_id":'2322222222',
    "site_id" : 8,
    "status" : 2,
    "depth" : 0,
    "url" : "http://list.mgtv.com/1/2836094---------2-1-0--.html",
    "remark" : ""
    }

    parser(url_info)

