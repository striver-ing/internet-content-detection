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
from wwa.parsers import *
import wwa.export_search_app_data as export_data
def main():
    db = MongoDB()
    oracle = OracleDB()

    def begin_callback():
        #db.update('WWA_app_urls',{'depth':0}, {'status':0})
        db.delete('WWA_search_app_urls')
        log.info('\n********** wwa begin **********')

    def end_callback():
        log.info('\n********** wwa end **********')
        export_data.main()

    keywords = []

    result_list = oracle.find('select keyword from TAB_MVMS_SEARCH_INFO where  MONITOR_START_TIME <= sysdate AND MONITOR_END_TIME >= sysdate and search_type=703')
    if not result_list:
        log.debug('无任务 结束')
        return

    keywords = []
    for result in result_list:
        keywords.extend(result[0].split(','))
    parser_params = {'keywords' : keywords}

    # 配置spider
    spider = Spider(tab_urls = 'WWA_search_app_urls', tab_site = 'WWA_search_app_site_info', tab_content = 'WWA_search_app_content_info', begin_callback = begin_callback, end_callback = end_callback, parser_params = parser_params)

    # 添加parser
    spider.add_parser(yingyongbao_parser)
    spider.add_parser(android_market_parser)
    spider.add_parser(baidu_mobile_assistant_parser)
    spider.add_parser(mobile360_assistant_parser)
    spider.start()

if __name__ == '__main__':
    main()