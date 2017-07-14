# -*- coding: utf-8 -*-
'''
Created on 2017-07-07 14:02
---------
@summary: 对ffmpeg封装,需要将ffmpeg.exe拷贝到Python安装目录下
---------
@author: Boris
'''
import os

# def convert_file_format(input_file, output_file, delete_input_file = False):
#     '''
#     @summary: 转码，需要将ffmpeg.exe拷贝到Python安装目录下
#     ---------
#     @param input_file:
#     @param output_file:
#     ---------
#     @result:
#     '''

#     is_exception = os.system('ffmpeg -i %s %s'%(input_file, output_file))

#     is_success = not is_exception
#     if is_success and delete_input_file:
#         os.remove(input_file)

#     return is_success

test = '''
z0522rnfto7-qq
养鸡参赛只为得到老爸认可 好友曾劝其改行
薛之谦 和戚薇深情合唱《为了遇见你》“为了遇见你
青海湖经幡塔挂满了藏族人民的祈祷，风每吹一遍，相当于念诵经文一遍。藏族人民对湖水的崇拜，源自他们相信万物有灵，相信青海湖吹来的风，会将他们的祈祷，带到世界的每一个角落。
北大校友葛兆光寄语毕业生：放下精英的傲慢，但别丢弃精英的意识
v1319drel9z-qq
古力娜扎为郑爽新电影造势宣传？网友：这又不是两人第一次同框了
直播连线：长江水位上涨致铜陵大通澜溪老街被淹
辽宁舰赴港首开放  抢票热“点燃”盛夏
我国最大页岩气田探明储量超6000亿方
蠢萌鸭子追主人，刚开始还是用两只腿追，但是主人越跑越快
东莞：男子伤害工友  已被警方制服
20170705《焦点访谈》：守护住那微弱的光亮
p1320z5wac2-qq
'''

test= test.strip()
print(test.replace('<br>', '       '))


14:02
14:02
14:02

