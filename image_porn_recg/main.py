# -*- coding: utf-8 -*-
'''
Created on 2017-03-01 09:44
---------
@summary: 图片识别的主程序
---------
@author: Boris
'''

from image_porn_control import ImagePornControl
from image_collector import Collector
import time

import sys
sys.path.append('../')

from utils.log import log
import utils.tools as tools


def main():
    # 需要图片鉴黄的表需要加上一下三个字段
    # * sexy_image_status   淫秽色情图像，多个逗号分隔
    # * sexy_image_url      淫秽色情图像地址，多个逗号分隔
    # * image_pron_status   图片扫描状态

    porn_thread_count = int(tools.get_conf_value('../config.conf', "image_porn", "porn_thread_count"))

    image_tables = tools.get_conf_value('../config.conf', "image_porn", "image_tables")
    image_tables = image_tables.split(',')

    deal_image_tables_one_by_one = int(tools.get_conf_value('../config.conf', "image_porn", 'deal_image_tables_one_by_one'))

    image_porns = []

    for image_table in image_tables:
        log.debug('图片识别 表名为 ：' + image_table)
        collector = Collector(image_table)
        collector.start()

        count = 0
        while count < porn_thread_count:
            image_porn = ImagePornControl(collector, image_table)
            image_porn.start()
            image_porns.append(image_porn)

            count = count + 1

        if deal_image_tables_one_by_one:
            for image_porn in image_porns:
                image_porn.join()

        else:
            image_porns = []


if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)