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
from game_app.parsers import *
def main():


    def begin_callback():
        db.update('GameApp_urls',{'depth':0}, {'status':0})
        log.info('\n********** game_app begin **********')

    def end_callback():
        log.info('\n********** game_app end **********')

    # 配置spider
    spider = Spider(tab_urls = 'GameApp_urls', tab_site = 'GameApp_site_info', tab_content = 'GameApp_content_info', begin_callback = begin_callback, end_callback = end_callback)

    # 添加parser
    spider.add_parser(yingyongbao_parser)
    spider.add_parser(android_market_parser)
    spider.add_parser(baidu_mobile_assistant_parser)
    spider.add_parser(mobile360_assistant_parser)
    spider.start()

if __name__ == '__main__':
    main()
