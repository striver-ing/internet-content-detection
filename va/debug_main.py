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
    search_keyword1 = ['成龙']
    search_keyword2 = []
    search_keyword3 = []

    parser_params = {
                'search_keyword1':search_keyword1,
                'search_keyword2':search_keyword2,
                'search_keyword3':search_keyword3
                }

    def begin_callback():
        log.info('\n********** VA begin **********')

    def end_callback():
        # 更新关键词状态 做完
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
    # spider.add_parser(douban_parser)

    spider.start()

if __name__ == '__main__':
    main()
