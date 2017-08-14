# -*- coding: utf-8 -*-
'''
Created on 2017-07-28 14:28
---------
@summary: 同步热点信息
---------
@author: Boris
'''

import sys
sys.path.append('../')
import utils.tools as tools
from utils.log import log
from utils.export_data import ExportData
from db.oracledb import OracleDB
from IOPM.vip_checked import VipChecked

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Host": "192.168.60.38:8001"
}

oracledb = OracleDB()
export_data = ExportData()
vip_checked = VipChecked()

def get_about_me_message(keywords, hot_id):
    root_url = 'http://192.168.60.38:8001/hotspot_al/interface/getCluesDataSearchInfo?pageNo=%d&pageSize=100&hotKeywords=%s'

    count = 0
    page = 1
    while True:
        url = root_url%(page,keywords)

        datas = tools.get_json_by_requests(url, headers = HEADERS)
        if datas['message'] == '查询记录为0':
            print('每页100条  第%d页无数据 共导出 %d 条数据'%(page, count))
            break

        messages = datas['data']['data']
        for msg in messages:
            if not msg['url']:
                continue

            weight = 0 # 权重
            clues_ids = msg['cluesIds']

            # 取id
            sql = 'select SEQ_IOPM_ARTICLE.nextval from dual'
            article_id = oracledb.find(sql)[0][0]

            # 同步线索与文章的中间表
            def export_callback(execute_type, sql):
                if execute_type != ExportData.EXCEPTION:
                    # 计算权重
                    url = 'http://192.168.60.30:8080/related_sort?article_id=%d'%article_id
                    tools.get_html_by_requests(url)

                    for clues_id in clues_ids.split(','):
                        key_map = {
                            'id':'vint_sequence.nextval',
                            'article_id':'vint_%d'%article_id,
                            'clues_id':'vint_%s'%clues_id
                        }
                        export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_ARTICLE_CLUES_SRC', unique_key = 'url', datas = [{}])



            key_map = {
                'id':'vint_%d'%article_id,
                'account': 'str_account',
                'author': 'str_author',
                'clues_ids': 'str_cluesIds',
                'comment_count': 'int_commtcount',
                'content': 'clob_content',
                'emotion': 'int_emotion',
                'host': 'str_host',
                'keywords': 'str_keywords',
                'image_url': 'str_picture',
                'release_time': 'date_pubtime',
                'review_count': 'int_reviewCount',
                'title': 'str_title',
                'info_type': 'int_type',
                'up_count': 'int_upCount',
                'url': 'str_url',
                'uuid': 'str_uuid',
                'website_name': 'str_websiteName',
                'MAY_INVALID':'int_mayInvalid',
                'KEYWORD_CLUES_ID':'str_keywordAndIds',
                'hot_id':"vint_%d"%hot_id,
                'keywords_count':'vint_%d'%len(msg['keywords'].split(',')),
                'is_vip':'vint_%d'%vip_checked.is_vip(msg['url']) or vip_checked.is_vip(msg['websiteName'])
            }

            count += export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_ARTICLE_INFO', unique_key = 'url', datas = msg, callback = export_callback, unique_key_mapping_source_key = {'url': 'str_url'})

        page += 1

def update_about_me_message_hot_id():
    sql = 'select t.id, t.keywords from TAB_IOPM_HOT_INFO t where t.hot_type != 0'
    hots = oracledb.find(sql)
    for hot in hots:
        hot_id = hot[0]
        keywords = hot[1]
        print(hot)

        get_about_me_message(keywords, hot_id)

def get_about_me_hot():
    '''
    @summary:
    ---------
    @param :
    ---------
    @result:
    '''
    url = 'http://192.168.60.38:8001/hotspot_al/interface/getHotAnalysis_self'
    json = tools.get_json_by_requests(url, headers = HEADERS)
    # print(json)

    hot_list = []
    datas = json['data']
    for data in datas:
        clues_id = list(data.keys())[0]
        sql = 'select t.name from TAB_IOPM_CLUES t where id = ' + clues_id
        name = oracledb.find(sql)[0][0]

        hot_infos = data[clues_id]['data']
        for hot_info in hot_infos:
            kw = hot_info['kw']
            hot = hot_info['hot']
            kg = hot_info['kg']
            hot_list.append({'clues_id':clues_id, 'kw':kw, 'hot':hot, 'name':name, 'kg':kg})

    about_me_hot_count = 0
    for hot_info in hot_list:
        print(hot_info['name'], ':', hot_info['kw'], hot_info['hot'])

        sql = 'select sequence.nextval from dual'
        hot_id = oracledb.find(sql)[0][0]

        def export_callback(execute_type, sql):
            print(ExportData.EXCEPTION)
            if execute_type != ExportData.EXCEPTION:
                # 计算权重
                url = 'http://192.168.60.30:8080/related_sort?hot_id=%d'%hot_id
                tools.get_html_by_requests(url)

                # 取涉我舆情
                get_about_me_message(hot_info['kg'], hot_id)


        key_map = {
            'id':'vint_%d'%hot_id,
            'title':'str_kw',
            'hot':'int_hot',
            'clues_id':'int_clues_id',
            'keywords':'str_kg',
            'hot_type':'vint_1'
        }

        about_me_hot_count += export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_HOT_INFO', unique_key = 'title', datas = hot_info, callback = export_callback)

    # 更新vip热点
    sql = '''
    update tab_iopm_hot_info set is_vip = 1 where id in (
         select distinct(hot_id) from TAB_IOPM_ARTICLE_INFO where is_vip != 0
        )
    '''
    oracledb.update(sql)
    print('共导出%d 条涉我热点'%about_me_hot_count)

def get_all_hot():
    '''
    @summary: 全网热点
    ---------
    @param :
    ---------
    @result:
    '''

    url = 'http://192.168.60.38:8001/hotspot_al/interface/getHotAnalysis?type=0'
    json = tools.get_json_by_requests(url, headers = HEADERS)
    datas = json['data']

    hot_count = 0
    message_count = 0
    # 相关新闻获取url
    root_url = 'http://192.168.60.38:8001/hotspot_al/interface/getHotRelateInfo?ids=%s'
    for data in datas:
        sql = 'select SEQ_IOPM_ARTICLE.nextval from dual'
        hot_id = oracledb.find(sql)[0][0]

        def export_callback(execute_type, sql):
                if execute_type != ExportData.EXCEPTION:
                    global message_count

                    infoIds = data['infoIds']
                    url = root_url%infoIds
                    json = tools.get_json_by_requests(url, headers = HEADERS)
                    articles = json['data']

                    key_map = {
                        'id':'int_dataId',
                        'content':'clob_content',
                        'url':'str_url',
                        'website_name':'str_site',
                        'image_url':'str_picture',
                        'release_time':'date_pubtime',
                        'keywords':'str_keywords',
                        'emotion':'str_emotion',
                        'host': 'str_site',
                        'title': 'str_title',
                        'info_type': 'int_type',
                        'hot_id':"vint_%d"%hot_id
                    }

                    message_count += export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_ARTICLE_INFO', unique_key = 'url', datas = articles)

        # 导出全国热点数据

        key_map = {
            'id':'vint_%d'%hot_id,
            'title':'str_kw',
            'hot':'int_hot',
            'hot_type':'vint_0'
        }

        hot_count += export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_HOT_INFO', unique_key = 'title', datas = data)


    log.info('''
        共导出%d条全网热点
        共导出%d条相关新闻
        '''%(hot_count, message_count))

def main():
    get_about_me_hot()
    get_all_hot()



if __name__ == '__main__':
    main()
    # update_about_me_message_hot_id()
