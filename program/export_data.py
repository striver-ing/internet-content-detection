import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    export_data = ExportData()

    # 导出部数据
    key_map = {
        'PROGRAM_ID' : 'int__id',
        'RELEASE_TIME' : 'date_release_time',
        'EPISODE' : 'str_episode',
        'ACTORS' : 'str_actors',
        'DIRECTORS' : 'str_directors',
        'PROGRAM_NAME' : 'str_program_name',
        'SUMMARY' : 'str_summary',
        'SITE_ID' : 'int_site_id',
        'IMAGE_URL' : 'str_image_url',
        'PROGRAM_URL' : 'str_program_url'
    }

    export_data.export_to_oracle(source_table = 'PROGRAM_info', aim_table = 'tab_ntms_program_info', key_map = key_map, unique_key = 'PROGRAM_ID')

    # 导出集数据
    key_map = {
        'ID' : 'int__id',
        'PROGRAM_ID' : 'int_program_id',
        'PROGRAM_EPISODE' : 'str_episode_num',
        'TIME_LENGTH' : 'str_time_length',
        'EPISODE_NAME' : 'str_episode_name',
        'DOWNLOAD_STATUS' : 'int_download_status',
        'DOWNLOAD_URL' : 'str_download_url',
        'PLAY_URL' : 'str_download_url',
        'EPISODE_URL' : 'str_episode_url',
        'UPDATE_TIME' : 'date_record_time',
        'SUMMARY' : 'str_summary',
        'IMAGE_URL' : 'str_image_url',
        'sto_path' : 'str_sto_path',
        'sto_id' : 'int_sto_id'
    }

    export_data.export_to_oracle(source_table = 'PROGRAM_EPISODE_info', aim_table = 'tab_ntms_program_episode_info', key_map = key_map, unique_key = 'EPISODE_URL')


if __name__ == '__main__':
    main()
