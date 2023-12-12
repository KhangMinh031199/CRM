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

URL_FID = 'http://103.226.250.83:9333/dir/assign'
URL_UPLOAD = 'http://103.226.250.83:8089/'


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
                ('file', (photo, open(str(path), 'rb'), 'jpeg'))
            ]
            response1 = requests.post(url1, headers=headers, data=payload, files=files)
            fid = fid.replace(',', '/')
    finally:
        os.remove(path)
    return fid


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


def get_cards(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {'shop_id': shop_id}
    slides = []
    cards = DATABASE.card.find(info).sort('timestamp', -1)
    for card in cards:
        photo = card.get('photo')
        if photo and len(photo) > 0:
            photo_conv = move_file(photo)
            slides.append(photo_conv)
    return slides


def get_survey_item(survey_id):
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    return DATABASE.survey_splash_page.find_one({'_id': survey_id})


def item_mini_game_by_id(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.mini_game_page.find_one({
        '_id': camp_id
    })


def get_splash_page_by_type(shop_id, type_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    pages = DATABASE.splash_page.find({
        'shop_id': shop_id,
        'type_page': type_page
    })
    return pages


def get_splash_page_by_type_active(shop_id, type_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    pages = DATABASE.splash_page.find({
        'shop_id': shop_id,
        'type_page': type_page,
        'active': True
    })
    return pages


def convert_campaign(id_camp):
    if not isinstance(id_camp, ObjectId):
        id_camp = ObjectId(id_camp)
    campaign = DATABASE.hotspot_campaign.find_one({'_id': id_camp})
    step_1 = campaign.get('step_1')
    step_2 = campaign.get('step_2')
    step_3 = campaign.get('step_3')
    step_4 = campaign.get('step_4')
    shop_id = campaign.get('shop_id')
    campaign_type = campaign.get('campaign_type')
    shop = get_shop_info(shop_id=shop_id)
    min_visit_camp = campaign.get('min_visit')
    max_visit_camp = campaign.get('max_visit')
    old_steps = []
    old_steps.append(step_1)
    old_steps.append(step_2)
    old_steps.append(step_3)
    if not min_visit_camp:
        min_visit_camp = 0
    if not max_visit_camp:
        max_visit_camp = 0
    tags_camp = []
    list_tags = []
    tags_camp = campaign.get('camp_tags_selects')
    if tags_camp and len(tags_camp) > 0:
        for tag in tags_camp:
            if not isinstance(tag, ObjectId):
                tag = ObjectId(tag)
            list_tags.append(tag)
    list_1 = []
    list_2 = []
    list_3 = []
    list_4 = []

    if step_1 == '0':
        list_1.append({})
    if step_1 == 'register':
        detail = shop.get('login_form')
        list_1.append(detail)
    if step_1 == "default":
        slides = get_cards(shop_id)
        detail = {
            'slides': slides,
            'num_slide': len(slides)
        }
        list_1.append(detail)
    if step_1 == 'plus_register':
        detail = shop.get('plus_login_form')
        list_1.append(detail)
    if step_1 == 'survey':
        survey_id = campaign.get('survey_step_1')
        survey = get_survey_item(survey_id)
        if survey:
            question = survey.get('question')
            detail = {
                'survey_id': survey_id,
                'question': question
            }
            list_1.append(detail)
    if step_1 == 'spin':
        spin_id = campaign.get('spin_step_1')
        spin = item_mini_game_by_id(spin_id)
        if spin:
            name_spin = spin.get('info').get('name')
            detail = {
                'spin_id': spin_id,
                'name_spin': name_spin
            }
            list_1.append(detail)

    if step_1 == 'birthday':
        page = get_splash_page_by_type(shop_id, 'birthday')[0]
        photo = page.get('photo')
        title = page.get('title')
        if not title:
            title = ''
        content = page.get('content')
        if not content:
            content = ''
        if photo and len(photo) > 0:
            photo_conv = move_file(photo)
            detail = {
                'photo': photo_conv,

                'title': title,
                'content': content
            }
            list_1.append(detail)

    if step_1 == 'hour':
        pages = get_splash_page_by_type_active(shop_id, 'hour')
        for page in pages:
            hour_from = page.get('hour_from')
            hour_to = page.get('hour_to')
            photo = page.get('photo')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''

            if photo and len(photo) > 0:
                photo_conv = move_file(photo)
                detail = {
                    'photo': photo_conv,
                    'title': title,
                    'content': content,
                    'hour_from': hour_from,
                    'hour_to': hour_to
                }
                list_1.append(detail)

    if step_1 == 'weekday':
        pages = get_splash_page_by_type_active(shop_id, 'weekday')
        for page in pages:
            weekday = page.get('weekday')
            photo = page.get('photo')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if photo and len(photo) > 0:
                photo_conv = move_file(photo)
                detail = {
                    'photo': photo_conv,
                    'title': title,
                    'content': content,
                    'weekday': weekday
                }
                list_1.append(detail)

    if step_1 == 'tags':
        pages = get_splash_page_by_type_active(shop_id, 'tag')
        for page in pages:
            tags = []
            tags = page.get('tag')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if list_tags and len(list_tags) > 0:
                if set(tags) < set(list_tags):
                    photo = page.get('photo')
                    if photo and len(photo) > 0:
                        photo_conv = move_file(photo)
                        detail = {
                            'photo': photo_conv,
                            'tag_group': tags,
                            'title': title,
                            'content': content
                        }
                        list_1.append(detail)
            else:
                photo = page.get('photo')
                if photo and len(photo) > 0:
                    photo_conv = move_file(photo)
                    detail = {
                        'photo': photo_conv,
                        'tag_group': tags,
                        'title': title,
                        'content': content
                    }
                    list_1.append(detail)
    if step_1 == 'loyal':
        pages = get_splash_page_by_type_active(shop_id, 'loyal')
        for page in pages:
            min_visit = 0
            max_visit = 0
            loyal_min = page.get('loyal_count')
            if not loyal_min:
                loyal_min = 0
            loyal_max = page.get('loyal_count_max')
            if not loyal_max:
                loyal_max = 1000
            if min_visit_camp == 0 and max_visit_camp == 0:
                min_visit = loyal_min
                max_visit = loyal_max
            else:
                if min_visit_camp > loyal_min:
                    min_visit = min_visit_camp
                else:
                    min_visit = loyal_min
                if max_visit_camp > loyal_max:
                    max_visit = loyal_max
                else:
                    max_visit = max_visit_camp
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            photo = page.get('photo')
            if photo:
                photo_conv = move_file(photo)
                if min_visit == 0 and max_visit == 0:
                    detail = {
                        'photo': photo_conv,
                        'min_visit': min_visit,
                        'max_visit': max_visit,
                        'title': title,
                        'content': content
                    }
                    list_1.append(detail)
                elif min_visit != 0 and max_visit != 0 and min_visit <= max_visit:
                    detail = {
                        'photo': photo_conv,
                        'min_visit': min_visit,
                        'max_visit': max_visit,
                        'title': title,
                        'content': content
                    }
                    list_1.append(detail)
                else:
                    pass

    # step 2
    if step_2 == '0':
        list_2.append({})
    if step_2 == 'register':
        detail = shop.get('login_form')
        list_2.append(detail)
    if step_2 == "default":
        slides = get_cards(shop_id)
        detail = {
            'slides': slides,
            'num_slide': len(slides)
        }
        list_2.append(detail)
    if step_2 == 'plus_register':
        detail = shop.get('plus_login_form')
        list_2.append(detail)
    if step_2 == 'survey':
        survey_id = campaign.get('survey_step_2')
        survey = get_survey_item(survey_id)
        if survey:
            question = survey.get('question')
            detail = {
                'survey_id': survey_id,
                'question': question
            }
            list_2.append(detail)
    if step_2 == 'spin':
        spin_id = campaign.get('spin_step_2')
        spin = item_mini_game_by_id(spin_id)
        if spin:
            name_spin = spin.get('info').get('name')
            detail = {
                'spin_id': spin_id,
                'name_spin': name_spin
            }
            list_2.append(detail)

    if step_2 == 'birthday':
        page = get_splash_page_by_type(shop_id, 'birthday')[0]
        photo = page.get('photo')
        title = page.get('title')
        if not title:
            title = ''
        content = page.get('content')
        if not content:
            content = ''
        if photo and len(photo) > 0:
            photo_conv = move_file(photo)
            detail = {
                'photo': photo_conv,
                'title': title,
                'content': content
            }
            list_2.append(detail)
    if step_2 == 'hour':
        pages = get_splash_page_by_type_active(shop_id, 'hour')
        for page in pages:
            hour_from = page.get('hour_from')
            hour_to = page.get('hour_to')
            photo = page.get('photo')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if photo and len(photo) > 0:
                photo_conv = move_file(photo)
                detail = {
                    'photo': photo_conv,
                    'title': title,
                    'content': content,
                    'hour_from': hour_from,
                    'hour_to': hour_to
                }
                list_2.append(detail)
    if step_2 == 'weekday':
        pages = get_splash_page_by_type_active(shop_id, 'weekday')
        for page in pages:
            weekday = page.get('weekday')
            photo = page.get('photo')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if photo and len(photo) > 0:
                photo_conv = move_file(photo)
                detail = {
                    'photo': photo_conv,
                    'title': title,
                    'content': content,
                    'weekday': weekday
                }
                list_2.append(detail)
    if step_2 == 'tags':
        pages = get_splash_page_by_type_active(shop_id, 'tag')
        for page in pages:
            tags = []
            tags = page.get('tag')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if list_tags and len(list_tags) > 0:
                if set(tags) < set(list_tags):
                    photo = page.get('photo')
                    if photo and len(photo) > 0:
                        photo_conv = move_file(photo)
                        detail = {
                            'photo': photo_conv,
                            'tag_group': tags,
                            'title': title,
                            'content': content
                        }
                        list_2.append(detail)
            else:
                photo = page.get('photo')
                if photo and len(photo) > 0:
                    photo_conv = move_file(photo)
                    detail = {
                        'photo': photo_conv,
                        'tag_group': tags,
                        'title': title,
                        'content': content
                    }
                    list_2.append(detail)
    if step_2 == 'loyal':
        pages = get_splash_page_by_type_active(shop_id, 'loyal')
        for page in pages:
            min_visit = 0
            max_visit = 0
            loyal_min = page.get('loyal_count')
            if not loyal_min:
                loyal_min = 0
            loyal_max = page.get('loyal_count_max')
            if not loyal_max:
                loyal_max = 1000
            if min_visit_camp == 0 and max_visit_camp == 0:
                min_visit = loyal_min
                max_visit = loyal_max
            else:
                if min_visit_camp > loyal_min:
                    min_visit = min_visit_camp
                else:
                    min_visit = loyal_min
                if max_visit_camp > loyal_max:
                    max_visit = loyal_max
                else:
                    max_visit = max_visit_camp
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            photo = page.get('photo')
            if photo:
                photo_conv = move_file(photo)
                if min_visit == 0 and max_visit == 0:
                    detail = {
                        'photo': photo_conv,
                        'min_visit': min_visit,
                        'max_visit': max_visit,
                        'title': title,
                        'content': content
                    }
                    list_2.append(detail)
                elif min_visit != 0 and max_visit != 0 and min_visit <= max_visit:
                    detail = {
                        'photo': photo_conv,
                        'min_visit': min_visit,
                        'max_visit': max_visit,
                        'title': title,
                        'content': content
                    }
                    list_2.append(detail)
                else:
                    pass

    if step_3 == '0':
        list_3.append({})
    if step_3 == 'register':
        detail = shop.get('login_form')
        list_3.append(detail)
    if step_3 == "default":
        slides = get_cards(shop_id)
        detail = {
            'slides': slides,
            'num_slide': len(slides)
        }
        list_3.append(detail)
    if step_3 == 'plus_register':
        detail = shop.get('plus_login_form')
        list_3.append(detail)
    if step_3 == 'survey':
        survey_id = campaign.get('survey_step_3')
        survey = get_survey_item(survey_id)
        if survey:
            question = survey.get('question')
            detail = {
                'survey_id': survey_id,
                'question': question
            }
            list_3.append(detail)
    if step_3 == 'spin':
        spin_id = campaign.get('spin_step_3')
        spin = item_mini_game_by_id(spin_id)
        if spin:
            name_spin = spin.get('info').get('name')
            detail = {
                'spin_id': spin_id,
                'name_spin': name_spin
            }
            list_3.append(detail)

    if step_3 == 'birthday':
        page = get_splash_page_by_type(shop_id, 'birthday')[0]
        photo = page.get('photo')
        title = page.get('title')
        if not title:
            title = ''
        content = page.get('content')
        if not content:
            content = ''
        if photo and len(photo) > 0:
            photo_conv = move_file(photo)
            detail = {
                'photo': photo_conv,
                'title': title,
                'content': content
            }
            list_3.append(detail)

    if step_3 == 'hour':
        pages = get_splash_page_by_type_active(shop_id, 'hour')
        for page in pages:
            hour_from = page.get('hour_from')
            hour_to = page.get('hour_to')
            photo = page.get('photo')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if photo and len(photo) > 0:
                photo_conv = move_file(photo)
                detail = {
                    'photo': photo_conv,
                    'title': title,
                    'content': content,
                    'hour_from': hour_from,
                    'hour_to': hour_to
                }
                list_3.append(detail)

    if step_3 == 'weekday':
        pages = get_splash_page_by_type_active(shop_id, 'weekday')
        for page in pages:
            weekday = page.get('weekday')
            photo = page.get('photo')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if photo and len(photo) > 0:
                photo_conv = move_file(photo)
                detail = {
                    'photo': photo_conv,
                    'title': title,
                    'content': content,
                    'weekday': weekday
                }
                list_3.append(detail)

    if step_3 == 'tags':
        pages = get_splash_page_by_type_active(shop_id, 'tag')
        for page in pages:
            tags = []
            tags = page.get('tag')
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            if list_tags and len(list_tags) > 0:
                if set(tags) < set(list_tags):
                    photo = page.get('photo')
                    if photo and len(photo) > 0:
                        photo_conv = move_file(photo)
                        detail = {
                            'photo': photo_conv,
                            'tag_group': tags,
                            'title': title,
                            'content': content
                        }
                        list_3.append(detail)
            else:
                photo = page.get('photo')
                if photo and len(photo) > 0:
                    photo_conv = move_file(photo)
                    detail = {
                        'photo': photo_conv,
                        'tag_group': tags,
                        'title': title,
                        'content': content
                    }
                    list_3.append(detail)

    if step_3 == 'loyal':
        pages = get_splash_page_by_type_active(shop_id, 'loyal')
        for page in pages:
            min_visit = 0
            max_visit = 0
            loyal_min = page.get('loyal_count')
            if not loyal_min:
                loyal_min = 0
            loyal_max = page.get('loyal_count_max')
            if not loyal_max:
                loyal_max = 1000
            if min_visit_camp == 0 and max_visit_camp == 0:
                min_visit = loyal_min
                max_visit = loyal_max
            else:
                if min_visit_camp > loyal_min:
                    min_visit = min_visit_camp
                else:
                    min_visit = loyal_min
                if max_visit_camp > loyal_max:
                    max_visit = loyal_max
                else:
                    max_visit = max_visit_camp
            title = page.get('title')
            if not title:
                title = ''
            content = page.get('content')
            if not content:
                content = ''
            photo = page.get('photo')
            if photo:
                photo_conv = move_file(photo)
                if min_visit == 0 and max_visit == 0:
                    detail = {
                        'photo': photo_conv,
                        'min_visit': min_visit,
                        'max_visit': max_visit,
                        'title': title,
                        'content': content
                    }
                    list_3.append(detail)
                elif min_visit != 0 and max_visit != 0 and min_visit <= max_visit:
                    detail = {
                        'photo': photo_conv,
                        'min_visit': min_visit,
                        'max_visit': max_visit,
                        'title': title,
                        'content': content
                    }
                    list_3.append(detail)
                else:
                    pass
    for detail_1 in list_1:
        for detail_2 in list_2:
            for detail_3 in list_3:
                new_step_1 = '0'
                new_step_2 = '0'
                new_step_3 = '0'
                new_step_4 = 'connect_success'

                name_new_cus_camp = 'Chiến dịch khách hàng mới'
                if campaign_type != 'register':
                    name_new_cus_camp = 'Chưa đặt tên'
                info = {
                    'shop_id': shop_id,
                    'type': campaign_type,
                    'step_1': new_step_1,
                    'step_2': new_step_2,
                    'step_3': new_step_3,
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
                        'convert_min_hour': 0,
                        'convert_max_hour': 23.5,
                        'timestamp_start_event': 0,
                        'timestamp_end_event': 0
                    },
                    'create_at': time.time(),
                    'update_at': time.time(),
                    'status': True,
                    'is_birthday': False,
                    'name': name_new_cus_camp
                }
                new_camp_id = DATABASE.campaigns.insert(info)

                connect_success = shop.get('connect_success')
                if not connect_success:
                    connect_success = {
                        'content_connect': '',
                        'connect_button': '',
                        'auto_popup': '',
                        'display_coupon': False,
                        'display_coupon_txt': '',
                        'hotspot_method': 'default',
                        'default_code': ''}
                connect_success['redirect_type'] = 'website'
                connect_success['auto_website'] = connect_success.get('auto_popup')
                connect_success['auto_popup_ios'] = ''
                connect_success['auto_popup_android'] = ''
                connect_success['auto_facebook_page'] = ''
                connect_success['auto_popup_zalo'] = ''
                connect_success['auto_popup_insta'] = ''
                connect_success['auto_facebook_mess'] = ''
                detail_step_4 = {
                    'camp_id': new_camp_id,
                    'type_page': 'connect_success',
                    'shop_id': shop_id,
                    'step': '4',
                    'details': connect_success
                }
                DATABASE.details_step_campaign.insert(detail_step_4)

                is_birthday = False
                min_visit = ''
                max_visit = ''
                weekday_sun = True
                weekday_mon = True
                weekday_tue = True
                weekday_wed = True
                weekday_thu = True
                weekday_fri = True
                weekday_sat = True
                convert_min_hour = 0
                convert_max_hour = 23.5
                min_hour = '00:00',
                max_hour = '23:30',
                tags_group_customer = []

                # step 1
                if step_1 == 'register' or step_1 == 'plus_register' or step_1 == 'survey' or step_1 == 'spin' or step_1 == 'default':
                    if step_1 == 'register' or step_1 == 'plus_register':
                        new_step_1 = "collect"
                    elif step_1 == 'default':
                        new_step_1 = "slides"
                    else:
                        new_step_1 = step_1
                    detail_step = {
                        'camp_id': new_camp_id,
                        'type_page': new_step_1,
                        'shop_id': shop_id,
                        'step': '1',
                        'details': detail_1
                    }
                    DATABASE.details_step_campaign.insert(detail_step)
                elif step_1 != '0':
                    if detail_1 != {} and step_1 == 'birthday':
                        is_birthday = True
                    elif detail_1 != {} and step_1 == 'loyal':
                        min_visit = detail_1.get('min_visit')
                        max_visit = detail_1.get('max_visit')
                        if min_visit == 0 or max_visit == 0:
                            min_visit = ''
                            max_visit = ''
                    elif detail_1 != {} and step_1 == 'hour':
                        hour_from = detail_1.get('hour_from')
                        hour_to = detail_1.get('hour_to')
                        split_hour_from = hour_from.split(':')
                        split_hour_to = hour_to.split(':')
                        if split_hour_from[1] != '00':
                            min_hour = split_hour_from[0] + ':30'
                            convert_min_hour = int(split_hour_from[0]) + 0.5
                        else:
                            min_hour = split_hour_from[0] + ':00'
                            convert_min_hour = int(split_hour_from[0])
                        if split_hour_to[1] != '00':
                            max_hour = split_hour_to[0] + ':30'
                            convert_max_hour = int(split_hour_to[0]) + 0.5
                        else:
                            max_hour = split_hour_to[0] + ':00'
                            convert_max_hour = int(split_hour_to[0])

                    elif detail_1 != {} and step_1 == 'weekday':
                        weekday = detail_1.get('weekday')
                        if weekday == 'monday':
                            weekday_sun = False
                            weekday_mon = True
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'tuesday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = True
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'wednesday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = True
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'thursday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = True
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'friday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = True
                            weekday_sat = False
                        if weekday == 'saturday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = True
                        if weekday == 'sunday':
                            weekday_sun = True
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                    elif detail_1 != {} and step_1 == 'tags':
                        tags_group_customer = detail_1.get('tag_group')

                else:
                    pass

                # step 2
                if step_2 == 'register' or step_2 == 'plus_register' or step_2 == 'survey' or step_2 == 'spin' or step_2 == 'default':
                    if step_2 == 'register' or step_2 == 'plus_register':
                        new_step_2 = "collect"
                    elif step_2 == 'default':
                        new_step_2 = "slides"
                    else:
                        new_step_2 = step_2
                    detail_step = {
                        'camp_id': new_camp_id,
                        'type_page': new_step_2,
                        'shop_id': shop_id,
                        'step': '2',
                        'details': detail_2
                    }
                    DATABASE.details_step_campaign.insert(detail_step)
                elif step_2 != '0':
                    if detail_2 != {} and step_2 == 'birthday':
                        is_birthday = True
                    elif detail_2 != {} and step_2 == 'loyal':
                        min_visit = detail_2.get('min_visit')
                        max_visit = detail_2.get('max_visit')
                        if min_visit == 0 or max_visit == 0:
                            min_visit = ''
                            max_visit = ''
                    elif detail_2 != {} and step_2 == 'hour':
                        hour_from = detail_2.get('hour_from')
                        hour_to = detail_2.get('hour_to')
                        split_hour_from = hour_from.split(':')
                        split_hour_to = hour_to.split(':')
                        if split_hour_from[1] != '00':
                            min_hour = split_hour_from[0] + ':30'
                            convert_min_hour = int(split_hour_from[0]) + 0.5
                        else:
                            min_hour = split_hour_from[0] + ':00'
                            convert_min_hour = int(split_hour_from[0])
                        if split_hour_to[1] != '00':
                            max_hour = split_hour_to[0] + ':30'
                            convert_max_hour = int(split_hour_to[0]) + 0.5
                        else:
                            max_hour = split_hour_to[0] + ':00'
                            convert_max_hour = int(split_hour_to[0])

                    elif detail_2 != {} and step_2 == 'weekday':
                        weekday = detail_2.get('weekday')
                        if weekday == 'monday':
                            weekday_sun = False
                            weekday_mon = True
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'tuesday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = True
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'wednesday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = True
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'thursday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = True
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'friday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = True
                            weekday_sat = False
                        if weekday == 'saturday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = True
                        if weekday == 'sunday':
                            weekday_sun = True
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                    elif detail_2 != {} and step_2 == 'tags':
                        tags_group_customer = detail_2.get('tag_group')

                else:
                    pass

                # step 3
                if step_3 == 'register' or step_3 == 'plus_register' or step_3 == 'survey' or step_3 == 'spin' or step_3 == 'default':
                    if step_3 == 'register' or step_3 == 'plus_register':
                        new_step_3 = "collect"
                    elif step_3 == 'default':
                        new_step_3 = "slides"
                    else:
                        new_step_3 = step_3
                    detail_step = {
                        'camp_id': new_camp_id,
                        'type_page': new_step_3,
                        'shop_id': shop_id,
                        'step': '3',
                        'details': detail_3
                    }
                    DATABASE.details_step_campaign.insert(detail_step)
                elif step_3 != '0':
                    if detail_3 != {} and step_3 == 'birthday':
                        is_birthday = True
                    elif detail_3 != {} and step_3 == 'loyal':
                        min_visit = detail_3.get('min_visit')
                        max_visit = detail_3.get('max_visit')
                        if min_visit == 0 or max_visit == 0:
                            min_visit = ''
                            max_visit = ''
                    elif detail_3 != {} and step_3 == 'hour':
                        hour_from = detail_3.get('hour_from')
                        hour_to = detail_3.get('hour_to')
                        split_hour_from = hour_from.split(':')
                        split_hour_to = hour_to.split(':')
                        if split_hour_from[1] != '00':
                            min_hour = split_hour_from[0] + ':30'
                            convert_min_hour = int(split_hour_from[0]) + 0.5
                        else:
                            min_hour = split_hour_from[0] + ':00'
                            convert_min_hour = int(split_hour_from[0])
                        if split_hour_to[1] != '00':
                            max_hour = split_hour_to[0] + ':30'
                            convert_max_hour = int(split_hour_to[0]) + 0.5
                        else:
                            max_hour = split_hour_to[0] + ':00'
                            convert_max_hour = int(split_hour_to[0])

                    elif detail_3 != {} and step_3 == 'weekday':
                        weekday = detail_3.get('weekday')
                        if weekday == 'monday':
                            weekday_sun = False
                            weekday_mon = True
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'tuesday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = True
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'wednesday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = True
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'thursday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = True
                            weekday_fri = False
                            weekday_sat = False
                        if weekday == 'friday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = True
                            weekday_sat = False
                        if weekday == 'saturday':
                            weekday_sun = False
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = True
                        if weekday == 'sunday':
                            weekday_sun = True
                            weekday_mon = False
                            weekday_tue = False
                            weekday_wed = False
                            weekday_thu = False
                            weekday_fri = False
                            weekday_sat = False
                    elif detail_3 != {} and step_3 == 'tags':
                        tags_group_customer = detail_3.get('tag_group')

                else:
                    pass
                step = 0
                if 'birthday' in old_steps:
                    step = old_steps.index('birthday') + 1
                elif 'loyal' in old_steps:
                    step = old_steps.index('loyal') + 1
                elif 'tags' in old_steps:
                    step = old_steps.index('tags') + 1
                elif 'hour' in old_steps:
                    step = old_steps.index('hour') + 1
                elif 'weekday' in old_steps:
                    step = old_steps.index('weekday') + 1
                if step != 0:
                    details = {}
                    if step == 1:
                        new_step_1 = 'image'
                        details = {
                            'photo': detail_1.get('photo'),
                            'title': detail_1.get('title'),
                            'content': detail_1.get('content')
                        }
                    elif step == 2:
                        new_step_2 = 'image'
                        details = {
                            'photo': detail_2.get('photo'),
                            'title': detail_2.get('title'),
                            'content': detail_2.get('content')
                        }
                    elif step == 3:
                        new_step_3 = 'image'
                        details = {
                            'photo': detail_3.get('photo'),
                            'title': detail_3.get('title'),
                            'content': detail_3.get('content')
                        }
                    detail_step = {
                        'camp_id': new_camp_id,
                        'type_page': 'image',
                        'shop_id': shop_id,
                        'step': str(step),
                        'details': details
                    }
                    DATABASE.details_step_campaign.insert(detail_step)
                if str(min_visit) == 'None':
                    min_visit = ''
                if str(max_visit) == 'None':
                    max_visit = ''
                DATABASE.campaigns.update({'_id': new_camp_id}, {'$set': {'step_1': new_step_1,
                                                                          'step_2': new_step_2,
                                                                          'step_3': new_step_3,
                                                                          'is_birthday': is_birthday,
                                                                          'group_customer.min_visit': str(min_visit),
                                                                          'group_customer.max_visit': str(max_visit),
                                                                          'group_customer.weekday_mon': weekday_mon,
                                                                          'group_customer.weekday_tue': weekday_tue,
                                                                          'group_customer.weekday_wed': weekday_wed,
                                                                          'group_customer.weekday_thu': weekday_thu,
                                                                          'group_customer.weekday_fri': weekday_fri,
                                                                          'group_customer.weekday_sat': weekday_sat,
                                                                          'group_customer.weekday_sun': weekday_sun,
                                                                          'group_customer.convert_min_hour': convert_min_hour,
                                                                          'group_customer.convert_max_hour': convert_max_hour,
                                                                          'group_customer.min_hour': min_hour,
                                                                          'group_customer.max_hour': max_hour,
                                                                          'group_customer.tags_group_customer': tags_group_customer}})
                DATABASE.shop.update({'_id': shop_id}, {'$set': {'new_camp': True}})


def remove_camp(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.campaigns.remove({'shop_id': shop_id})
    DATABASE.details_step_campaign.remove({'shop_id': shop_id})


camps = DATABASE.hotspot_campaign.find({'campaign_type': 'register',
                                        '$or': [
                                            {'step_1': {'$in': ['promotion', 'hour', 'tags', 'weekday']}},
                                            {'step_2': {'$in': ['promotion', 'hour', 'tags', 'weekday']}},
                                            {'step_3': {'$in': ['promotion', 'hour', 'tags', 'weekday']}},

                                        ]})

# list_shop = []
# for camp in camps:
#     shop_id = camp.get('shop_id')
#     if not isinstance(shop_id, ObjectId):
#         shop_id = ObjectId(shop_id)
#     list_shop.append(shop_id)
# shops = DATABASE.shop.find({})
# for shop in shops:
#     print (shop.get('name'))
#     logo = ''
#     background = ''
#     new_logo = ''
#     new_background = ''
#     shop_id = shop.get('_id')
    # logo = shop.get('logo')
    # if logo and len(logo) > 0 and len(logo) != 12:
    #     new_logo = move_file(logo)
    # else:
    #     new_logo = logo
    # background = shop.get('background')
    # print (background)
    # if background and len(background) > 0 and len(background) != 12:
    #     new_background = move_file(background)
    # else:
    #     new_background = background
    # DATABASE.shop.update({'_id': shop_id}, {'$set': {'logo': new_logo, 'background': new_background}})

    # if shop_id not in list_shop:
    #     print (shop_id)
    #     remove_camp(shop_id)
    #     old_camps = DATABASE.hotspot_campaign.find({'shop_id': shop_id, 'status': True})
    #     if old_camps:
    #         for camp in old_camps:
    #             id_camp = camp.get('_id')
    #             convert_campaign(id_camp)

# remove_camp('5e565128aba586894e988e59')
# convert_campaign('5f0ec4b32c05fd73f6ac5940')
