from bson.objectid import ObjectId
import requests
import time
from datetime import date
import api
import save_customers
import settings
import send_activity

ZALO_LIST_FOLLOWER = "https://openapi.zalo.me/v2.0/oa/getfollowers?"


def zalo_oa_send_mess(user_id, message, access_token, activity_id):
    URL = "https://openapi.zaloapp.com/v2.0/oa/message?access_token=%s" % (access_token)
    r = requests.post(URL, json={
        "recipient": {
            "user_id": user_id
        },
        "message": {
            "text": message
        }
    })
    if r.status_code == 200:
        r_content = r.json()
        error = r_content.get('error')
        if error != 1:
            send_activity.update_send_activity(activity_id, False)
        else:
            send_activity.update_send_activity(activity_id, True)

    else:
        send_activity.update_send_activity(activity_id, False)


def get_customers(shop_id, page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    customers = []
    recs = api.DATABASE.customers_location.find({'shop_id': shop_id}).sort('last_visit', 1). \
        skip(settings.ITEMS_PER_PAGE * (page - 1)).limit(settings.ITEMS_PER_PAGE)
    for rec in recs:
        customers.append(rec)
    return customers


def update_sync_customers_zalo_single(merchant_id, shop_id, access_token, user_id):
    user = api.get_user_info(user_id=user_id)
    phone = user.get('phone')
    if phone and len(phone) > 0:
        zalo_phone = phone.lstrip('0')
        zalo_phone = '+84' + str(zalo_phone)
        user_zalo = get_user_zalo_follower(access_token, zalo_phone)
        if user_zalo:
            user_gender = int(user_zalo.get('user_gender'))
            user_id_zalo = user_zalo.get('user_id')
            avatar = user_zalo.get('avatars').get('240')
            full_name = user_zalo.get('display_name')
            int_bday = user_zalo.get('birthDate')
            zalo_birthday = ""
            if int_bday and str(int_bday) != 'None':
                zalo_birthday = date.fromtimestamp(int(int_bday)).strftime('%m-%d')
            user = api.get_user_info(user_id=user_id)
            if user:
                name = user.get('name', '')
                birthday = user.get('birthday', '')
                gender = user.get('gender')
                info = {}
                if not name or len(name) == 0:
                    info['name'] = full_name
                if not birthday or len(birthday) == 0:
                    info['birthday'] = zalo_birthday
                if not gender:
                    info['gender'] = user_gender
                info['avatar'] = avatar
                api.DATABASE.user.update({'_id': user_id}, {'$set': info})
                tag_name = 'zalo'
                tag_item = api.get_tag_by_tag_name(merchant_id, tag_name)
                if tag_item:
                    tag_id = tag_item.get('_id')
                    api.create_user_tags(merchant_id, shop_id, user_id, tag_id)

                save_customers.update_customers_zalop(merchant_id, shop_id, user_id, user_id_zalo)


def update_sync_customers_zalo(shop_id, access_token):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    total = api.DATABASE.customers_location.find({'shop_id': shop_id}).count()
    zalo_sync = api.DATABASE.zalo_loc_sync.find_one({
        'shop_id': shop_id
    })
    page = 1
    if zalo_sync:
        page = int(zalo_sync.get('page', 1))
    else:
        api.DATABASE.zalo_loc_sync.insert({
            'shop_id': shop_id,
            'page': 1
        })

    total_page = total / settings.ITEMS_PER_PAGE
    if int(page) <= int(total_page):
        for page_count in range(int(page), int(total_page) + 1):
            shop = api.get_shop_info(shop_id=shop_id)
            merchant_id = shop.get('merchant_id')
            customers = get_customers(shop_id, page_count)
            for cus in customers:
                user = cus.get('user', {})
                phone = user.get('phone')
                user_id = cus.get('user_id')
                if phone and len(phone) > 0:
                    zalo_phone = phone.lstrip('0')
                    zalo_phone = '+84' + str(zalo_phone)
                    user_zalo = get_user_zalo_follower(access_token, zalo_phone)
                    if user_zalo:
                        user_gender = int(user_zalo.get('user_gender'))
                        user_id_zalo = user_zalo.get('user_id')
                        avatar = user_zalo.get('avatars').get('240')
                        full_name = user_zalo.get('display_name')
                        int_bday = user_zalo.get('birthDate')
                        zalo_birthday = ""
                        if int_bday and str(int_bday) != 'None':
                            zalo_birthday = date.fromtimestamp(int(int_bday)).strftime('%m-%d')
                        user = api.get_user_info(user_id=user_id)
                        if user:
                            name = user.get('name', '')
                            birthday = user.get('birthday', '')
                            gender = user.get('gender')
                            info = {}
                            if not name or len(name) == 0:
                                info['name'] = full_name
                            if not birthday or len(birthday) == 0:
                                info['birthday'] = zalo_birthday
                            if not gender:
                                info['gender'] = user_gender
                            info['avatar'] = avatar
                            api.DATABASE.user.update({'_id': user_id}, {'$set': info})
                            tag_name = 'zalo'
                            tag_item = api.get_tag_by_tag_name(merchant_id, tag_name)
                            if tag_item:
                                tag_id = tag_item.get('_id')
                                api.create_user_tags(merchant_id, shop_id, user_id, tag_id)

                            save_customers.update_customers_zalop(merchant_id, shop_id, user_id, user_id_zalo)

            api.DATABASE.zalo_loc_sync.update({
                'shop_id': shop_id,
            }, {
                '$set': {
                    'page': page_count
                }
            })


def get_total_zalo_follower(access_token):
    ZALO_URL_LIST_FOLLOWER = ZALO_LIST_FOLLOWER + 'access_token=%s&data={"offset": 0, "count": 1}' % (access_token)
    r = requests.get(ZALO_URL_LIST_FOLLOWER)
    content = r.json()
    if 'data' in content:
        data = content.get('data', {})
        total = data.get('total')
        return int(total)
    else:
        return 0


def get_user_zalo_follower(access_token, user_id):
    URL = 'https://openapi.zalo.me/v2.0/oa/getprofile?access_token=%s&data={"user_id":%s}' % (access_token, user_id)
    r = requests.get(URL)
    content = r.json()
    if 'data' in content:
        data = content.get('data', {})
        return data
    else:
        return False


def get_list_zalo_follower(access_token, offset, count):
    ZALO_URL_LIST_FOLLOWER = ZALO_LIST_FOLLOWER + 'access_token=%s&data={"offset": %s, "count": %s}' % (access_token,
                                                                                                        int(offset),
                                                                                                        int(count))
    r = requests.get(ZALO_URL_LIST_FOLLOWER)
    content = r.json()
    if 'data' in content:
        data = content.get('data', {})
        followers = data.get('followers', [])
        if len(followers) > 0:
            return offset
        else:
            return False
    else:
        return False


def get_ids_zalo_follower(access_token, offset, count):
    ids = []
    ZALO_URL_LIST_FOLLOWER = ZALO_LIST_FOLLOWER + 'access_token=%s&data={"offset": %s, "count": %s}' % (access_token,
                                                                                                        int(offset),
                                                                                                        int(count))
    r = requests.get(ZALO_URL_LIST_FOLLOWER)
    content = r.json()
    if 'data' in content:
        data = content.get('data', {})
        ids = data.get('followers', [])

    return ids


def sync_zalo(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = api.get_shop_info(shop_id=shop_id)
    if shop:
        access_token = shop.get('zalo_access_token')
        if access_token:
            offset = 0
            zalo_sync = api.DATABASE.zalo_loc_sync.find_one({
                'shop_id': shop_id
            })
            if zalo_sync:
                offset = int(zalo_sync.get('offset', 0))
            else:
                api.DATABASE.zalo_loc_sync.insert({
                    'shop_id': shop_id,
                    'offset': offset
                })
            total = get_total_zalo_follower(access_token)
            if offset < total:
                count = total - offset
                new_offset = get_list_zalo_follower(access_token, offset, count)
                if new_offset:
                    api.DATABASE.zalo_loc_sync.update({
                        'shop_id': shop_id
                    }, {
                        '$set': {
                            'offset': new_offset
                        }
                    })


def update_user_from_oa_first_time(shop_id, access_token):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = api.get_shop_info(shop_id=shop_id)
    if shop:
        total = get_total_zalo_follower(access_token)
        ids = get_ids_zalo_follower(access_token, 0, total)
        merchant_id = shop.get('merchant_id')
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        for id_zalo in ids:
            user_id_zalo = id_zalo.get('user_id')
            user_zalo = get_user_zalo_follower(access_token, user_id_zalo)
            if user_zalo:
                user = {}
                display_name = user_zalo.get('display_name')
                user_gender = int(user_zalo.get('user_gender'))
                user['gender'] = user_gender
                user_id_zalo = user_zalo.get('user_id')
                user['user_id_zalo'] = user_id_zalo
                avatar = user_zalo.get('avatars').get('240')
                user['avatar'] = avatar
                full_name = user_zalo.get('display_name')
                user['name'] = full_name
                int_bday = user_zalo.get('birthDate')
                zalo_birthday = ""
                if int_bday and str(int_bday) != 'None':
                    zalo_birthday = date.fromtimestamp(int(int_bday)).strftime('%m-%d')
                    user['birthday'] = zalo_birthday
                shared_info = user_zalo.get('shared_info')
                city = ''
                if shared_info:
                    city = shared_info.get('city')
                    district = shared_info.get('district')
                    phone = shared_info.get('phone')
                    if phone and len(str(phone)) > 0:
                        phone = str(phone).lstrip('84')
                        phone = '0' + phone
                    address = shared_info.get('address')
                    user['home_town'] = city
                    user['district'] = district
                    user['phone'] = phone
                    user['address'] = address

                check_user = api.DATABASE.customers.find_one({'user.user_id_zalo': user_id_zalo, 'merchant_id': merchant_id})
                if check_user:
                    user_id = check_user.get('user_id')
                    api.DATABASE.user.update({'_id': user_id}, {'$set': user})
                    tag_name = 'zalo'
                    tag_item = api.get_tag_by_tag_name(merchant_id, tag_name)
                    if tag_item:
                        tag_id = tag_item.get('_id')
                        api.create_user_tags(merchant_id, shop_id, user_id, tag_id)


                    user_tags_details = []
                    user_tags = api.get_user_tags(merchant_id, user_id)
                    if user_tags:
                        user_tag = user_tags.get('tags')
                        if len(user_tag) > 0:
                            if type(user_tag) != list:
                                user_tag = [user_tag]
                            for tag in user_tag:
                                tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                                if tag_db:
                                    user_tags_details.append(tag_db)

                    user['user_tags_details'] = user_tags_details
                    api.DATABASE.customers.update({
                        'merchant_id': merchant_id,
                        'user_id': user_id
                    }, {
                        '$set': {
                            'user': user,
                            'update_at': time.time()
                        }
                    })

                    api.DATABASE.customers_location.update({
                        'shop_id': ObjectId(shop_id),
                        'user_id': user_id
                    }, {
                        '$set': {
                            'user': user,
                            'update_at': time.time()
                        }
                    })
                else:
                    if user.get('phone') and len(user.get('phone', '')) > 0:
                        phone = user.get('phone')
                        user_exists = api.DATABASE.customers.find_one({
                            "user.phone": phone
                        })
                        if user_exists:
                            user_id = user_exists.get('user_id')
                            tag_name = 'zalo'
                            tag_item = api.get_tag_by_tag_name(merchant_id, tag_name)
                            if tag_item:
                                tag_id = tag_item.get('_id')
                                api.create_user_tags(merchant_id, shop_id, user_id, tag_id)

                            user_tags_details = []
                            user_tags = api.get_user_tags(merchant_id, user_id)
                            if user_tags:
                                user_tag = user_tags.get('tags')
                                if len(user_tags) > 0:
                                    for tag in user_tag:
                                        tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                                        if tag_db:
                                            user_tags_details.append(tag_db)

                            user['user_tags_details'] = user_tags_details

                            api.DATABASE.customers.update({
                                'merchant_id': merchant_id,
                                'user_id': user_id
                            }, {
                                '$set': {
                                    'user': user,
                                    'update_at': time.time()
                                }
                            })

                            api.DATABASE.customers_location.update({
                                'shop_id': ObjectId(shop_id),
                                'user_id': user_id
                            }, {
                                '$set': {
                                    'user': user,
                                    'update_at': time.time()
                                }
                            })

                        else:
                            #insert
                            user_id = api.register(
                                name=full_name,
                                phone=phone,
                                gender=user_gender,
                                birthday=zalo_birthday,
                                home_town=city
                            )
                            api.update_user_by_id(user_id, user_id_zalo=user_id_zalo)
                            tag_name = 'zalo'
                            tag_item = api.get_tag_by_tag_name(merchant_id, tag_name)
                            if tag_item:
                                tag_id = tag_item.get('_id')
                                api.create_user_tags(merchant_id, shop_id, user_id, tag_id)

                            user_tags_details = []
                            user_tags = api.get_user_tags(merchant_id, user_id)
                            if user_tags:
                                user_tag = user_tags.get('tags')
                                if len(user_tags) > 0:
                                    for tag in user_tag:
                                        tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                                        if tag_db:
                                            user_tags_details.append(tag_db)
                            user['user_tags_details'] = user_tags_details
                            api.DATABASE.customers.insert({
                                'merchant_id': merchant_id,
                                'user_id': user_id,
                                'user': user,
                                'last_visit': time.time(),
                                'total_visit': 0,
                                'update_at': time.time()
                            })
                            api.DATABASE.customers_location.insert({
                                'shop_id': shop_id,
                                'user_id': user_id,
                                'user': user,
                                'last_visit': time.time(),
                                'total_visit': 0,
                                'update_at': time.time()
                            })

                    else:
                        user_id = api.register(
                            name=full_name,
                            gender=user_gender,
                            birthday=zalo_birthday,
                            home_town=city
                        )
                        api.update_user_by_id(user_id, user_id_zalo=user_id_zalo)
                        tag_name = 'zalo'
                        tag_item = api.get_tag_by_tag_name(merchant_id, tag_name)
                        if tag_item:
                            tag_id = tag_item.get('_id')
                            api.create_user_tags(merchant_id, shop_id, user_id, tag_id)

                        user_tags_details = []
                        user_tags = api.get_user_tags(merchant_id, user_id)
                        if user_tags:
                            user_tag = user_tags.get('tags')
                            if len(user_tags) > 0:
                                for tag in user_tag:
                                    tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                                    if tag_db:
                                        user_tags_details.append(tag_db)

                        user['user_tags_details'] = user_tags_details
                        api.DATABASE.customers.insert({
                            'merchant_id': merchant_id,
                            'user_id': user_id,
                            'user': user,
                            'last_visit': time.time(),
                            'total_visit': 0,
                            'update_at': time.time()
                        })
                        api.DATABASE.customers_location.insert({
                            'shop_id': shop_id,
                            'user_id': user_id,
                            'user': user,
                            'last_visit': time.time(),
                            'total_visit': 0,
                            'update_at': time.time()
                        })






# shop_id = "5a6170e13fd79c2db9147cc7"
# shop = api.get_shop_info(shop_id=shop_id)
# access_token = shop.get('zalo_access_token')
# update_sync_customers_zalo(shop_id, access_token)


# shop_id = "5a6170e13fd79c2db9147cc7"
# shop = api.get_shop_info(shop_id=shop_id)
# access_token = shop.get('zalo_access_token')
# update_sync_customers_zalo(shop_id, access_token)
# sync_zalo(shop_id)
# get_list_zalo_follower(access_token, 0, 5)
