import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    # 导出数据
    key_map = {
        'id' : 'vint_sequence.nextval',
        'title' : 'str_title',
        'update_info' : 'str_update_info',
        'author' : 'str_author',
        'url' : 'str_url',
        'app_url' : 'str_app_url',
        'image_url' : 'str_image_url',
        'classify' : 'int_classify_id',
        'software_size' : 'str_software_size',
        'tag' : 'str_tag',
        'platform_type' : 'vint_502', #android
        'download_count' : 'str_download_count',
        'record_time' : 'date_record_time',
        'update_time' : 'date_release_time',
        'site_id' : 'int_site_id',
        'check_status' : 'vint_201',
        'sexy_image_status' : 'str_sexy_image_status',
        'sexy_image_url' : 'str_sexy_image_url',
        'score' : 'str_score',
        'summary' : 'str_summary',
        'compatibility' : 'str_platform',
        'language' : 'int_language',
    }

    export_data = ExportData(source_table = 'GameApp_content_info', aim_table = 'tab_gams_app_info', key_map = key_map, unique_key = 'url')
    export_data.export_to_oracle()

if __name__ == '__main__':
    main()
