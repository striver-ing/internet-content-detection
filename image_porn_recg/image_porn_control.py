# -*- coding: utf-8 -*-
'''
Created on 2017-02-28 15:38
---------
@summary: 图片违规鉴别控制器
---------
@author: Boris
'''
from image_porn_recg import ImagePornRecg
from mongodb import MongoDB

import sys
sys.path.append('..')

import utils.tools as tools
import base.constance as Constance
from utils.log import log
import threading
import time

class ImagePornControl(threading.Thread):
    def __init__(self, collector, tab_images):
        super(ImagePornControl, self).__init__()

        self._collector = collector
        self._tab_images = tab_images

        self._deal_image_count = int(tools.get_conf_value('../config.conf', "image_porn", "deal_image_count"))
        self._interval = int(tools.get_conf_value('../config.conf', "image_porn", "sleep_time"))


        self._db = MongoDB()
        self._image_porn_recg = ImagePornRecg()

    def run(self):
        while True:
            # 判断是否结束
            if self._collector.is_finished():
                break

            images = self._collector.get_images(self._deal_image_count)

            for image in images:
                try:
                    image_urls = image['sexy_image_url']
                    image_urls = image_urls if isinstance(image_urls, list) else [image_urls]

                    sexy_image_status = [] # 检测结果

                    for image_url in image_urls:
                        try:
                            result = self._image_porn_recg.image_predict(image_url)
                        except Exception as e:
                            log.debug(e)
                        else:
                            log.debug('''
                                image_url :%s
                                result    :%d
                                '''%(image_url, result))

                            sexy_image_status.append(str(result))

                    sexy_image_status = ','.join(sexy_image_status)

                    self._db.update(self._tab_images, {'_id':image['_id']}, {'image_pron_status':Constance.DONE, 'sexy_image_status':sexy_image_status})

                except Exception as e:
                    raise
                    # log.error('%s 表中无 image_url 字段'%self._tab_images)

            time.sleep(self._interval)

        self.finished()

    def finished(self):
        self._image_porn_recg.close()
