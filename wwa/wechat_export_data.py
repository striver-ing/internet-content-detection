import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time


export_data = ExportData()

def account_main():
    # 导出信息
    key_map = {
        'ID' : 'int__id',
        'NAME' : 'str_name',
        'ACCOUNT_ID' : 'str_account_id',
        'ARTICLE_COUNT' : 'int_article_count',
        'WECHAT_CERTIFICATION' : 'str_certification',
        'IS_VERIFIED' : 'int_is_verified',
        'BARCODE_URL' : 'str_barcode_url',
        'LOCAL_BARCODE_URL' : 'str_local_barcode_url',
        'IMAGE_URL' : 'str_image_url',
        'LOCAL_IMAGE_URL' : 'str_local_image_url',
        'ACCOUNT_URL' : 'str_account_url',
        # 'MONITOR_STATUS' : 'vint_401',
        'SUMMARY' : 'str_summary'
    }

    unique_key_mapping_source_key = {
        'ACCOUNT_ID' : 'str_account_id'
    }

    export_data.export_to_oracle(source_table = 'WWA_wechat_official_accounts', aim_table = 'TAB_MVMS_WECHAT_INFO', key_map = key_map, unique_key = 'ACCOUNT_ID', update_read_status = False, unique_key_mapping_source_key = unique_key_mapping_source_key)

def article_main():
    # 导出content信息
    key_map = {
        'ID':'int__id',
        'ACCOUNT_ID' : 'str_official_accounts_id',
        'ARTICLE_TITLE' : 'str_title',
        'SUMMARY' : 'str_summary',
        'ARTICLE_URL' : 'str_article_url',
        'RELEASE_TIME' : 'date_release_time',
        'ARTICLE_CONTENT' : 'clob_content',
        'VIDEO_URL' : 'str_video_url',
        'VIOLATE_STATUS' : 'int_violate_status',
        'IMAGE_URL' : 'str_image_url',
        'LOCAL_IMAGE_URL' : 'str_local_image_url'
    }

    export_data.export_to_oracle(source_table = 'WWA_wechat_article', aim_table = 'TAB_MVMS_WECHAT_ARTICLE_INFO', key_map = key_map, unique_key = 'ARTICLE_TITLE')


if __name__ == '__main__':
    while True:
        account_main()
        article_main()
        time.sleep(600)

