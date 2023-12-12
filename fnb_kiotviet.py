# coding=utf-8
import json
import time
from datetime import datetime

import pymongo
import requests
from bson import ObjectId

import api
import handle_customers
import save_customers

sync_pos = api.DATABASE['sync_pos']


def access_token(client_id, client_secret):
    '''
    Lay token de truy cap vao API cua kiotViet
    Return:
        token (string): Dinh dang "Bearer+token"
    '''
    scope = 'PublicApi.Access.FNB'
    url_get_token = 'https://id.kiotviet.vn/connect/token'
    data = {
        "scopes": scope,
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    result = requests.post(url_get_token, data=data, headers=headers)
    ACCESS_TOKEN = json.loads(result.text)
    token = str('Bearer ' + ACCESS_TOKEN['access_token'])
    return token


def get_branches_kiotviet(retailer, client_id, client_secret):
    token = access_token(client_id, client_secret)
    url = 'https://publicfnb.kiotapi.com/branches'
    headers = {
        "Retailer": retailer,
        "Authorization": token
    }
    result = requests.get(url, headers=headers)
    return result


# print access_token(client_id, client_secret)

def search_customer_by_phone(retailer, phone, client_id, client_secret):
    token = access_token(client_id, client_secret)

    phone = unicode(phone, "utf-8")
    url_customer = 'https://publicfnb.kiotapi.com/customers?contactNumber=' + phone

    headers = {
        "Retailer": retailer,
        "Authorization": str(token)
    }

    result = requests.get(url_customer, headers=headers)

    list_cus = json.loads(result.text)

    if list_cus['total'] == 0:
        return False
    else:
        return True


def search_customer_by_email(retailer, email, client_id, client_secret):
    token = access_token(client_id, client_secret)

    email = unicode(email, "utf-8")
    url_customer = 'https://publicfnb.kiotapi.com/customers?email=' + email

    headers = {
        "Retailer": retailer,
        "Authorization": str(token)
    }

    result = requests.get(url_customer, headers=headers)

    list_cus = json.loads(result.text)
    if list_cus['total'] == 0:
        return True
    else:
        return False


def get_customers(retailer, client_id, client_secret):
    ''' 
    Ham lay danh sach tat ca cac customer.
    Method: GET
    Args: Token
    Return: List tat cac customer thuoc merchant
    '''
    page_size = 100
    currentItem = 0
    token = access_token(client_id, client_secret)
    url = 'https://publicfnb.kiotapi.com/customers'
    params = {
        "pageSize": page_size,
        "currentitem": currentItem
    }
    headers = {
        "Retailer": retailer,
        "Authorization": token
    }
    response = requests.get(url, headers=headers, params=params)
    response = json.loads(response.text)
    page_number = response['total'] // 100
    # print page_number

    if page_number > 1:
        result = []
        for i in range(0, page_number):
            currentItem = currentItem + 100
            params = {
                "pageSize": page_size,
                "currentItem": currentItem
            }
            r = requests.get(url, headers=headers, params=params)
            r = json.loads(r.text)
            for item in r['data']:
                result.append(item)
        return result
    else:
        return response['data']


def get_shop_customer(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return api.DATABASE.customers_location.find({
        'shop_id': shop_id
    })


# print get_customers(retailer, client_id, client_secret)
def add_customer(retailer, client_id, client_secret, kiotviet_id, name, email, gender, contactNumber, birthDate,
                 comment):
    token = access_token(client_id, client_secret)

    url_add = 'https://publicfnb.kiotapi.com/customers'
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
        "Authorization": str(token)
    }

    result = requests.post(
        url_add, data=data, headers=headers)
    if result and result.status_code == 200:
        return result


def sync_to_crm(status, retailer, client_id, client_secret, merchant_id, shop_id):
    '''
    Day du lieu tu kiotviet den crm
    Args:
        status: Nut bat tat dong bo du lieu.
        retailer: Ten merchant.
        client_id % client_secret: Thong tin khach hang da khai bao.
        merchant_id:
        shop_id
    '''
    if status:
        customers = get_customers(retailer, client_id, client_secret)
        count = 0
        for cus in customers:
            count = count + 1
            user = {}

            try:
                last_update = cus['modifiedDate']
            except:
                last_update = cus['createdDate']

            last_update = last_update.encode("utf-8")
            last_update = last_update[:last_update.find(".")]
            last_update = datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%S")
            format_last_update = "%Y-%m-%d %H:%M:%S"
            last_update = last_update.strftime(format_last_update)
            last_update = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")

            # Phone
            try:
                phone = cus['contactNumber']
                phone = phone.encode("utf-8")
                user['phone'] = phone
            except:
                pass
            # Email
            try:
                email = cus['email']
                email = email.encode("utf-8")
                user['email'] = email
            except:
                pass

            # Name Str
            name = cus['name']
            name = name.encode("utf-8")
            user['name'] = name
            # Address Str
            try:
                address = cus['address']
                address = address.encode("utf-8")
                user['address'] = address
            except:
                pass

            # Comment Str
            try:
                note = cus['comment']
                note = note.encode("utf-8")
                user['note'] = note
            except:
                pass

            # Gender Str
            try:
                gender = cus['gender']
                if gender == True:
                    user['gender'] = '1'
                elif gender == False:
                    user['gender'] = '2'
                else:
                    user['gender'] = '0'
            except:
                pass
            # birthData Str
            try:
                dob = cus['birthDate']
                dob = dob.encode("utf-8")
                dob = dob[:dob.find(".")]
                dob = datetime.strptime(dob, "%Y-%m-%dT%H:%M:%S")
                format_dob = "%Y-%m-%d"
                dob = dob.strftime(format_dob)
                dob = str(dob).split('-')

                if len(dob) == 3:
                    b_day = str(dob[2])
                    b_month = str(dob[1])
                    birth = ''
                    if len(str(b_day)) > 0 and len(str(b_month)) > 0 and \
                            str(b_day).isdigit() \
                            and \
                            str(b_month).isdigit():
                        birth = '{}-{}'.format(str(b_month).lstrip("0"), str(b_day).lstrip("0"))
                        user['birth'] = birth

                        b_year = str(dob[0])
                        user['year_birthday'] = str(b_year)
            except:
                pass

            # Get user id
            if len(user) > 0:
                email = user.get('email', '')
                name = user.get('name', '')
                gender = user.get('gender' '')
                phone = user.get('phone', '')
                birthday = user.get('birth', '')
                note = user.get('note', '')
                address = user.get('address', '')
                year_birthday = user.get('year_birthday', '')
                user_id = None

                if phone and len(phone) > 0 and str(phone) != 'None':
                    phone = str(phone).lower()
                    # If phone exist, get user_id
                    user_by_phone = handle_customers.get_user_merchant_by_phone(merchant_id, phone)
                    if user_by_phone:
                        user_id = user_by_phone.get('user_id')
                elif email and len(email) > 0 and str(email) != 'None':
                    email = email.lower()
                    # If email exist, get user_id
                    user_by_email = handle_customers.get_user_merchant_by_email(merchant_id, email)
                    if user_by_email:
                        user_id = user_by_email.get('user_id')

                if user_id:

                    visit_log = \
                        api.DATABASE.visit_log.find_one({'user_id': ObjectId(user_id)}, sort=[("timestamp_date", -1)])[
                            "timestamp_date"]
                    visit_log = str(visit_log)
                    visit_log = visit_log[:visit_log.find(".")]
                    visit_log = datetime.strptime(visit_log, "%Y-%m-%d %H:%M:%S")
                    if visit_log < last_update:
                        user = api.get_user_info(user_id=user_id)
                        if user:
                            api.update_user_item(
                                user_id,
                                name=name,
                                phone=phone,
                                gender=gender,
                                birthday=birthday,
                                email=email,
                                year_birthday=year_birthday)
                        else:
                            api.register_with_id(
                                id_user=user_id,
                                name=name,
                                phone=phone,
                                gender=gender,
                                birthday=birthday,
                                email=email,
                                year_birthday=year_birthday, )
                        visit_id = api.save_visit_log(user_id, shop_id, merchant_id)
                        if visit_id:
                            save_customers.handle_customer_update(visit_id)
                        # else:
                        #   save_customers.update_customers(merchant_id, shop_id, user_id, time.time())
                    elif visit_log > last_update:
                        pass
                    else:
                        user = api.get_user_info(user_id=user_id)
                        if user:
                            api.update_user_item(
                                user_id,
                                name=name,
                                phone=phone,
                                gender=gender,
                                birthday=birthday,
                                email=email,
                                year_birthday=year_birthday, )
                        else:
                            api.register_with_id(
                                id_user=user_id,
                                name=name,
                                phone=phone,
                                gender=gender,
                                birthday=birthday,
                                email=email,
                                year_birthday=year_birthday)
                        visit_id = api.save_visit_log(user_id, shop_id, merchant_id)
                        if visit_id:
                            save_customers.handle_customer_update(visit_id)
                        else:
                            save_customers.update_customers(merchant_id, shop_id, user_id, time.time())
                else:
                    user_id = api.register(
                        name=name,
                        phone=phone,
                        gender=gender,
                        birthday=birthday,
                        email=email,
                        year_birthday=year_birthday
                    )
                    visit_id = api.save_visit_log(user_id, shop_id, merchant_id)
                    if visit_id:
                        save_customers.handle_customer_update(visit_id)
                    else:
                        save_customers.update_customers(merchant_id, shop_id, user_id, time.time())


def sycn_to_kiotviet(status, retailer, client_id, client_secret, kiotviet_id):
    ''' Ham dong bo den kiotviet. Lay tat ca du lieu cua shop truyen vao kiotviet
        Args:
            status: Nut bat tat dong bo du lieu.
            retailer: Ten merchant.
            client_id % client_secret: Thong tin khach hang da khai bao.
            shop_id: Id cua shop dang dong bo
    '''
    shop = api.get_shop_by_pos_id(kiotviet_id)
    if shop and status == 'True':
        shop_id = shop.get('_id')
        max_last_visit = api.DATABASE.customers_location.find_one({'shop_id': ObjectId(shop_id)},
                                                                  sort=[("last_visit", pymongo.DESCENDING)]).get(
            'last_visit')
        countt = sync_pos.find({'shop_id': ObjectId(shop_id), 'type_pos': 'fnb_kiotviet'}).count()
        if countt == 0:
            sync_pos.insert_one(
                {'last_sync': max_last_visit, 'type_pos': 'fnb_kiotviet', 'shop_id': ObjectId(shop_id), })
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
                        dob = datetime.strptime(birth, "%d-%m-%Y")
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
            pre_last_sync = sync_pos.find_one({'shop_id': ObjectId(shop_id), 'type_pos': 'fnb_kiotviet'}).get(
                'last_sync')
            sync_pos.update_one({'shop_id': ObjectId(shop_id), 'type_pos': 'fnb_kiotviet'},
                                {"$set": {'last_sync': max_last_visit}})
            if pre_last_sync <= max_last_visit:
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
                            dob = datetime.strptime(birth, "%d-%m-%Y")
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

# print sycn_to_kiotviet(status, merchant_id, retailer, client_id, client_secret)
