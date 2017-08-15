import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import you_get
import base.constance as Constance
import re

# 必须定义 网站id
SITE_ID = 7
# 必须定义 网站名
NAME = '搜狐视频'

FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'program_save_path')

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'PROGRAM_site_info'
    url = "http://so.tv.sohu.com"
    base_parser.add_website_info(table, site_id, url, name)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    def add_root_url(url, start, end):
        html, r = tools.get_html_by_requests(url)
        page_regex = '<div class="ssPages area">.*>(\d*?)</a>.*?<a title="下一页"'
        pages = tools.get_info(html, page_regex)
        pages = pages and pages[0] or ''
        if pages:
            pages = int(pages)
            for page in range(1, pages+1):
                url = start+str(page)+end
                base_parser.add_url('PROGRAM_urls', SITE_ID, url)
    #add_root_url("http://so.tv.sohu.com/list_p1106_p2_p3_p4_p5_p6_p73_p8_p9_2d1_p101_p110_p121_p13.html","http://so.tv.sohu.com/list_p1106_p2_p3_p4_p5_p6_p73_p8_p9_2d1_p10", "_p110_p121_p13.html")
    add_root_url("http://so.tv.sohu.com/list_p1101_p20_p3_p40_p5_p6_p73_p80_p9_p101_p11_p121_p13.html", "http://so.tv.sohu.com/list_p1101_p20_p3_p40_p5_p6_p73_p80_p9_p10", "_p11_p121_p13.html")
    #add_root_url("http://so.tv.sohu.com/list_p1100_p2_p3_p40_p5_p6_p77_p80_p9_2d1_p101_p11_p121_p13.html", "http://so.tv.sohu.com/list_p1100_p2_p3_p40_p5_p6_p77_p80_p9_2d1_p10", "_p11_p121_p13.html")

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    description = url_info['remark']

    html, r = tools.get_html_by_requests(source_url)
    regexs = '<ul class="st-list cfix">(.*?)<div class="ssPages area">'
    lis = tools.get_info(html, regexs)
    regexs = '<li>(.*?)</li>'
    html_lis = tools.get_info(lis, regexs)
    for html_li in html_lis:
        url_regex = '<a href="(.*?)"'
        url = tools.get_info(html_li, url_regex)
        url = url and url[0] or ''
        #取到每一部url
        url = "http:" + url

        everyone_html, r = tools.get_html_by_requests(url)

        # 部 信息
        regexs_program_name = '<h3 class="lh-tit">.*?<a.*?>(.*?)</a>'
        program_name = tools.get_info(html_li, regexs_program_name)
        program_name = program_name and program_name[0] or ''


        # 部 url
        program_url = url

        #部 发布时间
        release_time_regex = '发布时间：(.*?)</p>'
        release_time = tools.get_info(html_li, release_time_regex)
        release_time = release_time and release_time[0] or ''

        # 部 摘要
        regexs_summary = '<span class="full_intro" style="display: none">(.*?)</span>'
        summary = tools.get_info(everyone_html, regexs_summary)
        summary = summary and summary[0] or ''
        summary = tools.del_html_tag(summary)

        # 部 图片
        img_url_regex = '<img.*?src="(.*?)".*?>'
        image_url = tools.get_info(html_li, img_url_regex)
        image_url = image_url and image_url[0] or ''
        image_url = "http:"+image_url

        # log.debug('''
        #          depth                       = %s
        #          program_name                = %s
        #          program_url                 = %s
        #          image_url                   = %s
        #          summary                     = %s
        #          release_time                = %s
        #       ''' % (depth, program_name, program_url, image_url, summary, release_time))

        program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url,
                                                  image_url=image_url,
                                                  episode='', directors='', actors='', summary=summary,
                                                  release_time=release_time)
        print('-=-=-=-=-=-=-=-=-=-=-')

        #获取每集信息json url参数playlistId,variety_year

        everyone_html, r = tools.get_html_by_requests(program_url)
        playlistId_regex = 'var playlistId="(\d*?)";'
        playlistId = tools.get_info(everyone_html, playlistId_regex)
        playlistId = ''.join(playlistId)


        # 获取每集信息json url参数variety_year

        variety_years_regex = '<li class="v-year">(.*?)</li>'
        variety_years_html = tools.get_info(everyone_html, variety_years_regex)
        variety_years_regex = '<em>(\d*?)</em>'
        variety_years = tools.get_info(variety_years_html, variety_years_regex)


        if playlistId and variety_years:
            for variety_year in variety_years:

                episode_json_url = 'http://tv.sohu.com/item/VideoServlet?callback=&source=sohu&id=' + \
                                   playlistId + '&year=' + variety_year + '&month=0&page=1'
                episode_json = tools.get_json_by_requests(episode_json_url)
                # print(tools.dumps_json(episode_json))
                # 获取集数
                episode_json_infos = tools.get_json_value(episode_json, 'videos')
                #episode = len(episode_json_infos)

                for episode_json_info in episode_json_infos:
                    # 集摘要
                    episode_summary = tools.get_json_value(episode_json_info, 'videoDesc')
                    # 集名字
                    episode_name = tools.get_json_value(episode_json_info, 'title')
                    # 集url
                    episode_url = tools.get_json_value(episode_json_info, 'url')
                    # 下载地址
                    episode_download_url = you_get.get_video_url(episode_url)
                    if episode_download_url:
                        episode_download_url = '^_^'.join(episode_download_url)
                    # 集图片地址
                    episode_image_url = tools.get_json_value(episode_json_info, 'pic10')
                    # 当前集数
                    episode_num = tools.get_json_value(episode_json_info, 'showDate')

                    download_status = 102

                    time_length = ''

                    if episode_download_url:
                        # log.debug('''
                        #                         depth                       = %s
                        #                         episode_num                 = %s
                        #                         time_length                 = %s
                        #                         episode_name                = %s
                        #                         episode_url                 = %s
                        #                         episode_download_url        = %s
                        #                         episode_summary             = %s
                        #                         episode_image_url           = %s
                        #
                        #                      ''' % (
                        # depth, episode_num, time_length, episode_name, episode_url, episode_download_url, episode_summary,
                        # episode_image_url))

                        base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num, time_length, episode_name, download_status,
                                                     episode_download_url, episode_url, episode_summary, episode_image_url, sto_path='')
        if playlistId and not variety_years:
            regexs = '<!-- start : juqing title -->(.*?)<!-- end : plot content -->'
            episode_infos = tools.get_info(everyone_html, regexs)
            for episode_info in episode_infos:
                # 集名字
                regex = '<h4><.*?>(.*?)<span></span></a></h4>'
                episode_name = tools.get_info(episode_info, regex)
                episode_name = episode_name and episode_name[0] or ''

                # 摘要
                regex = '<p class="intro synopsis text">(.*?)</p>'
                episode_summary = tools.get_info(episode_info, regex)
                episode_summary = episode_summary and episode_summary[0] or ''
                episode_summary = tools.del_html_tag(episode_summary)

                # 图片url
                regex = '<img src="(.*?)" width=".*?" height=".*?"'
                episode_image_url = tools.get_info(episode_info, regex)
                episode_image_url = episode_image_url and episode_image_url[0] or ''
                episode_image_url = "http:" + episode_image_url

                # 集数
                regex = '<h4><a href=.*?>画心师 第一季(.*?)<span></span></a></h4>'
                episode_num = tools.get_info(episode_info, regex)
                episode_num = episode_num and episode_num[0] or ''

                # url
                regex = '<h4><a href="(.*?)" title=".*?" target="_blank">'
                episode_url = tools.get_info(episode_info, regex)
                episode_url = episode_url and episode_url[0] or ''
                episode_url = "http:" + episode_url

                # 下载地址
                episode_download_url = you_get.get_video_url(episode_url)
                if episode_download_url:
                    episode_download_url = '^_^'.join(episode_download_url)

                download_status = 102

                time_length = ''
                if episode_download_url:
                    log.debug('''
                                           depth                       = %s
                                           episode_num                 = %s
                                           time_length                 = %s
                                           episode_name                = %s
                                           episode_url                 = %s
                                           episode_download_url        = %s
                                           episode_summary             = %s
                                           episode_image_url           = %s

                                        ''' % (
                    depth+1, episode_num, time_length, episode_name, episode_url, episode_download_url, episode_summary,
                    episode_image_url))

                base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num,
                                                     time_length, episode_name, download_status,
                                                     episode_download_url, episode_url, episode_summary,
                                                     episode_image_url, sto_path='')

    # 更新source_url为done
    base_parser.update_url('PROGRAM_urls', source_url, Constance.DONE)

if __name__ == '__main__':
    # url_info = {
    #     "_id": "591bb22bea18a91f200aad10",
    #     "remark": "",
    #     "site_id": 9,
    #     "status": 3,
    #     "depth": 0,
    #     "url": "http://so.tv.sohu.com/list_p1106_p2_p3_p4_p5_p6_p73_p8_p9_2d1_p101_p110_p121_p13.html"
    everyone_html, r = tools.get_html_by_requests('http://tv.sohu.com/item/MTIwOTc1MQ==.html')



