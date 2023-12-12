# ! coding: utf-8
from pymongo import MongoClient
from collections import OrderedDict
from bson.objectid import ObjectId
import time
import os




Mongodb = MongoClient(
    '127.0.0.1',
    27017,
    document_class=OrderedDict,
    maxPoolSize=200,
    serverSelectionTimeoutMS=90000)

DATABASE = Mongodb['nextify']
DATABASE.authenticate(
    'develop',
    'g5i4dI8KzYmXs0K',
    source='nextify')

def remove_camp(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.campaigns.remove({'shop_id': shop_id})
    DATABASE.details_step_campaign.remove({'shop_id': shop_id})

def init_new_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    name_return_camp = "Chiến dịch khách hàng quay trở lại"
    name_new_cus_camp = "Chiến dịch khách hàng mới"

    #chien dich khach hang moi
    info_register = {
        'shop_id': shop_id,
        'type': 'register',
        'step_1': 'image',
        'step_2': 'collect',
        'step_3': '0',
        'step_4': 'connect_success',
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
        },
        'create_at': time.time(),
        'update_at': time.time(),
        'status': True,
        'is_birthday': False,
        'name': name_new_cus_camp
    }

    new_register_camp = DATABASE.campaigns.insert(info_register)

    details = {
        'content_connect': '',
        'connect_button': '',
        'display_coupon': False,
        'display_coupon_txt': '',
        'hotspot_method': 'default',
        'default_code': '', 
        'redirect_type': 'website',
        'auto_website': 'https://viettelconstruction.com.vn/',
        'auto_popup_ios': '',
        'auto_popup_android': '',
        'auto_facebook_page': '',
        'auto_popup_zalo': '',
        'auto_popup_insta': '',
        'auto_facebook_mess': '',
    }

    info_connect = {
        'camp_id': new_register_camp,
        'type_page': "connect_success",
        'shop_id': shop_id,
        'step': '4',
        'details': details
    }
    login_form = {
        'phone': True,
        'name': True,
        'birthday': False,
        'year_birthday': False,
        'gender': False,
        'email': True,
        'welcome_text': "Đăng ký khách hàng thân thiết để được nhận nhiều ưu đãi hấp dẫn.",
        'welcome_button': 'Kết nối',
        'birthday_text': "Chúc bạn sinh nhật vui vẻ tràn đầy hạnh phúc.",
        'phone_require': True,
        'name_require': True,
        'birthday_require': False,
        'gender_require': False,
        'email_require': False,
        'year_birthday_require': False,
        'otp': False,
        'company': False,
        'company_require': False,
        'company_role': False,
        'company_role_require': False,
        'vocation': False,
        'vocation_require': False,
        'connect_with_facebook': False,
        'connect_with_zalo': False,
        'allow_access_friend_zalo': False,
        'connect_with_messenger': False,
        'tag': [],
        'background': '7/2ee3934f7e' 
    }
    info_collect = {
        'camp_id': new_register_camp,
        'type_page': "collect",
        'shop_id': shop_id,
        'step': '2',
        'details': login_form
    }

    info_image_register = {
        'update_at': time.time(),
        'create_at': time.time(),
        'camp_id': new_register_camp,
        'type_page': "image",
        'shop_id': shop_id,
        'step': '1',
        'details': {
            'photo': '1/35db041b5e',
            'title_image': '',
            'content_image': '',

        }
    }
    DATABASE.details_step_campaign.insert(info_collect)
    DATABASE.details_step_campaign.insert(info_image_register)
    DATABASE.details_step_campaign.insert(info_connect)

    #chien dich quay tro lai mac dinh
    info_default = {
        'shop_id': shop_id,
        'type': 'default',
        'step_1': 'image',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'create_at': time.time(),
        'update_at': time.time(),
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
            'convert_min_hour': 0,
            'convert_max_hour': 23.5,
            'timestamp_start_event': 0,
            'timestamp_end_event': 0
        },
        'status': True,
        'is_birthday': False,
        'name': name_return_camp
    }

    new_default_camp = DATABASE.campaigns.insert(info_default)
    info_connect_return = {
        'camp_id': new_default_camp,
        'type_page': "connect_success",
        'shop_id': shop_id,
        'step': '4',
        'details': details
    }

    info_image_return = {
        'update_at': time.time(),
        'create_at': time.time(),
        'camp_id': new_default_camp,
        'type_page': "image",
        'shop_id': shop_id,
        'step': '1',
        'details': {
            'photo': '1/35db041b5e',
            'title_image': '',
            'content_image': '',

        }
    }
    DATABASE.details_step_campaign.insert(info_connect_return)
    DATABASE.details_step_campaign.insert(info_image_return)

    #lan3
    #chien dich quay tro lai mac dinh
    info_lan3 = {
        'shop_id': shop_id,
        'type': 'default',
        'step_1': 'survey',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'create_at': time.time(),
        'update_at': time.time(),
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
            'convert_min_hour': 0,
            'convert_max_hour': 23.5,
            'timestamp_start_event': 0,
            'timestamp_end_event': 0
        },
        'status': True,
        'is_birthday': False,
        'name': 'Khách tới lần 3'
    }

    lan_3 = DATABASE.campaigns.insert(info_lan3)
    info_connect_lan_3 = {
        'camp_id': lan_3,
        'type_page': "connect_success",
        'shop_id': shop_id,
        'step': '4',
        'details': details
    }
    survey = DATABASE.survey_splash_page.find_one({'shop_id': shop_id, 'question': "Bạn đánh giá thế nào về sản phẩm của chúng tôi?"})
    survey_id = survey.get('_id')
    # DATABASE.survey_splash_page.update({'_id': survey_id}, {'$set': {'photo': '6/090db213af51'}})
    info_survey = {
        'update_at': time.time(),
        'create_at': time.time(),
        'camp_id': lan_3,
        'type_page': "survey",
        'shop_id': shop_id,
        'step': '1',
        'details': {
            'survey_id': str(survey_id),
            'question': 'Bạn đánh giá thế nào về sản phẩm của chúng tôi?'

        }
    }
    DATABASE.details_step_campaign.insert(info_survey)
    DATABASE.details_step_campaign.insert(info_connect_lan_3)




# list_shop = ['6098b1f3b573f62a6921b3ed', '6098b2beb573f62b1bfc469b', '6098b30ab573f62b4f5db71c', '6098b35eb573f62bb8880d6d', '6098b392b573f62bec413266', '6098b3d7b573f62c4ee8c379', '6098b415b573f62c884f0183', '60934e49b573f617dda6eba5', '6098b48eb573f62d1279225d', '6098b4c6b573f62d51c1605d', '6098b518b573f62dbca656c9', '6098b556b573f62df13f1ba8', '6098b628b573f62e9d2171c9', '6098b65db573f62eda3f2954', '6098b6a2b573f62f19ec1827', '6098b7feb573f6311dfdc181', '6098b837b573f631539e0735', '6098b867b573f631818be317', '6098b89db573f631b7ce9a2c', '6098b8e9b573f631fd5aa770', '6098b916b573f632424c5cb9', '6098b981b573f632cbdcc1c3', '6098b9b0b573f632f7866aaa', '6098b9d9b573f633201827bb', '6098ba1fb573f6338580ff64', '6098ba51b573f633da8f7e36', '6098ba85b573f63401633861', '6098babab573f63428aae888', '6098baeeb573f6346e317960', '6098bb19b573f634c3e175ba', '6098bb4eb573f634f5d6c43e', '6098bb7eb573f63544ceb7d8', '6098bbb8b573f6357b2103f0', '6098bbeab573f635a3890b28', '6098bc1cb573f63605700d08', '6098bc4bb573f63633e8159a', '6098bc84b573f6365c838fd4', '6098bcb6b573f636ae81d297', '6098bcf1b573f636db5e5925', '6098bd1cb573f63701180449', '6098bd4cb573f6375091763d', '6098bd77b573f63784d32d70', '6098bddfb573f637d07342ed', '6098be14b573f6382a367c83', '6088c65d0b171525e5177cd7', '6098bfe6b573f639debe0b5f', '6098c00eb573f63a1b64314d', '6098c035b573f63a6d15296f', '6098c067b573f63a91434ab4', '6098c095b573f63ab9b881fd', '6098d857b573f64fa0eff8e4', '6098d887b573f64fd5ba5106', '6098d8b3b573f65013c0abbf', '6098d8f6b573f650796dab36', '6098d938b573f650c0c784a4', '607e8a6b0b171525e5177cb5', '607e953f0b171525e5177cb6', '607e9b020b171525e5177cb7', '607e9c2b0b171525e5177cb8', '607e9c4b0b171525e5177cb9', '6098d9b0b573f65138748541', '6098d9ebb573f651aee324da', '6098da1cb573f651d9c6a92d', '6098da4cb573f65210a9fa29', '6098da79b573f6523c708f88']
# for shop in list_shop:
#     remove_camp(shop)
#     init_new_campaign(shop)