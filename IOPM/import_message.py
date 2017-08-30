# -*- coding: utf-8 -*-
'''
Created on 2017-07-28 14:28
---------
@summary: 同步智能推荐的舆情信息
---------
@author: Boris
'''

import sys
sys.path.append('../')
import utils.tools as tools
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

db = OracleDB()
export_data = ExportData()
vip_checked = VipChecked()

STO_PER_SYNC_TIME = '.sync_time'

def get_url(time_lenght = 60):
    '''
    @summary:
    ---------
    @param time_lenght: 时间段 分钟
    ---------
    @result:
    '''

    current_date = tools.get_current_date()
    per_date = tools.read_file(STO_PER_SYNC_TIME) or tools.timestamp_to_date(tools.get_current_timestamp() - time_lenght * 60)

    tools.write_file(STO_PER_SYNC_TIME, current_date)

    root_url = 'http://192.168.60.38:8001/hotspot_al/interface/getCluesDataSearchInfo?pageNo=%d&pageSize=100&updateSTime={per_date}&updateETime={current_date}&sort=5&isDesc=0'.format(per_date = per_date, current_date = current_date)
    return root_url

def get_datas(root_url):
    count = 0
    page = 1
    while True:
        url = root_url%page
        print(url)

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
            article_id = db.find(sql)[0][0]

            def export_callback(execute_type, sql, data_json):
                if execute_type != ExportData.EXCEPTION:
                    for clues_id in clues_ids.split(','):
                        print(clues_id)
                        key_map = {
                            'id':'vint_sequence.nextval',
                            'article_id':'vint_%d'%article_id,
                            'clues_id':'vint_%s'%clues_id
                        }
                        export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_ARTICLE_CLUES_SRC', datas = [{}], sync_to_es = True)

            # 计算权重
            url = 'http://192.168.60.30:8080/related_sort?article_id=%d&clue_ids=%s&may_invalid=%s'%(article_id, msg['cluesIds'], msg['mayInvalid'] or '0')
            weight = tools.get_json_by_requests(url).get('weight', 0)

            key_map = {
                'id':'vint_%d'%article_id,
                'account': 'str_account',
                'author': 'str_author',
                'clues_ids': 'str_cluesIds',
                'comment_count': 'int_commtcount',
                'content': 'clob_content',
                'emotion': 'vint_%s'%(msg['emotion'] or 3),
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
                'keywords_count':'vint_%d'%len(msg['keywords'].split(',')),
                'is_vip':'vint_%d'%vip_checked.is_vip(msg['url']) or vip_checked.is_vip(msg['websiteName'])or vip_checked.is_vip(msg['author']),
                'weight':'vint_%s'%weight,
                'record_time':'vdate_%s'%tools.get_current_date()
            }

            export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_ARTICLE_INFO', unique_key = 'url', datas = msg, callback = export_callback, unique_key_mapping_source_key = {'url': 'str_url'}, sync_to_es = True)
            count += 1

        page += 1

def main():
    url = get_url(time_lenght = 60)
    print(url)
    get_datas(url)

if __name__ == '__main__':
    main()