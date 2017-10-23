import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def user_main():
    key_map = {
        'id': 'int__id',
        'name': 'str_name',
        'sex': 'int_sex',
        'summary': 'str_summary',
        'fans_count': 'int_fans_count',
        'blog_verified': 'str_blog_verified',
        'is_verified': 'int_is_verified',
        'account_url': 'str_url',
        'follow_count': 'int_follow_count',
        'image_url': 'str_image_url',
        'monitor_status': 'vint_401',
        'SEARCH_TYPE' : 'vint_702',
        'region' : 'str_area',
        'monitor_type': 'int_monitor_type'
    }

    export = ExportData('WWA_weibo_user_info', 'tab_mvms_weibo_info', key_map, 'account_url')
    export.export_to_oracle()

def info_main():
    key_map = {
        'id': 'int__id',
        'release_time': 'date_release_time',
        'come_from': 'str_come_from',
        'content': 'clob_content',
        'image_url': 'str_image_url',
        'video_url': 'str_video_url',
        'transpond_count': 'int_transpond_count',
        'praise_count': 'int_praise_count',
        'check_status': 'vint_301',
        'weibo_id': 'int_weibo_id',
        'article_url': 'str_url',
        'violate_status': 'int_violate_id',
        'sensitive_id' : 'int_sensitive_id',
        'record_time' : 'date_record_time',
        'SEXY_IMAGE_STATUS':'str_sexy_image_status'
    }

    export = ExportData('WWA_weibo_info_info', 'tab_mvms_weibo_article_info', key_map, unique_key='ARTICLE_url', condition = {'read_status':0, "image_pron_status" : 2})
    export.export_to_oracle()

if __name__ == '__main__':
    while True:
        user_main()
        info_main()
        time.sleep(600)
