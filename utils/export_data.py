# -*- coding: utf-8 -*-
'''
Created on 2017-01-11 15:41
---------
@summary: mongo 导数据 到oracle 或 mysql
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init

from db.mongodb import MongoDB
from db.oracledb import OracleDB
from db.mysqldb import MysqlDB
from utils.log import log
import utils.tools as tools
import os
os.environ['nls_lang'] = 'AMERICAN_AMERICA.AL32UTF8'   # 插入数据时编码错误 加上这句解决 设置客户端编码

class ExportData():
    def __init__(self, source_table = '', aim_table = '', key_map = '', unique_key = None, unique_key_mapping_source_key = None, update_read_status = True, condition = {'read_status':0}):
        '''
        @summary: 初始化
        ---------
        @param source_table: 源table
        @param aim_table:    目标table
        @param key_map:      目标table 和 源table 的键的映射
        eg: key_map = {
            'aim_key1' : 'str_source_key2',          # 目标键 = 源键对应的值         类型为str
            'aim_key2' : 'int_source_key3',          # 目标键 = 源键对应的值         类型为int
            'aim_key3' : 'date_source_key4',         # 目标键 = 源键对应的值         类型为date
            'aim_key4' : 'vint_id',                  # 目标键 = 值                   类型为int
            'aim_key5' : 'vstr_name',                # 目标键 = 值                   类型为str
            'aim_key6' : 'sint_select id from xxx'   # 目标键 = 值为sql 查询出的结果 类型为int
            'aim_key7' : 'sstr_select name from xxx' # 目标键 = 值为sql 查询出的结果 类型为str
            'aim_key8' : 'clob_key8'                 # 目标键 = 源键对应的值         类型为str
        }

        @param unique_key:    唯一的key 目标数据库根据该key去重
        @param unique_key_mapping_source_key: 目标表中唯一的key所对应的源表中的key 该值不为空时 更新目标表中已有的数据
         eg: unique_key_mapping_source_key = {
            'url':'str_url'                         # 目标键 = 源键对应的值         类型为str
         }
        @param condition:    导出满足什么样条件的数据 默认是read_status = 0 的
        ---------
        @result:
        '''

        super(ExportData, self).__init__()

        self._source_table = source_table
        self._aim_table = aim_table
        self._key_map = key_map
        self._unique_key = unique_key
        self._update_read_status = update_read_status
        self._condition = condition

        self._mongodb = MongoDB()

        self._is_oracle = False
        self._export_count = 0
        self._update_count = 0
        self._unique_key_mapping_source_key = unique_key_mapping_source_key


    def export_to_oracle(self, source_table = '', aim_table = '', key_map = '', unique_key = None, unique_key_mapping_source_key = None, update_read_status = True, condition = {'read_status':0}):
        if source_table:
            self._source_table = source_table
            self._aim_table = aim_table
            self._key_map = key_map
            self._unique_key = unique_key
            self._export_count = 0
            self._update_count = 0
            self._unique_key_mapping_source_key = unique_key_mapping_source_key
            self._update_read_status = update_read_status
            self._condition = condition

        self._aim_db = OracleDB()
        self._is_oracle = True
        self.__export()

    def export_to_mysql(self, source_table = '', aim_table = '', key_map = '', unique_key = None, unique_key_mapping_source_key = None, update_read_status = True, condition = {'read_status':0}):
        if source_table:
            self._source_table = source_table
            self._aim_table = aim_table
            self._key_map = key_map
            self._unique_key = unique_key
            self._export_count = 0
            self._update_count = 0
            self._unique_key_mapping_source_key = unique_key_mapping_source_key
            self._update_read_status = update_read_status
            self._condition = condition

        self._aim_db = MysqlDB()
        self.__export()

    # @tools.run_safe_model(__name__)
    def __export(self):
        if self._unique_key:
            self._aim_db.set_unique_key(self._aim_table, self._unique_key)

        aim_keys = tuple(self._key_map.keys())
        source_keys = tuple(self._key_map.values())

        # 取源key值 对应的type 和 key （源key包含type 和 key 信息）
        keys = []
        value_types = []
        for source_key in source_keys:
            temp_var = source_key.split('_', 1)
            value_types.append(temp_var[0])
            keys.append(temp_var[1])

        datas = self._mongodb.find(self._source_table, condition = self._condition, limit = 1)
        for data in datas:
            sql = 'insert into ' + self._aim_table + " (" + ', '.join(aim_keys) + ") values ("
            update_sql = 'update ' + self._aim_table + " set "
            values = []
            for i in range(len(keys)):
                if value_types[i] == 'str':
                    values.append(str(data[keys[i]]).replace("'", "''"))# if isinstance(data[keys[i]], str) else data[keys[i]])  # 将单引号替换成两个单引号 否者sql语句语法出错
                    sql += "'%s', "
                    update_sql += aim_keys[i] + " = '%s', "%values[-1]

                elif value_types[i] == 'clob':
                    text = str(data[keys[i]]).replace("'", "''")
                    if not text:
                        sql += "'%s', "
                        values.append(text)
                        update_sql += aim_keys[i] + " = '%s', "%values[-1]
                    else:
                        values_ = tools.cut_string(text, 2000)

                        clob_text = ''
                        for value in values_:
                            clob_text += "to_clob('%s') || "%value

                        clob_text = clob_text[:-len(' || ')]
                        values.append(clob_text)
                        sql += "%s, "

                        update_sql += aim_keys[i] + " = %s, "%values[-1]

                elif value_types[i] == 'int':
                    if isinstance(data[keys[i]], int):
                        values.append(data[keys[i]])
                        sql += '%d, '
                        update_sql += aim_keys[i] + " = %d, "%values[-1]
                    elif isinstance(data[keys[i]], str):
                        sql += '%s, '
                        if data[keys[i]]:
                            values.append(data[keys[i]])
                        else:
                            values.append('null')
                        update_sql += aim_keys[i] + " = %s, "%values[-1]
                    else:  # _id
                        values.append(int(str(data[keys[i]])[-6:], 16))
                        sql += '%d, '
                        update_sql += aim_keys[i] + " = %d, "%values[-1]

                elif value_types[i] == 'date':
                    values.append(data[keys[i]].replace('年', '-').replace('月', '-').replace('日', ''))
                    if self._is_oracle:
                        format_date = 'yyyy-mm-dd hh24:mi:ss'[:len(values[-1]) if len(values[-1]) <= 10 else None]
                        sql += "to_date('%s','{}'), ".format(format_date)
                        update_sql += aim_keys[i] + "= to_date('%s','%s'), "%(values[-1], format_date)
                    else:
                        sql += "'%s', "
                        update_sql += aim_keys[i] + " = '%s', "%values[-1]

                elif value_types[i] == 'vint':
                     values.append(keys[i])
                     sql += '%s, '
                     update_sql += aim_keys[i] + " = %s, "%values[-1]

                elif value_types[i] == 'vstr':
                     values.append(keys[i])
                     sql += "'%s', "
                     update_sql += aim_keys[i] + " = '%s', "%values[-1]

                elif value_types[i] == 'sint':
                    value = self._oracledb.find(keys[i], fetch_one = True)[0]
                    values.append(value)
                    sql += '%d, '
                    update_sql += aim_keys[i] + " = %d, "%value

                elif value_types[i] == 'sstr':
                    value = self._oracledb.find(keys[i], fetch_one = True)[0]
                    values.append(value)
                    sql += "'%s', "
                    update_sql += aim_keys[i] + " = '%s', "%value

                else:
                    log.error('%s不符合key_map规定格式'%value_types[i])
                    return

            sql = sql[:-2] + ")"
            sql = sql%tuple(values)

            if self._unique_key_mapping_source_key:
                aim_key = tuple(self._unique_key_mapping_source_key.keys())[0]

                value = tuple(self._unique_key_mapping_source_key.values())[0]
                temp_var = value.split('_', 1)

                source_key_types = temp_var[0]
                source_key = temp_var[1]

                if source_key_types == 'str':
                    update_sql = update_sql[:-2] + " where %s = '%s'" %(aim_key, data[source_key])
                elif source_key_types == 'int':
                    update_sql = update_sql[:-2] + " where %s = %d" %(aim_key, data[source_key])

            log.debug(sql)
            # tools.write_file(self._aim_table + '.txt', sql, 'w+')
            def exception_callfunc(e):
                if 'ORA-00001' in str(e):
                    if self._update_read_status:
                        self._mongodb.update(self._source_table, data, {'read_status':1})

            if self._aim_db.add(sql, exception_callfunc):
                self._export_count += 1
                if self._update_read_status:
                    self._mongodb.update(self._source_table, data, {'read_status':1})

            elif self._unique_key_mapping_source_key:
                log.debug(update_sql)
                if self._aim_db.update(update_sql):
                    self._update_count += 1
                    if self._update_read_status:
                        self._mongodb.update(self._source_table, data, {'read_status':1})



        log.debug('''
            共导出%d条数据
            共更新%d条数据
            '''%(self._export_count, self._update_count))

    def close(self):
        self._aim_db.close()


if __name__ == '__main__':
    task_id = 22

    key_map = {
        'program_id': 'vint_sequence.nextval',
        'search_type': 'int_search_type',
        'program_name': 'str_title',
        'program_url': 'str_url',
        'release_date': 'date_release_time',
        'image_url': 'str_image_url',
        'program_content':'str_content',
        'task_id': 'vint_%d'%task_id,
        'keyword':'str_keyword',
        'keyword_count':'int_keyword_count',
        'check_status':'vint_202'
    }

    # export = ExportData('VA_content_info', 'tab_ivms_program_info', key_map, 'program_url')
    # export.export_to_oracle()
    format_date = 'yyyy-mm-dd hh24:mi:ss'
    date_str = '2017'

    print(len('yyyy-mm-dd'))
    format_date = format_date[:len(date_str) if len(date_str) <= 10 else None]
    print(format_date)


