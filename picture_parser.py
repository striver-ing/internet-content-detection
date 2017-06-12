import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log

def spider_picture(p_url, end):
    for i in range(1,11):
        i = str(i)
        url = p_url+i+end
        html, r = tools.get_html_by_requests(url)
        regex = 'title=".*?".*?src = "(.*?)".*?<div class="wrapper-listTitle">'
        img_urls = tools.get_info(html, regex)
        regex_name = 'rseat="dsjp7".*?title="(.*?)".*?src = ".*?"'
        names = tools.get_info(html, regex_name)
        j=0
        for img_url in img_urls:
            name = names[j]
            name = tools.del_html_tag(name)
            j=j+1
            #print(img_url,'---',name,'****',j)
            FILE_LOCAL_PATH = 'd:'
            sto_path = '/picture/' + name + '.jpg'
            tools.download_file(img_url, FILE_LOCAL_PATH, sto_path)

if __name__ == '__main__':
    spider_picture('http://list.iqiyi.com/www/2/-------------11-', '-1-iqiyi--.html')
    spider_picture('http://list.iqiyi.com/www/1/-------------11-', '-1-iqiyi--.html')