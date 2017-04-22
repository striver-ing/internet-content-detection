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
from va_app.parsers import *
def main():
    def begin_callback():
        log.info('\n********** VA_APP begin **********')
        db = MongoDB()
        db.delete('VAApp_urls', {})

    def end_callback():
        log.info('\n********** VA_APP end **********')


    # 配置spider
    spider = Spider(tab_urls = 'VAApp_urls', tab_site = 'VAApp_site_info', tab_content = 'VAApp_content_info', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = {})

    # 添加parser
    spider.add_parser(headline_parser)
    spider.add_parser(kuaibao_parser)

    spider.start()

if __name__ == '__main__':
    main()
