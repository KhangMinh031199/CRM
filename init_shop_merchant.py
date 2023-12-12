# ! coding: utf-8
from pymongo import MongoClient
from collections import OrderedDict, defaultdict
from bson.objectid import ObjectId
# from validate_email import validate_email
import time 
from datetime import datetime
import random
import user_agents
import requests
import os
import unicodecsv
import io
import json
import dateparser
import pyexcel as p
import xlrd
from flask import Flask, escape, request, render_template
from datetime import timedelta, date
from base64 import b64encode, b64decode
from bs4 import BeautifulSoup
from uuid import uuid4
import unidecode
from slugify import slugify
from pbkdf2 import pbkdf2_bin
from hashlib import md5
import hashlib
from os import urandom
import rating




# lenh chay celery
# $ celery -A tasks worker --loglevel=info
# celery worker -A main.celery --loglevel=INFO

# Mongodb = MongoClient(
#         '127.0.0.1',
#         27017,
#         document_class=OrderedDict,
#         maxPoolSize=200,
#         serverSelectionTimeoutMS=90000)

# DATABASE = Mongodb['nextify']
# DATABASE.authenticate(
# 'develop',
# 'g5i4dI8KzYmXs0K',
# source='nextify')

# SALT_LENGTH = 12
# KEY_LENGTH = 24
# HASH_FUNCTION = 'sha256' 
# COST_FACTOR = 10000

# def make_hash(password):
#     """Generate a random salt and return a new hash for the password."""
#     if isinstance(password, unicode):
#         password = password.encode('utf-8')
#     salt = b64encode(urandom(SALT_LENGTH))
#     return 'PBKDF2${}${}${}${}'.format(
#         HASH_FUNCTION, COST_FACTOR, salt,
#         b64encode(
#             pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
#                        getattr(hashlib, HASH_FUNCTION))))

# def init_spin(shop_id):
#     if isinstance(shop_id, ObjectId):
#         shop_id = ObjectId(shop_id)
        
#         info = {
#             "gifts":[
#                 {
#                     "remaining_amount":"",
#                     "color":"1920FF",
#                     "rate_gravity":"50",
#                     "is_reward":False,
#                     "detail":"",
#                     "amount":"",
#                     "title":"không trúng",
#                     "rate_reward":"33"
#                 },
#                 {
#                     "remaining_amount":"6",
#                     "color":"FF3B09",
#                     "rate_gravity":"0",
#                     "is_reward":"code",
#                     "detail":"Giảm 20000đ",
#                     "amount":"6",
#                     "title":"Giam20",
#                     "rate_reward":"0"
#                 },
#                 {
#                     "remaining_amount":"7",
#                     "color":"32FF2B",
#                     "rate_gravity":"20",
#                     "is_reward":"code",
#                     "detail":"",
#                     "amount":"7",
#                     "title":"MA123",
#                     "rate_reward":"13"
#                 },
#                 {
#                     "remaining_amount":"",
#                     "color":"FF6F96",
#                     "rate_gravity":"50",
#                     "is_reward":False,
#                     "detail":"",
#                     "amount":"",
#                     "title":"không trúng",
#                     "rate_reward":"33"
#                 },
#                 {
#                     "remaining_amount":"9",
#                     "color":"2D73FF",
#                     "rate_gravity":"0",
#                     "is_reward":"code",
#                     "detail":"",
#                     "amount":"9",
#                     "title":"Giam10",
#                     "rate_reward":"0"
#                 },
#                 {
#                     "remaining_amount":"9",
#                     "color":"FF16C9",
#                     "rate_gravity":"10",
#                     "is_reward":"code",
#                     "detail":"",
#                     "amount":"9",
#                     "title":"Giam20",
#                     "rate_reward":"7"
#                 },
#                 {
#                     "remaining_amount":"9",
#                     "color":"63FFCB",
#                     "rate_gravity":"20",
#                     "is_reward":"code",
#                     "detail":"",
#                     "amount":"9",
#                     "title":"Giam10",
#                     "rate_reward":"13"
#                 }
#             ],
#             "content_win":"Xin chúc mừng, phần thưởng của bạn là",
#             "name":"Game",
#             "content_color":"FFFFFF",
#             "turns":"3",
#             "win_rate":"10",
#             "time_reset":"2",
#             "content":"",
#             "name_btn_win":"quay ngay",
#             "background":"4/20671de8c832",
#             "content_not_win":"Rất tiếc bạn đã không trúng thưởng, hãy thử lại vận may của mình.",
#             "total_gifts":"7",
#             "slug":"game",
#             "center":"2/2068d7565c86"
#         }
#     camp_id = DATABASE.mini_game_page.insert({
#             'shop_id': shop_id,
#             'info': info,
#             'game_type': 'spin',
#             'when': time.time()
#         })
#     unique_string = str(shop_id) + str(camp_id) + str(time.time())
#     unique_id = info['slug'] + '_' + hashlib.md5(str(unique_string)).hexdigest()
#     if not isinstance(camp_id, ObjectId):
#         camp_id = ObjectId(camp_id)
#     DATABASE.mini_game_page.update({
#         'shop_id': shop_id,
#         '_id': camp_id
#     }, {'$set': {
#         'unique_id': unique_id,
#         'when': time.time()
#     }})

# def get_merchant_by_slug(slug):
#     return DATABASE.merchants.find_one({'slug': slug})

# def get_merchant_by_email(email):
#     return DATABASE.merchants.find_one({'email': email})

# def get_merchant_by_phone(phone):
#     return DATABASE.merchants.find_one({'phone': phone})

# def create_merchant(name, name_shop):
#     info = {}
#     slug = slugify(name)
#     info['name'] = name
#     info['slug'] = slug
#     info['sms_provider'] = ''
#     info['user_sms'] = ''
#     info['pass_sms'] = ''
#     info['api_key_vhat'] = ''
#     info['secret_key_vhat'] = ''
#     info['brand_name'] = ''
#     info['quota'] = ''
#     info['sms_type'] = ''
#     info['company'] = name 
#     pass_login_hash = make_hash('123456Aa@')
#     info['password'] = pass_login_hash
#     info['business_model_id'] = '5c9ddd00e452d5225bb1ef31'
#     info['package'] = '5fe3fa5bbf873217586beac3'
#     info['phone'] = ''
#     info['email'] = ''
#     info['partner'] = '606d6aec8ddb538237043495'
#     info['when'] = time.time()
#     info['update_at'] = time.time()
#     info['date_start_contract'] = datetime.today().strftime('%d-%m-%Y')
#     info['date_end_contract'] = '12'
#     info['contract_period'] = datetime.today().strftime('%d-%m') + '-2022'
#     check_slug = get_merchant_by_slug(slug)
#     if check_slug:
#         print 'Tên đăng nhập đã tồn tại.'
#     if not check_slug:
#         merchant_id = DATABASE.merchants.insert(info)
#         print '-------------'
#         print name
#         print merchant_id
#         create_shop(name_shop, merchant_id)

# def create_shop(name_shop, merchant_id):
#     info = {}
#     info['name'] = name_shop
#     info['slug'] = slugify(name_shop) 
#     info['logo'] = '1/20597df698f2'
#     info['email'] = ''
#     info['merchant_id'] = str(merchant_id)
#     info['background'] = '5/205a816b1850'
#     info['splash_lang'] = 'vi'
#     info['welcome_member_text_splash'] = ''
#     info['created_at'] = time.time()
#     info['sms'] = {
#         'welcome': {},
#         'return': {},
#         'loyal': {},
#         'lost': {},
#         'happy_birthday': {},
#         'announcement': {}}
#     info['email_template'] = {
#         'welcome': {},
#         'return': {},
#         'loyal': {},
#         'lost': {},
#         'happy_birthday': {},
#         'announcement': {}}
#     info['login_form'] = {
#             'phone_require': True,
#             'gender': False,
#             'phone': True,
#             'birthday': False,
#             'email': True,
#             'name': True
#         }
#     info['plus_login_form'] = {

#     }
#     shop = DATABASE.shop.insert(info)
#     print "========"
#     print shop
#     rating.init_survey(shop, 'vmarketing.viettel.vn')
#     init_spin(shop)
#     print "done"

# # lst = ['VTT-angiang', 'VTT-vungtau', 'VTT-bacgiang', 'VTT-backan', 'VTT-baclieu', 'VTT-bacninh', 'VTT-bentre', 'VTT-binhdinh', 'VTT-binhduong', 'VTT-binhphuoc', 'VTT-binhthuan', 'VTT-camau', 'VTT-cantho', 'VTT-caobang', 'VTT-danang', 'VTT-daklak', 'VTT-daknong', 'VTT-dienbien', 'VTT-dongnai', 'VTT-dongthap', 'VTT-gialai', 'VTT-hagiang', 'VTT-hanam', 'VTT-hatinh', 'VTT-haiduong', 'VTT-haiphong', 'VTT-haugiang', 'VTT-hoabinh', 'VTT-hungyen', 'VTT-khanhhoa', 'VTT-kiengiang', 'VTT-kontum', 'VTT-laichau', 'VTT-lamdong', 'VTT-langson', 'VTT-laocai', 'VTT-longan', 'VTT-namdinh', 'VTT-nghean', 'VTT-ninhbinh', 'VTT-ninhthuan', 'VTT-phutho', 'VTT-phuyen', 'VTT-quangbinh', 'VTT-quangnam', 'VTT-quangngai', 'VTT-quangninh', 'VTT-quangtri', 'VTT-soctrang', 'VTT-sonla', 'VTT-tayninh', 'VTT-thaibinh', 'VTT-thainguyen', 'VTT-thanhhoa', 'VTT-thuathienhue', 'VTT-tiengiang', 'VTT-thanhphohochiminh', 'VTT-travinh', 'VTT-tuyenquang', 'VTT-vinhlong', 'VTT-vinhphuc', 'VTT-yenbai']
# # for pro in lst:
# #     # name = unicode(pro)
# #     # name_shop = unicode(pro)
# #     # create_merchant(name, name_shop)
# #     DATABASE.merchants.update({'name': pro}, {'$set': {'partner': '600a89ccf12e8e8e72022a4a'}})
# #     print 'done'

# string = "VTT-angiang"
# uni = unicode(string)
# print "------"
# print uni, type(uni)


