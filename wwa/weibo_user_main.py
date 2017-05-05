import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from db.oracledb import OracleDB
from utils.export_data import ExportData
import time

# 需配置
from wwa.parsers import weibo_user_parser
def main():
    db = OracleDB()

    sql = 'select t.KEYWORD from TAB_MVMS_SEARCH_INFO t where sysdate >= t.monitor_start_time and sysdate <= t.monitor_end_time  and search_type = 702'
    result = db.find(sql, fetch_one=False)
    if not result:
        log.debug('无任务 结束')
        return

    parser_params = []
    for i in result:
        parser_params.extend(str(i[0]).split(','))

    def begin_callback():
        log.info('\n********** WWA_weibo_user begin **********')

    def end_callback():
        # 导出数据
        key_map = {
            'id': 'int__id',
            'name': 'str_name',
            'sex': 'int_sex',
            'summary': 'str_summary',
            'fans_count': 'int_fans_count',
            'blog_verified': 'str_blog_verified',
            'is_verified': 'int_is_verified',
            'account_url': 'str_url',
            'follow_count': 'int_follow_count',
            'image_url': 'str_image_url',
            'monitor_status': 'vint_401',
            'SEARCH_TYPE' : 'vint_702',
            'region' : 'str_area'
        }

        export = ExportData('WWA_weibo_user_info', 'tab_mvms_weibo_info', key_map, 'account_url')
        export.export_to_oracle()
        log.info('\n********** WWA_weibo_user end **********')

    # 配置spider
    spider = Spider(tab_urls = 'WWA_weibo_user_urls', tab_site = 'WWA_site_info', tab_content = 'WWA_weibo_user_info',
                    parser_count = 1, begin_callback = begin_callback, end_callback = end_callback,
                    parser_params = parser_params)

    # 添加parser
    spider.add_parser(weibo_user_parser)
    spider.start()

if __name__ == '__main__':

    main()
