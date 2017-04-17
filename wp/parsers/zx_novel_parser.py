import sys
sys.path.append('../../')

import init
from db.mongodb import MongoDB
import base.base_parser as base_parser
import base.constance as Constance
import utils.tools as tools
from utils.log import log

SITE_ID = 3
DATA_TYPE = 3
# 必须定义 网站名
NAME = '坐享小说'


@tools.run_safe_model(__name__)
# 必须定义 添加网站信息
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WP_site_info'
    url = 'http://www.zuox.net/'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = 'http://www.zuox.net/'
    base_parser.add_url('WP_urls', SITE_ID, url)

def parser(url_info):
    url = url_info['url']
    depth = url_info['depth']
    if depth == 4:
        return
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_urllib(url,'GBK')
    # print(html)
    links = tools.get_urls(html)
    links = tools.fit_url(links, "http://www.zuox.net/")
    for fit_url in links:
        # log.debug('url = ' + url)
        base_parser.add_url('WP_urls', SITE_ID, fit_url, depth + 1)

    if tools.re.compile('http://www.zuox.net/info').findall(url):
        soup = tools.BeautifulSoup(html, "html.parser")
        type = soup.find('div', {'class': 'txt_nav'}).find_all('a')[1].get_text()
        title = soup.find('h1').get_text()
        author = ''.join(tools.re.compile('</span>作者：<a href=".+?">(.+?)</a>').findall(str(soup)))
        look_over = ''.join(tools.re.compile('"author"><span>(\d+)点击').findall(str(soup)))
        content = soup.find('div', {'class': 'r_cons'})
        for s in content('h2'):
            s.extract()
        content = tools.del_html_tag(content.get_text())
        jpg = soup.find('div', {'class': 'con_limg'}).find('img')['src']

        log.debug('''
                          url:                   %s
                          书名:                  %s
                          作品类型:              %s
                          作者:                  %s
                          正文:                  %s
                          封面:                  %s
                          观看数:                %s
                          ''' % (
        url, title, type, author, content, jpg, look_over))

        base_parser.add_wp_content_info('WP_content_info', SITE_ID, title=title, url=url, content=content,
                                        author=author, watched_count=look_over, image_url=jpg, article_type=type,
                                        data_type=DATA_TYPE
                                        )
    base_parser.update_url('WP_urls', url, Constance.DONE)




# import execjs
#
# url = 'http://www.1kkk.com/ch65-469940-p2/'
# html = tools.get_html_by_webdirver(url)
# print(html)
# regexs = ['\d{6}']
# page_id = ''.join(tools.get_info(url, regexs))
# image_cmd_url = url+'imagefun.ashx?cid=%s&page=18&key=&maxcount=10' % page_id
# print(image_cmd_url)
# infos = tools.get_html_by_urllib(image_cmd_url)
# print(infos)
#
# print (execjs.compile(infos).call("test"))
# while(not infos):
#     infos = tools.get_html_by_urllib(image_cmd_url)
# http://manhua1031.61-174-50-99.cdndm5.com/22/21077/469940/32_2825.jpg?cid=469940&key=9536b4d7de095cbb876b3dd0eebb6631
# http://www.1kkk.com/ch65-469940-p16/imagefun.ashx?cid=469940&page=18&key=&maxcount=10
# parameter_1_regexs = ['manhua\d{3,6}']
# parameter_1 = ''.join(tools.get_info(infos, parameter_1_regexs))
# print(parameter_1)
#
# parameter_2_regexs = ['\|(\d{1,5})\|\|manhua']
# parameter_2 = ''.join(tools.get_info(infos, parameter_2_regexs))
# print(parameter_2)
#
# parameter_3_regexs = ['cdndm5\|\|(\d{1,5})\|']
# parameter_3 = ''.join(tools.get_info(infos, parameter_3_regexs))
# print(parameter_3)
#
# parameter_4_regexs = ['\|(\d{1,5})\|\d{1,5}\|com']
# parameter_4 = ''.join(tools.get_info(infos, parameter_4_regexs))
# print(parameter_4)
#
# parameter_5_regexs = ['\|\d{1,5}\|(\d{1,5})\|com']
# parameter_5 = ''.join(tools.get_info(infos, parameter_5_regexs))
# print(parameter_5)
#
# parameter_6_regexs = ['\|(\d{1,5})\|for']
# parameter_6 = ''.join(tools.get_info(infos, parameter_6_regexs))
# print(parameter_6)
#
# parameter_7_regexs = ['\|(\d{1,5})\|jpg']
# parameter_7 = ''.join(tools.get_info(infos, parameter_7_regexs))
# print(parameter_7)
#
# parameter_8_regexs = ['\|(\d{1,5})\|jpg']
# parameter_8 = ''.join(tools.get_info(infos, parameter_8_regexs))
# print(parameter_8)







