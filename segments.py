import time
from bson.objectid import ObjectId
import api
import settings

def total_segment(merchant_id):
       return api.DATABASE.segment.find({
        'merchant_id': ObjectId(merchant_id)
    }).count()


def list_segment(merchant_id, page, page_size=settings.ITEMS_PER_PAGE):
    return api.DATABASE.segment.find({
        'merchant_id': ObjectId(merchant_id)
    }).sort('timestamp', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)


def insert_segment(merchant_id, name, phone, email, mst, address):
    info = {
        'name': name,
        'create_at': time.time(),
        'merchant_id': ObjectId(merchant_id),
        'update_at': time.time(),
     
    }
    api.DATABASE.segment.insert(info)
    


def update_group(merchant_id, company_id):
    pass


def remove_group(merchant_id, company_id):
    api.DATABASE.segment.remove({
        'merchant_id': ObjectId(merchant_id),
        '_id': ObjectId(company_id),
    })