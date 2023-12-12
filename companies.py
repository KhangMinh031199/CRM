import time
from bson.objectid import ObjectId
import api
import settings


def total_companies(merchant_id):
    return api.DATABASE.company.find({
        'merchant_id': ObjectId(merchant_id)
    }).count()


def list_companies(merchant_id, page, page_size=settings.ITEMS_PER_PAGE):
    return api.DATABASE.company.find({
        'merchant_id': ObjectId(merchant_id)
    }).sort('timestamp', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)


def insert_company(merchant_id, name, phone, email, mst, address):
    info = {
        'name': name,
        'phone': phone,
        'create_at': time.time(),
        'merchant_id': ObjectId(merchant_id),
        'email': email,
        'mst': mst,
        'address': address,
        'update_at': time.time(),
    }
    api.DATABASE.company.insert(info)
    


def update_company(merchant_id, company_id):
    pass


def remove_company(merchant_id, company_id):
    api.DATABASE.company.remove({
        'merchant_id': ObjectId(merchant_id),
        '_id': ObjectId(company_id),
    })