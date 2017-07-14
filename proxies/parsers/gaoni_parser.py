import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance

# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '高匿代理'

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'proxies_site_info'
    url = 'http://www.xicidaili.com'

    base_parser.add_website_info(table, site_id, url, name)


# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    url = 'http://www.xicidaili.com/nn/'
    base_parser.add_url('proxies_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    headers = {
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.xicidaili.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "If-None-Match": "W/\"23123ab646b5add95fb54a129f83fc3e\"",
        "Cache-Control": "max-age=0",
        "Referer": "http://www.xicidaili.com/api",
        "Cookie": "_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTllZTE5YzdmMzE3MTkyMjYzZWQ5YzY0ZTE5N2UyYjdlBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMXFDNERvYllMb3V2VUFWdk54RnYwbHF5VTRQdktjYnRYdUd6VTVDZjlicXM9BjsARg%3D%3D--25d29e9705eb048a4382f6ab20f130ea054a8cec; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1499054099; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1499054536"
    }

    # 解析
    html, request = tools.get_html_by_requests(root_url, headers = headers)
    if not html:
        base_parser.update_url('proxies_urls', root_url, Constance.EXCEPTION)

    regex = '<tr class=.*?>(.*?)</tr>'
    datas = tools.get_info(html, regex)
    for data in datas:
        regex = '<td.*?>(.*?)</td>'
        data =  tools.get_info(data, regex)

        ip = data[1]
        port = data[2]
        anonymous_type = data[4]   #匿名方式
        connect_type = data[5]
        speed = tools.get_info(data[6], 'div title="(.*?)"', fetch_one = True)
        alive_length = data[8]

        log.debug('''
            ip :            %s
            port:           %s
            connect_type:   %s
            anonymous_type  %s
            speed           %s
            alive_length    %s
            '''%(ip, port, connect_type, anonymous_type, speed, alive_length))

        base_parser.add_proxies_info('proxies_content_info', site_id, ip, port, connect_type, anonymous_type, speed, alive_length)

    base_parser.update_url('proxies_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    pass