# -*- coding: utf-8 -*-
'''
Created on 2017-07-26 19:04
---------
@summary:
---------
@author: Boris
'''


import sys
sys.path.append('../')

from db.oracledb import OracleDB
import utils.tools as tools

oracledb = OracleDB()

def main():
    url = 'http://192.168.60.38:8001/hotspot_al/interface/getHotAnalysis_self'
    json = tools.get_json_by_requests(url)
    # print(json)

    hot_list = []
    datas = json['data']
    for data in datas:
        clus_id = list(data.keys())[0]
        sql = 'select t.name from TAB_IOPM_CLUES t where id = ' + clus_id
        name = oracledb.find(sql)[0][0]

        hot_infos = data[clus_id]['data']
        for hot_info in hot_infos:
            kw = hot_info['kw']
            hot = hot_info['hot']
            # print(name, kw, hot)
            hot_list.append({'name':name, 'kw':kw, 'hot':hot, 'clus_id':clus_id})

    hot_list.sort(key=lambda obj:obj.get('hot'), reverse=True)

    for hot_info in hot_list:
        print(hot_info['name'], hot_info['clus_id'], '--->', hot_info['kw'], hot_info['hot'])


if __name__ == '__main__':
    main()