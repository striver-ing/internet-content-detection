import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    # 导出数据
    # 主播信息
    key_map = {
        'id': 'vint_sequence.nextval',
        'room_id': 'int_room_id',
        'name': 'str_name',
        'sex': 'int_sex',
        'age': 'int_age',
        'address': 'str_address',
        'image_url': 'str_image_url',
        'fans_count': 'int_fans_count',
        'watched_count': 'int_watched_count',
        'room_url': 'str_room_url',
        'video_path': 'str_video_path',
        'site_id': 'int_site_id',
        'record_time': 'date_record_time',
        'live_view': 'int_live_view',
        'monitor_status': 'vint_401',
        'json_data_url': 'str_watched_count_url'
    }

    export_data = ExportData(source_table = 'LiveApp_anchor_info', aim_table = 'tab_nbsp_anchor_info', key_map = key_map, update_read_status = False, unique_key_mapping_source_key = {'room_id':'int_room_id'})
    export_data.export_to_oracle()

    # 违规信息
    key_map = {
        'id' : 'vint_sequence.nextval',
        'TASK_ID':'int_task_id',
        'ANCHOR_ID':'int_room_id',
        'FOUND_TIME':'date_record_time',
        'CONTENT':'str_violate_content',
        'VIOLATE_IMAGE_STATUS':'str_sexy_image_status',
        'VIOLATE_IMAGE_URL':'str_sexy_image_url'
    }

    export_data = ExportData(source_table = 'LiveApp_anchor_info', aim_table = 'tab_nbsp_violate_anchor_info', key_map = key_map, update_read_status = True, condition = {'violate_content' : {'$ne':''}, 'read_status':0}, unique_key_mapping_source_key = {'ANCHOR_ID':'int_room_id'})
    export_data.export_to_oracle()

if __name__ == '__main__':
    main()
