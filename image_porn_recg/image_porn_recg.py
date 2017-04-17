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

tools.del_file('.*.jpg')  # 删除残留的jpg

class ImagePornRecg(object):
    """图片违规检测"""
    __image_porn_dll = ctypes.windll.LoadLibrary('ImagePornRecg.dll')

    def __init__(self):
        super(ImagePornRecg, self).__init__()

        self._porn_image_index = ImagePornRecg.__image_porn_dll.Pic_InitializeModel(1)

    # @tools.log_function_time
    def image_predict(self, image_url):
        result = ImagePornRecg.__image_porn_dll.Pic_Predict(image_url, self._porn_image_index)
        return result

    def close(self):
        ImagePornRecg.__image_porn_dll.Pic_ReleaseModel(self._porn_image_index)

def main():
    image_porn_recg = ImagePornRecg()
    result = image_porn_recg.image_predict('''https://ss0.bdstatic.com/70cFuHSh_Q1YnxGkpoWK1HF6hhy/it/u=3321587425,2008241233&fm=23&gp=0.jpg''')
    image_porn_recg.close()

    print(result)

if __name__ == '__main__':
    main()

