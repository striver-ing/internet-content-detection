import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    # 导出出版物信息
    key_map = {
        'id' : 'int__id',          # 目标键 = 源键对应的值         类型为str
        'name' : 'str_title',          # 目标键 = 源键对应的值         类型为int
        'type' : 'int_data_type',         # 目标键 = 源键对应的值         类型为date
        'page_url' : 'str_url',                  # 目标键 = 值                   类型为int
        'media_url' : 'str_image_url',                # 目标键 = 值                   类型为str
        'visit_number' : 'str_watched_count',   # 目标键 = 值为sql 查询出的结果 类型为int
        'site_id' : 'int_site_id', # 目标键 = 值为sql 查询出的结果 类型为str
        'VIOLATE_IMAGE_STATUS':'str_sexy_image_status',
        'VIOLATE_IMAGE_URL':'str_sexy_image_url',
        # 'description':
        # 'copyright_id':
        # 'text_result':
        # 'media_result':
        # 'media_confidence':
        # 'sto_id':
        # 'sto_path':
        # 'sto_tran_id':
        # 'sto_tran_path':
        # 'sto_fea_id':
        # 'sto_fea_path':
        # 'is_violation':
        # 'violation_description':
        # 'check_status':
        # 'check_time':
        'author':'str_author',
        # 'cover_path':
        'update_time':'date_update_time',
        # 'check_user_id':
    }

    export_data = ExportData()
    export_data.export_to_oracle(source_table = 'WP_content_info', aim_table = 'TAB_LCMS_PUBLICATION_INFO', key_map = key_map, unique_key = 'name', unique_key_mapping_source_key = {'name' : 'str_title'})

    #导出分集信息
    key_map = {
        'id' : 'int__id',          # 目标键 = 源键对应的值         类型为str
        'publication_id' : 'int_content_id',          # 目标键 = 源键对应的值         类型为int
        'title' : 'str_title',         # 目标键 = 源键对应的值         类型为date
        'video_url' : 'str_video_url',                  # 目标键 = 值                   类型为int
        'image_url' : 'str_image_url',                # 目标键 = 值                   类型为str
        'watched_count' : 'int_watched_count',   # 目标键 = 值为sql 查询出的结果 类型为int
        'comment_count' : 'int_comment_count', # 目标键 = 值为sql 查询出的结果 类型为str
        'release_time': 'date_release_time',
        'record_time': 'date_record_time'
    }
    export_data.export_to_oracle(source_table = 'WP_content_episode_info', aim_table = 'tab_lcms_episode_info', key_map = key_map, unique_key = 'title', unique_key_mapping_source_key = {'title' : 'str_title'})


    # 导出网站表
    key_map = {
        'id' : 'int_site_id',          # 目标键 = 源键对应的值         类型为str
        'name' : 'str_name',          # 目标键 = 源键对应的值         类型为int
        'url' : 'str_url',         # 目标键 = 源键对应的值         类型为date
        'domain_name' : 'str_domain',                  # 目标键 = 值                   类型为int
        'ip' : 'str_ip',                # 目标键 = 值                   类型为str
        'icp_number' : 'str_icp',   # 目标键 = 值为sql 查询出的结果 类型为int
        # 'city_id' : '', # 目标键 = 值为sql 查询出的结果 类型为str
        # 'iffocus': '',
        # 'status': '',
        'create_time': 'date_record_time',
        # 'update_time': 'date_record_time',
        # 'description': 'date_record_time',
        # 'crawl_status': 'date_record_time',
        'ip_address': 'str_address',
        'license_key': 'str_video_license'
        # 'hava_certificated': '',
        # 'site_sto_id': '',
        # 'site_sto_path': '',
        # 'check_status': '',

    }
    export_data.export_to_oracle(source_table = 'WP_site_info', aim_table = 'TAB_LCMS_SITE_INFO', key_map = key_map, unique_key = 'id')



if __name__ == '__main__':
    main()
