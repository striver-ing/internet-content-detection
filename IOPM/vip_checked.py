# -*- coding: utf-8 -*-
'''
Created on 2017-08-09 15:44
---------
@summary: 判断是不是主流媒体
---------
@author: Boris
'''
import sys
sys.path.append('../')
import utils.tools as tools
from utils.log import log
from db.oracledb import OracleDB

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls, *args, **kwargs)

        return cls._inst

class VipChecked(Singleton):
    def __init__(self):
        super(VipChecked, self).__init__()
        if not hasattr(self,'_vip_sites'):
            self._vip_sites = set()

            self._oracledb = OracleDB()

            self.load_vip_site()

    def load_vip_site(self):
        sql = 'select to_char(t.keyword2) from TAB_IOPM_CLUES t where zero_id = 7'
        sites = self._oracledb.find(sql)
        for site in sites:
            site_list = site[0].split(',')
            for site in site_list:
                if site:
                    self._vip_sites.add(site)

        # print(self._vip_sites)

    def is_vip(self, url = '', name = ''):
        is_vip = False
        for site in self._vip_sites:
            if url:
                is_vip = site in url

            elif name:
                is_vip = name in site

            if is_vip:
                break

        return is_vip

if __name__ == '__main__':
    vip_checked = VipChecked()
    is_vip = vip_checked.is_vip(name = '光明日报')
    print(is_vip)