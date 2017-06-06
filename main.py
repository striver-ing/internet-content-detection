# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 13:35
---------
@summary: 程序入口
---------
@author: Boris
'''
import init
import threading

import wwa.app_export_data
import wwa.app_main

import wwa.export_search_app_data
import wwa.search_app_main

import wwa.wechat_account_main
import wwa.wechat_article_main
import wwa.wechat_export_data

import wwa.weibo_export_date
import wwa.weibo_info_main
import wwa.weibo_user_main

def run(thread):
    threading.Thread(target = thread).start()

def main():
    run(wwa.app_export_data.main)
    run(wwa.app_main.main)

    run(wwa.export_search_app_data.main)
    run(wwa.search_app_main.main)

    run(wwa.wechat_account_main.main)
    run(wwa.wechat_article_main.main)
    run(wwa.wechat_export_data.main)

    run(wwa.weibo_export_date.main)
    run(wwa.weibo_info_main.main)
    run(wwa.weibo_user_main.main)



if __name__ == '__main__':
    main()