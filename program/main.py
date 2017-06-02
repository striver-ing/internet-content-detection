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
from program.parsers import *
def main():
    db = MongoDB()
    db.set_unique_key('PROGRAM_EPISODE_info', 'episode_url')
    db.set_ensure_index('PROGRAM_EPISODE_info', 'read_status')

    def begin_callback():
        log.info('\n********** program begin **********')
        db.delete('PROGRAM_urls')
        # db.update('PROGRAM_urls', {'status' : 1}, {'status' : 0})

    def end_callback():
        log.info('\n********** program end **********')


    # 配置spider
    spider = Spider(tab_urls = 'PROGRAM_urls', tab_site = 'PROGRAM_site_info', tab_content = 'PROGRAM_info', content_unique_key = 'program_url', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = {})

    # 添加parser
    spider.add_parser(mgtv_parser)
    spider.add_parser(news_v1_parser)
    spider.add_parser(tencent_parser)
    spider.add_parser(ku6_parser)

    spider.start()

if __name__ == '__main__':
    main()
