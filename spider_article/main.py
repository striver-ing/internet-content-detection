import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from utils.export_data import ExportData
import time

# 需配置
from spider_article.parsers import *
def main():

    def begin_callback():
        log.info('\n********** spider_article begin **********')

    def end_callback():
        log.info('\n********** spider_article end **********')


    # 配置spider
    spider = Spider(tab_urls = 'article_urls', tab_site = 'article_site_info', tab_content = 'article_text_info', parser_count = 40, begin_callback = begin_callback, end_callback = end_callback, parser_params = {})

    # 添加parser
    spider.add_parser(cctv_parser)
    spider.add_parser(ifeng_parser)
    spider.add_parser(xinhua_parser)
    spider.add_parser(tencent_parser)
    spider.add_parser(sohu_parser)
    spider.add_parser(wangyi_parser)
    spider.add_parser(people_parser)
    spider.add_parser(sina_parser)
    spider.start()

if __name__ == '__main__':
    main()
