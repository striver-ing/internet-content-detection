# -*- coding: utf-8 -*-
'''
Created on 2016-11-16 16:25
---------
@summary: 操作oracle数据库
---------
@author: Boris
'''
import sys
sys.path.append('../')
import init
import cx_Oracle
import utils.tools as tools
from utils.log import log

STOP_ORCL = False #禁用oracle

IP        = tools.get_conf_value('config.conf', 'oracledb', 'ip')
PORT      = int(tools.get_conf_value('config.conf', 'oracledb', 'port'))
DB        = tools.get_conf_value('config.conf', 'oracledb', 'db')
USER_NAME = tools.get_conf_value('config.conf', 'oracledb', 'user_name')
USER_PASS = tools.get_conf_value('config.conf', 'oracledb', 'user_pass')

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls, *args, **kwargs)

        return cls._inst


class OracleDB(Singleton):
    def __init__(self, ip = IP, port = PORT, db = DB, user_name = USER_NAME, user_pass = USER_PASS):
        super(OracleDB, self).__init__()

        if STOP_ORCL:
            return

        if not hasattr(self,'conn'):
            try:
                self.conn = cx_Oracle.connect(user_name, user_pass, '%s:%d/%s'%(ip, port, db))
                self.cursor = self.conn.cursor()
            except Exception as e:
                raise
            else:
                log.debug('连接到数据库 %s'%db)

    def find(self, sql, fetch_one = False):
        if STOP_ORCL:
            return []

        result = []
        if fetch_one:
            result =  self.cursor.execute(sql).fetchone()
        else:
            result =  self.cursor.execute(sql).fetchall()

        return result

    def add(self, sql, exception_callfunc = ''):
        if STOP_ORCL:
            return True

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            if exception_callfunc:
                exception_callfunc(e)

            return False
        else:
            return True

    def update(self, sql):
        if STOP_ORCL:
            return True

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def delete(self, sql):
        if STOP_ORCL:
            return True

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def set_unique_key(self, table, key):
        if STOP_ORCL:
            return

        try:
            sql = 'alter table %s add unique (%s)'%(table, key)
            self.cursor.execute(sql)
            self.conn.commit()

        except Exception as e:
            log.error(table + ' ' + str(e) + ' key = '+ key)
        else:
            log.debug('%s表创建唯一索引成功 索引为 %s'%(table, key))

    def close(self):
        if STOP_ORCL:
            return

        self.cursor.close()
        self.conn.close()