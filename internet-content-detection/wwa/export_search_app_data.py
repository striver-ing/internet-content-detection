import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    # 导出数据
    key_map = {
        'id' : 'int__id',
        'title' : 'str_title',
        'update_info' : 'str_update_info',
        'author' : 'str_author',
        'url' : 'str_url',
        'app_url' : 'str_app_url',
        'image_url' : 'str_image_url',
        'software_size' : 'str_software_size',
        'tag' : 'str_tag',
        'platform_type' : 'vint_502', #android
        'download_count' : 'str_download_count',
        'record_time' : 'date_record_time',
        'update_time' : 'date_release_time',
        'site_id' : 'int_site_id',
        'score' : 'str_score',
        'summary' : 'str_summary',
        'compatibility' : 'str_platform',
        'language' : 'int_language',
        'monitor_status' : 'vint_401'
    }
    export_data = ExportData()
    export_data.export_to_oracle(source_table='WWA_search_app_content_info', aim_table='TAB_MVMS_APP_INFO', key_map=key_map,
                                 unique_key='title')

if __name__ == '__main__':
    main()
