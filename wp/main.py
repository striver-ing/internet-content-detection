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
from wp.parsers import *
def main():
    db = MongoDB()

    def begin_callback():
        log.info('\n********** wp begin **********')
        db.delete('WP_urls', {})

    def end_callback():
        # 更新关键词状态 做完
        log.info('\n********** wp end **********')

    # 配置spider
    spider = Spider(tab_urls = 'WP_urls', tab_site = 'WP_site_info', tab_content = 'WP_content_info',
                    parser_count = 20, begin_callback = begin_callback, end_callback = end_callback,
                    content_unique_key = 'title')

    # 添加parser
    spider.add_parser(dongmanla_parser)
    spider.add_parser(zx_novel_parser)
    # spider.add_parser(jisu_cartoon_parser)
    spider.add_parser(ximalaya_parser)


    spider.start()

if __name__ == '__main__':
    main()
