import api
import settings


def get_wifi_access_code(shops, page, page_size=settings.ITEMS_PER_PAGE):
    recs = api.DATABASE.wifi_access_code.find({
        'shop_id': {
            '$in': shops
        }}).skip(page_size * (page - 1)).limit(page_size)

    results = [rec for rec in recs]
    return results


def total_wifi_access_code(shops):
    return api.DATABASE.wifi_access_code.find({
        'shop_id': {
            '$in': shops
        }}).count()