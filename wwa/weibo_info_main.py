import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from db.oracledb import OracleDB
from utils.export_data import ExportData
import time
from db.mongodb import MongoDB

# 需配置
from wwa.parsers import weibo_info_parser
def main():
    db = OracleDB()
    mongodb = MongoDB()

    sql = 'select t.ID from TAB_MVMS_WEIBO_INFO t where monitor_status = 402'
    result = db.find(sql, fetch_one=False)
    if not result:
        log.debug('无任务 结束')
        return

    parser_params = []
    for i in result:
        parser_params.extend(str(i[0]).split(','))

    def begin_callback():
        log.info('\n********** WWA_weibo_info begin **********')
        mongodb.delete('WWA_weibo_info_urls')


    def end_callback():
        # 导出数据
        key_map = {
            'id': 'int__id',
            'release_time': 'date_release_time',
            'come_from': 'str_come_from',
            'content': 'clob_content',
            'image_url': 'str_image_url',
            'video_url': 'str_video_url',
            'transpond_count': 'int_transpond_count',
            'praise_count': 'int_praise_count',
            'check_status': 'vint_301',
            'weibo_id': 'int_weibo_id',
            'article_url': 'str_url',
            'violate_status': 'int_violate_id',
            'sensitive_id' : 'int_sensitive_id',
            'record_time' : 'date_record_time'
        }

        export = ExportData('WWA_weibo_info_info', 'tab_mvms_weibo_article_info', key_map, unique_key='ARTICLE_url')
        export.export_to_oracle()
        log.info('\n********** WWA_weibo_info end **********')

    # 配置spider
    spider = Spider(tab_urls = 'WWA_weibo_info_urls', tab_site = 'WWA_site_info', tab_content = 'WWA_weibo_info_info',
                    parser_count = 1, begin_callback = begin_callback, end_callback = end_callback,
                    parser_params = parser_params)

    # 添加parser
    spider.add_parser(weibo_info_parser)
    spider.start()

if __name__ == '__main__':
    main()
    # # 导出数据
    # key_map = {
    #     'id': 'int__id',
    #     'release_time': 'date_release_time',
    #     'come_from': 'str_come_from',
    #     'content': 'clob_content',
    #     'image_url': 'str_image_url',
    #     'video_url': 'str_video_url',
    #     'transpond_count': 'int_transpond_count',
    #     'praise_count': 'int_praise_count',
    #     'check_status': 'vint_301',
    #     'weibo_id': 'int_weibo_id',
    #     'article_url': 'str_url',
    #     'violate_status': 'int_violate_id',
    #     'sensitive_id' : 'int_sensitive_id',
    #     'record_time' : 'date_record_time'
    # }

    # export = ExportData('WWA_weibo_info_info', 'tab_mvms_weibo_article_info', key_map, unique_key='ARTICLE_url')
    # export.export_to_oracle()
