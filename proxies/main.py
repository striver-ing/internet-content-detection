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
from proxies.parsers import *
def main():
    db = MongoDB()
    while True:
        def begin_callback():
            log.info('\n********** proxies begin **********')
            db.delete('proxies_urls')

        def end_callback():
            log.info('\n********** proxies end **********')

            # 更新任务状态 done

            # 导出数据
            # export_data = ExportData(source_table = '', aim_table = '', key_map = '', unique_key = '')
            # export_data.export_to_oracle()


        # 配置spider
        spider = Spider(tab_urls = 'proxies_urls', tab_site = 'proxies_site_info', tab_content = 'proxies_content_info', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = {}, content_unique_key = 'ip')

        # 添加parser
        spider.add_parser(gaoni_parser)

        spider.start()

        # time.sleep(60)
        break

if __name__ == '__main__':
    main()
