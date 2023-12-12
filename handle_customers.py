from bson.objectid import ObjectId
import api


def get_user_merchant_by_mac(merchant_id, client_mac):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return api.DATABASE.customers.find_one({
            'merchant_id': merchant_id,
            'user.client_mac': client_mac
        })

def get_user_merchant_by_phone(merchant_id, phone):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return api.DATABASE.customers.find_one({
            'merchant_id': merchant_id,
            'user.phone': phone
        })


def get_user_merchant_by_email(merchant_id, email):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return api.DATABASE.customers.find_one({
            'merchant_id': merchant_id,
            'user.email': email
        })

def get_user_merchant_by_user_id(merchant_id, user_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    return api.DATABASE.customers.find_one({
            'merchant_id': merchant_id,
            'user_id': user_id
        })