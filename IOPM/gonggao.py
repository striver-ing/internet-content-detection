import requests
import pymongo
from bs4 import BeautifulSoup
import sys
sys.path.append('../')
import utils.tools as tools
from utils.export_data import ExportData

client = pymongo.MongoClient("localhost",27017)
db = client.gonggao

if __name__ == '__main__':
    db.gonggao_content.ensure_index('url', unique=True)
    export_data = ExportData()

    urls = ['http://www.sapprft.gov.cn/sapprft/channels/6588.shtml', 'http://www.sapprft.gov.cn/sapprft/channels/6588_2.shtml',
    'http://www.sapprft.gov.cn/sapprft/channels/6588_3.shtml', 'http://www.sapprft.gov.cn/sapprft/channels/6588_4.shtml',
    'http://www.sapprft.gov.cn/sapprft/channels/6588_5.shtml']

    count = 0

    for url in urls:
        html, res = tools.get_html_by_requests(url)

        links = tools.get_tag(html, 'a', {'class': 'fl'})
        release_times = tools.get_tag(html, 'span', {'class': 'fr'})

        for link_num in range(len(links)):
            title = links[link_num].get_text()
            link = links[link_num]['href']
            link = 'http://www.sapprft.gov.cn' + link
            release_time = release_times[link_num].get_text()
            link_html, res = tools.get_html_by_requests(link)
            content = tools.get_tag(link_html, 'div', {'id': 'artibody'}, find_all=False)
            content = content.get_text()

            content_info = {'title': title, 'url': link, 'release_time': release_time, 'content': content}

            print(link+ '    '+ release_time)

            key_map = {
                'id':'vint_sequence.nextval',
                'title':'str_title',
                'content':'clob_content',
                'url':'str_url',
                'release_time':'date_release_time'
            }

            def export_callback(execute_type, sql):
                if execute_type == ExportData.EXCEPTION:
                    print('共导出 %s 条公告'%count)
                    exit()

            count += export_data.export_to_oracle(key_map = key_map, aim_table = 'TAB_IOPM_notice', unique_key = 'url', datas = content_info, callback = export_callback)


    print('共导出 %s 条公告'%count)