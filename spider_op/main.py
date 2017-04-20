import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from utils.export_data import ExportData
import time
import init
from db.mongodb import MongoDB

# 需配置
from spider_op.parsers import *
def main():
    db = MongoDB()
    def begin_callback():
        log.info('\n********** template begin **********')
        db.delete('op_urls', {})
        db.delete('op_content_info', {})
    def end_callback():
        log.info('\n********** template end **********')

        # 更新任务状态 done

        # 导出数据
        # export_data = ExportData(source_table = '', aim_table = '', key_map = '', unique_key = '')
        # export_data.export_to_oracle()


    # 配置spider
    spider = Spider(tab_urls = 'op_urls', tab_site = 'op_site_info', tab_content = 'op_content_info', parser_count = 20, begin_callback = begin_callback, end_callback = end_callback, parser_params = {})

    # 添加parser
    # spider.add_parser(cctv_parser)
    spider.add_parser(hejiang_parser)
    spider.add_parser(luzhou_parser)
    spider.add_parser(luxian_parser)
    spider.add_parser(naxi_parser)
    spider.add_parser(longmatan_parser)
    spider.start()

if __name__ == '__main__':
    main()
