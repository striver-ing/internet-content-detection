import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from utils.export_data import ExportData
import time
from db.mongodb import MongoDB
from db.oracledb import OracleDB

# 需配置
from wwa.parsers import wechat_article_parser
import wwa.wechat_export_data as export_data
def main():
    oracledb = OracleDB()
    sql = 'select t.account_id, t.monitor_type from TAB_MVMS_WECHAT_INFO t where monitor_status = 402'
    result_list = oracledb.find(sql)
    if not result_list:
        log.debug('无任务 结束')
        return

    # keywords = []
    # for result in result_list:
    #     keywords.append(result[0])

    def begin_callback():
        log.info('\n********** WWA_wechat_article begin **********')
        db = MongoDB()
        db.delete('WWA_wechat_article_url', {})

    def end_callback():
        log.info('\n********** WWA_wechat_article end **********')
        export_data.article_main()

    parser_params = result_list

    # 配置spider
    spider = Spider(tab_urls = 'WWA_wechat_article_url', tab_site = 'WWA_wechat_site_info', tab_content = 'WWA_wechat_article', content_unique_key = 'title', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = parser_params)

    # 添加parser
    spider.add_parser(wechat_article_parser)

    spider.start()

if __name__ == '__main__':
    main()