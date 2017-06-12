import sys
sys.path.append('../../')

import base.base_parser as base_parser
import init
import utils.tools as tools
from utils.log import log
import re

def spider_picture(p_url, end):
    for i in range(1,7):
        i = str(i)
        url = p_url+i+end
        #print(url)
        html, r = tools.get_html_by_requests(url)
        #print(html)
        regex = '<a class="figure.*?<img.*?src="(.*?)"/>'
        img_urls = tools.get_info(html, regex)

        regex_name = 'data-widget-searchlist-tvname="(.*?)"'
        names = tools.get_info(html, regex_name)
        j=0
        for img_url in img_urls:
            name = names[j]
            name = tools.del_html_tag(name)
            j=j+1
            # if not re.match(".jpg", img_url):
            #     img_url = img_url+'.jpg'
            #print(img_url,'---',name,'****',j)
            FILE_LOCAL_PATH = 'd:'
            sto_path = '/ViolatePicture/' + name + '.jpg'
            tools.download_file(img_url, FILE_LOCAL_PATH, sto_path)

if __name__ == '__main__':
    spider_picture('http://so.iqiyi.com/so/q_韩国色情妇电影_ctg__t_0_page_', '_p_1_qc_0_rd__site__m_1_bitrate_')
