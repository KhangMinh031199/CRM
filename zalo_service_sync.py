#! coding: utf-8
import time
from hashlib import sha256
import api
import zalo_api

from raven import Client
from raven.transport.http import HTTPTransport

client = Client(
	'http://9399211fa32c46a69c3b40d5a41c99ed:9989ba328bc748aeb4d8dd52b3fa8234@sentry.nextify.vn/2',
	transport=HTTPTransport)


def get_zalo_last_time_sync_visit_log():
	return api.DATABASE.social_sync_time.find_one({'sync_id': 'zalo'})


def get_mac_token_profile(page_account, page_key, uid):
	timestamp = time.time()
	timestamp = str(timestamp).split('.')[0]
	gen_mac = sha256(str(page_account) + str(uid) + str(timestamp) + page_key)
	hex_dig = gen_mac.hexdigest()
	return hex_dig

# @babis.decorator(ping_before='http://hc.nextify.vn/ping/6b9de7d3-07ec-460c-aff9-fbe57881215b', ping_after='http://hc.nextify.vn/ping/6b9de7d3-07ec-460c-aff9-fbe57881215b')
# def sync_zalo():
# 	last_time = get_zalo_last_time_sync_visit_log()
# 	print last_time
# 	visit_log = []
# 	if last_time:
# 		time_stamp_update = last_time.get('timestamp')
# 		visit_log = api.DATABASE.visit_log.find({
# 			'timestamp': {'$gte': int(time_stamp_update)}
# 		})
# 		print visit_log.count()
# 	else:
# 		visit_log = api.DATABASE.visit_log.find()
#
# 	for log in visit_log:
# 		shop_id = log.get('shop_id')
# 		user_id = log.get('user_id')
# 		timestamp = log.get('timestamp')
# 		shop = api.get_shop_info(shop_id=shop_id)
# 		user = api.get_user_info(user_id=user_id)
# 		if shop and user:
# 			zalo_oa_id = shop.get('zalo_oa_id')
# 			zalo_oa_key = shop.get('zalo_oa_key')
# 			if zalo_oa_id and zalo_oa_key:
# 				zalo_api.update_user_with_zalo(user, zalo_oa_id, zalo_oa_key,
# 				                               shop_id)
# 		time.sleep(5)
# 		check_time_update = api.DATABASE.social_sync_time.find_one(
# 			{'sync_id': 'zalo'})
# 		if check_time_update:
# 			api.DATABASE.social_sync_time.update({'sync_id': 'zalo'}, {
# 				'$set': {'timestamp': timestamp}})
# 		else:
# 			api.DATABASE.social_sync_time.insert(
# 				{'sync_id': 'zalo', 'timestamp': timestamp})
# sync_zalo()



shop_id = "5a6170e13fd79c2db9147cc7"
user_id = "5d196b7f57edfc4a85259892"
shop = api.get_shop_info(shop_id=shop_id)
user = api.get_user_info(user_id=user_id)
if shop and user:
	zalo_oa_id = shop.get('zalo_oa_id')
	zalo_oa_key = shop.get('zalo_oa_key')
	if zalo_oa_id and zalo_oa_key:
		zalo_api.update_user_with_zalo(user, zalo_oa_id, zalo_oa_key,
				                               shop_id)