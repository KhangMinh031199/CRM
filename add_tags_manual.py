from bson.objectid import ObjectId
import api


def random_customers(merchant_id, numbers):
    shops = []
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer['_id'])
    shop_id = shops[0]
    list_customers = api.list_customers(shops, shop_id, merchant_id,
                                        from_date=None,
                                        to_date=None,
                                        min_visit=None,
                                        max_visit=None,
                                        sort=None,
                                        bday_from_date=None,
                                        bday_to_date=None,
                                        ranks=None,
                                        gender=None, is_zalo=None,
                                        filter_tags=None,
                                        min_cash=None,
                                        max_cash=None,
                                        min_points=None,
                                        max_points=None,
                                        page=1,
                                        page_size=int(numbers))
    print 'OK'
    print len(list_customers)

    for cus in list_customers:
        tag_id = "5ad0390cf58a74876e9c3b00"
        add_tags(tag_id, merchant_id, shop_id, cus['_id'])



def add_tags(tags, merchant_id, shop_id, user_id):
    tags_array = []
    if tags and len(tags) > 0:
        tags_array = tags.split(',')
    print tags_array
    api.create_user_tags(merchant_id, shop_id, user_id, tags_array)


random_customers('5aaf6be8f58a74a488571733', 1000)
