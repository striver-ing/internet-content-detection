# -*- coding: utf-8 -*-
'''
Created on 2017-03-27 17:58
---------
@summary: 文本分词
---------
@author: Boris
'''
import sys
sys.path.append("..")
import utils.tools as tools
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
    央视网消息(新闻联播)：6月7日至10日，国家主席习近平应邀对哈萨克斯坦进行国事访问并出席上海合作组织成员国元首理事会第十七次会议和阿斯塔纳专项世博会开幕式。在行程结束之际，外交部长王毅向记者介绍此访取得丰硕成果。
这次访问是习近平主席主持“一带一路”国际合作高峰论坛后首次出访，也是中国面向欧亚地区的一次重大外交行动。
一、推动中哈关系迈上新台阶
访哈期间，习近平主席同纳扎尔巴耶夫总统一道全面规划两国合作，推动中哈关系“百尺竿头、更进一步”。
政治互信空前提升。两国元首就深化中哈全面战略伙伴关系达成重要共识，共同签署《中哈联合声明》，为两国关系下步发展指明方向、规划蓝图。双方同意继续相互政治支持，尊重对方发展道路和内外政策，维护彼此核心利益，在重大国际地区问题上保持密切沟通，在多边机制框架内加强协调配合。
发展战略加快对接。双方商定重点做好四方面对接：一是实现新亚欧大陆桥、中国－中亚－西亚经济走廊建设同哈萨克斯坦打造国际物流大通道战略对接；二是推动国际产能合作同哈萨克斯坦加快工业化进程对接；三是完成中国陆海联运优势同哈萨克斯坦东向海运需求对接；四是推进“数字丝绸之路”倡议同“数字哈萨克斯坦”战略对接。
友好合作全面推进。两国签署10多项政府部门间合作协议，涉及经贸、金融、基础设施建设、水利、质检、媒体等诸多领域。双方同意加强人文和地方合作。双方同意深化打击“三股势力”及跨国有组织犯罪等合作，共同应对威胁地区安全和稳定的挑战。
二、引领上合组织实现新发展
习近平主席同各国领导人就上合组织重大事项及国际和地区问题深入交换意见，贡献中国智慧、提出中国倡议、展现中国担当。
增强了上合组织成员的凝聚力。本次峰会正式接收印度、巴基斯坦为成员国，上合组织完成首次扩员。习近平主席指出，要不忘初心，继续弘扬“上海精神”；要与时俱进，开创地区合作新局面。呼吁新老成员保持团结协作的良好传统，构筑平等相待、守望相助、休戚与共、安危共担的命运共同体。这些重要主张将推动上合组织保持健康稳定发展。
指明了上合组织发展的大方向。习近平主席在会上宣布中国将于明年6月在华举办下次峰会，阐释中方接任轮值主席国的工作思路，明确上合组织下步发展的基本理念。各方普遍认为，习近平主席的思路和构想紧扣形势变化，契合各方需求，聚焦互利共赢，将带动上合组织实现新一轮发展，开创地区合作新气象。
提出了上合组织合作的新倡议。习近平主席就上合组织在政治、安全、经济、人文、对外交往、机制建设等领域合作提出一系列具体倡议，将推动上合组织朝着协调更全面、合作更务实、行动更高效的方向发展。
各成员国领导人共同签署、发表《阿斯塔纳宣言》和《新闻公报》等文件，充分吸纳了中方的主张和倡议。还签署《上海合作组织反极端主义公约》，完善了打击“三股势力”的法律基础。
峰会期间，习近平主席同俄罗斯总统普京举行会晤，两国元首同意继续加大相互支持，密切在国际和地区事务中的协调配合。习近平主席分别会晤阿富汗总统加尼和印度总理莫迪，就稳定中印关系，支持阿富汗和平进程达成重要共识。
习近平主席还分别会见塔吉克斯坦、西班牙、土库曼斯坦等国领导人。
三、谱写“一带一路”建设新篇章
高峰论坛共识得到有力弘扬。习近平主席此访将丝路精神与双多边会晤会议成果有机结合，弘扬共商、共建、共享原则，全方位推动政策沟通、设施联通、贸易畅通、资金融通、民心相通，为将“一带一路”建设成和平、繁荣、开放、创新、文明之路提供有力支撑。
发展战略对接得到有力推进。习近平主席此访推动中哈在共建“一带一路”和国际产能合作中发挥好示范作用。习近平主席强调中方将继续推进“一带一路”建设同各成员国发展战略和其他地区一体化倡议对接合作，上合组织将为此发挥平台作用。
“一带一路”倡议得到有力支持。中哈两国发表的《联合声明》及上合组织发表的《阿斯塔纳宣言》等文件均充分肯定“一带一路”的积极意义，高度评价并支持落实高峰论坛成果。各国领导人表示愿继续积极响应和参与“一带一路”建设。通过习近平主席这次访问，我们再次深刻感受到，“一带一路”倡议已成为广受欢迎的国际公共产品，使各国抓到合作机遇，看到发展希望。国际上认同“一带一路”的共识越来越多，预期越来越乐观。
    '''
    text = '支持'
    # 1.7482669353485107
    cut_text = CutText()
    # cut_text.set_stop_words('stop_word.txt')
    import time
    b = time.time()
    print(cut_text.cut(text))
    print(time.time() - b)
    # print(cut_text.cut(text, True))
    # print(cut_text.cut_for_search(text))
    # print(cut_text.cut_for_property(text))
    # print(cut_text.cut_for_keyword(text))

