# -*- coding: utf-8 -*-
'''
Created on 2017-07-26 19:04
---------
@summary:
---------
@author: Boris
'''


import sys
import os
sys.path.append('../')

from db.oracledb import OracleDB
import json
import utils.tools as tools
from utils.log import log
from utils.prpcrypt import Prpcrypt

db = OracleDB()

def delete_keys(keywords):
    is_delete = False
    keywords = keywords.split(',')
    for key in keywords:
        if (len(key) < 10):
            print(key if key else ',')

            if len(key) < 3:
                print('长度过小， 直接删除')
                is_delete = True
                keywords.remove(key)
            elif input("是否删除该词(n/y)") == 'y':
                is_delete = True
                keywords.remove(key)

    return is_delete, ','.join(keywords)

def format_keys(keywords):
    '''
    @summary: &表示与的关系 |表示或的关系，括号括起来表示一组
    ---------
    @param keywords:
    ---------
    @result:
    '''

    keywords = keywords.replace('（','(')
    keywords = keywords.replace('）',')')
    keywords = keywords.replace(')(',')&(')
    print(keywords)


    chinese_word = tools.get_chinese_word(keywords)
    keywords = keywords.split(',')
    for i in range(len(keywords)):
        keywords[i] = keywords[i].strip()
        # print('--------------------------')
        # print(keywords[i])
        # chinese_word = tools.get_chinese_word(keywords[i])
        regex = '[a-zA-Z 0-9:]+'
        english_words = tools.get_info(keywords[i], regex, allow_repeat = True)
        while ' ' in english_words:
            english_words.remove(' ')
        # print(english_words )
        print('=========================')
        for j in range(len(english_words)):
            english_words[j] = english_words[j].strip()
            if english_words[j]:
                keywords[i] = keywords[i].replace(english_words[j], '%s')

        keywords[i] = tools.replace_str(keywords[i], ' +', '&')
        print(keywords[i])
        print(english_words)
        keywords[i] = keywords[i]%(tuple(english_words)) if '%s' in keywords[i] else keywords[i]

    keywords = ')|('.join(keywords)
    keywords = '(' + keywords + ')' if not keywords.startswith('(') and keywords else keywords

    return keywords

def get_clues():
    sql = 'select t.id clues_id,to_char(t.keyword1),to_char(t.keyword2),to_char(t.keyword3),t.zero_id  from TAB_IOPM_CLUES t where zero_id != 7' # 7 为传播途径
    results = db.find(sql)

    clues_json = {
        "message":"查询成功",
        "status":1,
        "data":[
        {
            "clues_id":104,
            "keyword1":"",
            "keyword2":"",
            "keyword3":"",
            "zero_id":2
        }]
    }

    clues_json['data'] = []


    for result in results:
        data = {
            "clues_id":result[0] if result[0] else "",
            "keyword1":"%s"%(result[1].replace('"','“').replace('、','')[:-1] if result[1][-1] == ',' else result[1].replace('"','')) if result[1] else "",
            "keyword2":"%s"%(result[2].replace('"','“').replace('、','')[:-1] if result[2][-1] == ',' else result[2].replace('"','')) if result[2] else "",
            "keyword3":"%s"%(result[3].replace('"','“').replace('、','')[:-1] if result[3][-1] == ',' else result[3].replace('"','')) if result[3] else "",
            "zero_id":result[4] if result[4] else ""
        }

        # is_delete, keyword2 = delete_keys(result[2])
        # if is_delete:
        #     print('修改后的key->  ', keyword2)
        #     sql = "update TAB_IOPM_CLUES t set t.keyword2 = to_clob('%s') where t.id = %s"%(keyword2, result[0])
        #     if db.update(sql):
        #         print('更新数据库成功\n')


        data['keyword2'] = format_keys(data['keyword2'])
        data['keyword3'] = format_keys(data['keyword3'])
        clues_json["data"].append(data)

    return clues_json

def save_clues_to_file(clues_json_str):
    tools.write_file('clues/clues.txt', clues_json_str)
    os.system('start clues\\')


def record_sync_status(total, status, message, data, sync_type):
    delete_count = 'null'
    worn_clues_list = []
    update_count = 'null'
    save_count = 'null'

    if data:
        delete_count = data.get("deleteNum")
        worn_clues_list = data.get("wrongIdList")
        update_count = data.get("updateNum")
        save_count = data.get("saveNum")

    sql = "insert into TAB_IOPM_CLUES_SYNC_INFO (id, total, status, message, delete_count, update_count, save_count, worn_clues_list, sync_type) values (%s, %s, %s, '%s', %s, %s, %s, '%s', %s) "%('seq_iopm_sync.nextval', total, status, message, delete_count, update_count, save_count, ','.join(worn_clues_list), sync_type)

    print(sql)
    return db.add(sql)

def main():
    '''
    @summary:
    ---------
    @param :
    ---------
    @result:
    '''

    clues_json = get_clues()
    clues_count = len(clues_json['data'])

    clues_json = tools.dumps_json(clues_json)
    print(clues_json)
    # save_clues_to_file(clues_json)


    keys = 'pattek.com.cn'
    prpcrypt = Prpcrypt(keys)
    encrypt_text = prpcrypt.encrypt(clues_json)

    data = {'info':encrypt_text}

    # 同步到内网
    url = 'http://192.168.60.38:8002/datasync_al/interface/cluesConfSync?'
    json = tools.get_json_by_requests(url, data = data)
    # 记录同步行为
    result = record_sync_status(clues_count, json.get("status"), json.get('message'), json.get('data'), 0)
    print(result)
    log.debug('''
        ------ 同步线索到内网 -----
        %s
        记录到数据库 %d
        '''%(json, result))

    # 同步到外网
    url = 'http://124.205.229.232:8005/gdyq/datasync_al/interface/cluesConfSync'
    json = tools.get_json_by_requests(url, data = data)
    # 记录同步行为
    result = record_sync_status(clues_count, json.get("status"), json.get('message'), json.get('data'), 1)
    log.debug('''
        ------ 同步线索到外网 -----
        %s
        记录到数据库 %d
        '''%(json, result))

if __name__ == '__main__':
    main()
