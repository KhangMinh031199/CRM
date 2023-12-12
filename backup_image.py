# ! coding: utf-8
from pymongo import MongoClient
from collections import OrderedDict
from bson.objectid import ObjectId
import time
import requests
import os
import tempfile
import base64
from PIL import Image
from io import BytesIO
import storage_api

URL_FID = 'http://103.226.250.83:9333/dir/assign'
URL_UPLOAD = 'http://103.226.250.83:8089/'

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

#old 
# Old_Mongodb = MongoClient(
#     '127.0.0.1',
#     27017,
#     document_class=OrderedDict,
#     maxPoolSize=200,
#     serverSelectionTimeoutMS=90000)

# OLD_DATABASE = Old_Mongodb['nextify']
# OLD_DATABASE.authenticate(
#     'develop',
#     'g5i4dI8KzYmXs0K',
#     source='nextify')


def move_file(photo):
    img = storage_api.get_file(photo)
    file_data = img.get('file_data')
    file_data = str(file_data)
    file_data = base64.b64decode(str(file_data))
    fid = ''
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(file_data)
            response = requests.get(URL_FID)
            result = response.json()
            fid = result.get('fid')
            url1 = URL_UPLOAD + fid
            headers = {}
            payload = {}
            files = [
                ('file', (photo, open(str(path), 'rb'), 'png'))
            ]
            response1 = requests.post(url1, headers=headers, data=payload, files=files)
            fid = fid.replace(',', '/')
    finally:
        os.remove(path)
    return fid



# old_shop = OLD_DATABASE.shop.find({})
# for shop in old_shop:
#     logo = None
#     background = None
#     shop_id = shop.get('_id')
#     print "----shop id"
#     print shop_id
#     logo = shop.get('logo')
#     background = shop.get('background')
#     if logo and len(logo) > 0:
#         new_logo = move_file(logo)
#         if new_logo and len(new_logo) > 0:
#             print "---new logo"
#             DATABASE.shop.update({'_id': shop_id}, {'$set': {'logo': new_logo}})
#     if background and len(background) > 0:
#         new_background = move_file(background)
#         if new_background and len(new_background) > 0:
#             print '----new bg'
#             DATABASE.shop.update({'_id': shop_id}, {'$set': {'background': new_background}})


# old_survey = OLD_DATABASE.survey_splash_page.find({})
# for survey in old_survey:
#     survey_id = survey.get('_id')
#     photo = None
#     photo = survey.get('photo')
#     print "----survey"
#     print survey_id
#     if photo and len(photo) > 0:
#         new_photo = move_file(photo)
#         if new_photo and len(new_photo) > 0:
#             print "----new survey"
#             DATABASE.survey_splash_page.update({'_id': survey_id}, {'$set': {'photo': new_photo}})

list_mer = []
list_vcc = []
vcc = ['6098b1f3b573f62a6921b3ec',
    '6098b2beb573f62b1bfc469a',
    '6098b30ab573f62b4f5db71b',
    '6098b35eb573f62bb8880d6c',
    '6098b392b573f62bec413265',
    '6098b3d7b573f62c4ee8c378',
    '6098b415b573f62c884f0182',
    '60934e49b573f617dda6eba4',
    '6098b48eb573f62d1279225c',
    '6098b4c6b573f62d51c1605c',
    '6098b518b573f62dbca656c8',
    '6098b556b573f62df13f1ba7',
    '6098b628b573f62e9d2171c8',
    '6098b65db573f62eda3f2953',
    '6098b6a2b573f62f19ec1826',
    '6098b7feb573f6311dfdc180',
    '6098b837b573f631539e0734',
    '6098b867b573f631818be316',
    '6098b89db573f631b7ce9a2b',
    '6098b8e9b573f631fd5aa76f',
    '6098b916b573f632424c5cb8',
    '6098b981b573f632cbdcc1c2',
    '6098b9b0b573f632f7866aa9',
    '6098b9d9b573f633201827ba',
    '6098ba1fb573f6338580ff63',
    '6098ba51b573f633da8f7e35',
    '6098ba85b573f63401633860',
    '6098babab573f63428aae887',
    '6098baeeb573f6346e31795f',
    '6098bb19b573f634c3e175b9',
    '6098bb4eb573f634f5d6c43d',
    '6098bb7eb573f63544ceb7d7',
    '6098bbb7b573f6357b2103ef',
    '6098bbeab573f635a3890b27',
    '6098bc1cb573f63605700d07',
    '6098bc4bb573f63633e81599',
    '6098bc84b573f6365c838fd3',
    '6098bcb6b573f636ae81d296',
    '6098bcf1b573f636db5e5924',
    '6098bd1cb573f63701180448',
    '6098bd4cb573f6375091763c',
    '6098bd77b573f63784d32d6f',
    '6098bddfb573f637d07342ec',
    '6098be14b573f6382a367c82',
    '6088c4cc0b171525e5177ccc',
    '6098bfe5b573f639debe0b5e',
    '6098c00eb573f63a1b64314c',
    '6098c035b573f63a6d15296e',
    '6098c067b573f63a91434ab3',
    '6098c095b573f63ab9b881fc',
    '6098d857b573f64fa0eff8e3',
    '6098d887b573f64fd5ba5105',
    '6098d8b3b573f65013c0abbe',
    '6098d8f6b573f650796dab35',
    '6098d938b573f650c0c784a3',
    '607e89320b171525e5177caa',
    '6098d9b0b573f65138748540',
    '6098d9ebb573f651aee324d9',
    '6098da1cb573f651d9c6a92c',
    '6098da4cb573f65210a9fa28',
    '6098da79b573f6523c708f87'
]
# merchants = DATABASE.merchants.find({'when': {'$gte': 1617870377}})
# for mer in merchants:
#     list_mer.append(str(mer.get('_id')))
# merchants_vcc = DATABASE.merchants.find({'when': {'$gte': 1617870377}, 
#                                         '$or': [
#                                             {'name': {'$regex': '6000'}}, 
#                                             {'name': {'$regex': '300'}},
#                                             {'name': {'$regex': 'abc'}}
#                                         ]
#                                         })
# for mer_vcc in merchants_vcc:
#     list_vcc.append(str(mer_vcc.get('_id')))

# main_list = list(set(list_mer) - set(list_vcc))
# result = list(set(main_list) - set(vcc))
# print "+++++++++++++++++++++++++++"

# for re in result:
#     info = DATABASE.shop.find({'merchant_id': re})
#     for i in info:
#         print '-------------'
#         print i.get('name')
    
def normalize(mac_addr):
    # Determine which delimiter style out input is using
    if '.' in mac_addr:
        delimiter = '.'
    elif ':' in mac_addr:
        delimiter = ':'
    elif '-' in mac_addr:
        delimiter = '-'
    else:
        delimiter = None

    # Eliminate the delimiter
    m = mac_addr.replace(delimiter, '') if delimiter else mac_addr

    m = m.strip().lower()
    return ':'.join(['%s%s' % (m[i], m[i + 1]) for i in range(0, 12, 2)])

def get_shop_info(shop_id=None, gateway_mac=None):
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.shop.find_one({'_id': shop_id})
    elif gateway_mac:
        if isinstance(gateway_mac, list):
            gateway_mac = gateway_mac[0]
        gateway_mac = normalize(gateway_mac)
        return DATABASE.shop.find_one({'gateway_mac': gateway_mac})


def init_new_campaign_37(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = get_shop_info(shop_id=shop_id)
    name_return_camp = "Chiến dịch khách hàng quay trở lại"
    name_new_cus_camp = "Chiến dịch khách hàng mới"

    #chien dich khach hang moi
    info_register = {
        'shop_id': shop_id,
        'type': 'register',
        'step_1': 'collect',
        'step_2': '0',
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
    auto_popup = ''
    connect_success = shop.get('connect_success')
    if connect_success:
        auto_popup = connect_success.get('auto_popup')
    details = {
        'content_connect': '',
        'connect_button': '',
        'display_coupon': False,
        'display_coupon_txt': '',
        'hotspot_method': 'default',
        'default_code': '', 
        'redirect_type': 'website',
        'auto_website': auto_popup,
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
    login_form = shop.get('login_form')
    info_collect = {
        'camp_id': new_register_camp,
        'type_page': "collect",
        'shop_id': shop_id,
        'step': '1',
        'details': login_form
    }

    DATABASE.details_step_campaign.insert(info_collect)
    DATABASE.details_step_campaign.insert(info_connect)

    #chien dich quay tro lai mac dinh
    photo_img = ''
    logo = shop.get('logo')
    background = shop.get('background')
    if logo and len(logo) == 14:
        photo_img = logo
    elif logo and len(logo) > 0 and len(logo) != 14:
        new_photo = move_file(logo)
        if new_photo and len(new_photo) > 0:
            photo_img = new_photo
    elif background and len(background) == 14:
        photo_img = background
    elif background and len(background) > 0 and len(background) != 12:
        new_photo = move_file(background)
        if new_photo and len(new_photo) > 0:
            photo_img = new_photo
    else:
        photo_img = ''
    if photo_img and len(photo_img) > 0:
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
                'photo': photo_img,
                'title_image': '',
                'content_image': '',

            }
        }
        DATABASE.details_step_campaign.insert(info_connect_return)
        DATABASE.details_step_campaign.insert(info_image_return)
    else:
        info_default = {
            'shop_id': shop_id,
            'type': 'default',
            'step_1': '0',
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
        DATABASE.details_step_campaign.insert(info_connect_return)
    print 'done'





camps = DATABASE.hotspot_campaign.find({'campaign_type': 'register',
                                        '$or': [
                                            {'step_1': {'$in': ['promotion', 'hour', 'tags', 'weekday']}},
                                            {'step_2': {'$in': ['promotion', 'hour', 'tags', 'weekday']}},
                                            {'step_3': {'$in': ['promotion', 'hour', 'tags', 'weekday']}},

                                        ]})

list_shop = []
# for camp in camps:
#     shop_id = camp.get('shop_id')
#     if not isinstance(shop_id, ObjectId):
#         shop_id = ObjectId(shop_id)
#     list_shop.append(shop_id)
# print list_shop
# for shop in list_shop:
#     DATABASE.shop.update({'_id': shop}, {'$set': {'new_camp': True}})
#     # init_new_campaign_37(shop)

# init_new_campaign_37('597fe18647dd46ce3e554089')