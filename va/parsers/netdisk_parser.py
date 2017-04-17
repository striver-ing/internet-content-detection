import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10003
NAME = '网盘搜'
search_type = 103

HEADER = {
    'Cookie':'BAIDU_SSP_lcr=https://www.baidu.com/link?url=WUUgq8ofLooM45c49gQqo1ITVjEmpRWPB1LUz8MHuH0joAh9aZl_e80KWtoYnSa5&wd=&eqid=f315cbc900006f4200000004589bfabd; cscpvrich_fidx=1; uuid=ehabpzfr; _ga=GA1.2.1989624143.1482462347; _gat=1; Hm_lvt_311044e7f31d9fd867541074b4ba8cfd=1485148844,1486541675,1486617283; Hm_lpvt_311044e7f31d9fd867541074b4ba8cfd=1486617757',
    'Host':'www.wangpansou.cn',
    'Referer':'http://www.wangpansou.cn/s.php?wp=0&ty=gn&op=gn&q=%E7%BE%8E%E5%A5%B3&q=%E7%BE%8E%E5%A5%B3',
    'Upgrade-Insecure-Requests':1,
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
}

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'http://www.wangpansou.cn/'
    domain = 'wangpansou.cn'
    ip = '122.114.91.8'
    address = '中国 河南 郑州 电信/联通'
    icp = '15001638'
    base_parser.add_website_info(table, site_id, url, name, domain, ip, address,icp=icp)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))


    search_keyword1 = parser_params['search_keyword1']
    search_keyword2 = parser_params['search_keyword2']
    search_keyword3 = parser_params['search_keyword3']

    remark = parser_params

    search_keywords = []
    for str_key1 in search_keyword1:
        for str_key2 in search_keyword2:
            search_keywords.append((str_key1 + str_key2).strip())
    else:
        if not search_keyword1:
            search_keywords = search_keyword2
        if not search_keyword2:
            search_keywords = search_keyword1

    for j in search_keywords:
        if not j.strip():
            continue
        for i in range(0, 91, 10):
            url = 'http://www.wangpansou.cn/s.php?q=%s&wp=0&start=%d' % (j, i)
            if not base_parser.add_url('VA_urls', SITE_ID, url, remark=remark):
                base_parser.update_url('VA_urls', url, Constance.TODO)

# @tools.run_safe_model(__name__) # 移到parser_control
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html, requests = tools.get_html_by_requests(root_url, headers = HEADER)
    titles = tools.get_tag(html, 'div', {'id': tools.re.compile('id_cse_content_item_mid_.')})

    for i in range(0, len(titles)):
        try:
            url = tools.get_tag(titles[i].previous_sibling.previous_sibling, 'a', find_all=False)
            url = url['href']

            html2 = tools.get_html_by_urllib(url)
            regexs = ['<title>(.+?)</title>']
            mark = ''.join(tools.get_info(html2, regexs))
            regexs = ['不存在', '取消']
            if not tools.get_info(mark, regexs):
                title = tools.get_text(titles[i].previous_sibling.previous_sibling)
                title = tools.del_html_tag(title)
                info = tools.get_text(titles[i])

                file_name = tools.del_html_tag(''.join(tools.get_info(info, '文件名:(.+?)文')))

                file_size = tools.del_html_tag(''.join(tools.get_info(info, '文件大小:(.+?)分')))

                author = tools.del_html_tag(''.join(tools.get_info(info, '分享者:(.+?)时')))

                release_time = ''.join(tools.get_info(info, '时间:(.+?)下')).replace('\n', '')

                download_count = tools.del_html_tag(''.join(tools.get_info(info, '下载次数:(.+?)\.')))

        except:
            continue

            log.debug('''
                标题：    %s
                文件大小：%s
                文件名字：%s
                作者：    %s
                原文url： %s
                下载数量：%s
                日期：    %s
                   ''' % (title, file_size, file_name, author, url, download_count, release_time))

            contained_key, contained_key_count = base_parser.get_contained_key(title, '',
                                                                remark['search_keyword1'],
                                                                remark['search_keyword2'], remark['search_keyword3'])
            if not contained_key:
                continue

            base_parser.add_content_info('VA_content_info', SITE_ID, url, title, file_size = file_size,
                                         file_name = file_name, author = author, release_time = release_time,
                                         download_count = download_count, search_type = search_type,
                                         keyword = contained_key, keyword_count = contained_key_count, task_id = remark['task_id'])
    base_parser.update_url('VA_urls', root_url, Constance.DONE)
