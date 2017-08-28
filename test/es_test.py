# -*- coding: utf-8 -*-
'''
Created on 2017-07-29 12:29
---------
@summary:
---------
@author: Boris
'''
import sys
sys.path.append('../')
import init
import utils.tools as tools
from elasticsearch import Elasticsearch
from datetime import datetime


# es = Elasticsearch("127.0.0.1:9200")
es = Elasticsearch([{'host':'127.0.0.1','port':9200}])
print(es)

#创建索引，索引的名字是my-index,如果已经存在了，就返回个400，
#这个索引可以现在创建，也可以在后面插入数据的时候再临时创建
#{u'acknowledged':True}
#插入数据,(这里省略插入其他两条数据，后面用)
es.index(index="my-index",doc_type="test-type",id=12, body={"any":"data01","timestamp":datetime.now()})
#{u'_type':u'test-type',u'created':True,u'_shards':{u'successful':1,u'failed':0,u'total':2},u'_version':1,u'_index':u'my-index',u'_id':u'1}
#也可以，在插入数据的时候再创建索引test-index
es.index(index="test-index",doc_type="test-type",id=42,body={"any":"data","timestamp":datetime.now()})
es.index(index="test-index",doc_type="test-type",id=43,body={"any":"data","timestamp":datetime.now()})
es.index(index="test-index",doc_type="test-type",id=44,body={"any":"data","timestamp":datetime.now()})
es.index(index="test-index",doc_type="test-type",id=46,body={"haha":"haha","timestamp":datetime.now()})


#查询数据，两种get and search
#get获取
res = es.get(index="my-index", doc_type="test-type", id=1)
# print(res)
#{u'_type': u'test-type', u'_source': {u'timestamp': u'2016-01-20T10:53:36.997000', u'any': u'data01'}, u'_index': u'my-index', u'_version': 1, u'found': True, u'_id': u'1'}
# print(res['_source'])
#{u'timestamp': u'2016-01-20T10:53:36.997000', u'any': u'data01'}

#search获取
res = es.search(index="test-index", body={"query":{"match_all":{}}})
print(res)
#{u'hits':
#    {
#    u'hits': [
#        {u'_score': 1.0, u'_type': u'test-type', u'_id': u'2', u'_source': {u'timestamp': u'2016-01-20T10:53:58.562000', u'any': u'data02'}, u'_index': u'my-index'},
#        {u'_score': 1.0, u'_type': u'test-type', u'_id': u'1', u'_source': {u'timestamp': u'2016-01-20T10:53:36.997000', u'any': u'data01'}, u'_index': u'my-index'},
#        {u'_score': 1.0, u'_type': u'test-type', u'_id': u'3', u'_source': {u'timestamp': u'2016-01-20T11:09:19.403000', u'any': u'data033'}, u'_index': u'my-index'}
#    ],
#    u'total': 5,
#    u'max_score': 1.0
#    },
#u'_shards': {u'successful': 5, u'failed': 0, u'total':5},
#u'took': 1,
#u'timed_out': False
#}
for hit in res['hits']['hits']:
    print(hit["_source"])
res = es.search(index="test-index", body={'query':{'match':{'any':'data'}}}) #获取any=data的所有值
print(res)