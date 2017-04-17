# -*- coding: utf-8 -*-
'''
Created on 2017-03-09 13:56
---------
@summary: 校验 取oracle数据库中的违规知识和与我相关信息，校验游戏app
---------
@author: Boris
'''
import sys
sys.path.append('..')
import init

from db.oracledb import OracleDB
import time

SELEEP_TIME = 5

def main():
    # 查询知识库
    sql = 'select * from tab_gams_knowledge_info t where sysdate >= t.monitor_start_time and sysdate < t.monitor_end_time'

    # 查询待校验的信息
    sql = 'select t.* from tab_gams_app_info t where t.knowledge_check_status = 0'

if __name__ == '__main__':
    main()
