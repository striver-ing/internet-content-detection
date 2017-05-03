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
from wwa.parsers import wechat_account_parser
import wwa.export_data as export_data
def main():
    def begin_callback():
        log.info('\n********** WWA_wechat_account begin **********')
        db = MongoDB()
        db.delete('WWA_wechat_account_url', {})

    def end_callback():
        # export_data.main()
        log.info('\n********** WWA_wechat_account end **********')

    parser_params = {'keyword':'重庆'}

    # 配置spider
    spider = Spider(tab_urls = 'WWA_wechat_account_url', tab_site = 'WWA_wechat_site_info', tab_content = 'WWA_wechat_official_accounts', content_unique_key = 'account_id', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = parser_params)

    # 添加parser
    spider.add_parser(wechat_account_parser)

    spider.start()

if __name__ == '__main__':
    main()
