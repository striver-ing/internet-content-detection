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

# def format_keys(keywords):
#     '''
#     @summary: &表示与的关系 |表示或的关系，括号括起来表示一组如：(好先生&孙红雷)|(江疏影&好先生)
#     ---------
#     @param keywords:
#     ---------
#     @result:
#     '''

#     chinese_word = tools.get_chinese_word(keywords)
#     keywords = keywords.split(',')
#     for i in range(len(keywords)):
#         keywords[i] = keywords[i].strip()
#         keys = ''

#         per_word_is_chinese = False
#         for key in keywords[i].split(' '):
#             keys += key

#             if tools.is_have_chinese(key[-1:]):
#                 keys += '&'
#             else:
#                 keys += ' '

#         keywords[i] = keys[:-1]

#     keywords = ')|('.join(keywords)
#     keywords = '(' + keywords + ')' if not keywords.startswith('(') and keywords else keywords

#     return keywords

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
        keys = ''

        chinese_word = tools.get_chinese_word(keywords[i])
        english_words = tools.get_english_words(keywords[i])

        keys += '&'.join(chinese_word) + '&' + ' '.join(english_words)

        keywords[i] =  keys[:-1] if keys.endswith('&') else keys
        keywords[i] =  keywords[i][1:] if keywords[i].startswith('&') else keywords[i]

    keywords = ')|('.join(keywords)
    keywords = '(' + keywords + ')' if not keywords.startswith('(') and keywords else keywords

    return keywords

def main():
    '''
    @summary:
    ---------
    @param :
    ---------
    @result:
    '''
    db = OracleDB()
    sql = 'select t.id clues_id,to_char(t.keyword1),to_char(t.keyword2),to_char(t.keyword3),t.zero_id  from TAB_IOPM_CLUES t where zero_id != 7' # 7 为传播途径
    results = db.find(sql)

    keys_count = 0

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

        keys_count += len(result[2].split(','))


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

    tools.write_file('clues/clues.txt', clues_json)
    os.system('start clues\\')

    print(keys_count)

if __name__ == '__main__':
    main()