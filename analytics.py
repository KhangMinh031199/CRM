from pymongo import MongoClient
from collections import OrderedDict
from bson.objectid import ObjectId
from datetime import datetime
import time
import settings
import api


def count_total_range(shop_id, date_from, date_to):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'shop_id': shop_id,
        'timestamp': {
            '$lte': date_to,
            '$gte': date_from
        }
    }
    count = 0
    visits = api.DATABASE.visit_log.find(info).sort('timestamp', -1)
    for visit in visits:
        count += 1
    return count


def count_new_visit_range(shop_id, date_from, date_to):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'shop_id': shop_id,
        'timestamp': {
            '$lte': date_to,
            '$gte': date_from
        }
    }
    count = 0
    visits = api.DATABASE.visit_log.find(info).sort('timestamp', -1)
    for visit in visits:
        phone = visit['phone']
        count_user = api.DATABASE.visit_log.find({'phone': phone}).count()
        if count_user == 1:
            count += 1
    return count


def count_sms_in_range(shop_id, date_from, date_to):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'shop_id': shop_id,
        'timestamp': {
            '$lte': date_to,
            '$gte': date_from
        }
    }
    return api.DATABASE.sms_log.find(info).sort('timestamp', -1).count()


def count_coupon_in_range(shop_id, date_from, date_to):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'shop_id': shop_id,
        'created_at': {
            '$lte': date_to,
            '$gte': date_from
        }
    }
    return api.DATABASE.coupon.find(info).sort('created_at', -1).count()


def count_coupon_redeem_in_range(shop_id, date_from, date_to):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'shop_id': shop_id,
        'redeemed': True,
        'created_at': {
            '$lte': date_to,
            '$gte': date_from
        }
    }
    return api.DATABASE.coupon.find(info).sort('created_at', -1).count()


def count_customers_loyal(shop_id, date_from, date_to):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'shop_id': shop_id,
        'timestamp': {
            '$lte': date_to,
            '$gte': date_from
        }
    }

    recs = api.DATABASE.visit_log.aggregate([{
        '$match': info
    }, {
        '$group': {
            "_id": '$phone',
            "count": {
                '$sum': 1
            }
        }
    }, {
        '$match': {
            "count": {
                "$gte": 3
            }
        }
    }])
    return len(list(recs))


def count_customers_lost(shop_id, date_from):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {'shop_id': shop_id, 'timestamp': {'$lte': date_from - 30 * 86400}}

    recs = api.DATABASE.visit_log.aggregate([
        {
            '$match': info
        },
        {
            '$group': {
                "_id": '$phone',
            }
        },
    ])
    return len(list(recs))


def report_total_customers(
        shops,
        shop_id,
        merchant_id,
        from_date=None,
        to_date=None, ):
    total = api.total_customers(
        shops, shop_id, merchant_id, from_date=from_date, to_date=to_date)

    new_customers = api.total_customers(
        shops,
        shop_id,
        merchant_id,
        from_date=from_date,
        to_date=to_date,
        min_visit='1',
        max_visit='1')
    return_customers = int(total) - int(new_customers)

    info_visit = {'shop_id': {'$in': shops}}
    from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
        replace(hour=0, minute=0)
    from_tmp = time.mktime(from_obj.timetuple())
    info_visit['timestamp'] = {}
    info_visit['timestamp']['$gte'] = from_tmp
    to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
        replace(hour=23, minute=0)
    to_tmp = time.mktime(to_obj.timetuple())
    info_visit['timestamp']['$lte'] = to_tmp
    visit_total = api.DATABASE.visit_log.find(info_visit).count()

    return {
        'total': total,
        'new': new_customers,
        'return': return_customers,
        'visit_total': visit_total
    }


def visit_by_hours(shops, shop_id, merchant_id, from_date=None, to_date=None):
    visit_hour = []
    ranges = settings.HOURS_VISIT_RANGE
    for range_hour in ranges:
        min_range = range_hour.get('min')
        max_range = range_hour.get('max')
        info_visit = {'shop_id': {'$in': shops}}
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        info_visit['timestamp'] = {}
        info_visit['timestamp']['$gte'] = from_tmp
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=0)
        to_tmp = time.mktime(to_obj.timetuple())
        info_visit['timestamp']['$lte'] = to_tmp
        info_visit['time_hour'] = {'$lte': max_range, '$gte': min_range}
        count_visit = api.DATABASE.visit_log.find(info_visit).count()
        item = []
        range_str = str(min_range) + '-' + str(max_range)
        item.append(range_str)
        item.append(count_visit)
        visit_hour.append(item)
    return visit_hour


def count_visit_reports(shops,
                        shop_id,
                        merchant_id,
                        from_date=None,
                        to_date=None):
    count_visits = []
    ranges = settings.COUNT_VISIT_RANGE
    for range_visit in ranges:
        name_range = range_visit.get('name')
        text_range = range_visit.get('text')
        data_range = range_visit.get('data')
        type_range = range_visit.get('type')

        item = []
        item.append(text_range)
        if type_range != 'great':
            count_visit = api.total_customers(
                shops,
                shop_id,
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                min_visit=data_range[0],
                max_visit=data_range[1])

            item.append(count_visit)
        else:
            count_visit = api.total_customers(
                shops,
                shop_id,
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                min_visit=data_range[0])

            item.append(count_visit)
        count_visits.append(item)
    return count_visits

