# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 11:05
---------
@summary: 提供一些操作数据库公用的方法
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init

import base.constance as Constance
import utils.tools as tools
from db.mongodb import MongoDB
from text_cluster.cut_text import CutText

db = MongoDB()
cut_text = CutText()

def get_contained_key(title, content, key1, key2, key3):
    text = title + content

    # 过滤
    if tools.get_info(text, key3):
        return '', 0

    # 取包含的关键字
    contained_key = []
    contained_key_count = 0

    def get_weigth(text, keys, key_weigth):
        weigth = 0
        contained_key = []

        for key in keys:
            for cut_key in cut_text.cut_for_keyword(key):
                if cut_key.lower() in text.lower():
                    weigth += key_weigth
                    contained_key.append(cut_key)

        return weigth, contained_key

    # 判断标题
    # 标题中包含key1 权重+ 125
    result = get_weigth(title, key1, 125)
    contained_key_count += result[0]
    contained_key.extend(result[1])
    # 标题中包含key2 权重+ 25
    result = get_weigth(title, key2, 25)
    contained_key_count += result[0]
    contained_key.extend(result[1])

    # 判断内容
    # 内容中包含key1 权重+ 5
    result = get_weigth(content, key1, 5)
    contained_key_count += result[0]
    contained_key.extend(result[1])
    # 内容中包含key2 权重+ 1
    result = get_weigth(content, key2, 1)
    contained_key_count += result[0]
    contained_key.extend(result[1])

    return ','.join(contained_key), contained_key_count

def is_violate(content, key1 = [], key2 = [], key3 =[]):
    if not key1 and not key2:
        return False

    def check_key1(keys, content):
        for key in keys:
            if not key:
                continue

            if key not in content:
                return False
        else:
            return True

    def check_key2(keys, content):
        for key in keys:
            if not key:
                continue

            if key in content:
                return True
        else:
            return False

    def check_key3(keys, content):
        for key in keys:
            if not key:
                continue

            if key in content:
                return False
        else:
            return True

    result = True
    if key1:
        result = check_key1(key1, content)
    if key2:
        result = result and check_key2(key2, content)
    if key3:
        result = result and check_key3(key3, content)

    return result

def is_have_video_by_site(url):
    '''
    @summary: 根据特定网站的特征来判断
    ---------
    @param url:
    ---------
    @result:
    '''

    domain = tools.get_domain(url)

    feas = db.find('FeaVideo_site', {'domain':domain})

    for fea in feas:
        video_fea = fea['video_fea'].split(',')

        if tools.get_info(url, video_fea):
            return True

    return False

def is_have_video_by_judge(title, content):
    '''
    @summary: 根据title 和 content 来判断 （正负极）
    ---------
    @param title:
    @param content:
    ---------
    @result:
    '''

    text = title + content

    feas = db.find('FeaVideo_judge')

    for fea in feas:
        not_video_fea = fea['not_video_fea'].split(',')
        video_fea = fea['video_fea'].split(',')

        if tools.get_info(text, not_video_fea):
            return False

        if tools.get_info(text, video_fea):
            return True

    return False

def is_have_video_by_common(html):
    '''
    @summary: 根据html源码来判断
    ---------
    @param html: html源码
    ---------
    @result:
    '''

    feas = db.find('FeaVideo_common')

    for fea in feas:
        video_fea = fea['video_fea'].split(',')

        if tools.get_info(html, video_fea):
            return True

    return False

def get_site_id(table, site_name):
    result = db.find(table, {'name':site_name})
    if result:
        return result[0]['site_id']
    else:
        raise AttributeError('%s表中无%s信息'%(table, site_name))

def add_url(table, site_id, url, depth = 0, remark = '', status = Constance.TODO):
    url_dict = {'site_id':site_id, 'url':url, 'depth':depth, 'remark':remark, 'status':status}
    return db.add(table, url_dict)

def update_url(table, url, status):
    db.update(table, {'url':url}, {'status':status})

def add_website_info(table, site_id, url, name, domain = '', ip = '', address = '', video_license = '', public_safety = '', icp = ''):
    '''
    @summary: 添加网站信息
    ---------
    @param table: 表名
    @param site_id: 网站id
    @param url: 网址
    @param name: 网站名
    @param domain: 域名
    @param ip: 服务器ip
    @param address: 服务器地址
    @param video_license: 网络视听许可证|
    @param public_safety: 公安备案号
    @param icp: ICP号
    ---------
    @result:
    '''

    # 用程序获取domain,ip,address,video_license,public_safety,icp 等信息
    domain = tools.get_domain(url)

    site_info = {
        'site_id':site_id,
        'name':name,
        'domain':domain,
        'url':url,
        'ip':ip,
        'address':address,
        'video_license':video_license,
        'public_safety':public_safety,
        'icp':icp,
        'read_status':0,
        'record_time': tools.get_current_date()
    }
    db.add(table, site_info)


# 需要图片鉴黄的数据加上一下两个字段

# * sexy_image_status   淫秽色情图像，多个逗号分隔
# * sexy_image_url      淫秽色情图像地址，多个逗号分隔
# * image_pron_status   图片扫描状态

def add_content_info(table, site_id, url, title='', content='',
                     author='', video_url='', image_url='', origin='',
                     watched_count='', comment_count='', share_count='',
                     praise_count='', release_time='', file_size='',
                     file_name='', magnet_link='', download_count='',
                     reposts_count='', attitudes_count='', is_verified = '',
                     search_type='', keyword = '', keyword_count = 0, task_id = ''):
    '''
    @summary: 添加視頻信息
    ---------
    @param table: 表名
    @param site_id: 网站id
    @param url: 网址
    @param title: 标题
    @param content: 正文
    @param author: 作者
    @param origin: 来源
    @param release_time: 发布时间
    @param file_name: 文件名
    @param file_size: 文件大小
    @param video_url: 视频url
    @param image_url: 图片url
    @param magnet_link: 磁力链接
    @param download_count: 下载次数
    @param watched_count: 观看数
    @param comment_count: 评论数
    @param share_count: 分享数
    @param praise_count: 点赞数
    @param reposts_count: 转发数
    @param attitudes_count: 点赞数
    @param is_verified: 微博用户是否有V认证
    @param task_id : 任務id
    ---------
    @result:
    '''

    content_info = {
        'site_id':site_id,
        'title':title,
        'url':url,
        'content':content,
        'author':author,
        'video_url':video_url,
        'image_url':image_url,
        'origin':origin,
        'watched_count':watched_count,
        'comment_count': comment_count,
        'share_count': share_count,
        'praise_count': praise_count,
        'release_time': release_time,
        'file_size':file_size,
        'magnet_link':magnet_link,
        'download_count':download_count,
        'file_name':file_name,
        'reposts_count':reposts_count,
        'attitudes_count':attitudes_count,
        'is_verified':is_verified,
        'search_type':search_type,
        'read_status':0,
        'record_time': tools.get_current_date(),
        'keyword':keyword,
        'keyword_count':keyword_count,
        'sexy_image_status':'',
        'sexy_image_url':'',
        'image_pron_status':0,
        'task_id':task_id
    }

    db.add(table, content_info)

def add_appsite_info(table, site_id, url, name , app_url = '', summary = '', update_info = '', author = '', image_url = '', classify = '', size = '', tag = '', platform = 'android', download_count = '', release_time = ''):
    '''
    @summary: 添加app 网站信息
    ---------
    @param table: 表名
    @param site_id: 网站id
    @param url: 网址
    @param name: app名
    @param app_url: app url
    @param summary: 简介
    @param update_info: 更新信息
    @param author: 开发者
    @param image_url: 图标url
    @param classify: 分类
    @param size: 大小
    @param tag: 版本
    @param platform: 平台 默认android
    @param download_count: 下载次数
    @param release_time: 发布时间
    ---------
    @result:
    '''

    app_info = {
        'site_id':site_id,
        'url':url,
        'name':name,
        'app_url':app_url,
        'summary':summary,
        'update_info':update_info,
        'author':author,
        'image_url':image_url,
        'classify':classify,
        'size':size,
        'tag':tag,
        'platform':platform,
        'download_count':download_count,
        'release_time':release_time,
        'read_status':0,
        'record_time': tools.get_current_date(),
        'sexy_image_status':'',
        'sexy_image_url':'',
        'image_pron_status':0
    }

    db.add(table, app_info)

def add_wp_content_info(table, site_id , title = '', article_type = '', url= ' ', episodes = '', score = '',
                        subscribe_count = '',author = '', release_time = '', update_time = '',image_url = '',
                        watched_count = '', comment_count = '',charge_type = '', is_finished = '', origin = '',
                        abstract = '', content = '',data_type = ''):
    wp_content_info_dict = {
        'site_id': site_id,
        'title': title,
        'article_type': article_type,
        'url': url,
        'episodes': episodes,
        'score': score,
        'subscribe_count': subscribe_count,
        'author': author,
        'release_time': release_time,
        'update_time': update_time,
        'image_url': image_url,
        'watched_count': watched_count,
        'comment_count': comment_count,
        'charge_type': charge_type,
        'record_time': tools.get_current_date(),
        'is_finished': is_finished,
        'origin': origin,
        'abstract': abstract,
        'content': content,
        'image_pron_status': 0,
        'data_type': data_type,
        'read_status': 0
    }
    db.add(table, wp_content_info_dict)
    return wp_content_info_dict['_id']

def add_wp_content_episode_info(table, title = '', image_url = '', video_url = '',watched_count = '', play_length = '',
                                    comments_count = '',release_time = '', content_id = '', data_type = ''):
    wp_content_episode_info_dict = {
        'content_id':content_id,
        'image_url':image_url,
        'title': title,
        'video_url': video_url,
        'watched_count': watched_count,
        'play_length': play_length,
        'comment_count': comments_count,
        'release_time': release_time,
        'image_pron_status': 0,
        'record_time': tools.get_current_date(),
        'data_type': data_type,
        'read_status': 0
    }
    db.add(table, wp_content_episode_info_dict)


def add_anchor_info(table, site_id , title = '', name  = '', image_url  = '', room_id  = '', room_url  = '', video_path = '',  watched_count  = '', fans_count  = '', sex  = '', age = '', address  = '', live_view = 1, watched_count_url = ''):
    '''
    @summary:
    ---------
    @param table: 表名
    @param site_id: 网站id
    @param name: 主播名
    @param image_url: 贴图地址
    @param room_id: 房间号
    @param room_url: 房间网页的url
    @param video_path: 房间视频流地址
    @param watched_count: 观众数
    @param fans_count: 粉丝数
    @param sex:  性别
    @param age:  年龄
    @param address:   主播所在地址（城市）
    @param live_view: 直播状态（0 未直播 1 直播）
    @param watched_count_url： 实时观众数地址
    ---------
    @result:
    '''

    #违规知识库检索
    task_id = 0
    violate_content = ''
    #-交验--
    from db.oracledb import OracleDB
    oracle_db = OracleDB()

    sql = 'select t.name, t.keyword, t.task_id from tab_nbsp_violate_knowledge t where t.monitor_start_time <= sysdate and sysdate <= t.monitor_end_time'
    results = oracle_db.find(sql)#[('色情低俗', '性感,枪支,格斗,脱衣,透视,胸器', 1)]

    for result in results:
        name_, keywords, task_id_ = result
        keywords = keywords.split(',')
        for keyword in keywords:
            if name.find(keyword) != -1:
                task_id = task_id_
                violate_content = name

    anchor_info_dict = {
        'site_id':site_id,
        'title':title,
        'task_id':task_id,
        'violate_content':violate_content,
        'name':name,
        'image_url':image_url,
        'sex':sex,
        'age':age,
        'address':address,
        'fans_count':fans_count,
        'watched_count':watched_count,
        'room_id':room_id,
        'room_url':room_url,
        'video_path':video_path,
        'live_view':live_view,
        'record_time':tools.get_current_date(),
        'watched_count_url':watched_count_url,
        'read_status':0,
        'sexy_image_status':'',
        'sexy_image_url':'',
        'image_pron_status':0
    }

    if not db.add(table, anchor_info_dict):
        anchor_info_dict.pop('_id')
        anchor_info_dict.pop('sexy_image_status')
        anchor_info_dict.pop('sexy_image_url')
        anchor_info_dict.pop('image_pron_status')
        db.update(table, {'room_id':room_id}, anchor_info_dict)

def add_game_app_info(table, site_id, url, title = '', summary = '', update_info = '', score = '',
                     author = '', app_url = '', image_url='',
                     classify_id = '', software_size='', tag='',
                     platform='', download_count='', release_time='', language='',
                     sensitive_id='', read_status=0):

    '''
    @summary:
    ---------
    @param title: 标题
    @param site_id: 网站id
    @param summary: 简介
    @param update_info: 更新信息
    @param socre: 评分
    @param author: 作者
    @param url: 原文url
    @param app_url: app下载的url
    @param image_url : 图片url（多个url逗号分割）
    @param classify_id: 分类
    @param software_size: 大小
    @param tag: 版本 |
    @param platform: 平台（ios / android）
    @param download_count:下载次数
    @param release_time: 发布时间
    @param record_time: 记录时间
    @param sensitive_id: varchar|||敏感信息id（多个敏感信息id用逗号分割）
    @param read_status: 读取状态（0没读， 1读取）
    ---------
    @result:
    '''

    if language == '中文':
        language = 601
    elif language == '英文':
        language = 602
    else:
        language = 603

    def del_not_use_tag(content):
        content = tools.replace_str(content, '<script(.|\n)*?</script>')
        content = tools.replace_str(content, '<style(.|\n)*?</style>')
        content = tools.replace_str(content, '<!--(.|\n)*?-->')
        content = content.replace('</p>', '/p')
        content = tools.replace_str(content, '<[^p].*?>')
        content = content.replace('/p', '</p>')
        content = tools.replace_str(content, '&.*?;')
        content = tools.replace_str(content, '[ \f\r\t\v]')

        return content

    gameApp_info_dict={
        'site_id': site_id,
        'url': url,
        'summary': del_not_use_tag(summary),
        'title': title,
        'update_info': del_not_use_tag(update_info),
        'score': score,
        'author': author,
        'app_url': app_url,
        'image_url': image_url,
        'classify_id': classify_id,
        'software_size': software_size,
        'tag': tag,
        'platform': platform,
        'download_count': download_count,
        'release_time': release_time,
        'record_time': tools.get_current_date(),
        'language': language,
        'sensitive_id': sensitive_id,
        'read_status': 0,
        'sexy_image_status': '',
        'sexy_image_url': '',
        'image_pron_status': 0
    }
    db.add(table, gameApp_info_dict)


def add_va_app_content_info(table, site_id, title, summary, image_url, img_stor_path, url, release_time, video_url, video_stor_path, content, column_id, is_download, sensitive_id, violate_id, storage_id):
    '''
    @summary:
    ---------
    @param table:
    @param site_id:
    @param title:
    @param summary:
    @param image_url:
    @param img_stor_path:
    @param url:
    @param release_time:
    @param video_url:
    @param video_stor_path:
    @param content:
    @param column_id:
    @param is_download:
    @param sensitive_id:
    @param violate_id:
    ---------
    @result:
    '''


    is_audio = video_url and 1 or 0

    content_info_dict = {
        'title':title,
        'summary':summary,
        'image_url':image_url,
        'img_stor_path':img_stor_path,
        'url':url,
        'release_time':release_time,
        'video_url':video_url,
        'video_stor_path':video_stor_path,
        'content':content,
        'column_id':column_id,
        'is_download':is_download,
        'sensitive_id':sensitive_id,
        'violate_id':violate_id,
        'storage_id':storage_id,
        'site_id':site_id,
        'record_time':tools.get_current_date(),
        'sexy_image_status': '',
        'sexy_image_url': '',
        'image_pron_status': 0,
        'read_status':0,
        'is_audio':is_audio
    }

    db.add(table, content_info_dict)

    if sensitive_id or violate_id:
        content_info_dict['content_id'] = content_info_dict['_id']
        db.add('VAApp_vioation_content_info', content_info_dict)

def add_article_info(table, website_id, source_url, title, content):

    content_info_dict = {
        'site_id':website_id,
        'url':source_url,
        'title':title,
        'content':content,
        'record_time':tools.get_current_date(),
        'read_status':0
    }

    db.add(table, content_info_dict)

def add_op_info(table, website_id, url ='', title='', release_time='', author='', origin='', watched_count='', content=''):

    content_info_dict = {
        'site_id': website_id,
        'url': url,
        'title': title,
        'release_time': release_time,
        'author': author,
        'origin': origin,
        'watch_count': watched_count,
        'content': content,
        'record_time': tools.get_current_date(),
        'read_status': 0
    }
    db.add(table, content_info_dict)

def add_program_info(table, site_id, program_name, image_url = '', episode = '', directors = '', actors = '', summary = '', release_time = ''):
    '''
    @summary:
    ---------
    @param table:
    @param site_id:
    @param program_name:
    @param image_url:
    @param episode: 集数
    @param directors: 导演
    @param actors: 演员
    @param summary: 简介
    @param release_time:
    ---------
    @result:
    '''
    program_info = {
        'site_id' : site_id,
        'program_name' : program_name,
        'image_url' : image_url,
        'episode' : episode,
        'directors' : directors,
        'actors' : actors,
        'summary' : summary,
        'release_time' : release_time,
        'read_status' : 0,
        'record_time' : tools.get_current_date()
    }

    db.add(table, program_info)

    return program_info['_id']


# 两微一端

def add_wwa_weibo_user_info(table, site_id, _id = '', name = '', url = '', image_url = '',
                            verified_reason = '', is_verified_reason = '', sex = '',
                            summary = '', fans_count = '', follow_count = ''):
    '''
    @summary:
    ---------
    @param table:
    @param site_id:
    @param _id:       用户id
    @param name:      昵称
    @param image_url: 头像
    @param verified_reason: 认证详情
    @param is_verified_reason: 是否认证
    @param sex: 性别
    @param summary: 简介
    @param fans_count: 粉丝数
    @param follow_count: 关注数
    ---------
    @result:
    '''
    user_info = {
        '_id': _id,
        'site_id': site_id,
        'name': name,
        'url': url,
        'image_url': image_url,
        'blog_verified': verified_reason,
        'is_verified': is_verified_reason,
        'sex': sex,
        'summary': summary,
        'fans_count': fans_count,
        'follow_count': follow_count,
        'read_status': 0,
        'record_time': tools.get_current_date()
    }
    db.add(table, user_info)

def add_wwa_weibo_info_info(table, site_id, url = '', weibo_id = '', release_time = '', come_from = '',
                               content = '', image_url = '', video_url = '', transpond_count = '', praise_count = '',
                               violate_id = ''):
    '''
    @summary:
    ---------
    @param table:
    @param site_id:
    @param url:      原文地址
    @param weibo_id: 微博id
    @param release_time: 发布时间
    @param come_from: 来自
    @param image_url: 图片地址
    @param video_url: 视频地址
    @param transpond_count: 转发数
    @param praise_count: 点赞数
    @param violate_id: 违规id
    ---------
    @result:
    '''
    user_info = {
        'url': url,
        'site_id': site_id,
        'weibo_id': weibo_id,
        'url': url,
        'release_time': release_time,
        'come_from': come_from,
        'content': content,
        'image_url': image_url,
        'video_url': video_url,
        'transpond_count': transpond_count,
        'praise_count': praise_count,
        'read_status': 0,
        'violate_id': violate_id,
        'record_time': tools.get_current_date()
    }
    db.add(table, user_info)

def add_wechat_accout_info(table, site_id, name, account_id, account_url, image_url, local_image_url, article_count, summary, certification, is_verified, barcode_url, local_barcode_url):
    account_info = {
        'name' : name,
        'account_id' : account_id,
        'account_url' : account_url,
        'image_url' : image_url,
        'local_image_url' : local_image_url,
        'article_count' : article_count,
        'summary' : summary,
        'certification' : certification,
        'is_verified' : is_verified,
        'barcode_url' : barcode_url,
        'local_barcode_url' : local_barcode_url,
        'read_status' : 0,
        'record_time' : tools.get_current_date(),
    }

    db.add(table, account_info)

def add_wechat_content_info(table, site_id, official_accounts_id, title, summary = '', image_url = '', article_url = '', release_time = '', content = '', video_url = '', violate_status = '', local_image_url = ''):

    content_info = {
        'site_id' : site_id,
        'official_accounts_id' : official_accounts_id,
        'title' : title,
        'summary' : summary,
        'image_url' : image_url,
        'article_url' : article_url,
        'release_time' : release_time,
        'content' : content,
        'video_url' : video_url,
        'record_time' : tools.get_current_date(),
        'read_status' : 0,
        'violate_status' : violate_status,
        'local_image_url' : local_image_url
    }

    db.add(table, content_info)

def add_WWA_search_app_info(table, site_id, url, title = '', summary = '', update_info = '', score = '',
                     author = '', app_url = '', image_url='',
                     software_size='', tag='',
                     platform='', download_count='', release_time='', language='',
                     sensitive_id='', read_status=0):

    '''
    @summary:
    ---------
    @param title: 标题
    @param site_id: 网站id
    @param summary: 简介
    @param update_info: 更新信息
    @param socre: 评分
    @param author: 作者
    @param url: 原文url
    @param app_url: app下载的url
    @param image_url : 图片url（多个url逗号分割）
    @param classify_id: 分类
    @param software_size: 大小
    @param tag: 版本 |
    @param platform: 平台（ios / android）
    @param download_count:下载次数
    @param release_time: 发布时间
    @param record_time: 记录时间
    @param sensitive_id: varchar|||敏感信息id（多个敏感信息id用逗号分割）
    @param read_status: 读取状态（0没读， 1读取）
    ---------
    @result:
    '''

    if language == '中文':
        language = 601
    elif language == '英文':
        language = 602
    else:
        language = 603

    gameApp_info_dict={
        'site_id': site_id,
        'url': url,
        'summary': tools.del_html_tag(summary, except_line_break = True),
        'title': title,
        'update_info': tools.del_html_tag(update_info, except_line_break = True),
        'score': score,
        'author': author,
        'app_url': app_url,
        'image_url': image_url,
        'software_size': software_size,
        'tag': tag,
        'platform': platform,
        'download_count': download_count,
        'release_time': release_time,
        'record_time': tools.get_current_date(),
        'language': language,
        'sensitive_id': sensitive_id,
        'read_status': 0,
        'sexy_image_status': '',
        'sexy_image_url': '',
        'image_pron_status': 0
    }
    db.add(table, gameApp_info_dict)


def add_wwa_app_content_info(table, site_id, title, summary, image_url, img_stor_path, url, release_time, video_url, video_stor_path, content, column_id, is_download, sensitive_id, violate_id, storage_id):
    '''
    @summary:
    ---------
    @param table:
    @param site_id:
    @param title:
    @param summary:
    @param image_url:
    @param img_stor_path:
    @param url:
    @param release_time:
    @param video_url:
    @param video_stor_path:
    @param content:
    @param column_id:
    @param is_download:
    @param sensitive_id:
    @param violate_id:
    ---------
    @result:
    '''


    is_audio = video_url and 1 or 0

    content_info_dict = {
        'title':title,
        'summary':summary,
        'image_url':image_url,
        'img_stor_path':img_stor_path,
        'url':url,
        'release_time':release_time,
        'video_url':video_url,
        'video_stor_path':video_stor_path,
        'content':content,
        'column_id':column_id,
        'is_download':is_download,
        'sensitive_id':sensitive_id,
        'violate_id':violate_id,
        'storage_id':storage_id,
        'site_id':site_id,
        'record_time':tools.get_current_date(),
        'sexy_image_status': '',
        'sexy_image_url': '',
        'image_pron_status': 0,
        'read_status':0,
        'is_audio':is_audio
    }

    db.add(table, content_info_dict)

    if sensitive_id or violate_id:
        content_info_dict['content_id'] = content_info_dict['_id']
        db.add('WWA_app_vioation_content_info', content_info_dict)

