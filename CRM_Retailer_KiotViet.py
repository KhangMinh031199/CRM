#! coding: utf-8
import datetime
import json

import pymongo
import requests
from bson.objectid import ObjectId

import api

sync_pos = api.DATABASE['sync_pos']


def get_access_token(client_id, client_secret):
    scope = 'PublicApi.Access'

    url_get_token = 'https://id.kiotviet.vn/connect/token'
    data = {
        "scopes": scope,
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token = ''
    result = requests.post(
        url_get_token, data=data, headers=headers)
    if result and result.status_code == 200:
        return result
    else:
        return False


def get_branches_kiotviet(retailer, client_id, client_secret):
    token = get_access_token(client_id, client_secret)
    if token:
        access_token = json.loads(token.text)['access_token']
        url = 'https://public.kiotapi.com/branches'
        headers = {
            "Retailer": retailer,
            "Authorization": "Bearer " + str(access_token)
        }
        result = requests.get(url, headers=headers)
        return result
    else:
        return []


# Search customer in KiotViet
def search_customer_by_phone(retailer, phone, client_id, client_secret):
    token = get_access_token(client_id, client_secret)
    ACCESS_TOKEN = json.loads(token.text)['access_token']

    phone = unicode(phone, "utf-8")
    url_customer = 'https://public.kiotapi.com/customers?contactNumber=' + phone

    headers = {
        "Retailer": retailer,
        "Authorization": "Bearer " + str(ACCESS_TOKEN)
    }

    result = requests.get(url_customer, headers=headers)

    list_cus = json.loads(result.text)

    if list_cus['total'] == 0:
        return False
    else:
        return True


def search_customer_by_email(retailer, email, client_id, client_secret):
    token = get_access_token(client_id, client_secret)
    ACCESS_TOKEN = json.loads(token.text)['access_token']

    email = unicode(email, "utf-8")
    url_customer = 'https://public.kiotapi.com/customers?email=' + email

    headers = {
        "Retailer": retailer,
        "Authorization": "Bearer " + str(ACCESS_TOKEN)
    }

    result = requests.get(url_customer, headers=headers)

    list_cus = json.loads(result.text)
    if list_cus['total'] == 0:
        return True
    else:
        return False


# search_customer(retailer)

def add_customer(retailer, client_id, client_secret, kiotviet_id, name, email, gender, contactNumber, birthDate,
                 comment):
    token = get_access_token(client_id, client_secret)
    ACCESS_TOKEN = json.loads(token.text)['access_token']

    url_add = 'https://public.kiotapi.com/customers'
    data = {
        "branchId": kiotviet_id,
        "name": name,
        "contactNumber": contactNumber,
        "email": email,
        "gender": gender,
        "birthDate": birthDate,
        "comment": comment
    }

    headers = {
        "Retailer": retailer,
        "Authorization": "Bearer " + str(ACCESS_TOKEN)
    }

    result = requests.post(
        url_add, data=data, headers=headers)
    if result and result.status_code == 200:
        return result


def get_shop_customer(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return api.DATABASE.customers_location.find({
        'shop_id': shop_id
    })


def sync_customers(status, retailer, client_id, client_secret, kiotviet_id):
    shop = api.get_shop_by_pos_id(kiotviet_id)
    if shop and status == 'True':
        shop_id = shop.get('_id')
        max_last_visit = api.DATABASE.customers_location.find_one({'shop_id': ObjectId(shop_id)},
                                                                  sort=[("last_visit", pymongo.DESCENDING)]).get(
            'last_visit')
        countt = sync_pos.find({'shop_id': ObjectId(shop_id), 'type_pos': 'retailer_kiotviet'}).count()
        if countt == 0:
            sync_pos.insert_one(
                {'last_sync': max_last_visit, 'type_pos': 'retailer_kiotviet', 'shop_id': ObjectId(shop_id)})
            list_customer = get_shop_customer(shop_id)
            count = 0
            for cus in list_customer:
                count = count + 1
                text = "Number " + str(count)
                user = {}
                phone = None
                email = None
                name = None
                address = None

                try:
                    phone = cus["user"]["phone"]
                    phone = phone.encode("utf-8")
                    user['contactNumber'] = phone
                except:
                    pass

                try:
                    email = cus["user"]["email"]
                    email = email.encode("utf-8")
                    user['email'] = email
                except:
                    pass
                try:
                    name = cus["user"]["name"]
                    name = name.encode("utf-8")
                    user['name'] = name
                except:
                    pass

                try:
                    address = cus["user"]["address"]
                    address = address.encode("utf-8")
                    user['address'] = address
                except:
                    pass

                try:
                    note = cus["user"]["note"]
                    note = note.encode("utf-8")
                    user['comment'] = note
                except:
                    pass

                try:
                    gender = cus["user"]["gender"]
                    gender = gender.encode("utf-8")
                    if gender == '1':
                        user['gender'] = True
                    elif gender == '2':
                        user['gender'] = False
                    else:
                        pass
                except:
                    pass

                try:
                    birth = cus["user"]["birthday"]
                    if len(birth) > 0:
                        dob = datetime.datetime.strptime(birth, "%d-%m-%Y")
                        user['birthDate'] = dob
                except:
                    pass

                if len(user) > 0:
                    email = user.get('email', '')
                    name = user.get('name', '')
                    gender = user.get('gender', '')
                    contactNumber = user.get('contactNumber', '')
                    birthDate = user.get('birthDate', '')
                    comment = user.get('comment', '')

                    if contactNumber and len(contactNumber) > 0 and str(contactNumber) != 'None':
                        if not search_customer_by_phone(retailer, phone, client_id, client_secret):
                            add_customer(retailer, client_id, client_secret, kiotviet_id, name, email, gender,
                                         contactNumber, birthDate, comment)
                    elif email and len(email) > 0 and str(email) != 'None':
                        if not search_customer_by_email(retailer, email, client_id, client_secret):
                            add_customer(retailer, client_id, client_secret, kiotviet_id, name, email, gender,
                                         contactNumber, birthDate, comment)
        if countt != 0:
            pre_last_sync = sync_pos.find_one({'shop_id': ObjectId(shop_id), 'type_pos': 'retailer_kiotviet'}).get(
                'last_sync')
            sync_pos.update_one({'shop_id': ObjectId(shop_id), 'type_pos': 'retailer_kiotviet'},
                                {"$set": {'last_sync': max_last_visit}})
            if pre_last_sync < max_last_visit:
                list_sync_customer = api.DATABASE.customers_location.find(
                    {'last_visit': {'$gt': pre_last_sync, '$lte': max_last_visit}, 'shop_id': ObjectId(shop_id),
                     })
                count = 0
                for cus in list_sync_customer:
                    count = count + 1
                    text = "Number " + str(count)

                    user = {}
                    phone = None
                    try:
                        phone = cus["user"]["phone"]
                        phone = phone.encode("utf-8")
                        user['contactNumber'] = phone
                    except:
                        pass

                    try:
                        email = cus["user"]["email"]
                        email = email.encode("utf-8")
                        user['email'] = email
                    except:
                        pass

                    name = cus["user"]["name"]
                    name = name.encode("utf-8")
                    user['name'] = name

                    try:
                        address = cus["user"]["address"]
                        address = address.encode("utf-8")
                        user['address'] = address
                    except:
                        pass

                    try:
                        note = cus["user"]["note"]
                        note = note.encode("utf-8")
                        user['comment'] = note
                    except:
                        pass

                    try:
                        gender = cus["user"]["gender"]
                        gender = gender.encode("utf-8")
                        if gender == '1':
                            user['gender'] = True
                        elif gender == '2':
                            user['gender'] = False
                        else:
                            pass
                    except:
                        pass

                    try:
                        birth = cus["user"]["birthday"]
                        if len(birth) > 0:
                            dob = datetime.datetime.strptime(birth, "%d-%m-%Y")
                            user['birthDate'] = dob
                    except:
                        pass

                    if len(user) > 0:
                        email = user.get('email', '')
                        name = user.get('name', '')
                        gender = user.get('gender', '')
                        contactNumber = user.get('contactNumber', '')
                        birthDate = user.get('birthDate', '')
                        comment = user.get('comment', '')

                        if contactNumber and len(contactNumber) > 0 and str(contactNumber) != 'None':
                            if not search_customer_by_phone(retailer, phone, client_id, client_secret):
                                add_customer(retailer, client_id, client_secret, kiotviet_id, name, email, gender,
                                             contactNumber, birthDate, comment)
                        elif email and len(email) > 0 and str(email) != 'None':
                            if not search_customer_by_email(retailer, email, client_id, client_secret):
                                add_customer(retailer, client_id, client_secret, kiotviet_id, name, email, gender,
                                             contactNumber, birthDate, comment)

# status = 'True'
# print sync_customers(status, retailer, client_id, client_secret, shop_id, kiotviet_id)
