import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    # 导出content信息

    key_map = {
        'id': 'int__id',
        'APP_ID': 'int_site_id',
        'COLUMN_ID ': 'int_column_id',
        'CONTENT_ID': 'int__id',
        'RELEASE_TIME': 'date_release_time',
        'TITLE': 'str_title',
        'ORIGINAL_URL': 'str_url',
        'CONTENT': 'str_content',
        'ABSTRACT_IMAGE_URL': 'str_image_url',
        'ABSTRACT_IMAGE_LOCAL_PATH': 'str_img_stor_path',
        'VIDEO_URL': 'str_video_url',
        'VIDEO_LOCAL_PATH': 'str_video_stor_path',
        'ISAUDIO': 'int_is_audio',
        'ISDOWNLOAD': 'int_is_download',
        'CREATE_TIME': 'date_record_time',
        'VIOLATE_ID': 'int_violate_id',
        'SENSITIVE_ID': 'int_sensitive_id',
        'STORAGE_ID': 'int_storage_id',
        # 'CHECK_STATUS ':
        # 'CHECK_TIM'E':
        # 'CHECK_USER':
        # 'DOWN_STO_ID':

    }

    export_data = ExportData()
    export_data.export_to_oracle(source_table = 'WWA_app_content_info', aim_table = 'TAB_MVMS_APP_CONTENT', key_map = key_map, unique_key = 'ORIGINAL_URL')

    #导出信息
    key_map = {
        'id': 'int__id',          # 目标键 = 源键对应的值         类型为str
        'APP_ID': 'int_site_id',          # 目标键 = 源键对应的值         类型为int
        'COLUMN_ID': 'int_column_id',         # 目标键 = 源键对应的值         类型为date
        'CONTENT_ID': 'int__id',                  # 目标键 = 值                   类型为int
        'RELEASE_TIME': 'date_release_time',
        'TITLE': 'str_title',   # 目标键 = 值为sql 查询出的结果 类型为int
        'ORIGINAL_URL': 'str_url', # 目标键 = 值为sql 查询出的结果 类型为str
        'ABSTRACT_IMAGE_URL': 'str_image_url',
        'ABSTRACT_IMAGE_LOCAL_PATH': 'str_img_stor_path',
        'VIDEO_URL': 'str_video_url',
        'VIDEO_LOCAL_PATH': 'str_video_stor_path',
        'STORAGE_ID': 'int_storage_id',
        'VIOLATE_ID': 'int_violate_id',
        'SENSITIVE_ID': 'int_sensitive_id',
        'ISAUDIO': 'int_is_audio',
        'CREATE_TIME': 'date_record_time',
        # 'CHECK_STATUS': '',
        # 'CHECK_TIME': '',
        # 'CHECK_USER': '',
        # 'DOWN_STO_ID': '',
        'CONTENT': 'str_content',
        # 'CONTENT1': '',

    }
    export_data.export_to_oracle(source_table = 'VAApp_vioation_content_info', aim_table = 'TAB_MVMS_VIOLATION_CONTENT', key_map = key_map, unique_key = 'ORIGINAL_URL')

if __name__ == '__main__':
    main()
