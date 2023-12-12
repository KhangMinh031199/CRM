import time
from bson.objectid import ObjectId
import api
import settings

def total_groups(merchant_id):
       return api.DATABASE.groups.find({
        'merchant_id': ObjectId(merchant_id)
    }).count()


def list_groups(merchant_id, page, page_size=settings.ITEMS_PER_PAGE):
    return api.DATABASE.groups.find({
        'merchant_id': ObjectId(merchant_id)
    }).sort('timestamp', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)


def insert_group(merchant_id, name, phone, email, mst, address):
    info = {
        'name': name,
        'create_at': time.time(),
        'merchant_id': ObjectId(merchant_id),
        'update_at': time.time(),
     
    }
    api.DATABASE.groups.insert(info)
    


def update_group(merchant_id, company_id):
    pass


def remove_group(merchant_id, company_id):
    api.DATABASE.groups.remove({
        'merchant_id': ObjectId(merchant_id),
        '_id': ObjectId(company_id),
    })