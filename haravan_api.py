import api
import settings
from bson.objectid import ObjectId


def get_orders_haravan(merchant_id, page, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return api.DATABASE.order_haravan.find({
        'merchant_id': merchant_id,
        'source': "haravan"
    }).sort('created_at', -1).skip(page_size * (page - 1)).limit(page_size)

def total_orders_haravan(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return api.DATABASE.order_haravan.find({
        'merchant_id': merchant_id,
        'source': "haravan"
    }).count()