import time
import operator
from pymongo import MongoClient
import settings
from collections import OrderedDict
from bson.objectid import ObjectId
import sys
import api
import datetime


def mongodb_create():

    Mongodb = MongoClient(
        settings.MONGODB_HOST,
        settings.MONGODB_PORT,
        document_class=OrderedDict,
        maxPoolSize=200,
        serverSelectionTimeoutMS=90000)

    DATABASE = Mongodb['nextify']

    DATABASE.authenticate(
        settings.MONGODB_USER,
        settings.MONGODB_PASSWORD,
        source=settings.MONGO_NAME_AUTHEN)

    return Mongodb


MONGODB = mongodb_create()
DATABASE = MONGODB[settings.MONGODB_NAME]


def caculator_employee(merchant_id):
    merchant_id = str(merchant_id)
    shop_in_mer = DATABASE.shop.distinct("_id", {'merchant_id': merchant_id})

    current_time = time.time()
    past_30_time = current_time - 30 * 86400
    result = []
    for shop_id in shop_in_mer:
        top5 = DATABASE.customers_location.find({
            "shop_id": shop_id,
            "last_visit": {
                "$gte": past_30_time,
                "$lte": current_time,
            }
        }).count()
        if top5 != 0:
            if top5 > 20 and top5 < 40 or top5 < 20:
                top5 = 2
            else:
                top5 = top5 // 20
            print top5
            list_user_id = DATABASE.customers_location.find({
                "shop_id": shop_id,
                "last_visit": {
                    "$gte": past_30_time,
                    "$lte": current_time,
                }
            }).sort("total_visit", -1).limit(top5)

            for item in list_user_id:
                if item.get('total_visit') > 1:
                    result.append({
                        "employee_id": item.get('user_id'),
                        "visit": item.get('total_visit'),
                        "shop_id": item.get('shop_id')
                    })
                    try:
                        DATABASE.user.update({"_id": item.get('user_id')}, {"$set": {'is_employee': "True"}})
                        DATABASE.customers.update({"user_id": item.get('user_id'), "merchant_id": ObjectId(merchant_id)}, {"$set": {'user.is_employee': "True"}})
                        DATABASE.customers_location.update({"user_id": item.get('user_id'), 'shop_id':shop_id }, {"$set": {'user.is_employee': "True"}})
                    except:
                        pass

    info = {
        "merchant_id": ObjectId(merchant_id),
        "employee_id": result,
        "time_caculator": current_time
    }
    print info
    check_data = DATABASE.employee_merchant.find_one(
        {"merchant_id": ObjectId(merchant_id)})

    if not check_data:
        DATABASE.employee_merchant.insert(info)
    else:
        DATABASE.employee_merchant.update(
            {"merchant_id": ObjectId(merchant_id)}, {"$addToSet": {"employee_id": {"$each": result}},
                                                     "$set": {"time_caculator": current_time}
                                                     })


def access_time_caculator(merchant_id, hour_detection):

    hour_detection = int(hour_detection.split(
        ":")[0]) * 3600 + int(hour_detection.split(":")[1]) * 60
    print hour_detection

    merchant_id = str(merchant_id)
    shop_in_mer = DATABASE.shop.distinct("_id", {'merchant_id': merchant_id})

    current_time = time.time()
    past_30_time = current_time - 30 * 86400
    time_list = [datetime.datetime.utcfromtimestamp(
        past_30_time + i * 86400) for i in range(1, 31)]
    list_day = [datetime.datetime.strftime(
        item, "%m/%d/%y") for item in time_list]

    data_time_access = []
    result = []

    for shop_id in shop_in_mer:
        list_user_id = DATABASE.customers_location.find({
            "shop_id": shop_id,
            "last_visit": {
                "$gte": past_30_time,
                "$lte": current_time,
            }
        })
        for user_id in list_user_id:
            access_time = 0
            for day in list_day:
                data = DATABASE.visit_log.find({
                    "user_id": user_id.get("user_id"),
                    "shop_id": shop_id,
                    "time_day": day
                }).sort("timestamp", 1)
                data = list(data)
                if len(data) >= 2:
                    access_time = access_time + \
                        data[-1].get("timestamp") - data[0].get("timestamp")
            if access_time // 30 >= hour_detection:
                data_time_access.append(
                    {
                        "employee_id": user_id.get("user_id"),
                        "shop_id": shop_id,
                        "access_time": access_time / 30
                    })
                try:
                    DATABASE.user.update({"_id": user_id.get("user_id")}, {"$set": {'is_employee': "True"}})
                    DATABASE.customers.update({"user_id": user_id.get("user_id"), "merchant_id": ObjectId(merchant_id)}, {"$set": {'user.is_employee': "True"}})
                    DATABASE.customers_location.update({"user_id": user_id.get("user_id"), 'shop_id':shop_id }, {"$set": {'user.is_employee': "True"}})
                except:
                    pass

        info = {
            "merchant_id": ObjectId(merchant_id),
            "employee_id": data_time_access,
            "time_caculator": current_time
        }
        check_data = DATABASE.employee_merchant.find_one(
            {"merchant_id": ObjectId(merchant_id)})
        if not check_data:
            DATABASE.employee_merchant.insert(info)
        else:
            DATABASE.employee_merchant.update(
                {"merchant_id": ObjectId(merchant_id)}, {"$addToSet": {"employee_id": {"$each": data_time_access}},
                                                "$set": {"time_caculator": current_time}
                                            })
    pass


# merchant_id = "5a616f383fd79c2db9147c6a"
# hour_detection = "00:10"
# access_time_caculator(merchant_id, hour_detection)
# caculator_employee(merchant_id)
