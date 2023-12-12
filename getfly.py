# coding=utf-8
import requests
import json
import api
import pymongo
from bson import ObjectId
import datetime


def get_customer(base_url, api_key):
    '''Lay danh sach khach hang hoac tim kiem khach hang.
    Params chi tiet tai: https://developer.getfly.vn/#danh-s-ch
    Return: JSON
    '''
    url = base_url + '/api/v3/accounts/'
    headers = {'X-API-KEY': api_key}
    result = requests.get(url, headers=headers)
    # result = str(result).encode("utf-8")
    return json.loads(result.text).get('records')


def create_customer(base_url, api_key, **kwargs):
    '''Tao moi mot khach hang.
    '''
    url = base_url + '/api/v3/account/'
    headers = {'X-API-KEY': api_key,
               'Content-Type': 'application/json'}
    data = {
        "account": {
            "account_name": "",
            "phone_office": "",
            "email": "",
            "gender": 0,
            "billing_address_street": "",
            "birthday": "14/12/1984",
            "account_type": 1,
            "industry": "",
            "country_id": 1,
            "province_id": 1,
            "district_id": 1
        }
    }
    for key, value in kwargs.items():
        if key in ['account_name', 'phone_office', 'email', 'gender', 'billing_address_street', 'birthday']:
            value = str(value)
        else:
            value = int(value)
        data['account'][key] = value
    data = json.dumps(data)
    result = requests.post(url, data=data, headers=headers)
    result = result.json()
    print data
    return result


def get_customer_by_last_sync(base_url, api_key, last_sync):
    ''' Lay danh sach khach hang tu lan cuoi cung update den hien tai'''
    service_url = 'api/v3/accounts/sync'
    url = base_url + service_url
    headers = {'X-API-KEY': api_key,
               'Content-Type': 'application/json'}
    params = {'last_sync': last_sync}
    result = requests.get(url, params=params, headers=headers)
    result = result.json()['data']
    return result


def sync_nextify_to_getfly(status, base_url, api_key, merchant_id):
    '''Ham dong bo du lieu tu nextify den getfly.
    Lay tat ca du lieu cua merchant truyen vao getfly.
    Params:
        base_url, api_key:
    '''
    # Danh sach sdt va email da ton tai tren getfly
    if status == 'True':
        try:
            sync_info = api.DATABASE.app_synchronized.find_one(
                {'merchant_id': ObjectId(merchant_id), 'type_pos': 'getfly'})
            last_user_timestamp = sync_info['settings.last_user_timestamp']
        except:
            last_user_timestamp = None

        max_last_visit = api.DATABASE.customers.find_one({'merchant_id': ObjectId(merchant_id)},
                                                         sort=[("last_visit", pymongo.DESCENDING)]).get(
            'last_visit')
        #  Tim tat ca customer tu customer cuoi duoc dong bo den hien tai
        if last_user_timestamp:
            crm_customer_cursor = api.DATABASE.customers.find(
                {'last_visit': {'$gt': last_user_timestamp, '$lte': max_last_visit},
                 'merchant_id': ObjectId(merchant_id), 'type_pos': 'getfly'})
        else:
            crm_customer_cursor = api.DATABASE.customers.find({'merchant_id': ObjectId(merchant_id)},
                                                                       sort=[("last_visit", pymongo.ASCENDING)])
        count = 0
        for value in crm_customer_cursor:
            # print value
            # validate phone & email
            phone_office = None
            email = None
            try:
                phone_office = str(value.get('user')['phone'])
            except:
                pass

            if not phone_office or phone_office == 'None':
                phone_office = ''
            try:
                email = str(value.get('user')['email'])
            except:
                email = None

            if not email or email == 'None':
                email = ''
            if phone_office == '' and email == '':
                continue
            account_name = ''
            # Name
            if 'name' in value.get('user').keys():
                account_name = value.get('user')['name']
                try:
                    account_name = str(account_name).encode("utf-8").strip()
                except:
                    account_name = ''
            # validate gender:
            gender = 0
            try:
                gender = value["user"]["gender"].encode("utf-8")
                if gender == '1':
                    gender = 1
                elif gender == '2':
                    gender = 2
                else:
                    gender = 0
            except:
                gender = 0
            birthday = ''
            # validate birhday
            try:
                birthday = str(value.get('user')['birthday'])
            except:
                birthday = None
            if not birthday or birthday == 'None':
                birthday = ''
            # validate address:
            billing_address_street = ''
            try:
                billing_address_street = str(value.get('user')['address'])
            except:
                billing_address_street = None
            if not billing_address_street or billing_address_street == 'None':
                billing_address_street = ''

            if phone_office and len(phone_office) > 0:
                result = create_customer(base_url, api_key, account_name=account_name,
                                         phone_office=phone_office,
                                         email=email,
                                         gender=gender,
                                         billing_address_street=billing_address_street,
                                         birthday=birthday)
                count = count + 1
            elif email and len(email) > 0:
                result = create_customer(base_url, api_key, account_name=account_name,
                                         phone_office=phone_office,
                                         email=email,
                                         gender=gender,
                                         billing_address_street=billing_address_street,
                                         birthday=birthday)
                count = count + 1
            last_user_timestamp = value['last_visit']

            if not last_user_timestamp:
                api.DATABASE.app_synchronized.update_one({'merchant_id ': ObjectId(merchant_id), 'type_pos': 'getfly'}, {
                    "$push": {'settings': {'last_user_timestamp': last_user_timestamp}}})
            else:
                api.DATABASE.app_synchronized.update_one({'merchant_id': ObjectId(merchant_id), 'type_pos': 'getfly'}, {
                    "$set": {'settings': {'last_user_timestamp': last_user_timestamp}}})
