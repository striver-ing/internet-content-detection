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
from utils.prpcrypt import Prpcrypt

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

    chinese_word = tools.get_chinese_word(keywords)
    keywords = keywords.split(',')
    for i in range(len(keywords)):
        keywords[i] = keywords[i].strip()
        # print('--------------------------')
        # print(keywords[i])
        # chinese_word = tools.get_chinese_word(keywords[i])
        regex = '[a-zA-Z 0-9:]+'
        english_words = tools.get_info(keywords[i], regex)
        if ' ' in english_words:
            english_words.remove(' ')
        # print(english_words )
        # print('=========================')
        for j in range(len(english_words)):
            english_words[j] = english_words[j].strip()
            if english_words[j]:
                keywords[i] = keywords[i].replace(english_words[j], '%s')

        keywords[i] = tools.replace_str(keywords[i], ' +', '&')
        # print(keywords[i])
        # print(english_words)
        keywords[i] = keywords[i]%(tuple(english_words)) if '%s' in keywords[i] else keywords[i]

    keywords = ')|('.join(keywords)
    keywords = '(' + keywords + ')' if not keywords.startswith('(') and keywords else keywords

    return keywords

def get_clues():
    db = OracleDB()
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
    clues_json = tools.dumps_json(clues_json)
    print(clues_json)

    # tools.write_file('clues/clues.txt', clues_json)
    # os.system('start clues\\')

    return clues_json

def main():
    '''
    @summary:
    ---------
    @param :
    ---------
    @result:
    '''

    clues_json = get_clues()
    clues_json = tools.dumps_json(clues_json)


    keys = 'pattek.com.cn'
    prpcrypt = Prpcrypt(keys)
    encrypt_text = prpcrypt.encrypt(clues_json)

    # encrypt_text = '1ccdb60052d4aeb2aa924a98f6e38ec7f5e35dd6fcb456b4af24ef195ca12efe12638a657c389128dbf7e694aa5e4874f701f251ed6b5d2b8bb0b295960b68b4c70cc22bcf83a469c78bfd8fe71b4eac92145e74a9ecf232b63f6f8f75a8f914072867c6a7837854ee3d85224ba2cb32a812241a091af2ed2cbde8d477432303f91c7e9b7b114c7f42e12bfb36fe489ce88fb03a387a4168c72ca416551e7529499bc4f98bc96a58d24e847bd4136a2c6b6a2a3816395c9187e02db7349e66f26ae8ed9fd21ce045d150158cc87d4e7d8f73c2ad18868410321e5d53a2a1e1b9015f55ff6b514046365e377ed6511ef0d3d268300f822f2d3b9328c2ed7f4c0a7b81dff1ffa73e54f22211ecb41f3b7a0b7e82fec63e4e701f3ba185603996a899e6b7d559bd057018ae8e3d7ed2c2c1e554de6b92e791e66862adf947c4d2254a4f61164c3092080315deb4b52737305a03614fdb2cb313107520ac79dc338e'
    print(encrypt_text)
    tools.write_file('encrypt_text.txt', encrypt_text)

    # url = 'http://192.168.60.38:8002/datasync_al/interface/cluesConfSync?'
    # data = {'info':encrypt_text}
    # # print(data)
    # # print(len(encrypt_text))
    # json = tools.get_json_by_requests(url, data = data)
    # print(json)

if __name__ == '__main__':
    main()
    # keys = '“7-3” 事件,六.四事件'
    # keys = format_keys(keys)
    # print(keys)