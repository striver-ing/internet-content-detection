# -*- coding: utf-8 -*-
'''
Created on 2017-02-28 11:50
---------
@summary: 图片违规检测
---------
@author: Boris
'''

import sys
sys.path.append('..')
import ctypes
import utils.tools as tools
import os
import utils.ffmpeg_manager as ffmpeg_manager

TEMP_IMAGE_SAVE_PATH = '.img/'
tools.del_file(TEMP_IMAGE_SAVE_PATH + '*.jpg')  # 删除残留的jpg

class ImagePornRecg(object):
    """图片违规检测"""
    __image_porn_dll = ctypes.windll.LoadLibrary('ImagePornRecg.dll')

    def __init__(self):
        super(ImagePornRecg, self).__init__()

        self._porn_image_index = ImagePornRecg.__image_porn_dll.Pic_InitializeModel(1)

    # @tools.log_function_time
    def image_predict(self, image_url):
        if not image_url:
            return -1
        # 如果是网络图片 先下载 识别 然后删除
        if image_url.startswith('http'):
            local_image_path = TEMP_IMAGE_SAVE_PATH + tools.get_current_date(date_format = '%Y%m%d%H%M%S.%f') + '.jpg'
            is_success = tools.download_file(image_url, local_image_path)
            image_url = local_image_path if is_success else image_url
            result = ImagePornRecg.__image_porn_dll.Pic_Predict(image_url, self._porn_image_index)
            tools.del_file(local_image_path)

        # 如果是本地图片 不是jpg格式 则需要转成jpg格式
        elif not image_url.endswith('jpg'):
            jpg_image_url = image_url[:image_url.rfind('.')] + '.jpg'
            is_success = ffmpeg_manager.convert_file_format(image_url, jpg_image_url)
            image_url = jpg_image_url if is_success else image_url
            result = ImagePornRecg.__image_porn_dll.Pic_Predict(image_url, self._porn_image_index)

        else:
            result = ImagePornRecg.__image_porn_dll.Pic_Predict(image_url, self._porn_image_index)
        return result

    def close(self):
        ImagePornRecg.__image_porn_dll.Pic_ReleaseModel(self._porn_image_index)

def main():
    image_porn_recg = ImagePornRecg()

    result = image_porn_recg.image_predict("http://wx2.sinaimg.cn/large/5d08b5a3gy1fhdt8fxsj7j20hs0bvt9i.jpg")
    image_porn_recg.close()

    print(result)

if __name__ == '__main__':
    main()

