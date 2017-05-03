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
def main():
    db = MongoDB()
    oracle = OracleDB()

    def begin_callback():
        #db.update('WWA_app_urls',{'depth':0}, {'status':0})
        db.delete('WWA_search_app_urls')
        log.info('\n********** wwa begin **********')

    def end_callback():
        log.info('\n********** wwa end **********')

    keywords = []

    results = oracle.find('select keyword from TAB_MVMS_SEARCH_INFO where  MONITOR_START_TIME <= sysdate AND MONITOR_END_TIME >= sysdate and search_type=702')
    for result in results:
        for res in result:
            keywords = keywords + [res]

    parser_params = {'keyword' : keywords}

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