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
import wifimedia_radius

# lenh chay celery
# $ celery -A tasks worker --loglevel=info
# celery worker -A main.celery --loglevel=INFO

Mongodb = MongoClient(
        '127.0.0.1',
        27017,
        document_class=OrderedDict,
        maxPoolSize=200,
        serverSelectionTimeoutMS=90000)

DATABASE = Mongodb['nextify']
DATABASE.authenticate(
'develop',
'g5i4dI8KzYmXs0K',
source='nextify')

# SALT_LENGTH = 12
# KEY_LENGTH = 24
# HASH_FUNCTION = 'sha256' 
# COST_FACTOR = 10000

# URL_FID = 'http://103.226.250.83:9333/dir/assign'
# URL_UPLOAD = 'http://103.226.250.83:8089/'

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


# def remove_accents(s):
#     if not isinstance(s, unicode):
#         s = s.decode('utf-8')
#     return unidecode.unidecode(s)

# def get_merchant(merchant_id):
#     if not isinstance(merchant_id, ObjectId):
#         merchant_id = ObjectId(merchant_id)
#     return DATABASE.merchants.find_one({'_id': merchant_id})

# def new_survey_splash_page(shop_id, survey_type, question, answers, comment, min_point, max_point, active,
#                            auto_popup, photo_name, connect_button):
#     if not isinstance(shop_id, ObjectId):
#         shop_id = ObjectId(shop_id)
#     when = time.time()

#     if min_point and str(min_point) != 'None':
#         min_point = int(min_point)
#     if max_point and str(max_point) != 'None':
#         max_point = int(max_point)
#     question_accent = remove_accents(question)
#     slug = slugify(question_accent.decode('utf-8'))
#     # if not hotspot_method:
#     #     hotspot_method = 'default'
#     # if not default_code:
#     #     default_code = ''
#     return DATABASE.survey_splash_page.insert({
#         'shop_id': shop_id,
#         'survey_type': survey_type,
#         'question': question,
#         'answers': answers,
#         'comment': comment,
#         'min_point': min_point,
#         'max_point': max_point,
#         'active': active,
#         'auto_popup': auto_popup,
#         'photo': photo_name,
#         'connect_button': connect_button,
#         'slug': slug,
#         'when': when
#     })

# def get_survey_item(survey_id):
#     if not isinstance(survey_id, ObjectId):
#         survey_id = ObjectId(survey_id)
#     return DATABASE.survey_splash_page.find_one({'_id': survey_id})

# def update_survey_splash_page(shop_id, survey_id, survey_type=None,
#                               question=None, answers=None, comment=None, min_point=None,
#                               max_point=None, active=None, choose_status=None, step=None, unique_id=None):
#     if not isinstance(shop_id, ObjectId):
#         shop_id = ObjectId(shop_id)
#     if not isinstance(survey_id, ObjectId):
#         survey_id = ObjectId(survey_id)

#     when = time.time()

#     if min_point and str(min_point) != 'None':
#         min_point = int(min_point)
#     if max_point and str(max_point) != 'None':
#         max_point = int(max_point)
#     info = {}
#     if survey_type:
#         info['survey_type'] = survey_type
#     if question:
#         info['question'] = question
#     if answers:
#         info['answers'] = answers
#     if comment:
#         info['comment'] = comment
#     if min_point:
#         info['min_point'] = min_point
#     if max_point:
#         info['max_point'] = max_point
#     if str(active) != 'None':
#         info['active'] = active
#     info['when'] = when
#     if str(choose_status) != 'None' and str(step) != 'None':
#         info['choose_step_' + str(step)] = choose_status
#     if unique_id:
#         info['unique_id'] = unique_id
#     return DATABASE.survey_splash_page.update({
#         'shop_id': shop_id,
#         '_id': survey_id},
#         {'$set': info})

# def init_survey(shop_id_select):
#     survey_1 = {
#         'question': 'Bạn biết tới chúng tôi qua kênh nào?',
#         'survey_type': 'multi_select',
#         'answers': [
#             {'id': 0, 'value': 'Mạng xã hội'},
#             {'id': 1, 'value': 'Bạn bè'},
#             {'id': 2, 'value': 'Nhân viên nhà hàng'},
#             {'id': 3, 'value': 'Website nhà hàng'},
#             {'id': 4, 'value': 'SMS'},
#             {'id': 5, 'value': 'Khác'},
#         ],
#         'connect_button': 'Gửi khảo sát',
#         'photo_name': None
#     }

#     survey_2 = {
#         'question': 'Bạn có sẵn lòng giới thiệu chúng tôi tới bạn bè và đồng nghiệp?',
#         'survey_type': 'one_select',
#         'answers': [
#             {'id': 0, 'value': 'Có'},
#             {'id': 1, 'value': 'Không'},
#         ],
#         'connect_button': 'Gửi khảo sát',
#         'photo_name': None
#     }
#     survey_3 = {
#         'question': 'Bạn đánh giá thế nào về chất lượng phục vụ của chúng tôi?',
#         'survey_type': 'rating',
#         'min_point': '1',
#         'max_point': '5',
#         'connect_button': 'Gửi khảo sát',
#         'photo_name': None
#     }
#     survey_4 = {
#         'question': 'Bạn đánh giá thế nào về sản phẩm của chúng tôi?',
#         'survey_type': 'rating',
#         'min_point': '1',
#         'max_point': '5',
#         'connect_button': 'Gửi khảo sát',
#         'photo_name': None
#     }
#     survey_5 = {
#         'question': 'Bạn là khách du lịch hay địa phương?',
#         'survey_type': 'one_select',
#         'answers': [
#             {'id': 0, 'value': 'Khách địa phương'},
#             {'id': 1, 'value': 'Khách du lịch'},
#         ],
#         'connect_button': 'Gửi khảo sát',
#         'photo_name': None
#     }

#     surveys = [survey_1, survey_2, survey_3, survey_4, survey_5]
#     for sur in surveys:
#         survey_type = sur.get('survey_type')
#         question = sur.get('question')
#         answers = sur.get('answers')
#         min_point = sur.get('min_point')
#         max_point = sur.get('max_point')
#         photo_name = sur.get('photo_name')
#         connect_button = sur.get('connect_button')
#         survey_id= new_survey_splash_page(shop_id=shop_id_select, survey_type=survey_type,
#                                    question=question, answers=answers, comment='',
#                                    min_point=min_point, max_point=max_point, active=True,
#                                    auto_popup='', photo_name=photo_name,
#                                    connect_button=connect_button)
#         survey_item = get_survey_item(survey_id)
#         slug = survey_item.get('slug')
#         unique_string = str(shop_id_select) + str(survey_id) + str(time.time())
#         unique_id = slug + '_' + hashlib.md5(str(unique_string)).hexdigest()
#         long_url = "https://wificrm.vifb.vn/" + unique_id
#         update_survey_splash_page(shop_id_select, survey_id, unique_id=unique_id)
#         # bitly_token = merchant.get('bitly_access_token', '')
#         # if bitly_token and len(bitly_token) > 0:
#         #     try:
#         #         api.update_bitly_url(shop_id_select, survey_id, bitly_token, long_url)
#         #     except:
#         #         pass



# def init_merchant(name, phone, email):
#     info = {}
#     package = init_package()
#     partner = init_partner()
#     name = unicode(name)
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
#     info['company'] = 'Starbucks Viet Nam'
#     pass_login_hash = make_hash('123456A@')
#     info['password'] = pass_login_hash
#     info['package'] = str(package)
#     info['phone'] = phone
#     info['email'] = email
#     info['partner'] = str(partner)
#     info['when'] = time.time()
#     info['update_at'] = time.time()
#     merchant_id = DATABASE.merchants.insert(info)
#     print "-----mer"
#     print merchant_id
#     public = init_wifi_profile('public', merchant_id, '1', '5', '5')
#     private = init_wifi_profile('private', merchant_id, '2', '10', '10')
#     merchant = get_merchant(merchant_id)
#     #tạo địa điểm
#     path = os.getcwd() + '/static/images/logo_stb.png'
#     logo = save_new_file_init(path)
#     list_name_shop = ['Starbucks 1', 'Starbucks 2']
#     for name_shop in list_name_shop:
#         shop_id = init_shop(merchant_id, name_shop, logo)
#         init_wifi_camp_verify(shop_id)
#         init_wifi_camp_return(shop_id)
#         init_tags_profile(merchant_id, 'email_verify', 'email_verify', shop_id=shop_id)
#         init_tags_profile(merchant_id, 'email_notverify', 'email_notverify', shop_id=shop_id)
#         init_tags_profile(merchant_id, 'wifi', 'wifi', shop_id=shop_id)
#         init_survey(shop_id)
        
    

# def init_package():   
#     return DATABASE.package.insert({'name': "Acquire"})

# def init_partner():
#     pass_login_hash = make_hash('123456A@')
#     return DATABASE.dealers.insert({
#         'name': 'Nextify',
#         'slug': 'nextify',
#         'id_login': 'admin',
#         'pass_login': pass_login_hash,
#         'phone': '0902185580',
#         'email': 'tung1@nextify.vn',
#         'address': 'Hà Nội',
#         'contact': '',
#         'role': '',
#         'website': '',
#         'company': '',
#         "tax_code": '',
#         'from_date': '',
#         'to_date': '',
#         'mail_provider': '',
#         'mail_domain': '',
#         'mail_api_key': '',
#         'mail_api_url': '',
#         'captcha_site_key': '',
#         'captcha_secret_key': '',
#         'when': time.time()
#     })

# def save_new_file_init(path):
#     fid = ''
#     response = requests.get(URL_FID)
#     result = response.json()
#     fid = result.get('fid')
#     url1 = URL_UPLOAD + fid
#     headers = {}
#     payload={}
#     files=[
#         ('file',('logo_stb',open(str(path),'rb'),'png'))
#     ]
#     response1 = requests.post(url1, headers=headers, data=payload, files=files)
#     fid = fid.replace(',', '/')
#     return fid

# def init_shop(merchant_id, name_shop, logo):
#     info = {}
#     name_shop = unicode(name_shop)
#     info['name'] = name_shop
#     info['slug'] = slugify(name_shop) 
#     info['logo'] = logo
#     info['email'] = ''
#     info['merchant_id'] = str(merchant_id)
#     info['background'] = ''
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
#     info['plus_login_form'] = {}
#     info['settings_starbucks'] = {
#         'subject_email': 'Xác nhận tài khoản / Verification for Wifi',
#         'expire_authen': '60',
#         'content_email': 'Vui lòng xác nhận tài khoản bằng cách nhấp vào đường dẫn bên dưới. Cảm ơn bạn. Click on the link below to complete verification process. Thanks you.'
#     }
#     shop = DATABASE.shop.insert(info)
#     print "========"
#     print shop
#     return shop


# def init_wifi_camp_verify(shop_id):
#     if not isinstance(shop_id, ObjectId):
#         shop_id = ObjectId(shop_id)
#     new_register_camp = 'Chiến dịch xác thực email'
#     info_camp = {
#         'shop_id': shop_id,
#         'type': 'verify_email',
#         'step_1': 'terms',
#         'step_2': 'collect',
#         'step_3': '0',
#         'step_4': 'connect_success',
#         'group_customer': {
#             'tags_group_customer': [],
#             'min_visit': '',
#             'max_visit': '',
#             'date_type_select': 'week_day',
#             'weekday_sun': True,
#             'weekday_mon': True,
#             'weekday_tue': True,
#             'weekday_wed': True,
#             'weekday_thu': True,
#             'weekday_fri': True,
#             'weekday_sat': True,
#             'min_day': '',
#             'max_day': '',
#             'event_start_picker': '',
#             'event_end_picker': '',
#             'min_hour': '00:00',
#             'max_hour': '23:30',
#         },
#         'create_at': time.time(),
#         'update_at': time.time(),
#         'status': True,
#         'is_birthday': False,
#         'name': new_register_camp
#     }
#     new_register_camp = DATABASE.campaigns.insert(info_camp)
#     details = {
#         'content_connect': '',
#         'connect_button': '',
#         'display_coupon': False,
#         'display_coupon_txt': '',
#         'hotspot_method': 'default',
#         'default_code': '', 
#         'redirect_type': 'website',
#         'auto_website': '/starbucks_connect_success',
#         'auto_popup_ios': '',
#         'auto_popup_android': '',
#         'auto_facebook_page': '',
#         'auto_popup_zalo': '',
#         'auto_popup_insta': '',
#         'auto_facebook_mess': ''
#         }

#     info_connect = {
#         'camp_id': new_register_camp,
#         'type_page': "connect_success",
#         'shop_id': shop_id,
#         'step': '4',
#         'details': details
#     }
#     detail_collect = {
#             'phone': False,
#             'name': True,
#             'birthday': False,
#             'year_birthday': False,
#             'gender': False,
#             'email': True,
#             'welcome_text': '',
#             'welcome_button': False,
#             'birthday_text': False,
#             'phone_require': False,
#             'name_require': True,
#             'birthday_require': False,
#             'gender_require': False,
#             'email_require': True,
#             'year_birthday_require': False,
#             'otp': False,
#             'company': False,
#             'company_require': False,
#             'company_role': False,
#             'company_role_require': False,
#             'vocation': False,
#             'vocation_require': False,
#             'connect_with_facebook': False,
#             'connect_with_zalo': False,
#             'allow_access_friend_zalo': False,
#             'connect_with_messenger': False,
#             'tag': [],
#             'background': ''
#         }
#     info_collect = {
#             'step': '2',
#             'shop_id': shop_id,
#             'type_page': 'collect',
#             'camp_id': new_register_camp,
#             'details': detail_collect
#         }
#     welcome_text_vn = '<p style="text-align: center; "><span style="font-size: 15px; font-family: SoDo;">Chào mừng bạn đến với Starbucks!</span></p><p style="text-align: center; line-height: 1;"><span style="font-size: 15px; font-family: SoDo;"><br></span></p><p style="text-align: justify; "><span style="font-size: 15px; font-family: SoDo;">Làm theo những bước đơn giản sau để truy cập Wifi. Anh/Chị chỉ thực hiện việc này một lần duy nhất và có thể truy cập Wifi trực tiếp ở những lần tiếp theo.</span></p><p><span style="font-size: 15px; font-family: SoDo;"> 1. Nhấp vào "Tôi đồng ý với T&Cs của Starbucks".</span></p><p><span style="font-size: 15px; font-family: SoDo;">2. Đăng ký tên và địa chỉ email của bạn.</span></p><p><span style="font-size: 15px; font-family: SoDo;">3. Kiểm tra email, nhấp vào liên kết để xác thực.</span></p><p style="line-height: 1;"><span style="font-size: 15px; font-family: SoDo;"><br></span></p><p style="text-align: center; "><span style="font-size: 15px; font-family: SoDo;">Bạn đã sẵn sàng!﻿</span><br></p>'

#     welcome_text_eng = '<p style="text-align: center; "><span style="font-family: SoDo;">﻿Welcome to Starbucks!</span></p><p style="text-align: center; line-height: 1;"><span style="font-family: SoDo;"><br></span></p><p style="text-align: justify; "><span style="font-family: SoDo;">Follow these simple steps to access to our Wifi and only do this once. Enjoy direct Wifi access at your next visits.</span></p><p><span style="font-family: SoDo;"> 1. Click "I agree to the company T&Cs".</span></p><p><span style="font-family: SoDo;">2. Register your name and email address.</span></p><p><span style="font-family: SoDo;">3. Check email, click on verify link.</span></p><p style="line-height: 1;"><span style="font-family: SoDo;"><br></span></p><p></p><div style="text-align: center;"><span style="font-family: SoDo; font-size: 0.9375rem;">You are all set!</span></div><p></p>'

#     tcs_vn = '<p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0);"><span>﻿</span><span style="font-size: 11pt; font-family: SoDo;">﻿</span><span lang="vi" style="font-size: 11pt; font-family: SoDo;">Thỏa thuận này quy định các điều khoản và điều kiện</span><span lang="EN-US" style="font-size: 11pt; font-family: SoDo;"> về</span><span lang="vi" style="font-size: 11pt; font-family: SoDo;"> truy cập internet ("Dịch vụ"), </span><span lang="EN-US" style="font-size: 11pt; font-family: SoDo;">mỗi </span><span lang="vi" style="font-size: 11pt; font-family: SoDo;">khách</span><span lang="EN-US" style="font-size: 11pt; font-family: SoDo;"> hàng</span><span lang="vi" style="font-size: 11pt; font-family: SoDo;"> của Starbucks Việt Nam ("chúng tôi") </span><span lang="EN-US" style="font-size: 11pt; font-family: SoDo;">được</span><span lang="vi" style="font-size: 11pt; font-family: SoDo;"> cung cấp </span><span lang="EN-US" style="font-size: 11pt; font-family: SoDo;">sử dụng Dịch vụ trong </span><span lang="vi" style="font-size: 11pt; font-family: SoDo;">1 giờ</span><span lang="EN-US" style="font-size: 11pt; font-family: SoDo;"> phù hợp </span><span lang="vi" style="font-size: 11pt; font-family: SoDo;">với các điều khoản và điều kiện này</span><span lang="EN-US" style="font-size: 11pt; font-family: SoDo;">:</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Phạm vi dịch vụ</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi không khuyến nghị </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">truy cập vào</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> bất kỳ trang web</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> cụ thể</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> nào (hoặc các dịch vụ liên quan đến internet khác) ("Dịch vụ Internet") và việc bạn </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">sẽ chịu trách nhiệm đối với những rủi ro khi </span><span lang="vi" style="font-size: 15px; font-family: SoDo;">sử dụng Dịch vụ Internet</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi không chịu trách nhiệm hoặc kiểm soát </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">D</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">ịch vụ Internet mà bạn truy cập và không đảm bảo rằng bất kỳ </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">D</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">ịch vụ nào đều không có lỗi hoặc vi-rút.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi không chịu trách nhiệm hoặc kiểm soát thông tin bạn truyền hoặc nhận thông qua Dịch vụ</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi không kiểm tra việc sử dụng </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">D</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">ịch vụ</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> của</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> bạn hoặc bản chất của thông tin bạn </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">truyền</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> hoặc nhận cho mục đích chẩn đoán mạng</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi không đảm bảo:</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.5.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Tính khả dụng của Dịch vụ;</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.5.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Tốc độ thông tin có thể được truyền hoặc nhận qua Dịch vụ</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">;</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.5.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Dịch vụ sẽ tương thích với thiết bị của bạn hoặc bất kỳ phần mềm nào bạn sử dụng.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.6.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Trong khi chúng tôi thực hiện các bước hợp lý để đảm bảo tính bảo mật của Dịch vụ và ngăn chặn truy cập bất hợp pháp vào thông tin được truyền hoặc nhận bằng Dịch vụ</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">,</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> chúng tôi không đảm bảo tính bảo mật của thông tin mà bạn có thể truyền hoặc nhận bằng Dịch vụ hoặc nằm trên bất kỳ thiết bị nào sử dụng Dịch vụ và bạn chấp nhận rằng bạn có trách nhiệm bảo vệ thông tin của mình và có bảo mật đầy đủ (về thiết bị và thủ tục) để đảm bảo bảo mật, tính toàn vẹn và bảo mật của thông tin và dữ liệu của bạn.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">1.7.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi bảo lưu quyền </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">tạm dừng</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> Dịch vụ</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> bất kỳ</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> lúc</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> nào</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">, thay đổi thông số kỹ thuật hoặc cách sử dụng Dịch vụ, thay đổi mã truy cập, tên người dùng, mật khẩu hoặc thông tin bảo mật khác cần thiết để truy cập Dịch vụ.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Việc bạn sử dụng dịch vụ</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Bạn không được sử dụng Dịch vụ để truy cập Dịch vụ Internet, hoặc gửi hoặc nhận e-mail, mà:</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Phỉ báng, đe dọa, đe dọa hoặc có thể được phân loại là quấy rối;</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chứa ngôn ngữ hoặc tài liệu tục tĩu hoặc lạm dụng;</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-GB" style="font-size: 15px; font-family: SoDo;">C</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">hứa tài liệu khiêu dâm (đó là văn bản, hình ảnh, phim, video clip có tính chất khiêu dâm hoặc kích thích tình dục);</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">   </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chứa các hình ảnh xúc phạm hoặc liên quan đến tình dục, chủng tộc, tôn giáo, màu da, nguồn gốc, tuổi tác, khuyết tật về thể chất hoặc tinh thần, tình trạng y tế hoặc khuynh hướng tình dục;</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chứa tài liệu vi phạm quyền của bên thứ ba (bao gồm quyền sở hữu trí tuệ);</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.6.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-GB" style="font-size: 15px; font-family: SoDo;">T</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">heo ý kiến hợp lý của chúng tôi, có thể ảnh hưởng xấu đến cách chúng tôi thực hiện kinh doanh của mình; hoặc</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.1.7.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-GB" style="font-size: 15px; font-family: SoDo;">B</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">ất hợp pháp hoặc không phù hợp;</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Âm nhạc, video, hình ảnh, văn bản và nội dung khác trên internet là tác phẩm bản quyền và bạn không nên tải xuống, thay đổi, e-mail hoặc sử dụng nội dung đó trừ khi chắc chắn rằng chủ sở hữu của các tác phẩm đó đã cho phép bạn sử dụng chúng</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi có thể chấm dứt hoặc tạm thời đình chỉ Dịch vụ nếu chúng tôi tin tưởng một cách hợp lý rằng Bạn vi phạm bất kỳ điều khoản nào của thỏa thuận này bao gồm nhưng không giới hạn ở các điều khoản 2.1 đến 2.3 ở trên.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi khuyên bạn không nên sử dụng Service để truyền hoặc nhận bất kỳ thông tin hoặc dữ liệu bí mật nào và nếu bạn chọn làm như vậy, bạn </span><span lang="EN-GB" style="font-size: 15px; font-family: SoDo;">nên chấp nhận rủi ro cho việc này</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">2.5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Dịch vụ chỉ dành cho người tiêu dùng sử dụng. Trong trường hợp bạn sử dụng Dịch vụ cho mục đích thương mại, chúng tôi sẽ giới thiệu cụ thể cho bạn đến khoản 5.</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">b</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> dưới đây.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Hoạt động tội phạm</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoListParagraphCxSpFirst" style="text-align: justify; margin: 0cm 0cm 0cm 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">3.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Bạn không được sử dụng Dịch vụ để tham gia vào bất kỳ hoạt động nào cấu thành hoặc có khả năng cấu thành tội phạm hình sự, ở Việt Nam hoặc ở bất kỳ </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">quốc gia</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> nào trên toàn thế giới.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoListParagraphCxSpMiddle" style="text-align: justify; margin: 0cm 0cm 0cm 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">3.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Bạn đồng ý và thừa nhận rằng bạn có thể được yêu cầu cung cấp </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">thông tin</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">hoặc hỗ trợ</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> cho cơ quan </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">nhà nước có thẩm quyền.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoListParagraphCxSpMiddle" style="text-align: justify; margin: 0cm 0cm 0cm 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">3.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Bạn đồng ý và thừa nhận rằng chúng tôi có thể lưu giữ nhật ký địa chỉ Giao thức Internet ("IP") của bất kỳ thiết bị nào truy cập Dịch vụ, thời gian họ đã truy cập Dịch vụ và hoạt động liên quan đến địa chỉ IP đó</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoListParagraphCxSpLast" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">3.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Bạn cũng đồng ý rằng chúng tôi có quyền hợp tác với các cơ quan </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">nhà nước có thẩm quyền</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> và chủ sở hữu </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">của </span><span lang="vi" style="font-size: 15px; font-family: SoDo;">quyền </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">sở hữu trí tuệ </span><span lang="vi" style="font-size: 15px; font-family: SoDo;">trong việc điều tra bất kỳ hoạt động bất hợp pháp bị nghi ngờ hoặc bị cáo buộc nào của bạn có thể bao gồm, nhưng không giới hạn, tiết lộ thông tin như </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">quy định bên trên</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> (cho dù theo điều khoản 3.</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">c</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> hay cách khác), và </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">được yêu cầu</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> bởi pháp luật</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> hoặc</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> cơ quan</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> nhà nước có thẩm quyền</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> hoặc chủ sở hữu </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">của </span><span lang="vi" style="font-size: 15px; font-family: SoDo;">quyền</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> sở hữu trí tuệ</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi sử dụng thông tin của bạn</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">4.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Theo các điều khoản 3.</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">c</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> và 3.</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">d</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> </span><span lang="vi" style="font-size: 15px; font-family: SoDo;">ở trên, chúng tôi xác nhận rằng chúng tôi sẽ sử dụng các </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">thông tin</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> liên lạc </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">do </span><span lang="vi" style="font-size: 15px; font-family: SoDo;">bạn cung cấp cho chúng tôi chỉ cho mục đích liên hệ với bạn </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">để gửi</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> thông tin tiếp thị</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> và</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> cập nhật</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> các chương trình</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> khuyến mãi và ưu đãi đặc biệt liên quan đến doanh nghiệp của chúng tôi.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;"><span style="font-family: SoDo; font-size: 15px;">4.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;">Bằng cách cung cấp địa chỉ email của bạn ở đây, bạn đồng ý </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;">cho chúng tôi</span><span lang="vi" style="font-size: 15px; font-family: SoDo; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;"> sử dụng địa chỉ email đó để liên lạc với bạn.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif; background: yellow;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Các điều khoản khác</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">5.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Bạn đồng ý bồi thường cho chúng tôi đầy đủ </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">các thiệt hại phát sinh từ </span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> bất kỳ khiếu nại hoặc hành động bất hợp pháp nào được thực hiện hoặc đe dọa chống lại chúng tôi bởi </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">bất kỳ bên thứ 3 nào</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> vì </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">b</span><span lang="vi" style="font-size: 15px; font-family: SoDo;">ạn đã sử dụng Dịch vụ vi phạm các điều khoản và điều kiện này và đặc biệt là khoản 2.</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">a</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> đến 2.</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">c</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> và 3.</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">a</span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;"> </span><span lang="vi" style="font-size: 15px; font-family: SoDo;">ở trên.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">5.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">Mặc dù chúng tôi không tìm cách giới hạn trách nhiệm của mình đối với việc xuyên tạc gian lận </span><span style="background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial; font-family: SoDo; font-size: 15px;">hoặc nếu </span></span><span lang="EN-US" style="font-size: 15px; font-family: SoDo; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;">b</span><span lang="vi" style="font-size: 15px; font-family: SoDo; background-image: initial; background-position: initial; background-size: initial; background-repeat: initial; background-attachment: initial; background-origin: initial; background-clip: initial;">ạn bị thương hoặc chết do sơ suất của chúng tôi, chúng tôi không có trách nhiệm (trong phạm vi được pháp luật cho phép)</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> bồi thường cho bạn (cho dù chúng tôi có sơ suất) cho bất kỳ tổn thất tài chính trực tiếp, mất lợi nhuận, doanh thu, thời gian, tiết kiệm dự kiến hoặc lợi nhuận hoặc doanh thu, cơ hội , dữ liệu, sử dụng, kinh doanh, chi tiêu lãng phí, gián đoạn kinh doanh, tổn thất phát sinh từ việc tiết lộ thông tin bí mật, tổn thất phát sinh từ hoặc liên quan đến việc sử dụng Dịch vụ hoặc không có khả năng sử dụng hoặc truy cập Dịch vụ hoặc thất bại, đình chỉ hoặc rút toàn bộ hoặc một phần Dịch vụ bất cứ lúc nào hoặc thiệt hại cho tài sản vật chất hoặc cho bất kỳ tổn thất trực tiếp tương tự nào khác có thể phát sinh liên quan đến thỏa thuận này cho dù chúng tôi có được thông báo trước về khả năng hay không tổn thất hoặc thiệt hại đó.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">5.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Chúng tôi đồng ý rằng thỏa thuận này không cho phép một trong hai bên hành động như, hoặc cả hai bên tự coi mình là đại lý của bên kia và các điều khoản của thỏa thuận này không được bên thứ ba thực thi.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><span style="font-family: SoDo; font-size: 15px;">5.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="vi" style="font-size: 15px; font-family: SoDo;">Thỏa thuận này được điều chỉnh bởi pháp luật Việt Nam và phải tuân theo thẩm quyền </span><span lang="EN-US" style="font-size: 15px; font-family: SoDo;">riêng biệt</span><span lang="vi" style="font-size: 15px; font-family: SoDo;"> của tòa án Việt Nam.</span><span lang="EN-US" style="font-size: 12.5pt; font-family: "Times New Roman", serif;"><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt; line-height: 15.6933px; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0);"><span lang="vi" style="font-size: 11pt; line-height: 17.8333px; font-family: SoDo;">Tôi xác nhận rằng tôi chấp nhận các điều khoản và điều kiện này</span><span lang="EN-US" style="font-size: 11pt; line-height: 17.8333px; font-family: SoDo;"> để </span><span lang="vi" style="font-size: 11pt; line-height: 17.8333px; font-family: SoDo;">làm cơ sở cho việc tôi sử dụng </span><span lang="EN-US" style="font-size: 11pt; line-height: 17.8333px; font-family: SoDo;">Dịch vụ.</span><span lang="EN-US" style="font-size: 12.5pt; line-height: 17.8333px; font-family: "Times New Roman", serif;"><o:p></o:p></span></p>'


#     tcs_eng = '<p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0);"><span>﻿</span><span>﻿</span><span>﻿</span><span>﻿</span><span>﻿</span><span>﻿</span><span>﻿</span><span style="font-size: 15px;">﻿</span><span style="font-size: 15px;">﻿</span><span style="font-size: 15px;">﻿</span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">This agreement sets out the terms and conditions on which wireless internet access (“the Service”) is provided 1 hour, a guest of Starbucks Vietnam (“us”) in consideration for your custom, your agreement to these terms and conditions:</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Extent of the Service</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We do not recommend in particular the use of any websites (or other internet related services) ("Internet Services") and your use of Internet Services is carried out entirely at your own risk.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We have no responsibility for, or control over, the Internet Services you access and do not guarantee that any services are error or virus free.</span><o:p></o:p></span></p><p class="MsoNormal" style="margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We have no responsibility for, or control over, the information you transmit or receive via the Service</span><o:p></o:p></span></p><p class="MsoNormal" style="margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We do not examine the use to which you put the Service or the nature of the information you send or receive for the purpose of network diagnostics</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We do not guarantee:</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.5.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">The availability of the Service;</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.5.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">The speed at which information may be transmitted or received via the Service</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.5.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">That the Service will be compatible with your equipment or any software which you use.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.6.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Whilst we take reasonable steps to ensure the security of the Service and to prevent unlawful access to information transmitted or received using the Service, we do not guarantee the security of the information which you may transmit or receive using the Service or located on any equipment utilising the Service and you accept that it is your responsibility to protect your information and have adequate security (in terms of equipment and procedures) to ensure the security, integrity and confidentiality of your information and data.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.7.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We reserve the right at all times to withdraw the Service, change the specifications or manner of use of the Service, to change access codes, usernames, passwords or other security information necessary to access the Service.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Your Use of the Service</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">You must not use the Service to access Internet Services, or send or receive e-mails, which:</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.1.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Are defamatory, threatening, intimidatory or which could be classed as harassment;</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.1.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Contain obscene, profane or abusive language or material;</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.1.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">contain pornographic material (that is text, pictures, films, video clips of a sexually explicit or arousing nature);</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.1.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Contain offensive or derogatory images regarding sex, race, religion, colour, origin, age, physical or mental disability, medical condition or sexual orientation;</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">1.1.5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Contain material which infringe third party’s rights (including intellectual property rights);</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.1.6.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">in our reasonable opinion, may adversely affect the manner in which we carry out our business; or</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 61.2pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -25.2pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.1.7.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">    </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">are otherwise unlawful or inappropriate;</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Music, video, pictures, text and other content on the internet are copyright works and you should not download, alter, e-mail or otherwise use such contents unless certain that the owner of such works has authorised their use by you</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We may terminate or temporarily suspend the Service if we reasonably believe that you are in breach of any provisions of this agreement including but not limited to clauses 2.1 to 2.3 above.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We recommend that you do not use the Service to transmit or receive any confidential information or data and should you choose to do so, you do so at your own risk.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">2.5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">The Service is intended for consumer use only. In the event that you use the Service for commercial purposes we would specifically refer you to clause 5.2 below.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Criminal Activity</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">3.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">You must not use the Service to engage in any activity which constitutes or is capable of constituting a criminal offence, either in the Vietnam or in any state throughout the world.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">3.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">You agree and acknowledge that you may be required to provide assistance and information to law enforcement, governmental agencies and other authorities.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">3.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">You agree and acknowledge that we may keep a log of the Internet Protocol (“IP”) addresses of any devices which access the Service, the times when they have accessed the Service and the activity associated with that IP address</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">3.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">You further agree we are entitled to co-operate with law enforcement authorities and rights-holders in the investigation of any suspected or alleged illegal activity by you which may include, but is not limited to, disclosure of such information as we have (whether pursuant to clause 3.3 or otherwise), and are entitled to provide by law, to law enforcement authorities or rights-holders.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Our Use of your Information</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">4.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Subject to clauses 3.3 and 3.4 above we confirm that we shall use the contact details you provide to us solely for the purposes of contacting you with marketing information, updates, promotions and special offers relating to our business.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;="" background-image:="" initial;="" background-position:="" background-size:="" background-repeat:="" background-attachment:="" background-origin:="" background-clip:="" initial;"=""><font color="#000000" style=""><span style="font-family: SoDo; font-size: 15px;">4.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></font></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;="" background-image:="" initial;="" background-position:="" background-size:="" background-repeat:="" background-attachment:="" background-origin:="" background-clip:="" initial;"=""><font color="#000000" style=""><span style="font-family: SoDo; font-size: 15px;">By providing your email address here, you consent to the use of such email address for communicating with you.</span><span style="background-color: yellow;"><o:p></o:p></span></font></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 18pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -18pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">5.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">     </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Other Terms</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">5.1.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">5.1 You agree to compensate us fully for any claims or illegal action made or threatened against us by someone else because you have used the Service in breach of these terms and conditions, and in particular clause 2.1 to 2.3 and 3.1 above.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">5.2.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">Whilst we do not seek to limit our responsibility for fraudulent misrepresentation or if you are injured or die as a result of our negligence, we have no responsibility (to the extent permitted by law) to compensate you (whether or not we are negligent) for any direct financial loss, loss of profit, revenue, time, anticipated savings or profit or revenue, opportunity, data, use, business, wasted expenditure, business interruption, loss arising from disclosure of confidential information, loss arising from or in connection with use of the Service or inability to use or access the Service or a failure, suspension or withdrawal of all or part of the Service at any time or damage to physical property or for any other similar direct loss that may arise in relation to this agreement whether or not we were advised in advance of the possibility of such loss or damage.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">5.3.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">We agree that this agreement does not allow either party to act as, or both parties hold themselves out as, acting as an agent of the other party and that the terms of this agreement are not enforceable by a third party.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt 39.6pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); text-indent: -21.6pt;"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">5.4.</span><span style="font-variant-numeric: normal; font-variant-east-asian: normal; font-stretch: normal; font-size: 15px; line-height: normal; font-family: SoDo;">  </span></span><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">This agreement is governed by the law of Vietnam and is subject to the non-exclusive jurisdiction of the Vietnam courts.</span><o:p></o:p></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0);"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;">I confirm that I accept these terms and conditions as the basis of my use of the wireless internet access provided.</span></span></p><p class="MsoNormal" style="text-align: justify; margin: 0cm 0cm 8pt; line-height: normal; font-size: 11pt; font-family: Calibri, sans-serif; color: rgb(0, 0, 0);"><span lang="EN-US" style="font-size: 12.5pt; font-family: " times="" new="" roman",="" serif;"=""><span style="font-family: SoDo; font-size: 15px;"><br></span><o:p></o:p></span></p>'
    
#     welcome_button_vn = "Tiếp tục"
#     welcome_button_eng = "Continue"
#     term = {
#         'welcome_text_vn': welcome_text_vn,
#         'welcome_text_eng': welcome_text_eng,
#         'tcs_vn': tcs_vn,
#         'tcs_eng': tcs_eng,
#         'welcome_button_vn': welcome_button_vn,
#         'welcome_button_eng':welcome_button_eng
#     }
#     info_step = {
#             'step': '1',
#             'shop_id': shop_id,
#             'type_page': 'terms',
#             'camp_id': new_register_camp,
#             'details': term
#         }   
#     DATABASE.details_step_campaign.insert(info_step)
#     DATABASE.details_step_campaign.insert(info_collect)
#     DATABASE.details_step_campaign.insert(info_connect)


# def init_wifi_camp_return(shop_id):
#     if not isinstance(shop_id, ObjectId):
#         shop_id = ObjectId(shop_id)
    
#     name_return_camp = "Chiến dịch khách hàng quay trở lại"
   

#     details = {
#         'content_connect': '',
#         'connect_button': '',
#         'display_coupon': False,
#         'display_coupon_txt': '',
#         'hotspot_method': 'default',
#         'default_code': '', 
#         'redirect_type': 'website',
#         'auto_website': 'https://www.facebook.com/starbucksvietnam',
#         'auto_popup_ios': '',
#         'auto_popup_android': '',
#         'auto_facebook_page': '',
#         'auto_popup_zalo': '',
#         'auto_popup_insta': '',
#         'auto_facebook_mess': ''
#         }

#     info_default = {
#         'shop_id': shop_id,
#         'type': 'default',
#         'step_1': '0',
#         'step_2': '0',
#         'step_3': '0',
#         'step_4': 'connect_success',
#         'create_at': time.time(),
#         'update_at': time.time(),
#         'group_customer': {
#             'tags_group_customer': [],
#             'min_visit': '',
#             'max_visit': '',
#             'date_type_select': 'week_day',
#             'weekday_sun': True,
#             'weekday_mon': True,
#             'weekday_tue': True,
#             'weekday_wed': True,
#             'weekday_thu': True,
#             'weekday_fri': True,
#             'weekday_sat': True,
#             'min_day': '',
#             'max_day': '',
#             'event_start_picker': '',
#             'event_end_picker': '',
#             'min_hour': '00:00',
#             'max_hour': '23:30',
#             'convert_min_hour': 0,
#             'convert_max_hour': 23.5,
#             'timestamp_start_event': 0,
#             'timestamp_end_event': 0
#         },
#         'status': True,
#         'is_birthday': False,
#         'name': name_return_camp
#     }
#     new_default_camp = DATABASE.campaigns.insert(info_default)
#     info_connect = {
#         'camp_id': new_default_camp,
#         'type_page': "connect_success",
#         'shop_id': shop_id,
#         'step': '4',
#         'details': details
#     }
#     DATABASE.details_step_campaign.insert(info_connect)



# def init_wifi_profile(name, merchant_id, session_timeout, down_bw, up_bw):
#     name = unicode(name)
#     slug = slugify(name)
#     group_radius = str(merchant_id) + '_group_' + str(slug)
#     user_radius = str(merchant_id) + '_user_' + str(slug)
#     if not isinstance(merchant_id, ObjectId):
#         merchant_id = ObjectId(merchant_id)
#     profile = DATABASE.wifi_profile.insert({
#         'merchant_id': merchant_id,
#         'name': name,
#         'slug': slug,
#         'group_radius': group_radius,
#         'user_radius': user_radius,
#         'session_timeout': session_timeout,
#         'down_bw': int(down_bw),
#         'up_bw': int(up_bw),
#         'profile_type': 'Default',
#         'pricing': '',
#         'tags': '',
#         'active': True,
#         'expire': ''
#     })
#     check_user_rad = wifimedia_radius.get_client_radius_by_attr(user_radius, 'User-Profile')
#     if not check_user_rad:
#         wifimedia_radius.insert_client_radius(user_radius, 'User-Profile', user_radius, ':=')
#     check_user_realm = wifimedia_radius.get_client_radius_by_attr(user_radius, 'Rd-Realm')
#     if not check_user_realm:
#         wifimedia_radius.insert_client_radius(user_radius, 'Rd-Realm', 'WIFIMEDIA', ':=')
#     check_user_rd_account = wifimedia_radius.get_client_radius_by_attr(user_radius, 'Rd-Account-Disabled')
#     if not check_user_rd_account:
#         wifimedia_radius.insert_client_radius(user_radius, 'Rd-Account-Disabled', '0', ':=')
#     check_user_rd_cleartext = wifimedia_radius.get_client_radius_by_attr(user_radius, 'Cleartext-Password')
#     if not check_user_rd_cleartext:
#         wifimedia_radius.insert_client_radius(user_radius, 'Cleartext-Password', 'Accept', ':=')
#     check_user_rd_usertype = wifimedia_radius.get_client_radius_by_attr(user_radius, 'Rd-User-Type')
#     if not check_user_rd_usertype:
#         wifimedia_radius.insert_client_radius(user_radius, 'Rd-User-Type', 'user', ':=')
#     if not wifimedia_radius.check_profile_radius(user_radius):
#         wifimedia_radius.insert_profile_radius(user_radius)
#     check_group_rad = wifimedia_radius.check_radius_group(group_radius)
#     if not check_group_rad:
#         wifimedia_radius.insert_radius_group(group_radius, 'Auth-Type', 'Accept', ':=')

#         wifimedia_radius.insert_profile_component_radius(group_radius)
#     check_user_in_group = wifimedia_radius.check_user_in_group(user_radius, group_radius)
#     if not check_user_in_group:
#         wifimedia_radius.add_clients_to_radius_group(user_radius, group_radius, 1)
#     up_bw = int(up_bw) * 1000000
#     down_bw = int(down_bw) * 1000000
#     session_timeout = int(session_timeout) * 60
#     check_group_reply_session_timeout = wifimedia_radius.check_group_reply(group_radius, 'Session-Timeout')
#     if not check_group_reply_session_timeout:
#         wifimedia_radius.add_radius_group_reply(group_radius, 'Session-Timeout', session_timeout)
#     check_group_reply_up_bw = wifimedia_radius.check_group_reply(group_radius, 'WISPr-Bandwidth-Max-Up')
#     if not check_group_reply_up_bw:
#         wifimedia_radius.add_radius_group_reply(group_radius, 'WISPr-Bandwidth-Max-Up', up_bw)
#     check_group_reply_down_bw = wifimedia_radius.check_group_reply(group_radius, 'WISPr-Bandwidth-Max-Down')
#     if not check_group_reply_down_bw:
#         wifimedia_radius.add_radius_group_reply(group_radius, 'WISPr-Bandwidth-Max-Down', down_bw)
#     check_group_reply_fall = wifimedia_radius.check_group_reply(group_radius, 'Fall-Through')
#     if not check_group_reply_fall:
#         wifimedia_radius.add_radius_group_reply(group_radius, 'Fall-Through', 'Yes')
#     return profile

# def init_tags_profile(merchant_id, name, description, shop_id=None):
#     if not isinstance(merchant_id, ObjectId):
#         merchant_id = ObjectId(merchant_id)
#     if shop_id:
#         if not isinstance(shop_id, ObjectId):
#             shop_id = ObjectId(merchant_id)
#         return DATABASE.tags.insert({
#             'shop_id': shop_id,
#             'merchant_id': merchant_id,
#             'name': name,
#             'description': description,
#             'when': time.time()
#         })
#     else:
#         return DATABASE.tags.insert({
#             'merchant_id': merchant_id,
#             'name': name,
#             'description': description,
#             'when': time.time()
#         })
    
# # path = '/static/images/logo_sb.png'
# # save_new_file_init(path)
# name = "Starbucks Init"
# phone = "0969654321"
# email = 'nguyenvanson741ah@gmail.com'
# init_merchant(name, phone, email)
# merchant_id = '60e3eb8f414de3029f6eaa9f'
# DATABASE.dealers.remove({'name': 'Nextify_test'})
# DATABASE.package.remove({'name': "Acquire_test"})
# DATABASE.merchants.remove({'_id': ObjectId(merchant_id)})
# DATABASE.wifi_profile.remove({ 'merchant_id': ObjectId(merchant_id)})
# shops = DATABASE.shop.find({'merchant_id': merchant_id})
# for shop in shops:
#     shop_id = shop.get('_id')
#     camps = DATABASE.campagins.find({'shop_id': shop_id})
#     DATABASE.campagins.remove({'shop_id': shop_id})
#     for camp in camps:
#         camp_id = camp.get('_id')
#         DATABASE.details_step_campaign.remove({'camp_id': camp_id})
#     DATABASE.shop.remove({'_id': shop_id})
# print "done"
