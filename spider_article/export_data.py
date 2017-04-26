import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    # 导出数据
    export_data = ExportData()
    key_map = {
        'id': 'int__id',
        'name': 'str_name',
        'url': 'str_url',
    }
    export_data.export_to_oracle(source_table='article_site_info', aim_table='OP_SITE_INFO', key_map=key_map,
                                 unique_key='url')
    key2_map = {
        'id': 'int__id',
        'op_title': 'str_title',
        'ourl': 'str_url',
        'summary': 'str_content',
        # 'op_author': 'str_author',
        # 'found_time': 'date_release_time',
        # 'creat_time': 'date_record_time',
        'site_id': 'int_site_id'
    }
    export_data.export_to_oracle(source_table='article_text_info', aim_table='OP_OPINION_INFO', key_map=key2_map,
                                 unique_key='ourl')


if __name__ == '__main__':
    main()
