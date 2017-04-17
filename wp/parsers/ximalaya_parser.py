import sys
sys.path.append('../../')

import init
from db.mongodb import MongoDB
import base.base_parser as base_parser
import base.constance as Constance
import utils.tools as tools
from utils.log import log

SITE_ID = 1
# 必须定义 网站名
DATA_TYPE = 1
NAME = '喜马拉雅FM'


@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WP_site_info'
    url = 'http://www.ximalaya.com/'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    _db = base_parser.MongoDB()
    _db.set_unique_key('WP_content_episode_info', 'title')
    _db.update('WP_urls', {}, {'status': 0}, multi=True)

    for page_id in range(1, 1001):
        url = 'http://mobile.ximalaya.com/mobile/discovery/v2/category/metadata/albums?calcDimension=hot&categoryId=3&' \
              'device=android&pageId=%d&pageSize=1&version=5.4.81'% page_id
        base_parser.add_url('WP_urls', SITE_ID, url)

def parser(url_info):
    url = url_info['url']
    list_datas = tools.get_json_by_requests(url)
    list_datas = list_datas['list']

    for list_data in list_datas:
        title = list_data['title']
        watched_count = list_data['playsCounts']
        image_url = list_data['coverLarge']
        comment_count = list_data['commentsCount']
        charge_type = list_data['priceTypeId']
        is_finished = list_data['isFinished']
        article_type = list_data['tags']
        origin = list_data['provider']
        episodes = list_data['tracks']
        # uid = list_data['uid']
        author = list_data['nickname']
        album_id = list_data['albumId']
        abstract = list_data['intro']
        score = tools.get_json_value(list_data, 'score')
        # id = list_data['id']
        new_url_2 = 'http://mobile.ximalaya.com/mobile/v1/album/rich?albumId=%s' % album_id
        list_datas_2 = tools.get_json_by_requests(new_url_2)
        content = tools.get_json_value(list_datas_2, 'data.album.intro')
        release_time = tools.get_json_value(list_datas_2, 'data.album.createdAt')
        release_time = tools.timestamp_to_date(release_time/1000)
        update_time = tools.get_json_value(list_datas_2, 'data.album.lastUptrackAt')
        update_time = tools.timestamp_to_date(update_time/1000)
        subscribe_count = tools.get_json_value(list_datas_2, 'data.album.subscribeCount')

        new_url_3 = 'http://mobile.ximalaya.com/mobile/v1/album/track?albumId=%s&device=android&isAsc=true&pageId=1&' \
                    'pageSize=5000&pre_page=1' % album_id

        list_datas_3 = tools.get_json_by_requests(new_url_3)
        lists = tools.get_json_value(list_datas_3, 'data.list')

        log.debug('''
                    书名：                 %s
                    作品类型：             %s
                    集数：                 %s
                    评分：                 %s   (免费作品均无评分）
                    订阅数：               %s
                    作者：                 %s
                    创建时间：             %s
                    最近更新日期：         %s
                    贴图：                 %s
                    播放次数：             %s
                    评论数：               %s   (免费作品均无评论）
                    收费类型：             %s   (0:免费，1:单期购买， 2:全集购买)
                    是否完结：             %s   (0、1:未完结， 2:完结)
                    提供者：               %s
                    简介：                 %s
                    完整介绍：             %s
                    ''' % (title, article_type, episodes, score, subscribe_count, author, release_time, update_time,
                           image_url, watched_count, comment_count, charge_type,
                           is_finished, origin, abstract, content))
        content_id = base_parser.add_wp_content_info('WP_content_info', SITE_ID, title = title, article_type = article_type,
                                        episodes = episodes, score = score, subscribe_count = subscribe_count,
                                        author = author, release_time = release_time, update_time = update_time,
                                        image_url = image_url, watched_count = watched_count, comment_count = comment_count,
                                        charge_type = charge_type, is_finished = is_finished, origin = origin,
                                        abstract = abstract, content = content, data_type=DATA_TYPE)


        for list in lists:
            title = list['title']
            download_url = list['playPathAacv164']
            watched_count = list['playtimes']
            play_length = list['duration']
            comments_count = list['comments']
            create_time = list['createdAt']
            create_time = tools.timestamp_to_date(create_time / 1000)
            # log.debug('''
            #                    书名：                 %s
            #                    下载链接：             %s
            #                    播放次数：             %s
            #                    播放时长：             %s
            #                    评论数:                %s
            #                    创建时间：             %s
            #                    ''' % (
            # title, download_url, watched_count, play_length, comments_count, create_time))
            base_parser.add_wp_content_episode_info('WP_content_episode_info', content_id = content_id,
                                                    title = title, video_url = download_url,
                                                    watched_count = watched_count, play_length = play_length,
                                                    comments_count = comments_count, release_time = create_time,
                                                    data_type=DATA_TYPE)

        base_parser.update_url('WP_urls', url, Constance.DONE)

