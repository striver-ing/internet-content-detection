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
    INSERT = 1
    UPDATE = 2
    EXCEPTION = 3

    def __init__(self, source_table = '', aim_table = '', key_map = '', unique_key = None, unique_key_mapping_source_key = None, update_read_status = True, condition = {'read_status':0}, datas = [], callback = ''):
        '''
        @summary: 初始化
        ---------
        @param source_table: 源table mongo数据库
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
            'aim_key8' : 'clob_key8'                 # 目标键 = 源键对应的值         类型为clob
            'aim_key9' : 'clob_key8'                 # 目标键 = 源键对应的值         类型为str
        }

        @param unique_key:    唯一的key 目标数据库根据该key去重
        @param unique_key_mapping_source_key: 目标表中唯一的key所对应的源表中的key 该值不为空时 更新目标表中已有的数据
         eg: unique_key_mapping_source_key = {
            'url':'str_url'                         # 目标键 = 源键对应的值         类型为str
         }
        @param condition:    导出满足什么样条件的数据 默认是read_status = 0 的
        @param datas:   要导出的数据，格式为[{...},{...}] 或者 {}用于直接将json数组导入到目标表，为空时默认导出mongodb的数据
        @param callback 导出数据的回调，导出一组，执行一次，callback(execute_type, sql) execute_type为执行类型（ExportData.INSERT、ExportData.UPDATE、ExportData.EXCEPTION）
        sql 为执行的语句
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

        self._mongodb = MongoDB() if self._source_table else ''
        self._datas = datas

        self._is_oracle = False
        self._export_count = 0
        self._update_count = 0
        self._unique_key_mapping_source_key = unique_key_mapping_source_key


    def export_to_oracle(self, source_table = '', aim_table = '', key_map = '', unique_key = None, unique_key_mapping_source_key = None, update_read_status = True, condition = {'read_status':0}, datas = [], callback = ''):
        if source_table or datas:
            self._source_table = source_table
            self._aim_table = aim_table
            self._key_map = key_map
            self._unique_key = unique_key
            self._export_count = 0
            self._update_count = 0
            self._unique_key_mapping_source_key = unique_key_mapping_source_key
            self._update_read_status = update_read_status if not datas else False
            self._condition = condition
            self._datas = datas
            self._callback = callback

        self._aim_db = OracleDB()
        self._is_oracle = True
        return self.__export()

    def export_to_mysql(self, source_table = '', aim_table = '', key_map = '', unique_key = None, unique_key_mapping_source_key = None, update_read_status = True, condition = {'read_status':0}, datas = [], callback = ''):
        if source_table or datas:
            self._source_table = source_table
            self._aim_table = aim_table
            self._key_map = key_map
            self._unique_key = unique_key
            self._export_count = 0
            self._update_count = 0
            self._unique_key_mapping_source_key = unique_key_mapping_source_key
            self._update_read_status = update_read_status if not datas else False
            self._condition = condition
            self._datas = datas
            self._callback = callback

        self._aim_db = MysqlDB()
        return self.__export()

    def make_sql(self, data):
        '''
        @summary:
        ---------
        @param data: 数据字典
        ---------
        @result: 当unique_key_mapping_source_key不为空时返回insert_sql, update_sql 否则返回insert_sql
        '''
        aim_keys = tuple(self._key_map.keys())
        source_keys = tuple(self._key_map.values())

        # 取源key值 对应的type 和 key （源key包含type 和 key 信息）
        keys = []
        value_types = []
        for source_key in source_keys:
            temp_var = source_key.split('_', 1)
            value_types.append(temp_var[0])
            keys.append(temp_var[1])

        insert_sql = 'insert into ' + self._aim_table + " (" + ', '.join(aim_keys) + ") values ("
        update_sql = 'update ' + self._aim_table + " set "
        values = []
        for i in range(len(keys)):
            if value_types[i] != 'vint' and value_types[i] != 'sint' and value_types[i] != 'sstr' and not data[keys[i]] and data[keys[i]] != 0:
                    values.append('null')
                    insert_sql += '%s, '
                    update_sql += aim_keys[i] + " = %s, "%values[-1]

            elif value_types[i] == 'str':
                values.append(str(data[keys[i]]).replace("'", "''"))# if isinstance(data[keys[i]], str) else data[keys[i]])  # 将单引号替换成两个单引号 否者insert_sql语句语法出错
                insert_sql += "'%s', "
                update_sql += aim_keys[i] + " = '%s', "%values[-1]

            elif value_types[i] == 'clob':
                text = str(data[keys[i]]).replace("'", "''")
                if not text:
                    insert_sql += "'%s', "
                    values.append(text)
                    update_sql += aim_keys[i] + " = '%s', "%values[-1]
                else:
                    values_ = tools.cut_string(text, 2000)

                    clob_text = ''
                    for value in values_:
                        clob_text += "to_clob('%s') || "%value

                    clob_text = clob_text[:-len(' || ')]
                    values.append(clob_text)
                    insert_sql += "%s, "

                    update_sql += aim_keys[i] + " = %s, "%values[-1]

            elif value_types[i] == 'int':
                if isinstance(data[keys[i]], int) or isinstance(data[keys[i]], float) or isinstance(data[keys[i]], str):
                    values.append(data[keys[i]])
                    insert_sql += '%s, '
                    update_sql += aim_keys[i] + " = %s, "%values[-1]

                elif isinstance(data[keys[i]], bool):
                    values.append(data[keys[i]] and 1 or 0)
                    insert_sql += '%s, '
                    update_sql += aim_keys[i] + " = %s, "%values[-1]

                else:  # _id
                    values.append(int(str(data[keys[i]])[-6:], 16))
                    insert_sql += '%s, '
                    update_sql += aim_keys[i] + " = %s, "%values[-1]

            elif value_types[i] == 'date':
                values.append(data[keys[i]].replace('年', '-').replace('月', '-').replace('日', ''))
                if self._is_oracle:
                    format_date = 'yyyy-mm-dd hh24:mi:ss'[:len(values[-1]) if len(values[-1]) <= 10 else None]
                    insert_sql += "to_date('%s','{}'), ".format(format_date)
                    update_sql += aim_keys[i] + "= to_date('%s','%s'), "%(values[-1], format_date)
                else:
                    insert_sql += "'%s', "
                    update_sql += aim_keys[i] + " = '%s', "%values[-1]

            elif value_types[i] == 'vint':
                if isinstance(keys[i], bool):
                    values.append(keys[i] and 1 or 0)
                else:
                    values.append(keys[i])
                insert_sql += '%s, '
                update_sql += aim_keys[i] + " = %s, "%values[-1]

            elif value_types[i] == 'vstr':
                values.append(keys[i])
                insert_sql += "'%s', "
                update_sql += aim_keys[i] + " = '%s', "%values[-1]

            elif value_types[i] == 'sint':
                value = self._aim_db.find(keys[i], fetch_one = True)[0]
                values.append(value)
                insert_sql += '%s, '
                update_sql += aim_keys[i] + " = %s, "%value

            elif value_types[i] == 'sstr':
                value = self._aim_db.find(keys[i], fetch_one = True)[0]
                values.append(value)
                insert_sql += "'%s', "
                update_sql += aim_keys[i] + " = '%s', "%value

            else:
                error_msg = '%s不符合key_map规定格式'%value_types[i]
                raise(Exception(error_msg))

        insert_sql = insert_sql[:-2] + ")"
        insert_sql = insert_sql%tuple(values)

        # log.debug(insert_sql)
        if self._unique_key_mapping_source_key:
            aim_key = tuple(self._unique_key_mapping_source_key.keys())[0]

            value = tuple(self._unique_key_mapping_source_key.values())[0]
            temp_var = value.split('_', 1)

            source_key_types = temp_var[0]
            source_key = temp_var[1]

            if source_key_types == 'str':
                update_sql = update_sql[:-2] + " where %s = '%s'" %(aim_key, data[source_key])
            elif source_key_types == 'int':
                update_sql = update_sql[:-2] + " where %s = %s" %(aim_key, data[source_key])

            log.debug(update_sql)

            return insert_sql, update_sql
        else:
            return insert_sql



    # @tools.run_safe_model(__name__)
    def __export(self):
        if self._unique_key:
            self._aim_db.set_unique_key(self._aim_table, self._unique_key)

        datas = self._mongodb.find(self._source_table, condition = self._condition) if self._mongodb else (self._datas if isinstance(self._datas, list) else [self._datas])
        for data in datas:
            if self._unique_key_mapping_source_key:
                insert_sql, update_sql = self.make_sql(data)
            else:
                insert_sql = self.make_sql(data)

            # tools.write_file(self._aim_table + '.txt', insert_sql, 'w+')
            def exception_callfunc(e):
                if 'ORA-00001' in str(e):
                    if self._update_read_status:
                        self._mongodb.update(self._source_table, data, {'read_status':1})
                else:
                    log.error(insert_sql)

            execute_type = ExportData.EXCEPTION
            sql = ''
            if self._aim_db.add(insert_sql, exception_callfunc):
                self._export_count += 1
                sql = insert_sql
                execute_type = ExportData.INSERT

                if self._update_read_status:
                    self._mongodb.update(self._source_table, data, {'read_status':1})

            elif self._unique_key_mapping_source_key:
                log.debug(update_sql)
                if self._aim_db.update(update_sql):
                    self._update_count += 1
                    sql = update_sql
                    execute_type = ExportData.UPDATE

                    if self._update_read_status:
                        self._mongodb.update(self._source_table, data, {'read_status':1})

            if self._callback:
                self._callback(execute_type, sql)



        log.debug('''
            共导出%s条数据
            共更新%s条数据
            '''%(self._export_count, self._update_count))

        return self._export_count + self._update_count

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
        'task_id': 'vint_%s'%task_id,
        'keyword':'str_keyword',
        'keyword_count':'int_keyword_count',
        'check_status':'vint_202'
    }

    export = ExportData('VA_content_info', 'tab_ivms_program_info', key_map, 'program_url')