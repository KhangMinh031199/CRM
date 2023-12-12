#! coding: utf-8
import requests
import json
from mongo_connect import *
from bson import ObjectId

MONGODB = mongodb_create()
DATABASE = MONGODB[settings.MONGODB_NAME]
customers = DATABASE['customers']
sync_pos = DATABASE['sync_pos']

# access_token = 'JHTHWPCE6OCZBW0PBH9XRRBC6JTR1UWQ'
# pos_parent = 'SAOBANG'
# phone = '84982680997'
# merchant_id = '5cef7c1b57edfc011e95cf04'
# data = {
#     "phone": 842663752776,
#     "name": "Tuyen Pham",
#     "birthday": "25/12/2003",
#     "gender": 1
# }


def add_membership(access_token, pos_parent, data):
    url = 'https://api.foodbook.vn/ipos/ws/xpartner/add_membership?access_token={}&pos_parent={}'.format(access_token, pos_parent)

    return requests.post(url=url, data=json.dumps(data)).text

def get_membership_info_by_phone(access_token, pos_parent, phone):
    url = 'https://api.foodbook.vn/ipos/ws/xpartner/membership_detail?access_token={}&pos_parent={}&user_id={}'.format(access_token, pos_parent, phone)

    return requests.get(url=url).text

# a = get_membership_info_by_phone(access_token, pos_parent, phone)
# print json.loads(a).get('data')


def get_customer_of_merchant(merchant_id):
    return customers.find({'merchant_id': ObjectId(merchant_id)}).sort('last_visit', 1)

def type_ipos_membership(cursor):
    list_customer = [customer for customer in cursor]
    list_membership = []
    for i in range(len(list_customer)):
        name = list_customer[i].get('user').get('name')
        phone = str(list_customer[i].get('user').get('phone')).replace("0", "84", 1)
        birthday = list_customer[i].get('user').get('birthday')
        gender = list_customer[i].get('user').get('gender')
        if gender == '1':
            gender = 1
        elif gender == '2':
            gender = 0
        else:
            gender = -1
        ipos_membership = dict(name=name,
                               phone=phone,
                               birthday=birthday,
                               gender=gender)
        list_membership.append(ipos_membership)

    return list_membership


def sync_next_to_ipos(status, merchant_id, access_token, pos_parent):
    # list membership da sort
    customers_cursor = get_customer_of_merchant(merchant_id)
    list_ipos_member = type_ipos_membership(customers_cursor)

    # sort customers nextify
    customer_sort = customers.find({'merchant_id': ObjectId(merchant_id)}).sort('last_visit', 1)
    customer_sort_list = [cus for cus in customer_sort]

    if status == 'True':
        count = sync_pos.find({'type_pos': 'ipos', 'merchant_id': ObjectId(merchant_id)}).count()
        print count
        if count == 0:
            sync_pos.insert_one({'merchant_id': ObjectId(merchant_id),
                                 'type_pos': 'ipos',
                                 'last_sync': ''})
            last_visit = None
            for i in range(len(list_ipos_member)):
                phone = list_ipos_member[i].get('phone')
                last_visit = customer_sort_list[i].get('last_visit')
                print 'last_visit: {}'.format(last_visit)
                member = get_membership_info_by_phone(access_token, pos_parent, phone)
                if json.loads(member).get('data'):
                    print 'da ton tai {}'.format(phone)
                    print '==='
                else:
                    add_membership(access_token, pos_parent, list_ipos_member[i])
                    print 'day thanh cong {}'.format(phone)
                    print '==='
            sync_pos.update_one({'merchant_id': ObjectId(merchant_id), 'type_pos': 'ipos'},
                                {'$set': {'last_sync': last_visit}})
        else:
            pre_last_sync = sync_pos.find_one({'merchant_id': ObjectId(merchant_id), 'type_pos': 'ipos'}).get(
                'last_sync')
            last_visit = None
            for i in range(len(list_ipos_member)):
                if pre_last_sync < customer_sort_list[i]['last_visit']:
                    phone = list_ipos_member[i].get('phone')
                    last_visit = customer_sort_list[i].get('last_visit')
                    print 'last_visit: {}'.format(last_visit)
                    member = get_membership_info_by_phone(access_token, pos_parent, phone)
                    if json.loads(member).get('data'):
                        print 'da ton tai {}'.format(phone)
                        print '==='
                    else:
                        add_membership(access_token, pos_parent, list_ipos_member[i])
                        print 'day thanh cong {}'.format(phone)
                        print '==='
            sync_pos.update_one({'merchant_id': ObjectId(merchant_id), 'type_pos': 'ipos'},
                                {'$set': {'last_sync': last_visit}})

    return 'Chay xong!'


# status = 'True'
# print sync_next_to_ipos(status, merchant_id, access_token, pos_parent)

