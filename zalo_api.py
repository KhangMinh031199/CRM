#! coding: utf-8
import time
import requests
import urllib
from hashlib import sha256
import json
import api
from bson.objectid import ObjectId
from datetime import date

def gen_mac_token_follow_info(page_account, page_key, uid):
    timestamp = time.time()
    timestamp = str(timestamp).split('.')[0]
    gen_mac = sha256(str(page_account) + str(uid) + str(timestamp) + page_key)
    hex_dig = gen_mac.hexdigest()
    return hex_dig


def gen_mac_token_send_text(page_account, page_key, data):
    timestamp = time.time()
    timestamp = str(timestamp).split('.')[0]
    gen_mac = sha256(str(page_account) + str(data) + str(timestamp) + page_key)
    hex_dig = gen_mac.hexdigest()
    return hex_dig

def get_zalo_oa_profile():
    pass


def get_zalo_oa_follow_info(zalo_oa_id, zalo_oa_key, uid):
    timestamp = time.time()
    timestamp = str(timestamp).split('.')[0]
    data_get_profile = {
        'oaid': zalo_oa_id,
        'uid': uid,
        'timestamp': timestamp,
        'mac': gen_mac_token_follow_info(zalo_oa_id, zalo_oa_key, uid)
    }
    r = requests.get('https://openapi.zaloapp.com/oa/v1/getprofile', params=urllib.urlencode(data_get_profile))
    r_content = r.content
    
    json_content = json.loads(r_content)
    error_code = json_content["errorCode"]
    if error_code not in [0, 1]:
        if error_code == int('-201'):
            return '201'
        else:
            return False
    else:
        return json_content['data']

def zalo_oa_send_mess(zalo_oa_id, zalo_oa_key, uid, message):
    data = {
        'uid': long(uid),
        'message': message
    }
    timestamp = time.time()
    timestamp = str(timestamp).split('.')[0]
    data = json.dumps(data)
    data_post = {
        'oaid': zalo_oa_id,
        'data' : data,
        'timestamp': timestamp,
        'mac': gen_mac_token_send_text(zalo_oa_id, zalo_oa_key, data)
    }
    r = requests.post('https://openapi.zaloapp.com/oa/v1/sendmessage/text', data=data_post)
    return r.content


def update_user_with_zalo(user, zalo_oa_id, zalo_oa_key, shop_id):
    user_phone = user.get('phone', '')
    user_id = user.get('_id')
    if user_phone and len(user_phone) > 0 and str(user_phone) != 'None' and user_phone.isdigit():

        phone = str(user_phone).lstrip('0')
        phone = '84' + phone
        user_profile = get_zalo_oa_follow_info(zalo_oa_id, zalo_oa_key, int(phone))
        shop = api.get_shop_info(shop_id=shop_id)

        if user_profile and user_profile != '201':
            gender = user_profile.get('userGender')
            user_id_zalo = user_profile.get('userId')
            user_id_zalo_app = user_profile.get('userIdByApp')
            avatar = user_profile.get('avatars').get('240')
            full_name = user_profile.get('displayName')
            int_bday = user_profile.get('birthDate')
            birthday = date.fromtimestamp(int(int_bday)).strftime('%m-%d')
            exits_name = user.get('name')

            # if not exits_name or exits_name == 'None' or len(exits_name) == 0:
            #     api.update_user_by_id(user_id, name=full_name)
            # exists_birthday = user.get('birthday')
            # if not exists_birthday or len(exists_birthday) == 0:
            #     api.update_user_by_id(user_id, birthday=birthday)
            # api.update_user_by_id(user_id, gender=gender, avatar=avatar, user_id_zalo=user_id_zalo)
            # merchant_id = shop.get('merchant_id')
            # api.zalo_user_oa(user_id, shop_id, user_id_zalo, user_id_zalo_app, zalo_oa_id)


def update_zalo_sync_process(shop_id, status):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    is_sync = api.DATABASE.shop_syn_zalo.find_one({'shop_id': shop_id})
    if is_sync:
        api.DATABASE.shop_syn_zalo.update({'shop_id': shop_id}, {'$set': {
            'when': time.time(),
            'status': status
        }})
    else:
        api.DATABASE.shop_syn_zalo.insert({
            'shop_id': shop_id,
            'when': time.time(),
            'status': status
        })

def status_zalo_sync_process(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return api.DATABASE.shop_syn_zalo.find_one({'shop_id': shop_id})

