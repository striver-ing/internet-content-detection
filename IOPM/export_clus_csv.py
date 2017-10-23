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
    sql = 'select t.id clues_id,to_char(t.keyword2),to_char(t.keyword3),t.name  from TAB_IOPM_CLUES t where zero_id != 7' # 7 为传播途径
    results = db.find(sql)

    clues_json = {
        "message":"查询成功",
        "status":1,
        "data":[
        {
            "clues_id":104,
            "包含":"",
            "不包含":"",
            "线索":2
        }]
    }

    clues_json['data'] = []

    file = open('clues/clues.csv', 'w+',  encoding='utf8')
    file.write("线索,关键词\n")

    for result in results:
        print(result)
        data = {
            "线索id":result[0] if result[0] else "",
            "包含":"%s"%(result[1].replace('"','“').replace('、','')[:-1] if result[1][-1] == ',' else result[1].replace('"','')) if result[1] else "",
            "不包含":"%s"%(result[2].replace('"','“').replace('、','')[:-1] if result[2][-1] == ',' else result[2].replace('"','')) if result[2] else "",
            "线索":result[3] if result[3] else ""
        }

        # is_delete, keyword2 = delete_keys(result[2])
        # if is_delete:
        #     print('修改后的key->  ', keyword2)
        #     sql = "update TAB_IOPM_CLUES t set t.keyword2 = to_clob('%s') where t.id = %s"%(keyword2, result[0])
        #     if db.update(sql):
        #         print('更新数据库成功\n')

        print(data)
        # data['keyword2'] = format_keys(data['keyword2'])
        # data['keyword3'] = format_keys(data['keyword3'])
        clues_json["data"].append(data)
        file.write('"%s","%s"\n'%(data['线索'], data['包含']))

    file.close()
    # clues_json = tools.dumps_json(clues_json)
    # print(clues_json)

    # tools.write_file('clues/clues.txt', clues_json)
    os.system('start clues\\')

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


    # keys = 'pattek.com.cn'
    # prpcrypt = Prpcrypt(keys)
    # encrypt_text = prpcrypt.encrypt(clues_json)

    # print(encrypt_text)
    # tools.write_file('encrypt_text.txt', encrypt_text)

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