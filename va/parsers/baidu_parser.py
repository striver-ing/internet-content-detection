import sys
sys.path.append('../../')
import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log

SITE_ID = 10001
NAME = '百度'
search_type = 101

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'VA_site_info'
    url = 'http://www.baidu.com'
    domain = 'baidu.com'
    ip = '111.13.100.91'
    address = '北京市'
    public_safety = '11000002000001'
    icp = '030173'
    base_parser.add_website_info(table, site_id, url, name,domain,ip,address,public_safety=public_safety,icp=icp)


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

    for i in search_keywords:
        # print(i)
        if not i.strip():
            continue
        for num in range(0, 760, 10):
            link = "https://www.baidu.com/s?wd=%s%s&pn=%d" % (i,' 视频', num)
            # print(link)
            link = tools.quote(link, safe='#/:?=&%')
            if not base_parser.add_url('VA_urls', SITE_ID, link, remark=remark):
                base_parser.update_url('VA_urls', link, Constance.TODO)

# @tools.run_safe_model(__name__) # 移到parser_control
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html = tools.get_html_by_webdirver(root_url)
    headers = tools.get_tag(html,'h3', {'class': 't'})

    for i in range(0, len(headers)):
        title = tools.get_text(headers[i])
        title = tools.del_html_tag(title)
        if tools.re.compile('的相关视频在线观看_百度视频').findall(title):
            continue

        try:
            ssurl = headers[i].a["href"]
        except:
            continue
        r = tools.requests.head(ssurl)
        url = r.headers['Location']

        try:
            img = headers[i].next_sibling()[0].img['src']
        except:
            img = ''

        # if not img:
        #     continue

        try:
            release_time = headers[i].next_sibling()[0]
            release_time = tools.re.compile('\d\d\d\d年\d+?月\d+?日').findall(str(release_time))
            if not release_time:
                release_time = headers[i].next_sibling()[1]
                release_time = tools.re.compile('\d\d\d\d年\d+?月\d+?日').findall(str(release_time))
                if not release_time:
                    release_time = headers[i].next_sibling()[2]
                    release_time = tools.re.compile('\d\d\d\d年\d+?月\d+?日').findall(str(release_time))
                    if not release_time:
                        release_time = headers[i].next_sibling()[3]
                        release_time = tools.re.compile('\d\d\d\d年\d+?月\d+?日').findall(str(release_time))
            release_time = release_time[0]
            release_time = release_time.replace('年','-').replace('月','-').replace('日','')
        except:
            release_time = ''

        content = ''
        for content in headers[i].next_sibling():
            content = tools.get_tag(content,'div',{'class': 'c-abstract'},find_all=False)
            if content:
                content = tools.get_text(content)
                break
            else:
                content = ''

        log.debug('''
            标题：   %s
            内容：   %s
            原文url：%s
            图片url：%s
            日期：   %s
               ''' % (title, content , url, img, release_time))


        contained_key, contained_key_count = base_parser.get_contained_key(title,content,remark['search_keyword1'],
                                               remark['search_keyword2'],remark['search_keyword3'])
        if not contained_key:
            continue

        is_video1 = base_parser.is_have_video_by_site(url)
        if not is_video1:
            is_video2 = base_parser.is_have_video_by_judge(title, content)
            if is_video2:
                html2 = tools.get_html_by_requests(url)
                is_video3 = base_parser.is_have_video_by_common(html2)
                if not is_video3:
                    continue
            else:
                continue

        base_parser.add_content_info('VA_content_info', SITE_ID, url = url, title = title, content = content,
                                     image_url = img, release_time = release_time, search_type = search_type,
                                     keyword = contained_key, keyword_count = contained_key_count, task_id = remark['task_id'])
    base_parser.update_url('VA_urls', root_url, Constance.DONE)
