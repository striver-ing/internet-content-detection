import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from utils.export_data import ExportData
import time
from db.mongodb import MongoDB

# 需配置
from live_app.parsers import *
def main():
    db = MongoDB()

    def begin_callback():
        log.info('\n********** live_app begin **********')
        db.delete('LiveApp_urls', {})
        db.update('LiveApp_anchor_info', {}, {"live_view" : 0})
        db.update('LiveApp_anchor_info', {}, {"watched_count" : 0})
        db.update('LiveApp_anchor_info', {}, {'read_status':0})

    def end_callback():
        # 更新关键词状态 做完
        log.info('\n********** live_app end **********')

    # 配置spider
    spider = Spider(tab_urls = 'LiveApp_urls', tab_site = 'LiveApp_site_info', tab_content = 'LiveApp_anchor_info',
                    parser_count = 1, begin_callback = begin_callback, end_callback = end_callback,
                    content_unique_key = 'room_id')

    # 添加parser
    spider.add_parser(inke_parser)
    spider.add_parser(huajiao_parser)
    spider.add_parser(momo_parser)


    spider.start()

if __name__ == '__main__':
    main()
