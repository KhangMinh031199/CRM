import api
from bson.objectid import ObjectId


def search_customer_by_text(merchant_id, regex):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    query_search = {'merchant_id': merchant_id,
                    '$or': [
                        {"user.phone": {'$regex': regex, '$options': 'i'}},
                        {"user.name": {'$regex': regex, '$options': 'i'}},
                        {"user.email": {'$regex': regex, '$options': 'i'}},
                    ]}

    recs = api.DATABASE.customers.find(query_search).sort('last_visit', -1).limit(20)
    return recs


def search_coupon(merchant_id, regex):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    query_search = {'merchant_id': merchant_id,
                    '$or': [
                        {"code": {'$regex': regex, '$options': 'i'}},
                    ]}

    recs = api.DATABASE.coupon_manual.find(query_search).sort('when', -1).limit(20)
    return recs


def search_email_by_text(merchant_id, regex, shop_id=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    query_search = {}
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        query_search = {'merchant_id': merchant_id,
                        'shop_id': shop_id,
                    '$or': [
                        {"reception": {'$regex': regex, '$options': 'i'}},
                    ]}
    else:
        query_search = {'merchant_id': merchant_id,
                        '$or': [
                            {"reception": {'$regex': regex, '$options': 'i'}},
                        ]}
    recs = []
    logs = api.DATABASE.otp_log.find(query_search).sort('when', -1).limit(20)
    for log in logs:
            user_id = log.get('user_id')
            user = api.get_customer_by_user_id(merchant_id=merchant_id, user_id=user_id)
            if user:
                info_user = user.get('user')
                name = info_user.get('name', '')
                log['name'] = name
            recs.append(log)
    return recs