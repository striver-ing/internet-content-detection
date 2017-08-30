# -*- coding: utf-8 -*-
'''
Created on 2017-08-22 15:42
---------
@summary: 同步数据库到ES
---------
@author: Boris
'''

import sys
sys.path.append('../')
import init
import utils.tools as tools
from utils.log import log
from db.elastic_search import ES
from db.oracledb import OracleDB

STO_MAX_ID_FILE = '.max_id'

class SyncES():
    def __init__(self):
        self._es = ES(ip = '192.168.60.40', port = 9200)
        self._db = OracleDB()

        self._max_id = tools.read_file(STO_MAX_ID_FILE)
        self._max_id = self._max_id and eval(self._max_id) or {}

    def get_data(self, sql):
        return self._db.find(sql, to_json = True)

    def export_to_es(self, table, data, data_id):
        self._es.add(table = table, data = data, data_id = data_id)

    def sync_data(self, table, step = 20):
        '''
        @summary: 需要先把id设为主键
        ---------
        @param sql:
        @param table:
        @param is_step: 分批导 0 位一次导入， 适合数据量不多情况。速度快
        ---------
        @result:
        '''

        max_id = self._max_id.get(table, 0)
        self._db.set_primary_key(table)

        while True:
            inner_sql = 'select * from %s where id > %d and rownum <= %d order by id'%(table, max_id, step)
            datas = sync_es.get_data(inner_sql)

            if not datas:
                self.close()
                break

            for data in datas[:5]:
                data_id = data['ID']
                data = tools.dumps_json(data)
                # print(data_id)
                # print(data)

                max_id = data_id

                self.export_to_es(table, data, data_id)

        self._max_id[table] = max_id

    def close(self):
        tools.write_file(STO_MAX_ID_FILE, str(self._max_id))

if __name__ == '__main__':
    sync_es = SyncES()

    # 同步舆情数据
    sync_es.sync_data(table = 'TAB_IOPM_ARTICLE_INFO')

    # 同步热点数据
    sync_es.sync_data(table = 'TAB_IOPM_HOT_INFO')
