# -*- coding: utf-8 -*-
'''
Created on 2017-03-27 17:58
---------
@summary: 文本分词
---------
@author: Boris
'''

# import utils.tools as tools
import jieba
import jieba.analyse
import jieba.posseg as pseg
import os

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd(), path))

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls, *args, **kwargs)

        return cls._inst

class CutText(Singleton):
    def __init__(self, dict_path = ''):
        super(Singleton, self).__init__()
        if not hasattr(self,'_stop_words'):
            #导入自定义词典
            if dict_path:
                jieba.load_userdict(dict_path)

            self._stop_words = set((
                '', ' ', '\n', "the", "of", "is", "and", "to", "in", "that", "we", "for", "an", "are",
                "by", "be", "as", "on", "with", "can", "if", "from", "which", "you", "it",
                "this", "then", "at", "have", "all", "not", "one", "has", "or", "that"
            ))

    def set_stop_words(self, stop_words_path):
        '''
        @summary: 设置停用词
        ---------
        @param stop_words_path: 停用词文件路径
        ---------
        @result:
        '''

        abs_path = _get_abs_path(stop_words_path)
        if not os.path.isfile(abs_path):
            raise Exception("jieba: file does not exist: " + abs_path)

        content = open(abs_path, 'rb').read().decode('utf-8')
        for line in content.splitlines():
            self._stop_words.add(line)

        jieba.analyse.set_stop_words(stop_words_path) # analyse模块自带停用词设置

    def __del_stop_key(self, word_list):
        '''
        @summary: 删除停用字
        ---------
        @param word_list: 分词列表
        ---------
        @result: 返回删除停用词后的列表
        '''

        words = []
        for word in word_list:
            if word not in self._stop_words:
                words.append(word)

        return words

    def cut(self, text, cut_all = False):
        '''
        @summary: 分词
        ---------
        @param text: 文本
        @param cut_all: True 全模式 False 精准模式
          精确模式，试图将句子最精确地切开，适合文本分析；
          全模式，把句子中所有的可以成词的词语都扫描出来, 速度非常快，但是不能解决歧义；
        ---------
        @result:
        '''
        result = list(jieba.cut(text, cut_all = cut_all))
        result = self.__del_stop_key(result)
        return result

    def cut_for_search(self, text):
        '''
        @summary: 搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词；
        ---------
        @param text: 文本
        ---------
        @result:
        '''
        result = list(jieba.cut_for_search(text))
        result = self.__del_stop_key(result)
        return result

    def cut_for_keyword(self, text, with_weight = False, top_keyword_count = None):
        '''
        @summary: 取关键词
        ---------
        @param text: 切分文本
        @param with_weight: 是否返回权重 返回格式（keyword, word_weight）
        @param top_keyword_count: 保留前N个关键字 None是保留所有
        ---------
        @result:
        '''
        result = jieba.analyse.extract_tags(text, topK = top_keyword_count, withWeight = with_weight)
        return result

    def cut_for_property(self, text):
        '''
        @summary: 获取分词属性
        ---------
        @param text: 分词文本
        ---------
        @result: 返回[(text1, property1)...(textN, propertyN)]
        '''
        words_list = []

        words =pseg.cut(text)
        for word in words:
            if word.word not in self._stop_words:
                words_list.append((word.word, word.flag))

        return words_list






if __name__ == '__main__':

    text = '''
    原标题：习近平三番两次同密克罗尼西亚联邦总统克里斯琴举行会谈
    '''

    cut_text = CutText()
    cut_text.set_stop_words('stop_word.txt')
    print(cut_text.cut(text))
    print(cut_text.cut(text, True))
    print(cut_text.cut_for_search(text))
    print(cut_text.cut_for_property(text))
    print(cut_text.cut_for_keyword(text))

