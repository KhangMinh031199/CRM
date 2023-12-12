#  Developed by TungHa on 2017.
#  Last modified 7/23/19 7:27 PM
#  Copyright (c) 2019. All rights reserved.

from bson.objectid import ObjectId
import time
import api


def insert_send_activity(merchant_id, shop_id, customer_id, send_type, message, id_type, camp_id=None):
    if not isinstance(
            merchant_id,
            ObjectId):
        merchant_id = ObjectId(
            merchant_id
        )
    if not isinstance(
            shop_id,
            ObjectId):
        shop_id = ObjectId(
            shop_id
        )
    if not isinstance(
            customer_id,
            ObjectId):
        customer_id = ObjectId(
            customer_id
        )
    info = {
        'merchant_id': merchant_id,
        'shop_id': shop_id,
        'send_type': send_type,
        'customer_id': customer_id,
        'message': message,
        'id_type': id_type,
        'when': time.time()
    }
    if camp_id:
        if not isinstance(
                camp_id,
                ObjectId):
            camp_id = ObjectId(
                camp_id
            )
        info['camp_id'] = camp_id
    activity_id = api.DATABASE.send_activity_log.insert(info)
    return activity_id


def get_send_activity_by_shop_id(shop_id):
    if not isinstance(
            shop_id,
            ObjectId):
        shop_id = ObjectId(
            shop_id
        )
    return api.DATABASE.send_activity_log.find({
        'shop_id': shop_id
    })


def update_send_activity(activity_id, result):
    if not isinstance(
            activity_id,
            ObjectId):
        activity_id = ObjectId(
            activity_id
        )
    api.DATABASE.send_activity_log.update({
        '_id': activity_id
    }, {'$set': {
        'result': result
    }})

