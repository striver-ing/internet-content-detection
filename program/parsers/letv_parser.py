import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import re
import you_get
import time
import random
# 必须定义 网站id
SITE_ID = 10
# 必须定义 网站名
NAME = '乐视TV'

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

    def add_type_url(url):
        base_parser.add_url('PROGRAM_urls', SITE_ID, url)

    add_type_url('http://list.le.com/listn/cs4_o_p.html')
    add_type_url('http://list.le.com/listn/cs9_o17_p.html')
    add_type_url('http://list.le.com/listn/cs1_o4_p.html')
    add_type_url('http://list.le.com/listn/cs2_o51_p.html')
    add_type_url('http://list.le.com/listn/cs11_o1_p.html')
# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    source_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    description = url_info['remark']

    def get_tkey(t):
        def ror(val, key):
            i = 0
            while (i < key):
                val = (0x7fffffff & (val >> 1)) | ((val & 1) << 31)
                i += 1

            return val

        key = 185025305
        val = ror(t, key % 17)
        val = val ^ key
        return val

    def getdownload(episode_download_url_json):
        episode_json = tools.get_json_by_requests(episode_download_url_json)
        #print(episode_download_url_json)
        episode_download_url = tools.get_json_value(episode_json, 'msgs.playurl.domain')
        episode_download_url = episode_download_url and episode_download_url[0] or ''
        #print('-----',episode_download_url)
        episode_download_url_definition = tools.get_json_value(episode_json, 'msgs.playurl.dispatch.1080p')
        episode_download_url_definition = episode_download_url_definition and episode_download_url_definition[0] or ''
        print(episode_download_url_definition, '*********')
        episode_download_url = episode_download_url + episode_download_url_definition
        episode_download_url += "&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=Linux&tag=letv&sign=letv&expect=3&tn={}&pay=0&iscpn=f9051&rateid={}".format(random.random(), '1080p')
        episode_download_url_json = tools.get_json_by_requests(episode_download_url)
        episode_download_url = tools.get_json_value(episode_download_url_json, 'location')
        return episode_download_url

    if depth==0:
        cs_regex = 'cs(.*?)_'
        o_regex = 'cs.*?_o(.*?)_p'
        cs = tools.get_info(source_url, cs_regex)
        cs_value = cs and cs[0] or ''
        o = tools.get_info(source_url, o_regex)
        o_value = o and o[0] or ''
        #print('1'+o_value+'2','***', cs_value)
        url='http://list.le.com/apin/chandata.json?cs='+cs_value+'&_o='+o_value+'&_p='
        base_parser.add_url('PROGRAM_urls', site_id, url, depth+1)
    if depth==1:
        page = '1'
        #电视剧
        if 'cs=2' in source_url:
            while True:
                json = tools.get_json_by_requests(source_url+page)
                json_list = tools.get_json_value(json, 'album_list')
                #print(source_url)
                for info in json_list:
                    image_url = tools.get_json_value(info, 'images.1080*608')
                    program_name = tools.get_json_value(info, 'name')
                    program_url = tools.get_json_value(info, 'aid')
                    program_url = 'http://www.le.com/tv/'+program_url+'.html'
                    episode = tools.get_json_value(info, 'nowEpisodes')

                    directors = tools.get_json_value(info, 'directory')
                    #print(type(directors))
                    directors =','.join(tools.get_json(directors).values())

                    actors = tools.get_json_value(info, 'starring')
                    actors = ' '.join(actors.values())

                    summary = tools.get_json_value(info, 'description')

                    release_time = tools.get_json_value(info, 'releaseDate')
                    release_time = int(release_time)/1000
                    x = time.localtime(release_time)
                    release_time = time.strftime("%Y-%m-%d", x)

                    log.debug('''
                                    depth                       = %s
                                    program_name                = %s
                                    program_url                 = %s
                                    image_url                   = %s
                                    episode                     = %s
                                    directors                   = %s
                                    actors                      = %s
                                    summary                     = %s
                                    release_time                = %s
                                 ''' % (
                    depth, program_name, program_url, image_url, episode, directors, actors, summary, release_time))

                    program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url,
                                                              image_url=image_url, episode = episode, directors = directors, actors = actors,
                                                              summary = summary, release_time = release_time)

                    episode_url = tools.get_json_value(info, 'vids')
                    episode_url = episode_url+','
                    regex = '(\d*?),'
                    episode_urls = tools.get_info(episode_url, regex)
                    for episode_url_num in episode_urls:

                        episode_url = 'http://www.le.com/ptv/vplay/'+episode_url_num+'.html'

                        episode_download_url_json = 'http://player-pc.le.com/mms/out/video/playJson?id={}&platid=1&splatid=101&format=1&tkey={}&domain=www.le.com&dvtype=1000&devid=49BDB62DC27B044CCD48E49CCF38EAAE3B095825&region=cn&source=1000&accessyx=1'.format(episode_url_num, get_tkey(int(time.time())))

                        episode_json = tools.get_json_by_requests(episode_download_url_json)

                        episode_image_url = tools.get_json_value(episode_json, 'msgs.playurl.pic')

                        episode_name = tools.get_json_value(episode_json, 'msgs.playurl.title')

                        episode_num_regex = "(\d*?)"
                        episode_num = tools.get_info(episode_name, episode_num_regex)
                        episode_num = episode_num and episode_num[0] or ''

                        episode_download_url = getdownload(episode_download_url_json)

                        time_length = ''

                        episode_summary = ''

                        download_status = ''

                        log.debug('''
                                                   depth                       = %s
                                                   episode_num                 = %s
                                                   time_length                 = %s
                                                   episode_name                = %s
                                                   episode_url                 = %s
                                                   download_url                = %s
                                                   episode_summary             = %s
                                                   episode_image_url           = %s

                                                ''' % (
                        depth , episode_num, time_length, episode_name, episode_url, episode_download_url, episode_summary,
                        episode_image_url))

                        base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num, time_length,
                                                             episode_name, download_status,
                                                             episode_download_url, episode_url, episode_summary, episode_image_url, '')

                page = str(int(page)+1)

                if not json_list :
                    return False

        #体育
        if 'cs=4' in source_url:
            while True:
                json = tools.get_json_by_requests(source_url + page)
                video_list = tools.get_json_value(json, 'video_list')
                for info in video_list:
                    episode_name = tools.get_json_value(info, 'name')

                    episode_num = tools.get_json_value(info, 'name')
                    regex_episode_num ='第(.*?)期'
                    episode_num = tools.get_info(episode_num, regex_episode_num)
                    episode_num = ''.join(episode_num)

                    episode_summary = tools.get_json_value(info, 'description')

                    episode_image_url = tools.get_json_value(info, 'images.1080*608')

                    episode_url_num = tools.get_json_value(info, 'vid')
                    episode_url = 'http://sports.le.com/video/'+episode_url_num+'.html'

                    #获取Vid 也就是num
                    episode_download_url_json = 'http://player-pc.le.com/mms/out/video/playJson?id={}&platid=1&splatid=101&format=1&tkey={}&domain=www.le.com&dvtype=1000&devid=49BDB62DC27B044CCD48E49CCF38EAAE3B095825&region=cn&source=1000&accessyx=1'.format(
                        episode_url_num, get_tkey(int(time.time())))

                    episode_download_url = getdownload(episode_download_url_json)

                    program_name = tools.get_json_value(info, 'albumName')

                    summary = ''
                    program_url = ''
                    actors= ''
                    directors = ''
                    release_time = ''
                    image_url = ''
                    episode =''
                    aid = tools.get_json_value(info, 'aid')
                    download_status = 102
                    time_length = ''

                    log.debug('''
                                depth                       = %s
                                program_name                = %s
                                program_url                 = %s
                                image_url                   = %s
                                episode                     = %s
                                directors                   = %s
                                actors                      = %s
                                summary                     = %s
                                release_time                = %s
                                aid                         = %s
                    ''' % (
                    depth, program_name, program_url, image_url, episode, directors, actors, summary, release_time, aid))

                    program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url,
                                                              image_url=image_url, episode = episode, directors = directors, actors = actors, summary = summary,
                                                              release_time = release_time, _id=aid)
                    log.debug('''
                               depth                       = %s
                               episode_num                 = %s
                               time_length                 = %s
                               episode_name                = %s
                               episode_url                 = %s
                               download_url                = %s
                               episode_summary             = %s
                               episode_image_url           = %s
                            ''' % (
                        depth, episode_num, time_length, episode_name, episode_url, episode_download_url,
                        episode_summary, episode_image_url))
                    base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode, time_length,
                                                          program_name, download_status,
                                                          episode_download_url, program_url, summary, image_url, '')
                page = str(int(page) + 1)

                if not json_list:
                    return False

        # 综艺
        if 'cs=11' in source_url:
            while True:
                json = tools.get_json_by_requests(source_url + page)
                video_list = tools.get_json_value(json, 'video_list')
                for info in video_list:
                    episode_name = tools.get_json_value(info, 'name')

                    episode_num = tools.get_json_value(info, 'name')
                    regex_episode_num ='第(.*?)期'
                    episode_num = tools.get_info(episode_num, regex_episode_num)
                    episode_num = ''.join(episode_num)

                    episode_summary = tools.get_json_value(info, 'description')

                    episode_image_url = tools.get_json_value(info, 'images.1080*608')

                    episode_url_num = tools.get_json_value(info, 'vid')
                    episode_url = 'http://www.le.com/ptv/vplay/'+episode_url_num+'.html'

                    #获取Vid 也就是num
                    episode_download_url_json = 'http://player-pc.le.com/mms/out/video/playJson?id={}&platid=1&splatid=101&format=1&tkey={}&domain=www.le.com&dvtype=1000&devid=49BDB62DC27B044CCD48E49CCF38EAAE3B095825&region=cn&source=1000&accessyx=1'.format(
                    episode_url_num, get_tkey(int(time.time())))

                    episode_download_url = getdownload(episode_download_url_json)

                    program_name = tools.get_json_value(info, 'albumName')

                    summary = ''
                    actors= ''
                    directors = ''
                    release_time = ''
                    image_url = ''
                    episode =''
                    aid = tools.get_json_value(info, 'aid')
                    program_url = ''
                    download_status = 102
                    time_length = ''

                    log.debug('''
                                depth                       = %s
                                program_name                = %s
                                program_url                 = %s
                                image_url                   = %s
                                episode                     = %s
                                directors                   = %s
                                actors                      = %s
                                summary                     = %s
                                release_time                = %s
                                aid                         = %s
                    ''' % (
                    depth, program_name, program_url, image_url, episode, directors, actors, summary, release_time, aid))

                    program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url,
                                                              image_url=image_url, episode = episode, directors = directors, actors = actors, summary = summary,
                                                              release_time = release_time, _id=aid)
                    log.debug('''
                               depth                       = %s
                               episode_num                 = %s
                               time_length                 = %s
                               episode_name                = %s
                               episode_url                 = %s
                               download_url                = %s
                               episode_summary             = %s
                               episode_image_url           = %s
                    ''' % (
                    depth, episode_num, time_length, episode_name, episode_url, episode_download_url,
                    episode_summary, episode_image_url))

                    base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num, time_length,
                                                         episode_name, download_status,
                                                          episode_download_url, episode_url, episode_summary, episode_image_url, '')
                page = str(int(page) + 1)
                if not video_list:
                    return False

        # 音乐
        if 'cs=9' in source_url:
            while True:
                json = tools.get_json_by_requests(source_url + page)
                video_list = tools.get_json_value(json, 'video_list')
                for info in video_list:
                    episode_name = tools.get_json_value(info, 'name')

                    episode_num = tools.get_json_value(info, 'name')
                    regex_episode_num ='(\d*?):'
                    episode_num = tools.get_info(episode_num, regex_episode_num)
                    episode_num = ''.join(episode_num)

                    episode_summary = tools.get_json_value(info, 'description')

                    episode_image_url = tools.get_json_value(info, 'images.1080*608')

                    episode_url_num = tools.get_json_value(info, 'vid')
                    episode_url = 'http://www.le.com/ptv/vplay/'+episode_url_num+'.html'

                    #获取Vid 也就是num
                    episode_download_url_json = 'http://player-pc.le.com/mms/out/video/playJson?id={}&platid=1&splatid=101&format=1&tkey={}&domain=www.le.com&dvtype=1000&devid=49BDB62DC27B044CCD48E49CCF38EAAE3B095825&region=cn&source=1000&accessyx=1'.format(
                        episode_url_num, get_tkey(int(time.time())))

                    episode_download_url = getdownload(episode_download_url_json)

                    program_name = tools.get_json_value(info, 'albumName')

                    summary = ''
                    actors = tools.get_json_value(info, 'actor').values()
                    actors = ''.join(actors)
                    #print('**********', actors)

                    directors = ''
                    release_time = ''
                    image_url = ''
                    episode =''
                    aid = tools.get_json_value(info, 'aid')
                    program_url = ''
                    download_status = 102
                    time_length = ''

                    log.debug('''
                                depth                       = %s
                                program_name                = %s
                                program_url                 = %s
                                image_url                   = %s
                                episode                     = %s
                                directors                   = %s
                                actors                      = %s
                                summary                     = %s
                                release_time                = %s
                                aid                         = %s
                              ''' % (
                        depth, program_name, program_url, image_url, episode, directors, actors, summary, release_time, aid))

                    program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url,
                                                              image_url=image_url, episode = episode, directors = directors, actors = actors, summary = summary,
                                                              release_time = release_time, _id=aid)
                    log.debug('''
                               depth                       = %s
                               episode_num                 = %s
                               time_length                 = %s
                               episode_name                = %s
                               episode_url                 = %s
                               download_url                = %s
                               episode_summary             = %s
                               episode_image_url           = %s
                            ''' % (
                        depth, episode_num, time_length, episode_name, episode_url, episode_download_url,
                        episode_summary, episode_image_url))
                    base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num,
                                                         time_length, episode_name, download_status,
                                                         episode_download_url, episode_url, episode_summary,
                                                         episode_image_url, '')

                page = str(int(page) + 1)
                if not video_list:
                    return False
    # #     # 取当前页的文章信息
    # #     # 标题
    # #
    # #
    # #     everyone_html = tools.get_html_by_requests(program_url)
    # #
    # #     regexs_directors = '<span class="editor" style="color:#333;">(.*?)</span>'
    # #     directors = tools.get_info(everyone_html, regexs_directors)
    # #     directors = directors and directors[0] or ''
    # #
    # #     # 摘要
    # #     regexs_summary = '<p class="summaryList_long">(.*?)</p>'
    # #     summary = tools.get_info(everyone_html, regexs_summary)
    # #     summary = summary and summary[0] or ''
    # #
    # #     # 更新时间
    # #     regexs_release_time = ' <dt>发布时间：</dt>.*?<dd>(.*?)</dd>'
    # #     release_time = tools.get_info(everyone_html, regexs_release_time)
    # #     release_time = release_time and release_time[0] or ''
    # #
    # #     # 下载地址
    # #     regexs_download_url = 'videoUrl=(.*?)"'
    # #     download_url = tools.get_info(everyone_html, regexs_download_url)
    # #     download_url = download_url and download_url[0] or ''
    # #
    # #     download_status = 102
    # #     time_length = ''
    # #
    # #
    # #     if download_url:
    # #         program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url, image_url = image_url,
    # #                              episode = episode, directors = directors, actors = '', summary = summary,
    # #                              release_time = release_time)
    # #
    # #         sto_path = '/video/' + program_name + '.mp4'
    # #         is_download = tools.download_file(download_url, FILE_LOCAL_PATH, sto_path)
    # #         download_status = 101 if is_download else 102
    # #
    # #         base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode, time_length, program_name, download_status,
    # #                          download_url, program_url, summary, image_url, sto_path)
    # #
    # #
    # # # 更新source_url为done
    # # base_parser.update_url('PROGRAM_urls', source_url, Constance.DONE)

        # 电影
        if 'cs=1' in source_url:
            while True:
                json = tools.get_json_by_requests(source_url+page)
                json_list = tools.get_json_value(json, 'album_list')
                #print(source_url)
                for info in json_list:
                    image_url = tools.get_json_value(info, 'images.1080*608')
                    program_name = tools.get_json_value(info, 'name')
                    program_url = tools.get_json_value(info, 'aid')
                    program_url = 'http://www.le.com/movie/'+program_url+'.html'
                    episode = ' '

                    directors = tools.get_json_value(info, 'directory')
                    directors =','.join(tools.get_json(directors).values())


                    actors = tools.get_json_value(info, 'starring')
                    actors = ' '.join(actors.values())

                    summary = tools.get_json_value(info, 'description')

                    release_time = tools.get_json_value(info, 'releaseDate')
                    release_time = int(release_time)/1000
                    x = time.localtime(release_time)
                    release_time = time.strftime("%Y-%m-%d", x)

                    log.debug('''
                                    depth                       = %s
                                    program_name                = %s
                                    program_url                 = %s
                                    image_url                   = %s
                                    episode                     = %s
                                    directors                   = %s
                                    actors                      = %s
                                    summary                     = %s
                                    release_time                = %s
                                 ''' % (
                    depth, program_name, program_url, image_url, episode, directors, actors, summary, release_time))

                    program_id = base_parser.add_program_info('PROGRAM_info', site_id, program_name, program_url,
                                                              image_url=image_url, episode = episode, directors = directors, actors = actors,
                                                              summary = summary, release_time = release_time)

                    episode_url = tools.get_json_value(info, 'vids')
                    episode_url = episode_url+','
                    regex = '(.*?),'
                    episode_urls = tools.get_info(episode_url, regex)

                    for episode_url_num in episode_urls:

                        episode_url = 'http://www.le.com/ptv/vplay/'+episode_url_num+'.html'

                        episode_download_url_json = 'http://player-pc.le.com/mms/out/video/playJson?id={}&platid=1&splatid=101&format=1&tkey={}&domain=www.le.com&dvtype=1000&devid=49BDB62DC27B044CCD48E49CCF38EAAE3B095825&region=cn&source=1000&accessyx=1'.format(episode_url_num, get_tkey(int(time.time())))
                        print(episode_download_url_json)
                        episode_json = tools.get_json_by_requests(episode_download_url_json)

                        episode_image_url = tools.get_json_value(episode_json, 'msgs.playurl.pic')

                        episode_name = tools.get_json_value(episode_json, 'msgs.playurl.title')

                        episode_num_regex = "第(.*?)期"
                        episode_num = tools.get_info(episode_name, episode_num_regex)
                        episode_num = episode_num and episode_num[0] or ''

                        episode_download_url = getdownload(episode_download_url_json)

                        time_length = ''

                        episode_summary = ''

                        download_status = ''

                        log.debug('''
                                                   depth                       = %s
                                                   episode_num                 = %s
                                                   time_length                 = %s
                                                   episode_name                = %s
                                                   episode_url                 = %s
                                                   download_url                = %s
                                                   episode_summary             = %s
                                                   episode_image_url           = %s

                                                ''' % (
                        depth , episode_num, time_length, episode_name, episode_url, episode_download_url, episode_summary,
                        episode_image_url))

                        base_parser.add_program_episode_info('PROGRAM_EPISODE_info', site_id, program_id, episode_num, time_length,
                                                             episode_name, download_status,
                                                             episode_download_url, episode_url, episode_summary, episode_image_url, '')

                page = str(int(page)+1)

                if not json_list :
                    return False

if __name__ == '__main__':
    url_info = {
        "_id": "591bb22bea18a91f200aad10",
        "remark": "",
        "site_id": 9,
        "status": 3,
        "depth": 1,
        "url": "http://list.le.com/apin/chandata.json?cs=1&_o=4&_p=1"
    }
    parser(url_info)








