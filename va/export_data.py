import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    while True:
        # 导出数据
        key_map = {
            'program_id': 'vint_sequence.nextval',
            'search_type': 'int_search_type',
            'program_name': 'str_title',
            'program_url': 'str_url',
            'release_date': 'date_release_time',
            'image_url': 'str_image_url',
            'program_content':'str_content',
            'task_id': 'int_task_id',
            'keyword':'str_keyword',
            'keyword_count':'int_keyword_count',
            'check_status':'vint_202',
            'SEXY_IMAGE_STATUS':'int_sexy_image_status'
        }

        export = ExportData('VA_content_info', 'tab_ivms_program_info', key_map, 'program_url', condition = {'read_status':0, "image_pron_status" : 2})
        export.export_to_oracle()

        time.sleep(300) # 五分钟导一次数据


if __name__ == '__main__':
    main()