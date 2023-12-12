from bson.objectid import ObjectId
from datetime import datetime
import pytz
import arrow
import time
import api
import handle_customers


def handle_customer_update(visit_id):
    visit_id = str(visit_id)
    if not isinstance(visit_id, ObjectId):
        visit_id = ObjectId(visit_id)
    visit = api.get_visit_by_id(visit_id)
    if visit:
        user_id = visit.get('user_id')
        shop_id = visit.get('shop_id')
        timestamp = visit.get('timestamp')
        shop = api.get_shop_info(shop_id=shop_id)
        user = api.get_user_info(user_id=user_id)
        if shop and user:
            merchant_id = shop.get('merchant_id')
            save_customers(merchant_id, shop_id, user_id, timestamp)


def update_customers(merchant_id, shop_id, user_id, last_visit=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    shops = []
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    user_info = api.get_user_info(user_id=user_id)
    if not user_info:
        user_info = handle_customers.get_user_merchant_by_user_id(merchant_id, user_id)

    visit_count = api.get_user_activity_visit_count(user_id, shops)
    user_tags_details = []
    user_tags = api.get_user_tags(merchant_id, user_id)
    if user_tags:
        user_tag = user_tags.get('tags')
        if len(user_tags) > 0:
            for tag in user_tag:
                tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                if tag_db:
                    user_tags_details.append(tag_db)
    user_info['user_tags_details'] = user_tags_details
    info = {}
    info['merchant_id'] = merchant_id
    info['user_id'] = user_id
    info['user'] = user_info
    info['total_visit'] = visit_count
    if last_visit:
        info['last_visit'] = last_visit
    info['update_at'] = time.time()

    api.DATABASE.customers.update({
        'merchant_id': merchant_id,
        'user_id': user_id
    }, {
        '$set': info
    })

    check_customers_location = api.DATABASE.customers_location.find_one({
        'shop_id': shop_id,
        'user_id': user_id
    })
    visit_count_shop = api.get_user_activity_visit_count(user_id, [ObjectId(shop_id)])
    if not check_customers_location:
        info = {}
        info['shop_id'] = shop_id
        info['user_id'] = user_id
        info['user'] = user_info
        info['total_visit'] = visit_count_shop
        if last_visit:
            info['last_visit'] = last_visit
        info['update_at'] = time.time()
        api.DATABASE.customers_location.insert(info)
    else:
        info = {}
        info['shop_id'] = shop_id
        info['user_id'] = user_id
        info['user'] = user_info
        info['total_visit'] = visit_count_shop
        if last_visit:
            info['last_visit'] = last_visit
        info['update_at'] = time.time()
        api.DATABASE.customers_location.update({
            'shop_id': shop_id,
            'user_id': user_id
        }, {
            '$set': info
        })


def update_customers_merchant(merchant_id, user_id, last_visit=None, id_haravan=None, id_bizfly=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    shops = []
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    info = {}
    user_info = api.get_user_info(user_id=user_id)
    birth = ''
    if user_info:
        birthday = user_info.get('birthday')
        if birthday and len(birthday) > 0:
            split_birth = birthday.split('-')
            birth = '{}-{}'.format(
                str(split_birth[1]).lstrip("0"), str(split_birth[0]).lstrip("0"))
            user_info['birthday'] = birth
    if not user_info:
        user_info = handle_customers.get_user_merchant_by_user_id(merchant_id, user_id)
    visit_count = api.get_user_activity_visit_count(user_id, shops)
    user_tags_details = []
    user_tags = api.get_user_tags(merchant_id, user_id)
    if user_tags:
        user_tag = user_tags.get('tags')
        if len(user_tags) > 0:
            for tag in user_tag:
                tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                if tag_db:
                    user_tags_details.append(tag_db)
    user_info['user_tags_details'] = user_tags_details
    check_customers = api.DATABASE.customers.find_one({
        'merchant_id': merchant_id,
        'user_id': user_id
    })
    info['merchant_id'] = merchant_id
    info['user_id'] = user_id
    info['user'] = user_info
    info['update_at'] = time.time()
    if last_visit:
        info['last_visit'] = last_visit
    if id_haravan:
        info['id_haravan'] = id_haravan
    if id_bizfly:
        info['id_bizfly'] = id_bizfly
    if check_customers:
        info['total_visit'] = visit_count
        api.DATABASE.customers.update({
            'merchant_id': merchant_id,
            'user_id': user_id
        }, {
            '$set': info
        })
    else:
        info['total_visit'] = 0
        api.DATABASE.customers.insert(info)


def update_customers_location(merchant_id, shop_id, user_id, last_visit=None, id_haravan=None, id_bizfly=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_info = api.get_user_info(user_id=user_id)
    birth = ''
    if user_info:
        birthday = user_info.get('birthday')
        if birthday and len(birthday) > 0:
            split_birth = birthday.split('-')
            birth = '{}-{}'.format(
                str(split_birth[1]).lstrip("0"), str(split_birth[0]).lstrip("0"))
            user_info['birthday'] = birth
    if not user_info:
        user_info = handle_customers.get_user_merchant_by_user_id(merchant_id, user_id)
    user_tags_details = []
    user_tags = api.get_user_tags(merchant_id, user_id)
    if user_tags:
        user_tag = user_tags.get('tags')
        if len(user_tags) > 0:
            for tag in user_tag:
                tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                if tag_db:
                    user_tags_details.append(tag_db)
    user_info['user_tags_details'] = user_tags_details
    check_customers_location = api.DATABASE.customers_location.find_one({
        'shop_id': shop_id,
        'user_id': user_id
    })
    visit_count_shop = api.get_user_activity_visit_count(user_id, [ObjectId(shop_id)])
    info = {}
    info['shop_id'] = shop_id
    info['user_id'] = user_id
    info['user'] = user_info
    if last_visit:
        info['last_visit'] = last_visit
    if id_haravan:
        info['id_haravan'] = id_haravan
    if id_bizfly:
        info['id_bizfly'] = id_bizfly
    info['update_at'] = time.time()
    info['total_visit'] = visit_count_shop
    if not check_customers_location:
        api.DATABASE.customers_location.insert(info)
    else:
        api.DATABASE.customers_location.update({
            'shop_id': shop_id,
            'user_id': user_id
        }, {
            '$set': info
        })


def update_customers_zalop(merchant_id, shop_id, user_id, user_id_zalo):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_info = api.get_user_info(user_id=user_id)
    user_tags_details = []
    user_tags = api.get_user_tags(merchant_id, user_id)
    if user_tags:
        user_tag = user_tags.get('tags')
        if len(user_tags) > 0:
            for tag in user_tag:
                tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                if tag_db:
                    user_tags_details.append(tag_db)

    user_info['user_id_zalo'] = user_id_zalo
    user_info['user_tags_details'] = user_tags_details
    api.update_user_by_id(user_id,
                          user_id_zalo=user_id_zalo)
    api.DATABASE.customers.update({
        'merchant_id': merchant_id,
        'user_id': user_id
    }, {
        '$set': {
            'merchant_id': merchant_id,
            'user_id': user_id,
            'user': user_info,
            'update_at': time.time()
        }
    })
    api.DATABASE.customers_location.update({
        'shop_id': shop_id,
        'user_id': user_id
    }, {
        '$set': {
            'shop_id': shop_id,
            'user_id': user_id,
            'user': user_info,
            'update_at': time.time()
        }
    })


def save_customers(merchant_id, shop_id, user_id, last_visit):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_info = api.get_user_info(user_id=user_id)
    if user_info:
        shops = []
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer['_id'])
        user_info['_id'] = str(user_info['_id'])
        user_info['lastvisit'] = last_visit
        birthday = ''
        try:
            if user_info.get('birthday') and len(user_info.get(
                    'birthday')) > 0 and user_info.get('birthday') != 'None':
                birthday_arr = user_info['birthday'].split('-')
                if len(birthday_arr) == 2:
                    birthday = birthday_arr[1].lstrip("0") + '-' + \
                               birthday_arr[0].lstrip("0")
                    if user_info.get('year_birthday') and len(
                            str(user_info.get('year_birthday'))) > 0 \
                            and str(user_info.get('year_birthday')) != 'None':
                        birthday = birthday + '-' + \
                                   str(user_info.get('year_birthday'))
        except:
            pass

        user_info['birthday'] = birthday
        visit_count = api.get_user_activity_visit_count(user_id, shops)
        user_info['visit_count'] = visit_count
        user_tags_details = []
        user_tags = api.get_user_tags(merchant_id, user_id)
        if user_tags:
            user_tag = user_tags.get('tags')
            if len(user_tags) > 0:
                for tag in user_tag:
                    tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                    if tag_db:
                        user_tags_details.append(tag_db)
        user_info['user_tags_details'] = user_tags_details
        ex_customers = api.DATABASE.customers.find_one({
            'merchant_id': merchant_id,
            'user_id': user_id
        })
        if not ex_customers:
            api.DATABASE.customers.insert({
                'merchant_id': merchant_id,
                'user_id': user_id,
                'user': user_info,
                'last_visit': last_visit,
                'total_visit': visit_count,
                'update_at': time.time()
            })
        else:
            api.DATABASE.customers.update({
                'merchant_id': merchant_id,
                'user_id': user_id
            }, {
                '$set': {
                    'merchant_id': merchant_id,
                    'user_id': user_id,
                    'user': user_info,
                    'last_visit': last_visit,
                    'total_visit': visit_count,
                    'update_at': time.time()
                }
            })
        ex_customers_location = api.DATABASE.customers_location.find_one({
            'shop_id': shop_id,
            'user_id': user_id
        })
        if not ex_customers_location:
            api.DATABASE.customers_location.insert({
                'shop_id': shop_id,
                'user_id': user_id,
                'user': user_info,
                'last_visit': last_visit,
                'total_visit': visit_count,
                'update_at': time.time()
            })
        else:
            api.DATABASE.customers_location.update({
                'shop_id': shop_id,
                'user_id': user_id
            }, {
                '$set': {
                    'shop_id': shop_id,
                    'user_id': user_id,
                    'user': user_info,
                    'last_visit': last_visit,
                    'total_visit': visit_count,
                    'update_at': time.time()
                }
            })
