import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from db.oracledb import OracleDB
from utils.export_data import ExportData
import time

# 需配置
from va.parsers import *
def main():
    search_task_sleep_time = int(tools.get_conf_value('config.conf', 'task', 'search_task_sleep_time'))

    db = OracleDB()

    #  更新符合日期条件的任务状态 未做
    sql = 'update tab_ivms_task_info t set t.task_status = 501 where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time'
    db.update(sql)

    # 更新关键词状态 未做
    sql = 'update tab_ivms_task_keyword k set k.finish_status = 601 where k.task_id in (select t.task_id from tab_ivms_task_info t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time)'
    db.update(sql)

    while True:
        # 查任务
        log.debug('查询任务...')

        sql = 'select t.task_id from TAB_IVMS_TASK_INFO t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time and t.task_status = 501 and task_type = 802'
        result = db.find(sql, fetch_one = True)
        if not result:
            break

        task_id = result[0]

        while True:
            # 查看是否有正在执行的任务
            sql = 'select t.* from TAB_IVMS_TASK_KEYWORD t where t.task_id = %d and finish_status = 602'%task_id
            do_task = db.find(sql, fetch_one = True)
            if do_task:
                time.sleep(search_task_sleep_time)
                continue

            sql = 'select id,task_id,keyword1,keyword2,keyword3 from tab_ivms_task_keyword t where t.task_id = %d and finish_status = 601'%task_id
            result = db.find(sql, fetch_one = True)
            if not result:
                break

            keyword_id = result[0]
            task_id = result[1]
            search_keyword1 = result[2].split(',') if result[2] else []
            search_keyword2 = result[3].split(',') if result[3] else []
            search_keyword3 = result[4].split(',') if result[4] else []

            # parser_params = {
            #     'search_keyword1':search_keyword1,
            #     'search_keyword2':search_keyword2,
            #     'search_keyword3':search_keyword3,
            #     'task_id':task_id
            # }

            parser_params = {
                'search_keyword1': search_keyword1,
                'search_keyword2': search_keyword3,
                'search_keyword3': search_keyword2,
                'task_id': task_id
            }

            def begin_callback():
                log.info('\n********** VA begin **********')
                # 更新任务状态 正在做
                sql = 'update TAB_IVMS_TASK_INFO set task_status = 502 where task_id = %d'%task_id
                db.update(sql)

                # 更新关键词状态 正在做
                sql = 'update tab_ivms_task_keyword set finish_status = 602 where id = %d'%keyword_id
                db.update(sql)

            def end_callback():
                # 更新关键词状态 做完
                sql = 'update tab_ivms_task_keyword set finish_status = 603 where id = %d'%keyword_id
                db.update(sql)

                # 如果该任务的所有关键词都做完 则更新任务状态为做完
                sql = 'select t.* from tab_ivms_task_keyword t where task_id = %d and finish_status = 601'%task_id
                results = db.find(sql)
                if not results:
                    # # 导出数据
                    # key_map = {
                    #     'program_id': 'vint_sequence.nextval',
                    #     'search_type': 'int_search_type',
                    #     'program_name': 'str_title',
                    #     'program_url': 'str_url',
                    #     'release_date': 'date_release_time',
                    #     'image_url': 'str_image_url',
                    #     'program_content':'str_content',
                    #     'task_id': 'vint_%d' % task_id,
                    #     'keyword':'str_keyword',
                    #     'keyword_count':'int_keyword_count',
                    #     'check_status':'vint_202'
                    # }

                    # export = ExportData('VA_content_info', 'tab_ivms_program_info', key_map, 'program_url')
                    # export.export_to_oracle()

                    # 更新任务状态 做完
                    sql = 'update TAB_IVMS_TASK_INFO set task_status = 503 where task_id = %d'%task_id
                    db.update(sql)
                    log.info('\n********** VA end **********')

            # 配置spider
            spider = Spider(tab_urls = 'VA_urls', tab_site = 'VA_site_info', tab_content = 'VA_content_info',
                            parser_count = 1, begin_callback = begin_callback, end_callback = end_callback,
                            parser_params = parser_params)

            # 添加parser
            spider.add_parser(baidu_parser)
            spider.add_parser(magnet_parser)
            spider.add_parser(netdisk_parser)
            spider.add_parser(weibo_parser)
            spider.add_parser(wechat_parser)
            spider.add_parser(soubaidupan_parser)
            spider.add_parser(douban_parser)

            spider.start()

            time.sleep(search_task_sleep_time)

if __name__ == '__main__':
    main()
