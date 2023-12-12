#! coding: utf-8
from pymongo import MongoClient
from collections import OrderedDict, defaultdict
from bson.objectid import ObjectId
import api
import os
import settings
from pbkdf2 import pbkdf2_bin
from base64 import b64encode, b64decode
from os import urandom
import hashlib


SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'
COST_FACTOR = 10000

MONGODB = MongoClient(
    settings.MONGODB_HOST,
    settings.MONGODB_PORT,
    document_class=OrderedDict,
    maxPoolSize=200,
    serverSelectionTimeoutMS=90000)
DATABASE = MONGODB[settings.MONGODB_NAME]
DATABASE.authenticate(
    settings.MONGODB_USER,
    settings.MONGODB_PASSWORD,
    source=settings.MONGO_NAME_AUTHEN)

def make_hash(password):
    """Generate a random salt and return a new hash for the password."""
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    salt = b64encode(urandom(SALT_LENGTH))
    return 'PBKDF2${}${}${}${}'.format(
        HASH_FUNCTION, COST_FACTOR, salt,
        b64encode(
            pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                       getattr(hashlib, HASH_FUNCTION))))

print ('=======hash')
password = make_hash('123456Aa@')

merchant = DATABASE.merchants.find({"name": {'$regex': "VTT-", '$options': 'i'}})
for mer in merchant:
    mer_id = mer.get('_id')
    name = mer.get('name').lower()
    print name
    if not isinstance(mer_id, ObjectId):
        mer_id = ObjectId(mer_id)
    # shops = DATABASE.shop.find({'merchant_id': str(mer_id)})
    # for shop in shops:
    #     shop_id = shop.get('_id')
    #     if not isinstance(shop_id, ObjectId):
    #         shop_id = ObjectId(shop_id)
    #     print "=====shop"
    #     print shop_id
    # DATABASE.merchants.update({'_id': mer_id}, {'$set': {'business_model_id': '5c9ddd00e452d5225bb1ef31', 'package': '5b44517ac5e5f42f1687ed3b' } })

print "----done"