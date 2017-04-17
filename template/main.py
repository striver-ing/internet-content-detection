import sys
sys.path.append('../')
import init
from utils.log import log
from base.spider import Spider
import utils.tools as tools
from utils.export_data import ExportData
import time

# 需配置
from template.parsers import *
def main():
    search_task_sleep_time = int(tools.get_conf_value('config.conf', 'task', 'search_task_sleep_time'))
    # 更新任务状态 正在做的更新为等待
    while True:
        # 查询任务状态 有正在做的 sleep contine
        # TODO

        search_keyword1 = ['hi']
        search_keyword2 = ['hello']
        search_keyword3 = ['hello, hi']
        task_id = 1

        # 任务为空 sleep continue
        # TODO

        def begin_callback():
            log.info('\n********** template begin **********')
            # 更新任务状态 doing

        def end_callback():
            log.info('\n********** template end **********')

            # 更新任务状态 done

            # 导出数据
            # export_data = ExportData(source_table = '', aim_table = '', key_map = '', unique_key = '')
            # export_data.export_to_oracle()


        # 配置spider
        spider = Spider(tab_urls = 'template_urls', tab_site = 'template_site_info', tab_content = 'template_content_info', parser_count = 1, begin_callback = begin_callback, end_callback = end_callback, parser_params = {})

        # 添加parser
        spider.add_parser(xxx_parser)
        spider.add_parser(yyy_parser)

        spider.start()

        # time.sleep(search_task_sleep_time)
        break

if __name__ == '__main__':
    main()
