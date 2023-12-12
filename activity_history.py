from datetime import datetime
import api

def save_activity(Type, merchant_id, shop_id, code_camp=None, user_id=None, coupon_name=None, location_name=None):
    if Type == 'insert_campaign':
        api.DATABASE.activity_log.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'message': 'Ban vua them moi chien dich %s vao luc %s' % (code_camp, datetime.now()),
            'Type': Type,
            'when': datetime.now()
        })
    if Type == 'update_campaign':
	    api.DATABASE.activity_log.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'message': 'Ban vua cap nhat chien dich %s vao luc %s' % (code_camp, datetime.now()),
            'Type': Type,
            'when': datetime.now()
        })
    if Type == 'update_customer':
	    api.DATABASE.activity_log.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'message': 'Ban vua cap nhat khach hang %s vao luc %s' % (user_id, datetime.now()),
            'Type': Type,
            'when': datetime.now()
        })
    if Type == 'export_customer':
	    api.DATABASE.activity_log.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'message': 'Ban vua xuat file khach hang vao luc %s' % (datetime.now()),
            'Type': Type,
            'when': datetime.now()
        })
    if Type == 'update_coupon':
	    api.DATABASE.activity_log.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'message': 'Ban vua cap nhat coupon %s vao luc %s' % (coupon_name, datetime.now()),
            'Type': Type,
            'when': datetime.now()
        })
    if Type == 'insert_location':
	    api.DATABASE.activity_log.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'message': 'Ban vua them moi dia diem %s vao luc %s' % (location_name, datetime.now()),
            'Type': Type,
            'when': datetime.now()
        })
    if Type == 'update_location':
	    api.DATABASE.activity_log.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'message': 'Ban vua cap nhat dia diem %s vao luc %s' % (location_name, datetime.now()),
            'Type': Type,
            'when': datetime.now()
        })
