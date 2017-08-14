import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from utils.export_data import ExportData
import time
from db.mongodb import MongoDB
from db.oracledb import OracleDB

# 需配置
from wwa.parsers import wechat_account_parser
import wwa.wechat_export_data as export_data

def main():
    oracledb = OracleDB()
    sql = 'select t.KEYWORD from TAB_MVMS_SEARCH_INFO t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time  and search_type = 701'
    result_list = oracledb.find(sql)
    if not result_list:
        log.debug('无任务 结束')
        return

    keywords = []
    for result in result_list:
        keywords.extend(result[0].split(','))

    def begin_callback():
        log.info('\n********** WWA_wechat_account begin **********')
        db = MongoDB()
        db.delete('WWA_wechat_account_url', {})

    def end_callback():
        log.info('\n********** WWA_wechat_account end **********')
        export_data.account_main()

    parser_params = {'keywords': keywords}

    # 配置spider
    spider = Spider(tab_urls = 'WWA_wechat_account_url', tab_site = 'WWA_wechat_site_info', tab_content = 'WWA_wechat_official_accounts', content_unique_key = 'account_id', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = parser_params)

    # 添加parser
    spider.add_parser(wechat_account_parser)

    spider.start()

if __name__ == '__main__':
    main()
