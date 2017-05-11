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
from wwa.parsers import *
import wwa.app_export_data as export_data
def main():
    db = MongoDB()
    db.set_unique_key('WWA_app_vioation_content_info', 'url')
    db.set_ensure_index('WWA_app_vioation_content_info', 'read_status')

    def begin_callback():
        log.info('\n********** WWA_APP begin **********')
        db.delete('WWA_app_urls', {})

    def end_callback():
        export_data.main()
        log.info('\n********** WWA_APP end **********')


    # 配置spider
    spider = Spider(tab_urls = 'WWA_app_urls', tab_site = 'WWA_app_site_info', tab_content = 'WWA_app_content_info', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = {})

    # 添加parser
    spider.add_parser(headline_parser)
    spider.add_parser(kuaibao_parser)

    spider.start()

if __name__ == '__main__':
    main()
