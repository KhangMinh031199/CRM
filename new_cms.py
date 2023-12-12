#! coding: utf-8
from ast import Return
import base64
import email.message
import hashlib
import hmac
import io
import json
import math
import os
import random
import smtplib
import string
import sys
import time
from datetime import datetime, timedelta
from functools import wraps
from uuid import uuid4
import arrow
import avinit
import chartkick
import dateparser
import flask_excel as excel
import requests
import sendgrid
from bson.objectid import ObjectId
from dateutil.parser import parse
from email.mime.multipart import MIMEMultipart
from flask import (Flask, request, render_template, session, redirect, g,
                   Blueprint, url_for, abort, Response, send_from_directory,
                   jsonify)
from flask_session import Session
from flask_assets import Environment
from flask_babel import Babel, gettext
from flask_basicauth import BasicAuth
from flask_bootstrap import Bootstrap
from flask_compress import Compress
from flask_cors import CORS, cross_origin
from flask_oauthlib.client import OAuth, OAuthException
from flask_paginate import Pagination
from flask_seasurf import SeaSurf
from flask_talisman import Talisman
from itsdangerous import URLSafeTimedSerializer
from pytz import timezone
from sendgrid.helpers.mail import *
from slugify import slugify
from validate_email import validate_email
from werkzeug.contrib.fixers import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import CallbackDict
import CRM_Retailer_KiotViet
import activity_history
import api
import api_wifi_access_code
import email_api
import fb_api
import fnb_kiotviet
import gift_card_api
import handle_customers
import init_automation_template
import mongo_search
import rating
import save_customers
import search_engine
import settings
import sms_api
import storage_api
import viettel_ads_api
from email_api import send_by_mail_gun
from mongo_connect import *
from flask_session_captcha import FlaskSessionCaptcha
import overview
import re
from kafka import KafkaProducer
import ssl
import api_ghdc
import haravan_api
import companies
import groups
import segments
import automation

app = Flask(__name__)

CORS(app)
app.secret_key = 'foobar'

s = URLSafeTimedSerializer(app.secret_key)
#URLSafeTimedSerializer là một công cụ giúp tạo và kiểm tra các token an toàn với thời gian.

# app.wsgi_app = ProxyFix(app.wsgi_app)
Compress(app)

cache = {}
ck = Blueprint('ck_page',
               __name__,
               static_folder=chartkick.js(),
               static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")
#Thư viện hỗ trợ vẽ đồ thị nhanh

app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['BOOTSTRAP_QUERYSTRING_REVVING'] = True
Bootstrap(app)
assets = Environment(app)

app.config['BASIC_AUTH_USERNAME'] = 'nextify'
app.config['BASIC_AUTH_PASSWORD'] = 'dungtamthoinhe'
basic_auth = BasicAuth(app)

app.config['UPLOAD_FOLDER'] = '/srv/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.jinja_env.cache = {}

app.config['CAPTCHA_ENABLE'] = True
app.config['CAPTCHA_LENGTH'] = 5
app.config['CAPTCHA_WIDTH'] = 160
app.config['CAPTCHA_HEIGHT'] = 60

app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
import redis

app.config['SESSION_REDIS'] = redis.from_url('redis://@127.0.0.1:6379')
sess = Session()
sess.init_app(app)

captcha = FlaskSessionCaptcha(app)

babel = Babel(app)

NODOGSPLASH_URL = settings.NODOGSPLASH_URL

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_locale():
    return request.cookies.get("langs", "vi")


babel.localeselector(get_locale)
app.jinja_env.globals["get_locale"] = get_locale
#lấy ngôn ngữ hiện tại từ cookie. Sau đó, nó được sử dụng để cấu hình Flask-Babel để xác định ngôn ngữ hiện tại. Cả hai đều giúp ứng dụng hỗ trợ đa ngôn ngữ.

csrf = SeaSurf(app)
#SeaSurf là một extension cung cấp bảo vệ CSRF (Cross-Site Request Forgery). Nó giúp ngăn chặn các cuộc tấn công CSRF bằng cách tạo và kiểm tra token CSRF cho mỗi yêu cầu.
SELF = "'self' blob: data:"
talisman = Talisman(
    app,
    force_https=False,
    content_security_policy={
        'default-src': [
            SELF, '\'unsafe-inline\'', '\'unsafe-eval\'',
            'fonts.googleapis.com', 'use.fontawesome.com',
            'cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'fonts.gstatic.com',
            'static.nextify.vn', 'https://grandstream.nextify.vn:8443',
            'staging.nextify.vn', 'mcare.mobifone.vn', 'mobifone.vn',
            '*.google.com', '*.maxsolution.team', '*.leeon.vn', 'reactjs.org',
            'tinymce.com', 'www.google.com', '*.github.com', '*.nextify.co',
            'unlayer.com', 'maxcdn.bootstrapcdn.com', 'adminapi.unlayer.com',
            '*.nextify.vn', '*.facebook.com', 'http://0.0.0.0:8097/graphql',
            'https://report.nextify.vn/graphql',
            'http://127.0.0.1:8097/graphql', '*.fbcdn.net', 'dribbble.com',
            'gitcdn.github.io', '*.unlayer.com', 'mybusiness.googleapis.com',
            'https://connect.facebook.net/vi_VN/sdk.js', 'apis.google.com',
            '*.gogleapis.com', 'unitel.com.la', 'googleapis.com',
            'www.youtube.com', 'www.googleapis.com', 'https://app.woay.vn/',
            'http://wifi.gobydigital.vn',
            'https://cdn.zingchart.com/zingchart.min.js', 'quilljs.com',
            '*.quilljs.com'
        ],
        'img-src':
        '* data:',
        'object-src': [
            '*',
            '\'unsafe-eval\'',
        ],
        'script-src': [
            '\'unsafe-inline\'', '\'self\'', '\'unsafe-eval\'',
            'ajax.googleapis.com', 'https://grandstream.nextify.vn:8443',
            'http://0.0.0.0:8097/graphql', 'use.fontawesome.com',
            '*.google.com', '*.github.com', '*.nextify.co',
            '*.maxsolution.team', '*.leeon.vn', '*.unitel.com.la',
            'www.google.com', 'www.youtube.com', 'fonts.googleapis.com',
            'code.jquery.com', '*.gstatic.com', 'cdnjs.cloudflare.com',
            'cdn.jsdelivr.net', 'cdn.ckeditor.com', 'unpkg.com', 'unlayer.com',
            'adminapi.unlayer.com',
            'https://connect.facebook.net/en_US/sdk.js', 'gitcdn.github.io',
            '*.unlayer.com', '*.fonts.net', '*.driftt.com', '*.drift.com',
            '*.driftqa.com', '*.fontdeck.com',
            'https://connect.facebook.net/vi_VN/sdk.js',
            'maxcdn.bootstrapcdn.com', 'cdn1.swipewifi.com', '*.nextify.vn',
            '*.facebook.com', 'dribbble.com', 'https://app.woay.vn/',
            'http://wifi.gobydigital.vn',
            'https://cdn.zingchart.com/zingchart.min.js', 'quilljs.com',
            '*.quilljs.com'
        ],
        'font-src': [
            '* data:',
            'fonts.googleapis.com',
            'use.fontawesome.com',
        ]
    })

# class MongoSession(CallbackDict, SessionMixin):

#     def __init__(self, initial=None, sid=None):
#         CallbackDict.__init__(self, initial)
#         self.sid = sid
#         self.modified = False

# class MongoSessionInterface(SessionInterface):

#     def __init__(self):

#         MONGODB = mongodb_create()

#         DATABASE = MONGODB["session_db"]
#         DATABASE.authenticate(
#             "session",
#             "7PVEPwPg6mcls871",
#             source="session_db")
#         self.store = DATABASE["session"]

#     def open_session(self, app, request):
#         sid = request.cookies.get(app.session_cookie_name)
#         if sid:
#             stored_session = self.store.find_one({'sid': sid})
#             if stored_session:
#                 if stored_session.get('expiration') > datetime.utcnow():
#                     return MongoSession(initial=stored_session['data'],
#                                         sid=stored_session['sid'])
#         sid = str(uuid4())
#         return MongoSession(sid=sid)

#     def save_session(self, app, session, response):
#         domain = self.get_cookie_domain(app)
#         if not session:
#             response.delete_cookie(app.session_cookie_name, domain=domain)
#             return
#         if self.get_expiration_time(app, session):
#             expiration = self.get_expiration_time(app, session)
#         else:
#             expiration = datetime.utcnow() + timedelta(hours=1)
#         self.store.update({'sid': session.sid},
#                           {'sid': session.sid,
#                            'data': session,
#                            'expiration': expiration}, True)
#         response.set_cookie(app.session_cookie_name, session.sid,
#                             expires=self.get_expiration_time(app, session), domain=domain)


# kafka producer
def get_kafka_producer():
    return KafkaProducer(bootstrap_servers=settings.KAFKA_IP + ":9092")

producer = get_kafka_producer()
# app.session_interface = MongoSessionInterface()
oauth = OAuth(app)
facebook = oauth.remote_app(
    'facebook',
    consumer_key="981718895315274",
    consumer_secret="e8aadcfdb23395426945b30b679f8934",
    request_token_params={
        'scope':
        'email,user_birthday,user_hometown,user_relationships,publish_actions'
    },
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth')

FPT_URL = 'http://service.sms.fpt.net/'
FPT_URL_SANBOX = 'http://sandbox.sms.fpt.net/'


@app.template_filter('get_real_url_fb')
def real_url_fb(graph_url):
    resp = requests.get(graph_url)
    req_json = resp.json()
    picture = req_json.get('picture')
    url = None
    if picture:
        data = picture.get('data')
        if data:
            url = data.get('url')
    return url


@app.template_filter('capwords')
def format_datetime(value):
    return ' '.join([
        word.capitalize() if not word.isupper() else word
        for word in value.split()
    ])


@app.template_filter('format_time_hour')
def format_time_hour(value):
    str_hour = int(int(value) / 3600)
    str_min = (int(value) - str_hour * 3600) / 60
    return str(str_hour) + "h" + str(str_min) + "m"


@app.template_filter('jinja_currency_format')
def jinja_currency_format(value):
    if not isinstance(value, float):
        value = float(value)
    return '{:0,.0f}'.format(value).replace('$-', '-$')


@app.template_filter('human_time')
def format_human_time(value):
    if value:
        try:
            if str(request.cookies.get("langs")) == 'lo':
                return arrow.get(value).to('Asia/Ho_Chi_Minh').humanize(
                    locale='en')
            else:
                return arrow.get(value).to('Asia/Ho_Chi_Minh').humanize(
                    locale='vi_vn')
        except:
            return value
    else:
        return value


@app.template_filter('format__date_pick')
def format__date_pick(date_send):
    date_send = str(date_send)
    date_send = date_send.split(" ")
    result = date_send[1][:-3] + " " + "-".join(date_send[0].split("-")[::-1])
    return result


@app.template_filter('human_avatar')
def human_avatar(user):
    avatar = user.get('avatar', '')
    name = user.get('name', '')
    default_ava = '/static/v2/assets/img/medium-default-avatar.png'
    if not avatar or len(avatar) == 0 or str(avatar) == 'None':
        if name and len(name) > 0:
            default_ava = avinit.get_avatar_data_url(name)
    return default_ava


@app.template_filter('user_tag')
def user_tag(merchant_id_user_id):
    merchant_id_user_id_arr = merchant_id_user_id.split(',')
    merchant_id = merchant_id_user_id_arr[0]
    user_id = merchant_id_user_id_arr[1]
    user_tags_details = []
    try:
        user_tags = api.get_user_tags(merchant_id, user_id)
        if user_tags:
            user_tag = user_tags.get('tags')
            try:
                for tag in user_tag:
                    tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                    if tag_db:
                        user_tags_details.append(tag_db)
            except:
                pass
    except:
        pass
    return user_tags_details


@app.template_filter('human_birthday')
def human_birthday(user_birthday):
    birthday = ''
    if user_birthday and len(user_birthday) > 0 and str(
            user_birthday) != 'None':
        birthday_arr = user_birthday.split('-')
        if len(birthday_arr) == 2:
            birthday = birthday_arr[1] + '-' + \
                birthday_arr[0]
            return birthday

        elif len(birthday_arr) == 3:
            return user_birthday
        else:
            return user_birthday
    else:
        return birthday


@app.template_filter('jinja_get_human_time')
def jinja_get_human_time(time_):
    creat_time = datetime.utcfromtimestamp(time_ +
                                           7 * 3600).strftime('%d-%m-%Y')
    return creat_time


@app.template_filter('get_human_time')
def get_human_time(time_):
    creat_time = datetime.utcfromtimestamp(time_ + 7 *
                                           3600).strftime('%H:%M  %d-%m-%Y')
    return creat_time


@app.template_filter('jinja_get_status_call')
def jinja_get_status_call(merchant_id):
    if merchant_id:
        try:
            user_login = g.user
            id_login = user_login.get("_id")
            if str(id_login) == str(merchant_id):
                app_synchronized = api.get_app_synchronized(
                    merchant_id=str(merchant_id),
                    type_app="CALL",
                    status="True")
                if app_synchronized:
                    info = app_synchronized.get('setting').get('info')
                    if info:
                        for item in info:
                            if item.get('role_account') == "3":
                                return item.get('status_account')
            else:
                app_synchronized = api.get_app_synchronized(
                    merchant_id=str(merchant_id),
                    type_app="CALL",
                    staus="True")
                if app_synchronized:
                    info = app_synchronized.get('setting').get('info')
                    if info:
                        for item in info:
                            if item.get('account_id') == str(id_login):
                                return item.get('status_account')
        except:
            return ''
    else:
        return ''


@app.template_filter('jinja_get_name_app')
def jinja_get_name_app(merchant_id):
    if merchant_id:
        app_synchronized = api.get_app_synchronized(
            merchant_id=str(merchant_id), type_app="CALL", status="True")
        if app_synchronized:
            return app_synchronized.get('name_app')
        else:
            return ''
    else:
        return ''


@app.template_filter('cut_name_post')
def cut_name_post(string_format):
    if len(string_format) > 120:
        string_format = string_format.split(' ')
        return " ".join(string_format[:17]) + " ..."
    else:
        return string_format


@app.template_filter('cut_name_question')
def cut_name_question(string_format):
    if len(string_format) > 20:
        string_format = string_format.split(' ')
        return " ".join(string_format[:5])
    else:
        return string_format


@app.template_filter('cut_review')
def cut_name_post(string_format):
    if len(string_format) > 170:
        string_format = string_format.split(' ')
        return " ".join(string_format[:30]) + " ..."
    else:
        return string_format


@app.template_filter('divison_percent')
def divison_percent(num):
    return num * 0.01


@app.template_filter('convert_gender')
def convert_gender(string):
    if string == "female":
        return 'Nữ'
    elif string == "male":
        return 'Nam'
    else:
        return 'Không xác định'


@app.template_filter('jinja_get_domain')
def jinja_get_domain(merchant_id):
    if merchant_id:
        app_synchronized = api.get_app_synchronized(
            merchant_id=str(merchant_id), type_app="CALL", status="True")
        if app_synchronized:
            info = app_synchronized.get('setting').get('info')
            if info:
                for item in info:
                    return item.get('domain')
    else:
        return ''


@app.template_filter('jinja_get_extentions')
def jinja_get_extentions(merchant_id):
    if merchant_id:
        app_synchronized = api.get_app_synchronized(
            merchant_id=str(merchant_id), type_app="CALL", status="True")
        if app_synchronized:
            info = app_synchronized.get('setting').get('info')
            if info:
                for item in info:
                    return item.get('extentions')
    else:
        return ''


@app.template_filter('jinja_get_api_key')
def jinja_get_extentions(merchant_id):
    if merchant_id:
        app_synchronized = api.get_app_synchronized(
            merchant_id=str(merchant_id), type_app="CALL", status="True")
        if app_synchronized:
            return app_synchronized.get('api_key')
        else:
            return ''
    else:
        return ''


@app.template_filter('jinja_get_number')
def jinja_get_number(merchant_id):
    if merchant_id:
        try:
            user_login = g.user
            id_login = user_login.get("_id")
            if str(id_login) == str(merchant_id):
                app_synchronized = api.get_app_synchronized(
                    merchant_id=str(merchant_id), name_app="vcall")
                if app_synchronized:
                    info = app_synchronized.get('setting').get('info')
                    if info:
                        for item in info:
                            if item.get('role_account') == "3":
                                return item.get('authen_name')
            else:
                app_synchronized = api.get_app_synchronized(
                    merchant_id=str(merchant_id), name_app="vcall")
                if app_synchronized:
                    info = app_synchronized.get('setting').get('info')
                    if info:
                        for item in info:
                            if item.get('account_id') == str(id_login):
                                return item.get('authen_name')
        except:
            return ''
    else:
        return ''


@app.template_filter('jinja_get_token')
def jinja_get_token(merchant_id):
    if merchant_id:
        try:
            user_login = g.user
            id_login = user_login.get("_id")
            if str(id_login) == str(merchant_id):
                app_synchronized = api.get_app_synchronized(
                    merchant_id=str(merchant_id), name_app="vcall")
                if app_synchronized:
                    info = app_synchronized.get('setting').get('info')
                    if info:
                        for item in info:
                            if item.get('role_account') == "3":
                                return item.get('token')
            else:
                app_synchronized = api.get_app_synchronized(
                    merchant_id=str(merchant_id), name_app="vcall")
                if app_synchronized:
                    info = app_synchronized.get('setting').get('info')
                    if info:
                        for item in info:
                            if item.get('account_id') == str(id_login):
                                return item.get('token')
        except:
            return ''
    else:
        return ''


@app.template_filter('human_time_string')
def format_human_time_string(value):
    if value:
        try:
            return arrow.get(value).to('Asia/Ho_Chi_Minh').format(
                'DD-MM-YYYY HH:mm:ss')
        except:
            return ''
    else:
        ''


@app.template_filter('format_price')
def format_price(price):
    if str(price).isdigit():
        price = int(str(price).replace('.00', ''))
        return "{:,}".format(int(price))
    else:
        ''


@app.template_filter('shop_is_merchant')
def check_shop_in_merchant(shop):
    merchant_id = shop.get('merchant_id')
    isHQ = True if merchant_id and merchant_id != '0' else False
    if isHQ:
        merchant = api.get_merchant(merchant_id)
        return merchant
    else:
        return False


@app.template_filter('shops_in_merchant')
def get_shops_in_merchant(merchant_id):
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [shop['_id'] for shop in shop_in_mer]
    shops = [api.get_shop_info(i) for i in shop_ids]
    return shops


@app.template_filter('shop_info')
def get_shop_info(shop_id):
    return api.get_shop_info(shop_id=shop_id)


@app.template_filter('get_old_reward')
def get_old_reward(old_reward):
    result = old_reward
    if result.get('is_reward') in ['code', 'vnpay', 'gift']:
        result_detail = result.get('detail')
        if result_detail:
            return result_detail
        else:
            return result.get('title')
    else:
        return ''


@app.template_filter('get_old_reward_img')
def get_old_reward_img(old_reward):
    result = old_reward
    if result.get('is_reward') in ['gift']:
        return result.get('images')
    else:
        return ''


@app.template_filter('get_package_merchant')
def get_package_merchant(merchant_id):
    return api.get_package_by_merchant_id(merchant_id)


@app.template_filter('package_merchant')
def package_merchant(merchant_id):
    return api.get_name_package_by_merchant_id(merchant_id)


@app.template_filter('shop_name')
def jinja_get_shop_name(shop_id):
    return api.get_shop_info(shop_id=shop_id).get('name')


@app.template_filter('is_great_time_than')
def is_great_time_than(time_str):
    try:
        time_format = parse(time_str)
        return time_format > \
            datetime.today()
    except Exception as e:
        return False


@app.template_filter('format_birthday')
def format_birthday(birthday):
    birth = ''
    if birthday is not None and len(birthday) > 0:
        births = birthday.split('-')
        if len(births) > 0:
            try:
                birth = births[1] + '-' + births[0]
            except Exception as e:
                birth = ''

    return birth


@app.template_filter('getkey')
def getkey(py_list):
    for ke, va in py_list.items():
        return ke


@app.template_filter('getitem')
def getitem(py_list):
    for ke, va in py_list.items():
        return va


@app.template_filter('format_list_json')
def format_list_json(py_list):
    return json.dumps(py_list)


@app.template_filter('format_mac_device')
def format_mac_device(mac):
    return api.get_device_info(str(mac).upper())


@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    if 'static' == endpoint:
        filename = values.get('filename')
        if filename:
            static_folder = app.static_folder

            filename = os.path.join(static_folder, filename)
            if os.path.isfile(filename):
                values['t'] = int(os.stat(filename).st_mtime)


@app.template_filter('handle_jinja_list')
def handle_jinja_list(jinja_list):
    output = []
    if jinja_list:
        for item in jinja_list:
            output.append(str(item))
        return output
    return ""


@app.template_filter('sort_list_age')
def sort_list(list_age):
    result = sorted(list_age, key=lambda i: i['age'])
    return result


@app.template_filter('round_float')
def round_float(num):
    try:
        num = float(num)
        return round(num, 1)
    except:
        return num[:3]


@app.template_filter('format_to_picker')
def format_time_stamp_to_picker(tmp_stamp):
    return datetime.fromtimestamp(int(tmp_stamp)).strftime('%Y-%m-%d %H:%M')


@app.template_filter('num_shops_in_merchant')
def count_shop_in_merchant(merchant_id):
    return len(api.get_shop_by_merchant(str(merchant_id)))


@app.template_filter('md5_hash')
def md5_hash(value):
    m = hashlib.md5()
    m.update(value)
    return m.hexdigest()


@app.template_filter('cut_dot')
def cut_dot(value):
    arr1 = value.split(".")
    return arr1[0]


@app.template_filter('get_device_name')
def get_device_name(value):
    value = str(value)
    if value == "tplink":
        result = "Tp-Link"
    elif value == "pfsense":
        result = "pfSense"
    else:
        result = value.capitalize()
    return result


@app.template_filter('show_tag_name_splash_page')
def show_tag_name_splash_page(tags):
    tags_name = []
    if tags:
        if len(tags) > 0:
            for tag in tags:
                tag_item = api.get_tag_by_id(tag)
                tag_name = []
                if tag_item:
                    tag_name = tag_item.get('name')
                    tags_name.append(tag_name)
    return tags_name


@app.template_filter('get_dealer_id')
def get_dealer_id(merchant_id):
    merchant = api.get_merchant(merchant_id)
    partner = merchant.get('partner')
    dealer_name = api.get_dealer_by_id(partner)
    if dealer_name:
        return str(dealer_name.get("_id"))
    return ""


@app.template_filter('anphat_basic_package')
def anphat_basic_package(merchant):
    package = merchant.get('package')
    partner = merchant.get('partner')
    dealer_name = api.get_dealer_by_id(partner)
    if dealer_name:
        dealer_name = api.get_dealer_by_id(partner).get('slug')
        if dealer_name == 'an-phat':
            package = api.find_package_fee_by_id(package).get('name')

            return package


@app.template_filter('source_tags')
def source_tags(cus_id):
    source_tags = []
    customer = api.get_cus_by_id(cus_id)
    if not customer:
        customer = api.get_cus_loc_by_id(cus_id)
    else:
        customer = api.get_cus_by_id(cus_id)

    merchant_id = customer.get('merchant_id')
    user_id = customer.get('user_id')
    shop_id = ""
    if not merchant_id:
        shop_id = customer.get('shop_id')
        shop = api.get_shop_info(shop_id=shop_id)
        merchant_id = shop.get('merchant_id')
    user_tags = api.get_user_tags(merchant_id, user_id)
    if user_tags:
        user_tag = user_tags.get('tags')
        try:
            for tag in user_tag:
                tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                if tag_db:
                    tags_id = tag_db.get('_id')
                    # source_tags.append(str(tag))
                    source_tags.append(tags_id)
        except:
            pass
    return source_tags


@app.template_filter('get_top_domain')
def get_top_domain(host_domain):
    hosts = host_domain.split('.')
    if len(hosts) < 2:
        return host_domain
    top_domain = ''
    if len(hosts) == 4:
        top_domain = hosts[len(hosts) - 3] + '.' + \
            hosts[len(hosts) - 2] + '.' + hosts[len(hosts) - 1]
    else:
        top_domain = hosts[len(hosts) - 2] + '.' + hosts[len(hosts) - 1]
    return top_domain


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        phone = session.get('is_login')
        is_hq = session.get('is_hq')
        is_slug_login = session.get('is_slug_login')
        is_superuser = session.get('is_superuser')
        merchant_id = session.get('merchant_id')
        shop_id = session.get('shop_id')
        user = None
        super_user = api.get_super_user()
        merchant = api.get_merchant(merchant_id)
        if phone and merchant:
            if merchant_id and is_hq:
                is_email = validate_email(phone)
                is_slug = api.validate_slug(phone)
                if is_email:
                    merchant = api.get_merchant_by_email(phone)
                    if is_slug_login:
                        user_sup  = api.get_merchant_by_sup_account_email(merchant_id, phone)
                        if user_sup:
                           merchant = api.get_merchant(user_sup.get('merchant_id'))
                elif is_slug:
                    merchant = api.get_merchant_by_slug(phone)
                else:
                    merchant = api.get_merchant_by_phone(phone)
                    if is_slug_login:
                        user_sup = api.get_merchant_by_sup_account_phone(merchant_id, phone)
                        if user_sup:
                           merchant = api.get_merchant(user_sup.get('merchant_id'))
                if merchant:
                    shop_in_mer = api.get_shop_by_merchant(str(
                        merchant['_id']))
                    shop_ids = [shop['_id'] for shop in shop_in_mer]
                    g.shops = [api.get_shop_info(i) for i in shop_ids]
                    g.merchant = merchant
                    session['is_superuser'] = phone
                    session['merchant_id'] = str(merchant['_id'])
                    if len(g.shops) > 0:
                        g.shop = g.shops[0]
                        g.shop_id = g.shops[0]['_id']
                    else:
                        return redirect(url_for('setup_first_login'))
                    if is_superuser and is_superuser == super_user.get(
                            'phone'):
                        g.user = super_user
                        g.role = '3'
                    else:
                        g.user = merchant
                        merchant['roles'] = '3'
                        g.role = '3'
                else:
                    session['redirect_to'] = request.url
                    return redirect('/login')
            else:
                slug = merchant.get('slug')
                is_email = validate_email(phone)
                user = api.get_account_merchant_email(
                    str(merchant.get('_id')), phone) if is_email else \
                    api.get_account_merchant_phone(str(merchant.get('_id')),
                                                   phone)
                if user:
                    shop_in_mer = api.get_shop_by_merchant(str(
                        merchant['_id']))
                    shop_ids = [shop['_id'] for shop in shop_in_mer]
                    g.shops = [api.get_shop_info(i) for i in shop_ids]
                    g.merchant = merchant
                    session['is_superuser'] = phone
                    session['merchant_id'] = str(merchant['_id'])
                    session.pop('is_hq', None)
                    if len(g.shops) > 0:
                        g.shop = g.shops[0]
                        g.shop_id = g.shops[0]['_id']
                    else:
                        return redirect(url_for('setup_first_login'))
                    if is_superuser and is_superuser == super_user.get(
                            'phone'):
                        g.user = super_user
                    else:
                        g.user = user
                    g.role = user.get('roles')
                    if user.get('roles') == '1':
                        locations = user.get('shops', [])
                        g.locations = locations
                    else:
                        g.locations = shop_ids
                else:
                    redirect_uri = '/' + slug
                    return redirect(redirect_uri)
        else:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated_function


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_login = g.user
    if request.method == 'GET':
        merchant_id = session.get('merchant_id')
        merchant = g.merchant
        if merchant and merchant_id and str(merchant.get('_id')) \
                == str(merchant_id):
            shop_in_mer = api.get_shop_by_merchant(str(merchant['_id']))
            shop_ids = [shop['_id'] for shop in shop_in_mer]

            shops = []
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                    shops.append(shop_mer['_id'])
            if len(shop_ids) > 0:
                user_login = g.user
                role = g.role
                name_package = api.get_name_package_by_merchant_id(merchant_id)
                if name_package and name_package == "Brand":
                    return redirect('/hotspot')
                if role == '3':
                    shop_in_mer = api.get_shop_by_merchant(merchant['_id'])
                    merchant_id = merchant['_id']
                    if not isinstance(merchant_id, ObjectId):
                        merchant_id = ObjectId(merchant_id)
                    check = api.check_reset_password(merchant_id)
                    if check:
                        return redirect('/settings')
                    return redirect('/home')
                elif role == '1':
                    locations = g.locations
                    if len(locations) > 0:
                        return redirect('/customers?loc_id=%s' %
                                        (str(locations[0])))
                    else:
                        slug = merchant.get('slug')
                        return redirect('/%s/log_out' % (slug))
                elif role == '2':
                    return redirect('/coupons')
                elif role == '4':
                    return redirect('/hotspot')
            else:
                return redirect(url_for('setup_first_login'))
        else:
            session.pop('is_login', None)
            session.pop('is_superuser', None)
            session.pop('shop_id', None)
            session.pop('is_hq', None)
            return render_template("nextify/login.html")
    else:
        phone = request.form.get('phone')
        password = request.form.get('password')
        language = request.form.get('language')
        if not language:
            language = 'vn'
        session['lang'] = language
        if not phone or not password or len(phone) == 0 or len(password) == 0:
            error = gettext("Thong_tin_dang_nhap_khong_dung.")
            return render_template("nextify/login.html", error=error)
        is_sale_men = api.check_is_sales_person(phone, password)
        if is_sale_men:
            sale_redirect = '/sales/%s' % (phone)
            session['sale_pass'] = password
            return redirect(sale_redirect)
        merchant = api.get_merchant_by_phone(phone)
        if merchant:
            sign_in = api.hq_sign_in_by_phone(merchant['_id'], phone, password)
            if sign_in:
                session['is_login'] = phone
                session['is_hq'] = phone
                shop_in_mer = api.get_shop_by_merchant(str(merchant['_id']))
                shop_ids = [shop['_id'] for shop in shop_in_mer]
                g.shops = [api.get_shop_info(i) for i in shop_ids]
                g.merchant = merchant
                g.role = '3'
                session['is_superuser'] = phone
                if len(shop_ids) > 0:
                    user_login = g.user
                    merchant_id = merchant.get('_id')
                    check = api.check_reset_password(merchant_id)
                    if check:
                        return redirect('/settings')
                    return redirect('/home')
                else:
                    return redirect(url_for('setup_first_login'))
            else:
                error = gettext("Thong_tin_dang_nhap_khong_dung.")
                return render_template("nextify/login.html", error=error)

        else:
            error = gettext("Thong_tin_dang_nhap_khong_dung.")
            return render_template("nextify/login.html", error=error)


@app.route('/login', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        # return "ok"
        phone = session.get('is_login')
        shop_id = session.get('shop_id')
        is_superuser = session.get('is_superuser')
        is_hq = session.get('is_hq')
        if phone:
            is_email = validate_email(phone)
            is_slug = api.validate_slug(phone)
            if is_email:
                merchant = api.get_merchant_by_email(phone)
            elif is_slug:
                merchant = api.get_merchant_by_slug(phone)
            else:
                merchant = api.get_merchant_by_phone(phone)
            if merchant:
                session['is_login'] = phone
                session['is_hq'] = phone
                session['merchant_id'] = str(merchant['_id'])
                shop_in_mer = api.get_shop_by_merchant(str(merchant['_id']))
                shop_ids = [shop['_id'] for shop in shop_in_mer]
                g.shops = [api.get_shop_info(i) for i in shop_ids]
                g.merchant = merchant
                session['is_superuser'] = phone
                if len(shop_ids) > 0:
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('setup_first_login'))
            else:
                session.pop('is_login', None)
                session.pop('is_superuser', None)
                session.pop('shop_id', None)
                session.pop('merchant_id', None)
                session.pop('is_hq', None)
                return render_template("nextify/login.html")
        else:
            session.pop('is_login', None)
            session.pop('is_superuser', None)
            session.pop('shop_id', None)
            session.pop('merchant_id', None)
            session.pop('is_hq', None)
            return render_template("nextify/login.html")
    else:
        phone = request.form.get('phone')
        password = request.form.get('password')
        if not phone or not password or len(phone) == 0 or len(password) == 0:
            error = gettext("Thong_tin_dang_nhap_khong_dung.")
            return render_template("nextify/login.html", error=error)
        if not captcha.validate():
            error = "Mã captcha chưa đúng, vui lòng thử lại."
            return render_template("nextify/login.html", error=error)
        is_sale_men = api.check_is_sales_person(phone, password)
        if is_sale_men:
            sale_redirect = '/sales/%s' % (phone)
            session['sale_pass'] = password
            return redirect(sale_redirect)
        merchant = None
        sign_in = None
        phone = phone.strip()
        is_email = validate_email(phone)
        is_slug = api.validate_slug(phone)

        if is_email:
            merchant = api.get_merchant_by_email(phone)
            if merchant:
                sign_in = api.hq_sign_in_by_email(merchant['_id'], phone,
                                                  password)
            else:
                error = gettext("Thong_tin_dang_nhap_khong_dung.")
                return render_template("nextify/login.html", error=error)
        else:
            if is_slug:
                merchant = api.get_merchant_by_slug(phone)
                if merchant:
                    sign_in = api.hq_sign_in_by_slug(merchant['_id'], phone,
                                                     password)
                else:
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("nextify/login.html", error=error)
            else:
                merchant = api.get_merchant_by_phone(phone)
                if merchant:
                    sign_in = api.hq_sign_in_by_phone(merchant['_id'], phone,
                                                      password)
                else:
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("nextify/login.html", error=error)

        if merchant and sign_in:
            session['shop_id'] = None
            session['is_login'] = phone
            session['is_hq'] = phone
            bccs_id = merchant.get('bccs_account_id')
            if bccs_id and len(bccs_id) > 0:
                shop_in_mer = api.get_shop_by_merchant_active(
                    str(merchant['_id']))
                shop_ids = [shop['_id'] for shop in shop_in_mer]
                if len(shop_ids) == 0:
                    error = gettext(
                        "Tai_khoan_het_han_hoac_chua_duoc_kich_hoat")
                    return render_template("nextify/login.html", error=error)
            else:
                shop_in_mer = api.get_shop_by_merchant(str(merchant['_id']))
            shop_ids = [shop['_id'] for shop in shop_in_mer]
            g.shops = [api.get_shop_info(i) for i in shop_ids]
            g.merchant = merchant
            session['is_superuser'] = phone
            session['merchant_id'] = str(merchant['_id'])

            if len(shop_ids) > 0:
                return redirect(url_for('index'))
            else:
                return redirect(url_for('setup_first_login'))

        else:
            error = gettext("Thong_tin_dang_nhap_khong_dung.")
            return render_template("nextify/login.html", error=error)


def is_human(captcha_response):
    """ Validating recaptcha response from google server
                Returns True captcha test passed for submitted form else returns False.
        """
    if "anphat" in request.headers['Host']:
        secret = "6LcbCbwUAAAAAMmg5LAxFQmL26dp7BtMMG8hvot6"
    else:
        secret = "6LcpAnEUAAAAAHvtotbFuLlnRFtt5hpoGAbTz8Yu"

    payload = {'response': captcha_response, 'secret': secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify",
                             payload)
    response_text = json.loads(response.text)

    return response_text['success']


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('is_login', None)
    session.pop('is_hq', None)
    session.pop('is_superuser', None)
    session.pop('shop_id', None)
    session.pop('customers_filter', None)
    session.pop('merchant_id', None)
    g.shops = None
    g.merchant = None
    g.user = None
    return redirect('/')


@app.route('/<merchant_slug>/logout', methods=['GET'])
def logout_merchant(merchant_slug):
    session.pop('is_login', None)
    session.pop('is_hq', None)
    session.pop('is_superuser', None)
    session.pop('shop_id', None)
    session.pop('customers_filter', None)
    session.pop('merchant_id', None)
    g.shops = None
    g.merchant = None
    g.user = None
    return redirect('/%s' % (merchant_slug))


@app.route('/marketing', methods=['GET', 'POST'])
@login_required
def marketing():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    return render_template(
        'nextify/marketing.html',
        shop_in_mer=shop_in_mer,
        user_login=user_login,
        shop_id=shop_id,
        merchant_id=merchant_id,
        merchant=merchant,
        shop=shop,
    )


@app.route('/app', methods=['GET', 'POST'])
@login_required
def app_management():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    return render_template(
        'nextify/app.html',
        shop_in_mer=shop_in_mer,
        user_login=user_login,
        shop_id=shop_id,
        merchant_id=merchant_id,
        merchant=merchant,
        shop=shop,
    )


@app.route('/wifi_iframe/<api_key>/<mobio_id_merchant>',
           methods=['GET', 'POST'])
@cross_origin()
def wifi_iframe(api_key, mobio_id_merchant):
    page = int(request.args.get('page', 1))
    dealer_login = api.get_dealers_by_api_key(str(api_key))
    if not dealer_login:
        return redirect('/404')
    merchant = api.get_merchant_mobio(mobio_id_merchant)
    if not merchant:
        return redirect('/404')
    merchant_id = merchant.get('_id')
    if str(merchant.get('partner')) != str(dealer_login.get('_id')):
        return redirect('/404')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [shop['_id'] for shop in shop_in_mer]
    g.shops = [api.get_shop_info(i) for i in shop_ids]
    g.merchant = merchant
    session['is_login'] = merchant.get('phone')
    session['is_hq'] = merchant.get('phone')
    session['is_superuser'] = merchant.get('phone')
    session['merchant_id'] = merchant_id
    shops_info = []
    shops_info = api.get_gen_shop_by_merchant(
        str(merchant_id), page, page_size=settings.ITEMS_PER_PAGE)
    total = shops_info.count()
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/wifi_locations.html',
                           merchant=merchant,
                           pagination=pagination,
                           locations=shops_info)


# new menu wifi
@app.route('/config_spin', methods=['POST'])
@login_required
def config_spin():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')

    if request.method == 'POST':
        shop_id_select = request.form.get('shop_id_select')
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        spin_config = shop_select.get('spin')
        files = request.files
        spin = {}
        content = request.form.get('content')
        content_color = request.form.get('content_color')
        if not content or str(content) == 'None':
            content = ''
        spin['content'] = content
        spin['content_color'] = content_color
        turns = request.form.get('turns')
        spin['turns'] = turns
        time_reset = request.form.get('time_reset')
        spin['time_reset'] = time_reset
        gifts = request.form.get('gifts')
        spin['total_gifts'] = gifts

        win_rate = request.form.get('win_rate')
        spin['win_rate'] = win_rate
        name_btn_win = request.form.get('name_btn_win')
        if not name_btn_win or str(name_btn_win) == 'None':
            name_btn_win = 'Quay ngay'
        spin['name_btn_win'] = name_btn_win

        content_win = request.form.get('content_win')
        if not content_win or str(content_win) == 'None':
            content_win = 'Xin chúc mừng, phần thưởng của bạn là'
        spin['content_win'] = content_win

        content_not_win = request.form.get('content_not_win')
        if not content_not_win or str(content_not_win) == 'None':
            content_not_win = 'Rất tiếc bạn đã không trúng thưởng, hãy thử lại vận may của mình.'
        spin['content_not_win'] = content_not_win

        background = request.files.get('background')

        if background and \
                background.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            background_name = storage_api.save_new_file(background)
            spin['background'] = background_name
        else:
            spin['background'] = spin_config.get('background')
        center = request.files.get('center')
        if center and \
                center.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            center_name = storage_api.save_new_file(center)
            spin['center'] = center_name
        else:
            spin['center'] = spin_config.get('center')

        gifts = int(gifts)
        gifts_detail = []
        for i in range(0, gifts):
            each_gift = {}
            each_gift_input = request.files.get('gift_input_' + str(i))
            if each_gift_input and \
                    each_gift_input.filename.rsplit('.', 1)[1].lower() \
                    in ALLOWED_EXTENSIONS:
                photo = storage_api.save_new_file(each_gift_input)
                each_gift['images'] = photo
            else:
                try:
                    each_gift['images'] = spin_config.get('gifts')[i].get(
                        'images')
                except:
                    pass

            each_gift_text = request.form.get('gift_text_' + str(i))
            if not each_gift_text or str(each_gift_text) == 'None':
                each_gift_text = ''
            each_gift['title'] = each_gift_text

            each_gift_method = request.form.get('gift_select_' + str(i))
            if str(each_gift_method) == 'gift':
                each_gift_method = 'gift'
            elif str(each_gift_method) == 'code':
                each_gift_method = 'code'
            elif str(each_gift_method) == 'vnpay':
                each_gift_method = 'vnpay'
            elif str(each_gift_method) == '0':
                each_gift_method = False

            each_gift['is_reward'] = each_gift_method

            each_gift_detail = request.form.get('gift_detail_' + str(i))
            if not each_gift_detail or str(each_gift_detail) == 'None':
                each_gift_detail = ''
            each_gift['detail'] = each_gift_detail

            each_gift_color = request.form.get('gift_color_' + str(i))
            if not each_gift_color or str(each_gift_color) == 'None':
                each_gift_color = ''
            each_gift['color'] = each_gift_color

            each_gift_count = request.form.get('gift_count_' + str(i))
            each_gift['amount'] = each_gift_count
            each_gift['remaining_amount'] = each_gift_count

            win_rate_gift = request.form.get('win_rate_gift_' + str(i))
            each_gift['rate_reward'] = win_rate_gift

            gifts_detail.append(each_gift)
        spin['gifts'] = gifts_detail

        reset = request.form.get('reset')

        api.update_config_spin(shop_id=shop_id_select, info=spin, reset=reset)
        return json.dumps({'result': True})


@app.route('/hotspot', methods=['GET', 'POST'])
@login_required
def new_hotspot_campaign():
    if request.method == 'GET':
        shop = g.shop
        user_login = g.user
        shop_id = shop['_id']
        merchant_id = shop.get('merchant_id')
        merchant = api.get_merchant(merchant_id)
        page = request.args.get('page', 1)
        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]
        # shop_in_mer = api.get_shop_by_merchant(merchant_id)
        shop_id_select = request.args.get('shop_id_select', '')
        if not shop_id_select or len(shop_id_select) == 0:
            shop_id_select = shops[0]['_id']

        return redirect('/hotspot/%s' % (shop_id_select))
    else:
        camp_id = request.form.get('campaign_id')
        shop_id_select = request.form.get('shop_id_select')
        if camp_id and len(camp_id) > 0:
            api.remove_new_campaign_by_id(shop_id_select, camp_id)
        return json.dumps({'result': True})


@app.route('/hotspot/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def new_shop_hotspot_campaign(shop_id_select):
    if request.method == 'GET':
        shop = g.shop
        user_login = g.user
        shop_id = shop['_id']
        merchant_id = shop.get('merchant_id')
        merchant = api.get_merchant(merchant_id)
        page = int(request.args.get('page', 1))
        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]

        total_hotspot = api.new_total_hotspot_campaign(shop_id_select)
        if total_hotspot == 0:
            api.init_new_campaign(shop_id_select)

        campaigns_default = api.get_new_campaigns_default(shop_id_select)
        campaigns_default_id = [camp.get('_id') for camp in campaigns_default]
        # verify_email_camp = api.has_verify_email_camp(shop_id_select)
        # if not verify_email_camp:
        #     api.init_verify_email_camp(shop_id_select)

        # xoa campaign chua tao xong
        api.remove_campaigns(shop_id_select)
        campaigns = api.get_new_campaigns(shop_id_select,
                                          page,
                                          settings.ITEMS_PER_PAGE,
                                          not_default=campaigns_default_id)
        total_hotspot_campaign_not_default = api.new_total_hotspot_campaign_not_default(
            shop_id, campaigns_default_id)
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        pagination = Pagination(page=page,
                                total=total_hotspot_campaign_not_default,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        tag_list = api.get_splash_page_tag(shop_id=shop_id_select)
        return render_template('new_hotspot/menu_new_campaign.html',
                               merchant=merchant,
                               shop_id_select=shop_id_select,
                               shop_in_mer=shops,
                               campaigns=campaigns,
                               total=total_hotspot_campaign_not_default,
                               pagination=pagination,
                               shop_select=shop_select,
                               tag_list=tag_list,
                               tags=tags,
                               campaigns_default=campaigns_default)


@app.route('/wifi_ads', methods=['GET', 'POST'])
@login_required
def wifi_ads():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    page = int(request.args.get('page', 1))
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == 'GET':
        total_hotspot = api.total_wifi_ads(merchant_id)
        if total_hotspot == 0:
            api.init_wifi_ads(merchant_id)
        # xoa camp chua tao hoan thanh
        api.remove_camp_ads(merchant_id)
        campaigns = api.get_wifi_ads_camps(merchant_id, page,
                                           settings.ITEMS_PER_PAGE)
        total_hotspot = api.total_wifi_ads(merchant_id)
        events = []
        for camp in campaigns:
            start = ''
            end = ''
            name = camp.get("name")
            group_customer = camp.get('group_customer')
            start_time = group_customer.get('timestamp_start_event')
            end_time = group_customer.get('timestamp_end_event')
            if start_time and start_time > 0:
                start = datetime.fromtimestamp(
                    int(start_time)).strftime('%Y-%m-%d')
                if end_time and end_time > 0:
                    end = datetime.fromtimestamp(
                        int(end_time)).strftime('%Y-%m-%d')
                detail = {'title': name, 'start': start, 'end': end}
                events.append(detail)
        pagination = Pagination(page=page,
                                total=total_hotspot,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        return render_template('nextify/wifi_ads.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shops,
                               campaigns=campaigns,
                               total=total_hotspot,
                               events=json.dumps(events),
                               pagination=pagination,
                               tags=tags)
    else:
        page = int(request.args.get('page', 1))
        min_impressions = request.form.get('min_impressions')
        max_impressions = request.form.get('max_impressions')
        status_filter = request.form.get('status_filter')
        min_target = request.form.get('min_target')
        max_target = request.form.get('max_target')
        tags_filter = request.form.get('tags_filter')
        from_create = request.form.get('from_create')
        to_create = request.form.get('to_create')
        from_perform = request.form.get('from_perform')
        to_perform = request.form.get('to_perform')
        result_filter = request.form.get('result_filter')
        loc_filter = request.form.get('loc_filter')
        type_campaign_filter = request.form.get('type_campaign_filter')
        arr_loc = []
        arr_tag = []
        if loc_filter:
            arr_loc = loc_filter.split(',')
        if tags_filter:
            arr_tag = tags_filter.split(',')
        campaigns = api.filter_wifi_ads(
            page=page,
            min_impressions=min_impressions,
            max_impressions=max_impressions,
            status_filter=status_filter,
            min_target=min_target,
            max_target=max_target,
            tags_filter=arr_tag,
            from_create=from_create,
            to_create=to_create,
            from_perform=from_perform,
            to_perform=to_perform,
            result_filter=result_filter,
            loc_filter=arr_loc,
            type_campaign_filter=type_campaign_filter)
        return render_template('nextify/filter_wifi_ads.html',
                               campaigns=campaigns)


@app.route('/wifi_ads/<camp_id>/<action>/<status>', methods=['GET'])
@login_required
def wifi_ads_action(camp_id, action, status):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if action == 'active':
        if str(status).lower() == 'true':
            status = True
        else:
            stauts = False
        api.update_wifi_ads(camp_id, status=status)
    if action == "remove":
        api.remove_wifi_ads_by_id(camp_id)
    return json.dumps({'result': True})


@app.route('/sync_wifi_camp', methods=['POST'])
@login_required
def sync_wifi_camp():
    shop_origin = request.form.get('shop_origin')
    sync_campaign = request.form.get('sync_campaign')
    sync_camp_tags = request.form.get('sync_camp_tags')
    try:
        producer_data = {
            "shop_id": str(shop_origin),
            "task_name": "sync_wifi_camp",
            "params": {
                "shop_origin": str(shop_origin),
                "sync_campaign": str(sync_campaign),
                "sync_camp_tags": sync_camp_tags
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        return json.dumps({'result': True})
    except:
        return json.dumps({'result': False})


@app.route('/hotspot/<shop_id_select>/templates', methods=['GET', 'POST'])
@login_required
def hotspot_campaign_template(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    page = int(request.args.get('page', 1))
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    tag_list = api.get_splash_page_tag(shop_id=shop_id_select)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    return render_template('new_hotspot/hotspot_templates.html',
                           merchant=merchant,
                           shop_id_select=shop_id_select,
                           shop_in_mer=shops,
                           shop_select=shop_select,
                           tag_list=tag_list,
                           tags=tags)


@app.route('/wifi_camp/<shop_id_select>/active/<camp_id>', methods=['POST'])
@login_required
def active_wifi_campaign(shop_id_select, camp_id):
    camp = api.get_hotspot_campaign_by_id(camp_id)
    if not camp:
        return json.dumps({'result': False})
    camp_type = camp.get('campaign_type')
    status_campaign = request.form.get('status')
    status_campaign = True if str(status_campaign) == 'true' else False
    if not status_campaign:
        if api.count_active_hotspot_campaign(shop_id_select) == 1:
            return json.dumps({'result': False})

        exist_visit = api.active_hotspot_campaign(camp_id, shop_id_select,
                                                  status_campaign)
        if exist_visit:
            exist_camp_name = exist_visit.get('name')
            return json.dumps({'exist': 1, 'exist_camp_name': exist_camp_name})
        api.update_priority_after_deactive(camp_id)
    else:

        exist_visit = api.active_hotspot_campaign(camp_id, shop_id_select,
                                                  status_campaign)
        if exist_visit:
            exist_camp_name = exist_visit.get('name')
            return json.dumps({'exist': 1, 'exist_camp_name': exist_camp_name})
    return json.dumps({'result': True})


@app.route('/hotspot/<shop_id_select>/birthday/<camp_id>/<status>',
           methods=['GET'])
@login_required
def hotspot_campaign_quick_birthday(shop_id_select, camp_id, status):
    camp = api.get_new_campaign_by_id(camp_id)
    if not camp:
        return json.dumps({'result': False})
    status_campaign = True if str(status) == 'true' else False
    api.update_birthday_new_camp(camp_id, status_campaign)
    return json.dumps({'result': True})


@app.route('/hotspot/<shop_id_select>/active/<camp_id>/<status>',
           methods=['GET'])
@login_required
def hotspot_campaign_quick_active(shop_id_select, camp_id, status):
    camp = api.get_new_campaign_by_id(camp_id)
    if not camp:
        return json.dumps({'result': False})
    status_campaign = True if str(status) == 'true' else False
    api.update_status_new_camp(camp_id, status_campaign)
    return json.dumps({'result': True})


@app.route('/new_wifi_camp/<shop_id_select>/active/<camp_id>',
           methods=['POST'])
@login_required
def active_new_wifi_campaign(shop_id_select, camp_id):
    camp = api.get_new_campaign_by_id(camp_id)
    if not camp:
        return json.dumps({'result': False})
    camp_type = camp.get('type')
    if camp_type == "register":
        status_campaign = True
        api.update_status_new_camp(camp_id, status_campaign)
    else:
        status_campaign = request.form.get('status')
        status_campaign = True if str(status_campaign) == 'true' else False
        if status_campaign:
            api.update_status_new_camp(camp_id, status_campaign)
        else:
            check_active_camp = api.num_camp_active(shop_id_select)
            if int(check_active_camp) <= 1:
                return json.dumps({'result': False})
            else:
                api.update_status_new_camp(camp_id, status_campaign)

    return json.dumps({'result': True})


@app.route('/hotspot_details', methods=['GET', 'POST'])
@login_required
def hotspot_details():
    if request.method == 'GET':
        session.pop('step_1', None)
        session.pop('step_2', None)
        session.pop('step_3', None)
        session.pop('step_4', None)
        session.pop('survey_step_1', None)
        session.pop('survey_step_2', None)
        session.pop('survey_step_3', None)
        session.pop('spin_1', None)
        session.pop('spin_2', None)
        session.pop('spin_3', None)
        session.pop('current_step', None)
        shop = g.shop
        user_login = g.user
        shop_id = shop['_id']
        merchant_id = shop.get('merchant_id')
        merchant = api.get_merchant(merchant_id)

        shop_id_select = request.args.get('shop_id')
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        campaign_id = request.args.get('campaign_id')
        campaign_details = None
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        if campaign_id:
            campaign_details = api.get_hotspot_campaign_by_id(campaign_id)
            step_1 = campaign_details.get('step_1')
            if step_1:
                if str(step_1) == 'survey':
                    session['step_1'] = 'survey'
                    survey_step_1 = campaign_details.get('survey_step_1')
                    if survey_step_1:
                        session['survey_step_1'] = survey_step_1
                elif str(step_1) == 'spin':
                    session['step_1'] = 'spin'
                    survey_step_1 = campaign_details.get('spin_step_1')
                    if survey_step_1:
                        session['spin_1'] = survey_step_1
                else:
                    session['step_1'] = step_1
            else:
                session['step_1'] = '0'
            step_2 = campaign_details.get('step_2')
            if step_2:
                if str(step_2) == 'survey':
                    session['step_2'] = 'survey'
                    survey_step_2 = campaign_details.get('survey_step_2')
                    if survey_step_2:
                        session['survey_step_2'] = survey_step_2
                elif str(step_2) == 'spin':
                    session['step_2'] = 'spin'
                    survey_step_2 = campaign_details.get('spin_step_2')
                    if survey_step_2:
                        session['spin_2'] = survey_step_2
                else:
                    session['step_2'] = step_2
            else:
                session['step_2'] = '0'
            step_3 = campaign_details.get('step_3')
            if step_3:
                if str(step_3) == 'survey':
                    session['step_3'] = 'survey'
                    survey_step_3 = campaign_details.get('survey_step_3')
                    if survey_step_3:
                        session['survey_step_3'] = survey_step_3
                elif str(step_3) == 'spin':
                    session['step_3'] = 'spin'
                    survey_step_3 = campaign_details.get('spin_step_3')
                    if survey_step_3:
                        session['spin_3'] = survey_step_3
                else:
                    session['step_3'] = step_3
            else:
                session['step_3'] = '0'
            session['current_step'] = '1'

        return render_template('new_hotspot/menu_hotspot_details.html',
                               merchant=merchant,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               campaign_details=campaign_details,
                               campaign_id=campaign_id,
                               tags=tags)
    else:
        shop_id_select = request.form.get('shop_id')
        shop = api.get_shop_info(shop_id=shop_id_select)
        arr_splash = request.form.get('arr_splash')
        step = request.form.get('step')
        pre_step = request.form.get('pre_step')
        choose_splash = request.form.get('choose_splash', '0')
        # session check
        splash_choosed_step = '0'
        if ('step_' + str(step)) in session:
            splash_choosed_step = session['step_' + str(step)]
        if ('step_' + str(pre_step)) in session:
            session.pop('step_' + str(pre_step), None)
        if pre_step:
            session['step_' + str(pre_step)] = choose_splash
        session['current_step'] = step
        result = api.arr_splash(arr_splash)
        result.append(splash_choosed_step)

        return render_template('new_hotspot/menu_hotspot_each_step.html',
                               shop_id_select=shop_id_select,
                               arr_splash=json.dumps(result),
                               step=step,
                               shop=shop,
                               splash_choosed_step=splash_choosed_step)


@app.route('/new_hotspot_details', methods=['GET', 'POST'])
@login_required
def new_hotspot_details():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if request.method == 'GET':
        session.pop('step_1', None)
        session.pop('step_2', None)
        session.pop('step_3', None)
        session.pop('step_4', None)
        session.pop('current_step', None)

        shop_id_select = request.args.get('shop_id')
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        campaign_id = request.args.get('campaign_id')
        camp_init = request.args.get('init')
        if str(campaign_id) == "add":
            campaign_id = api.create_new_camp(shop_id_select)
        campaign_details = {}
        group_customer = {}
        detail_step_connect = []
        list_step = []
        list_tags = []
        type_camp = ''
        if campaign_id:
            campaign_details = api.get_new_campaign_by_id(campaign_id)
            type_camp = campaign_details.get('type')
            list_step = api.get_list_step(campaign_id)
            group_customer = campaign_details.get('group_customer')
            if group_customer:
                for tag in group_customer.get('tags_group_customer'):
                    list_tags.append(str(tag))

            detail_step_connect = api.get_new_detail_step(
                shop_id_select, campaign_id, 'connect_success', '4')
            step_1 = campaign_details.get('step_1')
            session['step_1'] = step_1
            step_2 = campaign_details.get('step_2')
            session['step_2'] = step_2
            step_3 = campaign_details.get('step_3')
            session['step_3'] = step_3
            step_4 = campaign_details.get('step_4')
            session['step_4'] = step_4

        session['current_step'] = '1'
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        if str(type_camp) == 'verify_email':
            detail = {}
            detail = api.get_detail_step(shop_id_select, campaign_id, 'terms',
                                         '1')
            settings_starbucks = shop_select.get('settings_starbucks', {})
            return render_template('new_hotspot/wifi_starbucks.html',
                                   merchant=merchant,
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   campaign_details=campaign_details,
                                   group_customer=group_customer,
                                   detail_step_connect=detail_step_connect,
                                   list_step=list_step,
                                   campaign_id=campaign_id,
                                   detail=detail,
                                   settings_starbucks=settings_starbucks,
                                   list_tags=list_tags,
                                   tags=tags)
        return render_template('new_hotspot/wifi_wizard.html',
                               merchant=merchant,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               campaign_details=campaign_details,
                               group_customer=group_customer,
                               detail_step_connect=detail_step_connect,
                               list_step=list_step,
                               campaign_id=campaign_id,
                               list_tags=list_tags,
                               camp_init=camp_init,
                               tags=tags)
    else:
        shop_id_select = request.form.get('shop_id')
        camp_id = request.form.get('camp_id')
        step = request.form.get('step')
        prev_step = request.form.get('prev_step')
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        choose_page = request.form.get('choose_page')
        shop_id_woay = shop_select.get('shop_id_woay', '1')
        link_woay = shop_select.get('link_woay', '')
        if not choose_page or choose_page == "0" and ('step_' +
                                                      str(step)) in session:
            choose_page = session['step_' + str(step)]
        elif choose_page and choose_page != "0":
            choose_page = choose_page
        else:
            choose_page = "0"
        detail_step = {}

        if choose_page != '0':
            detail_step = api.get_new_detail_step(shop_id_select, camp_id,
                                                  choose_page, step)
        list_survey_splash = api.list_survey_splash(
            shop_id_select, page=None, page_size=settings.ITEMS_PER_PAGE)
        list_spin_splash = api.list_mini_game(
            shop_id_select, page=None, page_size=settings.ITEMS_PER_PAGE)

        session['current_step'] = step
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        medical_declaration = shop_select.get('medical_declaration', {})
        return render_template('new_hotspot/wifi_wizard_each_step.html',
                               merchant=merchant,
                               shop_id_select=shop_id_select,
                               step=step,
                               shop_id_woay=shop_id_woay,
                               link_woay=link_woay,
                               detail_step=detail_step,
                               list_survey_splash=list_survey_splash,
                               list_spin_splash=list_spin_splash,
                               medical_declaration=medical_declaration,
                               choose_page=choose_page)


@app.route('/<shop_id_select>/wifi_camp/templates/segment',
           methods=['GET', 'POST'])
@login_required
def wifi_camp_segment_templates(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return render_template('new_hotspot/segment_wizard.html',
                           shop_id_select=shop_id_select,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           merchant=merchant)


@app.route('/<shop_id_select>/wifi_camp/templates/birthday',
           methods=['GET', 'POST'])
@login_required
def wifi_camp_birthday_templates(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return render_template('new_hotspot/birthday_wizard.html',
                           shop_id_select=shop_id_select,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           merchant=merchant)


@app.route('/<shop_id_select>/wifi_camp/templates/visit',
           methods=['GET', 'POST'])
@login_required
def wifi_camp_visit_templates(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return render_template('new_hotspot/visit_wizard.html',
                           shop_id_select=shop_id_select,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           merchant=merchant)


@app.route('/<shop_id_select>/wifi_camp/templates/days',
           methods=['GET', 'POST'])
@login_required
def wifi_camp_days_templates(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return render_template('new_hotspot/days_wizard.html',
                           shop_id_select=shop_id_select,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           merchant=merchant)


@app.route('/<shop_id_select>/wifi_camp/templates/happy_day',
           methods=['GET', 'POST'])
@login_required
def wifi_camp_happy_day_templates(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return render_template('new_hotspot/happy_day_wizard.html',
                           shop_id_select=shop_id_select,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           merchant=merchant)


@app.route('/<shop_id_select>/wifi_camp/templates/happy_hour',
           methods=['GET', 'POST'])
@login_required
def wifi_camp_happy_hour_templates(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return render_template('new_hotspot/happy_hour_wizard.html',
                           shop_id_select=shop_id_select,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           merchant=merchant)


@app.route('/preview/<shop_id_select>/<campaign_id>', methods=['GET'])
@login_required
def preview_campaign_hotspot(shop_id_select, campaign_id):
    campaign_details = api.get_new_campaign_by_id(campaign_id)
    if campaign_details:
        return render_template('new_hotspot/preview_campaign.html',
                               shop_id_select=shop_id_select,
                               camp=campaign_details)
    else:
        abort(404)


@app.route('/remove_image/<shop_id_select>/<campaign_id>/<photo>',
           methods=['GET'])
@login_required
def remove_image(shop_id_select, campaign_id, photo):
    api.remove_image_slides(shop_id_select, campaign_id, photo)
    return json.dumps({'resutl': True})


@app.route('/save_new_campaign/<shop_id_selected>/<camp_id>', methods=['POST'])
@login_required
def save_new_campaign(shop_id_selected, camp_id):
    data = request.form.to_dict()
    files = request.files
    # type step
    step_1 = data.get('step_1')
    step_2 = data.get('step_2')
    step_3 = data.get('step_3')
    step_4 = 'connect success'
    # sinh nhat va kich hoat
    is_birthday = data.get('birthday')
    is_birthday = True if str(is_birthday) == "true" else False
    active = data.get('active')
    camp_init = data.get('camp_init')
    active = True if str(active) == "true" or camp_init == "True" else False
    name_camp = data.get('name_camp')
    # group customer
    group_customer = json.loads(data.get('group_customer'))
    tags_group = group_customer.get('camp_tags_selects')
    tags_group_customer = []
    if tags_group and type(tags_group) != list:
        tags_group_customer.append(ObjectId(tags_group))
    else:
        if tags_group and len(tags_group) > 0:
            for tag in tags_group:
                tag = tag.strip()
                if len(tag) > 0:
                    tags_group_customer.append(ObjectId(tag))

    min_visit = group_customer.get('min_visit')
    max_visit = group_customer.get('max_visit')
    if not min_visit and max_visit:
        min_visit = 1
    if not max_visit and min_visit:
        max_visit = 1000
    if min_visit:
        min_visit = int(min_visit)
    if max_visit:
        max_visit = int(max_visit)
    date_type_select = group_customer.get('date_type_select')
    weekday_sun = data.get('weekday_sun_')
    weekday_sun = True if weekday_sun == "true" else False
    weekday_mon = data.get('weekday_mon_')
    weekday_mon = True if weekday_mon == "true" else False
    weekday_tue = data.get('weekday_tue_')
    weekday_tue = True if weekday_tue == "true" else False
    weekday_wed = data.get('weekday_wed_')
    weekday_wed = True if weekday_wed == "true" else False
    weekday_thu = data.get('weekday_thu_')
    weekday_thu = True if weekday_thu == "true" else False
    weekday_fri = data.get('weekday_fri_')
    weekday_fri = True if weekday_fri == "true" else False
    weekday_sat = data.get('weekday_sat_')
    weekday_sat = True if weekday_sat == "true" else False
    min_day = group_customer.get('min_day')
    max_day = group_customer.get('max_day')
    event_start_picker = group_customer.get('event_start_picker')
    event_end_picker = group_customer.get('event_end_picker')
    timestamp_start_event = 0
    if event_start_picker:
        date_start_event = datetime.strptime(event_start_picker,
                                             "%d-%m-%Y").timetuple()
        timestamp_start_event = time.mktime(date_start_event)
    timestamp_end_event = 0
    if event_end_picker:
        date_end_event = datetime.strptime(event_end_picker,
                                           "%d-%m-%Y").timetuple()
        timestamp_end_event = time.mktime(date_end_event)
    min_hour = group_customer.get('min_hour')
    max_hour = group_customer.get('max_hour')
    convert_min_hour = 0
    split_min_hour = min_hour.split(':')
    convert_min_hour = int(split_min_hour[0])
    if split_min_hour[1] == '30':
        convert_min_hour = convert_min_hour + 0.5
    convert_max_hour = 0
    split_max_hour = max_hour.split(':')
    convert_max_hour = int(split_max_hour[0])
    if split_max_hour[1] == '30':
        convert_max_hour = convert_max_hour + 0.5
    details_group_customer = {
        'tags_group_customer': tags_group_customer,
        'min_visit': min_visit,
        'max_visit': max_visit,
        'date_type_select': date_type_select,
        'weekday_sun': weekday_sun,
        'weekday_mon': weekday_mon,
        'weekday_tue': weekday_tue,
        'weekday_wed': weekday_wed,
        'weekday_thu': weekday_thu,
        'weekday_fri': weekday_fri,
        'weekday_sat': weekday_sat,
        'min_day': int(min_day),
        'max_day': int(max_day),
        'event_start_picker': event_start_picker,
        'event_end_picker': event_end_picker,
        'timestamp_start_event': timestamp_start_event,
        'timestamp_end_event': timestamp_end_event,
        'min_hour': min_hour,
        'max_hour': max_hour,
        'convert_min_hour': convert_min_hour,
        'convert_max_hour': convert_max_hour
    }
    type_camp = data.get('type_camp')
    api.update_new_campaign(shop_id_selected, camp_id, name_camp, type_camp,
                            active, is_birthday, step_1, step_2, step_3,
                            step_4, details_group_customer)
    api.update_shop(shop_id=shop_id_selected, new_camp=True)
    return json.dumps({'result': True})


@app.route('/save_step_campaign/<shop_id_selected>/<camp_id>',
           methods=['POST'])
@login_required
def save_step_campaign(shop_id_selected, camp_id):
    data = request.form.to_dict()
    files = request.files
    type_page = data.get('type_page')
    camp_id = data.get('camp_id')
    shop_id = data.get('shop_id_select')
    current_step = '0'
    details = {}

    if str(type_page) == 'collect':
        current_step = data.get('current_step')
        collect_page = json.loads(data.get('collect_page'))
        phone_visible = collect_page.get('phone_visible')
        phone_visible = True if phone_visible else False
        phone_require = collect_page.get('phone_require')
        phone_require = True if phone_require else False

        name_visible = collect_page.get('name_visible')
        name_visible = True if name_visible else False
        name_require = collect_page.get('name_require')
        name_require = True if name_require else False

        birthday_visible = collect_page.get('birthday_visible')
        birthday_visible = True if birthday_visible else False
        birthday_require = collect_page.get('birthday_require')
        birthday_require = True if birthday_require else False

        gender_visible = collect_page.get('gender_visible')
        gender_visible = True if gender_visible else False
        gender_require = collect_page.get('gender_require')
        gender_require = True if gender_require else False

        email_visible = collect_page.get('email_visible')
        email_visible = True if email_visible else False
        email_require = collect_page.get('email_require')
        email_require = True if email_require else False

        year_birthday_visible = collect_page.get('year_birthday_visible')
        year_birthday_visible = True if year_birthday_visible else False
        year_birthday_require = collect_page.get('year_birthday_require')
        year_birthday_require = True if year_birthday_require else False

        company_visible = collect_page.get('company_visible')
        company_visible = True if company_visible else False
        company_require = collect_page.get('company_require')
        company_require = True if company_require else False

        company_role_visible = collect_page.get('company_role_visible')
        company_role_visible = True if company_role_visible else False
        company_role_require = collect_page.get('company_role_require')
        company_role_require = True if company_role_require else False

        vocation = collect_page.get('vocation_visible')
        vocation = True if vocation else False
        vocation_require = collect_page.get('vocation_require')
        vocation_require = True if vocation_require else False

        identity_visible = collect_page.get('identity_visible')
        identity_visible = True if identity_visible else False
        identity_require = collect_page.get('identity_require')
        identity_require = True if identity_require else False

        connect_with_facebook = collect_page.get('connect_with_facebook')
        connect_with_facebook = True if connect_with_facebook else False

        connect_with_zalo = collect_page.get('connect_with_zalo')
        connect_with_zalo = True if connect_with_zalo else False
        allow_access_friend_zalo = collect_page.get('allow_access_friend_zalo')
        allow_access_friend_zalo = True if allow_access_friend_zalo else False

        connect_with_messenger = collect_page.get('connect_with_messenger')
        connect_with_messenger = True if connect_with_messenger else False

        connect_with_office365 = collect_page.get('connect_with_office365')
        connect_with_office365 = True if connect_with_office365 else False

        welcome_text = collect_page.get('welcome_text')
        welcome_button = collect_page.get('welcome_button')
        collect_button_color = collect_page.get('collect_button_color')
        birthday_text = collect_page.get('birthday_text')
        tag_input = collect_page.get('real_tags_filter')
        tags = []
        if tag_input and len(tag_input) > 0:
            tags_split = tag_input.split(',')
            if len(tags_split) > 0:
                for tag in tags_split:
                    tag = tag.strip()
                    if len(tag) > 0:
                        tags.append(ObjectId(tag))
        otp = collect_page.get('otp')
        otp_val = True if str(otp) == 'true' else False
        image_collect = files.get('img_collect')
        photo = None
        data_logo = None
        if image_collect and \
                image_collect.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            photo = storage_api.save_new_file(image_collect)
        else:
            detail_image = api.get_detail_step(shop_id, camp_id, type_page,
                                               current_step)
            if detail_image:
                photo = detail_image.get('background')
        details = {
            'phone': phone_visible,
            'name': name_visible,
            'birthday': birthday_visible,
            'year_birthday': year_birthday_visible,
            'gender': gender_visible,
            'email': email_visible,
            'identity': identity_visible,
            'welcome_text': welcome_text,
            'welcome_button': welcome_button,
            'birthday_text': birthday_text,
            'phone_require': phone_require,
            'name_require': name_require,
            'birthday_require': birthday_require,
            'gender_require': gender_require,
            'email_require': email_require,
            'identity_require': identity_require,
            'year_birthday_require': year_birthday_require,
            'otp': otp_val,
            'company': company_visible,
            'company_require': company_require,
            'company_role': company_role_visible,
            'company_role_require': company_role_require,
            'vocation': vocation,
            'vocation_require': vocation_require,
            'connect_with_facebook': connect_with_facebook,
            'connect_with_zalo': connect_with_zalo,
            'allow_access_friend_zalo': allow_access_friend_zalo,
            'connect_with_office365': connect_with_office365,
            'connect_with_messenger': connect_with_messenger,
            'tag': tags,
            'background': photo,
            'collect_button_color': collect_button_color
        }
    if str(type_page) == 'image':
        current_step = data.get('current_step')
        title = data.get('title_image')
        content_image = data.get('content_image')
        image_button = data.get('image_button')
        image_button_color = data.get('image_button_color')
        photo = data.get('img_image')
        details['title_image'] = title
        details['content_image'] = content_image
        details['image_button'] = image_button
        details['photo'] = photo
        details['image_button_color'] = image_button_color
    if str(type_page) == 'youtube':
        current_step = data.get('current_step')
        youtube_page = json.loads(data.get('youtube_page'))
        link_youtube = youtube_page.get('link_youtube')
        youtube_button = youtube_page.get('youtube_button')
        youtube_button_color = youtube_page.get('youtube_button_color')
        content_text_youtube = youtube_page.get('content_text_youtube')
        title_youtube = youtube_page.get('title_youtube')
        if link_youtube and len(link_youtube) > 0:
            split_link = link_youtube.split('=')
            id_link = split_link[1]
            content_youtube = '<iframe height="400" src="https://www.youtube.com/embed/' + id_link + \
                              '?autoplay=1&mute=1" frameborder="0" allow="autoplay" allowfullscreen></iframe>'
            details = {
                'link_youtube': link_youtube,
                'content_youtube': content_youtube,
                'youtube_button': youtube_button,
                'youtube_button_color': youtube_button_color,
                'content_text_youtube': content_text_youtube,
                'title_youtube': title_youtube
            }
    if str(type_page) == "spin":
        current_step = data.get('current_step')
        spin_id = data.get('spin_id')
        if spin_id and len(spin_id) > 0:
            details_spin = {}
            item = api.item_mini_game_by_id(spin_id)
            info_game = item.get('info')
            name_game = info_game.get('name')
            details = {'spin_id': spin_id, 'name_spin': name_game}
    if str(type_page) == "survey":
        current_step = data.get('current_step')
        survey_id = data.get('survey_id')
        if survey_id and len(survey_id) > 0:
            details_survey = {}
            survey_item = api.get_survey_splash(shop_id, survey_id)
            question = survey_item.get('question')
            details = {'survey_id': survey_id, 'question': question}
    if str(type_page) == "slides":
        images_slide = []
        current_step = data.get('current_step')
        number_slide = int(data.get('number_slide'))
        slide_button = data.get('slide_button')
        slide_button_color = data.get('slide_button_color')
        title_slides = data.get('title_slides')
        content_slides = data.get('content_slides')
        init = data.get('init', '')
        images = data.get('images')
        images_slide = images.split(',')
        slides = []
        for photo in images_slide:
            if photo and len(photo) > 0:
                slides.append(photo)
        if len(slides) == 0:
            slides = api.get_all_slides(shop_id, camp_id)
        if slides and len(slides) > 0:
            details = {
                'number_slide': number_slide,
                'slides': slides,
                'slide_button': slide_button,
                'slide_button_color': slide_button_color,
                'content_slides': content_slides,
                'title_slides': title_slides
            }
        if init == "True":
            api.update_init_default_camp(shop_id, camp_id)
    if str(type_page) == 'connect_success':
        # connect success page
        details = {}
        current_step = '4'
        connect_page = json.loads(data.get('connect_success_page'))
        content_connect = connect_page.get('content_connect')
        connect_button = connect_page.get('connect_button')

        redirect_type = connect_page.get('redirect_type')
        auto_website = connect_page.get('auto_website')
        auto_popup_ios = connect_page.get('auto_popup_ios')
        auto_popup_android = connect_page.get('auto_popup_android')
        auto_facebook_page = connect_page.get('auto_facebook_page')
        auto_popup_zalo = connect_page.get('auto_popup_zalo')
        auto_popup_insta = connect_page.get('auto_popup_insta')
        auto_facebook_mess = connect_page.get('auto_facebook_mess')
        connect_button_color = connect_page.get('connect_button_color')
        display_coupon = False
        display_coupon_check = connect_page.get('display_coupon')
        if display_coupon_check and str(display_coupon_check) == 'on':
            display_coupon = True
        display_coupon_txt = connect_page.get('display_coupon_txt').strip()

        hotspot_method = connect_page.get('hotspot_method', 'default')
        default_code = connect_page.get('default_code', '')
        default_code = default_code.strip()
        default_code = default_code.lower()
        image_connect = files.get('img_connect')
        photo = None
        data_logo = None
        if image_connect and \
                image_connect.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            photo = storage_api.save_new_file(image_connect)
        else:
            detail_image = api.get_detail_step(shop_id, camp_id, type_page,
                                               current_step)
            if detail_image:
                photo = detail_image.get('background_connect', '')
        details = {
            'content_connect': content_connect,
            'connect_button': connect_button,
            'redirect_type': redirect_type,
            'auto_website': auto_website,
            'auto_popup_ios': auto_popup_ios,
            'auto_popup_android': auto_popup_android,
            'auto_facebook_page': auto_facebook_page,
            'auto_popup_zalo': auto_popup_zalo,
            'auto_popup_insta': auto_popup_insta,
            'auto_facebook_mess': auto_facebook_mess,
            'display_coupon': display_coupon,
            'display_coupon_txt': display_coupon_txt,
            'hotspot_method': hotspot_method,
            'default_code': default_code,
            'background_connect': photo,
            'connect_button_color': connect_button_color
        }
    api.save_step_campaign(shop_id, camp_id, current_step, type_page, details)
    return json.dumps({'result': True})


@app.route('/save_page_init/<shop_id_select>', methods=['POST'])
@login_required
def save_page_init(shop_id_select):
    data = request.form.to_dict()
    type_page = data.get('type_page')
    if type_page == 'image_register':
        photo = data.get('img_register')
        if photo:
            session['image_register'] = photo
    if type_page == 'collect_register':
        collect_page = json.loads(data.get('collect_page'))
        logo = request.files.get('new_logo')
        background = request.files.get('new_background')
        logo_name = None
        background_name = None
        if logo and \
                logo.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            logo_name = storage_api.save_new_file(logo)
        if background and \
                background.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            background_name = storage_api.save_new_file(background)
        api.update_shop(shop_id_select,
                        logo=logo_name,
                        background=background_name)
        phone_visible = collect_page.get('phone_visible')
        phone_visible = True if phone_visible else False
        phone_require = False

        name_visible = collect_page.get('name_visible')
        name_visible = True if name_visible else False
        name_require = False

        birthday_visible = collect_page.get('birthday_visible')
        birthday_visible = True if birthday_visible else False
        birthday_require = False

        gender_visible = collect_page.get('gender_visible')
        gender_visible = True if gender_visible else False
        gender_require = False

        email_visible = collect_page.get('email_visible')
        email_visible = True if email_visible else False
        email_require = False

        welcome_text = collect_page.get('welcome_text')
        welcome_button = collect_page.get('welcome_button')
        birthday_text = collect_page.get('birthday_text')
        details = {
            'phone': phone_visible,
            'name': name_visible,
            'birthday': birthday_visible,
            'year_birthday': False,
            'gender': gender_visible,
            'email': email_visible,
            'welcome_text': welcome_text,
            'welcome_button': welcome_button,
            'birthday_text': birthday_text,
            'phone_require': False,
            'name_require': False,
            'birthday_require': False,
            'gender_require': False,
            'email_require': False,
            'year_birthday_require': False,
            'otp': False,
            'company': False,
            'company_require': False,
            'company_role': False,
            'company_role_require': False,
            'vocation': False,
            'vocation_require': False,
            'connect_with_facebook': False,
            'connect_with_zalo': False,
            'allow_access_friend_zalo': False,
            'connect_with_messenger': False,
            'tag': [],
        }
        session['collect_register'] = details
    if type_page == 'connect_register':
        details = {}
        connect_page = json.loads(data.get('connect_register'))
        redirect_type = connect_page.get('redirect_type')
        auto_website = connect_page.get('auto_website')
        auto_popup_ios = connect_page.get('auto_popup_ios')
        auto_popup_android = connect_page.get('auto_popup_android')
        auto_facebook_page = connect_page.get('auto_facebook_page')
        auto_popup_zalo = connect_page.get('auto_popup_zalo')
        auto_popup_insta = connect_page.get('auto_popup_insta')
        auto_facebook_mess = connect_page.get('auto_facebook_mess')
        details = {
            'content_connect': '',
            'connect_button': '',
            'redirect_type': redirect_type,
            'auto_website': auto_website,
            'auto_popup_ios': auto_popup_ios,
            'auto_popup_android': auto_popup_android,
            'auto_facebook_page': auto_facebook_page,
            'auto_popup_zalo': auto_popup_zalo,
            'auto_popup_insta': auto_popup_insta,
            'auto_facebook_mess': auto_facebook_mess,
            'display_coupon': '',
            'display_coupon_txt': '',
            'hotspot_method': 'default',
            'default_code': '',
        }
        session['connect_register'] = details
    if type_page == 'image_return':
        photo = data.get('img_register')
        if photo:
            session['image_return'] = photo
    if type_page == 'survey':
        survey_id = data.get('survey_id')
        if survey_id and len(survey_id) > 0:
            session['survey_return'] = survey_id
    if type_page == 'connect_return':
        details = {}
        connect_page = json.loads(data.get('connect_return'))
        redirect_type = connect_page.get('redirect_type_return')
        auto_website = connect_page.get('return_auto_website')
        auto_popup_ios = connect_page.get('return_auto_popup_ios')
        auto_popup_android = connect_page.get('return_auto_popup_android')
        auto_facebook_page = connect_page.get('return_auto_facebook_page')
        auto_popup_zalo = connect_page.get('return_auto_popup_zalo')
        auto_popup_insta = connect_page.get('return_auto_popup_insta')
        auto_facebook_mess = connect_page.get('return_auto_facebook_mess')
        details = {
            'content_connect': '',
            'connect_button': '',
            'redirect_type': redirect_type,
            'auto_website': auto_website,
            'auto_popup_ios': auto_popup_ios,
            'auto_popup_android': auto_popup_android,
            'auto_facebook_page': auto_facebook_page,
            'auto_popup_zalo': auto_popup_zalo,
            'auto_popup_insta': auto_popup_insta,
            'auto_facebook_mess': auto_facebook_mess,
            'display_coupon': '',
            'display_coupon_txt': '',
            'hotspot_method': 'default',
            'default_code': '',
        }
        session['connect_return'] = details
    return json.dumps({'result': True})


@app.route('/hotspot_type/<type_page>', methods=['GET', 'POST'])
@login_required
def new_hotspot_type(type_page):
    if request.method == 'GET':
        shop_id = g.shop_id
        user_login = g.user
        shop = g.shop
        merchant_id = shop.get('merchant_id')
        merchant = api.get_merchant(merchant_id)
        dealer_id = merchant.get('partner')
        shop_id_select = request.args.get('shop_id_select')
        step = request.args.get('step')
        if not step:
            try:
                step = session['current_step']
            except:
                pass
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        tag_list = api.get_splash_page_tag(shop_id=shop_id_select)
        settings_tag = {}
        if not shop_select:
            return redirect('/wifi')
        if type_page == 'default':
            pages = api.get_splash_page_by_type(shop_id_select, type_page)
            page = pages[0]
            page_id = page.get('_id')
            cards = api.get_cards(shop_id_select, mar_filter='default')

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)

            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)

            return render_template('new_hotspot/hotspot_default.html',
                                   shop=g.shop,
                                   cards=cards,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   page_id=page_id,
                                   tags=tags,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   page=page,
                                   step=step)
        elif type_page == 'youtube':
            pages = api.get_splash_page_by_type(shop_id_select, type_page)
            page = {}
            page_id = 'add'
            if pages.count() > 0:
                page = pages[0]
                page_id = page.get('_id')

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)

            return render_template('new_hotspot/hotspot_youtube.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   page_id=page_id,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   tags=tags,
                                   page=page,
                                   step=step)
        elif type_page == 'birthday':
            pages = api.get_splash_page_by_type(shop_id_select, type_page)
            page = {}
            page_id = 'add'
            if pages.count() > 0:
                page = pages[0]
                page_id = page.get('_id')

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)

            return render_template('new_hotspot/hotspot_birthday.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   page_id=page_id,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   tags=tags,
                                   page=page,
                                   step=step)
        elif type_page == 'loyal':
            pages = api.get_splash_page_by_type(shop_id_select, type_page)
            pages = [page for page in pages]
            total = api.total_splash_page_by_type(shop_id_select, type_page)

            # random splash display in preview
            page_active_random_arr = [
                page.get('_id') for page in pages
                if str(page.get('active')) == 'True'
            ]
            page_active_random = ''
            if len(page_active_random_arr) > 0:
                page_active_random = page_active_random_arr[0]

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)

            return render_template('new_hotspot/hotspot_loyal.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   pages=pages,
                                   total=total,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   tags=tags,
                                   page_active_random=page_active_random,
                                   step=step)
        elif type_page == 'tags':
            pages = api.get_splash_page_by_type(shop_id_select, "tag")
            pages = [page for page in pages]
            total = api.total_splash_page_by_type(shop_id_select, type_page)

            # random splash display in preview
            page_active_random_arr = [
                page.get('_id') for page in pages
                if str(page.get('active')) == 'True'
            ]
            page_active_random = ''
            if len(page_active_random_arr) > 0:
                page_active_random = page_active_random_arr[0]

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_tags.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   pages=pages,
                                   tag_list=tag_list,
                                   total=total,
                                   tags=tags,
                                   page_active_random=page_active_random,
                                   step=step)
        elif type_page == 'promotion':
            pages = api.get_splash_page_by_type(shop_id_select, type_page)
            pages = [page for page in pages]
            total = api.total_splash_page_by_type(shop_id_select, type_page)

            # random splash display in preview
            page_active_random_arr = [
                page.get('_id') for page in pages
                if str(page.get('active')) == 'True'
            ]
            page_active_random = ''
            if len(page_active_random_arr) > 0:
                page_active_random = page_active_random_arr[0]

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_promotion.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   pages=pages,
                                   total=total,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   tags=tags,
                                   page_active_random=page_active_random,
                                   step=step)
        elif type_page == 'weekday':
            pages = api.get_splash_page_weekday(shop_id_select, 'weekday')
            pages = [page for page in pages]
            # list_wk = ['Thứ 2', "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
            list_wk = [
                gettext("Thu_2"),
                gettext("Thu_3"),
                gettext("Thu_4"),
                gettext("Thu_5"),
                gettext("Thu_6"),
                gettext("Thu_7"),
                gettext("Chu_nhat")
            ]
            total = api.total_splash_page_by_type(shop_id_select, type_page)

            # random splash display in preview
            page_active_random_arr = [
                page.get('_id') for page in pages
                if str(page.get('active')) == 'True'
            ]
            page_active_random = ''
            if len(page_active_random_arr) > 0:
                page_active_random = page_active_random_arr[0]

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_weekday.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   list_wk=list_wk,
                                   pages=pages,
                                   total=total,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   tags=tags,
                                   page_active_random=page_active_random,
                                   step=step)
        elif type_page == 'survey':
            pages = api.list_survey_splash(shop_id_select)
            pages = [page for page in pages]
            total = api.total_survey_splash(shop_id_select)
            tags = [
                tag for tag in api.list_tags(merchant_id)
                if tag.get('name') and len(str(tag['name'])) > 0
            ]

            survey_other_step = []
            for i in range(1, 4):
                if str(i) != str(step):
                    this_step = 'survey_step_' + str(i)
                    if this_step in session:
                        choosed_page = session[this_step]
                        if choosed_page:
                            survey_other_step.append(choosed_page)

            choosed_this_step = None
            if ('survey_step_' + step) in session:
                choosed_this_step = session['survey_step_' + step]
            survey_item = None
            if choosed_this_step:
                survey_item = api.get_survey_item(choosed_this_step)
                # truong hop survey da bi xoa
                if not survey_item and ('survey_step_' + step) in session:
                    choosed_this_step = None
                    session.pop('survey_step_' + step, None)
            if len(survey_other_step) > 0:
                pages = [
                    page for page in pages
                    if str(page.get('_id')) not in survey_other_step
                ]
            for page in pages:
                if str(page.get('_id')) == str(
                        choosed_this_step) and survey_item:
                    page['choosed'] = True
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_survey.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   dealer_id=dealer_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   pages=pages,
                                   total=total,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   tags=tags,
                                   step=step,
                                   choosed_this_step=choosed_this_step)
        elif type_page == 'register':
            login_form = shop_select.get('login_form', {})

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_signup.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   tags=tags,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   login_form=login_form,
                                   step=step)
        elif type_page == 'plus_register':
            plus_login_form = shop_select.get('plus_login_form', {})

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_plus_signup.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   tags=tags,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   login_form=plus_login_form,
                                   step=step)
        elif type_page == 'woay':
            this_step = 'survey_step_' + str(step)
            shop_id_woay = shop_select.get('shop_id_woay')
            link_woay = shop_select.get('link_woay')
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_woay.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   tags=tags,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   step=step,
                                   shop_id_woay=shop_id_woay,
                                   link_woay=link_woay)
        elif type_page == 'hour':
            pages = api.get_splash_page_by_type(shop_id_select, type_page)
            pages = [page for page in pages]
            total = api.total_splash_page_by_type(shop_id_select, type_page)
            # random splash display in preview
            page_active_random_arr = [
                page.get('_id') for page in pages
                if str(page.get('active')) == 'True'
            ]
            page_active_random = ''
            if len(page_active_random_arr) > 0:
                page_active_random = page_active_random_arr[0]

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            return render_template('new_hotspot/hotspot_hour.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   tag_list=tag_list,
                                   pages=pages,
                                   total=total,
                                   tags=tags,
                                   page_active_random=page_active_random,
                                   step=step)
        elif type_page == 'connect_success':
            connect_success = shop_select.get('connect_success')

            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)
            login_form = shop_select.get('login_form', {})
            return render_template('new_hotspot/connect_success.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   tag_list=tag_list,
                                   tags=tags,
                                   connect_success=connect_success,
                                   login_form=login_form,
                                   step=step)
        elif type_page == '0':
            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            spin_step = 'spin_' + str(step)
            if spin_step in session:
                session.pop(spin_step, None)

            return render_template('new_hotspot/404.html', step=step)
        elif type_page == 'spin':
            pages = api.list_mini_game(shop_id_select)
            pages = [page for page in pages]
            total = api.total_mini_game(shop_id_select)
            survey_other_step = []
            for i in range(1, 4):
                if str(i) != str(step):
                    this_step = 'spin_' + str(i)
                    if this_step in session:
                        choosed_page = session[this_step]
                        if choosed_page:
                            survey_other_step.append(choosed_page)
            choosed_this_step = None
            if ('spin_' + step) in session:
                choosed_this_step = session['spin_' + step]

            survey_item = None
            if choosed_this_step:
                survey_item = api.item_mini_game_by_id(choosed_this_step)
                # truong hop minigame da bi xoa
                if not survey_item and ('spin_' + step) in session:
                    choosed_this_step = None
                    session.pop('spin_' + step, None)

            if len(survey_other_step) > 0:
                pages = [
                    page for page in pages
                    if str(page.get('_id')) not in survey_other_step
                ]

            for page in pages:
                if str(page.get('_id')) == str(
                        choosed_this_step) and survey_item:
                    page['choosed'] = True
            this_step = 'survey_step_' + str(step)
            if this_step in session:
                session.pop(this_step, None)
            # config_spin = shop_select.get('spin')
            return render_template('new_hotspot/hotspot_mini_game.html',
                                   shop=g.shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   dealer_id=dealer_id,
                                   shop_id_select=shop_id_select,
                                   shop_select=shop_select,
                                   pages=pages,
                                   total=total,
                                   tag_list=tag_list,
                                   settings=settings_tag,
                                   tags=tags,
                                   step=step,
                                   choosed_this_step=choosed_this_step)


@app.route('/<shop_id_select>/<type_page>/<page_id>/<action>', methods=['GET'])
@login_required
def splash_action(shop_id_select, type_page, page_id, action):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    step = request.args.get('step')
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    splash_item = None
    if type_page == 'survey':
        splash_item = api.get_survey_splash(shop_id=shop_id_select,
                                            survey_id=page_id)
    elif type_page == 'spin':
        splash_item = api.item_mini_game(shop_id_select, page_id)
    else:
        splash_item = api.get_splash_page_by_id(shop_id_select, page_id)
    if not splash_item and type_page != 'weekday':
        return redirect('/404')
    if action == 'active':
        if type_page == 'survey':
            update_active = True
            active = splash_item.get('active')
            if active:
                update_active = False
            api.update_survey_splash_page(shop_id=shop_id_select,
                                          survey_id=page_id,
                                          active=update_active)
            cur_choose_step = None
            if ('survey_step_' + step) in session:
                cur_choose_step = session['survey_step_' + step]
            if not update_active and cur_choose_step:
                session.pop('survey_step_' + step, None)
        elif type_page == 'weekday':
            api.active_splash_weekday(page_id=page_id, action=action)
        else:
            update_active = True
            active = splash_item.get('active')
            if active:
                update_active = False
            api.update_splash_page(shop_id=shop_id_select,
                                   item_id=page_id,
                                   type_page=type_page,
                                   active=update_active)
        return json.dumps({'result': True})
    elif action == 'remove':
        if type_page == 'survey':
            api.remove_survey_splash_page(shop_id=shop_id_select,
                                          survey_id=page_id)
            if ('survey_step_' + step) in session:
                session.pop('survey_step_' + step, None)
        else:
            update_active = True
            active = splash_item.get('active')
            if active:
                update_active = False
            api.remove_splash_page(shop_id=shop_id_select, card_id=page_id)
        return json.dumps({'result': True})
    elif action == 'choose':
        if type_page == 'survey':
            choose_status = True
            # tim survey da duoc chon o buoc nay -> id survey
            cur_choose_step = None
            if ('survey_step_' + step) in session:
                cur_choose_step = session['survey_step_' + step]
            if cur_choose_step and cur_choose_step == page_id:
                session.pop('survey_step_' + step, None)
                choose_status = False
            else:
                session['survey_step_' + step] = page_id
            return json.dumps({'result': True, 'choose_status': choose_status})
        elif type_page == 'spin':
            choose_status = True
            cur_choose_step = None
            if ('spin_' + step) in session:
                cur_choose_step = session['spin_' + step]
            if cur_choose_step and cur_choose_step == page_id:
                session.pop('spin_' + step, None)
                choose_status = False
            else:
                session['spin_' + step] = page_id
            return json.dumps({'result': True, 'choose_status': choose_status})


@app.route('/update_bitly_token', methods=['POST'])
@login_required
def update_bitly_token():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    access_token = request.form.get('access_token')
    api.update_merchant_bitly_token(merchant_id, access_token)
    return json.dumps({'result': True})


@app.route('/mini_game', methods=['GET'])
@login_required
def mini_game():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    locations = api.get_shop_by_merchant(merchant_id)
    if len(locations) > 0:
        shop_id_select = locations[0]['_id']
        return redirect('/mini_game/%s' % (shop_id_select))
    return render_template('nextify/wifi_locations.html',
                           merchant=merchant,
                           locations=locations)


@app.route('/mini_game/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def mini_game_shop(shop_id_select):
    page = int(request.args.get('page', 1))
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    # shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    login_form = shop_select.get('login_form', {})
    if request.method == 'GET':
        total = api.total_mini_game(shop_id_select)
        list_mini_game = api.list_mini_game(shop_id_select,
                                            page=page,
                                            page_size=settings.ITEMS_PER_PAGE)
        pagination = Pagination(page=page,
                                total=total,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        return render_template('nextify/mini_games.html',
                               shop_in_mer=shops,
                               user_login=user_login,
                               shop_id=shop_id,
                               merchant_id=merchant_id,
                               merchant=merchant,
                               shop=shop,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               login_form=login_form,
                               pagination=pagination,
                               list_mini_game=list_mini_game,
                               total=total,
                               dealer_id=dealer_id)
    else:
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        name = request.form.get('name')
        spin_config = shop_select.get('spin')
        spin = {}
        spin['name'] = name
        content = request.form.get('content')
        content_color = request.form.get('content_color')
        if not content or str(content) == 'None':
            content = ''
        spin['content'] = content
        spin['content_color'] = content_color
        turns = request.form.get('turns')
        spin['turns'] = turns
        time_reset = request.form.get('time_reset')
        if not time_reset or len(time_reset) == 0:
            time_reset = 4
        spin['time_reset'] = time_reset
        gifts = request.form.get('gifts')
        spin['total_gifts'] = gifts

        win_rate = request.form.get('win_rate')
        spin['win_rate'] = win_rate
        name_btn_win = request.form.get('name_btn_win')
        if not name_btn_win or str(name_btn_win) == 'None':
            name_btn_win = 'Quay ngay'
        spin['name_btn_win'] = name_btn_win

        content_win = request.form.get('content_win')
        if not content_win or str(content_win) == 'None':
            content_win = 'Xin chúc mừng, phần thưởng của bạn là'
        spin['content_win'] = content_win

        content_not_win = request.form.get('content_not_win')
        if not content_not_win or str(content_not_win) == 'None':
            content_not_win = 'Rất tiếc bạn đã không trúng thưởng, hãy thử lại vận may của mình.'
        spin['content_not_win'] = content_not_win

        background = request.files.get('background')

        if background and \
                background.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            background_name = storage_api.save_new_file(background)
            spin['background'] = background_name
        else:
            if spin_config and spin_config.get('background'):
                spin['background'] = spin_config.get('background')
            else:
                return json.dumps({
                    'results': False,
                    'error': 'Chưa chọn ảnh nền'
                })

        center = request.files.get('center')
        if center and \
                center.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            center_name = storage_api.save_new_file(center)
            spin['center'] = center_name
        else:
            if spin_config and spin_config.get('center'):
                spin['center'] = spin_config.get('center')
            else:
                return json.dumps({
                    'results': False,
                    'error': 'Chưa chọn ảnh nút quay'
                })

        gifts = int(gifts)
        gifts_detail = []
        for i in range(1, gifts + 1):
            each_gift = {}
            each_gift_input = request.files.get('gift_input_' + str(i))
            if each_gift_input and \
                    each_gift_input.filename.rsplit('.', 1)[1].lower() \
                    in ALLOWED_EXTENSIONS:
                photo = storage_api.save_new_file(each_gift_input)
                each_gift['images'] = photo

            each_gift_text = request.form.get('gift_text_' + str(i))
            if not each_gift_text or str(each_gift_text) == 'None':
                each_gift_text = ''
            each_gift['title'] = each_gift_text

            each_gift_method = request.form.get('gift_select_' + str(i))
            if str(each_gift_method) == 'gift':
                each_gift_method = 'gift'
            elif str(each_gift_method) == 'code':
                each_gift_method = 'code'
            elif str(each_gift_method) == 'vnpay':
                each_gift_method = 'vnpay'
            elif str(each_gift_method) == '0':
                each_gift_method = False

            each_gift['is_reward'] = each_gift_method

            each_gift_detail = request.form.get('gift_detail_' + str(i))
            if not each_gift_detail or str(each_gift_detail) == 'None':
                each_gift_detail = ''
            each_gift['detail'] = each_gift_detail

            each_gift_color = request.form.get('gift_color_' + str(i))
            if not each_gift_color or str(each_gift_color) == 'None':
                each_gift_color = ''
            each_gift['color'] = each_gift_color

            each_gift_count = request.form.get('gift_count_' + str(i))
            each_gift['amount'] = each_gift_count
            each_gift['remaining_amount'] = each_gift_count

            win_rate_gift = request.form.get('win_rate_gift_' + str(i))
            if not win_rate_gift or str(win_rate_gift) == 'None' or len(
                    win_rate_gift) == '':
                win_rate_gift = '0'
            each_gift['rate_reward'] = win_rate_gift

            win_rate_gravity = request.form.get('win_rate_gravity_' + str(i))
            if not win_rate_gravity or str(win_rate_gravity) == 'None' or len(
                    win_rate_gravity) == '':
                win_rate_gravity = '0'
            each_gift['rate_gravity'] = win_rate_gravity

            gifts_detail.append(each_gift)
        spin['gifts'] = gifts_detail

        # reset = request.form.get('reset')
        api.create_or_update_mini_game(shop_id=shop_id_select,
                                       camp_id=None,
                                       info=spin,
                                       game_type='spin')
        return json.dumps({'results': True})


@app.route('/mini_game/<shop_id_select>/reports/<page_id>', methods=['GET'])
@login_required
def mini_game_results(shop_id_select, page_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    item = api.item_mini_game_by_unique_id(page_id)
    if not item:
        item = api.item_mini_game_by_id(page_id)
    if not item:
        abort(404)
    page = int(request.args.get('page', 1))
    list_reports = api.list_mini_game_results(
        shop_id_select, page_id, page=page, page_size=settings.ITEMS_PER_PAGE)
    total = api.total_game_results(shop_id_select, page_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/mini_game_reports_results.html',
                           user_login=user_login,
                           shop_id=shop_id,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           shop=shop,
                           shop_select=shop_select,
                           shop_id_select=shop_id_select,
                           pagination=pagination,
                           list_reports=list_reports,
                           total=total,
                           item=item)


@app.route('/mini_game/<shop_id_select>/results/<page_id>',
           methods=['GET', 'POST'])
@login_required
def mini_game_item(shop_id_select, page_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    item = api.item_mini_game_by_unique_id(page_id)
    if not item:
        item = api.item_mini_game_by_id(page_id)
    if not item:
        abort(404)
    if request.method == 'GET':
        spin_config = item.get('info')
        old_reward_user = []
        shop_id_select = item.get('shop_id')
        shop_select = api.get_shop_info(shop_id_select)
        number_spin = spin_config.get('turns')

        return render_template('nextify/item_spin.html',
                               shop_id=shop_id,
                               shop_id_select=shop_id_select,
                               shop=shop_select,
                               user_login=user_login,
                               merchant_id=merchant_id,
                               merchant=merchant,
                               old_reward_user=json.dumps(old_reward_user),
                               spin_config=json.dumps(spin_config),
                               spin=spin_config,
                               number_spin=number_spin,
                               page_id=page_id,
                               item=item)
    else:
        name = request.form.get('name')
        spin_config = item.get('info')
        spin = {}
        spin['name'] = name
        content = request.form.get('content')
        content_color = request.form.get('content_color')
        if not content or str(content) == 'None':
            content = ''
        spin['content'] = content
        spin['content_color'] = content_color
        turns = request.form.get('turns')
        spin['turns'] = turns
        time_reset = request.form.get('time_reset')
        if not time_reset or len(time_reset) == 0:
            time_reset = 4
        spin['time_reset'] = time_reset
        gifts = request.form.get('gifts')
        spin['total_gifts'] = gifts

        win_rate = request.form.get('win_rate')
        spin['win_rate'] = win_rate
        name_btn_win = request.form.get('name_btn_win')
        if not name_btn_win or str(name_btn_win) == 'None':
            name_btn_win = 'Quay ngay'
        spin['name_btn_win'] = name_btn_win

        content_win = request.form.get('content_win')
        if not content_win or str(content_win) == 'None':
            content_win = 'Xin chúc mừng, phần thưởng của bạn là {{ gift }}'
        spin['content_win'] = content_win

        content_not_win = request.form.get('content_not_win')
        if not content_not_win or str(content_not_win) == 'None':
            content_not_win = 'Rất tiếc bạn đã không trúng thưởng, hãy thử lại vận may của mình.'
        spin['content_not_win'] = content_not_win

        background = request.files.get('background')

        if background and \
                background.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            background_name = storage_api.save_new_file(background)
            spin['background'] = background_name
        else:
            spin['background'] = spin_config.get('background')
        center = request.files.get('center')
        if center and \
                center.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            background_name = storage_api.save_new_file(center)
            spin['center'] = background_name
        else:
            spin['center'] = spin_config.get('center')

        gifts = int(gifts)
        gifts_detail = []
        for i in range(1, gifts + 1):
            each_gift = {}
            each_gift_input = request.files.get('gift_input_' + str(i))
            if each_gift_input and \
                    each_gift_input.filename.rsplit('.', 1)[1].lower() \
                    in ALLOWED_EXTENSIONS:
                photo = None
                photo = storage_api.save_new_file(each_gift_input)
                each_gift['images'] = photo
            else:
                each_gift['images'] = request.form.get('gift_ex_photo_' +
                                                       str(i))
            each_gift_text = request.form.get('gift_text_' + str(i))
            if not each_gift_text or str(each_gift_text) == 'None':
                each_gift_text = ''
            each_gift['title'] = each_gift_text

            each_gift_method = request.form.get('gift_select_' + str(i))
            if str(each_gift_method) == 'gift':
                each_gift_method = 'gift'
            elif str(each_gift_method) == 'code':
                each_gift_method = 'code'
            elif str(each_gift_method) == 'vnpay':
                each_gift_method = 'vnpay'
            elif str(each_gift_method) == '0':
                each_gift_method = False

            each_gift['is_reward'] = each_gift_method

            each_gift_detail = request.form.get('gift_detail_' + str(i))
            if not each_gift_detail or str(each_gift_detail) == 'None':
                each_gift_detail = ''
            each_gift['detail'] = each_gift_detail

            each_gift_color = request.form.get('gift_color_' + str(i))
            if not each_gift_color or str(each_gift_color) == 'None':
                each_gift_color = ''
            each_gift['color'] = each_gift_color

            each_gift_count = request.form.get('gift_count_' + str(i))
            each_gift['amount'] = each_gift_count
            each_gift['remaining_amount'] = each_gift_count

            win_rate_gift = request.form.get('win_rate_gift_' + str(i))
            if not win_rate_gift or str(win_rate_gift) == 'None' or len(
                    win_rate_gift) == '':
                win_rate_gift = '0'
            each_gift['rate_reward'] = win_rate_gift

            win_rate_gravity = request.form.get('win_rate_gravity_' + str(i))
            if not win_rate_gravity or str(win_rate_gravity) == 'None' or len(
                    win_rate_gravity) == '':
                win_rate_gravity = '0'
            each_gift['rate_gravity'] = win_rate_gravity

            gifts_detail.append(each_gift)
        spin['gifts'] = gifts_detail

        # reset = request.form.get('reset')
        api.create_or_update_mini_game(shop_id=shop_id_select,
                                       camp_id=page_id,
                                       info=spin,
                                       game_type='spin')
        return json.dumps({'results': True})


@app.route('/mini_game/<shop_id_select>/remove/<page_id>', methods=['GET'])
@login_required
def remove_mini_game_item(shop_id_select, page_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    api.DATABASE.mini_game_page.remove({
        'shop_id': ObjectId(shop_id_select),
        '_id': ObjectId(page_id)
    })
    return json.dumps({'results': True})


@app.route('/mini_game/<shop_id_select>/add', methods=['GET', 'POST'])
@login_required
def mini_game_shop_add(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    if request.method == 'GET':
        return render_template('nextify/new_spin.html',
                               shop_in_mer=shop_in_mer,
                               user_login=user_login,
                               shop_id=shop_id,
                               merchant_id=merchant_id,
                               merchant=merchant,
                               shop=shop,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               login_form=login_form,
                               dealer_id=dealer_id)


@app.route('/survey', methods=['GET'])
@login_required
def surveys_reports():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    locations = api.get_shop_by_merchant(merchant_id)
    if len(locations) > 0:
        shop_id_select = locations[0]['_id']
        return redirect('/surveys_reports/%s' % (shop_id_select))
    return render_template('nextify/wifi_locations.html',
                           merchant=merchant,
                           locations=locations,
                           user_login=user_login,
                           shop_id=shop_id)


@app.route('/surveys_reports/<shop_id_select>', methods=['GET'])
@login_required
def surveys_reports_shop(shop_id_select):
    page = int(request.args.get('page', 1))
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    login_form = shop.get('login_form', {})
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    # shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    surveys = api.total_survey_splash(shop_id_select)
    if surveys == 0:
        rating.init_survey(merchant, shop_id_select,
                           get_top_domain(request.host))
    list_survey = []
    list_survey_splash = api.list_survey_splash(
        shop_id_select, page=page, page_size=settings.ITEMS_PER_PAGE)

    for survey in list_survey_splash:
        survey_type = survey.get('survey_type')
        ans_dig = []
        if survey_type == 'multi_select' or survey_type == 'one_select':
            answers = survey.get('answers')
            for ans in answers:
                ans_item = []
                total_res = api.count_result_survery(survey['_id'],
                                                     survey_type,
                                                     shop_id_select,
                                                     ans.get('id'))
                ans_item.append(api.remove_accents(str(ans.get('value'))))
                ans_item.append(total_res)
                ans_dig.append(ans_item)

        if survey_type == 'rating':
            min_point = survey.get('min_point', 1)
            max_point = survey.get('max_point', 10)
            for ans in range(int(min_point), int(max_point) + 1):
                ans_item = []
                total_res = api.count_result_survery(survey['_id'],
                                                     survey_type,
                                                     shop_id_select, ans)
                ans_item.append(ans)
                ans_item.append(total_res)
                ans_dig.append(ans_item)
        survey['_id'] = str(survey['_id'])
        survey['shop_id'] = str(survey['shop_id'])
        survey['ans_dig'] = ans_dig
        if survey_type == 'comment':
            comment_count = api.count_result_survey_by_survey_id(
                survey['_id'], survey_type, shop_id_select)
            survey['comment_count'] = comment_count
        list_survey.append(survey)
    total_survey_splash = api.total_survey_splash(shop_id_select)

    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    pagination = Pagination(page=page,
                            total=total_survey_splash,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/survey_reports.html',
                           shop_in_mer=shops,
                           user_login=user_login,
                           shop_id=shop_id,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           shop=shop,
                           shop_select=shop_select,
                           shop_id_select=shop_id_select,
                           login_form=login_form,
                           pagination=pagination,
                           tags=tags,
                           list_survey_splash=list_survey,
                           total_survey_splash=total_survey_splash,
                           dealer_id=dealer_id)


@app.route('/new_wifi/<shop_id_select>/new_hotspot/<hotspot_type>',
           methods=['GET', 'POST'])
@login_required
def new_item_hotspot(shop_id_select, hotspot_type):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    template = 'nextify/item_hotspot_return.html'
    if hotspot_type == 'return':
        template = 'nextify/item_hotspot_return.html'
    elif hotspot_type == 'birthday':
        template = 'nextify/item_hotspot_birthday.html'
    elif hotspot_type == 'event':
        template = 'nextify/item_hotspot_event.html'
    elif hotspot_type == 'survey':
        template = 'nextify/item_hotspot_survey.html'
    if request.method == 'GET':
        return render_template(template,
                               shop_in_mer=shop_in_mer,
                               user_login=user_login,
                               shop_id=shop_id,
                               merchant_id=merchant_id,
                               merchant=merchant,
                               shop=shop,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               login_form=login_form)
    else:
        if hotspot_type == 'survey':
            if dealer_id == "5de0db6306e7eca17bd8e872":
                question_anv_1 = request.form.get('question_1')
                question_anv_2 = request.form.get('question_2')
                question_anv_3 = request.form.get('question_3')
                title_anvui = request.form.get('title_anvui')
                content_anvui = request.form.get('content_anvui')
                question = [question_anv_1, question_anv_2, question_anv_3]
            else:
                question = request.form.get('question')

            if not question or len(question) == 0:
                error = gettext("Ban_chua_nhap_cau_hoi?")
                return json.dumps({'error': error})
            survey_type = request.form.get('survey_type')
            if not survey_type or survey_type == '0':
                error = gettext("Ban_chua_chon_loai_khao_sat")
                return json.dumps({'error': error})
            answers = []
            comment = ''
            min_point = 1
            max_point = 5

            if survey_type == 'multi_select' or survey_type == 'one_select':
                answers = request.form.get('answers')
                answers = json.loads(answers)
                if len(answers) < 2:
                    error = gettext("Ban_can_de_xuat_it_nhat_2_dap_an")
                    return json.dumps({'error': error})
                for answer in answers:
                    if 'tag' in answer and len(answer['tag']) > 0:
                        answer['tag'] = ObjectId(answer['tag'])
            if survey_type == 'rating':
                min_point = request.form.get('min_point', '')
                max_point = request.form.get('max_point', '')
                min_point = min_point.strip()
                max_point = max_point.strip()
                if not min_point or not max_point or not min_point.isdigit(
                ) or not max_point.isdigit():
                    error = gettext("Thang_diem_cua_ban_chua_chinh_xac")
                    return json.dumps({'error': error})
                if int(max_point) < int(min_point):
                    error = gettext("Thang_diem_cua_ban_chua_chinh_xac")
                    return json.dumps({'error': error})
                if int(min_point) < 1:
                    error = gettext("Diem_thap_nhat_phai_lon_hon_0")
                    return json.dumps({'error': error})
                if int(max_point) > 10:
                    error = gettext(
                        "Diem_cao_nhat_nhat_phai_nho_hon_hoac_bang_10")
                    return json.dumps({'error': error})

            connect_button = request.form.get('connect_button', '')
            connect_button_color = request.form.get('connect_button_color')
            active_comment_fr = request.form.get('active_comment')
            active_comment = True
            if not active_comment_fr or str(active_comment_fr) == "None":
                active_comment = False
            photo = request.files.get('photo')
            photo_name = None
            if photo and \
                    photo.filename.rsplit('.', 1)[1].lower() \
                    in ALLOWED_EXTENSIONS:
                photo_name = storage_api.save_new_file(photo)

            active_request = request.form.get('active')
            active = True if str(active_request) == 'on' else False
            auto_popup = request.form.get('auto_popup')
            if dealer_id == "5de0db6306e7eca17bd8e872":
                survey_id = api.new_survey_splash_page_anvui(
                    shop_id=shop_id_select,
                    survey_type=survey_type,
                    question=question,
                    answers=answers,
                    comment=comment,
                    min_point=min_point,
                    max_point=max_point,
                    active=active,
                    auto_popup=auto_popup,
                    photo_name=photo_name,
                    title_anvui=title_anvui,
                    content_anvui=content_anvui,
                    merchant_id=merchant_id,
                    connect_button=connect_button)
            else:
                survey_id = api.new_survey_splash_page(
                    shop_id=shop_id_select,
                    survey_type=survey_type,
                    question=question,
                    answers=answers,
                    comment=comment,
                    min_point=min_point,
                    max_point=max_point,
                    active=active,
                    auto_popup=auto_popup,
                    photo_name=photo_name,
                    connect_button=connect_button,
                    connect_button_color=connect_button_color,
                    active_comment=active_comment)

            survey_item = api.get_survey_item(survey_id)
            slug = survey_item.get('slug')
            unique_string = str(shop_id_select) + \
                str(survey_id) + str(time.time())
            unique_id = slug + '_' + \
                hashlib.md5(str(unique_string).encode('utf-8')).hexdigest()
            long_url = "http://survey." + \
                get_top_domain(request.host) + "/" + unique_id
            api.update_survey_splash_page(shop_id_select,
                                          survey_id,
                                          unique_id=unique_id)
            bitly_token = merchant.get('bitly_access_token', '')
            if bitly_token and len(bitly_token) > 0:
                try:
                    api.update_bitly_url(shop_id_select, survey_id,
                                         bitly_token, long_url)
                except:
                    pass

            return json.dumps({'result': True})

        else:
            title = request.form.get('title')
            content = request.form.get('content')
            slug = None
            if title and len(title) > 0:
                slug = slugify(title)
            price = request.form.get('price')
            auto_mar = request.form.get('auto_mar')
            link_share = request.form.get('link_share')
            loyal_count = request.form.get('loyal_count', '')
            loyal_count_max = request.form.get('loyal_count_max', '')
            active_request = request.form.get('active')
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            visits_by = request.form.get('visits_by', 'shop')
            active = True if active_request else False

            if auto_mar == 'loyal':
                loyal_count = loyal_count.strip()
                loyal_count_max = loyal_count_max.strip()
                if not loyal_count:
                    error = gettext("Luot_den_phai_la_so_lon_hon_0")
                    return render_template(template,
                                           shop_in_mer=shop_in_mer,
                                           user_login=user_login,
                                           shop_id=shop_id,
                                           merchant_id=merchant_id,
                                           merchant=merchant,
                                           shop=shop,
                                           shop_select=shop_select,
                                           shop_id_select=shop_id_select,
                                           login_form=login_form,
                                           error=error)
                if not loyal_count_max:
                    error = gettext("Luot_den_phai_la_so_lon_hon_1")
                    return render_template(template,
                                           shop_in_mer=shop_in_mer,
                                           user_login=user_login,
                                           shop_id=shop_id,
                                           merchant_id=merchant_id,
                                           merchant=merchant,
                                           shop=shop,
                                           shop_select=shop_select,
                                           shop_id_select=shop_id_select,
                                           login_form=login_form,
                                           error=error)
                if not loyal_count.isdigit() or not loyal_count_max.isdigit():
                    error = gettext("Luot_den_phai_la_so_lon_hon_1")
                    return render_template(template,
                                           shop_in_mer=shop_in_mer,
                                           user_login=user_login,
                                           shop_id=shop_id,
                                           merchant_id=merchant_id,
                                           merchant=merchant,
                                           shop=shop,
                                           shop_select=shop_select,
                                           shop_id_select=shop_id_select,
                                           login_form=login_form,
                                           error=error)
                if int(loyal_count_max) < int(loyal_count):
                    error = gettext(
                        "Luot_den_nhieu_nhat_phai_lon_hon_luot_den_it_nhat")
                    return render_template(template,
                                           shop_in_mer=shop_in_mer,
                                           user_login=user_login,
                                           shop_id=shop_id,
                                           merchant_id=merchant_id,
                                           merchant=merchant,
                                           shop=shop,
                                           shop_select=shop_select,
                                           shop_id_select=shop_id_select,
                                           login_form=login_form,
                                           error=error)
            if auto_mar == 'promotion':
                if len(date_from) == 0 or len(date_to) == 0:
                    error = gettext("Ban_chua_chon_ngay_bat_dau_va_ket_thuc")
                    return render_template(template,
                                           shop_in_mer=shop_in_mer,
                                           user_login=user_login,
                                           shop_id=shop_id,
                                           merchant_id=merchant_id,
                                           merchant=merchant,
                                           shop=shop,
                                           shop_select=shop_select,
                                           shop_id_select=shop_id_select,
                                           login_form=login_form,
                                           error=error)
                is_date_correct = False
                try:
                    date_from_obj = datetime.strptime(date_from, "%d-%m-%Y")
                    date_to_obj = datetime.strptime(date_to, "%d-%m-%Y")

                    if date_from_obj < date_to_obj:
                        is_date_correct = True
                    else:
                        is_date_correct = False
                except:
                    is_date_correct = False
                if not is_date_correct:
                    error = gettext("Ngay_ket_thuc_phai_lon_hon_ngay_bat_dau")
                    return render_template(template,
                                           shop_in_mer=shop_in_mer,
                                           user_login=user_login,
                                           shop_id=shop_id,
                                           merchant_id=merchant_id,
                                           merchant=merchant,
                                           shop=shop,
                                           shop_select=shop_select,
                                           shop_id_select=shop_id_select,
                                           login_form=login_form,
                                           error=error)

            photo = request.files.get('photo')
            if not photo:
                error = gettext("Ban_chua_chon_anh_trang_chao")
                return render_template(template,
                                       shop_in_mer=shop_in_mer,
                                       user_login=user_login,
                                       shop_id=shop_id,
                                       merchant_id=merchant_id,
                                       merchant=merchant,
                                       shop=shop,
                                       shop_select=shop_select,
                                       shop_id_select=shop_id_select,
                                       login_form=login_form,
                                       error=error)

            photo_name = None
            if photo and \
                    photo.filename.rsplit('.', 1)[1].lower() \
                    in ALLOWED_EXTENSIONS:
                photo_name = storage_api.save_new_file(photo)

            api.new_splash_page(shop_id_select,
                                auto_mar,
                                active,
                                title=title,
                                content=content,
                                photo=photo_name,
                                slug=slug,
                                price=price,
                                link_share=link_share,
                                loyal_count=loyal_count,
                                loyal_count_max=loyal_count_max,
                                date_from=date_from,
                                date_to=date_to,
                                visits_by=visits_by)

            return redirect('/wifi/%s' % (shop_id_select))


@app.route('/wifi/<shop_id_select>/survey/<survey_id>/<action>')
@login_required
def item_survey_hotspot_action(shop_id_select, survey_id, action):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    survey_item = api.get_survey_splash(shop_id_select, survey_id)
    if not survey_item:
        return redirect('/404')
    if action == 'active':
        update_active = True
        active = survey_item.get('active')
        if active:
            update_active = False
        api.update_survey_splash_page(shop_id_select,
                                      survey_id,
                                      active=update_active)

        return redirect(
            url_for('splash_page_by_type',
                    shop_id_select=shop_id_select,
                    type_page='survey'))
    elif action == 'remove':
        api.remove_survey_splash_page(shop_id_select, survey_id)
        return json.dumps({'result': True})
    elif action == 'preview':
        survey_type = survey_item.get('survey_type')
        if survey_type == "multi_select":
            return render_template('wifi_portal/survey.html',
                                   shop_in_mer=shop_in_mer,
                                   user_login=user_login,
                                   shop_id=shop_id,
                                   merchant_id=merchant_id,
                                   merchant=merchant,
                                   shop=shop,
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   login_form=login_form,
                                   survey_item=survey_item)
        elif survey_type == "one_select":
            return render_template('wifi_portal/survey_single.html',
                                   shop_in_mer=shop_in_mer,
                                   user_login=user_login,
                                   shop_id=shop_id,
                                   merchant_id=merchant_id,
                                   merchant=merchant,
                                   shop=shop,
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   login_form=login_form,
                                   survey_item=survey_item)
        elif survey_type == 'rating':
            if merchant_id == "5dddd6d006e7eca17bd8e850":
                return render_template('wifi_portal/survey_rating_anvui.html',
                                       shop_in_mer=shop_in_mer,
                                       user_login=user_login,
                                       shop_id=shop_id,
                                       merchant_id=merchant_id,
                                       merchant=merchant,
                                       shop=shop,
                                       shop_select=shop_select,
                                       shop_id_select=shop_id_select,
                                       login_form=login_form,
                                       survey_item=survey_item)
            return render_template('wifi_portal/survey_rating.html',
                                   shop_in_mer=shop_in_mer,
                                   user_login=user_login,
                                   shop_id=shop_id,
                                   merchant_id=merchant_id,
                                   merchant=merchant,
                                   shop=shop,
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   login_form=login_form,
                                   survey_item=survey_item)
        elif survey_type == 'comment':
            return render_template('survey/survey_comment.html',
                                   shop_in_mer=shop_in_mer,
                                   user_login=user_login,
                                   shop_id=shop_id,
                                   merchant_id=merchant_id,
                                   merchant=merchant,
                                   shop=shop,
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   login_form=login_form,
                                   survey_item=survey_item)

    elif action == 'view':
        return render_template('nextify/view_survey_hotspot_item.html',
                               shop_in_mer=shop_in_mer,
                               user_login=user_login,
                               shop_id=shop_id,
                               merchant_id=merchant_id,
                               merchant=merchant,
                               shop=shop,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               login_form=login_form,
                               survey_item=survey_item)
    else:
        return redirect(
            url_for('splash_page_by_type',
                    shop_id_select=shop_id_select,
                    type_page='survey'))


@app.route('/surveys_reports/<shop_id_select>/remove/<survey_id>',
           methods=['GET'])
@login_required
def remove_survey_item(shop_id_select, survey_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    api.remove_survey_item(shop_id_select, survey_id)
    return json.dumps({'result': True})


@app.route('/surveys_reports/<shop_id_select>/update/<survey_id>',
           methods=['POST'])
@login_required
def update_survey_item(shop_id_select, survey_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    question = request.form.get('question').strip()
    connect_button = request.form.get('connect_button', '')
    connect_button_color = request.form.get('connect_button_color')
    active_comment_fr = request.form.get('active_comment')
    active_comment = True
    if not active_comment_fr or str(active_comment_fr) == "None":
        active_comment = False
    photo = request.files.get('photo')
    photo_name = None
    survey_item = api.get_survey_item(survey_id)
    old_slug = survey_item.get('slug')
    survey_type = survey_item.get('survey_type')
    phone_reply = request.form.get('phone_reply')
    cus_reply = request.form.get('cus_reply')
    answers = {}
    if photo and \
            photo.filename.rsplit('.', 1)[1].lower() \
            in ALLOWED_EXTENSIONS:
        photo_name = storage_api.save_new_file(photo)

    if survey_type in ['multi_select', 'one_select']:
        answers = request.form.get('answers')
        answers = json.loads(answers)
        for answer in answers:
            if 'tag' in answer and len(answer['tag']) > 0:
                answer['tag'] = ObjectId(answer['tag'])
    api.update_survey_item(shop_id_select,
                           survey_id,
                           question=question,
                           answers=answers,
                           photo=photo_name,
                           connect_button=connect_button,
                           connect_button_color=connect_button_color,
                           active_comment=active_comment,
                           phone_reply=phone_reply,
                           cus_reply=cus_reply)

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    merchant_id = shop_select.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    survey_item = api.get_survey_item(survey_id)
    slug = survey_item.get('slug')

    if slug != old_slug:
        unique_string = str(shop_id_select) + str(survey_id) + str(time.time())
        unique_id = slug + '_' + hashlib.md5(
            str(unique_string).encode('utf-8')).hexdigest()
        long_url = "http://survey." + \
                   get_top_domain(request.host) + "/" + unique_id
        api.update_survey_splash_page(shop_id_select,
                                      survey_id,
                                      unique_id=unique_id)
        bitly_token = merchant.get('bitly_access_token', '')
        if bitly_token and len(bitly_token) > 0:
            try:
                api.update_bitly_url(shop_id_select, survey_id, bitly_token,
                                     long_url)
            except:
                pass

    return json.dumps({'result': True})


@app.route('/surveys_reports/<shop_id_select>/view/<survey_id>',
           methods=['GET'])
@login_required
def view_result_survey(shop_id_select, survey_id):
    page = int(request.args.get('page', 1))
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    shop_id_select = shop_select['_id']
    survey = api.get_survey_item(survey_id)

    survey_type = survey.get('survey_type')
    ans_dig = []
    if survey_type in ['multi_select', 'one_select']:
        answers = survey.get('answers')
        for ans in answers:
            ans_item = []
            total_res = api.count_result_survery(survey['_id'], survey_type,
                                                 shop_id_select, ans.get('id'))
            ans_item.append(api.remove_accents(str(ans.get('value'))))
            ans_item.append(total_res)
            ans_dig.append(ans_item)

    if survey_type == 'rating':
        min_point = survey.get('min_point', 1)
        max_point = survey.get('max_point', 10)
        for ans in range(int(min_point), int(max_point) + 1):
            ans_item = []
            total_res = api.count_result_survery(survey['_id'], survey_type,
                                                 shop_id_select, ans)
            ans_item.append(ans)
            ans_item.append(total_res)
            ans_dig.append(ans_item)
    survey['_id'] = str(survey['_id'])
    survey['shop_id'] = str(survey['shop_id'])
    survey['ans_dig'] = ans_dig
    if survey_type == 'comment':
        comment_count = api.count_result_survey_by_survey_id(
            survey['_id'], survey_type, shop_id_select)
        survey['comment_count'] = comment_count

    return render_template('nextify/survey_report_item.html',
                           shop_in_mer=shop_in_mer,
                           user_login=user_login,
                           shop_id=shop_id,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           shop=shop,
                           shop_select=shop_select,
                           shop_id_select=shop_id_select,
                           page=survey)


@app.route('/surveys_reports/<shop_id_select>/results/<survey_id>',
           methods=['GET'])
@login_required
def surveys_reports_shop_results(shop_id_select, survey_id):
    page = int(request.args.get('page', 1))
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    login_form = shop.get('login_form', {})
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/404')
    survey_item = api.get_survey_item(survey_id)
    list_survey = api.list_survey_results(shop_id_select,
                                          survey_id,
                                          page=page,
                                          page_size=settings.ITEMS_PER_PAGE)
    total = api.total_survey_results_single(shop_id_select, survey_id)
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/survey_reports_results.html',
                           shop_in_mer=shop_in_mer,
                           user_login=user_login,
                           shop_id=shop_id,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           shop=shop,
                           shop_select=shop_select,
                           shop_id_select=shop_id_select,
                           pagination=pagination,
                           list_survey=list_survey,
                           total=total,
                           survey_item=survey_item,
                           tags=tags,
                           survey_id=survey_id)


@app.route('/create_locations', methods=['GET', 'POST'])
def create_locations():
    if request.method == 'GET':
        phone = session.get('is_login')
        is_email = validate_email(phone)
        is_slug = api.validate_slug(phone)
        if is_email:
            merchant = api.get_merchant_by_email(phone)
        elif is_slug:
            merchant = api.get_merchant_by_slug(phone)
        else:
            merchant = api.get_merchant_by_phone(phone)
        if not merchant or phone != session.get('is_hq'):
            session.pop('is_login', None)
            session.pop('is_superuser', None)
            session.pop('shop_id', None)
            session.pop('is_hq', None)
            return redirect('/')
        g.merchant = merchant
        return render_template('nextify/create_locations.html',
                               merchant=merchant,
                               phone=phone)
    else:
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        email = request.form.get('email')
        facebook_page = request.form.get('facebook_page')

        def error_locations(error):
            return render_template('nextify/create_locations.html',
                                   error=error,
                                   merchant=merchant)

        merchant_id = request.form.get('merchant_id')
        if not merchant_id:
            session.pop('is_login', None)
            session.pop('is_superuser', None)
            session.pop('shop_id', None)
            session.pop('is_hq', None)
            return redirect('/')
        merchant = api.get_merchant(merchant_id)
        if not merchant:
            session.pop('is_login', None)
            session.pop('is_superuser', None)
            session.pop('shop_id', None)
            session.pop('is_hq', None)
            return redirect('/')
        g.merchant = merchant

        name = request.form.get('name')
        if not name or len(name) == 0:
            error = gettext("Ten_dia_diem_khong_duoc_de_trong.")
            return error_locations(error)
        address = request.form.get('address')
        if not address or len(address) == 0:
            error = gettext("Dia_chi_lap_dat_khong_duoc_de_trong.")
            return error_locations(error)

        shop_id = None

        logo_filename = background_filename = None
        logo = request.files.get('logo')
        if not logo or logo.filename == '':
            error = gettext("Logo_khong_duoc_de_trong")
            return error_locations(error)

        if logo and allowed_file(logo.filename):
            logo_filename = storage_api.save_new_file(logo)

        else:
            error = gettext("Hay_chon_dung_dinh_dang_anh")
            return error_locations(error)

        background = request.files.get('background')
        if not background or background.filename == '':
            error = gettext("Hinh_nen_khong_duoc_de_trong")
            return error_locations(error)

        if background and allowed_file(background.filename):
            background_filename = storage_api.save_new_file(background)

        else:
            error = gettext("Hay_chon_dung_dinh_dang_anh")
            return error_locations(error)

        shop_id = api.create_shop(name,
                                  logo=logo_filename,
                                  address=address,
                                  background=background_filename,
                                  merchant_id=merchant_id,
                                  facebook_page=facebook_page)
        act_type = 'insert_location'
        activity_history.save_activity(act_type,
                                       merchant_id,
                                       shop_id,
                                       location_name=name)

        if shop_id:
            phone_merchant = merchant.get('phone')
            pass_merchant = merchant.get('password')
            email_merchant = merchant.get('email')
            api.insert_new_account(shop_id, phone_merchant, pass_merchant, "3",
                                   email_merchant, True)
            accounts = api.get_account(shop_id, phone)
            if not accounts and phone and str(
                    phone) != 'None' and api.get_phone_number(phone):
                api.insert_new_account(shop_id, phone, password, '1', email)

            g.shop_id = shop_id
            session['shop_id'] = str(shop_id)
            form_settings = {
                'phone_require': True,
                'gender': False,
                'phone': True,
                'birthday': False,
                'email': True,
                'name': True
            }
            api.update_login_form_settings(shop_id, form_settings)
            shop = api.get_shop_info(shop_id=shop_id)
            info = {}
            info['id'] = str(shop.get('_id'))
            name = shop.get('name', '')
            if str(name.encode('utf-8')) == 'None':
                name = ''
            info['name'] = api.remove_accents(name.encode('utf-8'))
            phone = shop.get('phone', '')
            if not phone or str(phone.encode('utf-8')) == 'None':
                phone = ''
            info['phone'] = phone
            email = shop.get('email', '')
            if type(email) is OrderedDict or not email or str(
                    email.encode('utf-8')) == 'None':
                email = ''
            info['email'] = email
            address = shop.get('address', '')
            if not address or str(address.encode('utf-8')) == 'None':
                address = ''
            info['address'] = api.remove_accents(address.encode('utf-8'))
            info['gateway_mac'] = shop.get('gateway_mac', [])
            return redirect('/locations')
        else:
            session.pop('is_login', None)
            session.pop('is_superuser', None)
            session.pop('shop_id', None)
            session.pop('is_hq', None)
            return redirect('/')


@app.route('/manage_shops', methods=['GET'])
@basic_auth.required
def shops():
    session['is_superuser'] = True
    if not api.get_super_user():
        api.insert_super_user()
    shop_ids = api.get_shop_ids()
    shops = [api.get_shop_info(i) for i in shop_ids]
    return render_template('shops.html', shops=shops)


@app.route('/shops', methods=['GET'])
@login_required
def shops_merchants():
    phone = session.get('is_login')
    if not phone:
        return redirect('/login')
    users = api.get_account(phone)
    shop_ids = users.get('shop_ids')
    shops = [api.get_shop_info(i['shop_id']) for i in shop_ids]
    return render_template('shops.html', shops=shops)


@app.route('/shops/<slug>', methods=['GET'])
def location(slug):
    shop = api.get_shop_by_slug(slug)
    if not shop:
        return redirect('/404')
    phone = session.get('is_login')
    session['shop_id'] = str(shop['_id'])
    session.pop('customers_filter', None)
    if session.get('is_superuser'):
        return redirect('/customers')
    else:
        user = api.get_account(shop['_id'], phone)
        if user:
            if get_roles_user(user['phone'], shop['_id']) in ['1', '3', '6']:
                return redirect('/customers')
            elif get_roles_user(user['phone'], shop['_id']) in ['2']:
                return redirect('/coupons')
            elif get_roles_user(user['phone'], shop['_id']) in ['4']:
                return redirect('/marketing')
            elif get_roles_user(user['phone'], shop['_id']) in ['5']:
                return redirect('/orders')
        else:
            return redirect('/shops/' + slug + '/login')


def get_total_customer_7d(shop_id, list_user_ids_staffs):
    return api.total_customers(shop_id, list_user_ids_staffs, 7)


def get_total_customer_30d(shop_id, list_user_ids_staffs):
    return api.total_customers(shop_id, list_user_ids_staffs, 30)


def get_total_customer_new(shop_id, list_user_ids_staffs):
    return api.total_customer_new(shop_id, list_user_ids_staffs)


def get_total_customer_loyal(shop_id, list_user_ids_staffs):
    return api.total_customer_loyal(shop_id, list_user_ids_staffs)


def get_total_customer_lost(shop_id, list_user_ids_staffs):
    return api.total_customer_lost(shop_id, list_user_ids_staffs)


def get_total_customer_birthday(shop_id, list_user_ids_staffs):
    return api.total_user_birthday(shop_id, list_user_ids_staffs)


@app.route("/export/<shop_id>/<filter>", methods=['GET'])
def export_records(shop_id, filter):
    shop = api.get_shop_info(shop_id)
    staffs = shop.get('staffs', [])
    emps = shop.get('emps', [])
    phone_numbers = shop.get('phone_numbers', [])
    if filter == "birthday":
        list_cus = api.data_export_birthday(shop_id, staffs, emps,
                                            phone_numbers)
    else:
        list_cus = api.data_export(shop_id, filter, staffs, emps,
                                   phone_numbers)
    return excel.make_response_from_array(list_cus,
                                          "csv",
                                          file_name="export_data")


@app.template_filter('country_phone')
def format_country_phone(phone):
    phone = phone.lstrip("0")
    phone = '84' + phone
    return phone


@app.route('/customer_files', methods=['GET'])
@login_required
def customers_export_list():
    shop = g.shop
    user_login = g.user
    shop_id = shop.get('_id')
    page = int(request.args.get('page', 1))
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    files = api.get_file_export_user(merchant_id, page,
                                     settings.ITEMS_PER_PAGE)
    total_files = api.total_file_export_user(merchant_id)
    pagination = Pagination(page=page,
                            total=total_files,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/merchant_file.html',
                           files=files,
                           pagination=pagination,
                           shop=shop,
                           page=page,
                           user_login=user_login,
                           merchant=merchant)


@app.route('/import_files', methods=['GET'])
@login_required
def import_files():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    tags = api.list_tags(merchant_id)
    return render_template('nextify/import_files.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           merchant_id=merchant_id,
                           shop_in_mer=shop_in_mer,
                           tags=tags)


@app.route('/import_kiotviet_files', methods=['GET', 'POST'])
@login_required
def view_import_kiotviet_files():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    tags = api.list_tags(merchant_id)
    if request.method == 'GET':
        return render_template("nextify/import_kiotviet_files.html",
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shop_in_mer,
                               tags=tags)
    else:
        shop_select = request.form.get('shop_select')
        file_import = request.files.get('files')
        is_employee = request.form.get('is_employee')
        is_employee = "True" if str(is_employee) == "on" else "False"
        if file_import and \
                file_import.filename.rsplit('.', 1)[1].lower() in ['csv',
                                                                   'xlsx',
                                                                   'xls']:
            # file_data = file_import.stream.read()
            # when = time.time()
            # logo_filename = \
            #     hashlib.md5(file_data).hexdigest() + '_' + str(shop_select) + '_' + str(int(when)) + '.' + \
            #     file_import.filename.rsplit('.', 1)[1]
            # data_logo = {
            #     'file_name': logo_filename,
            #     'file_data': base64.b64encode(file_data),
            #     'origin_name': file_import.filename
            # }
            logo_filename = ''
            logo_filename = storage_api.save_new_file(file_import)

            tags = request.form.get('real_tags_filter', '')
            tags_array = []
            tags_data = []
            list_tags = ['import', 'kiotviet']
            for tag in list_tags:
                check_tag = api.check_tag_name(tag, merchant_id)
                if not check_tag:
                    check_tag = api.create_tags(merchant_id,
                                                tag,
                                                tag,
                                                tag_id=None,
                                                shop_id=str(shop_select))
                tags_array.append(str(check_tag))
            if tags and len(tags) > 0:
                tags_data = tags.split(',')
                for tag in tags_data:
                    if tag not in tags_array:
                        tags_array.append(str(tag))
            if logo_filename and len(logo_filename) > 0:
                producer_data = {
                    "shop_id": str(shop_select),
                    "task_name": "celery_import_kiotviet_customers",
                    "params": {
                        "merchant_id": str(merchant_id),
                        "shop_id": str(shop_select),
                        "tags_array": tags_array,
                        "logo_filename": str(logo_filename),
                        "is_employee": is_employee,
                    }
                }

                producer_data = json.dumps(producer_data).encode('utf-8')
                producer.send(settings.cms_consumer, producer_data)
                producer.flush()
                message = gettext(
                    "File_dang_duoc_xu_ly,_du_lieu_se_duoc_cap_nhat_sau_3-5_phut_nua."
                )
                return render_template("nextify/import_kiotviet_files.html",
                                       shop=shop,
                                       user_login=user_login,
                                       merchant=merchant,
                                       merchant_id=merchant_id,
                                       message=message,
                                       shop_in_mer=shop_in_mer,
                                       tags=tags)
            else:
                error = gettext("Co_loi_xay_ra,_xin_thu_lai_sau")
                return render_template("nextify/import_kiotviet_files.html",
                                       shop=shop,
                                       user_login=user_login,
                                       merchant=merchant,
                                       merchant_id=merchant_id,
                                       error=error,
                                       shop_in_mer=shop_in_mer,
                                       tags=tags)
        else:
            error = gettext(
                "Vui_long_chon_File_co_dinh_dang_CSV,_XLS_hoac_XLSX._File_can_su_dung_theo_mau_cua_Nextify."
            )
            return render_template("nextify/import_kiotviet_files.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   error=error,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)


@app.route('/import_haravan_files', methods=['GET', 'POST'])
@login_required
def import_haravan_files():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    tags = api.list_tags(merchant_id)
    if request.method == 'GET':
        return render_template("nextify/import_haravan_files.html",
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shop_in_mer,
                               tags=tags)
    else:
        shop_select = request.form.get('shop_select')
        file_import = request.files.get('files')
        is_employee = request.form.get('is_employee')
        is_employee = "True" if str(is_employee) == "on" else "False"
        if file_import and \
                file_import.filename.rsplit('.', 1)[1].lower() in ['csv',
                                                                   'xlsx',
                                                                   'xls']:

            logo_filename = storage_api.save_new_file(file_import)
            tags = request.form.get('real_tags_filter', '')
            tags_array = []
            tags_data = []
            list_tags = ['import', 'haravan']
            for tag in list_tags:
                check_tag = api.check_tag_name(tag, merchant_id)
                if not check_tag:
                    check_tag = api.create_tags(merchant_id,
                                                tag,
                                                tag,
                                                tag_id=None,
                                                shop_id=str(shop_select))
                tags_array.append(str(check_tag))
            if tags and len(tags) > 0:
                tags_data = tags.split(',')
                for tag in tags_data:
                    if tag not in tags_array:
                        tags_array.append(str(tag))

            producer_data = {
                "shop_id": str(shop_select),
                "task_name": "celery_import_haravan_customers",
                "params": {
                    "merchant_id": str(merchant_id),
                    "shop_id": str(shop_select),
                    "tags_array": tags_array,
                    "logo_filename": str(logo_filename),
                    "is_employee": is_employee,
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()
            message = gettext(
                "File_dang_duoc_xu_ly,_du_lieu_se_duoc_cap_nhat_sau_3-5_phut_nua."
            )
            return render_template("nextify/import_haravan_files.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   message=message,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)
        else:
            error = gettext(
                "Vui_long_chon_File_co_dinh_dang_CSV,_XLS_hoac_XLSX._File_can_su_dung_theo_mau_cua_Nextify."
            )
            return render_template("nextify/import_haravan_files.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   error=error,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)


@app.route('/import_customers', methods=['GET', 'POST'])
@login_required
def import_customers():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    tags = api.list_tags(merchant_id)
    if request.method == 'GET':
        return render_template("nextify/import_customers.html",
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shop_in_mer,
                               tags=tags)
    else:
        shop_select = request.form.get('shop_select')
        file_import = request.files.get('files')
        is_employee = request.form.get('is_employee')
        is_employee = "True" if str(is_employee) == "on" else "False"
        if file_import and \
                file_import.filename.rsplit('.', 1)[1].lower() in ['csv',
                                                                   'xlsx',
                                                                   'xls']:

            logo_filename = storage_api.save_new_file(file_import)
            tags = request.form.get('real_tags_filter', '')
            tags_array = []
            check_tag = api.check_tag_name('import', merchant_id)
            if not check_tag:
                check_tag = api.create_tags(merchant_id,
                                            'import',
                                            'import',
                                            tag_id=None,
                                            shop_id=shop_select)
            tags_array.append(str(check_tag))
            if tags and len(tags) > 0:
                tags_data = tags.split(',')
                for tag in tags_data:
                    if tag not in tags_array:
                        tags_array.append(str(tag))
            producer_data = {
                "shop_id": str(shop_select),
                "task_name": "celery_import_manual_customers",
                "params": {
                    "merchant_id": str(merchant_id),
                    "shop_id": str(shop_select),
                    "tags_array": tags_array,
                    "logo_filename": str(logo_filename),
                    "is_employee": is_employee,
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()
            message = gettext(
                "File_dang_duoc_xu_ly,_du_lieu_se_duoc_cap_nhat_sau_3-5_phut_nua."
            )
            return render_template("nextify/import_customers.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   message=message,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)
        else:
            error = gettext(
                "Vui_long_chon_File_co_dinh_dang_CSV,_XLS_hoac_XLSX._File_can_su_dung_theo_mau_cua_Nextify."
            )
            return render_template("nextify/import_customers.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   error=error,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)


@app.route('/import_ipos_files', methods=['GET', 'POST'])
@login_required
def view_import_ipos_files():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    tags = api.list_tags(merchant_id)
    if request.method == 'GET':
        return render_template("nextify/import_ipos_files.html",
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shop_in_mer,
                               tags=tags)
    else:
        import_method = request.form.get('import_method')
        shop_select = request.form.get('shop_select')
        file_import = request.files.get('files')
        is_employee = request.form.get('is_employee')
        is_employee = "True" if str(is_employee) == "on" else "False"
        if file_import and \
                file_import.filename.rsplit('.', 1)[1].lower() in ['csv',
                                                                   'xlsx',
                                                                   'xls']:

            logo_filename = storage_api.save_new_file(file_import)

            tags = request.form.get('real_tags_filter', '')
            tags_array = []
            tags_data = []
            list_tags = ['import', 'ipos']
            for tag in list_tags:
                check_tag = api.check_tag_name(tag, merchant_id)
                if not check_tag:
                    check_tag = api.create_tags(merchant_id,
                                                tag,
                                                tag,
                                                tag_id=None,
                                                shop_id=str(shop_select))
                tags_array.append(str(check_tag))
            if tags and len(tags) > 0:
                tags_data = tags.split(',')
                for tag in tags_data:
                    if tag not in tags_array:
                        tags_array.append(str(tag))
            producer_data = {
                "shop_id": str(shop_select),
                "task_name": "celery_import_ipos_customers",
                "params": {
                    "merchant_id": str(merchant_id),
                    "shop_id": str(shop_select),
                    "tags_array": tags_array,
                    "logo_filename": str(logo_filename),
                    "is_employee": is_employee,
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()

            message = gettext(
                "File_dang_duoc_xu_ly,_du_lieu_se_duoc_cap_nhat_sau_3-5_phut_nua."
            )
            return render_template("nextify/import_ipos_files.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   message=message,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)
        else:
            error = gettext(
                "Vui_long_chon_File_co_dinh_dang_CSV,_XLS_hoac_XLSX._File_can_su_dung_theo_mau_cua_Ipos."
            )
            return render_template("nextify/import_ipos_files.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   error=error,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)


@app.route('/import_cukcuk_files', methods=['GET', 'POST'])
@login_required
def import_cukcuk_files():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    tags = api.list_tags(merchant_id)
    if request.method == 'GET':
        return render_template("nextify/import_cukcuk_files.html",
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shop_in_mer,
                               tags=tags)
    else:
        import_method = request.form.get('import_method')
        shop_select = request.form.get('shop_select')
        file_import = request.files.get('files')
        is_employee = request.form.get('is_employee')
        is_employee = "True" if str(is_employee) == "on" else "False"
        if file_import and \
                file_import.filename.rsplit('.', 1)[1].lower() in ['csv',
                                                                   'xlsx',
                                                                   'xls']:

            logo_filename = storage_api.save_new_file(file_import)

            tags = request.form.get('real_tags_filter', '')
            tags_array = []
            list_tags = ['import', 'cukcuk']
            for tag in list_tags:
                check_tag = api.check_tag_name(tag, merchant_id)
                if not check_tag:
                    check_tag = api.create_tags(merchant_id,
                                                tag,
                                                tag,
                                                tag_id=None,
                                                shop_id=str(shop_select))
                tags_array.append(str(check_tag))
            if tags and len(tags) > 0:
                tags_data = tags.split(',')
                for tag in tags_data:
                    if tag not in tags_array:
                        tags_array.append(str(tag))
            producer_data = {
                "shop_id": str(shop_select),
                "task_name": "celery_import_cukcuck_customers",
                "params": {
                    "merchant_id": str(merchant_id),
                    "shop_id": str(shop_select),
                    "tags_array": tags_array,
                    "logo_filename": str(logo_filename),
                    "is_employee": is_employee,
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()

            message = gettext(
                "File_dang_duoc_xu_ly,_du_lieu_se_duoc_cap_nhat_sau_3-5_phut_nua."
            )
            return render_template("nextify/import_cukcuk_files.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   message=message,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)
        else:
            error = gettext(
                "Vui_long_chon_File_co_dinh_dang_CSV,_XLS_hoac_XLSX._File_can_su_dung_theo_mau_cua_Cukcuk."
            )
            return render_template("nextify/import_cukcuk_files.html",
                                   shop=shop,
                                   user_login=user_login,
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   error=error,
                                   shop_in_mer=shop_in_mer,
                                   tags=tags)


@app.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    merchant_name = merchant.get('name')

    page = int(request.args.get('page', 1))
    list_cus = api.get_contacts(merchant_id, page, settings.ITEMS_PER_PAGE)
    total = api.total_merchant_customers(merchant_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template("nextify/contacts.html",
                           list_cus=list_cus,
                           page=page,
                           merchant=merchant,
                           pagination=pagination,
                           total=total)


@app.route('/contacts/index/<contact_id>', methods=['GET', 'POST'])
@login_required
def single_contact(contact_id):
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    contact = api.get_cus_by_id(contact_id, merchant_id=merchant_id)
    return render_template("nextify/contact.html",
                           merchant=merchant,
                           contact=contact,
                           contact_id=contact_id)


@app.route('/contacts/index/<contact_id>/notes', methods=['GET', 'POST'])
@login_required
def single_contact_note(contact_id):
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    contact = api.get_cus_by_id(contact_id, merchant_id=merchant_id)
    return render_template("nextify/contact_note.html",
                           merchant=merchant,
                           contact=contact,
                           contact_id=contact_id)


@app.route('/companies', methods=['GET', 'POST'])
@login_required
def view_companies():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    page = int(request.args.get('page', 1))
    list_comp = companies.list_companies(merchant_id, page,
                                         settings.ITEMS_PER_PAGE)
    total = companies.total_companies(merchant_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template("nextify/companies.html",
                           page=page,
                           merchant=merchant,
                           list_comp=list_comp,
                           total=total,
                           pagination=pagination)


@app.route('/groups', methods=['GET', 'POST'])
@login_required
def view_groups():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    merchant_name = merchant.get('name')
    print(merchant_name)
    page = int(request.args.get('page', 1))
    list_groups = groups.list_groups(merchant_id, page,
                                     settings.ITEMS_PER_PAGE)
    total = groups.total_groups(merchant_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template("nextify/groups.html",
                           page=page,
                           merchant=merchant,
                           list_groups=list_groups,
                           total=total,
                           pagination=pagination)

@app.route('/automations/list', methods=['GET', 'POST'])
@login_required
def view_automations():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    merchant_name = merchant.get('name')
    page = int(request.args.get('page', 1))
    list_groups = automation.list_automations(merchant_id, page,
                                     settings.ITEMS_PER_PAGE)
    total = automation.total_automations(merchant_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template("nextify/automation.html",
                           page=page,
                           merchant=merchant,
                           list_groups=list_groups,
                           total=total,
                           pagination=pagination)

@app.route('/segments', methods=['GET', 'POST'])
@login_required
def view_segments():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    merchant_name = merchant.get('name')
    print(merchant_name)
    page = int(request.args.get('page', 1))
    list_segment = segments.list_segment(merchant_id, page,
                                         settings.ITEMS_PER_PAGE)
    total = segments.total_segment(merchant_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template("nextify/segments.html",
                           page=page,
                           merchant=merchant,
                           list_segment=list_segment,
                           total=total,
                           pagination=pagination)

@app.route('/automations/builder', methods=['GET', 'POST'])
@login_required
def view_automations_builder():
    return render_template("automation/builder.html")

@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_id = shop.get('_id')
    shops = []
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    if g.role == '3':

        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        loc_id = request.args.get('loc_id', 'all')
        from_date = None
        to_date = None
        min_visit = None
        max_visit = None
        gender = None
        sort = 'time_asc'
        bday_from_date = None
        bday_to_date = None
        ranks = 'all'
        min_points = ''
        max_points = ''
        min_cash = ''
        max_cash = ''
        lost_day = 0
        tags_array = []
        employee = ""
        phone_filter = ""
        email_filter = ""
        zalo_filter = ""
        fb_filter = ""
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        customers_filter = session.get('customers_filter', {})
        if customers_filter or len(customers_filter) > 0:
            from_date = customers_filter.get('from_date')
            to_date = customers_filter.get('to_date')
            min_visit = customers_filter.get('min_visit')
            max_visit = customers_filter.get('max_visit')
            lost_day = customers_filter.get('lost_day')
            gender = customers_filter.get('gender')
            sort = customers_filter.get('sort')
            bday_from_date = customers_filter.get('bday_from_date')
            bday_to_date = customers_filter.get('bday_to_date')
            tags_array = customers_filter.get('filter_tags')
            employee = request.form.get('employee')
        list_cus = []
        total = 0
        total_phone = 0
        total_email = 0
        total_zalo = 0
        total_messenger_id = 0
        shop_select_name = merchant.get('name')
        if loc_id and str(loc_id) != 'all':
            shop_select_db = api.get_shop_info(shop_id=loc_id)
            shop_select_name = shop_select_db.get('name')
            list_cus = api.get_shop_customers(
                merchant_id,
                loc_id,
                from_date=from_date,
                to_date=to_date,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                employee=employee,
                page=page,
                page_size=settings.ITEMS_PER_PAGE,
                phone_filter=phone_filter,
                email_filter=email_filter,
                zalo_filter=zalo_filter,
                fb_filter=fb_filter)
            total = api.total_shop_customers(loc_id,
                                             from_date=from_date,
                                             to_date=to_date,
                                             min_visit=min_visit,
                                             max_visit=max_visit,
                                             lost_day=lost_day,
                                             gender=gender,
                                             employee=employee,
                                             sort=sort,
                                             bday_from_date=bday_from_date,
                                             bday_to_date=bday_to_date,
                                             tags_array=tags_array,
                                             phone_filter=phone_filter,
                                             email_filter=email_filter,
                                             zalo_filter=zalo_filter,
                                             fb_filter=fb_filter)
            total_phone = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_phone=True)
            total_zalo = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_zalo=True)
            total_email = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_email=True)
            total_messenger_id = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_messenger_id=True)
        else:
            list_cus = api.get_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                employee=employee,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                page=page,
                page_size=settings.ITEMS_PER_PAGE,
                phone_filter=phone_filter,
                email_filter=email_filter,
                zalo_filter=zalo_filter,
                fb_filter=fb_filter)
            total = api.total_merchant_customers(merchant_id,
                                                 from_date=from_date,
                                                 to_date=to_date,
                                                 employee=employee,
                                                 min_visit=min_visit,
                                                 max_visit=max_visit,
                                                 lost_day=lost_day,
                                                 gender=gender,
                                                 sort=sort,
                                                 bday_from_date=bday_from_date,
                                                 bday_to_date=bday_to_date,
                                                 tags_array=tags_array,
                                                 phone_filter=phone_filter,
                                                 email_filter=email_filter,
                                                 zalo_filter=zalo_filter,
                                                 fb_filter=fb_filter)
            total_phone = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_phone=True)
            total_zalo = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_zalo=True)
            total_email = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_email=True)
            total_messenger_id = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_messenger_id=True)
        phone_percent = 0
        email_percent = 0
        mess_percent = 0
        zalo_percent = 0
        try:
            mess_percent = float("%0.2f" %
                                 (total_messenger_id * 100 / float(total)))
        except ZeroDivisionError:
            pass

        try:
            email_percent = float("%0.2f" % (total_email * 100 / float(total)))
        except ZeroDivisionError:
            pass
        try:
            phone_percent = float("%0.2f" % (total_phone * 100 / float(total)))
        except ZeroDivisionError:
            pass
        try:
            zalo_percent = float("%0.2f" % (total_zalo * 100 / float(total)))
        except ZeroDivisionError:
            pass

        pagination = Pagination(page=page,
                                total=total,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')

        return render_template("nextify/customers.html",
                               merchant_id=merchant_id,
                               loc_id=loc_id,
                               customers=list_cus,
                               from_date=from_date,
                               to_date=to_date,
                               min_visit=min_visit,
                               max_visit=max_visit,
                               employee=employee,
                               lost_day=lost_day,
                               bday_from_date=bday_from_date,
                               bday_to_date=bday_to_date,
                               ranks=ranks,
                               gender=gender,
                               sort=sort,
                               shop=shop,
                               shops=shops,
                               page=page,
                               phone_filter=phone_filter,
                               email_filter=email_filter,
                               zalo_filter=zalo_filter,
                               fb_filter=fb_filter,
                               user_login=user_login,
                               pagination=pagination,
                               total=total,
                               merchant=merchant,
                               filter_tags=tags_array,
                               min_cash=min_cash,
                               max_cash=max_cash,
                               min_points=min_points,
                               max_points=max_points,
                               shop_in_mer=shops,
                               tags=tags,
                               total_phone=total_phone,
                               total_email=total_email,
                               total_zalo=total_zalo,
                               total_messenger_id=total_messenger_id,
                               phone_percent=phone_percent,
                               email_percent=email_percent,
                               zalo_percent=zalo_percent,
                               mess_percent=mess_percent,
                               shop_select_name=shop_select_name)
    else:
        shop = g.shop
        user_login = g.user
        merchant = g.merchant
        merchant_id = shop.get('merchant_id')
        shop_id = shop.get('_id')
        shops = []
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        if g.role == '3':

            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]
        page = int(request.args.get('page', 1))
        loc_id = request.form.get('loc_id', 'all')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        min_visit = request.form.get('min_visit')
        max_visit = request.form.get('max_visit')
        sort = request.form.get('sort', 'time_asc')
        bday_from_date = request.form.get('bday_from_date')
        bday_to_date = request.form.get('bday_to_date')
        gender_list = request.form.getlist('gender')
        employee = request.form.get('employee')
        phone_filter = request.form.get('phone_filter')
        email_filter = request.form.get('email_filter')
        zalo_filter = request.form.get('zalo_filter')
        fb_filter = request.form.get('fb_filter')
        gender = []
        shop_select_name = merchant.get('name')

        if 0 < len(gender_list) < 3:
            gender = [str(gen) for gen in gender_list]
            if '0' in gender:
                gender.append('')
                gender.append(None)

        else:
            gender = None
        max_visit = request.form.get('max_visit')
        lost_day = request.form.get('lost_day', 0)

        filter_tags = request.form.get('real_tags_filter', '')
        tags_array = []
        if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
            tags_array = filter_tags.split(',')
            tags_array = [str(tag) for tag in tags_array]

        session['customers_filter'] = {}
        session['customers_filter']['from_date'] = from_date
        session['customers_filter']['to_date'] = to_date
        session['customers_filter']['min_visit'] = min_visit
        session['customers_filter']['max_visit'] = max_visit
        session['customers_filter']['lost_day'] = lost_day
        session['customers_filter']['sort'] = sort
        session['customers_filter']['employee'] = employee
        session['customers_filter']['bday_from_date'] = bday_from_date
        session['customers_filter']['bday_to_date'] = bday_to_date
        session['customers_filter']['gender'] = gender
        session['customers_filter']['is_zalo'] = None
        session['customers_filter']['filter_tags'] = tags_array
        list_cus = []
        total = 0
        total_phone = 0
        total_email = 0
        total_zalo = 0
        total_messenger_id = 0
        if loc_id and str(loc_id) != 'all':
            shop_select_db = api.get_shop_info(shop_id=loc_id)
            shop_select_name = shop_select_db.get('name')
            list_cus = api.get_shop_customers(
                merchant_id,
                loc_id,
                from_date=from_date,
                to_date=to_date,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                employee=employee,
                page=page,
                page_size=settings.ITEMS_PER_PAGE,
                phone_filter=phone_filter,
                email_filter=email_filter,
                zalo_filter=zalo_filter,
                fb_filter=fb_filter)
            total = api.total_shop_customers(loc_id,
                                             from_date=from_date,
                                             to_date=to_date,
                                             min_visit=min_visit,
                                             max_visit=max_visit,
                                             lost_day=lost_day,
                                             gender=gender,
                                             employee=employee,
                                             sort=sort,
                                             bday_from_date=bday_from_date,
                                             bday_to_date=bday_to_date,
                                             tags_array=tags_array,
                                             phone_filter=phone_filter,
                                             email_filter=email_filter,
                                             zalo_filter=zalo_filter,
                                             fb_filter=fb_filter)
            total_phone = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_phone=True)
            total_zalo = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_zalo=True)
            total_email = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_email=True)
            total_messenger_id = api.total_shop_customers(
                loc_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_messenger_id=True)
        else:
            list_cus = api.get_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                employee=employee,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                page=page,
                page_size=settings.ITEMS_PER_PAGE,
                phone_filter=phone_filter,
                email_filter=email_filter,
                zalo_filter=zalo_filter,
                fb_filter=fb_filter)
            total = api.total_merchant_customers(merchant_id,
                                                 from_date=from_date,
                                                 to_date=to_date,
                                                 employee=employee,
                                                 min_visit=min_visit,
                                                 max_visit=max_visit,
                                                 lost_day=lost_day,
                                                 gender=gender,
                                                 sort=sort,
                                                 bday_from_date=bday_from_date,
                                                 bday_to_date=bday_to_date,
                                                 tags_array=tags_array,
                                                 phone_filter=phone_filter,
                                                 email_filter=email_filter,
                                                 zalo_filter=zalo_filter,
                                                 fb_filter=fb_filter)
            total_phone = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_phone=True)
            total_zalo = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_zalo=True)
            total_email = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_email=True)
            total_messenger_id = api.total_merchant_customers(
                merchant_id,
                from_date=from_date,
                to_date=to_date,
                employee=employee,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                is_has_messenger_id=True)
        phone_percent = 0
        email_percent = 0
        mess_percent = 0
        zalo_percent = 0
        if total != 0:
            try:
                mess_percent = float("%0.2f" %
                                     (total_messenger_id * 100 / float(total)))
            except ZeroDivisionError:
                return 0

            try:
                email_percent = float("%0.2f" %
                                      (total_email * 100 / float(total)))
            except ZeroDivisionError:
                return 0
            try:
                phone_percent = float("%0.2f" %
                                      (total_phone * 100 / float(total)))
            except ZeroDivisionError:
                return 0
            try:
                zalo_percent = float("%0.2f" %
                                     (total_zalo * 100 / float(total)))
            except ZeroDivisionError:
                return 0
        pagination = Pagination(page=page,
                                total=total,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]

        return render_template("nextify/customer_content.html",
                               merchant_id=merchant_id,
                               customers=list_cus,
                               loc_id=loc_id,
                               page=page,
                               user_login=user_login,
                               employee=employee,
                               pagination=pagination,
                               total=total,
                               total_phone=total_phone,
                               total_email=total_email,
                               total_zalo=total_zalo,
                               total_messenger_id=total_messenger_id,
                               phone_percent=phone_percent,
                               email_percent=email_percent,
                               zalo_percent=zalo_percent,
                               mess_percent=mess_percent)


@app.route('/get_customers', methods=['GET', 'POST'])
@login_required
def get_customers():
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    page = int(request.form.get('page', 1))
    loc_id = request.form.get('loc_id', 'all')
    from_date = None
    to_date = None
    min_visit = None
    max_visit = None
    gender_list = None
    sort = 'time_asc'
    bday_from_date = None
    bday_to_date = None
    ranks = 'all'
    min_points = ''
    max_points = ''
    min_cash = ''
    max_cash = ''
    lost_day = 0
    employee = ""
    tags_array = []
    customers_filter = session.get('customers_filter', {})
    if customers_filter or len(customers_filter) > 0:
        from_date = customers_filter.get('from_date')
        to_date = customers_filter.get('to_date')
        min_visit = customers_filter.get('min_visit')
        max_visit = customers_filter.get('max_visit')
        lost_day = customers_filter.get('lost_day')
        gender_list = customers_filter.get('gender')
        sort = customers_filter.get('sort')
        bday_from_date = customers_filter.get('bday_from_date')
        bday_to_date = customers_filter.get('bday_to_date')
        tags_array = customers_filter.get('filter_tags')
        employee = customers_filter.get('employee')
    else:

        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        min_visit = request.form.get('min_visit')
        max_visit = request.form.get('max_visit')
        sort = request.form.get('sort', 'time_asc')
        bday_from_date = request.form.get('bday_from_date')
        bday_to_date = request.form.get('bday_to_date')
        gender_list = request.form.getlist('gender')
        lost_day = request.form.get('lost_day', 0)
        filter_tags = request.form.get('real_tags_filter', '')
        employee = request.form.get('employee')
        if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
            tags_array = filter_tags.split(',')
            tags_array = [str(tag) for tag in tags_array]

    gender = []

    if gender_list:
        if 0 < len(gender_list) < 3:
            gender = [str(gen) for gen in gender_list]
            if '0' in gender:
                gender.append('')
                gender.append(None)

    else:
        gender = None

    if not str(lost_day).isdigit():
        lost_day = 0

    session['customers_filter'] = {}
    session['customers_filter']['from_date'] = from_date
    session['customers_filter']['to_date'] = to_date
    session['customers_filter']['min_visit'] = min_visit
    session['customers_filter']['max_visit'] = max_visit
    session['customers_filter']['lost_day'] = lost_day
    session['customers_filter']['sort'] = sort
    session['customers_filter']['employee'] = employee
    session['customers_filter']['bday_from_date'] = bday_from_date
    session['customers_filter']['bday_to_date'] = bday_to_date
    session['customers_filter']['gender'] = gender
    session['customers_filter']['is_zalo'] = None
    session['customers_filter']['filter_tags'] = tags_array
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    status_call = "False"
    app_call = api.get_app_synchronized(type_app="CALL",
                                        merchant_id=merchant_id,
                                        status="True")
    if app_call:
        if app_call.get('status') == "True":
            info_call = app_call.get("setting").get("info")
            if info_call:
                for item in info_call:
                    if str(user_login.get("_id")) == str(
                            item.get("account_id")):
                        status_call = item.get("status_account")

                    if str(merchant_id) == str(user_login.get("_id")):
                        if item.get("role_account") == "3":
                            status_call = item.get("status_account")
                            break
    total = 0
    if loc_id and str(loc_id) != 'all':
        list_cus = api.get_shop_customers(merchant_id,
                                          loc_id,
                                          from_date=from_date,
                                          to_date=to_date,
                                          min_visit=min_visit,
                                          max_visit=max_visit,
                                          lost_day=lost_day,
                                          gender=gender,
                                          sort=sort,
                                          bday_from_date=bday_from_date,
                                          bday_to_date=bday_to_date,
                                          tags_array=tags_array,
                                          employee=employee,
                                          page=page,
                                          page_size=settings.ITEMS_PER_PAGE)
        return render_template("nextify/list_customers.html",
                               customers=list_cus,
                               from_date=from_date,
                               status_call=status_call,
                               to_date=to_date,
                               min_visit=min_visit,
                               max_visit=max_visit,
                               lost_day=lost_day,
                               bday_from_date=bday_from_date,
                               tags=tags,
                               bday_to_date=bday_to_date,
                               gender=gender,
                               sort=sort,
                               shop=shop,
                               shops=shops,
                               page=page,
                               user_login=user_login,
                               total=list_cus.count(),
                               merchant=merchant,
                               employee=employee,
                               filter_tags=tags_array,
                               loc_id=loc_id)

    else:
        list_cus = api.get_merchant_customers(
            merchant_id,
            from_date=from_date,
            to_date=to_date,
            min_visit=min_visit,
            max_visit=max_visit,
            lost_day=lost_day,
            gender=gender,
            employee=employee,
            sort=sort,
            bday_from_date=bday_from_date,
            bday_to_date=bday_to_date,
            tags_array=tags_array,
            page=page,
            page_size=settings.ITEMS_PER_PAGE)
        return render_template("nextify/new_customers_list.html",
                               customers=list_cus,
                               from_date=from_date,
                               status_call=status_call,
                               to_date=to_date,
                               min_visit=min_visit,
                               max_visit=max_visit,
                               lost_day=lost_day,
                               bday_from_date=bday_from_date,
                               employee=employee,
                               bday_to_date=bday_to_date,
                               gender=gender,
                               sort=sort,
                               tags=tags,
                               shop=shop,
                               shops=shops,
                               page=page,
                               user_login=user_login,
                               total=list_cus.count(),
                               merchant=merchant,
                               filter_tags=tags_array,
                               loc_id=loc_id)


@app.route('/search_customers', methods=['POST'])
@login_required
# @cache.cached(timeout=300)
def search_customers():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    text_query = request.form.get('text_query', '')
    if text_query:
        text_query = text_query.strip()
    else:
        return redirect('/customers')
    results = mongo_search.search_customer_by_text(merchant_id, text_query)
    status_vcall = "False"
    app_vcall = api.get_app_synchronized(name_app="vcall",
                                         merchant_id=merchant_id)
    if app_vcall:
        info_vcall = app_vcall.get("setting").get("info")
        if info_vcall:
            for item in info_vcall:
                if str(user_login.get("_id")) == str(item.get("account_id")):
                    status_vcall = item.get("status_account")
                if str(merchant_id) == str(user_login.get("_id")):
                    status_vcall = item.get("status_account") if item.get(
                        "role_account") == "3" else "False"
                    break

    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    pagination = ""
    return render_template('nextify/search_customers_result.html',
                           customers=results,
                           shop=shop,
                           shops=shops,
                           user_login=user_login,
                           total=results.count(),
                           status_vcall=status_vcall,
                           merchant=merchant,
                           pagination=pagination,
                           tags=tags,
                           shop_in_mer=shops)


@app.route("/export_survey/<shop_select>", methods=['POST'])
@login_required
def export_survey(shop_select):
    shop = g.shop
    shop_id = shop.get('_id')
    merchant_id = shop.get('merchant_id')
    producer_data = {
        "shop_id": str(shop_select),
        "task_name": "export_survey",
        "params": {
            "merchant_id": str(merchant_id),
            "shop_id": str(shop_select)
        }
    }
    producer_data = json.dumps(producer_data).encode('utf-8')
    producer.send(settings.cms_consumer, producer_data)
    producer.flush()
    return json.dumps({'result': True})


@app.route("/export_customers", methods=['POST'])
@login_required
def export_hq():
    shop = g.shop
    shop_id = shop.get('_id')
    merchant_id = shop.get('merchant_id')
    try:
        loc_id = request.args.get('loc_id', 'all')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        min_visit = request.form.get('min_visit')
        sort = request.form.get('sort', 'time_asc')
        bday_from_date = request.form.get('bday_from_date')
        bday_to_date = request.form.get('bday_to_date')
        gender_list = request.form.getlist('gender')
        gender = []
        if 0 < len(gender_list) < 3:
            gender = [str(gen) for gen in gender_list]
        else:
            gender = None
        max_visit = request.form.get('max_visit')

        lost_day = request.form.get('lost_day', 0)

        filter_tags = request.form.get('real_tags_filter', '')
        tags_array = []
        if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
            tags_array = filter_tags.split(',')
            tags_array = [str(tag) for tag in tags_array]

        is_ads = request.form.getlist('is_ads')
        is_ads_arr = []
        if len(is_ads) > 0:
            is_ads_arr = [str(gen) for gen in is_ads]
        producer_data = {
            "shop_id": str(loc_id),
            "task_name": "export_customers",
            "params": {
                "merchant_id": str(merchant_id),
                "shop_id": str(loc_id),
                "from_date": str(from_date),
                "to_date": str(to_date),
                "min_visit": min_visit,
                "max_visit": max_visit,
                "sort": sort,
                "bday_from_date": bday_from_date,
                "bday_to_date": bday_to_date,
                "gender": gender,
                "filter_tags": tags_array,
                "lost_day": lost_day,
                "is_ads_arr": is_ads_arr
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        return json.dumps({'result': True})

    except Exception as e:
        print(e)
        return json.dumps({'result': False})


@app.route("/export_customers_fb", methods=['GET'])
@login_required
def export_fb():
    shop = g.shop
    shop_id = g.shop_id
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    min_visit = request.args.get('min_visit')
    max_visit = request.args.get('max_visit')
    bday_from_date = request.args.get('bday_from_date')
    bday_to_date = request.args.get('bday_to_date')
    sort = request.args.get('sort', 'time_asc')
    ranks = request.args.get('ranks', 'all')
    gender = request.args.get('gender', 'all')
    min_points = request.args.get('min_points', '')
    max_points = request.args.get('max_points', '')
    min_cash = request.args.get('min_cash', '')
    max_cash = request.args.get('max_cash', '')
    filter_tags = request.args.get('real_tags_filter', '')
    tags_array = []
    if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
        tags_array = filter_tags.split(',')
        tags_array = [str(tag) for tag in tags_array]
    producer_data = {
        "shop_id": str(shop_id),
        "task_name": "export_fb_task",
        "params": {
            "shop_id": str(shop_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "min_visit": min_visit,
            "max_visit": max_visit,
            "sort": sort,
            "bday_from_date": bday_from_date,
            "bday_to_date": bday_to_date,
            "ranks": ranks,
            "gender": gender,
            "min_cash": min_cash,
            "max_cash": max_cash,
            "min_points": min_points,
            "max_points": max_points,
            "tags_array": tags_array
        }
    }

    producer_data = json.dumps(producer_data).encode('utf-8')
    producer.send(settings.cms_consumer, producer_data)
    producer.flush()

    return json.dumps({'result': True})


@app.route("/export_coupon_manual", methods=['GET'])
@login_required
def export_coupon_manual():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    filter = request.args.get('filter')
    search = request.args.get('search')
    user_phone = request.args.get('user_phone')
    coupon_type_id = request.args.get('coupon_type')
    producer_data = {
        "shop_id": str(shop_id),
        "task_name": "export_coupon_task",
        "params": {
            "merchant_id": str(merchant_id),
            "shop_id": str(shop_id),
            "filter": filter,
            "coupon_type_id": str(coupon_type_id),
            "user_phone": user_phone,
        }
    }

    producer_data = json.dumps(producer_data).encode('utf-8')
    producer.send(settings.cms_consumer, producer_data)
    producer.flush()
    return json.dumps({'result': True})


@app.route('/coupons/redeem', methods=['GET'])
@login_required
def coupons_redeem():
    shop_id = session['shop_id']
    shop = api.get_shop_info(shop_id=shop_id)
    page = int(request.args.get('page', 1))
    user_login = g.user

    coupons = api.get_coupon_redeem_by_shop(shop_id,
                                            page=page,
                                            page_size=settings.ITEMS_PER_PAGE)
    coupons_count = api.total_coupon_redeem_shop(shop_id)

    pagination = Pagination(page=page,
                            total=coupons_count,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template("coupon_redeem.html",
                           shop=shop,
                           coupons=coupons,
                           total=coupons_count,
                           pagination=pagination,
                           user_login=user_login)


@app.route('/ma-giam-gia', methods=['GET'])
@login_required
def ma_giam_gia():
    shop_id = session['shop_id']
    shop = api.get_shop_info(shop_id=shop_id)
    user_login = g.user

    return render_template("ma_giam_gia.html",
                           shop=shop,
                           user_login=user_login)


@app.route('/thu-ngan', methods=['GET'])
def coupons_employee():
    if session.get('is_emps') and session.get('phone_emp'):
        shop_ids = api.get_shop_by_emp(session.get('phone_emp'))
        shops = [api.get_shop_info(i) for i in shop_ids]
        return render_template('shops.html', shops=shops)
    else:
        session['is_emps'] = True
        return redirect('/login')


@app.route('/user/<user_id>', methods=['GET', 'POST'])
@login_required
def user_detail(user_id):
    shop_id = g.shop_id
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    # TODO: Check nếu user đã đến quán thì mới cho shop xem thông tin

    if request.method == 'GET':
        message = session.pop('message', None)
        tags = api.list_tags(merchant_id)
        if user_id == 'add':
            user = {}
            points = 0
            return render_template('nextify/user_detail.html',
                                   user=user,
                                   shop=g.shop,
                                   message=message,
                                   points=points,
                                   user_login=user_login,
                                   tags=tags,
                                   merchant=merchant)
        else:
            user = api.get_user_info(user_id=user_id)
            # user_is_shop = api.get_visit_count(user_id, shop_id, all=True)
            # if user_is_shop == 0:
            #     return redirect('/customers')
            birthday = ''
            if user.get('birthday') and len(user.get(
                    'birthday')) > 0 and user.get('birthday') != 'None':
                birthday_arr = user['birthday'].split('-')
                if len(birthday_arr) == 2:
                    birthday = birthday_arr[1].lstrip("0") + '-' + \
                        birthday_arr[0].lstrip("0")

            last_visit = api.get_last_visit(user_id, shop_id)
            last_visit_str = arrow.get(last_visit).humanize(locale='vi_vn')
            visit_count = api.get_user_activity_visit_count(user_id, shops)
            isHQ = True if merchant_id and merchant_id != '0' else False

            logs_data_visit = []
            logs_data_visit = api.user_logs_count_by_hour(user_id, shop_id)

            user_tags = api.get_user_tags(merchant_id, user_id)
            source_tags = []
            user_tags_details = []
            if user_tags:
                user_tag = user_tags.get('tags')
                if len(user_tags) > 0:
                    for tag in user_tag:
                        tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                        if tag_db:
                            source_tags.append(str(tag))
                            user_tags_details.append(tag_db['name'])
            is_zalo_follow = api.get_user_zalo_oa(user_id, shop_id)
            zalo = True if is_zalo_follow else False
            user['zalo'] = zalo
            return render_template('nextify/user_detail.html',
                                   user=user,
                                   shop=g.shop,
                                   message=message,
                                   last_visit=last_visit,
                                   last_visit_str=last_visit_str,
                                   user_login=user_login,
                                   visit_count=visit_count,
                                   birthday=birthday,
                                   logs_data_visit=logs_data_visit,
                                   tags=tags,
                                   user_tags=user_tags,
                                   source_tags=source_tags,
                                   user_tags_details=user_tags_details,
                                   merchant=merchant)


@app.route('/user/<user_id>/unsubscribe', methods=['GET'])
@login_required
def unsubscribe_user(user_id):
    # shop_id = g.shop_id
    shop = g.shop
    # user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id_select = request.args.get('loc_id')
    if shop_id_select and shop_id_select != 'None':
        api.remove_customers_location_visit(shop_id_select, user_id)
    else:
        api.remove_customers_visit(merchant_id, user_id)
    return json.dumps({'result': True})


@app.route('/user/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    shop_id = g.shop_id
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    # TODO: Check nếu user đã đến quán thì mới cho shop xem thông tin
    act_type = ''
    if request.method == 'GET':
        message = session.pop('message', None)
        tags = api.list_tags(merchant_id)
        source_tags = []
        user_tags_details = []
        user_tags = None
        if user_id == 'add':
            user = {}
        else:
            user = api.get_user_info(user_id=user_id)
            user_tags = api.get_user_tags(merchant_id, user_id)
            if user_tags:
                user_tag = user_tags.get('tags')
                if len(user_tags) > 0:
                    for tag in user_tag:
                        tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                        if tag_db:
                            source_tags.append(str(tag))
                            user_tags_details.append(tag_db['name'])

        return render_template('nextify/user_add.html',
                               user_id=user_id,
                               user=user,
                               shop=g.shop,
                               message=message,
                               user_login=user_login,
                               tags=tags,
                               user_tags=user_tags,
                               source_tags=source_tags,
                               merchant=merchant)
    else:
        name = request.form.get('name')
        location_id = request.form.get('location_id')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        birthday = request.form.get('birthday')
        email = request.form.get('email')
        birth = ''
        if birthday and len(birthday) > 0:
            try:
                birthday = birthday.split('-')
                birth = '{}-{}'.format(birthday[1].lstrip("0"),
                                       birthday[0].lstrip("0"))
            except:
                pass
        tags = request.form.get('real_tags_filter')
        year = request.form.get('year_birth')
        company = request.form.get('company')
        company_role = request.form.get('company_role')
        is_employee = request.form.get('is_employee')
        is_employee = "True" if str(is_employee) == "true" else "False"
        tags_array = []
        if tags and len(tags) > 0:
            tags_split = tags.split(',')
            if len(tags_split) > 0:
                for tag in tags_split:
                    tag = tag.strip()
                    if len(tag) > 0:
                        tags_array.append(ObjectId(tag))
        error = ''
        if phone and len(phone) > 0:
            if not api.get_phone_number(phone) or not \
                    all([x.isdigit() for x in phone]):
                error = gettext("So_dien_thoai_chua_dung_dinh_dang")
                return json.dumps({'error': error})
        if email and len(email) > 0:
            is_valid = validate_email(email)
            if not is_valid:
                error = gettext("Email_chua_dung_dinh_dang")
                return json.dumps({'error': error})
        # if not phone and not email:
        #     error = 'Email hoặc số điện thoại không được để trống'
        #     return json.dumps({'error': error})
        # if not birthday or len(birthday) == 0:
        #     error = 'Ngày sinh không được để trống'
        #     return json.dumps({'error': error})

        note = request.form.get('note', '')
        address = request.form.get('address', '')
        facebook = request.form.get('facebook', '')
        twitter = request.form.get('twitter', '')
        if user_id == 'add':
            user_id = None
            if phone and len(phone) > 0 and str(phone) != 'None':
                phone = str(phone).lower()
                phone = phone.replace('+84', '0')
                phone = api.get_phone_number(phone)
                if phone:
                    user_by_phone = handle_customers.get_user_merchant_by_phone(
                        merchant_id, phone)
                    if user_by_phone:
                        user_id = user_by_phone.get('user_id')
            elif email and len(email) > 0 and str(email) != 'None':
                email = email.lower()
                user_by_email = handle_customers.get_user_merchant_by_email(
                    merchant_id, email)
                if user_by_email:
                    user_id = user_by_email.get('user_id')
            if user_id:
                user = api.get_user_info(user_id=user_id)
                if user:
                    api.update_user_item(user_id,
                                         name=name,
                                         phone=phone,
                                         gender=gender,
                                         birthday=birth,
                                         email=email,
                                         year_birthday=year,
                                         note=note,
                                         address=address,
                                         facebook=facebook,
                                         twitter=twitter,
                                         company=company,
                                         company_role=company_role,
                                         is_employee=is_employee)
                else:
                    user_id = api.register(name=name,
                                           phone=phone,
                                           gender=gender,
                                           birthday=birth,
                                           email=email,
                                           year_birthday=year,
                                           note=note,
                                           address=address,
                                           facebook=facebook,
                                           twitter=twitter,
                                           company=company,
                                           company_role=company_role,
                                           is_employee=is_employee)
            else:
                user_id = api.register(name=name,
                                       phone=phone,
                                       gender=gender,
                                       birthday=birth,
                                       email=email,
                                       year_birthday=year,
                                       note=note,
                                       address=address,
                                       facebook=facebook,
                                       twitter=twitter,
                                       company=company,
                                       company_role=company_role,
                                       is_employee=is_employee)

            check_tag = api.check_tag_name('export', merchant_id)
            if not check_tag:
                check_tag = api.create_tags(merchant_id,
                                            'export',
                                            'export',
                                            tag_id=None,
                                            shop_id=location_id)
            tags_array.append(check_tag)
            api.create_user_tags_update(merchant_id, user_id, tags_array)
            visit_id = api.save_visit_log(user_id, location_id)
            if visit_id:
                save_customers.handle_customer_update(visit_id)

            else:
                save_customers.update_customers(merchant_id,
                                                location_id,
                                                user_id,
                                                last_visit=time.time())
            shop_select = api.get_shop_info(shop_id=location_id)
            zalo_access_token = shop_select.get('zalo_access_token')
            zalo_oa_id = shop_select.get('zalo_oa_id')
            zalo_app_id = shop_select.get('zalo_app_id')
            if zalo_access_token and len(zalo_access_token) > 0 and zalo_oa_id \
                    and len(zalo_oa_id) > 0 and zalo_app_id and len(zalo_app_id) > 0:
                producer_data = {
                    "shop_id": str(location_id),
                    "task_name": "update_user_zalo",
                    "params": {
                        "merchant_id": str(merchant_id),
                        "shop_id": str(location_id),
                        "zalo_access_token": zalo_access_token,
                        "user_id": str(user_id)
                    }
                }

                producer_data = json.dumps(producer_data).encode('utf-8')
                producer.send(settings.cms_consumer, producer_data)
                producer.flush()
        else:
            user = handle_customers.get_user_merchant_by_user_id(
                merchant_id, user_id)
            loc_id = request.args.get('loc_id')
            if user:
                user_id = user.get('user_id')
                api.update_user_by_id(user_id,
                                      name=name,
                                      phone=phone,
                                      email=email,
                                      gender=gender,
                                      birthday=birth,
                                      year_birthday=year,
                                      note=note,
                                      address=address,
                                      facebook=facebook,
                                      twitter=twitter,
                                      company=company,
                                      company_role=company_role,
                                      is_employee=is_employee)
                api.create_user_tags_update(merchant_id, user_id, tags_array)
                save_customers.update_customers_merchant(merchant_id,
                                                         user_id,
                                                         last_visit=None)
                if loc_id and str(loc_id) != 'all':
                    save_customers.update_customers_location(merchant_id,
                                                             loc_id,
                                                             user_id,
                                                             last_visit=None)
                save_customers.update_customers(merchant_id,
                                                loc_id,
                                                user_id,
                                                last_visit=time.time())
                # producer_data = {
                #     "shop_id": str(loc_id),
                #     "task_name": "update_customers_all_locations",
                #     "params": {"merchant_id": str(merchant_id),
                #                "user_id": str(user_id)
                #                }
                # }

                # producer_data = json.dumps(producer_data)
                # producer.send(settings.cms_consumer, producer_data)
                # producer.flush()

                _is_employee = True if is_employee == "True" else False
                # producer_data = {
                #     "shop_id": str(loc_id),
                #     "task_name": "update_employee",
                #     "params": {"merchant_id": str(merchant_id),
                #                "user_id": str(user_id),
                #                "shop_id": str(loc_id),
                #                "is_employee": is_employee}
                # }

                # producer_data = json.dumps(producer_data)
                # producer.send(settings.cms_consumer, producer_data)
                # producer.flush()
        return json.dumps({'result': True})


@app.route('/user/<user_id>/coupons', methods=['GET'])
@login_required
def user_coupons(user_id):
    shop_id = g.shop_id
    shop = g.shop
    user_login = g.user
    user = api.get_user_info(user_id=user_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    merchant_id = shop.get('merchant_id')
    page = int(request.args.get('page', 1))
    coupons = gift_card_api.get_coupon_manual_by_user(
        merchant_id=merchant_id,
        shop_id=shop_id,
        user_id=user_id,
        page=page,
        page_size=settings.ITEMS_PER_PAGE)
    total_coupon_manual = gift_card_api.total_coupon_manual_by_user(
        merchant_id=merchant_id, shop_id=shop_id, user_id=user_id)
    pagination = Pagination(page=page,
                            total=total_coupon_manual,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/user_coupons.html',
                           coupons=coupons,
                           pagination=pagination,
                           shop=shop,
                           shop_id=shop_id,
                           user_login=user_login,
                           user=user,
                           page=page)


@app.route('/user/modal/<phone>', methods=['GET'])
@login_required
def user_modal(phone):
    shop_id = g.shop_id
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    # TODO: Check nếu user đã đến quán thì mới cho shop xem thông tin

    if request.method == 'GET':
        tags = api.list_tags(merchant_id)
        message = session.pop('message', None)
        user = api.get_user_info(phone_number=phone)
        user_id = user.get('_id')
        # user_is_shop = api.get_visit_count(user_id, shop_id, all=True)
        # if user_is_shop == 0:
        #     return redirect('/customers')
        birthday = ''
        if user.get('birthday') and len(
                user.get('birthday')) > 0 and user.get('birthday') != 'None':
            birthday_arr = user['birthday'].split('-')
            if len(birthday_arr) == 2:
                birthday = birthday_arr[1].lstrip("0") + '-' + \
                    birthday_arr[0].lstrip("0")

        last_visit = api.get_last_visit(user_id, shop_id)
        last_visit_str = arrow.get(last_visit).humanize(locale='vi_vn')
        visit_count = api.get_visit_phone(user['phone'], shop_id)
        coupon_codes = api.get_coupon_codes(user_id, shop_id)

        logs_data_visit = []
        logs_data_visit = api.user_logs_count_by_hour(user_id, shop_id)
        user_tags = api.get_user_tags(merchant_id, user_id)
        user_tags_details = []
        if user_tags:
            user_tag = user_tags.get('tags')
            if len(user_tags) > 0:
                for tag in user_tag:
                    tag_db = api.get_tag_by_tag_id(merchant_id, tag)
                    if tag_db:
                        user_tags_details.append(tag_db)
        return render_template('user_modal.html',
                               user=user,
                               shop=g.shop,
                               message=message,
                               last_visit=last_visit,
                               last_visit_str=last_visit_str,
                               coupon_codes=coupon_codes,
                               user_login=user_login,
                               visit_count=visit_count,
                               birthday=birthday,
                               logs_data_visit=logs_data_visit,
                               tags=tags,
                               user_tags=user_tags,
                               user_tags_details=user_tags_details)


@app.route('/<merchant_id>/customers/<cus_id>', methods=['GET'])
@login_required
def customer_info(merchant_id, cus_id):
    user = handle_customers.get_user_merchant_by_user_id(merchant_id, cus_id)
    return render_template('nextify/user_info.html',
                           merchant_id=merchant_id,
                           user=user,
                           cus_id=cus_id)


@app.route('/<merchant_id>/customers/<cus_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user_info(merchant_id, cus_id):
    user = handle_customers.get_user_merchant_by_user_id(merchant_id, cus_id)
    return render_template('nextify/update_user_info.html',
                           merchant_id=merchant_id,
                           cus=user,
                           cus_id=cus_id)


@app.route('/<merchant_id>/tags/search', methods=['GET', 'POST'])
@login_required
def get_tags_for_select(merchant_id):
    _search = request.args.get('search')
    tags = api.list_tags_by_regex(merchant_id, _search)
    resutls = []
    for tag in tags:
        item = {}
        item['_id'] = str(tag.get('_id'))
        item['name'] = tag.get('name')
        resutls.append(item)
    return jsonify(resutls)


@app.route('/<merchant_id>/visit_log/<cus_id>', methods=['GET'])
@login_required
def user_visit_info(merchant_id, cus_id):
    shops = []
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    page = 1
    visit_count = api.get_user_activity_visit_count(cus_id, shops)
    total_pages = (visit_count // 5) + \
        1 if visit_count % 5 != 0 else visit_count / 5
    log_visit = api.get_user_activity_visit(cus_id,
                                            shops,
                                            page=page,
                                            page_size=5)
    pagination = Pagination(page=page,
                            total=visit_count,
                            per_page=5,
                            css_framework='bootstrap3')
    user = handle_customers.get_user_merchant_by_user_id(merchant_id, cus_id)
    return render_template('nextify/visit_info.html',
                           merchant_id=merchant_id,
                           total_pages=total_pages,
                           log_visit=log_visit,
                           pagination=pagination,
                           cus_id=cus_id,
                           user=user)


@app.route('/<merchant_id>/visit_log/<cus_id>/<page>', methods=['GET'])
@login_required
def user_visit_info_page(merchant_id, cus_id, page):
    shops = []
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    page = int(page)

    log_visit = api.get_user_activity_visit(cus_id,
                                            shops,
                                            page=page,
                                            page_size=5)

    return render_template('nextify/visit_info_paging.html',
                           log_visit=log_visit)


@app.route('/customer_details', methods=['GET', 'POST'])
@login_required
def customer_details():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if request.method == 'GET':
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        cus_id = request.args.get('cus_id')
        shop_id_select = request.args.get('shop_id', 'all')
        if not shop_id_select or str(shop_id_select) == 'None':
            shop_id_select = 'all'
        shops = []
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer['_id'])
        page = int(request.args.get('page', 1))
        cus = None
        if shop_id_select == 'all':
            cus = api.get_cus_by_id(cus_id, merchant_id=merchant_id)
        else:
            cus = api.get_cus_loc_by_id(cus_id)
        user_id = cus.get('user_id')
        user = cus.get('user', {})

        visit_count = api.get_user_activity_visit_count(user_id, shops)
        total_pages = (visit_count // 5) + \
            1 if visit_count % 5 != 0 else visit_count / 5
        log_visit = api.get_user_activity_visit(user_id,
                                                shops,
                                                page=page,
                                                page_size=5)
        status_call = "False"

        total_amount_spent = api.get_total_amount_spent(merchant_id, user_id)
        total_order = api.get_total_order_customer(merchant_id, user_id)
        last_purchase = api.get_last_purchase(merchant_id, user_id)
        total_pages_orders = (total_order // 5) + \
            1 if total_order % 5 != 0 else total_order / 5
        orders = api.get_orders_customer(merchant_id,
                                         user_id,
                                         page=page,
                                         page_size=5)
        return render_template('nextify/user_activity.html',
                               logs=log_visit,
                               shop=shop,
                               shop_id_select=shop_id_select,
                               shop_id=shop_id,
                               visit_count=visit_count,
                               tags=tags,
                               user_login=user_login,
                               total_pages=total_pages,
                               total_pages_orders=total_pages_orders,
                               merchant=merchant,
                               cus=cus,
                               status_call=status_call,
                               user_id=user_id,
                               total_amount_spent=total_amount_spent,
                               total_order=total_order,
                               last_purchase=last_purchase,
                               orders=orders,
                               page=page)
    else:
        page = int(request.form.get('page', 1))
        user_id = request.form.get('user_id')
        type_page = request.form.get('type')
        user = api.get_user_info(user_id=user_id)
        merchant_id = shop.get('merchant_id')
        shops = []
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer['_id'])
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        visit_count = api.get_user_activity_visit_count(user_id, shops)
        total_pages = (visit_count // 5) + \
            1 if visit_count % 5 != 0 else visit_count / 5
        log_visit = api.get_user_activity_visit(user_id,
                                                shops,
                                                page=page,
                                                page_size=5)
        # get order info
        total_amount_spent = api.get_total_amount_spent(merchant_id, user_id)
        total_order = api.get_total_order_customer(merchant_id, user_id)
        total_pages_orders = (total_order // 5) + \
            1 if total_order % 5 != 0 else total_order / 5
        last_purchase = api.get_last_purchase(merchant_id, user_id)
        orders = api.get_orders_customer(merchant_id,
                                         user_id,
                                         page=page,
                                         page_size=5)
        if type_page == "user_activity":
            return render_template('nextify/activity.html',
                                   logs=log_visit,
                                   total_pages=total_pages,
                                   shop=shop,
                                   user_login=user_login,
                                   total_amount_spent=total_amount_spent,
                                   total_order=total_order,
                                   last_purchase=last_purchase,
                                   orders=orders,
                                   total_pages_orders=total_pages_orders,
                                   page=page)
        else:
            return render_template('nextify/orders_detail.html',
                                   logs=log_visit,
                                   total_pages=total_pages,
                                   shop=shop,
                                   user_login=user_login,
                                   total_amount_spent=total_amount_spent,
                                   total_order=total_order,
                                   last_purchase=last_purchase,
                                   orders=orders,
                                   total_pages_orders=total_pages_orders,
                                   page=page)


@app.route('/user/<phone>/credit', methods=['GET'])
@login_required
def user_log_credit(phone):
    shop_id = g.shop_id
    shop = g.shop
    user_login = g.user
    user = api.get_user_info(phone_number=phone)
    user_id = user['_id']
    merchant_id = shop.get('merchant_id')
    page = int(request.args.get('page', 1))
    visit_count = api.total_list_history_trans_by_user(merchant_id, user_id)
    history_trans = api.list_history_trans_by_user(
        merchant_id, user_id, page=page, page_size=settings.ITEMS_PER_PAGE)
    total_page = math.ceil(float(visit_count) / float(settings.ITEMS_PER_PAGE))
    pagination = Pagination(page=page,
                            total=visit_count,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('user_log_credit.html',
                           history_trans=history_trans,
                           pagination=pagination,
                           shop=shop,
                           shop_id=shop_id,
                           user_login=user_login,
                           user=user,
                           page=page,
                           total_page=total_page)


@app.route('/<shop_id>/user/<user_id>/redeem/<code>', methods=['GET'])
def user_redeem_coupon(shop_id, user_id, code):
    user = api.get_user_info(user_id=user_id)
    shop = api.get_shop_info(shop_id=shop_id)
    phone_emp = None
    if session.get('is_emps') and session.get('phone_emp'):
        phone_emp = session.get('phone_emp')
    else:
        phone_emp = shop.get('phone')
    coupon = api.redeem_coupon(user_id, shop_id, code, phone_emp)
    if coupon:
        message = '✓ ' + \
                  gettext("Doi_coupon_thanh_cong_cho_khach_hang") + \
                  '%s' % user['phone']
    else:
        message = gettext(
            "Coupon_khong_doi_duoc_hien_tai,_vui_long_thu_lai_sau")
    session['message'] = message
    return redirect('/coupons')


@app.route('/events', methods=['GET'])
@login_required
def events():
    shop_id = g.shop_id
    user = g.user
    events = api.get_events(shop_id)
    return render_template('events.html', shop=g.shop, events=events)


@app.route('/events/<event_id>', methods=['GET', 'POST'])
@login_required
def new_event(event_id):
    shop = g.shop
    shop_id = g.shop_id
    user = g.user
    if request.method == 'POST':
        name = request.form.get('name')
        active = request.form.get('active')
        if not active:
            active = "0"
        title = request.form.get('title')
        content = request.form.get('content')
        slug = ''
        if title:
            slug = slugify(title)
        link_share = request.form.get('link_share')
        social = request.form.get('social')

        photo = None
        if request.files.get('photo') and \
                request.files.get('photo').filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            file_data = request.files.get('photo').stream.read()
            photo = \
                hashlib.md5(file_data).hexdigest() + '.' + \
                request.files.get('photo').filename.rsplit('.', 1)[1]
            data_logo = {
                'file_name': photo,
                'file_data': base64.b64encode(file_data),
                'origin_name': request.files.get('photo').filename
            }
            storage_api.save_file(data_logo)
        if event_id == 'add':
            event_id = api.add_event(shop_id, title, content, photo, slug,
                                     active, name, link_share, social)
            api.deactive_other_event(shop_id, event_id, active)
        else:
            api.update_event(shop_id, event_id, title, content, photo, slug,
                             active, name, link_share, social)
            api.deactive_other_event(shop_id, event_id, active)

        return redirect('/events')
    else:

        if event_id == 'add':
            event = {}
        elif event_id == 'remove':
            pass
        else:
            event = api.get_event(shop_id, event_id)
        return render_template('event.html', shop=shop, event=event)


@app.route('/events/preview/<event_id>', methods=['GET', 'POST'])
@login_required
def preview_event(event_id):
    shop = g.shop
    shop_id = g.shop_id
    user = g.user
    if event_id == 'new':
        event_preview = {}
    else:
        event_preview = api.get_event(shop_id, event_id)
    return render_template("nextify/event_preview.html",
                           shop=shop,
                           event=event_preview)


@app.route('/events/<event_id>/<status>', methods=['GET'])
@login_required
def change_event_status(event_id, status):
    api.change_event_status(g.shop_id, event_id, str(status))
    api.deactive_other_event(g.shop_id, event_id, str(status))
    return redirect('/events')


@app.route('/splash_page/<page_id>/cards', methods=['GET'])
@login_required
def cards(page_id):
    shop_id = g.shop_id
    user_login = g.user
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    mar_filter = request.args.get('filter')
    if not mar_filter:
        mar_filter = 'default'
    cards = api.get_cards(shop_id, mar_filter)
    return render_template('nextify/cards.html',
                           shop=g.shop,
                           cards=cards,
                           mar_filter=mar_filter,
                           user_login=user_login,
                           merchant=merchant,
                           page_id=page_id)


@app.route("/splash_page_tags/remove/<tag_id>", methods=['POST'])
@login_required
def remove_tag(tag_id):
    a = api.remove_tag_for_gr_user(tag_id)
    return json.dumps({"result": True})


@app.route('/splash_page_tags/<shop_id>', methods=['POST'])
@login_required
def new_customers_tag_hotspot(shop_id):
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    tag_type = request.form.get('options')
    tag_id = request.form.get("tag_name")
    settings = {}
    if tag_type == 'by_visit':
        type_visit = request.form.get('visits_by')
        min_visit = request.form.get('min_visit')
        max_visit = request.form.get('max_visit')
        if int(max_visit) < int(min_visit):
            return json.dumps({"error": gettext("Luot_den_nhap_sai")})
        settings = {
            'type_visit': type_visit,
            'min_visit': min_visit,
            'max_visit': max_visit,
        }
    elif tag_type == 'by_datetime':
        array_date = request.form.get('dates')
        all_hours = request.form.get('all_hours')
        min_hour_in_date = request.form.get('min_hour_in_date')
        max_hour_in_date = request.form.get('max_hour_in_date')

        weekday_sun = request.form.get('weekday_sun')
        weekday_mon = request.form.get('weekday_mon')
        weekday_tue = request.form.get('weekday_tue')
        weekday_wed = request.form.get('weekday_wed')
        weekday_thu = request.form.get('weekday_thu')
        weekday_fri = request.form.get('weekday_fri')
        weekday_sat = request.form.get('weekday_sat')

        is_date_correct = False
        if all_hours != "on":
            try:
                # hour_from = datetime.strptime(hour_from, "%H:%M")
                # hour_to = datetime.strptime(hour_to, "%H:%M")
                if min_hour_in_date < max_hour_in_date:
                    is_date_correct = True
                else:
                    is_date_correct = False
            except Exception as e:
                is_date_correct = False
            if not is_date_correct:
                error = gettext("Gio_ket_thuc_phai_lon_hon_gio_bat_dau")
                return json.dumps({'error': error})

        settings = {
            'array_date': array_date,
            'weekday_sun': weekday_sun,
            'weekday_mon': weekday_mon,
            'weekday_tue': weekday_tue,
            'weekday_wed': weekday_wed,
            'weekday_thu': weekday_thu,
            'weekday_fri': weekday_fri,
            'weekday_sat': weekday_sat,
            'all_hours': all_hours,
            'min_hour_in_date': min_hour_in_date,
            'max_hour_in_date': max_hour_in_date
        }
    elif tag_type == 'by_event':
        min_date = request.form.get('date_from')
        max_date = request.form.get('date_to')
        min_hour = request.form.get('min_hour')
        max_hour = request.form.get('max_hour')
        if max_hour and min_hour:
            is_date_correct = True
            try:
                # hour_from = datetime.strptime(hour_from, "%H:%M")
                # hour_to = datetime.strptime(hour_to, "%H:%M")
                if min_hour > max_hour:
                    is_date_correct = False
                else:
                    is_date_correct = True
            except Exception as e:
                is_date_correct = False
            if not is_date_correct:
                error = gettext("Gio_ket_thuc_phai_lon_hon_gio_bat_dau")
                return json.dumps({'error': error})
        is_date_correct = True
        if min_date and max_date:
            try:
                min_date_obj = datetime.strptime(min_date, "%d-%m-%Y")
                max_date_obj = datetime.strptime(max_date, "%d-%m-%Y")

                if min_date_obj > max_date_obj:
                    is_date_correct = False
            except:
                is_date_correct = False
            if not is_date_correct:
                error = gettext("Ngay_ket_thuc_phai_lon_hon_ngay_bat_dau")
                return json.dumps({'error': error})
            settings = {
                'min_date': min_date,
                'max_date': max_date,
                'min_hour': min_hour,
                'max_hour': max_hour
            }
        else:
            return json.dumps(
                {"error": gettext("Khoang_ngay_khong_duoc_bo_trong!")})
    check_tag = api.get_splash_page_tag(tag_id, shop_id)
    if check_tag:
        tag_name = api.get_tag_name_by_tag_id(tag_id).get('name')
        api.update_splash_page_tags(tag_id=tag_id,
                                    tag_name=tag_name,
                                    shop_id=shop_id,
                                    settings=settings,
                                    tag_type=tag_type)
    else:
        tag_name = api.get_tag_name_by_tag_id(tag_id).get('name')
        api.save_splash_page_tags(merchant_id=merchant_id,
                                  tag_name=tag_name,
                                  tag_id=tag_id,
                                  shop_id=shop_id,
                                  tag_type=tag_type,
                                  settings=settings)

    return json.dumps({'result': True})


@app.route('/remove_cards/<card_id>', methods=['GET'])
@login_required
def remove_cards(card_id):
    shop_id = api.get_card_new_portal_by_card(card_id)
    api.remove_card_new_portal(card_id)
    return redirect('/new_portal/{}'.format(shop_id))


@app.route('/splash_page/<shop_id_select>/weekday/<page_id>', methods=['POST'])
@login_required
def save_splash_weekday(shop_id_select, page_id):
    shop_id_select = str(shop_id_select)
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    shop_select = api.get_shop_info(shop_id=shop_id_select)

    title = request.form.get('title')
    content = request.form.get('content')
    type_page = request.form.get('auto_mar')
    week_id = request.form.get('week_id')
    weekday = ''
    list_week_day = [
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
        'sunday'
    ]
    if week_id:
        weekday = list_week_day[int(week_id)]
        week_id = int(week_id)
    active = request.form.get('active')
    active = True if active and str(active) != 'false' else False
    auto_popup = request.form.get('auto_popup')
    # hotspot_method = request.form.get('hotspot_method', 'default')
    # default_code = request.form.get('default_code', '')
    # default_code = default_code.strip()
    # default_code = default_code.lower()

    connect_button = request.form.get('connect_button', '')

    photo = request.files.get('photo')
    photo_name = None
    if photo and \
            photo.filename.rsplit('.', 1)[1].lower() \
            in ALLOWED_EXTENSIONS:
        file_data = photo.stream.read()
        photo_name = \
            hashlib.md5(file_data).hexdigest() + '.' + \
            request.files.get('photo').filename.rsplit('.', 1)[1]
        data_logo = {
            'file_name': photo_name,
            'file_data': base64.b64encode(file_data),
            'origin_name': photo.filename
        }
        storage_api.save_file(data_logo)
    if page_id == 'add':
        try:
            new_page_id = api.new_splash_page_weekday(
                shop_id_select,
                type_page,
                active,
                week_id,
                weekday,
                title=title,
                content=content,
                photo=photo_name,
                connect_button=connect_button,
                auto_popup=auto_popup)

            return json.dumps({"result": 'OK'})
        except Exception as e:
            print(e)
            return json.dumps(
                {'error': gettext("Co_loi_xay_ra,_xin_thu_lai_sau")})
    else:
        try:
            api.update_splash_page_weekday(shop_id_select,
                                           page_id,
                                           type_page,
                                           active,
                                           week_id,
                                           weekday,
                                           title=title,
                                           content=content,
                                           photo=photo_name,
                                           connect_button=connect_button,
                                           auto_popup=auto_popup)

            return json.dumps({"result": 'OK'})
        except Exception as e:
            print(e)
            return json.dumps(
                {'error': gettext("Co_loi_xay_ra,_xin_thu_lai_sau!")})


@app.route('/rating', methods=['GET'])
@login_required
def rating_view():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    if len(shops) > 0:
        shop_id_select = shops[0]['_id']
        return redirect('/rating/%s' % (shop_id_select))
    else:
        return redirect(url_for('setup_first_login'))


@app.route('/rating/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def rating_location(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    source = request.args.get('source', 'all')
    star = request.args.get('star', None)
    page = int(request.args.get('page', 1))
    shop_select = api.get_shop_info(shop_id_select)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    # shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    survey_result = api.get_comment(merchant_id=merchant_id,
                                    shop_id=shop_id_select,
                                    source=source,
                                    page=page,
                                    page_size=settings.ITEMS_PER_PAGE,
                                    star=star)
    total = api.get_total_rating(merchant_id=merchant_id,
                                 shop_id=shop_id_select,
                                 source=source,
                                 star=star)
    sum_rating = api.sum_rating(merchant_id=merchant_id,
                                shop_id=shop_id_select,
                                source=source,
                                star=star)
    avg_rating = round(float(sum_rating) / total, 1) if total != 0 else 0
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template('nextify/rating_location.html',
                           source=source,
                           star=star,
                           user_login=user_login,
                           merchant=merchant,
                           shop_id=shop_id,
                           total_rating=total,
                           avg_rating=avg_rating,
                           shop_id_select=shop_id_select,
                           survey_result=survey_result,
                           pagination=pagination,
                           shop_select=shop_select,
                           page=page,
                           shop_in_mer=shops)


@app.route('/marketing_automation', methods=['GET'])
@login_required
def marketing_automation_locations():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    shop_id_select = request.args.get('shop_id_select')
    if shop_id_select and len(shop_id_select) > 0:
        return redirect('/marketing_automation/%s' % (shop_id_select))
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    if len(shops) > 0:
        shop_id_select = shops[0]['_id']
        return redirect('/marketing_automation/%s' % (shop_id_select))

    return render_template('nextify/wifi_locations.html',
                           merchant=merchant,
                           locations=shops)


@app.route('/black_list_keywords', methods=['GET'])
@login_required
def black_list_keywords():
    list_black_key = [
        'CTKM', 'Communist', 'Dang VN', 'Dang cong san', 'SUCK', 'Tinh duc',
        'alcohol', 'bieu tinh', 'call boy', 'call girl', 'chan dai',
        'chong My', 'chong Trung Quoc', 'cigarette', 'demonstrate',
        'demonstration', 'dit cha', 'dit con me', 'dit me', 'fuck', 'gai goi',
        'game online', 'hotgirl', 'khuyen mai', 'lo de', 'long leg',
        'postitude', 'quang cao', 'ruou', 'sex', 'soi cau', 'soicau', 'suck',
        'thuoc la', 'tobbaco', 'trai bao', 'ty le ca cuoc', 'giam gia',
        'uu dai', 'chiet khau', 'trung thuong', 'rut tham', 'sale', 'free',
        'co hoi nhan', 'mien phi', 'Qua tang', 'C/K x %', 'chiet khau x %'
    ]
    list_black_key.sort()
    return render_template('nextify/black_keywords.html',
                           list_black_key=list_black_key)


@app.route('/marketing_automation/<shop_id_select>', methods=['GET'])
@login_required
def marketing_automation_shop(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if 'sms' not in merchant:
        merchant['sms'] = {}

    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/marketing_automation')
    if 'email_template' not in shop_select:
        shop_select['email_template'] = {}
    if 'sms' not in shop_select:
        shop_select['sms'] = {}
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop_id_select, all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]

    welcome_sms_count = api.total_automation_by_type(shop_id_select, 'sms',
                                                     'welcome')
    return_sms_count = api.total_automation_by_type(shop_id_select, 'sms',
                                                    'return')
    loyal_sms_count = api.total_automation_by_type(shop_id_select, 'sms',
                                                   'loyal')
    lost_sms_count = api.total_automation_by_type(shop_id_select, 'sms',
                                                  'lost')
    birthday_sms_count = api.total_automation_by_type(shop_id_select, 'sms',
                                                      'happy_birthday')
    anoun_sms_count = api.total_automation_by_type(shop_id_select, 'sms',
                                                   'anoun')
    thank_you_sms_count = api.total_automation_by_type(shop_id_select, 'sms',
                                                       'thank_you')

    welcome_email_count = api.total_automation_by_type(shop_id_select, 'email',
                                                       'welcome')
    return_email_count = api.total_automation_by_type(shop_id_select, 'email',
                                                      'return')
    loyal_email_count = api.total_automation_by_type(shop_id_select, 'email',
                                                     'loyal')
    lost_email_count = api.total_automation_by_type(shop_id_select, 'email',
                                                    'lost')
    birthday_email_count = api.total_automation_by_type(
        shop_id_select, 'email', 'happy_birthday')
    anoun_email_count = api.total_automation_by_type(shop_id_select, 'email',
                                                     'anoun')
    thank_you_email_count = api.total_automation_by_type(
        shop_id_select, 'email', 'thank_you')

    welcome_zalo_count = api.total_automation_by_type(shop_id_select, 'zalo',
                                                      'welcome')
    return_zalo_count = api.total_automation_by_type(shop_id_select, 'zalo',
                                                     'return')
    loyal_zalo_count = api.total_automation_by_type(shop_id_select, 'zalo',
                                                    'loyal')
    lost_zalo_count = api.total_automation_by_type(shop_id_select, 'zalo',
                                                   'lost')
    birthday_zalo_count = api.total_automation_by_type(shop_id_select, 'zalo',
                                                       'happy_birthday')
    anoun_zalo_count = api.total_automation_by_type(shop_id_select, 'zalo',
                                                    'anoun')
    thank_you_zalo_count = api.total_automation_by_type(
        shop_id_select, 'zalo', 'thank_you')

    welcome_facebook_count = api.total_automation_by_type(
        shop_id_select, 'chatbot', 'welcome')
    return_facebook_count = api.total_automation_by_type(
        shop_id_select, 'chatbot', 'return')
    loyal_facebook_count = api.total_automation_by_type(
        shop_id_select, 'chatbot', 'loyal')
    lost_facebook_count = api.total_automation_by_type(shop_id_select,
                                                       'chatbot', 'lost')
    birthday_facebook_count = api.total_automation_by_type(
        shop_id_select, 'chatbot', 'happy_birthday')
    anoun_facebook_count = api.total_automation_by_type(
        shop_id_select, 'chatbot', 'anoun')
    thank_you_facebook_count = api.total_automation_by_type(
        shop_id_select, 'chatbot', 'thank_you')

    welcome_zalo_zns_count = api.total_automation_by_type(
        shop_id_select, 'zalo_zns', 'welcome')
    return_zalo_zns_count = api.total_automation_by_type(
        shop_id_select, 'zalo_zns', 'return')
    loyal_zalo_zns_count = api.total_automation_by_type(
        shop_id_select, 'zalo_zns', 'loyal')
    lost_zalo_zns_count = api.total_automation_by_type(shop_id_select,
                                                       'zalo_zns', 'lost')
    birthday_zalo_zns_count = api.total_automation_by_type(
        shop_id_select, 'zalo_zns', 'happy_birthday')
    anoun_zalo_zns_count = api.total_automation_by_type(
        shop_id_select, 'zalo_zns', 'anoun')
    thank_you_zalo_zns_count = api.total_automation_by_type(
        shop_id_select, 'zalo_zns', 'thank_you')

    send_settings = shop_select.get('send_settings')
    if not send_settings:
        send_settings = {'all': False, 'top': 'sms,zalo,email,chatbot'}

    return render_template('nextify/marketing_automation_shop.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           coupons_type_select=coupons_type_select,
                           coupons_type_select_ids=coupons_type_select_ids,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           welcome_sms_count=welcome_sms_count,
                           return_sms_count=return_sms_count,
                           loyal_sms_count=loyal_sms_count,
                           lost_sms_count=lost_sms_count,
                           birthday_sms_count=birthday_sms_count,
                           anoun_sms_count=anoun_sms_count,
                           thank_you_sms_count=thank_you_sms_count,
                           welcome_email_count=welcome_email_count,
                           return_email_count=return_email_count,
                           loyal_email_count=loyal_email_count,
                           lost_email_count=lost_email_count,
                           birthday_email_count=birthday_email_count,
                           anoun_email_count=anoun_email_count,
                           thank_you_email_count=thank_you_email_count,
                           welcome_zalo_count=welcome_zalo_count,
                           return_zalo_count=return_zalo_count,
                           loyal_zalo_count=loyal_zalo_count,
                           lost_zalo_count=lost_zalo_count,
                           birthday_zalo_count=birthday_zalo_count,
                           anoun_zalo_count=anoun_zalo_count,
                           thank_you_zalo_count=thank_you_zalo_count,
                           welcome_facebook_count=welcome_facebook_count,
                           return_facebook_count=return_facebook_count,
                           loyal_facebook_count=loyal_facebook_count,
                           lost_facebook_count=lost_facebook_count,
                           birthday_facebook_count=birthday_facebook_count,
                           anoun_facebook_count=anoun_facebook_count,
                           thank_you_facebook_count=thank_you_facebook_count,
                           welcome_zalo_zns_count=welcome_zalo_zns_count,
                           return_zalo_zns_count=return_zalo_zns_count,
                           loyal_zalo_zns_count=loyal_zalo_zns_count,
                           lost_zalo_zns_count=lost_zalo_zns_count,
                           birthday_zalo_zns_count=birthday_zalo_zns_count,
                           anoun_zalo_zns_count=anoun_zalo_zns_count,
                           thank_you_zalo_zns_count=thank_you_zalo_zns_count,
                           send_settings=send_settings)


@app.route('/marketing_automation/<shop_id_select>/channels', methods=['POST'])
@login_required
def shop_channels(shop_id_select):
    channel_list = request.form.get('channel_list')
    all_channel = request.form.get('all_channel')
    api.update_config_channel(shop_id_select, all_channel, channel_list)
    return json.dumps({'result': 'success'})


@app.route('/marketing_automation/<shop_id_select>/activity', methods=['GET'])
@login_required
def marketing_automation_shop_activity(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if 'sms' not in merchant:
        merchant['sms'] = {}

    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/marketing_automation')
    if 'email_template' not in shop_select:
        shop_select['email_template'] = {}
    if 'sms' not in shop_select:
        shop_select['sms'] = {}
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop_id_select, all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]

    page = int(request.args.get('page', 1))

    list_activity = api.get_shop_acvity_smart_message(
        merchant_id,
        shop_id_select,
        page=page,
        page_size=settings.ITEMS_PER_PAGE)
    total_activity = api.total_activity_smart_message(shop_id_select)

    pagination = Pagination(page=page,
                            total=total_activity,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template('nextify/marketing_automation_shop_activity.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           coupons_type_select=coupons_type_select,
                           coupons_type_select_ids=coupons_type_select_ids,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           list_activity=list_activity,
                           total_activity=total_activity,
                           pagination=pagination)


@app.route('/marketing_automation/<shop_id_select>/config/<mar_type>',
           methods=['GET'])
@login_required
def marketing_automation_shop_item(shop_id_select, mar_type):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    if not shop_select:
        return redirect('/marketing_automation')
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop_id_select, all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    sign_zns = False
    check_sign_zns = api.check_token_zns(shop_id_select)
    if check_sign_zns:
        sign_zns = True
    if 'sms' not in shop:
        shop['sms'] = {}

    if 'sms' not in merchant:
        merchant['sms'] = {}

    if 'email_template' not in merchant:
        merchant['email_template'] = {}

    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))

    if 'email_template' not in shop_select:
        shop_select['email_template'] = {}
    if 'sms' not in shop_select:
        shop_select['sms'] = {}

    mar_type_info_sms = {}
    mar_type_info_email = {}
    if mar_type == 'anoun':
        mar_type_info_sms = shop_select['sms'].get('announcement')
        mar_type_info_email = shop_select['email_template'].get('announcement')
    else:
        mar_type_info_sms = shop_select['sms'].get(str(mar_type))
        mar_type_info_email = shop_select['email_template'].get(str(mar_type))

    template_config = ''
    if mar_type == 'welcome':
        template_config = "nextify/marketing_automation_shop_welcome.html"
    elif mar_type == 'return':
        template_config = "nextify/marketing_automation_shop_return.html"
    elif mar_type == 'lost':
        template_config = "nextify/marketing_automation_shop_lost.html"
    elif mar_type == 'loyal':
        template_config = "nextify/marketing_automation_shop_loyal.html"
    elif mar_type == 'happy_birthday':
        template_config = "nextify/marketing_automation_shop_happy_birthday.html"
    elif mar_type == 'anoun':
        template_config = "nextify/marketing_automation_shop_announ.html"
    else:
        template_config = "nextify/marketing_automation_shop_thank_you.html"

    return render_template(template_config,
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           coupons_type_select=coupons_type_select,
                           coupons_type_select_ids=coupons_type_select_ids,
                           shop_in_mer=shop_in_mer,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           mar_type=mar_type,
                           mar_type_info_sms=mar_type_info_sms,
                           mar_type_info_email=mar_type_info_email,
                           tags=tags,
                           sign_zns=sign_zns)


@app.route('/marketing_automation/<shop_id_select>/config/<mar_type>/<active>',
           methods=['GET'])
@login_required
def marketing_automation_shop_active(shop_id_select, mar_type, active):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_sms = shop_select['sms'].get(str(mar_type))
    if str(active) in ['true', 'True']:
        active = True
    else:
        active = False
    api.update_sms_templates_active(shop_id_select, mar_type, active)
    producer_data = {"shop_id": str(shop_id_select), "status": active}

    producer_data = json.dumps(producer_data).encode('utf-8')
    if mar_type == 'lost':
        producer.send(settings.lost_consumer, producer_data)
        producer.flush()
    if mar_type == 'happy_birthday':
        producer.send(settings.birthday_consumer, producer_data)
        producer.flush()
    if mar_type == 'thank_you':
        producer.send(settings.thankyou_consumer, producer_data)
        producer.flush()
    return json.dumps({'result': True})


@app.route('/marketing_automation/select_email_template', methods=['GET'])
@login_required
def select_email_template():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    user_login = g.user
    page = int(request.args.get('page', 1))
    shop = g.shop
    shop_id = g.shop_id
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    list_email_templates = api.email_example_by_type(select_branch="all",
                                                     page=1)
    total = api.count_email_example(select_branch="all")
    total_pages = (total // 8) + 1 if total % 8 != 0 else total / 8
    return render_template('nextify/view_email_templates.html',
                           merchant=merchant,
                           user_login=user_login,
                           list_email_templates=list_email_templates,
                           total_pages=total_pages)


@app.route('/auto_marketing/<shop_id_select>/welcome_mail', methods=['POST'])
@login_required
def shop_content_welcome_mail(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')

    sms_templates = dict()
    sms_templates['title'] = request.form.get('welcome_title_mail').strip()
    sms_templates['content'] = request.form.get('welcome_content_mail').strip()

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if shop_select:
        api.update_email_shop_automation(shop_id_select, sms_templates,
                                         'welcome')

        return redirect('/marketing_automation/%s' % (shop_id_select))
    else:
        return redirect('/marketing_automation')


@app.route('/auto_marketing/<shop_id_select>/return_mail', methods=['POST'])
@login_required
def shop_content_return_mail(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')

    sms_templates = dict()
    sms_templates['title'] = request.form.get('return_title_mail').strip()
    sms_templates['content'] = request.form.get('return_content_mail').strip()

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if shop_select:
        api.update_email_shop_automation(shop_id_select, sms_templates,
                                         'return')
        return redirect('/marketing_automation/%s' % (shop_id_select))
    else:
        return redirect('/marketing_automation')


@app.route('/auto_marketing/<shop_id_select>/loyal_mail', methods=['POST'])
@login_required
def shop_content_loyal_mail(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')

    sms_templates = dict()
    sms_templates['title'] = request.form.get('loyal_title_mail').strip()
    sms_templates['content'] = request.form.get('loyal_content_mail').strip()

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if shop_select:
        api.update_email_shop_automation(shop_id_select, sms_templates,
                                         'loyal')
        return redirect('/marketing_automation/%s' % (shop_id_select))
    else:
        return redirect('/marketing_automation')


@app.route('/auto_marketing/<shop_id_select>/lost_customers_mail',
           methods=['POST'])
@login_required
def shop_content_lost_customers_mail(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')

    sms_templates = dict()
    sms_templates['title'] = request.form.get(
        'lost_customers_title_mail').strip()
    sms_templates['content'] = request.form.get(
        'lost_customers_content_mail').strip()

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if shop_select:
        api.update_email_shop_automation(shop_id_select, sms_templates,
                                         'lost_customers')
        return redirect('/marketing_automation/%s' % (shop_id_select))
    else:
        return redirect('/marketing_automation')


@app.route('/auto_marketing_hq/birthday_mail', methods=['POST'])
@login_required
def content_birthday_mail():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')

    sms_templates = dict()
    sms_templates['title'] = request.form.get('birthday_title_mail').strip()
    sms_templates['content'] = request.form.get(
        'birthday_content_mail').strip()

    api.update_email_content_sms_templates_hq_by_type(merchant_id,
                                                      sms_templates,
                                                      'happy_birthday')
    return redirect('/marketing_automation')


@app.route('/auto_marketing/<shop_id_select>/birthday_mail', methods=['POST'])
@login_required
def shop_content_birthday_mail(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')

    sms_templates = dict()
    sms_templates['title'] = request.form.get('birthday_title_mail').strip()
    sms_templates['content'] = request.form.get(
        'birthday_content_mail').strip()

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if shop_select:
        api.update_email_shop_automation(shop_id_select, sms_templates,
                                         'happy_birthday')
        return redirect('/marketing_automation/%s' % (shop_id_select))
    else:
        return redirect('/marketing_automation')


@app.route('/auto_marketing/<shop_id_select>/anoun_mail', methods=['POST'])
@login_required
def shop_content_anoun_mail(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')

    sms_templates = dict()
    sms_templates['title'] = request.form.get('anoun_title_mail').strip()
    sms_templates['content'] = request.form.get('anoun_content_mail').strip()

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if shop_select:
        api.update_email_shop_automation(shop_id_select, sms_templates,
                                         'anoun')
        return redirect('/marketing_automation/%s' % (shop_id_select))
    else:
        return redirect('/marketing_automation')


@app.route(
    '/marketing_automation/<shop_id_select>/update/<mar_type>/<mess_method>',
    methods=['POST'])
@login_required
def auto_marketing_active_method(shop_id_select, mar_type, mess_method):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    mess_value = request.form.get('mess_value')
    mess_value = True if str(mess_value) == 'true' else False
    if str(mess_method) == "facebook":
        if mess_value == True:
            try:
                app = api.get_app_synchronized(name_app='chatfuel',
                                               merchant_id=merchant_id)
                chatbot_id = app.get('setting')['chatbot_id']
                chatfuel_token = app.get('setting')['chatfuel_token']
                if str(chatbot_id) == "None" or str(chatfuel_token) == "None" \
                        or len(chatbot_id) == 0 or len(chatfuel_token) == 0:
                    try:
                        app = api.get_app_synchronized(name_app='ahachat',
                                                       merchant_id=merchant_id)
                        chatbot_id = app.get('setting')['chatbot_id']
                        ahachat_token = app.get('setting')['ahachat_token']
                        if str(chatbot_id) == "None" or str(ahachat_token) == "None" \
                                or len(chatbot_id) == 0 or len(ahachat_token) == 0:
                            return json.dumps(
                                {'error': gettext("Chua_cau_hinh_chatbot")})
                    except:
                        return json.dumps(
                            {'error': gettext("Chua_cau_hinh_chatbot")})
            except:
                try:
                    app = api.get_app_synchronized(name_app='ahachat',
                                                   merchant_id=merchant_id)
                    chatbot_id = app.get('setting')['chatbot_id']
                    chatfuel_token = app.get('setting')['ahachat_token']
                    if str(chatbot_id) == "None" or str(chatfuel_token) == "None" \
                            or len(chatbot_id) == 0 or len(chatfuel_token) == 0:
                        return json.dumps(
                            {'error': gettext("Chua_cau_hinh_chatbot")})
                except:
                    return json.dumps(
                        {'error': gettext("Chua_cau_hinh_chatbot")})
    api.update_automation_mess_method(shop_id_select, mar_type, mess_method,
                                      mess_value)
    return json.dumps({'result': True})


@app.route('/auto_marketing/<shop_id_select>/welcome', methods=['POST'])
@login_required
def auto_marketing_first_customer(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    error_count = 0
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    sms_templates = dict()
    sms_templates['welcome'] = {}
    status = request.form.get('status')
    if status and str(status) == 'True':
        sms_templates['welcome']['status'] = True
    else:
        sms_templates['welcome']['status'] = False
    sms_templates['welcome']['mess'] = request.form.get('welcome').strip()
    sms_templates['welcome']['zalo_mess'] = request.form.get(
        'zalo_mess').strip()
    sms_templates['welcome']['facebook_mess'] = request.form.get(
        'facebook_mess').strip()
    sms_templates['welcome']['zalo_zns_mess'] = request.form.get(
        'zns_mess').strip()

    sms_templates['welcome']['active'] = True if str(
        request.form.get('active_welcome')) == 'true' else False
    sms_templates['welcome']['expire'] = request.form.get('ex_welcome').strip()
    sms_templates['welcome']['enable'] = request.form.get('enable_welcome')
    sms_templates['welcome']['type_coupon'] = request.form.get(
        'welcome_type_coupon')

    gender = request.form.get('welcome_gender')
    sms_templates['welcome']['gender'] = gender
    ranks = request.form.get('welcome_ranks')
    sms_templates['welcome']['ranks'] = ranks
    # visit_by
    visit_by = request.form.get('welcome_visit_by')
    sms_templates['welcome']['visits_by'] = visit_by
    # Zalo
    zalo_welcome = request.form.get('zalo_welcome')
    sms_templates['welcome']['zalo'] = True if str(
        zalo_welcome) == 'true' else False
    # Email
    mail_welcome = request.form.get('mail_welcome')
    sms_templates['welcome']['mail'] = True if str(
        mail_welcome) == 'true' else False
    # Facebook
    facebook_welcome = request.form.get('facebook_welcome')
    sms_templates['welcome']['facebook'] = True if str(
        facebook_welcome) == 'true' else False
    # wifi
    wifi_welcome = request.form.get('wifi_welcome')
    sms_templates['welcome']['wifi'] = True if str(
        wifi_welcome) == 'true' else False
    # Zalo ZNS
    zns_welcome = request.form.get('zns_welcome')
    sms_templates['welcome']['zalo_zns'] = True if str(
        zns_welcome) == 'true' else False
    auto_coupon = request.form.get('auto_coupon')
    sms_templates['welcome']['auto_coupon'] = True if str(
        auto_coupon) == 'true' else False

    email_templates = dict()
    email_templates['title'] = request.form.get('welcome_title_mail').strip()
    email_templates['content'] = request.form.get(
        'welcome_content_mail').strip()
    email_templates['design'] = request.form.get('design').strip()
    api.update_email_shop_automation(shop_id_select, email_templates,
                                     'welcome')

    # Push
    push_welcome = request.form.get('push_welcome')
    sms_templates['welcome']['push'] = push_welcome
    coupon_expire = dict()
    coupon_expire['welcome'] = request.form.get('ex_welcome', '').strip()
    error_expire = 0
    for key, value in coupon_expire.items():
        if value and len(value) > 0:
            if not value.isdigit():
                error_expire += 1
    if error_expire > 0:
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "Ngay_het_han_coupon_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))

    api.update_sms_templates_by_type(shop_id_select, sms_templates, 'welcome')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_email = {}
    mar_type = 'welcome'
    mar_type_info_sms = shop_select['sms'].get(str(mar_type))
    mar_type_info_email = shop_select['email_template'].get(str(mar_type))
    is_save = request.form.get('is_save')
    if is_save and str(is_save) == 'True':
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            mar_type_info_sms=mar_type_info_sms,
            mar_type_info_email=mar_type_info_email)
    return redirect(
        url_for('marketing_automation_shop', shop_id_select=shop_id_select))


@app.route('/auto_marketing/<shop_id_select>/thank_you', methods=['POST'])
@login_required
def auto_marketing_thank_you(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    error_count = 0
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    sms_templates = dict()
    sms_templates['thank_you'] = {}
    status = request.form.get('status')
    if status and str(status) == 'True':
        sms_templates['thank_you']['status'] = True
    else:
        sms_templates['thank_you']['status'] = False
    sms_templates['thank_you']['mess'] = request.form.get('thank_you').strip()
    sms_templates['thank_you']['zalo_mess'] = request.form.get(
        'zalo_mess').strip()
    sms_templates['thank_you']['facebook_mess'] = request.form.get(
        'facebook_mess').strip()
    sms_templates['thank_you']['active'] = True if str(
        request.form.get('active_thank_you')) == 'true' else False
    sms_templates['thank_you']['zalo_zns_mess'] = request.form.get(
        'zns_mess').strip()
    sms_templates['thank_you']['expire'] = request.form.get(
        'ex_thank_you').strip()
    sms_templates['thank_you']['enable'] = request.form.get('enable_thank_you')

    sms_templates['thank_you']['type_coupon'] = request.form.get(
        'welcome_type_coupon')
    thank_you_count = request.form.get('thank_you_count', '').strip()
    if thank_you_count and len(
            thank_you_count) > 0 and not thank_you_count.isdigit():
        error_count += 1
    sms_templates['thank_you']['count'] = thank_you_count
    tags_group = request.form.get('tags_selects')
    tags_group = tags_group.split(',')
    tags_array = []
    if tags_group and len(tags_group) > 0:
        for tag in tags_group:
            tag = tag.strip()
            if len(tag) > 0:
                tags_array.append(ObjectId(tag))
    sms_templates['thank_you']['tags'] = tags_array
    gender = request.form.get('thank_you_gender')
    sms_templates['thank_you']['gender'] = gender
    ranks = request.form.get('thank_you_ranks')
    sms_templates['thank_you']['ranks'] = ranks
    auto_coupon = request.form.get('auto_coupon')
    sms_templates['thank_you']['auto_coupon'] = True if str(
        auto_coupon) == 'true' else False
    # Zalo
    zalo_thank_you = request.form.get('zalo_thank_you')
    sms_templates['thank_you']['zalo'] = True if str(
        zalo_thank_you) == 'true' else False
    # Email
    mail_thank_you = request.form.get('mail_thank_you')
    sms_templates['thank_you']['mail'] = True if str(
        mail_thank_you) == 'true' else False
    # Facebook
    facebook_thank_you = request.form.get('facebook_thank_you')
    sms_templates['thank_you']['facebook'] = True if str(
        facebook_thank_you) == 'true' else False
    # wifi
    wifi_thank_you = request.form.get('wifi_thank_you')
    sms_templates['thank_you']['wifi'] = True if str(
        wifi_thank_you) == 'true' else False
    # Zalo ZNS
    zns_thank_you = request.form.get('zns_thank_you')
    sms_templates['thank_you']['zalo_zns'] = True if str(
        zns_thank_you) == 'true' else False
    email_templates = dict()
    email_templates['title'] = request.form.get('thank_you_title_mail').strip()
    email_templates['content'] = request.form.get(
        'thank_you_content_mail').strip()
    email_templates['design'] = request.form.get('design').strip()
    api.update_email_shop_automation(shop_id_select, email_templates,
                                     'thank_you')

    # Push
    push_welcome = request.form.get('push_thank_you')
    sms_templates['thank_you']['push'] = push_welcome
    coupon_expire = dict()
    coupon_expire['thank_you'] = request.form.get('ex_thank_you', '').strip()
    error_expire = 0
    for key, value in coupon_expire.items():
        if value and len(value) > 0:
            if not value.isdigit():
                error_expire += 1
    if error_expire > 0:
        return render_template(
            'nextify/marketing_automation_shop_thank_you.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "Ngay_het_han_coupon_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))
    if error_count > 0:
        return render_template(
            'nextify/marketing_automation_shop_thank_you.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "So_ngay_hoac_so_lan_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))

    api.update_sms_templates_by_type(shop_id_select, sms_templates,
                                     'thank_you')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_email = {}
    mar_type = 'thank_you'
    mar_type_info_sms = shop_select['sms'].get(str(mar_type))
    mar_type_info_email = shop_select['email_template'].get(str(mar_type))
    is_save = request.form.get('is_save')
    if is_save and str(is_save) == 'True':
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            mar_type_info_sms=mar_type_info_sms,
            mar_type_info_email=mar_type_info_email)
    return redirect(
        url_for('marketing_automation_shop', shop_id_select=shop_id_select))


@app.route('/auto_marketing/<shop_id_select>/return', methods=['POST'])
@login_required
def auto_marketing_return(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    error_count = 0
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    sms_templates = dict()
    sms_templates['return'] = {}
    status = request.form.get('status')
    if status and str(status) == 'True':
        sms_templates['return']['status'] = True
    else:
        sms_templates['return']['status'] = False
    count = request.form.get('return_count').strip()
    if count and len(count) > 0 and not count.isdigit():
        error_count += 1
    count_max = request.form.get('return_count_max').strip()
    if count_max and len(count_max) > 0 and not count_max.isdigit():
        error_count += 1
    sms_templates['return']['count'] = count
    sms_templates['return']['count_max'] = count_max
    tags_group = request.form.get('tags_selects')
    tags_group = tags_group.split(',')
    tags_array = []
    if tags_group and len(tags_group) > 0:
        for tag in tags_group:
            tag = tag.strip()
            if len(tag) > 0:
                tags_array.append(ObjectId(tag))
    sms_templates['return']['tags'] = tags_array
    sms_templates['return']['mess'] = request.form.get('returning').strip()
    sms_templates['return']['zalo_mess'] = request.form.get(
        'zalo_mess').strip()
    sms_templates['return']['facebook_mess'] = request.form.get(
        'facebook_mess').strip()
    # sms_templates['return']['info'] = request.form.get(
    #     'info_returning', '').strip()
    sms_templates['return']['zalo_zns_mess'] = request.form.get(
        'zns_mess').strip()
    active = request.form.get('active_returning')
    sms_templates['return']['active'] = True if str(
        active) == 'true' else False
    sms_templates['return']['expire'] = request.form.get(
        'ex_returning').strip()
    sms_templates['return']['enable'] = request.form.get('enable_return')
    sms_templates['return']['type_coupon'] = request.form.get(
        'returning_type_coupon')
    zalo_return = request.form.get('zalo_return')
    sms_templates['return']['zalo'] = True if str(
        zalo_return) == 'true' else False
    facebook_return = request.form.get('facebook_return')
    sms_templates['return']['facebook'] = True if str(
        facebook_return) == 'true' else False
    # wifi
    wifi_return = request.form.get('wifi_return')
    sms_templates['return']['wifi'] = True if str(
        wifi_return) == 'true' else False
    auto_coupon = request.form.get('auto_coupon')
    sms_templates['return']['auto_coupon'] = True if str(
        auto_coupon) == 'true' else False
    # Email
    mail_return = request.form.get('mail_return')
    sms_templates['return']['mail'] = True if str(
        mail_return) == 'true' else False
    # Zalo ZNS
    zns_return = request.form.get('zns_return')
    sms_templates['return']['zalo_zns'] = True if str(
        zns_return) == 'true' else False
    email_templates = dict()
    email_templates['title'] = request.form.get('return_title_mail').strip()
    email_templates['content'] = request.form.get(
        'return_content_mail').strip()
    email_templates['design'] = request.form.get('design').strip()

    api.update_email_shop_automation(shop_id_select, email_templates, 'return')
    push_return = request.form.get('push_return')
    sms_templates['return']['push'] = push_return
    gender = request.form.get('return_gender')
    sms_templates['return']['gender'] = gender
    ranks = request.form.get('return_ranks')
    sms_templates['return']['ranks'] = ranks
    # visit_by
    visit_by = request.form.get('return_visit_by')
    sms_templates['return']['visits_by'] = visit_by
    coupon_expire = dict()
    coupon_expire['return'] = request.form.get('ex_returning', '').strip()
    error_expire = 0
    for key, value in coupon_expire.items():
        if value and len(value) > 0:
            if not value.isdigit():
                error_expire += 1
    if error_expire > 0:
        return render_template(
            'nextify/marketing_automation_shop_return.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "Ngay_het_han_coupon_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))
    if error_count > 0:
        return render_template(
            'nextify/marketing_automation_shop_return.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "So_ngay_hoac_so_lan_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))

    api.update_sms_templates_by_type(shop_id_select, sms_templates, 'return')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_email = {}
    mar_type = 'return'
    mar_type_info_sms = shop_select['sms'].get(str(mar_type))
    mar_type_info_email = shop_select['email_template'].get(str(mar_type))
    is_save = request.form.get('is_save')
    if is_save and str(is_save) == 'True':
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            mar_type_info_sms=mar_type_info_sms,
            mar_type_info_email=mar_type_info_email)
    return redirect(
        url_for('marketing_automation_shop', shop_id_select=shop_id_select))


@app.route('/auto_marketing/<shop_id_select>/loyal', methods=['POST'])
@login_required
def auto_marketing_loyal(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    error_count = 0
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    sms_templates = dict()
    sms_templates['loyal'] = {}
    status = request.form.get('status')
    if status and str(status) == 'True':
        sms_templates['loyal']['status'] = True
    else:
        sms_templates['loyal']['status'] = False
    count = request.form.get('loyal_count').strip()
    if count and len(count) > 0 and not count.isdigit():
        error_count += 1
    count_max = request.form.get('loyal_count_max').strip()
    if count_max and len(count_max) > 0 and not count_max.isdigit():
        error_count += 1
    sms_templates['loyal']['count'] = count
    sms_templates['loyal']['count_max'] = count_max
    loyal_count = request.form.get('loyal_count', '').strip()
    if loyal_count and len(loyal_count) > 0 and not loyal_count.isdigit():
        error_count += 1
    sms_templates['loyal']['mess'] = request.form.get(
        'regular_customer').strip()
    sms_templates['loyal']['zalo_mess'] = request.form.get('zalo_mess').strip()
    sms_templates['loyal']['facebook_mess'] = request.form.get(
        'facebook_mess').strip()
    sms_templates['loyal']['zalo_zns_mess'] = request.form.get(
        'zns_mess').strip()
    tags_group = request.form.get('tags_selects')
    tags_group = tags_group.split(',')
    tags_array = []
    if tags_group and len(tags_group) > 0:
        for tag in tags_group:
            tag = tag.strip()
            if len(tag) > 0:
                tags_array.append(ObjectId(tag))
    sms_templates['loyal']['tags'] = tags_array
    # sms_templates['loyal']['info'
    # ] = request.form.get('info_regular_customer').strip().strip()
    active_loyal = request.form.get('active_regular_cus')
    sms_templates['loyal']['active'] = True if str(
        active_loyal) == 'true' else False
    sms_templates['loyal']['expire'] = request.form.get(
        'ex_regular_customer').strip()
    sms_templates['loyal']['enable'] = request.form.get('enable_loyal')
    sms_templates['loyal']['type_coupon'] = request.form.get(
        'regular_customer_type_coupon')
    auto_coupon = request.form.get('auto_coupon')
    sms_templates['loyal']['auto_coupon'] = True if str(
        auto_coupon) == 'true' else False
    zalo_loyal = request.form.get('zalo_loyal')
    sms_templates['loyal']['zalo'] = True if str(
        zalo_loyal) == 'true' else False
    facebook_loyal = request.form.get('facebook_loyal')
    sms_templates['loyal']['facebook'] = True if str(
        facebook_loyal) == 'true' else False
    # wifi
    wifi_loyal = request.form.get('wifi_loyal')
    sms_templates['loyal']['wifi'] = True if str(
        wifi_loyal) == 'true' else False
    push_loyal = request.form.get('push_loyal')
    sms_templates['loyal']['push'] = push_loyal
    coupon_expire = dict()
    coupon_expire['loyal'] = request.form.get('ex_regular_customer',
                                              '').strip()
    # Email
    mail_loyal = request.form.get('mail_loyal')
    sms_templates['loyal']['mail'] = True if str(
        mail_loyal) == 'true' else False
    # Zalo ZNS
    zns_loyal = request.form.get('zns_loyal')
    sms_templates['loyal']['zalo_zns'] = True if str(
        zns_loyal) == 'true' else False
    email_templates = dict()
    email_templates['title'] = request.form.get('loyal_title_mail').strip()
    email_templates['content'] = request.form.get('loyal_content_mail').strip()
    email_templates['design'] = request.form.get('design').strip()

    api.update_email_shop_automation(shop_id_select, email_templates, 'loyal')
    gender = request.form.get('loyal_gender')
    sms_templates['loyal']['gender'] = gender
    ranks = request.form.get('loyal_ranks')
    sms_templates['loyal']['ranks'] = ranks
    # visit_by
    visit_by = request.form.get('loyal_visit_by')
    sms_templates['loyal']['visits_by'] = visit_by
    error_expire = 0
    for key, value in coupon_expire.items():
        if value and len(value) > 0:
            if not value.isdigit():
                error_expire += 1
    if error_expire > 0:
        return render_template(
            'nextify/marketing_automation_shop_loyal.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "Ngay_het_han_coupon_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))
    if error_count > 0:
        return render_template(
            'nextify/marketing_automation_shop_loyal.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "So_ngay_hoac_so_lan_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))

    api.update_sms_templates_by_type(shop_id_select, sms_templates, 'loyal')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_email = {}
    mar_type = 'loyal'
    mar_type_info_sms = shop_select['sms'].get(str(mar_type))
    mar_type_info_email = shop_select['email_template'].get(str(mar_type))
    is_save = request.form.get('is_save')
    if is_save and str(is_save) == 'True':
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            mar_type_info_sms=mar_type_info_sms,
            mar_type_info_email=mar_type_info_email)
    return redirect(
        url_for('marketing_automation_shop', shop_id_select=shop_id_select))


@app.route('/auto_marketing/<shop_id_select>/lost', methods=['POST'])
@login_required
def auto_marketing_lost(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    error_count = 0
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    sms_templates = dict()
    sms_templates['lost'] = {}
    status = request.form.get('status')
    if status and str(status) == 'True':
        sms_templates['lost']['status'] = True
    else:
        sms_templates['lost']['status'] = False
    sms_templates['lost']['count'] = request.form.get('lost_count')
    lost_count = request.form.get('lost_count', '').strip()
    if not lost_count or str(lost_count) == 'None' or len(
            lost_count) == 0 or not str(lost_count).isdigit():
        return render_template(
            'nextify/marketing_automation_shop_lost.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext("Ban_chua_nhap_so_ngay_da_lau_chua_quay_lai"))
    if lost_count and len(lost_count) > 0 and not str(lost_count).isdigit():
        error_count += 1
    lost_return_count = request.form.get('lost_return_count').strip()
    if lost_return_count and len(
            lost_return_count) > 0 and not lost_return_count.isdigit():
        error_count += 1
    lost_return_count_max = request.form.get('lost_return_count_max').strip()
    if lost_return_count_max and len(
            lost_return_count_max) > 0 and not lost_return_count_max.isdigit():
        error_count += 1
    sms_templates['lost']['return_count'] = lost_return_count
    sms_templates['lost']['return_count_max'] = lost_return_count_max
    tags_group = request.form.get('tags_selects')
    tags_group = tags_group.split(',')
    tags_array = []
    if tags_group and len(tags_group) > 0:
        for tag in tags_group:
            tag = tag.strip()
            if len(tag) > 0:
                tags_array.append(ObjectId(tag))
    sms_templates['lost']['tags'] = tags_array
    sms_templates['lost']['mess'] = request.form.get('one_month').strip()
    sms_templates['lost']['zalo_mess'] = request.form.get('zalo_mess').strip()
    sms_templates['lost']['facebook_mess'] = request.form.get(
        'facebook_mess').strip()
    sms_templates['lost']['zalo_zns_mess'] = request.form.get(
        'zns_mess').strip()
    # sms_templates['lost']['info'] = request.form.get('info_one_month').strip()
    active_one_month = request.form.get('active_one_month')
    sms_templates['lost']['active'] = True if str(
        active_one_month) == 'true' else False
    expire = request.form.get('ex_one_month')
    sms_templates['lost']['expire'] = expire.strip() if expire else expire
    sms_templates['lost']['enable'] = request.form.get('enable_lost')
    sms_templates['lost']['type_coupon'] = request.form.get(
        'one_month_type_coupon')
    zalo_lost = request.form.get('zalo_lost')
    sms_templates['lost']['zalo'] = True if str(zalo_lost) == 'true' else False
    facebook_lost = request.form.get('facebook_lost')
    sms_templates['lost']['facebook'] = True if str(
        facebook_lost) == 'true' else False
    # Zalo ZNS
    zns_lost = request.form.get('zns_lost')
    sms_templates['lost']['zalo_zns'] = True if str(
        zns_lost) == 'true' else False
    # wifi
    wifi_lost = request.form.get('wifi_lost')
    sms_templates['lost']['wifi'] = True if str(wifi_lost) == 'true' else False
    auto_coupon = request.form.get('auto_coupon')
    sms_templates['lost']['auto_coupon'] = True if str(
        auto_coupon) == 'true' else False
    push_lost = request.form.get('push_lost')
    sms_templates['lost']['push'] = push_lost

    gender = request.form.get('lost_gender')
    sms_templates['lost']['gender'] = gender
    ranks = request.form.get('lost_ranks')
    sms_templates['lost']['ranks'] = ranks

    # Email
    mail_lost = request.form.get('mail_lost')
    sms_templates['lost']['mail'] = True if str(mail_lost) == 'true' else False
    email_templates = dict()
    email_templates['title'] = request.form.get(
        'lost_customers_title_mail').strip()
    email_templates['content'] = request.form.get(
        'lost_customers_content_mail').strip()
    email_templates['design'] = request.form.get('design').strip()

    api.update_email_shop_automation(shop_id_select, email_templates, 'lost')
    coupon_expire = dict()
    coupon_expire['lost'] = request.form.get('ex_one_month', '').strip()
    error_expire = 0
    for key, value in coupon_expire.items():
        if value and len(value) > 0:
            if not value.isdigit():
                error_expire += 1
    if error_expire > 0:
        return render_template(
            'nextify/marketing_automation_shop_lost.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "Ngay_het_han_coupon_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))
    if error_count > 0:
        return render_template(
            'nextify/marketing_automation_shop_lost.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "So_ngay_hoac_so_lan_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))

    api.update_sms_templates_by_type(shop_id_select, sms_templates, 'lost')
    automate_type = shop_select.get('sms', {})
    lost_tmp = automate_type.get('lost', {})
    count = lost_tmp.get('count')
    if lost_tmp and count:
        if str(count) != 'None' and len(
                str(count)) > 0 and str(count).isdigit():
            sms = lost_tmp.get('active')
            zalo = lost_tmp.get('zalo')
            email = lost_tmp.get('mail')
            facebook = lost_tmp.get('facebook')
            if sms or zalo or email or facebook:
                api.save_lost_remind(shop_id, 1)
            else:
                api.save_lost_remind(shop_id, 0)
    is_save = request.form.get('is_save')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_email = {}
    mar_type = 'lost'
    mar_type_info_sms = shop_select['sms'].get(str(mar_type))
    mar_type_info_email = shop_select['email_template'].get(str(mar_type))
    if is_save and str(is_save) == 'True':
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            mar_type_info_sms=mar_type_info_sms,
            mar_type_info_email=mar_type_info_email)
    return redirect(
        url_for('marketing_automation_shop', shop_id_select=shop_id_select))


@app.route('/auto_marketing/<shop_id_select>/birthday', methods=['POST'])
@login_required
def auto_marketing_birthday(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    error_count = 0
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    sms_templates = dict()

    sms_templates['happy_birthday'] = {}

    happy_birthday_cp = request.form.get('happy_birthday_cp')
    reminder_birthday_mess = request.form.get('reminder_birthday')
    happy_birthday_reminder_cp = request.form.get('happy_birthday_reminder_cp')

    status = request.form.get('status')
    if status and str(status) == 'True':
        sms_templates['happy_birthday']['status'] = True
    else:
        sms_templates['happy_birthday']['status'] = False
    sms_templates['happy_birthday']['message'] = request.form.get(
        'happy_birthday').strip()
    sms_templates['happy_birthday']['zalo_mess'] = request.form.get(
        'zalo_mess').strip()
    sms_templates['happy_birthday']['facebook_mess'] = request.form.get(
        'facebook_mess').strip()
    sms_templates['happy_birthday']['zalo_zns_mess'] = request.form.get(
        'zns_mess').strip()

    if happy_birthday_cp and len(happy_birthday_cp) > 0:
        sms_templates['happy_birthday']['mess_cp'] = happy_birthday_cp.strip()
    if reminder_birthday_mess and len(reminder_birthday_mess) > 0:
        sms_templates['happy_birthday'][
            'mess_reminder'] = reminder_birthday_mess.strip()
    if happy_birthday_reminder_cp and len(happy_birthday_reminder_cp) > 0:
        sms_templates['happy_birthday'][
            'mess_reminder_cp'] = happy_birthday_reminder_cp.strip()

    expire = request.form.get('ex_happy_birthday')
    sms_templates['happy_birthday']['expire'] = expire.strip() if expire \
        else expire
    bday_date_send = request.form.get('bday_date_send')
    tags_group = request.form.get('tags_selects')
    tags_group = tags_group.split(',')
    tags_array = []
    if tags_group and len(tags_group) > 0:
        for tag in tags_group:
            tag = tag.strip()
            if len(tag) > 0:
                tags_array.append(ObjectId(tag))
    sms_templates['happy_birthday']['tags'] = tags_array
    if not bday_date_send or not bday_date_send.isdigit():
        return render_template(
            'nextify/marketing_automation_shop_happy_birthday.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext("Vui_long_nhap_ngay_nhac_truoc_sinh_nhat."))
    sms_templates['happy_birthday']['date_send'] = request.form.get(
        'bday_date_send')
    sms_templates['happy_birthday']['reminder'] = request.form.get(
        'reminder_bday')
    active_birthday = request.form.get('active_birthday')
    sms_templates['happy_birthday']['active'] = True if str(
        active_birthday) == 'true' else False
    sms_templates['happy_birthday']['enable'] = request.form.get(
        'enable_birthday')
    sms_templates['happy_birthday']['type_coupon'] = request.form.get(
        'happy_birthday_type_coupon')
    auto_coupon = request.form.get('auto_coupon')
    sms_templates['happy_birthday']['auto_coupon'] = True if str(
        auto_coupon) == 'true' else False
    zalo_happy_birthday = request.form.get('zalo_happy_birthday')
    sms_templates['happy_birthday']['zalo'] = True if str(
        zalo_happy_birthday) == 'true' else False
    facebook_happy_birthday = request.form.get('facebook_happy_birthday')
    sms_templates['happy_birthday']['facebook'] = True if str(
        facebook_happy_birthday) == 'true' else False
    # Zalo ZNS
    zns_happy_birthday = request.form.get('zns_happy_birthday')
    sms_templates['happy_birthday']['zalo_zns'] = True if str(
        zns_happy_birthday) == 'true' else False
    # wifi
    wifi_birthday = request.form.get('wifi_birthday')
    sms_templates['happy_birthday']['wifi'] = True if str(
        wifi_birthday) == 'true' else False
    push_happy_birthday = request.form.get('push_happy_birthday')
    sms_templates['happy_birthday']['push'] = push_happy_birthday

    gender = request.form.get('happy_birthday_gender')
    sms_templates['happy_birthday']['gender'] = gender
    ranks = request.form.get('happy_birthday_ranks')
    sms_templates['happy_birthday']['ranks'] = ranks
    # Email
    mail_birthday = request.form.get('mail_happy_birthday')
    sms_templates['happy_birthday']['mail'] = True if str(
        mail_birthday) == 'true' else False
    reminder_bday = request.form.get('reminder_bday')
    sms_templates['happy_birthday']['reminder'] = True if str(
        reminder_bday) == 'true' else False
    email_templates = dict()
    email_templates['title'] = request.form.get('birthday_title_mail').strip()
    email_templates['content'] = request.form.get(
        'birthday_content_mail').strip()
    email_templates['design'] = request.form.get('design').strip()
    api.update_email_shop_automation(shop_id_select, email_templates,
                                     'happy_birthday')

    coupon_expire = dict()
    coupon_expire['happy_birthday'] = request.form.get('ex_happy_birthday',
                                                       '').strip()
    error_expire = 0
    for key, value in coupon_expire.items():
        if value and len(value) > 0:
            if not value.isdigit():
                error_expire += 1
    if error_expire > 0:
        return render_template(
            'nextify/marketing_automation_shop_happy_birthday.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "Ngay_het_han_coupon_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))
    if error_count > 0:
        return render_template(
            'nextify/marketing_automation_shop_happy_birthday.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=
            'Số ngày hoặc số lần không đúng định dạng, phải là số ngày > 0')

    api.update_sms_templates_by_type(shop_id_select, sms_templates,
                                     'happy_birthday')

    automate_type = shop_select.get('sms', {})
    happy_birthday_tmp = automate_type.get('happy_birthday', {})
    date_send = happy_birthday_tmp.get('date_send')
    if happy_birthday_tmp and date_send:
        sms = happy_birthday_tmp.get('active')
        zalo = happy_birthday_tmp.get('zalo')
        email = happy_birthday_tmp.get('mail')
        facebook = happy_birthday_tmp.get('facebook')
        if sms or zalo or email or facebook:
            api.save_shop_birthday_remind(shop_id, 1)
        else:
            api.save_shop_birthday_remind(shop_id, 0)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_email = {}
    mar_type = 'happy_birthday'
    mar_type_info_sms = shop_select['sms'].get(str(mar_type))
    mar_type_info_email = shop_select['email_template'].get(str(mar_type))
    is_save = request.form.get('is_save')
    if is_save and str(is_save) == 'True':
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            mar_type_info_sms=mar_type_info_sms,
            mar_type_info_email=mar_type_info_email)
    return redirect(
        url_for('marketing_automation_locations',
                shop_id_select=shop_id_select))


@app.route('/auto_marketing/<shop_id_select>/anoun', methods=['POST'])
@login_required
def auto_marketing_anoun(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    error_count = 0
    coupons_type = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    coupons_type_select = [coupon for coupon in coupons_type]
    coupons_type_select_ids = [
        str(coupon.get('_id')) for coupon in coupons_type_select
    ]
    sms_templates = dict()
    sms_templates['announcement'] = {}
    status = request.form.get('status')
    if status and str(status) == 'True':
        sms_templates['announcement']['status'] = True
    else:
        sms_templates['announcement']['status'] = False
    sms_templates['announcement']['mess'] = request.form.get(
        'announcement').strip()
    sms_templates['announcement']['zalo_mess'] = request.form.get(
        'zalo_mess').strip()
    sms_templates['announcement']['facebook_mess'] = request.form.get(
        'facebook_mess').strip()
    sms_templates['announcement']['zalo_zns_mess'] = request.form.get(
        'zns_mess').strip()
    tags_group = request.form.get('tags_selects')
    tags_group = tags_group.split(',')
    tags_array = []
    if tags_group and len(tags_group) > 0:
        for tag in tags_group:
            tag = tag.strip()
            if len(tag) > 0:
                tags_array.append(ObjectId(tag))
    sms_templates['announcement']['tags'] = tags_array
    # sms_templates[
    #     'announcement']['info'] = request.form.get('info_announcement').strip()
    active_announ = request.form.get('active_announ')
    sms_templates['announcement']['active'] = True if str(
        active_announ) == 'true' else False
    expire = request.form.get('ex_announ')
    sms_templates['announcement']['expire'] = expire.strip(
    ) if expire else expire
    sms_templates['announcement']['enable'] = request.form.get('enable_announ')
    sms_templates['announcement']['type_coupon'] = request.form.get(
        'announ_type_coupon')
    auto_coupon = request.form.get('auto_coupon')
    sms_templates['announcement']['auto_coupon'] = True if str(
        auto_coupon) == 'true' else False
    zalo_announcement = request.form.get('zalo_announcement')
    sms_templates['announcement']['zalo'] = True if str(
        zalo_announcement) == 'true' else False
    facebook_announcement = request.form.get('facebook_announcement')
    sms_templates['announcement']['facebook'] = True if str(
        facebook_announcement) == 'true' else False
    # Zalo ZNS
    zns_announcement = request.form.get('zns_announcement')
    sms_templates['announcement']['zalo_zns'] = True if str(
        zns_announcement) == 'true' else False
    # wifi
    wifi_announcement = request.form.get('wifi_announcement')
    sms_templates['announcement']['wifi'] = True if str(
        wifi_announcement) == 'true' else False
    push_announcement = request.form.get('push_announcement')
    sms_templates['announcement']['push'] = push_announcement
    # Email
    mail_announcement = request.form.get('mail_announcement')
    sms_templates['announcement']['mail'] = True if str(
        mail_announcement) == 'true' else False
    email_templates = dict()
    email_templates['title'] = request.form.get('anoun_title_mail').strip()
    email_templates['content'] = request.form.get('anoun_content_mail').strip()
    email_templates['design'] = request.form.get('design').strip()

    api.update_email_shop_automation(shop_id_select, email_templates, 'anoun')
    gender = request.form.get('anoun_gender')
    sms_templates['announcement']['gender'] = gender
    ranks = request.form.get('anoun_ranks')
    sms_templates['announcement']['ranks'] = ranks

    coupon_expire = dict()
    coupon_expire['announcement'] = request.form.get('ex_announ', '').strip()
    error_expire = 0
    for key, value in coupon_expire.items():
        if value and len(value) > 0:
            if not value.isdigit():
                error_expire += 1
    if error_expire > 0:
        return render_template(
            'nextify/marketing_automation_shop_announ.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "Ngay_het_han_coupon_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))
    if error_count > 0:
        return render_template(
            'nextify/marketing_automation_shop_announ.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            error=gettext(
                "So_ngay_hoac_so_lan_khong_dung_dinh_dang,_phai_la_so_ngay_>_0"
            ))

    api.update_sms_templates_by_type(shop_id_select, sms_templates,
                                     'announcement')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    mar_type_info_sms = {}
    mar_type_info_email = {}
    mar_type_info_sms = shop_select['sms'].get('announcement')
    mar_type_info_email = shop_select['email_template'].get('announcement')
    is_save = request.form.get('is_save')
    if is_save and str(is_save) == 'True':
        return render_template(
            'nextify/marketing_automation_shop_welcome.html',
            shop=shop,
            user_login=user_login,
            merchant=merchant,
            coupons_type_select=coupons_type_select,
            coupons_type_select_ids=coupons_type_select_ids,
            shop_in_mer=shop_in_mer,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            mar_type_info_sms=mar_type_info_sms,
            mar_type_info_email=mar_type_info_email)
    return redirect(
        url_for('marketing_automation_shop', shop_id_select=shop_id_select))


def isTimeFormat(input):
    try:
        time.strptime(input, '%H:%M')
        return True
    except ValueError:
        return False


@app.route('/sms_marketing', methods=['GET'])
@login_required
def sms_marketing():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    page = int(request.args.get('page', 1))

    list_camp = []
    total_camp = 0
    list_camp = api.get_list_sms_campaign_hq(merchant_id,
                                             is_sms=True,
                                             page=page,
                                             is_hq=True,
                                             page_size=settings.ITEMS_PER_PAGE)
    total_camp = api.total_sms_campaign_hq(merchant_id, is_sms=True)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/sms_marketing.html',
                           user_login=user_login,
                           merchant=merchant,
                           list_camp=list_camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/sms_marketing/<shop_id_select>/<camp_id>',
           methods=['GET', 'POST'])
@login_required
def sms_marketing_camp_item(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/sms_marketing')
    if request.method == 'GET':
        camp = {}
        if 'sms' not in shop:
            shop['sms'] = {}
        if camp_id == 'add':
            camp = {'all_customers': 'on'}
        else:
            camp = api.get_sms_campaign_hq(merchant_id,
                                           camp_id,
                                           shop_id=shop_id_select)
        if 'sms' not in shop:
            shop['sms'] = {}
        coupons_type_select = gift_card_api.get_coupon_manual_type(
            merchant_id=merchant_id, shop_id=shop_id_select, all=True)
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]
        ghdc = api.check_ghdc(merchant_id)
        # if ghdc:
        #     list_career = []
        #     info_ghdc = api.check_ghdc(merchant_id)
        #     setting_ghdc = info_ghdc.get('setting')
        #     username = setting_ghdc.get('username')
        #     password = setting_ghdc.get('password')
        #     print "==================="
        #     print username
        #     print password
        #     token, org_id = api_ghdc.get_token(username, password)
        #     if token:
        #         list_career = api_ghdc.get_career(token)

        #     return render_template('nextify/sms_ghdc_marketing.html',
        #                         shop=shop,
        #                        user_login=user_login,
        #                        merchant=merchant,
        #                        shop_in_mer=shops,
        #                        shop_id_select=shop_id_select,
        #                        camp=camp,
        #                        tags=tags,
        #                        list_career=list_career,
        #                        shop_select=shop_select)
        return render_template('nextify/sms_marketing_item.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               shop_in_mer=shops,
                               shop_id_select=shop_id_select,
                               camp=camp,
                               tags=tags,
                               shop_select=shop_select)
    else:
        code_camp = request.form.get('code_camp').strip()
        desc_camp = request.form.get('desc_camp').strip()
        date_send = request.form.get('date_send')
        message = request.form.get('announcement').strip()
        if date_send and len(date_send) > 0:
            date_send = datetime.strptime(date_send, '%H:%M %d-%m-%Y')

        min_visit = request.form.get('min_visit').strip()
        max_visit = request.form.get('max_visit').strip()
        visit_from_date = request.form.get('visit_from_date')
        visit_to_date = request.form.get('visit_to_date')
        is_sms = True if request.form.get('is_sms') else False
        is_push_app = True if request.form.get('is_push_app') else False
        type_coupon = request.form.get('type_coupon')
        is_zalo = True if request.form.get('is_zalo') else False
        is_email = True if request.form.get('is_email') else False
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        ex_camp = request.form.get('ex_manual', '').strip()
        ranks = request.form.get('ranks', 'all')
        camp_id = request.form.get('camp_id')
        locations = request.form.get('camp_locations')
        lost_day = request.form.get('lost_day')
        shops_locations = []
        if locations and len(locations) > 0 and str(locations) != 'None':
            shops_locations = locations.split(',')
        visit_by = request.form.get('visit_by')
        camp_exist = ""
        if camp_id != "add":
            camp_exist = api.get_sms_campaign_hq(merchant_id, camp_id)
        is_spam = request.form.get('is_spam')
        code_fpt = ''
        real_tags_filter = request.form.get('real_tags_filter')
        tags_array = []
        if real_tags_filter and len(real_tags_filter) > 0 \
                and str(real_tags_filter) != 'None':
            tags_array = real_tags_filter.split(',')
            tags_array = [str(tag) for tag in tags_array]
        gender_filter = request.form.get('gender_filter')
        gender_array = []
        if isinstance(gender_filter, list):
            gender_array = gender_filter
        elif gender_filter and len(gender_filter) > 0 and str(
                gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]

        predict_message = request.form.get('predict_message')
        email_design = request.form.get('design')
        email_content = request.form.get('email_content')
        email_title = request.form.get('email_title')
        all_customers = request.form.get('all_customers')
        send_to_cus = request.form.get('send_to_cus')
        from_time = request.form.get('from_time', '')
        to_time = request.form.get('to_time', '')
        act_type = ''
        if camp_exist:
            api.update_sms_campaign_hq(merchant_id=merchant_id,
                                       message=message,
                                       shop_id=shop_id_select,
                                       camp_id=camp_id,
                                       code=code_camp,
                                       desc=desc_camp,
                                       gender=gender_array,
                                       from_date=from_date,
                                       to_date=to_date,
                                       type_coupon=type_coupon,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       visit_from_date=visit_from_date,
                                       all_customers=all_customers,
                                       visit_to_date=visit_to_date,
                                       is_sms=is_sms,
                                       is_push_app=is_push_app,
                                       is_email=is_email,
                                       is_zalo=is_zalo,
                                       expire_coupon=ex_camp,
                                       ranks=ranks,
                                       code_fpt=code_fpt,
                                       is_spam=is_spam,
                                       date_send=date_send,
                                       tags=tags_array,
                                       camp_locations=shops_locations,
                                       visit_by=visit_by,
                                       lost_day=lost_day,
                                       predict_message=predict_message,
                                       from_time=from_time,
                                       to_time=to_time)
            # act_type = 'update_campaign'
            # activity_history.save_activity(
            #     act_type, merchant_id, shop_id, code_camp=code_camp)

        else:
            camp_id = api.insert_sms_campaign_hq(
                merchant_id=merchant_id,
                shop_id=shop_id_select,
                message=message,
                code=code_camp,
                desc=desc_camp,
                gender=gender_array,
                all_customers=all_customers,
                from_date=from_date,
                to_date=to_date,
                type_coupon=type_coupon,
                min_visit=min_visit,
                max_visit=max_visit,
                visit_from_date=visit_from_date,
                visit_to_date=visit_to_date,
                is_sms=is_sms,
                is_email=is_email,
                predict_message=predict_message,
                is_push_app=is_push_app,
                is_zalo=is_zalo,
                expire_coupon=ex_camp,
                lost_day=lost_day,
                ranks=ranks,
                code_fpt=code_fpt,
                is_spam=is_spam,
                date_send=date_send,
                tags=tags_array,
                camp_locations=shops_locations,
                visit_by=visit_by,
                from_time=from_time,
                to_time=to_time)
            # act_type = 'insert_campaign'
            # activity_history.save_activity(
            #     act_type, merchant_id, shop_id, code_camp=code_camp)
        producer_data = {
            "shop_id": str(shop_id_select),
            "task_name": "count_predict_message_campaign_task",
            "params": {
                "merchant_id": str(merchant_id),
                "camp_id": str(camp_id),
                "shop_id": str(shop_id_select),
                "is_hq": True
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        api.update_shop_camp_status(shop_id_select, camp_id, 0)
        if send_to_cus and send_to_cus == '1' and date_send and len(
                str(date_send)) > 0:

            if date_send < datetime.now():
                return json.dumps({
                    'result':
                    "false",
                    'error':
                    "Ngày bắt đầu gửi phải lớn hơn ngày hiện tại"
                })
            date_send = timezone('Asia/Ho_Chi_Minh').localize(date_send)

            check_config = False
            sms_provider = merchant.get('sms_provider')
            user_sms = merchant.get('user_sms')
            pass_sms = merchant.get('pass_sms')
            brand_name = merchant.get('brand_name')
            if sms_provider and sms_provider.upper() == 'VHAT':
                VHAT_API_KEY = merchant.get('api_key_vhat')
                VHAT_SECRET_KEY = merchant.get('secret_key_vhat')
                VHAT_SMS_TYPE = merchant.get('sms_type')
                if message and len(message) > 0 and VHAT_API_KEY and len(VHAT_API_KEY) > 0 \
                        and VHAT_SECRET_KEY and len(VHAT_SECRET_KEY) > 0 and VHAT_SMS_TYPE and len(VHAT_SMS_TYPE) > 0:
                    check_config = True
            elif sms_provider and sms_provider.upper() == 'VINAPHONE':
                info_brand_name = merchant.get('brand_name_vina')
                LABELID = info_brand_name.get('vina_label_id')
                USERNAME = info_brand_name.get('vina_user_name')
                APIUSER = info_brand_name.get('vina_api_user')
                APIPASS = info_brand_name.get('vina_api_pass')
                APIURL = info_brand_name.get('vina_api_url')
                AGENTID = info_brand_name.get('vina_agent_id')
                CONTRACTID = info_brand_name.get('vina_contract_id')
                if message and len(message) > 0 and LABELID and len(LABELID) > 0 \
                        and USERNAME and len(USERNAME) > 0 and APIUSER and len(APIUSER) > 0 \
                        and APIPASS and len(APIPASS) > 0 and AGENTID and len(AGENTID) > 0 \
                        and CONTRACTID and len(CONTRACTID) > 0 and APIURL and len(APIURL) > 0:
                    check_config = True

            else:
                if message and len(message) > 0 and sms_provider and len(sms_provider) > 0 and user_sms \
                        and len(user_sms) > 0 and pass_sms and len(pass_sms) > 0 and brand_name and len(brand_name) > 0:
                    check_config = True

            if check_config:
                api.update_shop_camp_status(shop_id_select, camp_id, 1)
                camp = api.get_sms_campaign_hq(merchant_id,
                                               camp_id,
                                               shop_id=shop_id_select)
                if camp.get('status') == 1:
                    producer_data = {
                        "shop_id": str(shop_id_select),
                        "task_name": "send_sms_camp",
                        "params": {
                            "merchant_id": str(merchant_id),
                            "shop_id": str(shop_id_select),
                            "camp_id": str(camp_id),
                            "eta": str(date_send)
                        }
                    }

                    producer_data = json.dumps(producer_data).encode('utf-8')
                    producer.send(settings.cms_consumer, producer_data)
                    producer.flush()
                return json.dumps({
                    'result':
                    "true",
                    'message':
                    '/sms_marketing/%s' % shop_id_select
                })
            else:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext(
                        "Ban_chua_cau_hinh_SMS_Brandname._Vui_long_cau_hinh_SMS_Brandname_truoc."
                    )
                })

        return json.dumps({
            'result': "true",
            'message': '/sms_marketing/%s' % shop_id_select
        })


@app.route('/ghdc_sms_marketing/<shop_id_select>/<camp_id>',
           methods=['GET', 'POST'])
@login_required
def ghdc_sms_marketing(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if request.method == 'GET':
        camp = api.get_ghdc_camp(camp_id)
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        return render_template('nextify/sms_ghdc_marketing.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               shop_id_select=shop_id_select,
                               camp=camp,
                               tags=tags,
                               shop_select=shop_select)
    else:
        info_ghdc = api.check_ghdc(merchant_id)
        setting_ghdc = info_ghdc.get('setting')
        username = setting_ghdc.get('username')
        password = setting_ghdc.get('password')
        code_camp = request.form.get('code_camp').strip()
        visit_from_date = request.form.get('visit_from_date')
        visit_to_date = request.form.get('visit_to_date')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        min_visit = request.form.get('min_visit').strip()
        max_visit = request.form.get('max_visit').strip()
        lost_day = request.form.get('lost_day')
        all_customers = request.form.get('all_customers')
        message = request.form.get('announcement').strip()
        date_start_send = request.form.get('date_start_send')
        date_end_send = request.form.get('date_end_send')
        brandname = request.form.get('brandname')
        career = request.form.get('career')
        type_cskh = request.form.get('type_cskh')
        type_qc = request.form.get('type_qc')
        price = request.form.get('price')
        camp_id = request.form.get('camp_id')
        desc_camp = request.form.get('desc_camp').strip()
        predict_message = request.form.get('predict_message')
        camp_exist = ""
        if camp_id != "add":
            camp_exist = api.get_sms_campaign_hq(merchant_id, camp_id)
        real_tags_filter = request.form.get('real_tags_filter')
        tags_array = []
        if real_tags_filter and len(real_tags_filter) > 0 \
                and str(real_tags_filter) != 'None':
            tags_array = real_tags_filter.split(',')
            tags_array = [str(tag) for tag in tags_array]
        gender_filter = request.form.get('gender_filter')
        gender_array = []
        if isinstance(gender_filter, list):
            gender_array = gender_filter
        elif gender_filter and len(gender_filter) > 0 and str(
                gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]
        cp_type = 0
        if type_qc and str(type_qc) == "true":
            cp_type = 1
        mt_type = 2  # loai tin nhan Only SMS
        sending_time = '["08:00-12:00", "13:30-20:00"]'
        max_mt_per_day = 100
        max_mt_campaign = 100
        # goi api sang GHDC
        token, org_id = api_ghdc.get_token(username, password)
        if token:
            cp_id = api_ghdc.createcamp(token, org_id, code_camp,
                                        date_start_send, date_end_send,
                                        sending_time, date_end_send, brandname,
                                        cp_type, mt_type, max_mt_per_day,
                                        max_mt_campaign, desc_camp, career)
            if cp_id:
                temp_id = api_ghdc.create_tempSMS(token, cp_id, message,
                                                  cp_type, price, brandname)
                if temp_id:
                    result_phone = api_ghdc.add_phone_file_to_camp(
                        cp_id, token)
                else:
                    return json.dumps(
                        {'error': "Tạo template không thành công."})
                # luu chien dich
                if camp_id == "add":
                    type_sms = 'Only SMS'
                    api.insert_ghdc_campaign(merchant_id=merchant_id,
                                             shop_id=shop_id_select,
                                             type_sms=type_sms,
                                             name_camp=code_camp,
                                             visit_from_date=visit_from_date,
                                             visit_to_date=visit_to_date,
                                             from_date=from_date,
                                             to_date=to_date,
                                             min_visit=min_visit,
                                             max_visit=max_visit,
                                             lost_day=lost_day,
                                             all_customers=all_customers,
                                             message=message,
                                             date_start_send=date_start_send,
                                             date_end_send=date_end_send,
                                             brandname=brandname,
                                             career=career,
                                             type_cskh=type_cskh,
                                             type_qc=type_qc,
                                             price=price,
                                             desc_camp=desc_camp,
                                             predict_message=predict_message,
                                             tags_array=tags_array,
                                             gender_array=gender_array,
                                             cp_type=cp_type,
                                             mt_type=mt_type,
                                             sending_time=sending_time,
                                             max_mt_per_day=max_mt_per_day,
                                             max_mt_campaign=max_mt_campaign,
                                             cp_ghdc=cp_id,
                                             temp_ghdc=temp_id)
            else:
                return json.dumps(
                    {'error': "Tạo chiến dịch không thành công."})
        return json.dumps({'result': True})


@app.route('/zalo_marketing', methods=['GET'])
@login_required
def zalo_marketing():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    page = int(request.args.get('page', 1))

    list_camp = []
    total_camp = 0
    list_camp = api.get_list_sms_campaign_hq(merchant_id,
                                             is_zalo=True,
                                             page=page,
                                             is_hq=True,
                                             page_size=settings.ITEMS_PER_PAGE)
    total_camp = api.total_sms_campaign_hq(merchant_id, is_zalo=True)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/zalo_marketing.html',
                           user_login=user_login,
                           merchant=merchant,
                           list_camp=list_camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/zalo_marketing/<shop_id_select>', methods=['GET'])
@login_required
def zalo_marketing_locations(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    page = int(request.args.get('page', 1))
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/zalo_marketing')
    list_camp = api.get_list_sms_campaign_hq(merchant_id,
                                             is_zalo=True,
                                             shop_id=shop_id_select,
                                             page=page,
                                             is_hq=True,
                                             page_size=settings.ITEMS_PER_PAGE)
    total_camp = api.total_sms_campaign_hq(merchant_id,
                                           shop_id=shop_id_select,
                                           is_zalo=True)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/zalo_marketing.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           list_camp=list_camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/zalo_marketing/<shop_id_select>/<camp_id>',
           methods=['GET', 'POST'])
@login_required
def zalo_marketing_camp_item(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    check_token = api.check_token_zns(shop_id=shop_id_select)
    is_zns = None
    if not check_token:
        is_zns = False
    else:
        is_zns = True
    if not shop_select:
        return redirect('/zalo_marketing')
    if request.method == 'GET':
        camp = {}
        if 'sms' not in shop:
            shop['sms'] = {}
        if camp_id == 'add':
            camp = {'all_customers': 'on'}
        else:
            camp = api.get_sms_campaign_hq(merchant_id,
                                           camp_id,
                                           shop_id=shop_id_select)
        if 'sms' not in shop:
            shop['sms'] = {}
        coupons_type_select = gift_card_api.get_coupon_manual_type(
            merchant_id=merchant_id, shop_id=shop_id_select, all=True)
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]
        return render_template('nextify/zalo_marketing_item.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               shop_in_mer=shops,
                               shop_id_select=shop_id_select,
                               camp=camp,
                               tags=tags,
                               shop_select=shop_select,
                               is_zns=is_zns)
    else:
        code_camp = request.form.get('code_camp').strip()
        desc_camp = request.form.get('desc_camp').strip()
        date_send = request.form.get('date_send')
        message = request.form.get('announcement').strip()
        active_zns = request.form.get('active_zns')
        temp_id = request.form.get('temp_id')
        if date_send and len(date_send) > 0:
            date_send = datetime.strptime(date_send, '%H:%M %d-%m-%Y')

        min_visit = request.form.get('min_visit').strip()
        max_visit = request.form.get('max_visit').strip()
        visit_from_date = request.form.get('visit_from_date')
        visit_to_date = request.form.get('visit_to_date')
        is_sms = True if request.form.get('is_sms') else False
        is_push_app = True if request.form.get('is_push_app') else False
        type_coupon = request.form.get('type_coupon')
        is_zalo = True if request.form.get('is_zalo') else False
        is_email = True if request.form.get('is_email') else False
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        ex_camp = request.form.get('ex_manual', '').strip()
        ranks = request.form.get('ranks', 'all')
        camp_id = request.form.get('camp_id')
        locations = request.form.get('camp_locations')
        lost_day = request.form.get('lost_day')
        shops_locations = []
        if locations and len(locations) > 0 and str(locations) != 'None':
            shops_locations = locations.split(',')
        visit_by = request.form.get('visit_by')
        camp_exist = ""
        if camp_id != "add":
            camp_exist = api.get_sms_campaign_hq(merchant_id, camp_id)
        is_spam = request.form.get('is_spam')
        code_fpt = ''
        real_tags_filter = request.form.get('real_tags_filter')
        tags_array = []
        if real_tags_filter and len(real_tags_filter) > 0 \
                and str(real_tags_filter) != 'None':
            tags_array = real_tags_filter.split(',')
            tags_array = [str(tag) for tag in tags_array]
        gender_filter = request.form.get('gender_filter')
        gender_array = []
        if isinstance(gender_filter, list):
            gender_array = gender_filter
        elif gender_filter and len(gender_filter) > 0 and str(
                gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]

        predict_message = request.form.get('predict_message')
        email_design = request.form.get('design')
        email_content = request.form.get('email_content')
        email_title = request.form.get('email_title')
        all_customers = request.form.get('all_customers')
        send_to_cus = request.form.get('send_to_cus')
        from_time = request.form.get('from_time', '')
        to_time = request.form.get('to_time', '')
        active_zns = request.form.get('active_zns')
        act_type = ''
        image = request.files.get('logo')
        access_token = shop_select.get('zalo_access_token')
        image_filename = None
        att_id = None
        if image:
            if allowed_file(image.filename):
                image_filename = storage_api.save_new_file(image)
                file_data = image.stream.read()
                att_id = api.get_attachment_id_image_zalo(
                    access_token, file_data)
                if not att_id:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext("Co_loi_xay_ra,_xin_thu_lai_sau")
                    })
            else:
                error = gettext("Hay_chon_dung_dinh_dang_anh")
                return json.dumps({'result': False, 'msg': error})
        if camp_exist:
            api.update_sms_campaign_hq(merchant_id=merchant_id,
                                       message=message,
                                       shop_id=shop_id_select,
                                       camp_id=camp_id,
                                       code=code_camp,
                                       desc=desc_camp,
                                       gender=gender_array,
                                       from_date=from_date,
                                       to_date=to_date,
                                       type_coupon=type_coupon,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       visit_from_date=visit_from_date,
                                       all_customers=all_customers,
                                       visit_to_date=visit_to_date,
                                       is_sms=is_sms,
                                       is_push_app=is_push_app,
                                       is_email=is_email,
                                       is_zalo=is_zalo,
                                       expire_coupon=ex_camp,
                                       ranks=ranks,
                                       code_fpt=code_fpt,
                                       is_spam=is_spam,
                                       date_send=date_send,
                                       tags=tags_array,
                                       camp_locations=shops_locations,
                                       visit_by=visit_by,
                                       lost_day=lost_day,
                                       predict_message=predict_message,
                                       from_time=from_time,
                                       to_time=to_time,
                                       temp_id=temp_id,
                                       image=image_filename,
                                       attachment_id=att_id)

        else:
            camp_id = api.insert_sms_campaign_hq(
                merchant_id=merchant_id,
                shop_id=shop_id_select,
                message=message,
                code=code_camp,
                desc=desc_camp,
                gender=gender_array,
                all_customers=all_customers,
                from_date=from_date,
                to_date=to_date,
                type_coupon=type_coupon,
                min_visit=min_visit,
                max_visit=max_visit,
                visit_from_date=visit_from_date,
                visit_to_date=visit_to_date,
                is_sms=is_sms,
                is_email=is_email,
                predict_message=predict_message,
                is_push_app=is_push_app,
                is_zalo=is_zalo,
                expire_coupon=ex_camp,
                lost_day=lost_day,
                ranks=ranks,
                code_fpt=code_fpt,
                is_spam=is_spam,
                date_send=date_send,
                tags=tags_array,
                camp_locations=shops_locations,
                visit_by=visit_by,
                from_time=from_time,
                to_time=to_time,
                active_zns=active_zns,
                temp_id=temp_id,
                image=image_filename,
                attachment_id=att_id)
        api.update_shop_camp_status(shop_id_select, camp_id, 0)
        if send_to_cus and send_to_cus == '1' and date_send and len(
                str(date_send)) > 0:
            if date_send < datetime.now():
                return json.dumps({
                    'result':
                    "false",
                    'error':
                    "Ngày bắt đầu gửi phải lớn hơn ngày hiện tại"
                })
            date_send = timezone('Asia/Ho_Chi_Minh').localize(date_send)
            # gui qua zalo oa
            if active_zns == "off":
                access_token = shop_select.get('zalo_access_token')
                if not access_token:
                    return json.dumps({
                        'result':
                        "false",
                        'error':
                        gettext("Chua_cai_dat_cau_hinh_Zalo_OA")
                    })

                api.update_shop_camp_status(shop_id_select, camp_id, 1)
                camp = api.get_sms_campaign_hq(merchant_id,
                                               camp_id,
                                               shop_id=shop_id_select)
                if camp.get('status') == 1:
                    producer_data = {
                        "shop_id": str(shop_id_select),
                        "task_name": "send_zalo_oa_camp",
                        "params": {
                            "merchant_id": str(merchant_id),
                            "shop_id": str(shop_id_select),
                            "camp_id": str(camp_id),
                            "eta": str(date_send)
                        }
                    }

                    producer_data = json.dumps(producer_data).encode('utf-8')
                    producer.send(settings.cms_consumer, producer_data)
                    producer.flush()
                    sms_api.get_zalo_oa_data_camp(merchant_id, camp_id,
                                                  shop_id_select)
                    sms_api.send_zalo_oa_campaign(merchant_id, camp_id,
                                                  shop_id_select)
                return json.dumps({
                    'result':
                    "true",
                    'message':
                    '/zalo_marketing/%s' % shop_id_select
                })
            # gửi zns
            if active_zns == "on":
                api.update_shop_camp_status(shop_id_select, camp_id, 1)
                camp = api.get_sms_campaign_hq(merchant_id,
                                               camp_id,
                                               shop_id=shop_id_select)
                if camp.get('status') == 1:
                    producer_data = {
                        "shop_id": str(shop_id_select),
                        "task_name": "send_zns_camp",
                        "params": {
                            "merchant_id": str(merchant_id),
                            "shop_id": str(shop_id_select),
                            "camp_id": str(camp_id),
                            "eta": str(date_send)
                        }
                    }

                    producer_data = json.dumps(producer_data).encode('utf-8')
                    producer.send(settings.cms_consumer, producer_data)
                    producer.flush()

                return json.dumps({
                    'result':
                    "true",
                    'message':
                    '/zalo_marketing/%s' % shop_id_select
                })
        return json.dumps({
            'result': "true",
            'message': '/zalo_marketing/%s' % shop_id_select
        })


@app.route('/send_zalo_camp_test/<shop_id_select>', methods=['POST'])
@login_required
def send_zalo_camp_test(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)

    message = request.form.get('message')
    merchant_name = merchant.get('name')
    phone_number = request.form.get('phone_test')
    active_zns = request.form.get('active_zns')
    access_token = shop_select.get('zalo_access_token')
    temp_id = request.form.get('temp_id')
    image = request.files.get('logo')
    result = False
    if active_zns == "off":
        if message and len(message) > 0 and access_token and len(
                access_token) > 0:
            message = api.remove_accents(message)
            att_id = None
            if image:
                if allowed_file(image.filename):
                    file_data = image.stream.read()
                    att_id = api.get_attachment_id_image_zalo(
                        access_token, file_data)
            user_id_zalo = api.check_phone_follow_zaloOA(
                shop_id_select, str(phone_number))
            if not user_id_zalo:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    phone_number + " " + gettext(" chua_follow_Zalo_OA")
                })
            else:
                result = sms_api.send_sms_zalo_oa(access_token, message,
                                                  user_id_zalo, att_id)
            if result and str(result) == 'True':
                return json.dumps({'result': True})
            else:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext("Co_loi_xay_ra,_xin_thu_lai_sau")
                })
        else:
            return json.dumps({
                'result': False,
                'error': gettext("Chua_cai_dat_cau_hinh_Zalo_OA")
            })
    if active_zns == "on":
        check_config = api.check_token_zns(shop_id_select)
        if not check_config:
            return json.dumps({
                'result':
                False,
                'error':
                gettext("Ban_phai_dang_ky_dich_vu_zns,_xin_thu_lai_sau")
            })
        else:
            result = sms_api.send_zns(temp_id, access_token, 'bạn',
                                      phone_number)
            if result and str(result) == 'True':
                return json.dumps({'result': True})
            else:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext("Co_loi_xay_ra,_xin_thu_lai_sau")
                })


@app.route('/zalo_marketing/<shop_id_select>/<camp_id>/logs', methods=['GET'])
@login_required
def zalo_camp_logs(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)

    if not shop_select:
        return redirect('/email_marketing')
    page = int(request.args.get('page', 1))
    camp = api.get_sms_campaign_hq(merchant_id,
                                   camp_id,
                                   shop_id=shop_id_select)
    list_camp = email_api.list_email_logs(shop_id_select,
                                          camp_id,
                                          page=page,
                                          page_size=settings.ITEMS_PER_PAGE)
    total_camp = email_api.total_list_email_logs(shop_id_select, camp_id)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/zalo_camp_logs.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           list_camp=list_camp,
                           camp=camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/mms_marketing', methods=['GET'])
@login_required
def mms_marketing():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    page = int(request.args.get('page', 1))

    list_camp = []
    total_camp = 0
    list_camp = api.get_list_sms_campaign_hq(merchant_id,
                                             is_mms=True,
                                             page=page,
                                             is_hq=True,
                                             page_size=settings.ITEMS_PER_PAGE)
    total_camp = api.total_sms_campaign_hq(merchant_id, is_mms=True)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/mms_marketing.html',
                           user_login=user_login,
                           merchant=merchant,
                           list_camp=list_camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/mms_marketing/<shop_id_select>', methods=['GET'])
@login_required
def mms_marketing_locations(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    page = int(request.args.get('page', 1))
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/mms_marketing')
    list_camp = api.get_list_sms_campaign_hq(merchant_id,
                                             is_mms=True,
                                             shop_id=shop_id_select,
                                             page=page,
                                             is_hq=True,
                                             page_size=settings.ITEMS_PER_PAGE)
    total_camp = api.total_sms_campaign_hq(merchant_id,
                                           shop_id=shop_id_select,
                                           is_zalo=True)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/mms_marketing.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           list_camp=list_camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/mms_marketing/<shop_id_select>/<camp_id>',
           methods=['GET', 'POST'])
@login_required
def mms_marketing_camp_item(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    check_token = api.check_token_zns(shop_id=shop_id_select)

    if not shop_select:
        return redirect('/mms_marketing')
    if request.method == 'GET':
        camp = {}
        if 'sms' not in shop:
            shop['sms'] = {}
        if camp_id == 'add':
            camp = {'all_customers': 'on'}
        else:
            camp = api.get_sms_campaign_hq(merchant_id,
                                           camp_id,
                                           shop_id=shop_id_select)
        if 'sms' not in shop:
            shop['sms'] = {}
        coupons_type_select = gift_card_api.get_coupon_manual_type(
            merchant_id=merchant_id, shop_id=shop_id_select, all=True)
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]
        return render_template('nextify/mms_marketing_item.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               shop_in_mer=shops,
                               shop_id_select=shop_id_select,
                               camp=camp,
                               tags=tags,
                               shop_select=shop_select)
    else:
        info_ghdc = api.check_ghdc(merchant_id)
        setting_ghdc = info_ghdc.get('setting')
        username = setting_ghdc.get('username')
        password = setting_ghdc.get('password')
        code_camp = request.form.get('code_camp').strip()
        visit_from_date = request.form.get('visit_from_date')
        visit_to_date = request.form.get('visit_to_date')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        min_visit = request.form.get('min_visit').strip()
        max_visit = request.form.get('max_visit').strip()
        lost_day = request.form.get('lost_day')
        all_customers = request.form.get('all_customers')
        message = request.form.get('announcement').strip()
        date_start_send = request.form.get('date_start_send')
        date_end_send = request.form.get('date_end_send')
        brandname = request.form.get('brandname')
        career = request.form.get('career')
        type_cskh = request.form.get('type_cskh')
        type_qc = request.form.get('type_qc')
        price = request.form.get('price')
        camp_id = request.form.get('camp_id')
        desc_camp = request.form.get('desc_camp').strip()
        predict_message = request.form.get('predict_message')
        camp_exist = ""
        if camp_id != "add":
            camp_exist = api.get_sms_campaign_hq(merchant_id, camp_id)
        real_tags_filter = request.form.get('real_tags_filter')
        tags_array = []
        if real_tags_filter and len(real_tags_filter) > 0 \
                and str(real_tags_filter) != 'None':
            tags_array = real_tags_filter.split(',')
            tags_array = [str(tag) for tag in tags_array]
        gender_filter = request.form.get('gender_filter')
        gender_array = []
        if isinstance(gender_filter, list):
            gender_array = gender_filter
        elif gender_filter and len(gender_filter) > 0 and str(
                gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]
        cp_type = 0
        if type_qc and str(type_qc) == "true":
            cp_type = 1
        mt_type = 2  # loai tin nhan Only SMS
        sending_time = '["08:00-12:00", "13:30-20:00"]'
        max_mt_per_day = 100
        max_mt_campaign = 100
        # goi api sang GHDC
        token, org_id = api_ghdc.get_token(username, password)
        if token:
            cp_id = api_ghdc.createcamp(token, org_id, code_camp,
                                        date_start_send, date_end_send,
                                        sending_time, date_end_send, brandname,
                                        cp_type, mt_type, max_mt_per_day,
                                        max_mt_campaign, desc_camp, career)
            if cp_id:
                temp_id = api_ghdc.create_tempSMS(token, cp_id, message,
                                                  cp_type, price, brandname)
                if temp_id:
                    result_phone = api_ghdc.add_phone_file_to_camp(
                        cp_id, token)
                else:
                    return json.dumps(
                        {'error': "Tạo template không thành công."})
                # luu chien dich
                if camp_id == "add":
                    type_sms = 'Only SMS'
                    api.insert_ghdc_campaign(merchant_id=merchant_id,
                                             shop_id=shop_id_select,
                                             type_sms=type_sms,
                                             name_camp=code_camp,
                                             visit_from_date=visit_from_date,
                                             visit_to_date=visit_to_date,
                                             from_date=from_date,
                                             to_date=to_date,
                                             min_visit=min_visit,
                                             max_visit=max_visit,
                                             lost_day=lost_day,
                                             all_customers=all_customers,
                                             message=message,
                                             date_start_send=date_start_send,
                                             date_end_send=date_end_send,
                                             brandname=brandname,
                                             career=career,
                                             type_cskh=type_cskh,
                                             type_qc=type_qc,
                                             price=price,
                                             desc_camp=desc_camp,
                                             predict_message=predict_message,
                                             tags_array=tags_array,
                                             gender_array=gender_array,
                                             cp_type=cp_type,
                                             mt_type=mt_type,
                                             sending_time=sending_time,
                                             max_mt_per_day=max_mt_per_day,
                                             max_mt_campaign=max_mt_campaign,
                                             cp_ghdc=cp_id,
                                             temp_ghdc=temp_id)
            else:
                return json.dumps(
                    {'error': "Tạo chiến dịch không thành công."})
        return json.dumps({'result': True})


@app.route('/email_marketing', methods=['GET'])
@login_required
def email_marketing():
    user_login = g.user
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    merchant_name = merchant.get('name')
    print(merchant_id)
    page = int(request.args.get('page', 1))

    list_camp = api.get_list_sms_campaign_hq(merchant_id,
                                             is_email=True,
                                             page=page,
                                             page_size=settings.ITEMS_PER_PAGE)
    total_camp = api.total_sms_campaign_hq(merchant_id, is_email=True)

    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/email_marketing.html',
                           user_login=user_login,
                           merchant=merchant,
                           list_camp=list_camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/email_marketing/<shop_id_select>/<camp_id>',
           methods=['GET', 'POST'])
@login_required
def email_marketing_camp_item(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/email_marketing')
    if request.method == 'GET':
        camp = {}
        if 'sms' not in shop:
            shop['sms'] = {}
        if camp_id == 'add':
            camp = {'all_customers': 'on'}
        else:
            camp = api.get_sms_campaign_hq(merchant_id,
                                           camp_id,
                                           shop_id=shop_id_select)
        if 'sms' not in shop:
            shop['sms'] = {}
        coupons_type_select = gift_card_api.get_coupon_manual_type(
            merchant_id=merchant_id, shop_id=shop_id_select, all=True)
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]

        return render_template('nextify/email_marketing_item.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               shop_in_mer=shops,
                               shop_id_select=shop_id_select,
                               camp=camp,
                               tags=tags,
                               shop_select=shop_select)
    else:
        code_camp = request.form.get('code_camp').strip()
        desc_camp = request.form.get('desc_camp').strip()
        date_send = request.form.get('date_send')
        if date_send and len(date_send) > 0:
            date_send = datetime.strptime(date_send, '%H:%M %d-%m-%Y')
        min_visit = request.form.get('min_visit').strip()
        max_visit = request.form.get('max_visit').strip()
        visit_from_date = request.form.get('visit_from_date')
        visit_to_date = request.form.get('visit_to_date')
        is_sms = True if request.form.get('is_sms') else False
        is_push_app = True if request.form.get('is_push_app') else False
        type_coupon = request.form.get('type_coupon')
        is_zalo = True if request.form.get('is_zalo') else False
        is_email = True if request.form.get('is_email') else False
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        ex_camp = request.form.get('ex_manual', '').strip()
        ranks = request.form.get('ranks', 'all')
        camp_id = request.form.get('camp_id')
        locations = request.form.get('camp_locations')
        lost_day = request.form.get('lost_day')
        shops_locations = []
        if locations and len(locations) > 0 and str(locations) != 'None':
            shops_locations = locations.split(',')
        visit_by = request.form.get('visit_by')
        camp_exist = ""
        if camp_id != "add":
            camp_exist = api.get_sms_campaign_hq(merchant_id, camp_id)
        is_spam = request.form.get('is_spam')
        code_fpt = ''
        real_tags_filter = request.form.get('real_tags_filter')
        tags_array = []
        if real_tags_filter and len(real_tags_filter) > 0 \
                and str(real_tags_filter) != 'None':
            tags_array = real_tags_filter.split(',')
            tags_array = [str(tag) for tag in tags_array]
        gender_filter = request.form.get('gender_filter')
        gender_array = []
        if isinstance(gender_filter, list):
            gender_array = gender_filter
        elif gender_filter and len(gender_filter) > 0 and str(
                gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]

        predict_message = request.form.get('predict_message')
        email_design = request.form.get('design')
        email_content = request.form.get('email_content')
        email_title = request.form.get('email_title')
        all_customers = request.form.get('all_customers')
        send_to_cus = request.form.get('send_to_cus')
        from_time = request.form.get('from_time', '')
        to_time = request.form.get('to_time', '')
        act_type = ''
        if camp_exist:
            api.update_sms_campaign_hq(merchant_id=merchant_id,
                                       shop_id=shop_id_select,
                                       camp_id=camp_id,
                                       code=code_camp,
                                       desc=desc_camp,
                                       gender=gender_array,
                                       from_date=from_date,
                                       to_date=to_date,
                                       type_coupon=type_coupon,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       visit_from_date=visit_from_date,
                                       all_customers=all_customers,
                                       visit_to_date=visit_to_date,
                                       is_sms=is_sms,
                                       is_push_app=is_push_app,
                                       is_email=is_email,
                                       is_zalo=is_zalo,
                                       expire_coupon=ex_camp,
                                       ranks=ranks,
                                       code_fpt=code_fpt,
                                       is_spam=is_spam,
                                       date_send=date_send,
                                       tags=tags_array,
                                       camp_locations=shops_locations,
                                       visit_by=visit_by,
                                       email_design=email_design,
                                       email_content=email_content,
                                       lost_day=lost_day,
                                       predict_message=predict_message,
                                       email_title=email_title,
                                       from_time=from_time,
                                       to_time=to_time)
            # act_type = 'update_campaign'
            # activity_history.save_activity(
            #     act_type, merchant_id, shop_id, code_camp=code_camp)

        else:
            camp_id = api.insert_sms_campaign_hq(
                merchant_id=merchant_id,
                shop_id=shop_id_select,
                code=code_camp,
                desc=desc_camp,
                gender=gender_array,
                all_customers=all_customers,
                from_date=from_date,
                to_date=to_date,
                type_coupon=type_coupon,
                min_visit=min_visit,
                max_visit=max_visit,
                visit_from_date=visit_from_date,
                visit_to_date=visit_to_date,
                is_sms=is_sms,
                is_email=is_email,
                predict_message=predict_message,
                is_push_app=is_push_app,
                is_zalo=is_zalo,
                expire_coupon=ex_camp,
                lost_day=lost_day,
                ranks=ranks,
                code_fpt=code_fpt,
                is_spam=is_spam,
                date_send=date_send,
                tags=tags_array,
                camp_locations=shops_locations,
                visit_by=visit_by,
                email_design=email_design,
                email_content=email_content,
                email_title=email_title,
                from_time=from_time,
                to_time=to_time)
            # act_type = 'insert_campaign'
            # activity_history.save_activity(
            #     act_type, merchant_id, shop_id, code_camp=code_camp)
        producer_data = {
            "shop_id": str(shop_id_select),
            "task_name": "count_predict_message_campaign_task",
            "params": {
                "merchant_id": str(merchant_id),
                "shop_id": str(shop_id_select),
                "camp_id": str(camp_id),
                "is_hq": True
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        api.update_shop_camp_status(shop_id_select, camp_id, 0)
        if send_to_cus and send_to_cus == '1' and date_send and len(
                str(date_send)) > 0:
            if date_send < datetime.now():
                return json.dumps({
                    'result':
                    "false",
                    'error':
                    "Ngày bắt đầu gửi phải lớn hơn ngày hiện tại"
                })
            date_send = timezone('Asia/Ho_Chi_Minh').localize(date_send)
            mail_settings = merchant.get('mail_settings')
            if mail_settings:
                mail_name = mail_settings.get('mail_name')
                mail_user = mail_settings.get('mail_user')
                mail_pass = mail_settings.get('mail_pass')
                mail_server = mail_settings.get('mail_server')
                mail_port = mail_settings.get('mail_port')
                mail_ssl = mail_settings.get('mail_ssl')
                merchant_name = merchant.get('name')
                if mail_user and len(mail_user) > 0 and mail_pass and \
                        len(mail_pass) > 0 and mail_server and len(mail_server) > 0:
                    if 'nextify' in str(
                            mail_server) or 'mail_gun' in mail_server:
                        from_obj = '''%s <mailgun@%s>''' % (merchant_name,
                                                            mail_user)
                        r = requests.post(mail_server,
                                          auth=("api", mail_pass),
                                          data={
                                              "from":
                                              from_obj,
                                              "to": ['support@nextify.vn'],
                                              "subject":
                                              "Test email %s" % str(camp_id),
                                              "html":
                                              email_content
                                          })
                        if r.status_code == 200:
                            api.update_shop_camp_status(
                                shop_id_select, camp_id, 1)
                            camp = api.get_sms_campaign_hq(
                                merchant_id, camp_id, shop_id=shop_id_select)
                            if camp.get('status') == 1:
                                producer_data = {
                                    "shop_id": str(shop_id_select),
                                    "task_name": "send_email_camp",
                                    "params": {
                                        "merchant_id": str(merchant_id),
                                        "shop_id": str(shop_id_select),
                                        "camp_id": str(camp_id),
                                        "eta": str(date_send)
                                    }
                                }

                                producer_data = json.dumps(
                                    producer_data).encode('utf-8')
                                producer.send(settings.cms_consumer,
                                              producer_data)
                                producer.flush()
                            return json.dumps({
                                'result':
                                "true",
                                'message':
                                '/email_marketing/%s' % shop_id_select
                            })
                        else:
                            return json.dumps({
                                'result':
                                False,
                                'error':
                                'Không thành công, vui lòng kiểm tra lại cấu hình Email.'
                            })
                    elif 'sendgrid' in str(mail_server):
                        sg = sendgrid.SendGridAPIClient(api_key=mail_pass)
                        from_email = Email(mail_user)
                        to_email = To('support@nextify.vn')
                        subject = "Test email %s" % str(camp_id)
                        content = Content("text/html", email_content)
                        mail = Mail(from_email, to_email, subject, content)
                        try:
                            response = sg.client.mail.send.post(
                                request_body=mail.get())

                            if response.status_code == 202:
                                api.update_shop_camp_status(
                                    shop_id_select, camp_id, 1)
                                camp = api.get_sms_campaign_hq(
                                    merchant_id,
                                    camp_id,
                                    shop_id=shop_id_select)
                                if camp.get('status') == 1:
                                    producer_data = {
                                        "shop_id": str(shop_id_select),
                                        "task_name": "send_email_camp",
                                        "params": {
                                            "merchant_id": str(merchant_id),
                                            "shop_id": str(shop_id_select),
                                            "camp_id": str(camp_id),
                                            "eta": str(date_send)
                                        }
                                    }

                                    producer_data = json.dumps(
                                        producer_data).encode('utf-8')
                                    producer.send(settings.cms_consumer,
                                                  producer_data)
                                    producer.flush()
                                return json.dumps({
                                    'result':
                                    "true",
                                    'message':
                                    '/email_marketing/%s' % shop_id_select
                                })
                            else:
                                return json.dumps({
                                    'result':
                                    False,
                                    'error':
                                    gettext(
                                        "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                                    )
                                })

                        except Exception as e:
                            return json.dumps({
                                'result':
                                False,
                                'error':
                                gettext(
                                    "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                                )
                            })

                    else:
                        if mail_server == 'smtp.gmail.com':
                            mail_port = 587
                            try:
                                msg = email.message.Message()
                                msg['Subject'] = "Test email %s" % str(camp_id)
                                msg['From'] = mail_user
                                msg['To'] = 'support@nextify.vn'
                                msg.add_header('Content-Type', 'text/html')
                                msg.set_payload(email_content)

                                s = smtplib.SMTP(mail_server, int(mail_port))
                                s.ehlo()
                                s.starttls()
                                s.login(str(mail_user), str(mail_pass))
                                s.sendmail(mail_user, 'support@nextify.vn',
                                           msg.as_string())
                                s.close()
                                return json.dumps({
                                    'result':
                                    "true",
                                    'message':
                                    '/email_marketing/%s' % shop_id_select
                                })
                            except Exception as e:
                                return json.dumps({
                                    'result':
                                    False,
                                    'error':
                                    gettext(
                                        "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                                    )
                                })
                        else:
                            try:
                                msg = MIMEMultipart()
                                msg['From'] = mail_user
                                msg['To'] = ', '.join(['support@nextify.vn'])
                                msg['Subject'] = "Test email %s" % str(camp_id)
                                msg.add_header('Content-Type', 'text/html')
                                msg.set_payload(email_content)

                                server = smtplib.SMTP(mail_server,
                                                      int(mail_port))
                                server.ehlo()
                                server.starttls()
                                server.ehlo()
                                server.login(mail_user, mail_pass)
                                server.sendmail(mail_user,
                                                ['support@nextify.vn'],
                                                msg.as_string())
                                server.close()
                                api.update_shop_camp_status(
                                    shop_id_select, camp_id, 1)
                                camp = api.get_sms_campaign_hq(
                                    merchant_id,
                                    camp_id,
                                    shop_id=shop_id_select)
                                if camp.get('status') == 1:
                                    producer_data = {
                                        "shop_id": str(shop_id_select),
                                        "task_name": "send_email_camp",
                                        "params": {
                                            "merchant_id": str(merchant_id),
                                            "shop_id": str(shop_id_select),
                                            "camp_id": str(camp_id),
                                            "eta": date_send
                                        }
                                    }

                                    producer_data = json.dumps(
                                        producer_data).encode('utf-8')
                                    producer.send(settings.cms_consumer,
                                                  producer_data)
                                    producer.flush()

                                return json.dumps({
                                    'result':
                                    "true",
                                    'message':
                                    '/email_marketing/%s' % shop_id_select
                                })
                            except:
                                return json.dumps({
                                    'result':
                                    False,
                                    'error':
                                    gettext(
                                        "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                                    )
                                })
                else:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext(
                            "Ban_chua_cau_hinh_Email_Server._Vui_long_cau_hinh_Email_Server_truoc."
                        )
                    })
            else:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext(
                        "Ban_chua_cau_hinh_Email_Server._Vui_long_cau_hinh_Email_Server_truoc."
                    )
                })

        return json.dumps({
            'result': "true",
            'message': '/email_marketing/%s' % shop_id_select
        })


@app.route('/email_marketing/<shop_id_select>/<camp_id>/preview',
           methods=['GET'])
@login_required
def email_camp_preview(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)

    if not shop_select:
        return redirect('/email_marketing')
    camp = api.get_sms_campaign_hq(merchant_id,
                                   camp_id,
                                   shop_id=shop_id_select)
    camp_id = camp.get('_id')
    return render_template('nextify/email_camp_preview.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           camp=camp,
                           camp_id=camp_id)


@app.route('/email_marketing/<shop_id_select>/<camp_id>/preview_html',
           methods=['GET'])
def email_camp_preview_html(shop_id_select, camp_id):
    shop_select = api.get_shop_info(shop_id=shop_id_select)

    if not shop_select:
        return redirect('/email_marketing')
    merchant_id = shop_select.get('merchant_id')
    camp = api.get_sms_campaign_hq(merchant_id,
                                   camp_id,
                                   shop_id=shop_id_select)
    email_content = camp.get('email_content')
    email_title = camp.get('email_title')
    return email_content


@app.route('/email_marketing/<shop_id_select>/<camp_id>/logs', methods=['GET'])
@login_required
def email_camp_logs(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)

    if not shop_select:
        return redirect('/email_marketing')
    page = int(request.args.get('page', 1))
    camp = api.get_sms_campaign_hq(merchant_id,
                                   camp_id,
                                   shop_id=shop_id_select)
    list_camp = email_api.list_email_logs(shop_id_select,
                                          camp_id,
                                          page=page,
                                          page_size=settings.ITEMS_PER_PAGE)
    total_camp = email_api.total_list_email_logs(shop_id_select, camp_id)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/email_camp_logs.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           list_camp=list_camp,
                           camp=camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/sms_marketing/<shop_id_select>/<camp_id>/logs', methods=['GET'])
@login_required
def sms_camp_logs(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)

    if not shop_select:
        return redirect('/email_marketing')
    page = int(request.args.get('page', 1))
    camp = api.get_sms_campaign_hq(merchant_id,
                                   camp_id,
                                   shop_id=shop_id_select)
    list_camp = email_api.list_email_logs(shop_id_select,
                                          camp_id,
                                          page=page,
                                          page_size=settings.ITEMS_PER_PAGE)
    total_camp = email_api.total_list_email_logs(shop_id_select, camp_id)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/sms_camp_logs.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           shop_in_mer=shops,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           list_camp=list_camp,
                           camp=camp,
                           total_camp=total_camp,
                           pagination=pagination)


@app.route('/send_sms_test/<shop_id_select>', methods=['POST'])
@login_required
def send_sms_test(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)

    message = request.form.get('message')
    merchant_name = merchant.get('name')
    phone_number = request.form.get('phone_test')
    sms_provider = merchant.get('sms_provider')
    user_sms = merchant.get('user_sms')
    pass_sms = merchant.get('pass_sms')
    brand_name = merchant.get('brand_name')
    result = False
    if message and len(message) > 0 and sms_provider and len(sms_provider) > 0:
        message = api.remove_accents(message)
        if sms_provider.upper() == 'VINAPHONE':
            result = sms_api.send_sms_vinaphone(merchant_id,
                                                phone_number,
                                                message,
                                                activity_id=None,
                                                camp_id=None)
        else:
            if user_sms and len(user_sms) > 0 and pass_sms and len(
                    pass_sms) > 0 and brand_name and len(brand_name) > 0:
                if sms_provider.upper() == 'BLUESEA':
                    result = sms_api.send_sms_bluesea(merchant_id, user_sms,
                                                      pass_sms, brand_name,
                                                      phone_number, message)

                elif sms_provider.upper() == 'VHT':
                    result = sms_api.send_sms_vht(merchant_id,
                                                  user_sms,
                                                  pass_sms,
                                                  brand_name,
                                                  phone_number,
                                                  message,
                                                  activity_id=None,
                                                  camp_id=None)
                elif sms_provider.upper() == 'VHAT':
                    VHAT_API_KEY = merchant.get('api_key_vhat')
                    VHAT_SECRET_KEY = merchant.get('secret_key_vhat')
                    VHAT_SMS_TYPE = merchant.get('sms_type')
                    if VHAT_API_KEY and len(
                            VHAT_API_KEY) > 0 and VHAT_SECRET_KEY and len(
                                VHAT_SECRET_KEY) > 0:
                        result = sms_api.send_sms_vhat(merchant_id,
                                                       VHAT_API_KEY,
                                                       VHAT_SECRET_KEY,
                                                       VHAT_SMS_TYPE,
                                                       brand_name,
                                                       phone_number,
                                                       message,
                                                       activity_id=None,
                                                       camp_id=None)
                    else:
                        result = False
                elif sms_provider.upper() == 'VIETTEL':
                    result = sms_api.send_sms_viettel(merchant_id,
                                                      user_sms,
                                                      pass_sms,
                                                      brand_name,
                                                      phone_number,
                                                      message,
                                                      activity_id=None,
                                                      camp_id=None)
                elif sms_provider.upper() == 'FPT':
                    result = sms_api.send_sms_fpt_gateway(merchant_id,
                                                          user_sms,
                                                          pass_sms,
                                                          phone_number,
                                                          brand_name,
                                                          'send_brandname_otp',
                                                          message,
                                                          activity_id=None,
                                                          camp_id=None)
                elif sms_provider.upper() == 'MOBIFONE':
                    result = sms_api.send_sms_mobi(merchant_id,
                                                   user_sms,
                                                   pass_sms,
                                                   brand_name,
                                                   phone_number,
                                                   message,
                                                   activity_id=None,
                                                   camp_id=None)
                elif sms_provider.upper() == 'VIETGUY':
                    result = sms_api.send_sms_vietguy(merchant_id,
                                                      user_sms,
                                                      pass_sms,
                                                      brand_name,
                                                      phone_number,
                                                      message,
                                                      activity_id=None,
                                                      camp_id=None)
                else:
                    result = False

        if result and str(result) == 'True':
            return json.dumps({'result': True})
        else:
            return json.dumps({
                'result':
                False,
                'error':
                gettext(
                    "Khong_thanh_cong._Cau_hinh_SMS_Brandname_chua_chinh_xac.")
            })
    else:
        return json.dumps({
            'result':
            False,
            'error':
            gettext(
                "Ban_chua_cau_hinh_SMS_Brandname._Vui_long_cau_hinh_SMS_Brandname_truoc."
            )
        })


@app.route('/send_email_test/<shop_id_select>', methods=['POST'])
@login_required
def send_email_test(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)
    mail_settings = merchant.get('mail_settings')
    subject = request.form.get('subject')
    email_test = request.form.get('email')
    email_content = request.form.get('email_content')
    merchant_name = merchant.get('name')
    if mail_settings:
        mail_name = mail_settings.get('mail_name')
        mail_user = mail_settings.get('mail_user')
        email_test = request.form.get('email')
        mail_pass = mail_settings.get('mail_pass')
        mail_server = mail_settings.get('mail_server')
        mail_port = mail_settings.get('mail_port')
        mail_ssl = mail_settings.get('mail_ssl')

        if mail_user and len(mail_user) > 0 and mail_pass and \
                len(mail_pass) > 0 and mail_server and len(mail_server) > 0:

            if 'nextify' in str(mail_server) or 'mail_gun' in mail_server:
                from_obj = '''%s <mailgun@%s>''' % (merchant_name, mail_user)
                r = requests.post(mail_server,
                                  auth=("api", mail_pass),
                                  data={
                                      "from": from_obj,
                                      "to": [email_test],
                                      "subject": subject,
                                      "html": email_content
                                  })
                if r.status_code == 200:
                    return json.dumps({'result': True})
                else:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext(
                            "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                        )
                    })
            elif 'sendgrid' in str(mail_server):
                sg = sendgrid.SendGridAPIClient(api_key=mail_pass)
                from_email = Email(mail_user)
                to_email = To(email_test)
                subject = subject
                content = Content("text/html", email_content)
                mail = Mail(from_email, to_email, subject, content)
                try:
                    response = sg.client.mail.send.post(
                        request_body=mail.get())
                    if response.status_code == 202:
                        return json.dumps({'result': True})
                    else:
                        return json.dumps({
                            'result':
                            False,
                            'error':
                            gettext(
                                "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                            )
                        })
                except Exception as e:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext(
                            "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                        )
                    })
            else:
                if 'gmail' in mail_server:
                    mail_port = 587
                    try:
                        msg = email.message.Message()
                        msg['Subject'] = subject
                        msg['From'] = mail_user
                        msg['To'] = email_test
                        msg.add_header('Content-Type', 'text/html')
                        msg.set_payload(email_content)
                        s = smtplib.SMTP(mail_server, int(mail_port))
                        s.ehlo()
                        s.starttls()
                        s.login(str(mail_user), str(mail_pass))
                        s.sendmail(mail_user, email_test, msg.as_string())
                        s.close()
                        return json.dumps({'result': True})
                    except Exception as e:
                        print(e)
                        return json.dumps({
                            'result':
                            False,
                            'error':
                            gettext(
                                "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                            )
                        })
                else:
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = mail_user
                        msg['To'] = ', '.join([email_test])
                        msg['Subject'] = subject
                        msg.add_header('Content-Type', 'text/html')
                        msg.set_payload(email_content)

                        server = smtplib.SMTP(mail_server, int(mail_port))
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.login(mail_user, mail_pass)
                        server.sendmail(mail_user, [email_test],
                                        msg.as_string())
                        server.close()

                        return json.dumps({'result': True})
                    except Exception as e:
                        print(e)
                        return json.dumps({
                            'result':
                            False,
                            'error':
                            gettext(
                                "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                            )
                        })

        else:
            return json.dumps({
                'result':
                False,
                'error':
                gettext(
                    "Ban_chua_cau_hinh_Email_Server._Vui_long_cau_hinh_Email_Server_truoc."
                )
            })
    else:
        return json.dumps({
            'result':
            False,
            'error':
            gettext(
                "Ban_chua_cau_hinh_Email_Server._Vui_long_cau_hinh_Email_Server_truoc."
            )
        })


@app.route('/marketing_campaign', methods=['GET'])
@login_required
def marketing_campaign():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    page = int(request.args.get('page', 1))
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    merchant = api.get_merchant(merchant_id)
    sms_provider = merchant.get('sms_provider')
    is_hq = True
    list_camp = api.get_list_sms_campaign_hq(merchant_id,
                                             shop_id,
                                             page,
                                             is_hq=True,
                                             page_size=settings.ITEMS_PER_PAGE)
    total_camp = api.total_sms_campaign_hq(merchant_id)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/marketing_campaign.html',
                           shop_in_mer=shop_in_mer,
                           total_camp=total_camp,
                           shop=shop,
                           list_camp=list_camp,
                           user_login=user_login,
                           sms_provider=sms_provider,
                           is_hq=is_hq,
                           page=page,
                           pagination=pagination,
                           merchant=merchant)


@app.route('/marketing_campaign/<shop_id_select>', methods=['GET'])
@login_required
def marketing_campaign_shop(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    page = int(request.args.get('page', 1))
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    merchant = api.get_merchant(merchant_id)
    sms_provider = merchant.get('sms_provider')
    is_hq = True
    if shop_id_select == 'all':
        return redirect('/marketing_campaign')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    total_camp = api.total_sms_campaign_hq(shop_id_select)
    pagination = Pagination(page=page,
                            total=total_camp,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/marketing_campaign_shop.html',
                           shop_in_mer=shop_in_mer,
                           shop=shop,
                           user_login=user_login,
                           sms_provider=sms_provider,
                           is_hq=is_hq,
                           page=page,
                           pagination=pagination,
                           merchant=merchant,
                           shop_select=shop_select,
                           shop_id_select=shop_id_select)


@app.route('/get_sms_marketing/<shop_id_select>', methods=['GET'])
@login_required
def get_sms_announcement(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    sms_provider = merchant.get('sms_provider')
    user_sms = merchant.get('user_sms')
    pass_sms = merchant.get('pass_sms')
    brand_name = merchant.get('brand_name')
    page = int(request.args.get('page', 1))
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shops = []
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    list_camp = api.get_list_sms_campaign(shop_id_select,
                                          page,
                                          page_size=settings.ITEMS_PER_PAGE)

    return render_template('nextify/get_sms_campaign_shop.html',
                           merchant_id=merchant_id,
                           shop=shop,
                           list_camp=list_camp,
                           user_login=user_login,
                           merchant=merchant,
                           sms_provider=sms_provider,
                           user_sms=user_sms,
                           pass_sms=pass_sms,
                           brand_name=brand_name,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select)


@app.route('/marketing_campaign/detail/<camp_id>', methods=['GET', 'POST'])
@login_required
def sms_campaign_item_hq(camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    if not merchant_id or merchant_id == '0':
        return redirect(url_for('sms_campaign_item', camp_id=camp_id))
    merchant = api.get_merchant(merchant_id)
    sms_provider = merchant.get('sms_provider')

    camp = {}
    if 'sms' not in shop:
        shop['sms'] = {}
    if camp_id == 'add':
        camp = {}
    else:
        camp = api.get_sms_campaign_hq(merchant_id, camp_id)
    coupons_type_select = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    shop_id_select = 'all'
    loyal_settings = shop.get('loyal_settings')
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    if request.method == 'GET':
        return render_template('nextify/sms_campaign_item_hq.html',
                               shop=shop,
                               camp=camp,
                               camp_id=camp_id,
                               user_login=user_login,
                               merchant_id=merchant_id,
                               merchant=merchant,
                               coupons_type_select=coupons_type_select,
                               tags=tags,
                               shop_in_mer=shop_in_mer,
                               shop_id_select=shop_id_select)
    else:
        code_camp = request.form.get('code_camp').strip()
        desc_camp = request.form.get('desc_camp').strip()
        message = request.form.get('announcement').strip()
        date_send = request.form.get('date_send')
        if date_send and len(date_send) > 0:
            date_send = datetime.strptime(date_send, '%H:%M %d-%m-%Y')
        min_visit = request.form.get('min_visit').strip()
        max_visit = request.form.get('max_visit').strip()
        visit_from_date = request.form.get('visit_from_date')
        visit_to_date = request.form.get('visit_to_date')
        is_sms = True if request.form.get('is_sms') else False
        is_push_app = True if request.form.get('is_push_app') else False
        type_coupon = request.form.get('type_coupon')
        is_zalo = True if request.form.get('is_zalo') else False
        is_email = True if request.form.get('is_email') else False
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        ex_camp = request.form.get('ex_manual', '').strip()
        ranks = request.form.get('ranks', 'all')
        camp_id = request.form.get('camp_id')
        locations = request.form.get('camp_locations')
        lost_day = request.form.get('lost_day')
        shops_locations = []
        if locations and len(locations) > 0 and str(locations) != 'None':
            shops_locations = locations.split(',')
        visit_by = request.form.get('visit_by')
        camp_exist = ""
        if camp_id != "add":
            camp_exist = api.get_sms_campaign_hq(merchant_id, camp_id)
        is_spam = request.form.get('is_spam')
        code_fpt = ''
        real_tags_filter = request.form.get('real_tags_filter')
        tags_array = []
        if real_tags_filter and len(real_tags_filter) > 0 \
                and str(real_tags_filter) != 'None':
            tags_array = real_tags_filter.split(',')
            tags_array = [str(tag) for tag in tags_array]
        gender_filter = request.form.get('gender_filter')
        gender_array = []
        if isinstance(gender_filter, list):
            gender_array = gender_filter
        elif gender_filter and len(gender_filter) > 0 and str(
                gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]
        gender_male = request.form.get('gender_male')
        gender_female = request.form.get('gender_female')
        gender_other = request.form.get('gender_other')
        if gender_male:
            gender_array.append(gender_male)
        if gender_female:
            gender_array.append(gender_female)
        if gender_other:
            gender_array.append(gender_other)
        predict_message = request.form.get('predict_message')
        email_design = request.form.get('design')
        email_content = request.form.get('email_content')
        email_title = request.form.get('email_title')
        all_customers = request.form.get('all_customers')
        act_type = ''
        if camp_exist:
            api.update_sms_campaign_hq(merchant_id=merchant_id,
                                       camp_id=camp_id,
                                       code=code_camp,
                                       desc=desc_camp,
                                       message=message,
                                       gender=gender_array,
                                       from_date=from_date,
                                       to_date=to_date,
                                       type_coupon=type_coupon,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       visit_from_date=visit_from_date,
                                       all_customers=all_customers,
                                       visit_to_date=visit_to_date,
                                       is_sms=is_sms,
                                       is_push_app=is_push_app,
                                       is_email=is_email,
                                       is_zalo=is_zalo,
                                       expire_coupon=ex_camp,
                                       ranks=ranks,
                                       code_fpt=code_fpt,
                                       is_spam=is_spam,
                                       date_send=date_send,
                                       tags=tags_array,
                                       camp_locations=shops_locations,
                                       visit_by=visit_by,
                                       email_design=email_design,
                                       email_content=email_content,
                                       lost_day=lost_day,
                                       predict_message=predict_message,
                                       email_title=email_title)
            # act_type = 'update_campaign'
            # activity_history.save_activity(
            #     act_type, merchant_id, shop_id, code_camp=code_camp)

        else:
            camp_id = api.insert_sms_campaign_hq(
                merchant_id=merchant_id,
                code=code_camp,
                desc=desc_camp,
                message=message,
                gender=gender_array,
                all_customers=all_customers,
                from_date=from_date,
                to_date=to_date,
                type_coupon=type_coupon,
                min_visit=min_visit,
                max_visit=max_visit,
                visit_from_date=visit_from_date,
                visit_to_date=visit_to_date,
                is_sms=is_sms,
                is_email=is_email,
                predict_message=predict_message,
                is_push_app=is_push_app,
                is_zalo=is_zalo,
                expire_coupon=ex_camp,
                lost_day=lost_day,
                ranks=ranks,
                code_fpt=code_fpt,
                is_spam=is_spam,
                date_send=date_send,
                tags=tags_array,
                camp_locations=shops_locations,
                visit_by=visit_by,
                email_design=email_design,
                email_content=email_content,
                email_title=email_title)
            # act_type = 'insert_campaign'
            # activity_history.save_activity(
            #     act_type, merchant_id, shop_id, code_camp=code_camp)
        producer_data = {
            "shop_id": str(shop_id),
            "task_name": "count_predict_message_campaign_task",
            "params": {
                "merchant_id": str(merchant_id),
                "shop_id": str(shop_id),
                "camp_id": str(camp_id),
                "is_hq": True
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        api.update_sms_camp_status(str(merchant_id), camp_id, '0')
        return json.dumps({'result': "true", 'message': '/marketing_campaign'})


@app.route('/marketing_campaign/detail/<camp_id>/remove',
           methods=['GET', 'POST'])
@login_required
def remove_sms_campaign_item_hq(camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    camp = api.get_sms_campaign_hq(merchant_id, camp_id)
    if camp:
        api.remove_sms_campaign_hq(merchant_id, camp_id)
    return json.dumps({"result": "True"})


@app.route('/marketing_campaign/detail/<camp_id>/active',
           methods=['GET', 'POST'])
@login_required
def active_sms_campaign_item_hq(camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    camp = api.get_sms_campaign_hq(merchant_id, camp_id)
    if camp:
        api.register_sms_campaign_hq(merchant_id, camp_id)
    return json.dumps({"result": "True"})


@app.route('/sms_marketing_hq/<camp_id>/fpt_campaign', methods=['GET'])
@login_required
def fpt_register_campaign(camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    user_sms = merchant.get('user_sms')
    pass_sms = merchant.get('pass_sms')
    brand_name = merchant.get('brand_name')
    camp = api.get_sms_campaign_hq(str(merchant_id), camp_id)
    if not camp:
        camp = api.get_sms_campaign(shop_id, camp_id)
    if camp:
        schedule_time = camp.get('date_send', '')
        if user_sms and pass_sms and brand_name and schedule_time and \
                len(schedule_time) > 0:
            producer_data = {
                "shop_id": str(shop_id),
                "task_name": "register_fpt_campaign_task",
                "params": {
                    "merchant_id": str(merchant_id),
                    "shop_id": str(shop_id),
                    "camp_id": str(camp_id),
                    "user_sms": user_sms,
                    "pass_sms": pass_sms,
                    "code": camp.get('code'),
                    "brand_name": brand_name,
                    "message": camp.get('message'),
                    "schedule_time": schedule_time,
                    "predict_message": camp.get('predict_message')
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()

    return redirect('/marketing_campaign')


@app.route('/sms_marketing/<camp_id>/fpt_campaign', methods=['GET'])
@login_required
def fpt_register_campaign_shop(camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    user_sms = merchant.get('user_sms')
    pass_sms = merchant.get('pass_sms')
    brand_name = merchant.get('brand_name')
    camp = api.get_sms_campaign(shop_id, camp_id)
    if camp:

        schedule_time = camp.get('date_send', '')
        if user_sms and pass_sms and brand_name and schedule_time and \
                len(schedule_time) > 0:
            producer_data = {
                "shop_id": str(shop_id),
                "task_name": "register_fpt_campaign_task",
                "params": {
                    "merchant_id": str(merchant_id),
                    "shop_id": str(shop_id),
                    "camp_id": str(camp_id),
                    "user_sms": user_sms,
                    "pass_sms": pass_sms,
                    "code": camp.get('code'),
                    "brand_name": brand_name,
                    "message": camp.get('message'),
                    "schedule_time": schedule_time,
                    "predict_message": camp.get('predict_message')
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()
    return redirect('/sms_marketing')


@app.route('/marketing_campaign/<shop_id_select>/detail/<camp_id>',
           methods=['GET', 'POST'])
@login_required
def sms_campaign_item(shop_id_select, camp_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    camp = {}
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/marketing_campaign')
    coupons_type_select = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop_id_select, all=True)
    if camp_id == 'add':
        camp = {}
    else:
        camp = api.get_sms_campaign(shop_id_select, camp_id)

    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    if request.method == 'GET':
        return render_template('nextify/sms_campaign_item.html',
                               shop=shop,
                               camp=camp,
                               camp_id=camp_id,
                               user_login=user_login,
                               coupons_type_select=coupons_type_select,
                               merchant=merchant,
                               tags=tags,
                               shop_id_select=shop_id_select,
                               shop_select=shop_select,
                               shop_in_mer=shop_in_mer)
    else:
        code_camp = request.form.get('code_camp').strip()
        desc_camp = request.form.get('desc_camp').strip()
        message = request.form.get('announcement').strip()
        date_send = request.form.get('date_send')

        min_visit = request.form.get('min_visit').strip()
        max_visit = request.form.get('max_visit').strip()
        visit_from_date = request.form.get('visit_from_date')
        visit_to_date = request.form.get('visit_to_date')
        gender_filter = request.form.get('gender_filter')
        gender_array = []
        if gender_filter and len(gender_filter) > 0 \
                and str(gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]
        type_coupon = request.form.get('type_coupon')
        is_zalo = True if request.form.get('is_zalo') else False
        is_sms = True if request.form.get('is_sms') else False
        is_push_app = True if request.form.get('is_push_app') else False
        is_email = True if request.form.get('is_email') else False
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        ranks = request.form.get('ranks', 'all')
        ex_camp = request.form.get('ex_manual').strip()
        is_spam = request.form.get('is_spam')
        camp_id = request.form.get('camp_id')
        camp_exist = api.get_sms_campaign(shop_id, camp_id)
        real_tags_filter = request.form.get('real_tags_filter')
        tags_array = []
        if real_tags_filter and len(real_tags_filter) > 0 \
                and str(real_tags_filter) != 'None':
            tags_array = real_tags_filter.split(',')
            tags_array = [str(tag) for tag in tags_array]
        act_type = ''
        if camp_exist:
            api.update_sms_campaign(shop_id_select,
                                    camp_id,
                                    code=code_camp,
                                    desc=desc_camp,
                                    message=message,
                                    gender=gender_array,
                                    from_date=from_date,
                                    to_date=to_date,
                                    type_coupon=type_coupon,
                                    min_visit=min_visit,
                                    max_visit=max_visit,
                                    visit_from_date=visit_from_date,
                                    visit_to_date=visit_to_date,
                                    is_sms=is_sms,
                                    is_push_app=is_push_app,
                                    is_email=is_email,
                                    is_zalo=is_zalo,
                                    expire_coupon=ex_camp,
                                    ranks=ranks,
                                    is_spam=is_spam,
                                    date_send=date_send,
                                    tags=tags_array)
            act_type = 'update_campaign'
            activity_history.save_activity(act_type,
                                           merchant_id,
                                           shop_id,
                                           code_camp=code_camp)
        else:
            camp_id = api.insert_sms_campaign(shop_id_select,
                                              code=code_camp,
                                              desc=desc_camp,
                                              message=message,
                                              gender=gender_array,
                                              from_date=from_date,
                                              to_date=to_date,
                                              type_coupon=type_coupon,
                                              min_visit=min_visit,
                                              max_visit=max_visit,
                                              visit_from_date=visit_from_date,
                                              visit_to_date=visit_to_date,
                                              is_sms=is_sms,
                                              is_push_app=is_push_app,
                                              is_email=is_email,
                                              is_zalo=is_zalo,
                                              expire_coupon=ex_camp,
                                              ranks=ranks,
                                              is_spam=is_spam,
                                              date_send=date_send,
                                              tags=tags_array)
            act_type = 'insert_campaign'
            # activity_history.save_activity(
            #     act_type, merchant_id, shop_id, code_camp=code_camp)

            producer_data = {
                "shop_id": str(shop_id_select),
                "task_name": "count_predict_message_campaign_task",
                "params": {
                    "merchant_id": str(merchant_id),
                    "shop_id": str(shop_id_select),
                    "camp_id": str(camp_id),
                    "is_hq": False,
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()
        api.update_sms_camp_fb_status(shop_id_select, camp_id, '0')
        return redirect(
            url_for('marketing_campaign_shop', shop_id_select=shop_id_select))


@app.route('/<slug>', methods=['GET', 'POST'])
def hq_shops(slug):
    merchant = api.get_merchant_by_slug(slug)
    if not merchant:
        return abort(404)
    merchant_id = merchant.get('_id')
    if request.method == 'GET':
        session.pop('is_login', None)
        session.pop('is_superuser', None)
        session.pop('shop_id', None)
        session.pop('is_hq', None)
        return render_template("nextify/login.html",
                               merchant_id=merchant_id,
                               merchant=merchant)
    else:
        phone = request.form.get('phone')
        password = request.form.get('password')
        if not phone or not password or len(phone) == 0 or len(password) == 0:
            error = gettext("Thong_tin_dang_nhap_khong_dung.")
            return render_template("nextify/login.html",
                                   error=error,
                                   merchant_id=merchant_id,
                                   merchant=merchant)
        is_email_merchant = validate_email(phone)

        if not is_email_merchant:
            merchant_phone = api.get_merchant_by_phone(phone)

            if merchant_phone:
                merchant_phone_id = merchant_phone.get('_id')
                if str(merchant_id) == str(merchant_phone_id):
                    sign_in = api.hq_sign_in_by_phone_acc(
                        merchant_id, phone, password)
                    if sign_in:
                        session['is_login'] = phone
                        session['is_hq'] = phone
                        shop_in_mer = api.get_shop_by_merchant(
                            str(merchant['_id']))
                        shop_ids = [shop['_id'] for shop in shop_in_mer]
                        g.shops = [api.get_shop_info(i) for i in shop_ids]
                        g.merchant = merchant
                        g.role = '3'
                        session['is_superuser'] = phone
                        if len(shop_ids) > 0:
                            return redirect('/home')
                        else:
                            return redirect(url_for('setup_first_login'))
                    else:
                        error = gettext("Thong_tin_dang_nhap_khong_dung.")
                        return render_template("nextify/login.html",
                                               error=error,
                                               merchant_id=merchant_id,
                                               merchant=merchant)
                else:
                    is_email = validate_email(phone)
                    user = api.sign_in_by_account_email(str(merchant_id), phone, password) if is_email else \
                        api.sign_in_by_account_phone(
                            str(merchant_id), phone, password)

                    if user:
                        role = user.get('roles')
                        if role == '3':
                            session['is_login'] = phone
                            session['is_hq'] = None
                            session['merchant_id'] = str(merchant['_id'])
                            session['is_superuser'] = None
                            shop_in_mer = api.get_shop_by_merchant(
                                str(merchant['_id']))
                            shop_ids = [shop['_id'] for shop in shop_in_mer]
                            g.shops = [api.get_shop_info(i) for i in shop_ids]
                            g.merchant = merchant
                            g.role = role
                            session['is_superuser'] = phone

                            if len(shop_ids) > 0:
                                return redirect('/home')
                            else:
                                return redirect(url_for('setup_first_login'))
                        else:
                            if role == '1':
                                session['is_login'] = phone
                                session['is_hq'] = None
                                session['merchant_id'] = str(merchant['_id'])
                                session['is_superuser'] = None
                                shop_in_mer = api.get_shop_by_merchant(
                                    str(merchant['_id']))
                                shop_ids = [
                                    shop['_id'] for shop in shop_in_mer
                                ]
                                if len(shop_ids) > 0:
                                    session['shop_id'] = str(shop_ids[0])
                                    g.shops = [
                                        api.get_shop_info(i) for i in shop_ids
                                    ]
                                    g.merchant = merchant
                                    g.role = role
                                    locations = user.get('shops', [])
                                    if len(locations) > 0:
                                        g.locations = locations
                                        return redirect(
                                            '/customers?loc_id=%s' %
                                            (str(locations[0])))
                                    else:
                                        error = gettext(
                                            "Thong_tin_dang_nhap_khong_dung.")
                                        return render_template(
                                            "nextify/login.html",
                                            error=error,
                                            merchant_id=merchant_id,
                                            merchant=merchant)
                                else:
                                    error = gettext(
                                        "Thong_tin_dang_nhap_khong_dung.")
                                    return render_template(
                                        "nextify/login.html",
                                        error=error,
                                        merchant_id=merchant_id,
                                        merchant=merchant)
                            elif role == '2':
                                session['is_login'] = phone
                                session['is_hq'] = None
                                session['merchant_id'] = str(merchant['_id'])
                                session['is_superuser'] = None
                                shop_in_mer = api.get_shop_by_merchant(
                                    str(merchant['_id']))
                                shop_ids = [
                                    shop['_id'] for shop in shop_in_mer
                                ]
                                if len(shop_ids) > 0:
                                    session['shop_id'] = str(shop_ids[0])
                                    g.shops = [
                                        api.get_shop_info(i) for i in shop_ids
                                    ]
                                    g.merchant = merchant
                                    g.role = role
                                    g.locations = shop_ids
                                    return redirect('/coupons')
                                else:
                                    error = gettext(
                                        "Thong_tin_dang_nhap_khong_dung.")
                                    return render_template(
                                        "nextify/login.html",
                                        error=error,
                                        merchant_id=merchant_id,
                                        merchant=merchant)
                            else:
                                # Marketingcoupons
                                session['is_login'] = phone
                                session['is_hq'] = None
                                session['merchant_id'] = str(merchant['_id'])
                                session['is_superuser'] = None
                                shop_in_mer = api.get_shop_by_merchant(
                                    str(merchant['_id']))
                                shop_ids = [
                                    shop['_id'] for shop in shop_in_mer
                                ]
                                g.locations = shop_ids
                                if len(shop_ids) > 0:
                                    session['shop_id'] = str(shop_ids[0])
                                    g.shops = [
                                        api.get_shop_info(i) for i in shop_ids
                                    ]
                                    g.merchant = merchant
                                    g.role = role
                                    return redirect('/hotspot/%s' %
                                                    (str(locations[0])))
                                else:
                                    error = gettext(
                                        "Thong_tin_dang_nhap_khong_dung.")
                                    return render_template(
                                        "nextify/login.html",
                                        error=error,
                                        merchant_id=merchant_id,
                                        merchant=merchant)
                    else:
                        error = gettext("Thong_tin_dang_nhap_khong_dung.")
                        return render_template("nextify/login.html",
                                               error=error,
                                               merchant_id=merchant_id,
                                               merchant=merchant)
            else:
                is_email = validate_email(phone)
                user = api.sign_in_by_account_email(str(merchant_id), phone, password) if is_email else \
                    api.sign_in_by_account_phone(
                        str(merchant_id), phone, password)
                if user:
                    role = user.get('roles')
                    if role == '3':
                        session['is_login'] = phone
                        session['is_hq'] = None
                        session['merchant_id'] = str(merchant['_id'])
                        shop_in_mer = api.get_shop_by_merchant(
                            str(merchant['_id']))
                        shop_ids = [shop['_id'] for shop in shop_in_mer]
                        g.shops = [api.get_shop_info(i) for i in shop_ids]
                        g.merchant = merchant
                        g.role = role
                        session['is_superuser'] = phone

                        if len(shop_ids) > 0:
                            return redirect('/home')
                        else:
                            return redirect(url_for('setup_first_login'))
                    else:
                        if role == '1':
                            session['is_login'] = phone
                            session['is_hq'] = None
                            session['merchant_id'] = str(merchant['_id'])
                            session['is_superuser'] = None
                            shop_in_mer = api.get_shop_by_merchant(
                                str(merchant['_id']))
                            shop_ids = [shop['_id'] for shop in shop_in_mer]
                            if len(shop_ids) > 0:
                                session['shop_id'] = str(shop_ids[0])
                                g.shops = [
                                    api.get_shop_info(i) for i in shop_ids
                                ]
                                g.merchant = merchant
                                g.role = role
                                locations = user.get('shops', [])
                                if len(locations) > 0:
                                    g.locations = locations
                                    return redirect('/customers?loc_id=%s' %
                                                    (str(locations[0])))
                                else:
                                    error = gettext(
                                        "Thong_tin_dang_nhap_khong_dung.")
                                    return render_template(
                                        "nextify/login.html",
                                        error=error,
                                        merchant_id=merchant_id,
                                        merchant=merchant)
                            else:
                                error = gettext(
                                    "Thong_tin_dang_nhap_khong_dung.")
                                return render_template("nextify/login.html",
                                                       error=error,
                                                       merchant_id=merchant_id,
                                                       merchant=merchant)
                        elif role == '2':
                            session['is_login'] = phone
                            session['is_hq'] = None
                            session['merchant_id'] = str(merchant['_id'])
                            session['is_superuser'] = None
                            shop_in_mer = api.get_shop_by_merchant(
                                str(merchant['_id']))
                            shop_ids = [shop['_id'] for shop in shop_in_mer]
                            if len(shop_ids) > 0:
                                session['shop_id'] = str(shop_ids[0])
                                g.shops = [
                                    api.get_shop_info(i) for i in shop_ids
                                ]
                                g.merchant = merchant
                                g.role = role
                                g.locations = shop_ids
                                return redirect('/coupons')
                            else:
                                error = gettext(
                                    "Thong_tin_dang_nhap_khong_dung.")
                                return render_template("nextify/login.html",
                                                       error=error,
                                                       merchant_id=merchant_id,
                                                       merchant=merchant)
                        else:
                            # Marketingcoupons
                            session['is_login'] = phone
                            session['is_hq'] = None
                            session['merchant_id'] = str(merchant['_id'])
                            session['is_superuser'] = None
                            shop_in_mer = api.get_shop_by_merchant(
                                str(merchant['_id']))
                            shop_ids = [shop['_id'] for shop in shop_in_mer]
                            g.locations = shop_ids
                            if len(shop_ids) > 0:
                                session['shop_id'] = str(shop_ids[0])
                                g.shops = [
                                    api.get_shop_info(i) for i in shop_ids
                                ]
                                g.merchant = merchant
                                g.role = role
                                return redirect('/hotspot/%s' %
                                                (str(shop_ids[0])))
                            else:
                                error = gettext(
                                    "Thong_tin_dang_nhap_khong_dung.")
                                return render_template("nextify/login.html",
                                                       error=error,
                                                       merchant_id=merchant_id,
                                                       merchant=merchant)
                else:
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("nextify/login.html",
                                           error=error,
                                           merchant_id=merchant_id,
                                           merchant=merchant)
        else:
            merchant_email = api.get_merchant_by_email(phone)
            if merchant_email:
                merchant_email_id = merchant_email.get('_id')
                if str(merchant_id) == str(merchant_email_id):
                    sign_in = api.hq_sign_in_by_email(merchant_id, phone,
                                                      password)
                    if sign_in:
                        session['is_login'] = phone
                        session['is_hq'] = phone
                        session['merchant_id'] = str(merchant['_id'])
                        shop_in_mer = api.get_shop_by_merchant(
                            str(merchant['_id']))
                        shop_ids = [shop['_id'] for shop in shop_in_mer]
                        g.shops = [api.get_shop_info(i) for i in shop_ids]
                        g.merchant = merchant
                        g.role = '3'
                        session['is_superuser'] = phone
                        if len(shop_ids) > 0:
                            return redirect('/home')
                        else:
                            return redirect(url_for('setup_first_login'))
                    else:
                        error = gettext("Thong_tin_dang_nhap_khong_dung.")
                        return render_template("nextify/login.html",
                                               error=error,
                                               merchant_id=merchant_id,
                                               merchant=merchant)
                else:
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("nextify/login.html",
                                           error=error,
                                           merchant_id=merchant_id,
                                           merchant=merchant)
            else:
                is_email = validate_email(phone)
                user = api.sign_in_by_account_email(str(merchant_id), phone, password) if is_email else \
                    api.sign_in_by_account_phone(
                        str(merchant_id), phone, password)
                if user:
                    role = user.get('roles')
                    if role == '3':
                        session['is_login'] = phone
                        session['is_hq'] = phone
                        session['merchant_id'] = str(merchant['_id'])
                        shop_in_mer = api.get_shop_by_merchant(
                            str(merchant['_id']))
                        shop_ids = [shop['_id'] for shop in shop_in_mer]
                        g.shops = [api.get_shop_info(i) for i in shop_ids]
                        g.merchant = merchant
                        g.role = role
                        g.locations = shop_ids
                        session['is_superuser'] = phone
                        if len(shop_ids) > 0:
                            return redirect('/home')
                        else:
                            return redirect(url_for('setup_first_login'))
                    else:
                        if role == '1':
                            session['is_login'] = phone
                            session['is_hq'] = None
                            session['merchant_id'] = str(merchant['_id'])
                            session['is_superuser'] = None
                            shop_in_mer = api.get_shop_by_merchant(
                                str(merchant['_id']))
                            shop_ids = [shop['_id'] for shop in shop_in_mer]
                            if len(shop_ids) > 0:
                                session['shop_id'] = str(shop_ids[0])
                                g.shops = [
                                    api.get_shop_info(i) for i in shop_ids
                                ]
                                g.merchant = merchant
                                g.role = role
                                locations = user.get('shops', [])
                                if len(locations) > 0:
                                    g.locations = locations
                                    return redirect('/customers?loc_id=%s' %
                                                    (str(locations[0])))
                                else:
                                    error = gettext(
                                        "Thong_tin_dang_nhap_khong_dung.")
                                    return render_template(
                                        "nextify/login.html",
                                        error=error,
                                        merchant_id=merchant_id,
                                        merchant=merchant)
                            else:
                                error = gettext(
                                    "Thong_tin_dang_nhap_khong_dung.")
                                return render_template("nextify/login.html",
                                                       error=error,
                                                       merchant_id=merchant_id,
                                                       merchant=merchant)
                        elif role == '2':
                            session['is_login'] = phone
                            session['is_hq'] = None
                            session['merchant_id'] = str(merchant['_id'])
                            session['is_superuser'] = None
                            shop_in_mer = api.get_shop_by_merchant(
                                str(merchant['_id']))
                            shop_ids = [shop['_id'] for shop in shop_in_mer]
                            g.locations = shop_ids
                            if len(shop_ids) > 0:
                                session['shop_id'] = str(shop_ids[0])
                                g.shops = [
                                    api.get_shop_info(i) for i in shop_ids
                                ]
                                g.merchant = merchant
                                g.role = role
                                return redirect('/coupons')
                            else:
                                error = gettext(
                                    "Thong_tin_dang_nhap_khong_dung.")
                                return render_template("nextify/login.html",
                                                       error=error,
                                                       merchant_id=merchant_id,
                                                       merchant=merchant)

                        else:
                            # Marketingcoupons
                            session['is_login'] = phone
                            session['is_hq'] = None
                            session['merchant_id'] = str(merchant['_id'])
                            session['is_superuser'] = None
                            shop_in_mer = api.get_shop_by_merchant(
                                str(merchant['_id']))
                            shop_ids = [shop['_id'] for shop in shop_in_mer]
                            g.locations = shop_ids
                            if len(shop_ids) > 0:
                                session['shop_id'] = str(shop_ids[0])
                                g.shops = [
                                    api.get_shop_info(i) for i in shop_ids
                                ]
                                g.merchant = merchant
                                g.role = role
                                return redirect('/hotspot/%s' %
                                                (str(locations[0])))
                            else:
                                error = gettext(
                                    "Thong_tin_dang_nhap_khong_dung.")
                                return render_template("nextify/login.html",
                                                       error=error,
                                                       merchant_id=merchant_id,
                                                       merchant=merchant)
                else:
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("nextify/login.html",
                                           error=error,
                                           merchant_id=merchant_id,
                                           merchant=merchant)


@app.route('/locations', methods=['GET'])
@login_required
def locations_settings():
    shop = g.shop
    user_login = g.user
    shop_id = shop.get('_id')
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    shop_in_mer = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if len(shops) > 0:
        return render_template('nextify/wifi_locations.html',
                               shop=shop,
                               shop_id=shop_id,
                               user_login=user_login,
                               shops=shops,
                               shop_in_mer=shop_in_mer,
                               locations=shops,
                               merchant=merchant)
    else:
        return redirect(url_for('setup_first_login'))


@app.route('/ads_banner', methods=['GET', 'POST'])
@login_required
def ads_banner():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')

    if request.method == 'GET':

        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]
        # shop_in_mer = api.get_shop_by_merchant(merchant_id)
        shop_id_select = request.args.get('shop_id_select', '')
        if not shop_id_select or len(shop_id_select) == 0:
            shop_id_select = shops[0]['_id']

        return redirect('/ads_banner/%s' % (shop_id_select))


@app.route('/ads_banner/<loc_id>', methods=['GET'])
@login_required
def ads_banner_log(loc_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop.get('_id')
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    shop_in_mer = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    shop_select = api.get_shop_info(shop_id=loc_id)
    page = 1
    logs = api.list_ads_banner_log(loc_id, page)
    total = api.total_ads_banner_log(loc_id)
    total_banner_1 = api.total_ads_banner_banner(loc_id, '1')
    total_banner_2 = api.total_ads_banner_banner(loc_id, '2')
    pagination = Pagination(page=page,
                            total=total,
                            per_page=5,
                            css_framework='bootstrap3')

    return render_template('nextify/ads_banner_detail.html',
                           shop=shop,
                           shop_id=shop_id,
                           user_login=user_login,
                           shops=shops,
                           shop_in_mer=shop_in_mer,
                           total=total,
                           logs=logs,
                           merchant=merchant,
                           pagination=pagination,
                           shop_select=shop_select,
                           total_banner_1=total_banner_1,
                           total_banner_2=total_banner_2)


@app.route('/locations/<location_id>', methods=['GET', 'POST'])
@login_required
def location_item(location_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop.get('_id')
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shops = []
    page_in_mer = api.get_pagefb_by_merchant(merchant_id)
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    shop_select = api.get_shop_info(shop_id=location_id)
    if request.method == 'GET':
        return render_template('nextify/location.html',
                               shop=shop,
                               shop_id=shop_id,
                               user_login=user_login,
                               dealer_id=dealer_id,
                               shops=shops,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               page_in_mer=page_in_mer,
                               shop_select=shop_select)
    else:
        app.logger.debug(request.form)
        app.logger.debug(request.files)

        name = request.form.get('name')
        hotline = request.form.get('hotline')
        address = request.form.get('address')
        address_lat = request.form.get('lat')
        address_long = request.form.get('long')
        email = request.form.get('email')
        website = request.form.get('website')
        is_sms = request.form.get('is_sms')
        sms_count = request.form.get('sms_count')
        facebook_page = request.form.get('facebook_page')
        page_id = request.form.get('page_id')
        zalo_oa_id = request.form.get('zalo_oa_id')
        zalo_app_id = request.form.get('zalo_app_id')
        zalo_access_token = request.form.get('zalo_access_token')
        type_pos = request.form.get('type_pos')
        place_id = request.form.get('place_id')
        company_id_anvui = request.form.get('company_id_anvui')
        id_page = request.form.get('page_fb')
        access_token_page = ""

        def error_locations(error):
            return render_template('nextify/location.html',
                                   shop=shop,
                                   shop_id=shop_id,
                                   user_login=user_login,
                                   dealer_id=dealer_id,
                                   shops=shops,
                                   shop_in_mer=shop_in_mer,
                                   merchant=merchant,
                                   shop_select=shop_select,
                                   page_in_mer=page_in_mer,
                                   error=error)

        if id_page and id_page != "all":
            check_double = api.check_double_fb(id_page=id_page,
                                               shop_id_select=location_id)
            if not check_double:
                error = gettext(
                    "Page_Facebook_nay_da_duoc_chon_cho_mot_dia_diem_khac._Ban_hay_chon_mot_trang_khac."
                )
                return error_locations(error)
            access_token_page = api.get_access_token_page(id_page)
            if access_token_page:
                api.facebook_lead_ad(page_id=id_page,
                                     access_token_page=access_token_page)
        is_sms = True if is_sms else False
        if not sms_count:
            sms_count = 0
        gateway_mac = None
        geolocation = None
        act_type = ''

        if place_id:
            check_double = api.check_double_fb(place_id=place_id,
                                               shop_id_select=location_id)
            if not check_double:
                error = gettext(
                    "Dia_diem_tren_google_nay_da_duoc_chon_cho_mot_dia_diem_khac._Ban_hay_chon_mot_dia_diem_khac_tren_google."
                )
                return error_locations(error)
        if not name or len(name) == 0:
            error = gettext("Ten_cua_hang_khong_duoc_de_trong")
            return error_locations(error)

        if hotline and len(hotline) > 0:
            if not api.get_phone_number(hotline) or not \
                    all([x.isdigit() for x in hotline]):
                error = gettext("So_dien_thoai_chua_dung_dinh_dang")
                return error_locations(error)

        logo_filename = background_filename = None
        logo = request.files.get('logo')
        if logo:
            if allowed_file(logo.filename):
                logo_filename = storage_api.save_new_file(logo)
            else:
                error = gettext("Hay_chon_dung_dinh_dang_anh")
                return error_locations(error)

        background = request.files.get('background')
        if background:
            if allowed_file(background.filename):
                background_filename = storage_api.save_new_file(background)
            else:
                error = gettext("Hay_chon_dung_dinh_dang_anh")
                return error_locations(error)

        api.update_shop(location_id,
                        name,
                        logo=logo_filename,
                        background=background_filename,
                        hotline=hotline,
                        address=address,
                        email=email,
                        website=website,
                        is_sms=is_sms,
                        sms_count=sms_count,
                        facebook_page=facebook_page,
                        page_id=page_id,
                        address_lat=address_lat,
                        address_long=address_long,
                        zalo_oa_id=zalo_oa_id,
                        zalo_app_id=zalo_app_id,
                        zalo_access_token=zalo_access_token,
                        merchant_id=merchant_id,
                        company_id_anvui=company_id_anvui,
                        id_page=id_page,
                        place_id=place_id,
                        access_token_page=access_token_page,
                        type_pos=type_pos)
        # act_type = 'update_location'
        # activity_history.save_activity(
        #     act_type, merchant_id, shop_id, location_name=name)

        shop_select = api.get_shop_info(shop_id=location_id)
        access_token = shop_select.get('zalo_access_token')
        zalo_oa_id = shop_select.get('zalo_oa_id')
        zalo_app_id = shop_select.get('zalo_app_id')
        if access_token and len(access_token) > 0 and zalo_oa_id \
                and len(zalo_oa_id) > 0 and zalo_app_id and len(zalo_app_id) > 0:
            producer_data = {
                "shop_id": str(location_id),
                "task_name": "sync_zalo_user",
                "params": {
                    "shop_id": str(location_id)
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()

        return render_template('nextify/location.html',
                               shop=shop,
                               shop_id=shop_id,
                               user_login=user_login,
                               merchant_id=merchant_id,
                               message='✓ ' + gettext("Da_luu_thong_tin"),
                               shops=shops,
                               shop_in_mer=shop_in_mer,
                               page_in_mer=page_in_mer,
                               id_page=id_page,
                               merchant=merchant,
                               shop_select=shop_select)


@app.route('/<slug>/login', methods=['GET', 'POST'])
def hq_login(slug):
    if request.method == 'GET':
        merchant = api.get_merchant_by_slug(slug)
        if not merchant:
            return abort(404)
        session.pop('is_login', None)
        session.pop('is_hq', None)
        session.pop('is_superuser', None)
        session.pop('shop_id', None)
        session.pop('customers_filter', None)
        session.pop('merchant_id', None)
        g.shops = None
        g.merchant = None
        g.user = None
        return render_template('nextify/login.html', slug=slug)
    else:
        phone = request.form.get("phone")
        password = request.form.get("password")
        merchant = api.get_merchant_by_slug(slug)
        if not merchant:
            return abort(404)
        merchant_id = merchant.get('_id')
        if len(phone) > 0 and len(password) > 0:
            phone = phone.strip()
            is_email = validate_email(phone)
            is_slug = api.validate_slug(phone)
            is_sale = api.ICO_person(phone, password, str(merchant_id))
            is_merchant_acc = api.get_merchant_by_email(phone) if is_email \
                else api.get_merchant_by_phone(phone)
            language = request.form.get('language')
            if not language:
                language = 'vn'
            session['lang'] = language

            if is_merchant_acc and str(
                    is_merchant_acc.get('_id')) == str(merchant_id):
                if is_email:
                    merchant = api.get_merchant_by_email(phone)
                    if merchant:
                        sign_in = api.hq_sign_in_by_email(
                            merchant_id, phone, password)
                    else:
                        error = gettext("Thong_tin_dang_nhap_khong_dung.")
                        return render_template("nextify/login.html",
                                               error=error)

                elif is_slug:
                    merchant = api.get_merchant_by_slug(phone)
                    if merchant:
                        sign_in = api.hq_sign_in_by_slug(
                            merchant_id, phone, password)
                    else:
                        error = gettext("Thong_tin_dang_nhap_khong_dung.")
                        return render_template("nextify/login.html",
                                               error=error)
                else:
                    merchant = api.get_merchant_by_phone(phone)
                    if merchant:
                        sign_in = api.hq_sign_in_by_phone_acc(
                            merchant_id, phone, password)
                    else:
                        error = gettext("Thong_tin_dang_nhap_khong_dung.")
                        return render_template("nextify/login.html",
                                               error=error)

                if merchant and sign_in:
                    session['shop_id'] = None
                    session['is_login'] = phone
                    session['is_hq'] = phone
                    shop_in_mer = api.get_shop_by_merchant(str(
                        merchant['_id']))
                    shop_ids = [shop['_id'] for shop in shop_in_mer]
                    g.shops = [api.get_shop_info(i) for i in shop_ids]
                    g.merchant = merchant
                    session['is_superuser'] = phone
                    session['merchant_id'] = str(merchant_id)
                    if len(shop_ids) > 0:
                        return redirect(url_for('index'))
                    else:
                        return redirect(url_for('setup_first_login'))

                else:
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("nextify/login.html", error=error)
            elif is_sale:
                session['shop_id'] = None
                session['is_login'] = merchant.get('phone')
                session['is_hq'] = merchant.get('phone')
                shop_in_mer = api.get_shop_by_merchant(str(merchant['_id']))
                shop_ids = [shop['_id'] for shop in shop_in_mer]
                g.shops = [api.get_shop_info(i) for i in shop_ids]
                g.merchant = merchant
                session['is_superuser'] = merchant.get('phone')
                session['merchant_id'] = str(merchant_id)
                if len(shop_ids) > 0:
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('setup_first_login'))
            else:
                account = api.get_account_merchant_email(str(merchant_id),
                                                         phone) if is_email \
                    else api.get_account_merchant_phone(str(merchant_id),
                                                        phone)
                if account:

                    sign_in = api.sign_in_staff_by_email(str(merchant_id),
                                                         phone,
                                                         password) if \
                        is_email else api.sign_in_staff_by_phone(str(
                            merchant_id), phone, password)
                    if sign_in:
                        account_id = account.get('_id')
                        session['is_login'] = phone
                        session['shop_id'] = None
                        session.pop('is_hq', None)
                        shop_in_mer = api.get_shop_by_merchant(
                            str(merchant['_id']))
                        shop_ids = [shop['_id'] for shop in shop_in_mer]
                        g.shops = [api.get_shop_info(i) for i in shop_ids]
                        g.merchant = merchant
                        session['is_superuser'] = phone
                        session['merchant_id'] = str(merchant['_id'])
                        if get_roles_user_merchant(account_id,
                                                   str(merchant['_id'])) \
                                in ['1', '3', '6']:
                            return redirect('/customers')
                        elif get_roles_user_merchant(
                                account_id, str(merchant['_id'])) in ['2']:
                            return redirect('/coupons')
                        elif get_roles_user_merchant(
                                account_id, str(merchant['_id'])) in ['4']:
                            return redirect('/marketing')
                        elif get_roles_user_merchant(
                                account_id, str(merchant['_id'])) in ['5']:
                            return redirect('/orders')
                        else:
                            session.pop('is_login', None)
                            session.pop('is_hq', None)
                            session.pop('is_superuser', None)
                            session.pop('shop_id', None)
                            session.pop('customers_filter', None)
                            g.shops = None
                            g.merchant = None
                            g.user = None
                            error = gettext("Thong_tin_dang_nhap_khong_dung.")
                            return render_template("dang_nhap.html",
                                                   error=error,
                                                   slug=slug)
                    else:
                        session.pop('is_login', None)
                        session.pop('is_hq', None)
                        session.pop('is_superuser', None)
                        session.pop('shop_id', None)
                        session.pop('customers_filter', None)
                        g.shops = None
                        g.merchant = None
                        g.user = None
                        error = gettext("Thong_tin_dang_nhap_khong_dung.")
                        return render_template("nextify/login.html",
                                               error=error)
                else:
                    session.pop('is_login', None)
                    session.pop('is_hq', None)
                    session.pop('is_superuser', None)
                    session.pop('shop_id', None)
                    session.pop('customers_filter', None)
                    g.shops = None
                    g.merchant = None
                    g.user = None
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("nextify/login.html", error=error)
        else:
            session.pop('is_login', None)
            session.pop('is_hq', None)
            session.pop('is_superuser', None)
            session.pop('shop_id', None)
            session.pop('customers_filter', None)
            g.shops = None
            g.merchant = None
            g.user = None
            error = gettext("Thong_tin_dang_nhap_khong_dung.")
            return render_template("nextify/login.html", error=error)


@app.route('/shops/<slug>/login', methods=['GET', 'POST'])
def dang_nhap(slug):
    if request.method == 'GET':
        session.pop('is_login', None)
        session.pop('shop_id', None)
        session.pop('customers_filter', None)
        return render_template("dang_nhap.html", slug=slug)
    else:
        phone = request.form.get("phone")
        password = request.form.get("password")
        slug = request.form.get('slug')
        if len(phone) > 0 and len(password) > 0:
            shop_info = api.get_shop_by_slug(slug)
            phone = phone.strip()
            if not shop_info:
                error = gettext("Thong_tin_dang_nhap_khong_dung.")
                return render_template("dang_nhap.html",
                                       error=error,
                                       slug=slug)
            sign_in = api.sign_in_by_phone(shop_info['_id'], phone, password)
            if sign_in:
                session['is_login'] = phone
                session['shop_id'] = str(shop_info['_id'])
                if get_roles_user(phone, shop_info['_id']) in ['1', '3', '6']:
                    return redirect('/customers')
                elif get_roles_user(phone, shop_info['_id']) in ['2']:
                    return redirect('/coupons')
                elif get_roles_user(phone, shop_info['_id']) in ['4']:
                    return redirect('/marketing')
                elif get_roles_user(phone, shop_info['_id']) in ['5']:
                    return redirect('/orders')
                else:
                    session.pop('is_login', None)
                    session.pop('shop_id', None)
                    error = gettext("Thong_tin_dang_nhap_khong_dung.")
                    return render_template("dang_nhap.html",
                                           error=error,
                                           slug=slug)
            else:
                session.pop('is_login', None)
                session.pop('shop_id', None)
                error = gettext("Thong_tin_dang_nhap_khong_dung.")
                return render_template("dang_nhap.html",
                                       error=error,
                                       slug=slug)
        else:
            session.pop('is_login', None)
            session.pop('shop_id', None)
            error = gettext("Ban_chua_nhap_tai_khoan.")
            return render_template("dang_nhap.html", error=error, slug=slug)


@app.route('/search', methods=['POST'])
@login_required
def search():
    app.logger.debug(session)
    app.logger.debug(request.form)

    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user

    keyword = request.form.get('keyword')
    user = api.search_user(keyword)

    if not user and not keyword:
        error = gettext("Khong_tim_thay_thong_tin.")
        return render_template('shop.html',
                               shop=shop,
                               keyword=keyword,
                               error=error,
                               user_login=user_login,
                               shop_id=shop_id)

    if user:
        return redirect('/user/{}'.format(user['phone']))
    else:
        error = gettext("Khong_tim_thay_thong_tin.")
        return render_template('shop.html',
                               shop=shop,
                               keyword=keyword,
                               error=error,
                               user_login=user_login,
                               shop_id=shop_id)


def percentage(new_value, old_value):
    change = new_value - old_value
    try:
        percentage_change = (change / float(old_value)) * 100
        return round(percentage_change, 2)
    except ZeroDivisionError:
        return 0


def save_coupon_code(user, shop, message, detail, type_message):
    user_id = user["_id"]
    # message = api.remove_accents(message)
    shop_id = shop['_id']
    coupon_code = api.extract_coupon_code(message)
    if coupon_code:
        coupon_expire = shop.get("coupon_expire")
        expire_settings = coupon_expire[type_message]
        expire = expire_settings if expire_settings else 5
        coupon = api.add_coupon_code(user_id, shop_id, coupon_code, detail,
                                     type_message, expire)
        message = message.replace(coupon_code, coupon)
    message = message.replace('{{ name }}', user['name'])

    if user['phone'] not in shop.get('staffs', []) and \
            user['phone'] not in shop.get('phone_numbers', []) and \
            user['phone'] not in shop.get('emps', []):
        message_no_accent = api.remove_accents(message)
        message_sms = '[{}] {}'.format(api.remove_accents(shop['name']),
                                       message_no_accent)
        send_sms_message(shop, user, message_sms, shop_id, type_message)

    return message, type_message


def send_sms_message(shop, user, message, shop_id, type_message):
    is_sms = shop.get('is_sms')
    sms_count = shop.get('sms_count')
    sms_active = shop.get('coupon_active')
    if sms_active:
        mess_active = sms_active.get(type_message)
        if is_sms and sms_count and mess_active:
            if int(sms_count) > 1:
                api.send_sms(user['phone'],
                             message,
                             expire=14 * 86400,
                             shop_id=shop_id)


@app.route('/fb_login', methods=['GET'])
def fb_login():
    gateway_mac = request.args.get('gateway_mac')
    fb_event = request.args.get('fb_event')
    client_mac = request.args.get('client_mac')
    card_id = request.args.get('card_id')
    auth_target = request.args.get('auth_target')
    # print auth_target
    next = "/welcome?gateway_mac=%s&fb_event=%s&client_mac=%s&auth_target=%s" \
           % (gateway_mac, fb_event, client_mac, auth_target)
    if card_id:
        next = next + "&card_id=%s" % card_id

    callback = url_for('facebook_authorized',
                       client_mac=client_mac,
                       gateway_mac=gateway_mac,
                       auth_target=auth_target,
                       fb_event=fb_event,
                       next=next or request.referrer or None,
                       _external=True)
    return facebook.authorize(callback=callback)


@app.route('/login/authorized', methods=['GET'])
def facebook_authorized():
    resp = facebook.authorized_response()
    gateway_mac = request.args.get('gateway_mac')
    shop = api.get_shop_info(gateway_mac=gateway_mac)
    if resp is None:
        return redirect(shop.get('facebook_page'))
    if isinstance(resp, OAuthException):
        return redirect(shop.get('facebook_page'))

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=email,birthday,age_range,name,gender')
    fb_id = me.data["id"]
    name = me.data["name"]
    email = ''
    if 'email' in me.data:
        email = me.data["email"]
    birthday = ''
    if 'birthday' in me.data:
        birthday = me.data["birthday"].replace("/", "-")
    age_range = ''
    if 'age_range' in me.data:
        age_range = me.data["age_range"]
    gender = 0
    # if 'gender' in me.data:
    #     gender = me.data["gender"]
    client_mac = request.args.get('client_mac')
    user = api.get_user_info(client_mac=client_mac)
    api.update_user_fb(user['_id'],
                       name,
                       birthday=birthday,
                       email=email,
                       fb_id=fb_id,
                       age_range=age_range,
                       gender=gender)
    shop = api.get_shop_info(gateway_mac=gateway_mac)
    card_id = request.args.get('card_id')
    facebook_page = shop.get('facebook_page')
    auth_target = request.args.get('auth_target')
    fb_event = request.args.get('fb_event')
    place_id = shop.get('page_id')
    card_link = ""
    if card_id:
        card = api.get_card(shop['_id'], card_id)
        card_link = card.get('link_share')
    link_share = card_link if len(card_link) > 0 else facebook_page
    if fb_event == 'share':
        facebook_share(link_share)
    elif fb_event == 'check_in':
        facebook_check_in(place_id)
    return redirect(auth_target)


@app.route('/social', methods=['GET'])
def handle_social():
    gateway_mac = request.args.get('gateway_mac')
    fb_event = request.args.get('fb_event')
    client_mac = request.args.get('client_mac')

    shop = api.get_shop_info(gateway_mac=gateway_mac)
    card_id = request.args.get('card_id')
    facebook_page = shop.get('facebook_page')
    auth_target = request.args.get('auth_target')
    place_id = shop.get('page_id')
    card_link = ""
    if card_id:
        card = api.get_card(shop['_id'], card_id)
        card_link = card.get('link_share')
    link_share = card_link if len(card_link) > 0 else facebook_page
    if fb_event == 'share':
        facebook_share(link_share)
    elif fb_event == 'check_in':
        facebook_check_in(place_id)
    return redirect(auth_target)


def facebook_share(link):
    facebook.post('/me/feed', data={'link': link})


def facebook_check_in(place_id):
    facebook.post('/me/feed', data={"place": place_id})


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@app.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    users = api.get_accounts_merchants(merchant_id)
    if str(request.cookies.get('langs')) == 'lo':
        roles = settings.roles_lo
    else:
        roles = settings.roles
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    return render_template('nextify/accounts.html',
                           merchant=merchant,
                           user_login=user_login,
                           users=users,
                           roles=roles,
                           shop_in_mer=shop_in_mer)


def get_roles_user(user_id, shop_id):
    user = api.get_account_merchant(shop_id, user_id)
    if user:
        roles = user.get('roles')
        return roles
    else:

        return False


def get_roles_user_merchant(user_id, merchant_id):
    user = api.get_account_merchant(str(merchant_id), user_id)
    if user:
        roles = user.get('roles')
        return roles
    else:

        return False


app.jinja_env.globals.update(get_roles_user=get_roles_user)


@app.route('/account/<account_id>', methods=['GET', 'POST'])
@login_required
def account(account_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shops = []
    merchant = g.merchant
    merchant_id = str(merchant.get('_id'))
    roles = settings.roles
    status = api.get_app_synchronized(merchant_id=merchant_id,
                                      name_app="vcall")
    if status:
        status = status.get("status", '')
    if not status:
        status = 'False'
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    if request.method == 'GET':
        if account_id == 'add':
            account_item = {}
            return render_template('nextify/account.html',
                                   shops=shops,
                                   shop_in_mer=shop_in_mer,
                                   user_login=user_login,
                                   account_item=account_item,
                                   roles=roles,
                                   merchant=merchant)
        else:
            account_item = api.get_account_merchant(str(merchant_id),
                                                    account_id)
            current_shops = [str(shop) for shop in account_item.get('shops')
                             ] if account_item.get('shops') else []
        return render_template('nextify/account.html',
                               status=status,
                               shops=shops,
                               shop_in_mer=shop_in_mer,
                               account_item=account_item,
                               user_login=user_login,
                               current_shops=current_shops,
                               roles=roles,
                               merchant=merchant)
    else:
        phone = request.form.get('phone')
        password = request.form.get('password')
        email = request.form.get('email')
        role = request.form.get('roles')
        locations = request.form.get('locations')
        shops_locations = []
        if locations and len(locations) > 0 and str(locations) != 'None':
            shops_locations = locations.split(',')

        if account_id == "add":
            if not password or len(password) < 6:
                error = gettext("Mat_khau_phai_tu_6_ky_tu_tro_len.")
                return json.dumps({'error': error})
            if not phone:
                error = gettext("So_dien_thoai_chua_dung!")
                return json.dumps({'error': error})
        else:
            if password and len(password) < 6:
                error = gettext("Mat_khau_phai_tu_6_ky_tu_tro_len.")
                return json.dumps({'error': error})
            if not phone:
                error = gettext("So_dien_thoai_chua_dung!")
                return json.dumps({'error': error})
        if user_login['roles'] in ['2', '4']:
            error = gettext(
                "Ban_khong_co_quyen_thay_doi_trang_thai_tai_khoan_nay.")
            return json.dumps({'error': error})
        check_acc = api.check_acc_merchant(str(merchant_id), phone)
        if account_id == 'add' and not check_acc:
            api.insert_new_account_merchant(str(merchant_id), phone,
                                            str(password), role, email,
                                            shops_locations)
            return json.dumps({'result': True})
        else:
            if account_id != 'add':
                api.update_account_merchant(account_id, str(merchant_id),
                                            phone, password, role, email,
                                            shops_locations)
                return json.dumps({'result': True})
            else:
                return json.dumps(
                    {'error': gettext("Cap_nhat_tai_khoan_bi_loi.")})


@app.route('/new_access', methods=['POST'])
@login_required
def new_access():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shops = []
    merchant = g.merchant
    merchant_id = str(merchant.get('_id'))
    roles = settings.roles
    status = api.get_app_synchronized(merchant_id=merchant_id,
                                      name_app="vcall")
    if status:
        status = status.get("status", '')
    if not status:
        status = 'False'
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    list_phone = request.form.get('phone_list')
    list_identity = request.form.get('identity_list')
    api.save_access(merchant_id, list_phone, list_identity)
    return json.dumps({'result': True})


@app.route('/account/<account_id>/remove', methods=['POST'])
@login_required
def account_remove(account_id):
    if request.method == "POST":
        shop = g.shop
        shop_id = g.shop_id
        merchant = g.merchant
        merchant_id = merchant.get('_id')
        user_login = g.user
        roles = settings.roles
        login_roles = user_login.get('roles')
        account = api.get_account_merchant(str(merchant_id), account_id)
        acc_role = account.get('roles')
        if acc_role == '3' and login_roles == '1':
            return redirect('/accounts')
        if login_roles in ['1', '3']:
            api.remove_account_by_id(str(merchant_id), account_id)
            return json.dumps({"result": "true"})
        else:
            return json.dumps({
                "error":
                gettext(
                    "Ban_khong_co_quyen_thay_doi_trang_thai_tai_khoan_nay.")
            })


@app.route('/splash_page', methods=['GET'])
@login_required
def splash_page():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    is_HQ = True
    if not merchant_id or merchant_id == '0':
        is_HQ = False
    pages = api.get_splash_page(shop_id)
    default_page = api.get_splash_page_by_type(shop_id, 'default')
    if pages.count() == 0 or default_page.count() == 0:
        api.new_splash_page(shop_id, 'default', True, title='Mặc định')
    cards = api.get_cards(shop_id)
    if len(cards) == 0:
        return redirect('/splash_page/cards')
    page_select = pages[0]
    return render_template('splash_page.html',
                           shop=shop,
                           pages=pages,
                           cards=cards,
                           user_login=user_login,
                           is_HQ=is_HQ,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           page_select=page_select)


@app.route('/game/<page_id>', methods=['GET'])
@login_required
def preview_spin(page_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    item = api.item_mini_game_by_unique_id(page_id)
    if not item:
        item = api.item_mini_game_by_id(page_id)
    if not item:
        abort(404)
    spin_config = item.get('info')
    old_reward_user = []
    shop_id_select = item.get('shop_id')
    shop_select = api.get_shop_info(shop_id_select)
    number_spin = spin_config.get('turns')

    return render_template(
        'new_hotspot/public_spin.html',
        shop_id=shop_id_select,
        shop=shop_select,
        old_reward_user=json.dumps(old_reward_user),
        spin_config=json.dumps(spin_config),
        spin=spin_config,
        number_spin=number_spin,
        page_id=page_id,
        shop_id_select=shop_id_select,
    )


@app.route('/setting_json/<page_id>', methods=['GET'])
def spin_json(page_id):
    old_reward_user = []
    item = api.item_mini_game_by_unique_id(page_id)
    if not item:
        item = api.item_mini_game_by_id(page_id)
    if not item:
        abort(404)
    spin_config = item.get('info')
    spin_config_gift = spin_config.get('gifts')
    try:
        win_rate = int(spin_config.get('win_rate'))
    except:
        win_rate = 0
        pass
    list_segments = []
    number_reward_user = 0
    number_code_user = 0
    shop_id_select = item.get('shop_id')
    shop_select = api.get_shop_info(shop_id_select)
    for item in spin_config_gift:
        if number_reward_user > 0 and win_rate:
            if (number_reward_user / len(old_reward_user)) > (win_rate / 100):
                if item.get('is_reward') != False:
                    item["rate_reward"] = 0
        if item.get('remaining_amount') == 0 or item.get(
                'remaining_amount') == '0':
            item["rate_reward"] = 0
        if item.get('is_reward') in ['code', 'vnpay'] and number_code_user > 0:
            item["rate_reward"] = 0
        IsCouponCode = 'true' if item.get('is_reward') in ['code', 'vnpay'
                                                           ] else 'false'
        list_segments.append({
            "txtDisplayText":
            item.get('title'),
            "txtResultText":
            item.get('detail'),
            "txtBackgroundColor":
            "#" + item.get('color', 'FFC521'),
            "amount":
            item.get('amount'),
            "remaining_amount":
            item.get('remaining_amount'),
            "ddlGravity":
            item.get("rate_gravity"),
            "hdnGravityPerc":
            item.get("rate_reward"),
            "is_reward":
            item.get("is_reward"),
            "images":
            item.get('images') if item.get('images') else "",
            "detail":
            item.get('detail', ''),
            "IsCouponCode":
            IsCouponCode
        })
    return json.dumps({
        "data": [{
            "segmentsList":
            list_segments,
            "OuterRadius":
            "212",
            "InnerRadius":
            "60",
            "WheelStrokeColor":
            "#FFFFFF",
            "WheelStrokeWidth":
            "4",
            "WheelTextColor":
            "#FFFFFF",
            "WheelTextSize":
            "20",
            "GameOverText":
            "THANK YOU FOR PLAYING SPIN2WIN WHEEL. COME AND PLAY AGAIN SOON!",
            "IntroText":
            "YOU HAVE TO CLICK SPIN BUTTON TO WIN IT!",
            "backgroundOption": {
                "type": "image",
                "value": "background_12ec1d70a7c72c01f48a1d4416074129.jpg"
            },
            "centerWheelImage":
            'http://static.nextify.vn/static/uploads/' +
            str(shop_select.get('logo')),
            "WheelPinImage":
            "wheelcenter_42b535480fd11de938ec249bf2b60678.png",
            "enablediscountbar":
            "on",
            "countdowntime":
            "15",
            "position":
            "screen_bottom",
            "showdesktop":
            "on",
            "desktopintent":
            "on",
            "desktopinterval":
            "on",
            "DesktopIntervaltext":
            "17",
            "showmobile":
            "off",
            "mobileintent":
            "on",
            "mobileinterval":
            "on",
            "MobileIntervaltext":
            "19",
            "cookiedays":
            "1"
        }]
    })


@app.route('/splash_page/<shop_id_select>/preview/<page_id>', methods=['GET'])
@login_required
def splash_page_preview(shop_id_select, page_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    is_HQ = True
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not merchant_id or merchant_id == '0':
        is_HQ = False
    # print page_id
    if page_id == 'setting_json':
        old_reward_user = []
        spin_config = shop_select.get('spin')
        spin_config_gift = spin_config.get('gifts')
        try:
            win_rate = int(spin_config.get('win_rate'))
        except:
            win_rate = 0
            pass
        list_segments = []
        number_reward_user = 0
        number_code_user = 0

        for item in spin_config_gift:
            if number_reward_user > 0 and win_rate:
                if (number_reward_user / len(old_reward_user)) > (win_rate /
                                                                  100):
                    if not item.get('is_reward'):
                        item["rate_reward"] = 0
            if item.get('remaining_amount') == 0 or item.get(
                    'remaining_amount') == '0':
                item["rate_reward"] = 0
            if item.get('is_reward') == 'code' and number_code_user > 0:
                item["rate_reward"] = 0
            list_segments.append({
                "txtDisplayText":
                item.get('title'),
                "txtResultText":
                item.get('detail'),
                "txtBackgroundColor":
                "#" + item.get('color', 'FFC521'),
                "amount":
                item.get('amount'),
                "remaining_amount":
                item.get('remaining_amount'),
                "ddlGravity":
                "30",
                "hdnGravityPerc":
                item.get("rate_reward"),
                "is_reward":
                item.get("is_reward"),
                "images":
                item.get('images') if item.get('images') else ""
            })
        data = {
            "data": [{
                "segmentsList":
                list_segments,
                "OuterRadius":
                "212",
                "InnerRadius":
                "60",
                "WheelStrokeColor":
                "#FFFFFF",
                "WheelStrokeWidth":
                "4",
                "WheelTextColor":
                "#FFFFFF",
                "WheelTextSize":
                "20",
                "GameOverText":
                "THANK YOU FOR PLAYING SPIN2WIN WHEEL. COME AND PLAY AGAIN SOON!",
                "IntroText":
                "YOU HAVE TO CLICK SPIN BUTTON TO WIN IT!",
                "backgroundOption": {
                    "type": "image",
                    "value": "background_12ec1d70a7c72c01f48a1d4416074129.jpg"
                },
                "centerWheelImage":
                'http://static.nextify.vn/static/uploads/' +
                str(shop.get('logo')),
                "WheelPinImage":
                "wheelcenter_42b535480fd11de938ec249bf2b60678.png",
                "enablediscountbar":
                "on",
                "countdowntime":
                "15",
                "position":
                "screen_bottom",
                "showdesktop":
                "on",
                "desktopintent":
                "on",
                "desktopinterval":
                "on",
                "DesktopIntervaltext":
                "17",
                "showmobile":
                "off",
                "mobileintent":
                "on",
                "mobileinterval":
                "on",
                "MobileIntervaltext":
                "19",
                "cookiedays":
                "5"
            }]
        }

        return data
    if page_id == 'connect_success':
        connect_success = shop_select.get('connect_success')
        login_form = shop.get('login_form', {})
        return render_template('wifi_portal/connect_success.html',
                               connect_success=connect_success,
                               shop=shop_select,
                               login_form=login_form)
    if page_id == 'spin':
        old_reward_user = []
        spin_config = shop_select.get('spin')
        if not spin_config:
            return render_template('new_hotspot/404.html'), 404
        number_spin = spin_config.get('turns')
        return render_template('new_hotspot/hotspot_spin.html',
                               shop_id=shop_id_select,
                               shop=shop_select,
                               old_reward_user=json.dumps(old_reward_user),
                               spin_config=json.dumps(spin_config),
                               number_spin=number_spin)
    if page_id == '0':
        abort(404)
    page = api.get_splash_page_by_id(shop_id_select, page_id)
    login_form = {}
    login_form = shop.get('login_form', {})
    cards = api.get_cards(shop_id_select)
    user = {
        "age_range": None,
        "relationship_status": None,
        "home_town": None,
        "fb_id": None,
        "phone": "0946xx0912",
        "birthday": "12-09",
        "id": "Thomas",
        "name": "Thomas",
        "gender": "",
        "email": None,
        "year_birthday": None
    }
    content = page.get('content', '')
    if content or str(content) != 'None':
        content = content.strip()
        content = content.replace('{{ name }}', user.get('name', ''))
    title = page.get('title', '')
    if title or str(title) != 'None':
        title = title.strip()
        title = title.replace('{{ name }}', user.get('name', ''))
    if page:
        if page['type_page'] == 'birthday':
            return render_template(
                'wifi_portal/event_v2.html',
                user=user,
                shop=shop,
                shop_id=shop_id,
                shop_select=shop_select,
                shop_id_select=shop_id_select,
                card=page,
                content=content,
                title=title,
                login_form=login_form,
            )
        elif page['type_page'] == 'youtube':
            return render_template(
                'wifi_portal/event_v2.html',
                user=user,
                shop=shop,
                shop_id=shop_id,
                shop_select=shop_select,
                shop_id_select=shop_id_select,
                card=page,
                content=content,
                title=title,
                type_page="youtube",
                login_form=login_form,
            )
        elif page['type_page'] == 'promotion':
            return render_template(
                'wifi_portal/event_v2.html',
                user=user,
                shop=shop,
                card=page,
                content=content,
                shop_select=shop_select,
                shop_id_select=shop_id_select,
                title=title,
                login_form=login_form,
                shop_id=shop_id,
            )
        elif page['type_page'] == 'weekday':
            return render_template(
                'wifi_portal/event_v2.html',
                user=user,
                shop=shop,
                card=page,
                content=content,
                shop_select=shop_select,
                shop_id_select=shop_id_select,
                title=title,
                login_form=login_form,
                shop_id=shop_id,
            )
        elif page['type_page'] == 'loyal':
            return render_template(
                'wifi_portal/event_v2.html',
                user=user,
                shop=shop,
                card=page,
                content=content,
                shop_select=shop_select,
                shop_id_select=shop_id_select,
                title=title,
                login_form=login_form,
                shop_id=shop_id,
            )
        elif page['type_page'] == 'hour':
            return render_template(
                'wifi_portal/event_v2.html',
                user=user,
                shop=shop,
                card=page,
                content=content,
                shop_select=shop_select,
                shop_id_select=shop_id_select,
                title=title,
                login_form=login_form,
                shop_id=shop_id,
            )

        elif page['type_page'] == 'tag':
            return render_template(
                'wifi_portal/event_v2.html',
                user=user,
                shop=shop,
                card=page,
                content=content,
                shop_select=shop_select,
                shop_id_select=shop_id_select,
                title=title,
                login_form=login_form,
                shop_id=shop_id,
            )
        else:
            return render_template('wifi_portal/default.html',
                                   user=user,
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   shop=shop,
                                   cards=cards,
                                   login_form=login_form,
                                   shop_id=shop_id)

    else:
        return render_template('wifi_portal/default.html',
                               user=user,
                               shop=shop,
                               cards=cards,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               login_form=login_form,
                               shop_id=shop_id)


@app.route('/wifi_access_code', methods=['GET', 'POST'])
@login_required
def wifi_access_code():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    page = int(request.args.get('page', 1))
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant['_id']))
    shops = []
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])

    list_access_code = api_wifi_access_code.get_wifi_access_code(shops, page)

    total_access_code = api_wifi_access_code.total_wifi_access_code(shops)
    pagination = Pagination(
        page=page,
        total=total_access_code,
        per_page=settings.ITEMS_PER_PAGE,
        css_framework='bootstrap3',
    )
    return render_template('nextify/wifi_access_code.html',
                           shop=shop,
                           user_login=user_login,
                           list_access_code=list_access_code,
                           pagination=pagination,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           total_access_code=total_access_code)


@app.route('/wifi_settings_remarketing/<shop_id_select>', methods=['POST'])
@login_required
def update_remarketing_shop(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    login_form = shop_select.get('login_form', {})
    if not shop_select:
        return redirect('/404')
    page_id = request.form.get('page_id')
    facebook_pixel_id = request.form.get('facebook_pixel_id')
    facebook_pixel_code = request.form.get('facebook_pixel_code')
    google_pixel_code = request.form.get('google_pixel_code')
    api.update_shop(shop_id_select,
                    None,
                    facebook_pixel_code=facebook_pixel_code,
                    facebook_pixel_id=facebook_pixel_id,
                    google_pixel_code=google_pixel_code,
                    page_id=page_id)

    return redirect(url_for('wifi_settings', shop_id_select=shop_id_select))


@app.route('/devices_shop/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def devices_shop_item(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    gateway_macs = shop_select.get('gateway_mac')
    error = ''
    if not gateway_macs:
        error = "Chưa có thiết bị nào được thêm!"
    return render_template('new_hotspot/device.html',
                           shop_id_select=shop_id_select,
                           user_login=user_login,
                           shop_select=shop_select,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           shop_in_mer=shops,
                           error=error,
                           gateway_macs=gateway_macs)


@app.route('/devices_shop', methods=['GET', 'POST'])
@login_required
def devices_shop():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')

    if request.method == 'GET':

        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]
        # shop_in_mer = api.get_shop_by_merchant(merchant_id)
        shop_id_select = request.args.get('shop_id_select', '')
        if not shop_id_select or len(shop_id_select) == 0:
            shop_id_select = shops[0]['_id']

        return redirect('/devices_shop/%s' % (shop_id_select))
    else:
        mac_add = request.form.get('mac_add')
        shop_mac = request.form.get('shop_mac')
        device_type = request.form.get('device_type')
        try:
            mac_add = api.normalize(mac_add) if mac_add else None
        except Exception as e:
            error = 'Mã thiết bị chưa đúng!'
            return json.dumps({'results': False, 'error': error})
        if not mac_add:
            error = 'Mã thiết bị chưa đúng!'
            return json.dumps({'results': False, 'error': error})
        try:
            shop_by_mac = api.get_shop_info(gateway_mac=mac_add)
        except Exception as e:
            error = 'Mã thiết bị chưa đúng!'
            return json.dumps({'results': False, 'error': error})

        if shop_by_mac:
            error = "Thiết bị đã được thêm vào tài khoản khác, vui lòng gỡ thiết bị hoặc liên hệ support."
            return json.dumps({'result': False, 'error': error})
        is_radius_req = request.form.get('is_radius')
        is_radius = True if is_radius_req else False
        unifi_controller = request.form.get('unifi_controller')
        api.update_shop(shop_mac, name=None, gateway_mac=mac_add)
        device_id = api.insert_device(mac_add.upper(), is_radius)
        nas_id = ''
        if device_type == 'mikrotik':
            nas_id = api.gen_device_nas_id_mikrotik(mac_add)
        api.update_device_type(device_id, device_type, nas_id, is_radius)
        return json.dumps({'result': True})


@app.route('/edit_devices_shop/<device_id>', methods=['GET', 'POST'])
@login_required
def edit_device_shop(device_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant['_id']))
    shops = []
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])
    device = api.get_device_by_id(device_id)
    if request.method == 'GET':
        return render_template('nextify/device_item.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               device=device)
    else:
        is_radius_req = request.form.get('is_radius')
        is_radius = True if is_radius_req else False

        api.update_radius_device(device_id, is_radius)
        return json.dumps({'result': True})


@app.route('/devices_shop_remove', methods=['GET'])
@login_required
def remove_device_shop():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return '200'


@app.route('/sms_log', methods=['GET'])
@login_required
def sms_log_hq():
    shop = g.shop
    user_login = g.user
    page = int(request.args.get('page', 1))
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if not merchant_id or merchant_id == '0':
        return redirect('/sms_log')
    sms_log = api.get_sms_log_hq(merchant_id, page, settings.ITEMS_PER_PAGE)
    sms_count = api.get_sms_count_hq(merchant_id)
    pagination = Pagination(page=page,
                            total=sms_count,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template("nextify/sms_log.html",
                           shop=shop,
                           sms_log=sms_log,
                           total=sms_count,
                           pagination=pagination,
                           user_login=user_login,
                           merchant=merchant)


@app.route('/app/reviews', methods=['GET'])
@login_required
def app_reviews():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    user_login = g.user
    page = int(request.args.get('page', 1))
    shops = []
    shops.append(shop['_id'])
    if merchant_id and merchant_id != '0':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer['_id'])
    reviews_arr = api.get_app_reviews(shops, page, settings.ITEMS_PER_PAGE)
    total_reviews = api.total_reviews(shops)
    pagination = Pagination(
        page=page,
        total=total_reviews,
        per_page=settings.ITEMS_PER_PAGE,
        css_framework='bootstrap3',
    )
    return render_template("app_reviews.html",
                           shop=shop,
                           merchant=merchant,
                           user_login=user_login,
                           reviews_arr=reviews_arr,
                           pagination=pagination)


@app.route('/vouchers_pos', methods=['GET'])
@login_required
def coupon_vouncher():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    user_login = g.user
    shop_id = g.shop_id
    page = int(request.args.get('page', 1))
    vounchers = gift_card_api.get_coupon_series(merchant_id, page,
                                                settings.ITEMS_PER_PAGE)
    total_vouncher = gift_card_api.total_coupon_series(merchant_id)
    pagination = Pagination(
        page=page,
        total=total_vouncher,
        per_page=settings.ITEMS_PER_PAGE,
        css_framework='bootstrap3',
    )
    return render_template("vounchers.html",
                           shop=shop,
                           user_login=user_login,
                           vounchers=vounchers,
                           pagination=pagination)


@app.route('/vouchers_pos/<coupon_id>', methods=['GET'])
@login_required
def coupon_vouncher_item(coupon_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    coupon_serier = gift_card_api.get_coupon_series_item(
        merchant_id, coupon_id)
    if coupon_serier:
        coupon_series_name = coupon_serier.get('CouponSeriesName')
        page = int(request.args.get('page', 1))
        vounchers = gift_card_api.get_coupon_cards(merchant_id, coupon_id,
                                                   page,
                                                   settings.ITEMS_PER_PAGE)
        total_vouncher = gift_card_api.total_coupon_cards(
            merchant_id, coupon_id)
        pagination = Pagination(
            page=page,
            total=total_vouncher,
            per_page=settings.ITEMS_PER_PAGE,
            css_framework='bootstrap3',
        )
        return render_template("vounchers_item.html",
                               shop=shop,
                               user_login=user_login,
                               vounchers=vounchers,
                               pagination=pagination,
                               coupon_series_name=coupon_series_name,
                               coupon_serier=coupon_serier)
    else:
        return redirect('/vouchers_pos')


@app.route('/coupons', methods=['GET', 'POST'])
@login_required
def coupon_manual_type():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = g.shop_id
    if request.method == 'GET':
        coupon_id = request.args.get('id')
        coupon_type_item = None
        if coupon_id:
            coupon_type_item = gift_card_api.get_coupon_manual_type_by_id(
                merchant_id=merchant_id,
                shop_id=shop['_id'],
                coupon_type_id=coupon_id)
        page = int(request.args.get('page', 1))
        coupons_type = gift_card_api.get_coupon_manual_type(
            merchant_id=merchant_id,
            shop_id=shop['_id'],
            all=False,
            page=page,
            page_size=settings.ITEMS_PER_PAGE)
        total_coupons_type = gift_card_api.total_coupon_manual_type(
            merchant_id=merchant_id, shop_id=shop['_id'])
        pagination = Pagination(
            page=page,
            total=total_coupons_type,
            per_page=settings.ITEMS_PER_PAGE,
            css_framework='bootstrap3',
        )
        coupons_type_select = gift_card_api.get_coupon_manual_type(
            merchant_id=merchant_id, shop_id=shop['_id'], all=True)
        return render_template('nextify/coupon_types.html',
                               shop=shop,
                               user_login=user_login,
                               coupons_type=coupons_type,
                               coupons_type_select=coupons_type_select,
                               coupon_type_item=coupon_type_item,
                               pagination=pagination,
                               merchant=merchant)
    else:
        name = request.form.get('name')
        code = request.form.get('code')
        money = request.form.get('money')
        coupon_id = request.form.get('coupon_id')
        content = request.form.get('content')
        discount_percent = request.form.get('discount_percent')
        quantity = request.form.get('quantity')
        act_type = ''
        if money and len(money) > 0:
            money = money.replace(',', '')
        gift_card_api.create_coupon_manual_type(
            merchant_id=merchant_id,
            shop_id=shop_id,
            name=name,
            code=code,
            money_exchange=money,
            cp_id=coupon_id,
            content=content,
            discount_percent=discount_percent,
            quantity=quantity)
        act_type = 'update_coupon'
        activity_history.save_activity(act_type,
                                       merchant_id,
                                       shop_id,
                                       coupon_name=name)
        return json.dumps({'result': True})


@app.route('/vouchers/coupon_type/remove', methods=['GET'])
@login_required
def coupon_manual_type_remove():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    voucher_id = request.args.get('voucher_id')
    coupon_info = gift_card_api.get_coupon_manual_type_by_id(
        merchant_id=merchant_id, shop_id=shop_id, coupon_type_id=voucher_id)
    if coupon_info:
        gift_card_api.remove_coupon_manual_type(voucher_id,
                                                merchant_id=merchant_id,
                                                shop_id=shop_id)
        gift_card_api.remove_coupon_manual_by_type(merchant_id=merchant_id,
                                                   shop_id=shop_id,
                                                   coupon_type=str(voucher_id))
        return redirect('/coupons')
    else:
        return redirect('/coupons')


@app.route('/vouchers/gen_coupons', methods=['POST'])
@login_required
def create_multi_coupon_manual():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    type_coupon = request.form.get('type_coupon')
    quantity = request.form.get('quantity')
    expire_date = request.form.get('expire_date')
    for i in range(0, int(quantity), 1):
        coupon_code = gift_card_api.gen_coupon_manual(
            merchant_id=merchant_id,
            shop_id=shop_id,
            coupon_type_id=type_coupon)
        gift_card_api.create_coupon_manual(merchant_id=merchant_id,
                                           shop_id=shop_id,
                                           coupon_type=type_coupon,
                                           date_expire=expire_date,
                                           coupon_code=coupon_code,
                                           coupon_id=None)
    return redirect('/vouchers')


@app.route('/coupons/codes', methods=['GET'])
@login_required
def coupon_manual_list():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = g.shop_id
    filter = request.args.get('filter')
    search = request.args.get('search')
    user_phone = request.args.get('user_phone')
    coupon_type_id = request.args.get('coupon_type')
    coupons_type_select = gift_card_api.get_coupon_manual_type(
        merchant_id=merchant_id, shop_id=shop['_id'], all=True)
    page = int(request.args.get('page', 1))
    coupons = []
    total_coupon_manual = 0
    if search and len(search) > 0:
        results = mongo_search.search_coupon(merchant_id, search)
        for coupon in results:
            coupon[
                'coupon_type_info'] = gift_card_api.get_coupon_manual_type_by_id(
                    merchant_id=merchant_id,
                    shop_id=shop_id,
                    coupon_type_id=coupon['coupon_type'])
            if 'user' in coupon:
                user = api.get_user_info(user_id=coupon['user'])
                coupon['user_info'] = user
            coupons.append(coupon)
        total_coupon_manual = len(coupons)

    else:
        if coupon_type_id:
            results = gift_card_api.get_coupon_manual_by_type(
                merchant_id=merchant_id,
                shop_id=shop_id,
                coupon_type=coupon_type_id,
                page=page,
                page_size=settings.ITEMS_PER_PAGE)

            for rec in results:
                rec['coupon_type_info'] = gift_card_api.get_coupon_manual_type_by_id(
                    merchant_id=merchant_id,
                    shop_id=shop_id,
                    coupon_type_id=rec['coupon_type'])
                if 'user' in rec:
                    user = api.get_user_info(user_id=rec['user'])
                    rec['user_info'] = user
                coupons.append(rec)
            total_coupon_manual = gift_card_api.total_coupon_manual_by_type(
                merchant_id=merchant_id,
                shop_id=shop_id,
                coupon_type=coupon_type_id)
        else:
            results = gift_card_api.get_coupon_manual(
                merchant_id=merchant_id,
                shop_id=shop_id,
                page=page,
                page_size=settings.ITEMS_PER_PAGE)

            for rec in results:
                rec['coupon_type_info'] = gift_card_api.get_coupon_manual_type_by_id(
                    merchant_id=merchant_id,
                    shop_id=shop_id,
                    coupon_type_id=rec['coupon_type'])
                if 'user' in rec:
                    user = api.get_user_info(user_id=rec['user'])
                    rec['user_info'] = user
                coupons.append(rec)
            total_coupon_manual = gift_card_api.total_coupon_manual(
                merchant_id=merchant_id, shop_id=shop_id)
    pagination = Pagination(
        page=page,
        total=total_coupon_manual,
        per_page=settings.ITEMS_PER_PAGE,
        css_framework='bootstrap3',
    )
    return render_template('nextify/coupons.html',
                           shop=shop,
                           user_login=user_login,
                           coupons=coupons,
                           pagination=pagination,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           coupons_type_select=coupons_type_select,
                           coupon_type_id=coupon_type_id,
                           total_coupon_manual=total_coupon_manual,
                           user_phone=user_phone,
                           filter=filter)


@app.route('/apps/order_haravan', methods=['GET'])
@login_required
def order_haravan():
    if request.method == 'GET':
        shop = g.shop
        user_login = g.user
        merchant_id = shop.get('merchant_id')
        shop_id = g.shop_id
        merchant = api.get_merchant(merchant_id)
        page = int(request.args.get('page', 1))
        orders = haravan_api.get_orders_haravan(merchant_id, page,
                                                settings.ITEMS_PER_PAGE)
        total = haravan_api.total_orders_haravan(merchant_id)
        pagination = Pagination(
            page=page,
            total=total,
            per_page=settings.ITEMS_PER_PAGE,
            css_framework='bootstrap3',
        )
        return render_template('nextify/orders.html',
                               merchant=merchant,
                               orders=orders,
                               pagination=pagination)


@app.route('/apps', methods=['GET', 'POST'])
@login_required
def apps_pos():
    if request.method == 'GET':
        shop = g.shop
        user_login = g.user
        merchant_id = shop.get('merchant_id')
        shop_id = g.shop_id
        merchant = api.get_merchant(merchant_id)
        apps = api.get_app_synchronized()
        return render_template('nextify/app_pos.html',
                               merchant=merchant,
                               apps=apps)


@app.route('/save_getfly_settings', methods=['POST'])
@login_required
def save_getfly_settings():
    shop = g.shop
    shop_id = shop.get('_id')
    merchant_id = shop.get('merchant_id')
    name_app = "getfly"
    type_app = "CRM"
    url_login = request.form.get('url_login')
    api_key = request.form.get('api_key')
    merchant_id_app = request.form.get('merchant_id_app')
    if merchant_id_app:
        check_mer_id_app = api.check_mer_id_app(merchant_id_app, merchant_id)
        if check_mer_id_app:
            return json.dumps(
                {'error': gettext("Merchant_App_ID_da_ton_tai!")})
    status = request.form.get('status')
    if not status:
        status = "False"
    else:
        status = "True"
    check_app = api.get_app_synchronized(name_app=name_app,
                                         merchant_id=merchant_id)
    if check_app:
        api.update_app_synchronized(merchant_id=merchant_id,
                                    merchant_id_app=merchant_id_app,
                                    name_app=name_app,
                                    type_app=type_app,
                                    url_login=url_login,
                                    api_key=api_key,
                                    status=status)
        tags = ["CRM", "GETFLY"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)

        producer_data = {
            "shop_id": str(shop_id),
            "task_name": "sync_getfly",
            "params": {
                "status": status,
                "url_login": url_login,
                "api_key": api_key,
                "merchant_id": str(merchant_id)
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()

        return json.dumps({"result": True})
    else:
        api.create_app_synchronized(merchant_id=merchant_id,
                                    merchant_id_app=merchant_id_app,
                                    name_app=name_app,
                                    type_app=type_app,
                                    url_login=url_login,
                                    api_key=api_key,
                                    status=status)
        tags = ["CRM", "GETFLY"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)

        producer_data = {
            "shop_id": str(shop_id),
            "task_name": "sync_getfly",
            "params": {
                "status": status,
                "url_login": url_login,
                "api_key": api_key,
                "merchant_id": str(merchant_id)
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        return json.dumps({"result": True})


@app.route('/save_setting_loop', methods=['POST'])
@login_required
def save_merchant_id_loop():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    name_app = "loop"
    type_app = 'POS'
    status = request.form.get('status')
    access_token = request.form.get('access_token_loop')
    merchant_id_app = request.form.get('merchant_id_app')
    if merchant_id_app:
        check_mer_id_app = api.check_mer_id_app(merchant_id_app, merchant_id)
        if check_mer_id_app:
            return json.dumps(
                {'error': gettext("Merchant_App_ID_da_ton_tai!")})
    if not status:
        status = "False"
        check_app = api.check_app_pos(type_app=type_app,
                                      name_app=name_app,
                                      merchant_id=merchant_id)
        if not check_app:
            api.update_all_merchant_id_app(merchant_id_app)
            api.create_app_synchronized(name_app=name_app,
                                        merchant_id=merchant_id,
                                        status=status,
                                        type_app=type_app,
                                        merchant_id_app=merchant_id_app,
                                        api_key=access_token)
            api.update_merchant_id_app(merchant_id, merchant_id_app)
            return json.dumps({"result": "True"})
        else:
            api.delete_all_app(merchant_id, type_app)
            api.update_all_merchant_id_app(merchant_id_app)
            api.create_app_synchronized(name_app=name_app,
                                        merchant_id=merchant_id,
                                        status=status,
                                        type_app=type_app,
                                        merchant_id_app=merchant_id_app,
                                        api_key=access_token)
            api.update_merchant_id_app(merchant_id, merchant_id_app)
            return json.dumps({"result": "True"})
    else:
        status = "True"
        check = api.check_access_token_loop(access_token)
        if check:
            tags = ["POS", "LOOP"]
            api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
            for tag in tags:
                get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                                  tag_name=tag)
                if not get_tag:
                    api.create_tags(merchant_id=merchant_id,
                                    name=tag,
                                    description=tag)
            check_app = api.check_app_pos(type_app=type_app,
                                          merchant_id=merchant_id)
            token = access_token
            access_token = api.get_access_token_loop(access_token)
            if not check_app:
                api.update_all_merchant_id_app(merchant_id_app)
                api.create_app_synchronized(name_app=name_app,
                                            merchant_id=merchant_id,
                                            status=status,
                                            type_app=type_app,
                                            merchant_id_app=merchant_id_app,
                                            token=token,
                                            api_key=access_token)
                api.update_merchant_id_app(merchant_id, merchant_id_app)
                return json.dumps({"result": "True"})
            if check_app:
                api.delete_all_app(merchant_id, type_app)
                api.update_all_merchant_id_app(merchant_id_app)
                api.create_app_synchronized(name_app=name_app,
                                            merchant_id=merchant_id,
                                            status=status,
                                            type_app=type_app,
                                            merchant_id_app=merchant_id_app,
                                            token=token,
                                            api_key=access_token)
                api.update_merchant_id_app(merchant_id, merchant_id_app)
                return json.dumps({"result": "True"})
        else:
            return json.dumps({
                'error':
                gettext("sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!")
            })


@app.route('/check_kiotviet', methods=['POST'])
@login_required
def check_kiotviet():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    merchant_id_app = request.form.get('merchant_id_app')
    if merchant_id_app:
        merchant_id_app = merchant_id_app.strip()
        check_mer_id_app = api.check_mer_id_app(merchant_id_app, merchant_id)
        if check_mer_id_app:
            return json.dumps(
                {'error': gettext("Merchant_App_ID_da_ton_tai!")})
    else:
        return json.dumps(
            {'error': gettext("Merchant_App_ID_khong_duoc_de_trong!")})
    retailer = request.form.get('retailer')
    if retailer:
        retailer = retailer.strip()
    client_id = request.form.get('client_id')
    if client_id:
        client_id = client_id.strip()
    secret_id = request.form.get('secret_id')
    if secret_id:
        secret_id = secret_id.strip()
    kind_kiotviet = request.form.get('kind_kiotviet')
    name_app = 'kiotviet'
    type_app = 'POS'
    src_logo = 'https://crm.nextify.co/static/nextify/img/kiotviet.png'
    status = request.form.get('status')
    if not status:
        status = "False"
        tags = ["POS", "KIOTVIET"]
        check_app = api.check_app_pos(merchant_id=merchant_id,
                                      name_app=name_app,
                                      type_app=type_app)
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)
        if not check_app:
            api.create_app_synchronized(client_id=client_id,
                                        merchant_id_app=merchant_id_app,
                                        secret_id=secret_id,
                                        name_shop=retailer,
                                        status=status,
                                        kind=kind_kiotviet,
                                        merchant_id=merchant_id,
                                        name_app=name_app,
                                        type_app=type_app,
                                        src_logo=src_logo)
            return json.dumps({'result': 'OK'})
        else:
            api.update_app_synchronized(client_id=client_id,
                                        secret_id=secret_id,
                                        name_shop=retailer,
                                        merchant_id_app=merchant_id_app,
                                        status=status,
                                        kind=kind_kiotviet,
                                        merchant_id=merchant_id,
                                        name_app=name_app,
                                        type_app=type_app)
            return json.dumps({'result': 'OK'})

    else:
        status = "True"
        if kind_kiotviet == 'FnB':
            check = api.get_access_token_api_fnb(client_id, secret_id)
        elif kind_kiotviet == 'Retailer':
            check = api.get_access_token_api_retailer(client_id, secret_id)
        if check and check.status_code == 200:
            check_json = check.json()
            app_access_token = check_json.get('access_token')
            tags = ["POS", "KIOTVIET"]

            check_app = api.check_app_pos(type_app=type_app,
                                          name_app=name_app,
                                          merchant_id=merchant_id)
            api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
            for tag in tags:
                get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                                  tag_name=tag)
                if not get_tag:
                    api.create_tags(merchant_id=merchant_id,
                                    name=tag,
                                    description=tag)

            if kind_kiotviet == 'FnB':
                branches = fnb_kiotviet.get_branches_kiotviet(
                    retailer, client_id, secret_id)
                if branches and branches.status_code == 200:
                    if 'errorCode' in branches.text:
                        return json.dumps({
                            'error':
                            gettext(
                                "sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!"
                            )
                        })
                else:
                    return json.dumps({
                        'error':
                        gettext(
                            "sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!")
                    })
            elif kind_kiotviet == 'Retailer':
                branches = CRM_Retailer_KiotViet.get_branches_kiotviet(
                    retailer, client_id, secret_id)
                if branches and branches.status_code == 200:
                    if 'errorCode' in branches.text:
                        return json.dumps({
                            'error':
                            gettext(
                                "sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!"
                            )
                        })
                else:
                    return json.dumps({
                        'error':
                        gettext(
                            "sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!")
                    })
            if not check_app:
                api.create_app_synchronized(client_id=client_id,
                                            merchant_id_app=merchant_id_app,
                                            secret_id=secret_id,
                                            name_shop=retailer,
                                            status=status,
                                            kind=kind_kiotviet,
                                            merchant_id=merchant_id,
                                            name_app=name_app,
                                            type_app=type_app,
                                            src_logo=src_logo,
                                            app_access_token=app_access_token)

            else:
                api.update_app_synchronized(client_id=client_id,
                                            secret_id=secret_id,
                                            name_shop=retailer,
                                            merchant_id_app=merchant_id_app,
                                            status=status,
                                            kind=kind_kiotviet,
                                            type_app=type_app,
                                            merchant_id=merchant_id,
                                            name_app=name_app,
                                            app_access_token=app_access_token)
            return json.dumps({'result': 'OK'})
        else:
            return json.dumps({
                'error':
                gettext("sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!")
            })


@app.route('/sync_customers_kiotviet', methods=['POST'])
@login_required
def sync_customers_kiotviet():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    name_app = 'kiotviet'
    check_app = api.get_app_synchronized(name_app=name_app,
                                         merchant_id=merchant_id)
    if check_app:
        kind_app = check_app.get('setting').get('kind')
        client_id = check_app.get('setting').get('client_id')
        secret_id = check_app.get('setting').get('secret_id')
        retailer = check_app.get('setting').get('name_shop')
        status = check_app.get('status')
        list_id_map = api.get_shop_has_pos_id(merchant_id)
        if kind_app == 'Retailer':
            for item in list_id_map:
                if item and str(item) != 'None':
                    producer_data = {
                        "shop_id": str(shop.get("_id")),
                        "task_name": "sync_kiotviet",
                        "params": {
                            "status": status,
                            "retailer": retailer,
                            "client_id": client_id,
                            "secret_id": secret_id,
                            "item": item
                        }
                    }

                    producer_data = json.dumps(producer_data).encode('utf-8')
                    producer.send(settings.cms_consumer, producer_data)
                    producer.flush()

            return json.dumps({'result': 'OK'})
        if kind_app == 'FnB':
            for item in list_id_map:
                if item and str(item) != 'None':
                    producer_data = {
                        "shop_id": str(shop.get("_id")),
                        "task_name": "sync_kiotviet_fnb",
                        "params": {
                            "status": status,
                            "retailer": retailer,
                            "client_id": client_id,
                            "secret_id": secret_id,
                            "item": item
                        }
                    }

                    producer_data = json.dumps(producer_data).encode('utf-8')
                    producer.send(settings.cms_consumer, producer_data)
                    producer.flush()

            return json.dumps({'result': 'OK'})
    else:
        return json.dumps({
            'error':
            gettext("sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!")
        })


@app.route('/check_access_token_ipos', methods=['POST'])
@login_required
def check_access_token_api():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    merchant_id_app = request.form.get('merchant_id_app')
    if merchant_id_app:
        merchant_id_app = merchant_id_app.strip()
        check_mer_id_app = api.check_mer_id_app(merchant_id_app, merchant_id)
        if check_mer_id_app:
            return json.dumps(
                {'error': gettext("Merchant_App_ID_da_ton_tai!")})
    pos_parent = request.form.get('pos_parent')
    access_token = request.form.get('access_token')
    name_app = 'ipos'
    type_app = 'POS'
    src_logo = 'https://crm.nextify.vn/static/nextify/img/ipos.png'
    status = request.form.get('status')
    if not status:
        status = "False"
        check_app = api.check_app_pos(type_app=type_app,
                                      merchant_id=merchant_id)
        tags = ["POS", "IPOS"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)
        if not check_app:
            api.create_app_synchronized(merchant_id_app=merchant_id_app,
                                        status=status,
                                        pos_parent=pos_parent,
                                        access_token=access_token,
                                        merchant_id=merchant_id,
                                        name_app=name_app,
                                        type_app=type_app,
                                        src_logo=src_logo)
            return json.dumps({'result': 'OK'})
        else:
            api.update_app_synchronized(merchant_id_app=merchant_id_app,
                                        status=status,
                                        type_app=type_app,
                                        pos_parent=pos_parent,
                                        access_token=access_token,
                                        merchant_id=merchant_id,
                                        name_app=name_app)
            return json.dumps({'result': 'OK'})
    else:
        status = "True"
        check_app = api.check_app_pos(type_app=type_app,
                                      merchant_id=merchant_id)
        tags = ["POS", "IPOS"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)
        if not check_app:
            api.create_app_synchronized(merchant_id_app=merchant_id_app,
                                        status=status,
                                        type_app=type_app,
                                        pos_parent=pos_parent,
                                        access_token=access_token,
                                        merchant_id=merchant_id,
                                        name_app=name_app,
                                        src_logo=src_logo)
            producer_data = {
                "task_name": "sync_ipos",
                "params": {
                    "merchant_id": merchant_id,
                    "access_token": access_token,
                    "pos_parent": pos_parent
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()
            return json.dumps({'result': 'OK'})
        else:
            api.update_app_synchronized(merchant_id_app=merchant_id_app,
                                        status=status,
                                        type_app=type_app,
                                        pos_parent=pos_parent,
                                        access_token=access_token,
                                        merchant_id=merchant_id,
                                        name_app=name_app)

            producer_data = {
                "task_name": "sync_ipos",
                "params": {
                    "merchant_id": merchant_id,
                    "access_token": access_token,
                    "pos_parent": pos_parent
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()

            return json.dumps({'result': 'OK'})


@app.route('/save_chatbot_id_CHATFUEL', methods=['POST'])
@login_required
def save_chatbot_id_CHATFUEL():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    chatbot_id = request.form.get('chatbot_id')
    chatfuel_token = request.form.get('chatfuel_token')
    status = request.form.get('status')
    if not status:
        status = "False"
    else:
        status = "True"
    if status == "True":
        count = api.count_active_chatbot(merchant_id=merchant_id,
                                         name_app="ahachat")
        if count > 0:
            return json.dumps(
                {'error': gettext("Ban_da_kich_hoat_chatbot_khac")})
    merchant_id_app = ""
    check_app = api.get_app_synchronized(name_app='chatfuel',
                                         merchant_id=merchant_id)
    if not check_app:
        api.create_app_synchronized(
            chatbot_id=chatbot_id,
            merchant_id=merchant_id,
            chatfuel_token=chatfuel_token,
            status=status,
            type_app='chatbot',
            src_logo='https://crm.nextify.vn/static/nextify/img/chatfuel.png',
            name_app='chatfuel')

        tags = ["CHATBOT", "CHATFUEL"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)
        return json.dumps({'result': 'OK'})
    if check_app:
        api.update_app_synchronized(name_app='chatfuel',
                                    merchant_id=merchant_id,
                                    chatbot_id=chatbot_id,
                                    type_app='chatbot',
                                    chatfuel_token=chatfuel_token,
                                    status=status)

        tags = ["CHATBOT", "CHATFUEL"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)
        return json.dumps({'result': 'OK'})


@app.route('/save_chatbot_id_AHACHAT', methods=['POST'])
@login_required
def save_chatbot_id_AHACHAT():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    chatbot_id = request.form.get('chatbot_id')
    ahachat_token = request.form.get('ahachat_token')
    status = request.form.get('status')
    if not status:
        status = "False"
    else:
        status = "True"
    if status == "True":
        count = api.count_active_chatbot(merchant_id=merchant_id,
                                         name_app="chatfuel")
        if count > 0:
            return json.dumps(
                {'error': gettext("Ban_da_kich_hoat_chatbot_khac")})
    merchant_id_app = ""
    check_app = api.get_app_synchronized(name_app='ahachat',
                                         merchant_id=merchant_id)
    if not check_app:
        api.create_app_synchronized(
            chatbot_id=chatbot_id,
            merchant_id=merchant_id,
            ahachat_token=ahachat_token,
            type_app="chatbot",
            status=status,
            src_logo='https://crm.nextify.vn/static/nextify/img/ahachat.png',
            name_app='ahachat')

        tags = ["CHATBOT", "AHACHAT"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)
        return json.dumps({'result': 'OK'})
    if check_app:
        api.update_app_synchronized(name_app='ahachat',
                                    merchant_id=merchant_id,
                                    type_app="chatbot",
                                    chatbot_id=chatbot_id,
                                    ahachat_token=ahachat_token,
                                    status=status)

        tags = ["CHATBOT", "AHACHAT"]
        api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
        for tag in tags:
            get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                              tag_name=tag)
            if not get_tag:
                api.create_tags(merchant_id=merchant_id,
                                name=tag,
                                description=tag)
        return json.dumps({'result': 'OK'})


@app.route('/broadcast_chatfuel', methods=['POST'])
@login_required
def broadcast_chatfuel():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    block_name = request.form.get('block_name')
    try:
        app = api.get_app_synchronized(name_app='chatfuel',
                                       merchant_id=merchant_id)
        chatbot_id = app.get('setting')['chatbot_id']
        chatfuel_token = app.get('setting')['chatfuel_token']
    except:
        return json.dumps({
            'error':
            gettext("Ban_can_luu_du_thong_tin_chatbot_truoc_khi_gui_tin_nhan")
        })
    list_cus = api.get_chatfuel_customer_by_merchant(merchant_id)
    if str(list_cus) == 'False':
        return json.dumps(
            {'error': gettext("Ban_khong_co_khach_hang_nao_tu_chatfuel")})
    else:
        for cus in list_cus:
            messenger_id = cus.get("user").get("messenger_id")
            r = api.chatfuel_broadcasting(chatfuel_token, messenger_id,
                                          chatbot_id, block_name)
            result = json.loads(r.text)['success']
            if str(result) == 'False':
                error = json.loads(r.text)['result']
                return json.dumps({'error': error})
            else:
                pass
    return json.dumps({'result': 'OK'})


@app.route('/save_setting_botup', methods=['GET', 'POST'])
@login_required
def save_setting_botup():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    if request.method == 'POST':
        data = request.form.get('data')
        data = json.loads(data)
        api.save_botup_setting(merchant_id=merchant_id, data_shop=data)
        return json.dumps({"result": "True"})
    else:
        data = request.args.get('data', "")
        api.apply_merchant_botup(merchant_id=merchant_id, data=data)
        return json.dumps({"result": "True"})


@app.route('/apps/botup', methods=['GET', 'POST'])
@login_required
def app_botup():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    page = request.args.get("page", 1)
    page = int(page)
    merchant = api.get_merchant(merchant_id)
    shop_id = request.args.get("shop_id")
    shop_in_mer = api.get_shop_by_merchant(merchant_id=merchant_id)
    shop_id_in_mer = []

    for shop_id_ in shop_in_mer[(page - 1) * 7:page * 7]:
        shop_id_in_mer.append({
            'id': shop_id_.get('_id'),
            'bot_up': shop_id_.get('bot_up'),
            'name': shop_id_.get('name'),
            '_id': shop_id_.get('_id')
        })

    pagination = Pagination(
        page=page,
        total=len(shop_in_mer),
        per_page=7,
        css_framework='bootstrap3',
    )
    return render_template('nextify/botup.html',
                           merchant_id=merchant_id,
                           pagination=pagination,
                           shop_id_in_mer=json.dumps(shop_id_in_mer),
                           shop_info_in_mer=shop_id_in_mer,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/kas_pos', methods=['GET', 'POST'])
@login_required
def apps_kas():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_id = request.args.get("shop_id")
    shop_select = ''
    if shop_id:
        shop_select = api.get_shop_info(shop_id)
    if request.method == "POST":
        shop_id = request.args.get("shop_id")
        id_loc = request.form.get("id_loc")

        if shop_id:
            if id_loc:
                if api.check_pos_id(id_loc, shop_id):
                    error = gettext("ID_dia_diem_da_ton_tai!")
                    return json.dumps({"error": error})
            api.update_pos_id(shop_id=shop_id, pos_id=id_loc)
            return json.dumps({'result': 'true'})
        return json.dumps({'error': gettext("Ban_chua_chon_dia_diem")})
    try:
        app = api.get_app_synchronized(name_app='kaspos',
                                       merchant_id=merchant_id)
        merchant_id_app = app.get('setting')['merchant_id_app']
        status = app.get('status')
    except:
        merchant_id_app = None
        status = 'False'
    return render_template('nextify/kas_pos.html',
                           id_mer_kas=merchant_id_app,
                           shop_in_mer=shop_in_mer,
                           shop_select=shop_select,
                           merchant_id=merchant_id,
                           merchant=merchant,
                           status=status,
                           user_login=user_login)


@app.route('/apps/chatfuel', methods=['GET', 'POST'])
@login_required
def apps_chatfuel():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    try:
        app = api.get_app_synchronized(name_app='chatfuel',
                                       merchant_id=merchant_id)
        status = app.get('status')
        chatbot_id = app.get('setting').get('chatbot_id')
        chatfuel_token = app.get('setting').get('chatfuel_token')
    except:
        chatbot_id = None
        chatfuel_token = None
        status = None

    return render_template('nextify/chatfuel.html',
                           chatbot_id=chatbot_id,
                           chatfuel_token=chatfuel_token,
                           merchant=merchant,
                           status=status,
                           user_login=user_login)


@app.route('/apps/ahachat', methods=['GET', 'POST'])
@login_required
def apps_ahachat():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    user_login = g.user
    try:
        app = api.get_app_synchronized(name_app='ahachat',
                                       merchant_id=merchant_id)
        status = app.get('status')
        chatbot_id = app.get('setting').get('chatbot_id')
        ahachat_token = app.get('setting').get('ahachat_token')
    except:
        chatbot_id = None
        ahachat_token = None
        status = None

    return render_template('nextify/ahachat.html',
                           chatbot_id=chatbot_id,
                           ahachat_token=ahachat_token,
                           merchant=merchant,
                           status=status,
                           user_login=user_login)


@app.route('/apps/ipos', methods=['GET', 'POST'])
@login_required
def apps_ipos():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_id = request.args.get("shop_id")
    shop_select = ''
    if shop_id:
        shop_select = api.get_shop_info(shop_id)
    if request.method == "POST":
        shop_id = request.args.get("shop_id")
        id_loc = request.form.get("id_loc")

        if shop_id:
            if id_loc:
                if api.check_pos_id(id_loc, shop_id):
                    error = gettext("ID_dia_diem_da_ton_tai!")
                    return json.dumps({"error": error})
            api.update_pos_id(shop_id=shop_id, pos_id=id_loc)
            return json.dumps({'result': 'true'})
        return json.dumps({'error': gettext("Ban_chua_chon_dia_diem")})
    try:
        app = api.get_app_synchronized(name_app='ipos',
                                       merchant_id=merchant_id)
        pos_parent = app.get('setting')['pos_parent']
        access_token = app.get('setting')['access_token']
        status = app.get('status')
        merchant_id_app = app.get('setting')['merchant_id_app']
    except:
        pos_parent = None
        access_token = None
        status = None
        merchant_id_app = None
    return render_template('nextify/ipos.html',
                           merchant_id_app=merchant_id_app,
                           access_token=access_token,
                           pos_parent=pos_parent,
                           shop_select=shop_select,
                           shop_in_mer=shop_in_mer,
                           status=status,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/zalo', methods=['GET', 'POST'])
@login_required
def apps_zalo():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    user_login = g.user
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = {
        'zalo_oa_id': "",
        'zalo_app_id': "",
        'zalo_app_secret_key': "",
    }
    return render_template('nextify/app_zalo.html',
                           shop_select=shop_select,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/sms_register', methods=['GET', 'POST'])
@login_required
def sms_register():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    user_login = g.user
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    if request.method == 'GET':
        brandname = api.check_register_brandname(merchant_id)
        return render_template('nextify/sms_register.html',
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               user_login=user_login,
                               brandname=brandname)
    else:
        photo = request.files.get('photo')
        photo_name = None
        if photo and \
                photo.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            photo_name = storage_api.save_new_file(photo)
        else:
            return json.dumps({'results': False, 'error': 'Chưa chọn ảnh nền'})
        website_name = request.form.get('website_name')
        company_name = request.form.get('company_name')
        brandname = request.form.get('brandname')
        custom_mess_fr = request.form.get('custom_mess')
        info_mess_fr = request.form.get('info_mess')
        ads_mess_fr = request.form.get('ads_mess')
        lba_ads_mess_fr = request.form.get('lba_ads_mess')
        education_fr = request.form.get('education')
        bank_fr = request.form.get('bank')
        elec_fr = request.form.get('elec')
        economic_fr = request.form.get('economic')
        estate_fr = request.form.get('estate')
        diff_fr = request.form.get('diff')

        custom_mess = True if custom_mess_fr else False
        info_mess = True if info_mess_fr else False
        ads_mess = True if ads_mess_fr else False
        lba_ads_mess = True if lba_ads_mess_fr else False
        education = True if education_fr else False
        bank = True if bank_fr else False
        elec = True if elec_fr else False
        economic = True if economic_fr else False
        estate = True if estate_fr else False
        diff = True if diff_fr else False

        type_message = {
            'custom_mess': custom_mess,
            'info_mess': info_mess,
            'ads_mess': ads_mess,
            'lba_ads_mess': lba_ads_mess
        }

        feilds = {
            'education': education,
            'bank': bank,
            'elec': elec,
            'economic': economic,
            'estate': estate,
            'diff': diff
        }
        api.save_register_brandname(merchant_id, photo_name, website_name,
                                    company_name, brandname, type_message,
                                    feilds)

        return json.dumps({"result": True})


@app.route('/buyform/<type_buy>', methods=['GET', 'POST'])
@login_required
def buyform(type_buy):
    print(type_buy)
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    if request.method == "GET":
        arr = ['mms', 'callbot']
        if type_buy in arr:
            if type_buy == "mms":
                type_buy = "GHDC"
            app = api.get_app_synchronized(name_app=type_buy,
                                           merchant_id=merchant_id)
            if not app:
                if type_buy == "GHDC":
                    type_buy = "mms"
                url = '/apps/' + type_buy
                return redirect(url)
        if type_buy == 'sms':
            sms_provider = merchant.get('sms_provider')
            if not sms_provider or sms_provider == "" or str(
                    sms_provider) == "None":
                url = '/apps/sms_brandname'
                return redirect(url)

        return render_template('nextify/buyform.html',
                               merchant=merchant,
                               user_login=user_login,
                               type_buy=type_buy)
    else:
        amount_news = request.form.get('amount_news')
        api.save_buy_message(merchant_id, amount_news, type_buy)
        return json.dumps({"result": True})


@app.route('/apps/client_key', methods=['GET', 'POST'])
@login_required
def apps_client_key():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    return render_template('nextify/app_client_key.html',
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/sms_brandname', methods=['GET', 'POST'])
@login_required
def apps_sms_brandname():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    return render_template('nextify/app_sms_brandname.html',
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/email', methods=['GET', 'POST'])
@login_required
def apps_email():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    mail_settings = merchant.get('mail_settings')
    return render_template('nextify/app_email.html',
                           merchant=merchant,
                           user_login=user_login,
                           mail_settings=mail_settings)


@app.route('/apps/bitly', methods=['GET', 'POST'])
@login_required
def apps_bitly():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    return render_template('nextify/app_bitly.html',
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/tiktok', methods=['GET', 'POST'])
@login_required
def apps_tiktok():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    return render_template('nextify/app_tiktok.html',
                           merchant=merchant,
                           shop_in_mer=shop_in_mer,
                           user_login=user_login)


@app.route('/apps/facebook', methods=['GET', 'POST'])
@login_required
def apps_facebook():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    return render_template('nextify/app_facebook.html',
                           merchant=merchant,
                           shop_in_mer=shop_in_mer,
                           user_login=user_login)


@app.route('/apps/google', methods=['GET', 'POST'])
@login_required
def apps_google():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    return render_template('nextify/app_google.html',
                           merchant=merchant,
                           shop_in_mer=shop_in_mer,
                           user_login=user_login)


@app.route('/apps/facebook/<shop_id>', methods=['GET', 'POST'])
@login_required
def apps_facebook_id(shop_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id)
    merchant = api.get_merchant(merchant_id)
    if request.method == "GET":
        return render_template('nextify/app_facebook.html',
                               shop_select=shop_select,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               user_login=user_login)
    else:
        pass


@app.route('/apps/tracking', methods=['GET', 'POST'])
@login_required
def apps_tracking():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    if request.method == "GET":
        return render_template('nextify/app_tracking.html',
                               merchant=merchant,
                               shop_in_mer=shop_in_mer,
                               user_login=user_login)
    else:
        shop_select_id = request.form.get('shop_select_id')
        nextify_tracking_code = request.form.get('nextify_tracking_code')
        if not shop_select_id:
            return json.dumps({'error': "Bạn chưa chọn địa điểm."})

        api.update_shop(shop_select_id,
                        nextify_tracking_code=nextify_tracking_code)

        return json.dumps({'result': "True"})


@app.route('/apps/tracking/<shop_id>', methods=['GET', 'POST'])
@login_required
def apps_tracking_id(shop_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id)
    merchant = api.get_merchant(merchant_id)
    if request.method == "GET":
        return render_template('nextify/app_tracking.html',
                               shop_select=shop_select,
                               shop_select_id=shop_id,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               user_login=user_login)
    else:
        pass


@app.route('/apps/zalo/<shop_id>', methods=['GET', 'POST'])
@login_required
def apps_zalo_id(shop_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id)
    merchant = api.get_merchant(merchant_id)
    if request.method == "GET":
        return render_template('nextify/app_zalo.html',
                               shop_select=shop_select,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               user_login=user_login)
    if request.method == "POST":
        zalo_oa_id = request.form.get("zalo_oa_id")
        zalo_app_id = request.form.get("zalo_app_id")
        zalo_app_secret_key = request.form.get("zalo_app_secret_key")
        zalo_access_token = request.form.get("zalo_access_token")
        zalo_refesh_token = request.form.get("zalo_refesh_token")
        api.update_shop(shop_id,
                        zalo_oa_id=zalo_oa_id,
                        zalo_app_id=zalo_app_id,
                        zalo_app_secret_key=zalo_app_secret_key,
                        zalo_access_token=zalo_access_token,
                        zalo_refesh_token=zalo_refesh_token)
        if zalo_access_token and len(zalo_access_token) > 0 and zalo_oa_id \
                and len(zalo_oa_id) > 0 and zalo_app_id and len(zalo_app_id) > 0 and zalo_refesh_token and len(zalo_refesh_token) > 0:
            producer_data = {
                "shop_id": str(shop_id),
                "task_name": "sync_zalo_user",
                "params": {
                    "shop_id": str(shop_id)
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()
        return json.dumps({"result": "true"})


@app.route('/apps/woay', methods=['GET', 'POST'])
@login_required
def apps_woay():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = {
        'link_woay': "",
        'shop_id_woay': "",
    }
    return render_template('nextify/app_woay.html',
                           shop_select=shop_select,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/woay/<shop_id>', methods=['GET', 'POST'])
@login_required
def apps_woay_id(shop_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id)
    merchant = api.get_merchant(merchant_id)
    if request.method == "GET":
        return render_template('nextify/app_woay.html',
                               shop_select=shop_select,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               user_login=user_login)
    if request.method == "POST":
        link_woay = request.form.get("link_woay")
        shop_id_woay = request.form.get("shop_id_woay")
        api.update_shop(shop_id,
                        link_woay=link_woay,
                        shop_id_woay=shop_id_woay)

        return json.dumps({"result": "true"})


@app.route('/apps/mailchimp', methods=['GET', 'POST'])
@login_required
def apps_mailchimp():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    app_mailchimp = {
        'mailchimp_user': "",
        'mailchim_api_key': "",
        'id_list': ""
    }
    shop_select = {}
    return render_template('nextify/app_mailchimp.html',
                           shop_select=shop_select,
                           app_mailchimp=app_mailchimp,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/mailchimp/<shop_id>', methods=['GET', 'POST'])
@login_required
def apps_mailchimp_id(shop_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id)
    merchant = api.get_merchant(merchant_id)
    name_app = "mailchimp"
    type_app = "email_marketing"
    if request.method == "GET":
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id,
                                             shop_id=str(shop_id))
        return render_template('nextify/app_mailchimp.html',
                               shop_select=shop_select,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               check_app=check_app,
                               user_login=user_login)
    if request.method == "POST":
        mailchimp_user = request.form.get("mailchimp_user")
        mailchimp_api_key = request.form.get("mailchimp_api_key")
        id_list = request.form.get("id_list")
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id,
                                             shop_id=shop_id)
        if not check_app:
            api.create_app_synchronized(name_app=name_app,
                                        merchant_id=merchant_id,
                                        shop_id=shop_id,
                                        status="True",
                                        type_app=type_app,
                                        id_list=id_list,
                                        mailchimp_user=mailchimp_user,
                                        mailchimp_api_key=mailchimp_api_key,
                                        last_sync_mailchimp=time.time())

        else:
            last_sync_mailchimp = check_app.get('last_sync_mailchimp')
            api.update_app_synchronized(
                merchant_id=merchant_id,
                status="True",
                name_app=name_app,
                type_app=type_app,
                shop_id=shop_id,
                id_list=id_list,
                mailchimp_user=mailchimp_user,
                mailchimp_api_key=mailchimp_api_key,
                last_sync_mailchimp=last_sync_mailchimp)

        producer_data = {
            "shop_id": str(shop_id),
            "task_name": "sync_mailchimp",
            "params": {
                "shop_id": str(shop_id),
                "name_app": name_app
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        return json.dumps({"result": "true"})


@app.route('/apps/mms', methods=['GET', 'POST'])
@login_required
def apps_mms():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    name_app = "GHDC"
    type_app = "sms"
    status = False
    active_mms = False
    active_sms = False
    if request.method == "GET":
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        return render_template('nextify/app_mms.html',
                               merchant=merchant,
                               check_app=check_app,
                               user_login=user_login)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        is_active = request.form.get("is_active_app")
        is_active_mms = request.form.get("is_active_mms")
        is_active_sms = request.form.get("is_active_sms")
        if is_active == "on":
            status = True
            check_info = api.login_ghdc(username, password)
            if not check_info:
                return json.dumps(
                    {'error': gettext("Sai_thong_tin_tai_khoan")})
        if is_active_mms == "on":
            active_mms = True
        if is_active_sms == "on":
            active_sms = True
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        if not check_app:
            api.create_app_synchronized(name_app=name_app,
                                        merchant_id=merchant_id,
                                        status=status,
                                        active_mms=active_mms,
                                        active_sms=active_sms,
                                        type_app=type_app,
                                        username=username,
                                        password=password)
        else:
            api.update_app_synchronized(merchant_id=merchant_id,
                                        status=status,
                                        active_mms=active_mms,
                                        active_sms=active_sms,
                                        name_app=name_app,
                                        type_app=type_app,
                                        username=username,
                                        password=password)
        return json.dumps({'result': True})


@app.route('/apps/anvui', methods=['GET', 'POST'])
@login_required
def apps_anvui():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    name_app = "anvui"
    type_app = "synch_data"
    status = False
    if request.method == "GET":
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        return render_template('nextify/app_anvui.html',
                               merchant=merchant,
                               check_app=check_app,
                               user_login=user_login)
    else:
        company_id = request.form.get('company_id')
        is_active = request.form.get("is_active_app")
        if is_active == "on":
            status = True
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        if not check_app:
            api.create_app_synchronized(name_app=name_app,
                                        merchant_id=merchant_id,
                                        status=status,
                                        type_app=type_app,
                                        company_id_anvui=company_id)
        else:
            api.update_app_synchronized(merchant_id=merchant_id,
                                        status=status,
                                        name_app=name_app,
                                        type_app=type_app,
                                        company_id_anvui=company_id)
        return json.dumps({'result': True})


@app.route('/apps/zalo_pay', methods=['GET', 'POST'])
@login_required
def apps_zalo_pay():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    name_app = "zalo_pay"
    type_app = "register"
    if request.method == "GET":
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        return render_template('nextify/register_zalo_pay.html',
                               merchant=merchant,
                               check_app=check_app,
                               user_login=user_login)
    else:
        company_name = request.form.get('company_name')
        brand_name = request.form.get("brand_name")
        bussiness_type = request.form.get("bussiness_type")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        if phone_number:
            if not api.get_phone_number(phone_number) or not all(
                [x.isdigit() for x in phone_number]):
                return json.dumps(
                    {'error': gettext("So_dien_thoai_chua_dung_dinh_dang")})
        if email:
            is_valid = validate_email(email)
            if not is_valid:
                return json.dumps(
                    {'error': gettext("Email_chua_dung_dinh_dang")})
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        if not check_app:
            app_id = api.create_app_synchronized(
                name_app=name_app,
                merchant_id=merchant_id,
                type_app=type_app,
                company_name_zalo_pay=company_name,
                brand_name_zalo_pay=brand_name,
                bussiness_type_zalo_pay=bussiness_type,
                phone_number_zalo_pay=phone_number,
                email_zalo_pay=email)
            time_create = api.get_time_register_zalo_pay(app_id)
            email_content = render_template(
                'nextify/content_register_zalo_pay.html',
                company_name=company_name,
                brand_name=brand_name,
                bussiness_type=bussiness_type,
                phone_number=phone_number,
                email=email,
                time_create=str(time_create))
            name_merchant = merchant.get('name')
            subject = "[Nextify]" + name_merchant
            email_api.send_by_mail_gun('Nextify',
                                       settings.MAIL_REGISTER_ZALO_PAY,
                                       subject, email_content)
            return json.dumps({'result': True})
        return json.dumps({'error': 'Có lỗi xảy ra thử lại sau.'})


@app.route('/apps/messenger', methods=['GET', 'POST'])
@login_required
def apps_messenger():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    user_login = g.user
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = {}
    shop_select_messenger = {
        'id_app_facebook': "",
        'app_facebook_secret': "",
        'id_facebook_page': "",
        'facebook_page_token': "",
        'facebook_user_token': "",
        'content_messenger': "",
    }
    return render_template('nextify/messenger.html',
                           shop_select_messenger=shop_select_messenger,
                           shop_select=shop_select,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/messenger/<shop_id>', methods=['GET', 'POST'])
@login_required
def apps_messenger_shop_id(shop_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id)
    shop_select_mess = shop_select.get('app_messenger')
    merchant = api.get_merchant(merchant_id)
    id_app_facebook = ""
    app_facebook_secret = ""
    id_facebook_page = ""
    facebook_page_token = ""
    facebook_user_token = ""
    content_messenger = ""
    if request.method == "GET":
        return render_template('nextify/messenger.html',
                               shop_select=shop_select,
                               shop_in_mer=shop_in_mer,
                               shop_select_messenger=shop_select_mess,
                               merchant=merchant,
                               user_login=user_login)
    if request.method == "POST":
        id_app_facebook = request.form.get("id_app_facebook")
        app_facebook_secret = request.form.get("app_facebook_secret")
        id_facebook_page = request.form.get("id_facebook_page")
        facebook_page_token = request.form.get("facebook_page_token")
        facebook_user_token = request.form.get("facebook_user_token")
        content_messenger = request.form.get("content_messenger")
        api.update_shop(shop_id,
                        id_app_facebook=id_app_facebook,
                        app_facebook_secret=app_facebook_secret,
                        id_facebook_page=id_facebook_page,
                        facebook_page_token=facebook_page_token,
                        facebook_user_token=facebook_user_token,
                        content_messenger=content_messenger)
        return json.dumps({"result": "true"})


@app.route('/apps/getfly', methods=['GET', 'POST'])
@login_required
def apps_getfly():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_id = request.args.get("shop_id")
    shop_select = ''
    if shop_id:
        shop_select = api.get_shop_info(shop_id)

    merchant_id_app = None
    url_login = None
    api_key = None
    status = 'False'
    app_get_fly = api.get_app_synchronized(name_app='getfly',
                                           merchant_id=merchant_id)
    if app_get_fly:
        merchant_id_app = app_get_fly.get('setting')['merchant_id_app']
        url_login = app_get_fly.get('setting')['url_login']
        api_key = app_get_fly.get('setting')['api_key']
        status = app_get_fly.get('status')

    return render_template("nextify/app_getfly.html",
                           merchant_id_app=merchant_id_app,
                           merchant=merchant,
                           shop_select=shop_select,
                           shop_in_mer=shop_in_mer,
                           url_login=url_login,
                           api_key=api_key,
                           status=status,
                           user_login=user_login)


@app.route('/apps/pos365', methods=['GET', 'POST'])
@login_required
def apps_pos365():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_id = request.args.get("shop_id")
    shop_select = ''
    if shop_id:
        shop_select = api.get_shop_info(shop_id)
    if request.method == "POST":
        shop_id = request.args.get("shop_id")
        id_loc = request.form.get("id_loc")

        if shop_id:
            if id_loc:
                if api.check_pos_id(id_loc, shop_id):
                    error = gettext("ID_dia_diem_da_ton_tai!")
                    return json.dumps({"error": error})
            api.update_pos_id(shop_id=shop_id, pos_id=id_loc)
            return json.dumps({'result': 'true'})
        return json.dumps({'error': gettext("Ban_chua_chon_dia_diem")})
    try:
        app = api.get_app_synchronized(name_app='pos365',
                                       merchant_id=merchant_id)
        merchant_id_app = app.get('setting')['merchant_id_app']
    except:
        merchant_id_app = None
    return render_template("nextify/app_pos365.html",
                           merchant_id_app=merchant_id_app,
                           shop_select=shop_select,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/pos', methods=['GET', 'POST'])
@login_required
def apps_setting_pos():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    pos_id = ""
    merchant_id_app = ""
    return render_template('nextify/app_setting_pos.html',
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           pos_id=pos_id,
                           merchant_id_app=merchant_id_app,
                           user_login=user_login)


@app.route('/apps/pos/<shop_id>', methods=['GET', 'POST'])
@login_required
def apps_pos_id(shop_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_select = api.get_shop_info(shop_id)
    merchant = api.get_merchant(merchant_id)
    merchant_id_app = merchant.get('merchant_id_app', "")
    pos_id = shop_select.get('pos_id', "")

    if request.method == "GET":
        return render_template('nextify/app_setting_pos.html',
                               shop_select=shop_select,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               pos_id=pos_id,
                               merchant_id_app=merchant_id_app,
                               user_login=user_login)
    if request.method == "POST":
        merchant_app_id_fr = request.form.get("merchant_id_app")
        pos_id_fr = request.form.get("pos_id")
        if not merchant_id_app or len(merchant_id_app) == 0:
            api.update_merchant_app_id(merchant_id, merchant_app_id_fr)
        if not pos_id or len(pos_id) == 0:
            api.update_shop(shop_id, pos_id=pos_id_fr)
        return json.dumps({"result": "true"})


@app.route('/apps/kiotviet', methods=['GET', 'POST'])
@login_required
def apps_kiotviet():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_id = request.args.get("shop_id")
    shop_select = ''
    if shop_id:
        shop_select = api.get_shop_info(shop_id)
    if request.method == "POST":
        shop_select = request.form.get("redirect_shop_select")
        shop_select_app = request.form.get("shop_select_app")
        if shop_select and shop_select_app:
            api.remove_pos_id(shop_select_app)
            api.update_pos_id(shop_select, shop_select_app)
            return json.dumps({'result': 'true'})
        return json.dumps({'error': gettext("Ban_chua_chon_dia_diem")})

    retailer = None
    client_id = None
    secret_id = None
    status = None
    kind = None
    merchant_id_app = None
    try:
        app = api.get_app_synchronized(name_app='kiotviet',
                                       merchant_id=merchant_id)
        retailer = app.get('setting')['name_shop']
        client_id = app.get('setting')['client_id']
        secret_id = app.get('setting')['secret_id']
        status = app.get('status')
        kind = app.get('setting')['kind']
        merchant_id_app = app.get('setting')['merchant_id_app']
    except:
        pass
    mapping_shop = []
    list_shop_app = []
    if kind == 'FnB':
        branches = fnb_kiotviet.get_branches_kiotviet(retailer, client_id,
                                                      secret_id)
        if branches and branches.status_code == 200:
            branch_json = json.loads(branches.text.encode('utf-8'))
            list_shop_app = branch_json.get(
                'data') if 'data' in branch_json else []
    elif kind == 'Retailer':
        branches = CRM_Retailer_KiotViet.get_branches_kiotviet(
            retailer, client_id, secret_id)
        if branches and branches.status_code == 200:
            branch_json = json.loads(branches.text.encode('utf-8'))
            list_shop_app = branch_json.get(
                'data') if 'data' in branch_json else []

    return render_template('nextify/kiotviet.html',
                           retailer=retailer,
                           mapping_shop=mapping_shop,
                           list_shop_app=list_shop_app,
                           client_id=client_id,
                           shop_in_mer=shop_in_mer,
                           shop_select=shop_select,
                           merchant_id_app=merchant_id_app,
                           secret_id=secret_id,
                           status=status,
                           kind=kind,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/omicrm', methods=['GET', 'POST'])
@login_required
def apps_omicall():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    role = g.role
    app = api.get_app_synchronized(name_app='omicrm', merchant_id=merchant_id)
    if app:
        api_key = app.get('setting').get('api_key')
        status = app.get('status')
        merchant_id_app = app.get('setting').get('merchant_id_app')
    else:
        api_key = None
        status = None
        merchant_id_app = None
    return render_template('nextify/omicall.html',
                           role=role,
                           status=status,
                           api_key=api_key,
                           merchant_id_app=merchant_id_app,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/bizfly', methods=['GET', 'POST'])
@login_required
def apps_bizfly():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    role = g.role
    app = api.get_app_synchronized(name_app='bizfly', merchant_id=merchant_id)
    if app:
        api_key = app.get('setting').get('api_key')
        api_secret_key = app.get('setting').get('api_secret_key')
        project_token = app.get('setting').get('project_token')
    else:
        api_key = None
        api_secret_key = None
        project_token = None
    return render_template('nextify/bizfly.html',
                           role=role,
                           api_key=api_key,
                           api_secret_key=api_secret_key,
                           project_token=project_token,
                           merchant=merchant,
                           user_login=user_login)


@app.route('/apps/haravan', methods=['GET', 'POST'])
@login_required
def apps_haravan():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    role = g.role
    email = None
    if request.method == "GET":

        email_haravan = merchant.get('email_haravan')
        token_haravan = merchant.get('token_haravan')
        haravan = merchant.get('haravan')
        callbot_order_web = ""
        callbot_order_ecom = ""
        campaign_id_web = ""
        campaign_id_ecom = ""
        if haravan and len(haravan) > 0:
            callbot_order_web = haravan.get('callbot_order_web')
            callbot_order_ecom = haravan.get('callbot_order_ecom')
            campaign_id_web = haravan.get('campaign_id_web')
            campaign_id_ecom = haravan.get('campaign_id_ecom')
        callbot_api_key = merchant.get('callbot_api_key')
        if not callbot_api_key:
            callbot_api_key = ""
        return render_template('nextify/haravan.html',
                               role=role,
                               email=email_haravan,
                               token=token_haravan,
                               merchant=merchant,
                               user_login=user_login,
                               callbot_order_web=callbot_order_web,
                               callbot_order_ecom=callbot_order_ecom,
                               campaign_id_web=campaign_id_web,
                               campaign_id_ecom=campaign_id_ecom,
                               callbot_api_key=callbot_api_key)
    else:
        email = request.form.get('email')
        token = request.form.get('token')
        callbot_order_web = request.form.get('callbot_order_web')
        if not callbot_order_web:
            callbot_order_web = ""
        callbot_order_ecom = request.form.get('callbot_order_ecom')
        if not callbot_order_ecom:
            callbot_order_ecom = ""
        campaign_id_web = request.form.get('campaign_id_web')
        if not campaign_id_web:
            campaign_id_web = ""
        campaign_id_ecom = request.form.get('campaign_id_ecom')
        if not campaign_id_ecom:
            campaign_id_ecom = ""
        callbot_api_key = request.form.get('callbot_api_key')
        if not callbot_api_key:
            callbot_api_key = ""
        api.update_merchant_haravan(merchant_id, email, token, callbot_api_key)
        api.update_merchant_haravan_callbot(merchant_id, callbot_order_web,
                                            callbot_order_ecom,
                                            campaign_id_web, campaign_id_ecom)
        haravan_domain = None
        haravan_id_shop = None
        if len(email) > 0 and len(token) > 0:
            url_info = "https://apis.haravan.com/com/shop.json"
            header = {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            }
            response_info = requests.request("GET", url_info, headers=header)
            if response_info.status_code == 200:
                result_info = response_info.json()
                haravan_shop = result_info.get('shop')
                haravan_domain = str(haravan_shop.get('domain'))
                haravan_id_shop = str(haravan_shop.get('id'))
        api.update_merchant_haravan_shop(merchant_id, haravan_domain,
                                         haravan_id_shop)

        return json.dumps({"result": "True"})


@app.route('/apps/callbot', methods=['GET', 'POST'])
@login_required
def apps_callbot():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    role = g.role
    name_app = 'callbot'
    type_app = 'callbot'
    if request.method == "GET":
        app = api.get_app_synchronized(name_app=name_app,
                                       merchant_id=merchant_id)
        return render_template('nextify/callbot_setting.html',
                               role=role,
                               email=email,
                               merchant=merchant,
                               app=app,
                               user_login=user_login)
    else:
        api_key = request.form.get('api_key')
        is_active = request.form.get("is_active_app")
        status = False
        if is_active == "on":
            status = True
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        if not check_app:
            api.create_app_synchronized(name_app=name_app,
                                        merchant_id=merchant_id,
                                        status=status,
                                        type_app=type_app,
                                        api_key=api_key)
        else:
            api.update_app_synchronized(merchant_id=merchant_id,
                                        status=status,
                                        name_app=name_app,
                                        type_app=type_app,
                                        api_key=api_key)
        return json.dumps({'result': True})


@app.route('/save_omicrm', methods=['POST'])
@login_required
def save_omicrm():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    name_app = "omicrm"
    type_app = 'CRM'
    status = request.form.get('status')
    api_key = request.form.get('api_key')
    merchant_id_app = request.form.get('merchant_id_app')
    if merchant_id_app:
        check_mer_id_app = api.check_mer_id_app(merchant_id_app, merchant_id)
        if check_mer_id_app:
            return json.dumps(
                {'error': gettext("Merchant_App_ID_da_ton_tai!")})
    else:
        return json.dumps({'error': gettext("Ban_phai_nhap_Merchant_App_ID!")})
    if not status:
        status = "False"
        check_app = api.get_app_synchronized(name_app=name_app,
                                             merchant_id=merchant_id)
        if not check_app:
            api.create_app_synchronized(name_app=name_app,
                                        merchant_id=merchant_id,
                                        status=status,
                                        type_app=type_app,
                                        merchant_id_app=merchant_id_app,
                                        api_key=api_key)
            return json.dumps({"result": "True"})
        else:
            api.update_app_synchronized(merchant_id_app=merchant_id_app,
                                        status=status,
                                        merchant_id=merchant_id,
                                        name_app=name_app,
                                        type_app=type_app,
                                        api_key=api_key)
            return json.dumps({"result": "True"})
    else:
        status = "True"
        access_token = api.check_api_key_omicrm(api_key)
        if access_token:
            tags = ["CRM", "OMICRM"]
            api.update_tag_for_merchant(merchant_id, merchant_id_app, tags)
            for tag in tags:
                get_tag = api.get_tag_by_tag_name(merchant_id=merchant_id,
                                                  tag_name=tag)
                if not get_tag:
                    api.create_tags(merchant_id=merchant_id,
                                    name=tag,
                                    description=tag)
            check_app = api.get_app_synchronized(name_app=name_app,
                                                 merchant_id=merchant_id)
            if not check_app:
                api.create_app_synchronized(name_app=name_app,
                                            merchant_id=merchant_id,
                                            status=status,
                                            type_app=type_app,
                                            merchant_id_app=merchant_id_app,
                                            api_key=api_key)
                return json.dumps({"result": "True"})
            if check_app:
                api.update_app_synchronized(merchant_id_app=merchant_id_app,
                                            status=status,
                                            merchant_id=merchant_id,
                                            name_app=name_app,
                                            type_app=type_app,
                                            api_key=api_key)
                return json.dumps({"result": "True"})
        else:
            return json.dumps({
                'error':
                gettext("sai_thong_tin_truy_suat,_xin_hay_kiem_tra_lai!")
            })


@app.route('/vouchers/redeem', methods=['POST'])
@login_required
def coupon_manual_redeem():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    shop_code = request.form.get('shop_id')
    merchant_code = request.form.get('merchant_id')
    code = request.form.get('code')
    gift_card_api.redeem_coupon_manual(merchant_id=merchant_code,
                                       shop_id=shop_code,
                                       coupon_code=code,
                                       phone_emp=user_login['phone'])
    return redirect('/coupons?filter=redeem')


@app.route('/vouchers/remove', methods=['GET'])
@login_required
def coupon_manual_remove():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    coupon_id = request.args.get('coupon_id')
    gift_card_api.remove_coupon_manual(merchant_id=merchant_id,
                                       shop_id=shop_id,
                                       coupon_id=coupon_id)
    return redirect('/coupons')


@app.route('/gift_cards', methods=['GET'])
@login_required
def gift_cards():
    shop = g.shop
    user_login = g.user
    shop_id = g.shop_id
    merchant_id = shop.get('merchant_id')
    page = int(request.args.get('page', 1))
    vounchers = gift_card_api.get_gift_cards(merchant_id, page,
                                             settings.ITEMS_PER_PAGE)
    total_vouncher = gift_card_api.total_gift_card(merchant_id)
    pagination = Pagination(
        page=page,
        total=total_vouncher,
        per_page=settings.ITEMS_PER_PAGE,
        css_framework='bootstrap3',
    )
    return render_template("gift_cards.html",
                           shop=shop,
                           user_login=user_login,
                           vounchers=vounchers,
                           pagination=pagination)


@app.route('/pos_settings/<location_id>', methods=['POST'])
@login_required
def pos_settings(location_id):
    shop = g.shop
    user_login = g.user
    shop_id = g.shop_id
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shops = []
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer['_id'])

    shop_select = api.get_shop_info(shop_id=location_id)
    pos_patner = request.form.get("pos_patner")
    pos_id = request.form.get("pos_id")
    server_hq = request.form.get("server_hq")
    user_hq = request.form.get("user_hq")
    db_hq = request.form.get("db_hq")
    pass_hq = request.form.get("pass_hq")

    access_token = request.form.get("access_token")
    pass_ipos = request.form.get("pass_ipos")
    pos_parent = request.form.get("pos_parent")
    pos_id_ipos = request.form.get("pos_id_ipos")

    api.update_pos_settings(location_id, pos_patner, str(merchant_id), pos_id,
                            server_hq, user_hq, db_hq, pass_hq, access_token,
                            pass_ipos, pos_parent, pos_id_ipos)

    shop_select = api.get_shop_info(shop_id=location_id)

    return render_template('nextify/location.html',
                           shop=shop,
                           dealer_id=dealer_id,
                           shop_id=shop_id,
                           user_login=user_login,
                           message='✓ {{ gettext("Da_luu_thong_tin") }}.',
                           shops=shops,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant_id,
                           shop_select=shop_select)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def config_hq():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    merchant = ''
    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    if request.method == 'GET':
        package_merchant = merchant.get('package')
        if not package_merchant or str(package_merchant) == 'None':
            package_merchant = '5c2c2047fa8a2c7893438810'
        package = api.find_package_fee_by_id(package_merchant)
        mail_settings = merchant.get('mail_settings')
        alias_id = merchant.get('alias_id')
        alias_detail = None
        alias_status = None

        error = None
        check = api.check_reset_password(merchant_id)
        if g.role == '3' and check:
            error = "Bạn cần cập nhật mật khẩu sau 90 ngày"
        return render_template('nextify/settings.html',
                               merchant=merchant,
                               mail_settings=mail_settings,
                               shop=shop,
                               user_login=user_login,
                               package=package,
                               alias_status=alias_status,
                               alias_detail=alias_detail,
                               shop_in_mer=shops,
                               shop_id_select='all',
                               error=error)

    else:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        identity = request.form.get('identity')
        agent = request.form.get('agent')
        role = request.form.get('role')
        business_model = request.form.get('business_model')
        average_earnings = request.form.get('average_earnings')
        time_after_send = request.form.get('time_after_send')
        time_per_visit = request.form.get('time_per_visit', '')
        time_user_connect = request.form.get('time_user_connect', '')
        if not time_per_visit:
            time_per_visit = 240
        else:
            time_per_visit = int(time_per_visit)
        if not time_user_connect:
            time_user_connect = 240
        else:
            time_user_connect = int(time_user_connect)
        if time_after_send and time_after_send != "None":
            time_after_send = int(time_after_send.strip())
        else:
            time_after_send = 7
        if average_earnings:
            average_earnings = int("".join(str(average_earnings).split(",")))
        else:
            average_earnings = 100000
        # avatar = request.files.get('avatar')

        if phone:
            if not api.get_phone_number(phone) or not all(
                [x.isdigit() for x in phone]):
                return json.dumps(
                    {'error': gettext("So_dien_thoai_chua_dung_dinh_dang")})

        else:
            return json.dumps(
                {'error': gettext("So_dien_thoai_la_thong_tin_bat_buoc.")})
        if email:
            is_valid = validate_email(email)
            if not is_valid:
                return json.dumps(
                    {'error': gettext("Email_chua_dung_dinh_dang")})
        if not name or len(name.strip()) == 0:
            return json.dumps({'error': gettext("Ten_la_thong_tin_bat_buoc.")})

        try:
            avatar = None
            if request.files.get('avatar') and \
                    request.files.get('avatar').filename.rsplit('.', 1)[1].lower() \
                    in ALLOWED_EXTENSIONS:
                file_data = request.files.get('avatar')
                avatar = storage_api.save_new_file(file_data)

            api.update_merchants(
                merchant_id=merchant_id,
                avatar=avatar,
                business_model_id=business_model,
                identity=identity,
                role=role,
                agent=agent,
                phone=phone,
                email=email,
                time_per_visit=time_per_visit,
                time_user_connect=time_user_connect,
                average_earnings=average_earnings,
                name=name,
                time_after_send=time_after_send,
            )
            return json.dumps({'result': 'ok'})
        except Exception as er:
            return json.dumps({
                'error':
                gettext(
                    "Thay_doi_thong_tin_khong_thanh_cong,_vui_long_thu_lai_sau"
                )
            })


@app.route('/email_otp', methods=['GET'])
@login_required
def email_otp():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    merchant = ''

    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    shops = []
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])
        shops.append(shop_mer)
    page = int(request.args.get('page', 1))
    loc_id = request.args.get('loc_id', 'all')
    logs = []
    total = 0
    if loc_id and str(loc_id) != 'all':
        logs = api.get_otp_log(merchant_id=merchant_id,
                               page=page,
                               page_size=settings.ITEMS_PER_PAGE,
                               shop_id=loc_id)
        total = api.get_total_otp_log(merchant_id=merchant_id, shop_id=loc_id)
    else:
        logs = api.get_otp_log(merchant_id=merchant_id,
                               page=page,
                               page_size=settings.ITEMS_PER_PAGE)
        total = api.get_total_otp_log(merchant_id=merchant_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('new_hotspot/email_otp.html',
                           merchant=merchant,
                           shop=shop,
                           loc_id=loc_id,
                           user_login=user_login,
                           shop_in_mer=shops,
                           pagination=pagination,
                           total=total,
                           page=page,
                           logs=logs)


@app.route('/settings/locations/<shop_id_select>', methods=['GET'])
@login_required
def settings_location(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    merchant = ''

    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    if shop_id_select == 'all':
        return redirect('/settings')

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_select:
        return redirect('/')

    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    business_model_list = api.business_model_list()
    ls_business_model = []
    for bus_model in business_model_list:
        ls_business_model.append(bus_model)

    access_token = shop_select.get('zalo_access_token')
    zalo_oa_id = shop_select.get('zalo_oa_id')
    zalo_app_id = shop_select.get('zalo_app_id')
    if access_token and len(access_token) > 0 and zalo_oa_id \
            and len(zalo_oa_id) > 0 and zalo_app_id and len(zalo_app_id) > 0:
        producer_data = {
            "shop_id": str(shop_id_select),
            "task_name": "sync_zalo_user",
            "params": {
                "shop_id": str(shop_id_select)
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
    access_token_page = shop_select.get('access_token_page')
    id_page = shop_select.get('id_page')

    surveys = api.total_survey_splash(shop_id_select)
    if surveys == 0:
        rating.init_survey(merchant, shop_id_select,
                           get_top_domain(request.host))
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    info_detect = api.get_info_detect_zalo(shop_id_select)
    phones_report_zalo = api.get_phones_report_zalo(shop_id_select)
    phones_detect = api.get_phones_detect_customer(shop_id_select)
    package_merchant = merchant.get('package')
    if not package_merchant or str(package_merchant) == 'None':
        package_merchant = '5b445168c5e5f42f1687ec5e'
    package = api.find_package_fee_by_id(package_merchant)
    source_tags = []
    shop_tags = shop_select.get('tags')
    if shop_tags:
        for tag in shop_tags:
            tag_db = api.get_tag_by_tag_id(merchant_id, tag)
            if tag_db:
                source_tags.append(str(tag))
    return render_template('nextify/settings_location.html',
                           merchant=merchant,
                           shop=shop,
                           user_login=user_login,
                           shop_in_mer=shops,
                           shop_select=shop_select,
                           shop_id_select=shop_id_select,
                           phones=phones_report_zalo,
                           tags=tags,
                           info_detect=info_detect,
                           package=package,
                           phones_detect=phones_detect,
                           ls_business_model=ls_business_model,
                           shop_tags=source_tags)


@app.route('/settings/locations/<shop_id_select>/update', methods=['POST'])
@login_required
def settings_location_update(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    name = request.form.get('name').strip()
    hotline = request.form.get('hotline')
    address = request.form.get('address')
    email = request.form.get('email')
    website = request.form.get('website')
    facebook_page = request.form.get('facebook_page')
    company_id_anvui = request.form.get('company_id_anvui')
    unifi_controller = request.form.get('unifi_controller')
    shop_select = api.get_shop_info(shop_id=shop_id_select)

    if not name or len(name) == 0:
        error = gettext("Ten_cua_hang_khong_duoc_de_trong")
        return json.dumps({'result': False, 'msg': error})

    if hotline and len(hotline) > 0:
        if not api.get_phone_number(hotline) or not \
                all([x.isdigit() for x in hotline]):
            error = gettext("So_dien_thoai_chua_dung_dinh_dang")
            return json.dumps({'result': False, 'msg': error})

    logo_filename = None
    background_filename = None
    logo = request.files.get('logo')
    if logo:
        if allowed_file(logo.filename):
            logo_filename = storage_api.save_new_file(logo)
        else:
            error = gettext("Hay_chon_dung_dinh_dang_anh")
            return json.dumps({'result': False, 'msg': error})

    background = request.files.get('background')
    if background:
        if allowed_file(background.filename):
            background_filename = storage_api.save_new_file(background)
        else:
            error = gettext("Hay_chon_dung_dinh_dang_anh")
            return json.dumps({'result': False, 'msg': error})
    business_model = request.form.get('business_model')
    tags = request.form.get('real_tags_filter')
    tags_array = []
    if tags and len(tags) > 0:
        tags_split = tags.split(',')
        if len(tags_split) > 0:
            for tag in tags_split:
                tag = tag.strip()
                if len(tag) > 0:
                    tags_array.append(ObjectId(tag))
    api.update_shop(shop_id_select,
                    name,
                    logo=logo_filename,
                    background=background_filename,
                    hotline=hotline,
                    address=address,
                    email=email,
                    website=website,
                    facebook_page=facebook_page,
                    merchant_id=merchant_id,
                    company_id_anvui=company_id_anvui,
                    business_model=business_model,
                    tags=tags_array,
                    unifi_controller=unifi_controller)
    # act_type = 'update_location'
    # activity_history.save_activity(
    #     act_type, merchant_id, shop_id, location_name=name)
    access_token = shop_select.get('zalo_access_token')
    zalo_oa_id = shop_select.get('zalo_oa_id')
    zalo_app_id = shop_select.get('zalo_app_id')
    if access_token and len(access_token) > 0 and zalo_oa_id \
            and len(zalo_oa_id) > 0 and zalo_app_id and len(zalo_app_id) > 0:
        producer_data = {
            "shop_id": str(shop_id_select),
            "task_name": "sync_zalo_user",
            "params": {
                "shop_id": str(shop_id_select)
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
    return json.dumps({'result': True})


@app.route('/settings/locations/<shop_id_select>/update_social',
           methods=['POST'])
@login_required
def settings_location_update_social(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    merchant_id = shop_info.get('merchant_id')
    id_page = request.form.get('page_fb')
    access_token_page = ""

    place_id = request.form.get('place_id')
    facebook_page = request.form.get('facebbook_page')
    tripadvisor = request.form.get('tripadvisor')

    facebook_pixel_id = request.form.get('facebook_pixel_id')
    pixel_code = request.form.get('pixel_code')
    google_pixel_code = request.form.get('google_pixel_code')
    tiktok_pixel_code = request.form.get('tiktok_pixel_code')
    ga_id = request.form.get('ga_id')
    # id_page = request.form.get('page_fb')

    # if id_page and id_page != "all":
    #     check_double = api.check_double_fb(id_page=id_page, shop_id_select=shop_id_select)
    #     if not check_double:
    #         error = "Page Facebook này đã được chọn cho một địa điểm khác. Bạn hãy chọn một trang khác."
    #         return json.dumps({'result': False,
    #                            'msg': error})
    #     access_token_page = api.get_access_token_page(id_page)
    #     if access_token_page:
    #         api.facebook_lead_ad(page_id=id_page, access_token_page=access_token_page)

    if place_id:
        check_double = api.check_double_fb(place_id=place_id,
                                           shop_id_select=shop_id_select)
        if not check_double:
            error = gettext(
                "Dia_diem_tren_google_nay_da_duoc_chon_cho_mot_dia_diem_khac._Ban_hay_chon_mot_dia_diem_khac_tren_google."
            )
            return json.dumps({'result': False, 'msg': error})

    api.update_shop(shop_id_select,
                    merchant_id=merchant_id,
                    id_page=id_page,
                    place_id=place_id,
                    access_token_page=access_token_page,
                    facebook_page=facebook_page,
                    tripadvisor=tripadvisor,
                    facebook_pixel_code=pixel_code,
                    facebook_pixel_id=facebook_pixel_id,
                    google_pixel_code=google_pixel_code,
                    tiktok_pixel_code=tiktok_pixel_code,
                    ga_id=ga_id)
    # act_type = 'update_location'
    # activity_history.save_activity(
    #     act_type, merchant_id, shop_id, location_name=name)

    access_token = shop_select.get('zalo_access_token')
    zalo_oa_id = shop_select.get('zalo_oa_id')
    zalo_app_id = shop_select.get('zalo_app_id')
    if access_token and len(access_token) > 0 and zalo_oa_id \
            and len(zalo_oa_id) > 0 and zalo_app_id and len(zalo_app_id) > 0:
        producer_data = {
            "shop_id": str(shop_id_select),
            "task_name": "sync_zalo_user",
            "params": {
                "shop_id": str(shop_id_select)
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()

    return json.dumps({'result': True})


@app.route('/settings/update_password', methods=['POST'])
@login_required
def update_password():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    re_new_password = request.form.get('re_new_password')
    NON_ALPHABETIC_CHARACTERS = {'#', '@', '%'}
    DIGITS_CHARACTERS = set(string.digits)
    LETTERS_CHARACTERS = set(string.ascii_letters)
    if not old_password or not new_password or not re_new_password \
            or len(old_password) == 0 or len(new_password) == 0 and len(re_new_password) == 0:
        return json.dumps({'error': gettext("Ban_can_du_cac_truong_bat_buoc")})

    if new_password != re_new_password:
        return json.dumps(
            {'error': gettext("Ban_can_nhap_lai_mat_khau_moi_chinh_xac")})

    sign_in = api.hq_sign_in_by_id(merchant_id, old_password)
    if not sign_in:
        return json.dumps({'error': 'Mật khẩu bạn nhập chưa chính xác'})

    if len(new_password) < 8:
        error = gettext("Mat_khau_can_co_it_nhat_8_ki_tu")
        return json.dumps({'error': error})

    if not any(char in new_password for char in LETTERS_CHARACTERS):
        error = gettext("Mat_khau_can_co_it_nhat_1_chu_thuong")
        return json.dumps({'error': error})
    if not any(char.isupper() for char in new_password):
        error = gettext("Mat_khau_can_co_it_nhat_1_chu_hoa")
        return json.dumps({'error': error})

    if not any(char in new_password for char in DIGITS_CHARACTERS):
        error = gettext("Mat_khau_can_co_it_nhat_1_chu_so")
        return json.dumps({'error': error})
    if not any(char in new_password for char in NON_ALPHABETIC_CHARACTERS):
        error = gettext("Mat_khau_can_co_it_nhat_1_ki_tu_dac_biet")
        return json.dumps({'error': error})

    passwd = api.update_password_merchant(merchant_id, new_password)
    if passwd:
        return json.dumps({'result': True})
    else:
        return json.dumps({
            'error':
            gettext("Thay_doi_mat_khau_khong_thanh_cong,_vui_long_thu_lai_sau")
        })


@app.route('/setting_integration', methods=['GET', 'POST'])
@login_required
def setting_integration():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    business_model_list = api.business_model_list()
    ls_business_model = []
    for bus_model in business_model_list:
        ls_business_model.append(bus_model)

    if request.method == 'GET':
        package_merchant = merchant.get('package')
        if not package_merchant or str(package_merchant) == 'None':
            package_merchant = '5c2c2047fa8a2c7893438810'
        package = api.find_package_fee_by_id(package_merchant)
        mail_settings = merchant.get('mail_settings')
        alias_id = merchant.get('alias_id')
        alias_detail = None
        alias_status = None
        if alias_id and str(alias_id) != 'None':
            alias_detail = viettel_ads_api.alias_detail(str(alias_id))
            if alias_detail and 'data' in alias_detail:
                alias_status = alias_detail['data']['status']
        get_a_business_model = api.business_model(merchant_id)
        request_integration_sms = api.DATABASE.request_integration_sms.find_one(
            {'merchant_id': merchant_id})
        request_register_sms_brandname = api.DATABASE.request_register_sms.find_one(
            {'merchant_id': merchant_id})
        return render_template(
            'nextify/setting_intergration.html',
            merchant=merchant,
            mail_settings=mail_settings,
            shop=shop,
            user_login=user_login,
            package=package,
            alias_status=alias_status,
            alias_detail=alias_detail,
            get_business_model=get_a_business_model,
            get_a_business_model=get_a_business_model,
            business_model_list=business_model_list,
            request_integration_sms=request_integration_sms,
            request_register_sms_brandname=request_register_sms_brandname)


@app.route('/setting_detection_employee', methods=['GET', 'POST'])
@login_required
def setting_detection_employee():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    if request.method == 'GET':
        active_detection = merchant.get('active_detection')
        top5_detection = merchant.get('top5_detection')
        timing_detection = merchant.get('timing_detection')
        return render_template('nextify/setting_detection_employee.html',
                               merchant=merchant,
                               active_detection=active_detection,
                               top5_detection=top5_detection,
                               timing_detection=timing_detection)
    if request.method == 'POST':
        active_detection = request.form.get('active_detection')
        top5_detection = request.form.get('top5_detection')
        timing_detection = request.form.get('timing_detection')
        time_ = ""
        active_detection = "True" if str(
            active_detection) == "true" else "False"
        top5_detection = "True" if str(top5_detection) == "true" else "False"
        timing_detection = "True" if str(
            timing_detection) == "true" else "False"
        if timing_detection == "True":
            time_ = request.form.get('time_')
            if time_:
                time_ = time_.strip()
        api.update_setting_detection(merchant_id, active_detection,
                                     top5_detection, timing_detection, time_)

        if top5_detection == "True" or len(time_) > 0:
            last_time = api.get_time_detective_employee(merchant_id)
            if last_time:
                time_now = datetime.today()
                datetime_last_time = datetime.fromtimestamp(last_time)
                if (str(datetime_last_time.day) + "/" +
                        str(datetime_last_time.month) + "/" +
                        str(datetime_last_time.year)) != (
                            str(time_now.day) + "/" + str(time_now.month) +
                            "/" + str(time_now.year)):
                    header = {
                        "Authorization":
                        "Bearer 57f9468f5ff42afd41b41e11474fe670"
                    }
                    requests.get(
                        settings.API_URL +
                        '/employee_detect?merchant_id={}'.format(merchant_id),
                        headers=header)
            else:
                header = {
                    "Authorization": "Bearer 57f9468f5ff42afd41b41e11474fe670"
                }
                requests.get(
                    settings.API_URL +
                    '/employee_detect?merchant_id={}'.format(merchant_id),
                    headers=header)

        return json.dumps({"result": True})


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def merchant_payment():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    merchant = ''
    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    business_model_list = api.business_model_list()
    ls_business_model = []
    for bus_model in business_model_list:
        ls_business_model.append(bus_model)

    if request.method == 'GET':
        package_merchant = merchant.get('package')
        if not package_merchant or str(package_merchant) == 'None':
            package_merchant = '5c2c2047fa8a2c7893438810'
        package = api.find_package_fee_by_id(package_merchant)
        mail_settings = merchant.get('mail_settings')
        alias_id = merchant.get('alias_id')
        alias_detail = None
        alias_status = None
        if alias_id and str(alias_id) != 'None':
            alias_detail = viettel_ads_api.alias_detail(str(alias_id))
            if alias_detail and 'data' in alias_detail:
                alias_status = alias_detail['data']['status']
        get_a_business_model = api.business_model(merchant_id)

        return render_template('nextify/payment.html',
                               merchant=merchant,
                               mail_settings=mail_settings,
                               shop=shop,
                               user_login=user_login,
                               package=package,
                               alias_status=alias_status,
                               alias_detail=alias_detail,
                               get_business_model=get_a_business_model,
                               get_a_business_model=get_a_business_model,
                               business_model_list=business_model_list)


@app.route('/create_QR_code', methods=['GET', 'POST'])
@login_required
def create_QR_code():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    if request.method == 'GET':
        return render_template('nextify/create_QR_code.html',
                               merchant=merchant)


@app.route('/info_email', methods=['POST'])
@login_required
def config_hq_email():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')

    mail_name = ''
    mail_user = ''
    mail_pass = ''
    mail_server = ''
    mail_port = ''
    mail_ssl = ''

    mail_box = request.form.get('mail_box')
    if mail_box == "mail_gun":
        mail_name = request.form.get('mail_domain')
        mail_user = request.form.get('mail_domain')
        mail_pass = request.form.get('mail_api_key')
        mail_server = request.form.get('mail_api_url')
        mail_port = "25"
        mail_ssl = True
    #
    if mail_box == "gmail":
        mail_name = request.form.get('name_gmail')
        mail_user = mail_name
        mail_pass = request.form.get('pass_gmail')
        mail_server = "smtp.gmail.com"
        mail_port = "465"
        mail_ssl = True

    if mail_box == "mail_khac":
        mail_name = request.form.get('smtp_email')
        mail_user = request.form.get('smtp_user')
        mail_pass = request.form.get('smtp_pass')
        mail_server = request.form.get('smtp_server')
        mail_port = request.form.get('smtp_port')
        mail_ssl = request.form.get('checkbox_ssl')
    # SendGrid
    if mail_box == "sendgrid":
        mail_name = request.form.get('from_email')
        mail_user = request.form.get('from_email')
        mail_pass = request.form.get('api_key')
        mail_server = "sendgrid"

    mail_settings = {
        "mail_name": mail_name,
        "mail_user": mail_user,
        "mail_pass": mail_pass,
        "mail_server": mail_server,
        "mail_port": mail_port,
        "mail_ssl": mail_ssl
    }
    api.update_merchants(merchant_id=merchant_id, mail_settings=mail_settings)
    init = request.args.get('init')
    if init == '1':
        return json.dumps({'result': True})
    return json.dumps({'result': True})
    # return redirect('/apps/email')


@app.route('/info_sms', methods=['POST'])
@login_required
def info_sms():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    sms_provider = request.form.get('sms_provider')
    print("log save sms")
    print(sms_provider)
    user_sms = request.form.get('user_sms')
    pass_sms = request.form.get('pass_sms')
    cp_code = request.form.get('cp_code')
    brand_name = request.form.get('brand_name')
    if sms_provider == "GHD":
        user_sms = request.form.get('user_sms_ghd')
        pass_sms = request.form.get('pass_sms_ghd')
    if sms_provider == "VIETTEL":
        user_sms = request.form.get('user_sms_viettel')
        pass_sms = request.form.get('pass_sms_viettel')
        brand_name = request.form.get('brand_name_viettel')
    print(user_sms)
    print(pass_sms)

    api_key_vhat = request.form.get('api_key_vhat')
    secret_key_vhat = request.form.get('secret_key_vhat')
    quota = request.form.get('quota', '-1')
    sms_type = request.form.get('sms_type')
    brand_name_vina = {}
    if not sms_provider or len(sms_provider) == 0:
        return json.dumps({
            'result': False,
            'error': gettext("Ban_chua_chon_nha_cung_cap_SMS")
        })
    if sms_provider != "VINAPHONE":
        if sms_provider == "GHD":
            if not user_sms or len(user_sms) == 0:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext("Ban_chua_nhap_thong_tin_nguoi_dung_SMS")
                })

            if not pass_sms or len(pass_sms) == 0:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext("Ban_chua_nhap_thong_tin_mat_khau_SMS")
                })
        else:
            if not user_sms or len(user_sms) == 0:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext("Ban_chua_nhap_thong_tin_nguoi_dung_SMS")
                })

            if not pass_sms or len(pass_sms) == 0:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext("Ban_chua_nhap_thong_tin_mat_khau_SMS")
                })
            if not brand_name or len(brand_name) == 0:
                return json.dumps({
                    'result':
                    False,
                    'error':
                    gettext("Ban_chua_nhap_thong_tin_SMS_brandname")
                })
            if sms_provider == "MOBIFONE":
                check_info = api.check_info_brandname_mobi(user_sms, pass_sms)
                if not check_info:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext(
                            "Khong_thanh_cong._Cau_hinh_SMS_Brandname_chua_chinh_xac."
                        )
                    })
    info = {}
    if sms_provider == "INCOM":
        sms_type_incom = request.form.get('sms_type_incom', '')
        username_incom = request.form.get('username_incom', '')
        password_incom = request.form.get('password_incom', '')
        command_code_incom = request.form.get('command_code_incom', '')
        prefix_id_incom = request.form.get('prefix_id_incom', '')
        api.update_merchants(merchant_id=merchant_id,
                             sms_type_incom=sms_type_incom,
                             username_incom=username_incom,
                             password_incom=password_incom,
                             command_code_incom=command_code_incom,
                             prefix_id_incom=prefix_id_incom)
    elif sms_provider == "VINAPHONE":
        vina_label_id = request.form.get('vina_label_id')
        vina_template_id = request.form.get('vina_template_id')
        vina_contract_id = request.form.get('vina_contract_id')
        vina_agent_id = request.form.get('vina_agent_id')
        vina_api_user = request.form.get('vina_api_user')
        vina_api_pass = request.form.get('vina_api_pass')
        vina_api_url = request.form.get('vina_api_url')
        vina_user_name = request.form.get('vina_user_name')
        brand_name_vina['vina_label_id'] = vina_label_id
        brand_name_vina['vina_contract_id'] = vina_contract_id
        brand_name_vina['vina_agent_id'] = vina_agent_id
        brand_name_vina['vina_api_user'] = vina_api_user
        brand_name_vina['vina_api_url'] = vina_api_url
        brand_name_vina['vina_api_pass'] = vina_api_pass
        brand_name_vina['vina_user_name'] = vina_user_name
        api.update_merchants(merchant_id=merchant_id,
                             sms_provider=sms_provider,
                             brand_name_vina=brand_name_vina)

    else:
        api.update_merchants(merchant_id=merchant_id,
                             sms_provider=sms_provider,
                             user_sms=user_sms,
                             pass_sms=pass_sms,
                             api_key_vhat=api_key_vhat,
                             secret_key_vhat=secret_key_vhat,
                             brand_name=brand_name,
                             quota=quota,
                             sms_type=sms_type,
                             cp_code=cp_code)

    return json.dumps({'result': True})


@app.route('/info_brand_name', methods=['POST'])
@login_required
def info_brand_name():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')

    brand_name = request.form.get('brand_name')
    # category = request.form.get('category')
    category_list = request.form.getlist('category')
    category = []
    if 0 < len(category_list) < 7:
        category = [int(cat) for cat in category_list]
        category = str(category)
    else:
        category = None
    telcos = request.form.getlist('telco')
    telco = []
    if len(telcos) > 0:
        telco = [str(cat) for cat in telcos]
        telco = str(telco)

    if not brand_name or len(brand_name) < 1:
        error_alias = gettext("Ten_thuong_hieu_khong_duoc_de_trong.")
        return json.dumps({'results': False, 'message': error_alias})
    if brand_name and len(brand_name) > 11:
        error_alias = gettext("Ten_thuong_hieu_khong_duoc_qua_11_ky_tu.")
        return json.dumps({'results': False, 'message': error_alias})
    if not category or len(category) == 0:
        error_alias = gettext("Ban_phai_chon_toi_thieu_mot_danh_muc.")
        return json.dumps({'results': False, 'message': error_alias})
    if not telco or len(telco) == 0:
        error_alias = gettext("Ban_phai_chon_toi_thieu_mot_nha_mang.")
        return json.dumps({'results': False, 'message': error_alias})

    alias_create = viettel_ads_api.alias_create(brand_name, category, telco)

    if not alias_create or 'data' not in alias_create:
        error_alias = gettext(
            "Dang_ky_khong_thanh_cong._Vui_long_lien_he_tu_van_vien_ho_tro.")
        return json.dumps({'results': False, 'message': error_alias})
    else:
        alias_id = alias_create['data']['alias_id']
        viettel_ads_api.alias_request_approved(alias_id)

        api.update_merchants(merchant_id=merchant_id,
                             brand_name=brand_name,
                             category=category,
                             telco=telco,
                             alias_id=alias_id)

        return json.dumps({'results': True})


@app.route('/splash_page/<shop_id_select>/hotspot/survey/get_list_tags',
           methods=['GET', 'POST'])
@login_required
def get_list_tags(shop_id_select):
    shop = g.shop
    shop_id = shop_id_select
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    tags = [{
        'text': str(tag.get('name')),
        'id': str(tag.get('_id'))
    } for tag in api.list_tags(merchant_id)
            if tag['name'] and len(str(tag['name'])) > 0]
    result = json.dumps(tags)
    resp = Response(result, status=200, mimetype='application/json')
    return resp


@app.route('/create_tags/<tag_id>', methods=['GET', 'POST'])
@login_required
def create_user_tags(tag_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_info.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if request.method == 'GET':
        tag_item = {}
        if tag_id and str(tag_id) != 'add':
            tag_item = api.get_tag_by_tag_id(merchant_id, tag_id)
        return render_template('nextify/tags_item.html',
                               merchant_id=merchant_id,
                               merchant=merchant,
                               shop=shop,
                               user_login=user_login,
                               shop_id=shop_id,
                               tag_item=tag_item)

    else:
        if tag_id and str(tag_id) != 'add':
            name = request.form.get('name_update_tag')
            desc = request.form.get('desc')
            try:
                old_name_tag = api.get_tag_name_by_tag_id(tag_id)
                if old_name_tag['name'] == name:
                    api.create_tags(merchant_id, name, desc, tag_id=tag_id)
                    return json.dumps({'result': 'success'})
            except:
                pass
            if api.check_tag_name(name, merchant_id):
                error = gettext("Ten_tag_nay_da_ton_tai!")
                return json.dumps({'error': error})
            api.create_tags(merchant_id, name, desc, tag_id=tag_id)
            return json.dumps({'result': 'success'})

        elif tag_id and str(tag_id) == 'add':
            name = request.form.get('name')
            desc = request.form.get('desc')
            if api.check_tag_name(name, merchant_id):
                error = gettext("Ten_tag_nay_da_ton_tai!")
                return json.dumps({'error': error})
            api.create_tags(merchant_id, name, desc, tag_id=tag_id)
            return json.dumps({'result': 'success'})
        return redirect('/tags')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html'), 404


@app.errorhandler(503)
def page_error(e):
    return render_template('error_pages/503.html'), 503


@app.errorhandler(500)
def page_internal_server(e):
    return render_template('error_pages/500.html'), 500


@app.errorhandler(502)
def page_bad_gateway(e):
    return render_template('error_pages/502.html'), 502


@app.route('/preview/<shop_id_select>/register', methods=['GET', 'POST'])
@login_required
def preview_register(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    login_form = shop_select.get('login_form', {})
    background = login_form.get('background')

    if not shop_select:
        return redirect('/404')
    return render_template('wifi_portal/register.html',
                           login_form=login_form,
                           shop_select=shop_select,
                           user_login=user_login)


@app.route('/preview_init_camp/<shop_id_select>/<type_page>',
           methods=['GET', 'POST'])
@login_required
def preview_init(shop_id_select, type_page):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if type_page == "image_register":
        image = session.get('image_register')
        if not image:
            image = '2/205b2f83eb39'
        return render_template('wifi_portal_preview/image_preview.html',
                               image=image,
                               user_login=user_login)
    if type_page == "collect_register":
        login_form = session.get('collect_register')
        return render_template('wifi_portal/register.html',
                               login_form=login_form,
                               shop_select=shop_select)
    if type_page == "connect_register" or type_page == 'connect_return':
        connect_success = {'hotspot_method': 'default'}
        return render_template(
            'wifi_portal/connect_success.html',
            connect_success=connect_success,
            shop=shop_select,
        )
    if type_page == "image_return":
        image = session.get('image_return')
        if not image:
            image = shop_select.get('background')
        return render_template('wifi_portal_preview/image_preview.html',
                               image=image,
                               user_login=user_login)
    if type_page == "survey":
        survey_id = session.get('survey_return')
        if survey_id and len(survey_id) > 0:
            survey_item = api.get_survey_splash(shop_id_select, survey_id)
            merchant_id = shop_select.get('merchant_id')
            survey_type = survey_item.get('survey_type')
            if survey_type == "multi_select":
                return render_template('wifi_portal/survey.html',
                                       shop_select=shop_select,
                                       shop_id_select=shop_id_select,
                                       survey_item=survey_item)
            elif survey_type == "one_select":
                return render_template('wifi_portal/survey_single.html',
                                       shop_select=shop_select,
                                       shop_id_select=shop_id_select,
                                       survey_item=survey_item)
            elif survey_type == 'rating':
                return render_template('wifi_portal/survey_rating.html',
                                       shop_select=shop_select,
                                       shop_id_select=shop_id_select,
                                       survey_item=survey_item)
    if type_page == "0":
        return render_template('new_hotspot/404.html')


@app.route('/save_cache/<shop_id_select>/<type_page>', methods=['POST'])
@login_required
def save_cache(shop_id_select, type_page):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if type_page == "register" or type_page == "plus_register":
        phone_visible = request.form.get('phone_visible')
        phone_visible = True if phone_visible else False
        phone_require = request.form.get('phone_require')
        phone_require = True if phone_require else False

        name_visible = request.form.get('name_visible')
        name_visible = True if name_visible else False
        name_require = request.form.get('name_require')
        name_require = True if name_require else False

        birthday_visible = request.form.get('birthday_visible')
        birthday_visible = True if birthday_visible else False
        birthday_require = request.form.get('birthday_require')
        birthday_require = True if birthday_require else False

        gender_visible = request.form.get('gender_visible')
        gender_visible = True if gender_visible else False
        gender_require = request.form.get('gender_require')
        gender_require = True if gender_require else False

        email_visible = request.form.get('email_visible')
        email_visible = True if email_visible else False
        email_require = request.form.get('email_require')
        email_require = True if email_require else False

        year_birthday_visible = request.form.get('year_birthday_visible')
        year_birthday_visible = True if year_birthday_visible else False
        year_birthday_require = request.form.get('year_birthday_require')
        year_birthday_require = True if year_birthday_require else False

        welcome_text = request.form.get('welcome_text')
        welcome_button = request.form.get('welcome_button')
        birthday_text = request.form.get('birthday_text')
        tag_input = request.form.get('real_tags_filter')
        tags = []
        if tag_input and len(tag_input) > 0:
            tags_split = tag_input.split(',')
            if len(tags_split) > 0:
                for tag in tags_split:
                    tag = tag.strip()
                    if len(tag) > 0:
                        tags.append(ObjectId(tag))

        company_visible = request.form.get('company_visible')
        company_visible = True if company_visible else False
        company_require = request.form.get('company_require')
        company_require = True if company_require else False

        company_role_visible = request.form.get('company_role_visible')
        company_role_visible = True if company_role_visible else False
        company_role_require = request.form.get('company_role_require')
        company_role_require = True if company_role_require else False

        vocation = request.form.get('vocation_visible')
        vocation = True if vocation else False
        vocation_require = request.form.get('vocation_require')
        vocation_require = True if vocation_require else False

        connect_with_facebook = request.form.get('connect_with_facebook')
        connect_with_facebook = True if connect_with_facebook else False

        connect_with_zalo = request.form.get('connect_with_zalo')
        connect_with_zalo = True if connect_with_zalo else False
        allow_access_friend_zalo = request.form.get('allow_access_friend_zalo')
        allow_access_friend_zalo = True if allow_access_friend_zalo else False

        connect_with_messenger = request.form.get('connect_with_messenger')
        connect_with_messenger = True if connect_with_messenger else False

        otp = request.form.get('otp')

        otp_val = True if str(otp) == 'true' else False
        background_register = api.get_background_register(shop_id_select)
        background_filename_fr = None
        background_fr = request.files.get('background_fr')
        if background_fr:
            if allowed_file(background_fr.filename):
                background_filename_fr = storage_api.save_new_file(
                    background_fr)
            else:
                error = gettext("Hay_chon_dung_dinh_dang_anh")
                return json.dumps({'result': False, 'msg': error})
        else:
            background_filename_fr = background_register
        form_settings = {
            'phone': phone_visible,
            'name': name_visible,
            'birthday': birthday_visible,
            'year_birthday': year_birthday_visible,
            'gender': gender_visible,
            'email': email_visible,
            'welcome_text': welcome_text,
            'welcome_button': welcome_button,
            'birthday_text': birthday_text,
            'phone_require': phone_require,
            'name_require': name_require,
            'birthday_require': birthday_require,
            'gender_require': gender_require,
            'email_require': email_require,
            'year_birthday_require': year_birthday_require,
            'otp': otp_val,
            'company': company_visible,
            'company_require': company_require,
            'company_role': company_role_visible,
            'company_role_require': company_role_require,
            'vocation': vocation,
            'vocation_require': vocation_require,
            'connect_with_facebook': connect_with_facebook,
            'connect_with_zalo': connect_with_zalo,
            'allow_access_friend_zalo': allow_access_friend_zalo,
            'connect_with_messenger': connect_with_messenger,
            'tag': tags,
            'background': background_filename_fr,
        }
        session['login_form'] = form_settings
        return json.dumps({'result': True})
    if type_page == 'birthday':
        title = request.form.get('title')
        content = request.form.get('content')
        connect_button = request.form.get('connect_button')
        photo_name = None
        photo = request.files.get('photo')
        if photo:
            if allowed_file(photo.filename):
                photo_name = storage_api.save_new_file(photo)
            else:
                error = gettext("Hay_chon_dung_dinh_dang_anh")
                return json.dumps({'result': False, 'msg': error})
        page = {
            'title': title,
            'content': content,
            'connect_button': connect_button,
            'photo': photo_name
        }
        session['birthday_page'] = page
        return json.dumps({'result': True})
    if type_page == 'youtube':
        link_youtube = request.form.get('link_youtube')
        connect_button = request.form.get('connect_button')
        page = {
            'link_youtube': link_youtube,
            'connect_button': connect_button,
        }
        session['youtube_page'] = page
        return json.dumps({'result': True})


@app.route('/preview_wifi/<shop_id_select>/<type_page>', methods=['GET'])
@login_required
def preview_register_wifi_wizard(shop_id_select, type_page):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if not shop_id:
        return redirect('/404')
    if type_page == "register" or type_page == "plus_register":
        form_settings = session.get('login_form')
        return render_template('wifi_portal/register.html',
                               login_form=form_settings,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               user_login=user_login)
    if type_page == "birthday":
        page = session.get('birthday_page')
        content = page['content']
        title = page['title']
        return render_template(
            'wifi_portal/event_v2.html',
            user=user_login,
            shop=shop,
            shop_id=shop_id,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            card=page,
            content=content,
            title=title,
        )
    if type_page == "youtube":
        page = session.get('youtube_page')
        link_youtube = page['link_youtube']
        split_link = link_youtube.split('=')
        id_link = split_link[1]
        content = '<iframe height="400" src="https://www.youtube.com/embed/' + id_link + \
                  '?autoplay=1&mute=1" frameborder="0" allow="autoplay" allowfullscreen></iframe>'
        return render_template('wifi_portal/event_v2.html',
                               user=user_login,
                               shop=shop,
                               shop_id=shop_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               card=page,
                               content=content,
                               type_page="youtube")


@app.route('/preview/<shop_id_select>/plus_register', methods=['GET', 'POST'])
@login_required
def preview_plus_register(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    plus_login_form = shop_select.get('plus_login_form', {})
    shop_id = shop_select['_id']
    if not shop_select:
        return redirect('/404')
    return render_template('wifi_portal/register.html',
                           shop=shop,
                           login_form=plus_login_form,
                           shop_select=shop_select,
                           shop_id=shop_id,
                           user_login=user_login)


@app.route('/email_templates', methods=['GET', 'POST'])
@login_required
def email_templates():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    user_login = g.user
    page = int(request.args.get('page', 1))
    shop = g.shop
    shop_id = g.shop_id
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    list_email_templates = api.list_email_template(merchant_id, page,
                                                   settings.ITEMS_PER_PAGE)
    count_email_template = api.count_email_template(merchant_id)
    pagination = Pagination(page=page,
                            total=count_email_template,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/email_templates.html',
                           merchant=merchant,
                           user_login=user_login,
                           shop_in_mer=shop_in_mer,
                           pagination=pagination,
                           shop_id=shop_id,
                           list_email_templates=list_email_templates,
                           total_email=count_email_template)


@app.route('/email_templates/<email_id>', methods=['GET', 'POST'])
@login_required
def email_templates_item(email_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    user_login = g.user
    if request.method == 'GET':
        email_template = None
        try:
            email_template = api.merchant_email_template_item(
                merchant_id, email_id)

        except:
            pass

        if not email_template:
            return redirect('/email_templates')
        else:
            return render_template('nextify/email_builder_v2.html',
                                   shop=shop,
                                   user_login=user_login,
                                   merchant_id=merchant_id,
                                   shop_in_mer=shop_in_mer,
                                   merchant=merchant,
                                   email_sample=email_template,
                                   update_template=True,
                                   email_id=email_id)
    else:
        name = request.form.get('name')
        note = request.form.get('note')
        html = request.form.get('html')
        design = request.form.get('design')
        api.update_email_merchant_template_item(merchant_id,
                                                email_id,
                                                name=name,
                                                note=note,
                                                code=html,
                                                design=design)
        return redirect('/email_templates')


@app.route('/email_templates/<email_id>/preview', methods=['GET', 'POST'])
@login_required
def email_templates_item_preview(email_id):
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(merchant_id)
    user_login = g.user
    email_template = None
    try:
        email_template = api.merchant_email_template_item(
            merchant_id, email_id)

    except:
        pass

    if not email_template:
        return redirect('/email_templates')
    else:
        return render_template('email/email_render.html',
                               shop=shop,
                               user_login=user_login,
                               merchant_id=merchant_id,
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               email=email_template,
                               update_template=True,
                               email_id=email_id)


@app.route('/home', methods=['GET'])
@login_required
def home():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    return render_template(
        'nextify/home.html',
        shop=shop,
        user_login=user_login,
        merchant_id=merchant_id,
        merchant=merchant,
    )


@app.route('/merchant_reports', methods=['GET'])
@login_required
def v2_merchant_reports():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    total_employee = api.get_employee_by_mer(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    merchant = api.get_merchant(merchant_id)
    today = datetime.now().date()
    date_from = today - timedelta(days=today.weekday())
    date_to = date_from + timedelta(days=7)
    date_from = datetime.strftime(date_from, '%d-%m-%Y')
    date_to = datetime.strftime(date_to, '%d-%m-%Y')
    locations_pie = []
    package_merchant = api.get_name_package_by_merchant_id(merchant_id)
    return render_template('nextify/overview.html',
                           shop=shop,
                           locations_pie=locations_pie,
                           date_to=date_to,
                           date_from=date_from,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           package_merchant=package_merchant,
                           total_employee=total_employee)


@app.route('/merchant_reports/customers', methods=['GET'])
@login_required
def overview_customers():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')
    total_customers = 0
    graph_report = {}
    total_customers_ex_percent = 0
    if range_time != 'all':
        range_time = int(range_time)
        ex_start_time = datetime.now() - timedelta(days=int(range_time))
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_customers(
                merchant_id,
                start_time=ex_start_time,
                shop_id=shop_id_select,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
        else:
            total_customers, graph_report = overview.count_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_customers(
                merchant_id,
                start_time=ex_start_time,
                shop_id=None,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
    else:
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
        else:
            total_customers, graph_report = overview.count_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
    return render_template(
        'overview/customers.html',
        range_time=range_time,
        merchant_id=merchant_id,
        shop_id_select=shop_id_select,
        total_customers=total_customers,
        total_customers_ex_percent=total_customers_ex_percent,
        graph_report=graph_report)


@app.route('/merchant_reports/visits', methods=['GET'])
@login_required
def overview_visits():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')
    total_customers = 0
    total_customers_ex_percent = 0
    graph_report = {}
    if range_time != 'all':
        range_time = int(range_time)
        ex_start_time = datetime.now() - timedelta(days=int(range_time))
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_vists(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_vists(
                merchant_id,
                start_time=ex_start_time,
                shop_id=shop_id_select,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
        else:
            total_customers, graph_report = overview.count_vists(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_vists(
                merchant_id,
                start_time=ex_start_time,
                shop_id=None,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
    else:
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_vists(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
        else:
            total_customers, graph_report = overview.count_vists(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)

    return render_template(
        'overview/visits.html',
        range_time=range_time,
        merchant_id=merchant_id,
        shop_id_select=shop_id_select,
        total_customers=total_customers,
        total_customers_ex_percent=total_customers_ex_percent,
        graph_report=graph_report)


@app.route('/merchant_reports/new_customers', methods=['GET'])
@login_required
def overview_new_customers():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')
    total_customers = 0
    total_customers_ex_percent = 0
    graph_report = {}
    if range_time != 'all':
        range_time = int(range_time)
        ex_start_time = datetime.now() - timedelta(days=int(range_time))
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_new_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_new_customers(
                merchant_id,
                start_time=ex_start_time,
                shop_id=shop_id_select,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
        else:
            total_customers, graph_report = overview.count_new_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_new_customers(
                merchant_id,
                start_time=ex_start_time,
                shop_id=None,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
    else:
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_new_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
        else:
            total_customers, graph_report = overview.count_new_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)

    return render_template(
        'overview/new_customers.html',
        range_time=range_time,
        merchant_id=merchant_id,
        shop_id_select=shop_id_select,
        total_customers=total_customers,
        total_customers_ex_percent=total_customers_ex_percent,
        graph_report=graph_report)


@app.route('/merchant_reports/return_customers', methods=['GET'])
@login_required
def overview_return_customers():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')
    total_customers = 0
    total_customers_ex_percent = 0
    graph_report = {}
    if range_time != 'all':
        range_time = int(range_time)
        ex_start_time = datetime.now() - timedelta(days=int(range_time))
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_return_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_return_customers(
                merchant_id,
                start_time=ex_start_time,
                shop_id=shop_id_select,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
        else:
            total_customers, graph_report = overview.count_return_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_return_customers(
                merchant_id,
                start_time=ex_start_time,
                shop_id=None,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
    else:
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_return_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
        else:
            total_customers, graph_report = overview.count_return_customers(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
    return render_template(
        'overview/return_customers.html',
        range_time=range_time,
        merchant_id=merchant_id,
        shop_id_select=shop_id_select,
        total_customers=total_customers,
        total_customers_ex_percent=total_customers_ex_percent,
        graph_report=graph_report)


@app.route('/merchant_reports/smart_message', methods=['GET'])
@login_required
def overview_smart_message():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')
    total_customers = 0
    total_customers_ex_percent = 0
    graph_report = {}
    if range_time != 'all':
        range_time = int(range_time)
        ex_start_time = datetime.now() - timedelta(days=int(range_time))
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_message_send(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_message_send(
                merchant_id,
                start_time=ex_start_time,
                shop_id=shop_id_select,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
        else:
            total_customers, graph_report = overview.count_message_send(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_message_send(
                merchant_id,
                start_time=ex_start_time,
                shop_id=None,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
    else:
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_message_send(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
        else:
            total_customers, graph_report = overview.count_message_send(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
    return render_template(
        'overview/smart_message.html',
        range_time=range_time,
        merchant_id=merchant_id,
        shop_id_select=shop_id_select,
        total_customers=total_customers,
        total_customers_ex_percent=total_customers_ex_percent,
        graph_report=graph_report)


@app.route('/merchant_reports/walkthrough', methods=['GET'])
@login_required
def overview_walkthrough():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')
    total_customers = 0
    total_customers_ex_percent = 0
    graph_report = {}
    if range_time != 'all':
        range_time = int(range_time)
        ex_start_time = datetime.now() - timedelta(days=int(range_time))
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_walk_throughs(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_walk_throughs(
                merchant_id,
                start_time=ex_start_time,
                shop_id=shop_id_select,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
        else:
            total_customers, graph_report = overview.count_walk_throughs(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
            total_customers_ex_time, graph_report_ex = overview.count_walk_throughs(
                merchant_id,
                start_time=ex_start_time,
                shop_id=None,
                time_range=range_time)
            total_customers_ex_percent = percentage(total_customers,
                                                    total_customers_ex_time)
    else:
        if shop_id_select != 'all':
            total_customers, graph_report = overview.count_walk_throughs(
                merchant_id,
                start_time=datetime.now(),
                shop_id=shop_id_select,
                time_range=range_time,
                is_report=True)
        else:
            total_customers, graph_report = overview.count_walk_throughs(
                merchant_id,
                start_time=datetime.now(),
                shop_id=None,
                time_range=range_time,
                is_report=True)
    return render_template(
        'overview/walkthrough.html',
        range_time=range_time,
        merchant_id=merchant_id,
        shop_id_select=shop_id_select,
        total_customers=total_customers,
        total_customers_ex_percent=total_customers_ex_percent,
        graph_report=graph_report)


@app.route('/merchant_reports/locations', methods=['GET'])
@login_required
def overview_locations():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')
    cus_by_location = []
    label = []
    dataset = []
    if range_time != 'all':
        range_time = int(range_time)
    if shop_id_select != 'all':
        cus_by_location = overview.count_customers_by_locations(
            merchant_id,
            start_time=datetime.now(),
            shop_id=shop_id_select,
            time_range=range_time)
    else:
        cus_by_location = overview.count_customers_by_locations(
            merchant_id,
            start_time=datetime.now(),
            shop_id=None,
            time_range=range_time)
    for loc in cus_by_location:
        label.append(list(loc.keys())[0])
        dataset.append(list(loc.values())[0])

    return render_template('overview/location_customers.html',
                           range_time=range_time,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           cus_by_location=cus_by_location,
                           label=json.dumps(label),
                           dataset=json.dumps(dataset))


@app.route('/merchant_reports/devices', methods=['GET'])
@login_required
def overview_devices():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')

    cus_by_devices = []
    label = []
    dataset = []
    if range_time != 'all':
        range_time = int(range_time)
    if shop_id_select != 'all':
        cus_by_devices = overview.count_customers_by_device(
            merchant_id,
            start_time=datetime.now(),
            shop_id=shop_id_select,
            time_range=range_time)
    else:
        cus_by_devices = overview.count_customers_by_device(
            merchant_id,
            start_time=datetime.now(),
            shop_id=None,
            time_range=range_time)
    for loc in cus_by_devices:
        label.append(list(loc.keys())[0])
        dataset.append(list(loc.values())[0])

    return render_template('overview/user_devices.html',
                           range_time=range_time,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           cus_by_devices=cus_by_devices,
                           label=json.dumps(label),
                           dataset=json.dumps(dataset))


@app.route('/merchant_reports/user_visits', methods=['GET'])
@login_required
def overview_user_visits():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')

    cus_by_visit = []
    label = []
    dataset = []
    if range_time != 'all':
        range_time = int(range_time)
    if shop_id_select != 'all':
        cus_by_visit = overview.count_customers_by_visits(
            merchant_id,
            start_time=datetime.now(),
            shop_id=shop_id_select,
            time_range=range_time)
    else:
        cus_by_visit = overview.count_customers_by_visits(
            merchant_id,
            start_time=datetime.now(),
            shop_id=None,
            time_range=range_time)
    for loc in cus_by_visit:
        label.append(list(loc.keys())[0])
        dataset.append(list(loc.values())[0])
    return render_template('overview/user_by_visits.html',
                           range_time=range_time,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           cus_by_visit=cus_by_visit,
                           label=json.dumps(label),
                           dataset=json.dumps(dataset))


@app.route('/merchant_reports/user_hours', methods=['GET'])
@login_required
def overview_user_hours():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')

    cus_by_hours = []
    label = []
    dataset = []
    if range_time != 'all':
        range_time = int(range_time)
    if shop_id_select != 'all':
        cus_by_hours = overview.count_customers_by_hours(
            merchant_id,
            start_time=datetime.now(),
            shop_id=shop_id_select,
            time_range=range_time)
    else:
        cus_by_hours = overview.count_customers_by_hours(
            merchant_id,
            start_time=datetime.now(),
            shop_id=None,
            time_range=range_time)
    for loc in cus_by_hours:
        label.append(loc[0])
        dataset.append(loc[1])

    return render_template('overview/user_by_hours.html',
                           range_time=range_time,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           cus_by_hours=cus_by_hours,
                           label=json.dumps(label),
                           dataset=json.dumps(dataset))


@app.route('/merchant_reports/user_days', methods=['GET'])
@login_required
def overview_user_days():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    range_time = request.args.get('range_time')
    shop_id_select = request.args.get('shop_id_select')

    cus_by_day = []
    label = []
    dataset = []
    if range_time != 'all':
        range_time = int(range_time)
    if shop_id_select != 'all':
        cus_by_day = overview.count_customers_by_day(merchant_id,
                                                     start_time=datetime.now(),
                                                     shop_id=shop_id_select,
                                                     time_range=range_time)
    else:
        cus_by_day = overview.count_customers_by_day(merchant_id,
                                                     start_time=datetime.now(),
                                                     shop_id=None,
                                                     time_range=range_time)
    cus_by_day = sorted(cus_by_day, key=lambda d: d['_id'])
    for loc in cus_by_day:
        if loc.get('_id'):
            label.append(settings.DAY_IN_WEEEK.get(str(loc.get('_id'))))
            dataset.append(loc.get('count'))

    return render_template('overview/user_by_day.html',
                           range_time=range_time,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           cus_by_day=cus_by_day,
                           label=json.dumps(label),
                           dataset=json.dumps(dataset))


@app.route('/advertising', methods=['GET', 'POST'])
@login_required
def advertising():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        merchant = api.get_merchant(merchant_id)
        merchant_fb_setting = api.get_info_fb_setting(merchant_id)
        user_info_login = ""
        list_post_show = ""
        total_post = 1
        post_engagement_total = 0
        data_chart = ""
        clicks = 0
        impressions = 0
        if merchant_fb_setting:
            user_id_fb = merchant_fb_setting.get("fb_user_id")
            user_info_login = fb_api.get_user_info_by_user_id(
                user_id=user_id_fb)
            result = api.get_post_fb(user_id_fb, page, 5)
            data_chart = api.insights_all_ads(user_id_fb)
            list_post_show = result.get('result')
            post_engagement_total = data_chart.get('total_post')
            clicks = data_chart.get('total_clicks')
            impressions = data_chart.get('total_impressison')
            total_post = api.get_total_post_fb(user_id_fb)
        pagination = Pagination(page=page,
                                total=total_post,
                                per_page=5,
                                css_framework='bootstrap3')

        return render_template('nextify/advertising.html',
                               shop=shop,
                               merchant_id=merchant_id,
                               merchant_fb_setting=merchant_fb_setting,
                               post_engagement_total=post_engagement_total,
                               clicks=clicks,
                               impressions=impressions,
                               list_post_show=list_post_show,
                               user_info_login=user_info_login,
                               data_chart=json.dumps(data_chart),
                               pagination=pagination,
                               merchant=merchant)
    else:
        page = 1
        merchant = api.get_merchant(merchant_id)
        merchant_fb_setting = api.get_info_fb_setting(merchant_id)
        created_time_ts = request.form.get("created_time_ts")
        completed_time_ts = request.form.get("completed_time_ts")
        user_info_login = ""
        list_post_show = ""
        total_post = 1
        post_engagement_total = 0
        clicks = 0
        impressions = 0
        if merchant_fb_setting:
            user_id_fb = merchant_fb_setting.get("fb_user_id")
            user_info_login = fb_api.get_user_info_by_user_id(
                user_id=user_id_fb)
            result = api.get_post_fb(user_id_fb, page, 5, created_time_ts,
                                     completed_time_ts)
            data_chart = api.insights_all_ads(
                user_id_fb,
                created_time_ts=created_time_ts,
                completed_time_ts=completed_time_ts)
            list_post_show = result.get('result')
            post_engagement_total = data_chart.get('total_post')
            clicks = data_chart.get('total_clicks')
            impressions = data_chart.get('total_impressison')
            total_post = api.get_total_post_fb(
                user_id_fb,
                created_time_ts=created_time_ts,
                completed_time_ts=completed_time_ts)

        pagination = Pagination(page=page,
                                total=total_post,
                                per_page=5,
                                css_framework='bootstrap3')

        return render_template('nextify/advertising_time.html',
                               shop=shop,
                               merchant_id=merchant_id,
                               merchant_fb_setting=merchant_fb_setting,
                               post_engagement_total=post_engagement_total,
                               completed_time_ts=completed_time_ts,
                               created_time_ts=created_time_ts,
                               clicks=clicks,
                               impressions=impressions,
                               data_chart=json.dumps(data_chart),
                               list_post_show=list_post_show,
                               user_info_login=user_info_login,
                               pagination=pagination,
                               merchant=merchant)


@app.route('/email_builder', methods=['GET'])
@login_required
def email_builder():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    merchant = api.get_merchant(merchant_id)
    return render_template(
        'nextify/email_builder.html',
        shop=shop,
        user_login=user_login,
        merchant_id=merchant_id,
        shop_in_mer=shop_in_mer,
        merchant=merchant,
    )


@app.route('/manage_emails', methods=['GET', 'POST'])
# @basic_auth.required
def manage_emails():
    page = int(request.args.get('page', 1))
    emails = api.get_email_sample_template(page, settings.ITEMS_PER_PAGE)
    email_count = api.get_email_sample_template_count()
    merchant = None
    pagination = Pagination(page=page,
                            total=email_count,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('email/list_email_templates.html',
                           merchant=merchant,
                           page=page,
                           emails=emails,
                           pagination=pagination,
                           total=email_count)


@app.route('/manage_emails/<email_id>', methods=['GET', 'POST'])
# @basic_auth.required
@login_required
def manage_email_template_item(email_id):
    if request.method == 'GET':
        shop = g.shop
        shop_id = g.shop_id
        user_login = g.user
        merchant_id = shop.get('merchant_id')
        merchant = api.get_merchant(merchant_id)
        email = {}
        if email_id != 'add':
            email = api.get_email_sample_template_item(email_id)

        return render_template('email/email_template_item.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               email=email,
                               email_id=email_id)
    else:

        name = request.form.get('name')
        code = request.form.get('code')
        thumb = request.files.get('thumb')
        design = request.form.get('design')
        avatar_filename = None
        if thumb and thumb.filename.rsplit('.',
                                           1)[1].lower() in ALLOWED_EXTENSIONS:
            avatar_filename = storage_api.save_new_file(thumb)

        api.update_sample_template_item(email_id,
                                        name=name,
                                        thumb=avatar_filename,
                                        code=code,
                                        design=design)
        return redirect('/manage_emails')


@app.route('/manage_emails/<email_id>/preview', methods=['GET', 'POST'])
@basic_auth.required
def preview_email_template(email_id):
    email = api.get_email_sample_template_item(email_id)

    return render_template('email/email_render.html', email=email)


@app.route('/box', methods=['GET', 'POST'])
@basic_auth.required
def wifi_box():
    if request.method == 'GET':
        return render_template('box/setup.html')
    else:
        pass


@app.route('/wifi_profiles', methods=['GET', 'POST'])
@login_required
def wifi_profiles():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    page = int(request.args.get('page', 1))
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    merchant = api.get_merchant(merchant_id)
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]

    profiles = api.list_wifi_profiles(merchant_id, page,
                                      settings.ITEMS_PER_PAGE)
    total_profile = api.total_wifi_profiles(merchant_id)

    pagination = Pagination(page=page,
                            total=total_profile,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/profiles_wifi.html',
                           shop=shop,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           tags=tags,
                           profiles=profiles,
                           total_profile=total_profile,
                           pagination=pagination)


@app.route('/wifi_profiles/<profile>/remove', methods=['GET'])
@login_required
def wifi_profiles_remove(profile):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    api.remove_wifi_profile_by_id(merchant_id, profile)
    return redirect('/wifi_profiles')


@app.route('/wifi_profiles/<profile>', methods=['POST'])
@login_required
def wifi_profiles_item(profile):
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    name = request.form.get('name')
    session_timeout = request.form.get('session_timeout', '')
    down_bw = request.form.get('down_bw', '')
    up_bw = request.form.get('up_bw', '')
    profile_type = request.form.get('profile_type')
    pricing = request.form.get('pricing', '')
    active_request = request.form.get('active')
    expire = request.form.get('expire', 4)
    active = True if str(active_request) == 'on' else False
    tags = request.form.get('real_tags_filter', '')
    error = ''
    tags_array = []
    if tags and len(tags) > 0:
        tags_array = tags.split(',')
    if profile == 'add':
        slug = slugify(name)
        item_slug = api.check_wifi_profile_by_slug(merchant_id, slug)
        if item_slug:
            error = gettext("Profile_da_ton_tai,_vui_long_dat_ten_khac")
            return json.dumps({'error': error})
        api.item_wifi_profile(merchant_id,
                              profile_id=profile,
                              name=name,
                              session_timeout=session_timeout,
                              down_bw=down_bw,
                              up_bw=up_bw,
                              profile_type=profile_type,
                              pricing=pricing,
                              tags=tags_array,
                              active=active,
                              expire=expire)
        return json.dumps({'result': 'ok'})

    api.item_wifi_profile(merchant_id,
                          profile_id=profile,
                          name=name,
                          session_timeout=session_timeout,
                          down_bw=down_bw,
                          up_bw=up_bw,
                          profile_type=profile_type,
                          pricing=pricing,
                          tags=tags_array,
                          active=active,
                          expire=expire)

    return json.dumps({'result': '200'})


@app.route('/wifi_profiles_code', methods=['GET', 'POST'])
@login_required
def wifi_profiles_code():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    page = int(request.args.get('page', 1))
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    merchant = api.get_merchant(merchant_id)

    profiles = api.list_wifi_profiles_code(merchant_id, page,
                                           settings.ITEMS_PER_PAGE)
    total_profile = api.total_wifi_profiles_code(merchant_id)

    pagination = Pagination(page=page,
                            total=total_profile,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/wifi_profiles_code.html',
                           shop=shop,
                           user_login=user_login,
                           merchant_id=merchant_id,
                           shop_in_mer=shop_in_mer,
                           merchant=merchant,
                           profiles=profiles,
                           total_profile=total_profile,
                           pagination=pagination)


@app.route('/<merchant_id>/wificode', methods=['GET', 'POST'])
def gen_merchant_profile_code(merchant_id):
    shops = api.get_shop_by_merchant(merchant_id)
    profiles = api.list_all_wifi_profiles(merchant_id)
    if request.method == 'GET':
        return render_template('nextify/vinpearl_code.html',
                               shops=shops,
                               profiles=profiles,
                               merchant_id=merchant_id)
    else:
        phone = request.form.get('phone')
        location = request.form.get('location')
        profile = request.form.get('profile')
        email = request.form.get('email')
        wifi_code = api.insert_wifi_profiles_code(merchant_id, location,
                                                  profile, phone, email)
        return render_template('nextify/vinpearl_code.html',
                               shops=shops,
                               profiles=profiles,
                               location=location,
                               profile=profile,
                               phone=phone,
                               email=email,
                               wifi_code=wifi_code,
                               merchant_id=merchant_id)


@app.route('/vincode', methods=['GET', 'POST'])
def gen_profile_code():
    merchant_id = '5c861625aeb2ff77d5ab50e5'
    shops = api.get_shop_by_merchant(merchant_id)
    profiles = api.list_all_wifi_profiles(merchant_id)
    if request.method == 'GET':
        return render_template('nextify/vinpearl_code.html',
                               shops=shops,
                               profiles=profiles)
    else:
        phone = request.form.get('phone')
        location = request.form.get('location')
        profile = request.form.get('profile')
        email = request.form.get('email')
        wifi_code = api.insert_wifi_profiles_code(merchant_id, location,
                                                  profile, phone, email)
        return render_template('nextify/vinpearl_code.html',
                               shops=shops,
                               profiles=profiles,
                               location=location,
                               profile=profile,
                               phone=phone,
                               email=email,
                               wifi_code=wifi_code)


@app.route('/fonts/tinymce.woff', methods=['GET'])
def gen_tiny_mce_font_woff():
    return send_from_directory('static', 'fonts/tinymce.woff')


@app.route('/fonts/tinymce.ttf', methods=['GET'])
def gen_tiny_mce_font_ttf():
    return send_from_directory('static', 'fonts/tinymce.ttf')


@app.route('/request_integration_brandname', methods=['POST'])
@login_required
def request_integration_brandname():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    sms_provider = request.form.get('sms_provider')
    brand_name = request.form.get('brand_name')
    check_request = api.DATABASE.request_integration_sms.find_one(
        {'merchant_id': merchant_id})
    if check_request:
        api.DATABASE.request_integration_sms.update(
            {'merchant_id': merchant_id}, {
                '$set': {
                    'sms_provider': sms_provider,
                    'brand_name': brand_name,
                    'when': time.time(),
                    'active': '1'
                }
            })
    else:
        api.DATABASE.request_integration_sms.insert({
            'merchant_id': merchant_id,
            'sms_provider': sms_provider,
            'brand_name': brand_name,
            'when': time.time(),
            'active': '1'
        })

    return json.dumps({'result': True})


@app.route('/request_register_brandname', methods=['POST'])
@login_required
def request_register_brandname():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    brand_name = request.form.get('brand_name')
    categories = request.form.get('categories')
    telcos = request.form.get('telcos')
    check_request = api.DATABASE.request_register_sms.find_one(
        {'merchant_id': merchant_id})
    if check_request:
        api.DATABASE.request_register_sms.update({'merchant_id': merchant_id},
                                                 {
                                                     'brand_name': brand_name,
                                                     'categories': categories,
                                                     'telcos': telcos,
                                                     'when': time.time(),
                                                     'active': '1'
                                                 })
    else:
        api.DATABASE.request_register_sms.insert({
            'merchant_id': merchant_id,
            'brand_name': brand_name,
            'categories': categories,
            'telcos': telcos,
            'when': time.time(),
            'active': '1'
        })
    return json.dumps({'result': True})


@app.route('/tags', methods=['GET'])
@login_required
def tags_manager():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    page = int(request.args.get('page', 1))
    tags = api.list_item_tags(merchant_id, page, settings.ITEMS_PER_PAGE)

    total = api.total_tags(merchant_id)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')

    return render_template('nextify/tags_manager.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           tags=tags,
                           total=total,
                           pagination=pagination)


@app.route('/tags/<tag_id>_remove', methods=['GET'])
@login_required
def tag_remove(tag_id):
    check_remove = api.remove_tag(tag_id)
    if check_remove:
        return json.dumps({'result': True})
    return json.dumps({'result': False})


@app.route("/forgot", methods=['GET', 'POST'])
def forget():
    global URLSafeTimedSerializer_salt
    URLSafeTimedSerializer_salt = os.urandom(4)

    if request.method == "POST":
        # if 'vmarketing.viettel.vn' in request.url:
        # # if '0.0.0.0:8096' in request.url:
        #     phone = request.form.get('phone')
        #     phone = str(phone).strip()
        #     phone = api.get_phone_number(phone)
        #     merchant = api.get_merchant_by_phone(phone)
        #     if not phone:
        #         return render_template('forgot_password_page_phone.html',
        #                                error=gettext(
        #                                    "Nhap_sai_so_dien_thoai!"))

        #     if not captcha.validate():
        #         error = "Mã captcha chưa đúng, vui lòng thử lại."
        #         return render_template("forgot_password_page_phone.html", phone=phone, error=error)
        #     if merchant:
        #         punctuation = "@#$"
        #         password = ''.join(
        #             (random.choice(string.ascii_lowercase + string.ascii_uppercase + punctuation + string.digits) for i
        #              in range(8)))
        #         merchant_id = merchant.get('_id')
        #         user_sms = settings.VIETTEL_USER_SMS
        #         pass_sms = settings.VIETTEL_PASS_SMS
        #         brand_name = settings.VIETTEL_BRAND_NAME
        #         message = settings.VIETTEL_MESSAGE + password
        #         result = sms_api.send_sms_viettel(merchant_id, user_sms, pass_sms, brand_name, phone,
        #                                           message, activity_id=None, camp_id=None)
        #         api.update_merchants(merchant_id=merchant_id, password=password)
        #         return render_template('forgot_password_page_3.html', merchant_email=phone, text='True')
        #     else:
        #         return render_template('forgot_password_page_phone.html',
        #                                error="Không có account nào tồn tại với số điện thoại này!")
        # else:
        email = request.form.get('email')
        email = str(email).strip()
        merchant = api.get_merchant_by_email(email)
        is_email = validate_email(email)
        if not is_email:
            return render_template(
                'forgot_password_page.html',
                error=gettext("Hay_nhap_email_dung_dinh_dang!"))

        if not captcha.validate():
            error = "Mã captcha chưa đúng, vui lòng thử lại."
            return render_template("forgot_password_page.html",
                                   email=email,
                                   error=error)

        if merchant:
            s = URLSafeTimedSerializer(URLSafeTimedSerializer_salt)
            merchant_id = str(merchant['_id'])
            token = s.dumps(merchant_id, salt='nextify')

            VHT_id = '5cd80e8d57edfc026a4158f9'
            VT_id = '5cde180357edfc45b0a726cb'
            Vmarketing_id = "600a89ccf12e8e8e72022a4a"

            partner = str(merchant.get('partner', ''))
            merchant_name = merchant.get('name')
            confirm_url = ''
            if partner == Vmarketing_id:
                confirm_url = 'https://crm.vmarketing.viettel.vn/confirm_reset_email/{}'.format(
                    token)
            if partner == VT_id:
                confirm_url = 'https://vwifi.viettel.vn/confirm_reset_email/{}'.format(
                    token)
            if partner == VHT_id:
                confirm_url = 'https://crm.crmx.com.vn/confirm_reset_email/{}'.format(
                    token)
            else:
                confirm_url = 'https://crm.nextify.vn/confirm_reset_email/{}'.format(
                    token)
            email_content = render_template('forgotPassword_mail_content.html',
                                            title='mail content',
                                            confirm_url=confirm_url,
                                            name=merchant_name)
            # Gui email
            send_by_mail_gun(merchant_name, email,
                             "Thay đổi mật khẩu hệ thống CRM", email_content)
            return render_template('forgot_password_page_3.html',
                                   merchant_email=email,
                                   text=None)

        else:
            return render_template(
                'forgot_password_page.html',
                email_error="Không có account nào tồn tại với email này!")
    # if 'vmarketing.viettel.vn' in request.url:
    # # if '0.0.0.0:8096' in  request.url:
    #     return render_template('forgot_password_page_phone.html')
    # else:
    return render_template('forgot_password_page.html')


@app.route("/confirm_reset_email/<token>", methods=['GET', 'POST'])
def reset(token):
    if request.method == 'GET':
        try:
            s = URLSafeTimedSerializer(URLSafeTimedSerializer_salt)
            merchant_id = s.loads(token, max_age=28800,
                                  salt='nextify')  # seconds
            return render_template('forgot_password_page_2.html',
                                   merchant_id=merchant_id,
                                   token=token,
                                   title='Forgot password')
        except:
            return render_template('forgot_password_page_3.html',
                                   title='Quên mật khẩu',
                                   merchant_email=None,
                                   text='Link đã hết hạn.')
    else:
        merchant_id = request.form.get('merchant_id')
        password = request.form.get('password')
        password = str(password).strip()
        confirm_password = request.form.get('confirm_password')
        confirm_password = str(confirm_password).strip()
        if not captcha.validate():
            error = "Mã captcha chưa đúng, vui lòng thử lại."
            return render_template('forgot_password_page_2.html',
                                   merchant_id=merchant_id,
                                   title='Forgot password',
                                   token=token,
                                   error=error)
        if not password:
            return render_template('forgot_password_page_2.html',
                                   merchant_id=merchant_id,
                                   title='Forgot password',
                                   token=token,
                                   error=str(
                                       gettext("Hay_dien_day_du_thong_tin!")))
        elif bool(
                re.match('(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,50}',
                         password)) is False:
            return render_template(
                'forgot_password_page_2.html',
                merchant_id=merchant_id,
                title='forgot password',
                token=token,
                error=str(
                    gettext(
                        "Phai_du_8_ky_tu,_chua_it_nhat_mot_chu_cai_viet_thuong,_mot_chu_cai_viet_hoa,_mot_chu_so_va_mot_ky_tu_dac_biet."
                    )))
        if not confirm_password:
            return render_template('forgot_password_page_2.html',
                                   merchant_id=merchant_id,
                                   title='Forgot password',
                                   token=token,
                                   error=str(
                                       gettext("Hay_dien_day_du_thong_tin!")))
        elif confirm_password != password:
            return render_template(
                'forgot_password_page_2.html',
                merchant_id=merchant_id,
                title='Forgot password',
                token=token,
                error=str(gettext("Xac_nhan_mat_khau_khong_khop!")))
        api.update_password_merchant(merchant_id, password)
        return render_template('forgot_password_page_4.html',
                               title='Password changed')


@app.route("/hardware")
def hardware_integration():
    page = int(request.args.get('page', 1))
    router_firmware = api.list_router_firmware(
        page=page, page_size=settings.ITEMS_PER_PAGE)
    total = api.total_router_firmware()
    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template('nextify/hardware.html',
                           router_firmware=router_firmware,
                           pagination=pagination,
                           total=total)


@app.route("/vcall_pop_up/<user_id>")
@login_required
def vcall_pop_up(user_id):
    shop = g.shop
    shop_id = g.shop_id
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    user = api.get_user_info(user_id=user_id)
    name = user.get('name')
    phone = user.get('phone')
    avatar = user.get('avatar', '')

    if not avatar or len(avatar) == 0 or str(avatar) == 'None':
        if name and len(name) > 0:
            user['avatar'] = avinit.get_avatar_data_url(name)
    return render_template('nextify/pop_up_call.html',
                           name=name,
                           cus=user,
                           phone=phone,
                           merchant_id=merchant_id,
                           merchant=merchant)


@app.route("/get_user_info/<user_phone>")
@login_required
def get_user_info_vcall(user_phone):
    user_phone = str(user_phone)
    shop = g.shop
    shop_id = g.shop_id
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    customers_in_mer = handle_customers.get_user_merchant_by_phone(
        merchant_id, user_phone)
    if not customers_in_mer:
        return render_template('nextify/user_data_call_in.html',
                               name="",
                               cus="",
                               phone="phone",
                               merchant_id=merchant_id)
    user = customers_in_mer.get("user")
    name = user.get('name')
    phone = user.get('phone')
    avatar = user.get('avatar', '')
    if not avatar or len(avatar) == 0 or str(avatar) == 'None':
        if name and len(name) > 0:
            user['avatar'] = avinit.get_avatar_data_url(name)
    return render_template('nextify/user_data_call_in.html',
                           name=name,
                           cus=user,
                           phone=phone,
                           merchant_id=merchant_id)


@app.route("/get_data_campaign")
@login_required
def get_data_campaign():
    shop = g.shop
    shop_id = g.shop_id
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    campaign_id = request.args.get('campaign_id')
    date_preset = request.args.get("date_preset")
    campaign_info = api.get_post_fb_by_id(campaign_id)
    campaign_info_detail = campaign_info.get("detail")
    campaign_info_number = {
        "post_engagement": campaign_info_detail.get("post_engagement"),
        "impressions": campaign_info_detail.get("impressions"),
        "clicks": campaign_info_detail.get("clicks"),
        "frequency": campaign_info_detail.get("frequency"),
        "ctr": campaign_info_detail.get("ctr")
    }
    return render_template(
        'nextify/data_campaign.html',
        merchant=merchant,
        campaign_info=campaign_info,
        campaign_info_detail=json.dumps(campaign_info_number),
        campaign_info_number=campaign_info_number,
    )


@app.route("/hardware/<router_id>")
def hardware_integration_item(router_id):
    router_item = api.router_firmware_guide_item(router_id)
    if not router_item:
        abort(404)
    return render_template('nextify/hardware_item_guide.html',
                           router_item=router_item)


@app.route("/advertising_logout", methods=['GET'])
def advertising_logout():
    merchant_id = request.args.get("merchant_id")
    fb_api.logout_info_setting_fb(merchant_id)
    return json.dumps({"url": "/advertising"})


@app.route("/fb_callback", methods=['POST'])
def fb_callback():
    data = dict(request.form)
    merchant_id = str(data.get("merchant_id")[0])
    data_resp = data['data'][0]
    data_resp = json.loads(data_resp)
    data_setting = {}
    access_token = ""
    if data_resp:
        authResponse = data_resp.get('authResponse')
        if authResponse:
            access_token = authResponse.get("accessToken")
            user_id_fb = str(authResponse.get("userID"))
            fb_api.facebook_login(merchant_id, user_id_fb, access_token)
    return json.dumps({"result": "true", "url": "/advertising"})


@app.route("/fb_setting", methods=['POST'])
@login_required
def fb_setting():
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    data = dict(request.form)
    merchant_id = str(request.form.get("merchant_id"))
    data_resp = data['data'][0]
    data_resp = json.loads(data_resp)
    if data_resp:
        authResponse = data_resp.get('authResponse')
        if authResponse:
            access_token = authResponse.get("accessToken")
            user_id_fb = str(authResponse.get("userID"))
            access_token_long = fb_api.fb_long_lived_user_access_token(
                settings.NEXTIFY_FACEBOOK_APP_ID,
                settings.NEXTIFY_FACEBOOK_APP_SECRET, access_token)
            api.save_page_facebook(merchant_id, user_id_fb, access_token_long)
    return json.dumps({"result": "true"})


@app.route('/test_ajax_create_tag', methods=['POST'])
@login_required
def test_ajax_create_tag():
    shop_id = g.shop_id
    user_login = g.user
    shop = g.shop
    merchant_id = shop.get('merchant_id')

    name = request.form.get('name_add_new_tag')
    desc = request.form.get('desc')
    try:
        if api.check_tag_name(name, merchant_id):
            error = gettext("Ten_tag_nay_da_ton_tai!")
            return json.dumps({'error': error})
        api.create_tags(merchant_id, name, desc)
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        result = []
        for tag in tags:
            result.append({'id': str(tag['_id']), 'text': tag.get('name')})
        return json.dumps(result)
    except:
        return json.dumps(
            {'error': gettext("Da_co_loi_xay_ra_xin_thu_lai_sau")})


@app.route('/save_image_new_portal/<shop_id>', methods=['POST'])
@login_required
def save_image_new_portal(shop_id):
    shop_select = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop_select.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    photo1 = request.files.get('photo1')
    photo2 = request.files.get('photo2')
    photo3 = request.files.get('photo3')
    photo4 = request.files.get('photo4')
    photo5 = request.files.get('photo5')
    photo6 = request.files.get('photo6')
    list_photo = [photo1, photo2, photo3, photo4, photo5, photo6]
    for photo in list_photo:
        if photo:
            image = storage_api.save_new_file(photo)
    return redirect('/new_portal/{}'.format(shop_id))


@app.route('/new_portal/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def new_portal(shop_id_select):
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    dealer_id = merchant.get('partner')
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    tags = [
        tag for tag in api.list_tags(merchant_id)
        if tag.get('name') and len(str(tag['name'])) > 0
    ]
    tag_list = api.get_splash_page_tag(shop_id=shop_id_select)
    cards = api.get_card_new_portal(shop_id=shop_id_select)

    list_photo = []
    for card in cards:
        if card:
            list_photo.append({
                "id":
                random.randrange(0, 999999),
                "postedById":
                10005,
                "postedByDisplayName":
                "Nextify WiFi",
                "postedByProfileImage":
                "https://cdn1.swipewifi.com/Content/Uploads/Users/10005/5cdcc47a-42b6-4b01-b920-7335e727b7cf.png",
                "whenPosted":
                "2019-01-24T11:55:15",
                "titleColour":
                0,
                "postLink":
                "",
                "attachmentImageUrl":
                "",
                "type":
                "CallToActionCard",
                "buttonText":
                shop_select.get('connect_button'),
                "buttonColour":
                1,
                "buttonLinkType":
                1,
                "webUrl":
                "",
                "ctaBackgroundImagePath":
                "https://static.nextify.vn/images/{}/thumb/original".format(
                    card.get('photo'))
            })

    data = json.dumps({
        "campaign": {
            "publicPath":
            "https://cdn1.swipewifi.com/ClientApp/build/",
            "platformProviderTagline":
            "Powered by Nextify WiFi™",
            "platformWiFiName":
            "Nextify WiFi",
            "clientRedirectUrl":
            "",
            "enableWelcomeText":
            True,
            "alternateDisplayText":
            shop_select.get('welcome_member_text_splash'),
            "defaultCardBackgroundImage":
            "http://static.nextify.vn/static/uploads/{}".format(
                shop_select.get('background')),
            "enableSplashLogo":
            True,
            "defaultCardLogo":
            "https://static.nextify.vn/images/{}/thumb/320".format(
                shop_select.get('logo')),
            "textColour":
            "Light",
            "themeDisplayName":
            "Nextify WiFi",
            "targetUserId":
            10005,
            "id":
            70071,
            "vendor":
            0,
            "isPreview":
            True,
            "isAndroid":
            False,
            "isSamsung":
            False,
            "isChromeWebView":
            False
        },
        "analytics": {
            "enable": True,
            "debug": False,
            "version": 2,
            "endpoint": "https://e1.swipewifi.com/captive/"
        },
        "cards": list_photo,
        "device": {
            "isAndroid": False,
            "isSamsung": False,
            "isChromeWebView": False
        },
        "language": {},
        "resources": {
            "androidInstructions":
            "Follow the three instructions below to complete your journey to Wi-Fi.",
            "androidEndInstructions":
            "For more great content follow the three instructions below.",
            "androidBlogInstructions":
            "Follow the three instructions below to continue reading.",
            "androidInstructionsHeading": "Instructions",
            "androidListUse": "Use the",
            "androidListCopy": "Copy Link button",
            "androidListBelow": "below",
            "androidListOpen": "Open your",
            "androidListDevice": "device browser manually",
            "androidListPaste": "Paste",
            "androidListCopied": "copied link into the",
            "androidListAddress": "address bar",
            "androidButtonCopy": "Copy Link",
            "androidButtonCopied": "Link Copied",
            "androidButtonWifi": "Wi-Fi Only",
            "androidEndTitle": "You're almost there...",
            "samsungInstructions":
            "Get the best Wi-Fi experience by following the three instructions below.",
            "samsungOpen": "Open the",
            "samsungMenu": "menu",
            "samsungAt": "at the",
            "samsungTop": "top",
            "samsungScreen": "of your screen",
            "samsungSelect": "Select",
            "samsungOpenBrowser": "Open in browser",
            "samsungFromMenu": "from the menu",
            "samsungSwipe": shop_select.get('connect_button'),
            "samsungWiFi": "& enjoy free Wi-Fi",
            "samsungWelcome": "Welcome to",
            "samsungWiFiOnly": "Wi-Fi",
            "bySwiping": shop_select.get('connect_button'),
            "termsConditions": "",
            "terms": "Terms",
            "privacy": "Privacy"
        }
    })

    return render_template("nextify/new_portal.html",
                           merchant_id=merchant_id,
                           merchant=merchant,
                           tags=tags,
                           data=data,
                           tag_list=tag_list,
                           shop_select=shop_select,
                           cards=cards,
                           shop_id_select=shop_id_select)


@app.route('/save_setting_rating', methods=['POST'])
@login_required
def save_setting_rating():
    shop = g.shop
    merchant_id = shop.get('merchant_id')

    shop_id = request.form.get('shop_id_rating')
    url_facebook = request.form.get('url_facebook')
    url_google = request.form.get('url_google')
    url_tripadvisor = request.form.get('url_tripadvisor')
    content_rating = request.form.get('content_rating')
    check_facebook = request.form.get('check_facebook')
    check_google = request.form.get('check_google')
    check_tripadvisor = request.form.get('check_tripadvisor')
    api.save_setting_rating(merchant_id,
                            shop_id,
                            url_facebook=url_facebook,
                            url_google=url_google,
                            url_tripadvisor=url_tripadvisor,
                            content_rating=content_rating,
                            check_facebook=check_facebook,
                            check_google=check_google,
                            check_tripadvisor=check_tripadvisor)

    return json.dumps({"result": True})


@app.route('/info_shop_rating', methods=['POST'])
@login_required
def info_shop_rating():
    shop_id = request.form.get('shop_id')
    url_facebook = ""
    url_google = ""
    url_tripadvisor = ""
    content_rating = ""
    check_facebook = "false"
    check_google = "false"
    check_tripadvisor = "false"
    if shop_id != "all":
        shop_info = api.get_shop_info(shop_id=shop_id)
        if shop_info:
            setting_rating = shop_info.get('setting_rating')
            if setting_rating:
                url_facebook = setting_rating.get('url_facebook')
                if not url_facebook:
                    url_facebook = ""
                url_google = setting_rating.get('url_google')
                if not url_google:
                    url_google = ""
                url_tripadvisor = setting_rating.get('url_tripadvisor')
                if not url_tripadvisor:
                    url_tripadvisor = ""
                content_rating = setting_rating.get('content_rating')
                if not content_rating:
                    content_rating = ""
                check_facebook = setting_rating.get('check_facebook')
                if not check_facebook:
                    check_facebook = "false"
                check_google = setting_rating.get('check_google')
                if not check_google:
                    check_google = "false"
                check_tripadvisor = setting_rating.get('check_tripadvisor')
                if not check_tripadvisor:
                    check_tripadvisor = "false"
                return render_template("nextify/modal_setting_reviews.html",
                                       url_facebook=url_facebook,
                                       url_google=url_google,
                                       url_tripadvisor=url_tripadvisor,
                                       content_rating=content_rating,
                                       check_facebook=check_facebook,
                                       check_google=check_google,
                                       check_tripadvisor=check_tripadvisor)
    return render_template("nextify/modal_setting_reviews.html",
                           url_facebook=url_facebook,
                           url_google=url_google,
                           url_tripadvisor=url_tripadvisor,
                           content_rating=content_rating,
                           check_facebook=check_facebook,
                           check_google=check_google,
                           check_tripadvisor=check_tripadvisor)


@app.route('/get_code_html_reviews', methods=['POST'])
@login_required
def get_code_html_reviews():
    shop_id = request.form.get('shop_id')
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop_select = api.get_shop_info(shop_id=shop_id)
    setting_rating = shop_select.get('setting_rating')
    url_facebook = ""
    content_rating = ""
    url_google = ""
    check_facebook = "false"
    check_google = "false"
    check_tripadvisor = "false"
    url_tripadvisor = ""
    if setting_rating:
        url_facebook = setting_rating.get('url_facebook')
        if not url_facebook:
            url_facebook = ""
        url_google = setting_rating.get('url_google')
        if not url_google:
            url_google = ""
        url_tripadvisor = setting_rating.get('url_tripadvisor')
        if not url_tripadvisor:
            url_tripadvisor = ""
        content_rating = setting_rating.get('content_rating')
        if not content_rating:
            content_rating = ""
        check_facebook = setting_rating.get('check_facebook')
        if not check_facebook:
            check_facebook = "false"
        check_google = setting_rating.get('check_google')
        if not check_google:
            check_google = "false"
        check_tripadvisor = setting_rating.get('check_tripadvisor')
        if not check_tripadvisor:
            check_tripadvisor = "false"
    return render_template(
        "nextify/reviews_code_html.html",
        content_rating=content_rating,
        url_facebook=url_facebook,
        url_google=url_google,
        check_facebook=check_facebook,
        url_tripadvisor=url_tripadvisor,
        check_google=check_google,
        check_tripadvisor=check_tripadvisor,
    )


@app.route('/data_create_campaign', methods=['GET'])
@login_required
def data_create_campaign():
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_id = shop.get('_id')

    if request.method == 'GET':
        page = int(request.args.get('current_page', 1))
        shop_id_select = request.args.get('shop_id_select')
        active_zns = request.args.get('active_zns')
        loc_id = request.args.get('loc_id', shop_id_select)
        # thoi gian den
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        # luot den
        min_visit = request.args.get('min_visit')
        max_visit = request.args.get('max_visit')
        sort = request.args.get('sort', 'time_asc')
        # ngay sinh
        bday_from_date = request.args.get('bday_from_date')
        bday_to_date = request.args.get('bday_to_date')
        # gioi tinh
        gender_filter = request.args.get('gender_filter')
        gender_array = []
        if isinstance(gender_filter, list):
            gender_array = gender_filter
        elif gender_filter and len(gender_filter) > 0 and str(
                gender_filter) != 'None':
            gender_array = gender_filter.split(',')
            gender_array = [str(tag) for tag in gender_array]

        lost_day = request.args.get('lost_day', 0)

        is_email = request.args.get('is_email', False)
        if is_email:
            is_email = True
        is_sms = request.args.get('is_sms', False)
        if is_sms:
            is_sms = True
        is_zalo = request.args.get('is_zalo', False)
        if is_zalo:
            is_zalo = True
        filter_tags = request.args.get('real_tags_filter', '')
        tags_array = []
        if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
            tags_array = filter_tags.split(',')
            tags_array = [str(tag) for tag in tags_array]
        list_cus = []
        total = 0
        customers_sources = request.args.get('customers_sources')
        if customers_sources == "on":
            from_date = ""
            to_date = ""
            min_visit = ""
            max_visit = ""
            lost_day = ""
            bday_from_date = ""
            bday_to_date = ""
            gender = ""
            filter_tags = ""
            list_cus, real_send = api.filter_campaign(merchant_id,
                                                      shop_id=shop_id_select,
                                                      page=page,
                                                      is_email=is_email,
                                                      is_sms=is_sms,
                                                      is_zalo=is_zalo,
                                                      active_zns=active_zns,
                                                      page_size=7)
            if not shop_id_select or str(shop_id_select) == 'all':
                total = api.total_merchant_customers(merchant_id)
            else:
                total = api.total_shop_customers(shop_id_select)

        else:

            list_cus, real_send = api.filter_campaign(
                merchant_id,
                shop_id=shop_id_select,
                from_date=from_date,
                is_email=is_email,
                is_sms=is_sms,
                is_zalo=is_zalo,
                to_date=to_date,
                min_visit=min_visit,
                max_visit=max_visit,
                lost_day=lost_day,
                gender=gender_array,
                sort=sort,
                bday_from_date=bday_from_date,
                bday_to_date=bday_to_date,
                tags_array=tags_array,
                page=page,
                active_zns=active_zns,
                page_size=7)
            if not shop_id_select or str(shop_id_select) == 'all':
                total = api.total_merchant_customers(
                    merchant_id,
                    is_email=is_email,
                    is_sms=is_sms,
                    is_zalo=is_zalo,
                    from_date=from_date,
                    to_date=to_date,
                    min_visit=min_visit,
                    max_visit=max_visit,
                    lost_day=lost_day,
                    gender=gender_array,
                    sort=sort,
                    bday_from_date=bday_from_date,
                    bday_to_date=bday_to_date,
                    active_zns=active_zns,
                    tags_array=tags_array)

            else:
                total = api.total_shop_customers(shop_id_select,
                                                 is_email=is_email,
                                                 is_sms=is_sms,
                                                 is_zalo=is_zalo,
                                                 from_date=from_date,
                                                 to_date=to_date,
                                                 min_visit=min_visit,
                                                 max_visit=max_visit,
                                                 lost_day=lost_day,
                                                 gender=gender_array,
                                                 sort=sort,
                                                 bday_from_date=bday_from_date,
                                                 bday_to_date=bday_to_date,
                                                 active_zns=active_zns,
                                                 tags_array=tags_array)

        total_pages = (real_send // 7) + \
            1 if real_send % 7 != 0 else real_send / 7

        return jsonify({
            "data":
            render_template("nextify/data_cus_campaign.html",
                            shop_id_select=shop_id_select,
                            is_email=is_email,
                            is_sms=is_sms,
                            is_zalo=is_zalo,
                            customers=list_cus,
                            loc_id=loc_id,
                            current_page=page,
                            from_date=from_date,
                            to_date=to_date,
                            min_visit=min_visit,
                            max_visit=max_visit,
                            lost_day=lost_day,
                            bday_from_date=bday_from_date,
                            bday_to_date=bday_to_date,
                            gender=gender_array,
                            sort=sort,
                            shop=shop,
                            shops=shops,
                            total=total,
                            total_pages=total_pages,
                            user_login=user_login,
                            real_send=real_send,
                            sub=total - real_send,
                            merchant=merchant,
                            filter_tags=tags_array,
                            shop_in_mer=shops),
            "shop_id_select":
            shop_id_select,
            "real_send":
            real_send,
            "total":
            total,
            "current_page":
            page,
            "total_pages":
            total_pages
        })


@app.route('/data_cus_pagination', methods=['GET'])
@login_required
def data_cus_pagination():
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_id = shop.get('_id')
    active_zns = request.args.get('active_zns')
    page = int(request.args.get('current_page', 1))
    shop_id_select = request.args.get('shop_id_select')
    loc_id = request.args.get('loc_id', shop_id_select)
    # thoi gian den
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    # luot den
    min_visit = request.args.get('min_visit')
    max_visit = request.args.get('max_visit')
    sort = request.args.get('sort', 'time_asc')
    # ngay sinh
    bday_from_date = request.args.get('bday_from_date')
    bday_to_date = request.args.get('bday_to_date')
    # gioi tinh
    gender_filter = request.args.get('gender_filter')
    gender_array = []
    if isinstance(gender_filter, list):
        gender_array = gender_filter
    elif gender_filter and len(gender_filter) > 0 and str(
            gender_filter) != 'None':
        gender_array = gender_filter.split(',')
        gender_array = [str(tag) for tag in gender_array]

    lost_day = request.args.get('lost_day', 0)

    is_email = request.args.get('is_email', False)
    if is_email:
        is_email = True
    is_sms = request.args.get('is_sms', False)
    if is_sms:
        is_sms = True
    is_zalo = request.args.get('is_zalo', False)
    if is_zalo:
        is_zalo = True

    filter_tags = request.args.get('real_tags_filter', '')
    tags_array = []
    if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
        tags_array = filter_tags.split(',')
        tags_array = [str(tag) for tag in tags_array]
    list_cus = []
    total = 0
    customers_sources = request.args.get('customers_sources')
    if customers_sources == "on":
        list_cus, real_send = api.filter_campaign(merchant_id,
                                                  shop_id=shop_id_select,
                                                  page=page,
                                                  is_email=is_email,
                                                  is_sms=is_sms,
                                                  is_zalo=is_zalo,
                                                  active_zns=active_zns,
                                                  page_size=7)
        if not shop_id_select or str(shop_id_select) == 'all':
            total = api.total_merchant_customers(merchant_id)
        else:
            total = api.total_shop_customers(shop_id_select)
        from_date = ""
        to_date = ""
        min_visit = ""
        max_visit = ""
        lost_day = ""
        bday_from_date = ""
        bday_to_date = ""
        gender = ""
        filter_tags = ""
    else:
        list_cus, real_send = api.filter_campaign(
            merchant_id,
            shop_id=shop_id_select,
            from_date=from_date,
            is_email=is_email,
            is_sms=is_sms,
            is_zalo=is_zalo,
            active_zns=active_zns,
            to_date=to_date,
            min_visit=min_visit,
            max_visit=max_visit,
            lost_day=lost_day,
            gender=gender_array,
            sort=sort,
            bday_from_date=bday_from_date,
            bday_to_date=bday_to_date,
            tags_array=tags_array,
            page=page,
            page_size=7)
        if not shop_id_select or str(shop_id_select) == 'all':
            total = api.total_merchant_customers(merchant_id,
                                                 is_email=is_email,
                                                 is_sms=is_sms,
                                                 is_zalo=is_zalo,
                                                 active_zns=active_zns,
                                                 from_date=from_date,
                                                 to_date=to_date,
                                                 min_visit=min_visit,
                                                 max_visit=max_visit,
                                                 lost_day=lost_day,
                                                 gender=gender_array,
                                                 sort=sort,
                                                 bday_from_date=bday_from_date,
                                                 bday_to_date=bday_to_date,
                                                 tags_array=tags_array)
        else:
            total = api.total_shop_customers(shop_id_select,
                                             is_email=is_email,
                                             is_sms=is_sms,
                                             is_zalo=is_zalo,
                                             active_zns=active_zns,
                                             from_date=from_date,
                                             to_date=to_date,
                                             min_visit=min_visit,
                                             max_visit=max_visit,
                                             lost_day=lost_day,
                                             gender=gender_array,
                                             sort=sort,
                                             bday_from_date=bday_from_date,
                                             bday_to_date=bday_to_date,
                                             tags_array=tags_array)
    total_pages = (real_send / 7) + 1 if real_send % 7 != 0 else real_send / 7

    return render_template("nextify/data_customers_pagination.html",
                           is_email=is_email,
                           is_sms=is_sms,
                           customers=list_cus,
                           loc_id=loc_id,
                           current_page=page,
                           from_date=from_date,
                           to_date=to_date,
                           min_visit=min_visit,
                           max_visit=max_visit,
                           lost_day=lost_day,
                           bday_from_date=bday_from_date,
                           bday_to_date=bday_to_date,
                           gender=gender_array,
                           sort=sort,
                           shop=shop,
                           shops=shops,
                           user_login=user_login,
                           real_send=real_send,
                           sub=total - real_send,
                           total=total,
                           total_pages=total_pages,
                           merchant=merchant,
                           filter_tags=tags_array,
                           shop_in_mer=shops,
                           is_zalo=is_zalo,
                           active_zns=active_zns)


@app.route('/data_email_pagination', methods=['GET'])
def data_email_pagination():
    page = int(request.args.get('page', 1))
    select_branch = request.args.get("select_branch", 'all')
    list_email_templates = api.email_example_by_type(
        select_branch=select_branch, page=page)
    total = api.count_email_example(select_branch=select_branch)
    if total == 1:
        total_pages = 1
    else:
        total_pages = (total // 8) + 1 if total % 8 != 0 else total / 8

    return render_template("nextify/email_example.html",
                           list_email_templates=list_email_templates,
                           total_pages=total_pages)


@app.route('/result_spin_splash', methods=['GET'])
@login_required
def result_spin_splash():
    shop = g.shop
    merchant = g.merchant

    merchant_id = shop.get('merchant_id')
    page = int(request.args.get('page', 1))
    list_result, total = api.get_result_spin_splash(
        merchant_id=merchant_id, page_size=settings.ITEMS_PER_PAGE, page=page)

    pagination = Pagination(page=page,
                            total=total,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template(
        "nextify/result_spin_splash.html",
        total=total,
        merchant=merchant,
        list_result=list_result,
        pagination=pagination,
    )


@app.route('/survey_remove/<survey_id>', methods=['GET'])
@login_required
def survey_remove(survey_id):
    api.remove_survey_result(survey_id)
    return json.dumps({'result': True})


@app.route('/welcome', methods=['GET'])
def setup_first_login():
    merchant_id = session.get('merchant_id')
    if not merchant_id:
        return redirect('/logout')
    merchant = api.get_merchant(merchant_id)
    return render_template('nextify/setup_first_login.html',
                           merchant=merchant,
                           merchant_id=merchant_id)


@app.route('/welcome/init', methods=['GET', 'POST'])
def setup_second_login():
    merchant_id = session.get('merchant_id')
    if not merchant_id:
        return redirect('/logout')
    merchant = api.get_merchant(merchant_id)
    contract_locations = merchant.get('contract_locations')
    if request.method == 'GET':
        shops = api.total_shop_in_merchant(str(merchant_id))
        if contract_locations and int(contract_locations) > shops:
            access_token = request.args.get('access_token')
            fb_pages = []
            user_id_fb = None
            if access_token:
                url_get_user_id_fb = "https://graph.facebook.com/v6.0/me?fields=id&access_token={}".format(
                    access_token)
                result = requests.get(url=url_get_user_id_fb)
                user_fb = json.loads(result.text)
                user_id_fb = user_fb.get('id')

            if user_id_fb:
                get_list_fb_page_url = 'https://graph.facebook.com/v6.0/%s/accounts?access_token=%s' % (
                    user_id_fb, access_token)
                result = requests.get(url=get_list_fb_page_url)
                result_fb = json.loads(result.text)
                fb_pages = result_fb.get('data')
            business_model_list = api.business_model_list()
            ls_business_model = []
            for bus_model in business_model_list:
                ls_business_model.append(bus_model)
            return render_template('nextify/setup_second_login.html',
                                   merchant=merchant,
                                   merchant_id=merchant_id,
                                   access_token=access_token,
                                   fb_pages=fb_pages,
                                   ls_business_model=ls_business_model)
        else:
            return redirect('/')
    else:
        contract_locations = merchant.get('contract_locations')
        shops = api.total_shop_in_merchant(str(merchant_id))
        if contract_locations and int(contract_locations) > shops:
            name = request.form.get('name').strip()
            if not name or len(name) == 0:
                error = gettext("Ban_can_nhap_ten_dia_diem.")
                return json.dumps({'result': False, 'msg': error})

            email = request.form.get('email')
            website = request.form.get('website')
            address = request.form.get('address')
            city = request.form.get('city')
            page_id = request.form.get('page_id')
            page_access_token = request.form.get('page_access_token')
            facebook_page = request.form.get('facebook_page')
            if page_id and page_id != "all":
                check_double = api.check_facebook_has_page(page_id)
                if check_double:
                    error = gettext(
                        "Facebook_Page_nay_da_duoc_dong_bo_voi_dia_diem_khac._Ban_hay_chon_mot_Page_khac."
                    )
                    return json.dumps({'result': False, 'msg': error})
            shop_id = api.create_shop(name,
                                      address=address,
                                      merchant_id=merchant_id,
                                      facebook_page=facebook_page,
                                      city=city)
            act_type = 'insert_location'
            activity_history.save_activity(act_type,
                                           merchant_id,
                                           shop_id,
                                           location_name=name)

            if shop_id:
                logo = None
                background = None
                url_logo = None
                url_background = None
                if page_id and page_access_token:
                    try:
                        url_logo = settings.FACBOOK_GRAPH_API + '/%s/?fields=picture&type=large&redirect=false&access_token=%s' % (
                            str(page_id), str(page_access_token))
                        url_logo = real_url_fb(url_logo)

                        fb_background = settings.FACBOOK_GRAPH_API + '/%s/?fields=cover&access_token=%s' % (
                            str(page_id), str(page_access_token))
                        req_background = requests.get(fb_background)
                        req_background_json = req_background.json()
                        data_background = req_background_json.get('cover')
                        url_background = data_background.get('source')
                        logo = save_image_from_url(shop_id, url_logo, 'logo')
                        background = save_image_from_url(
                            shop_id, url_background, 'background')
                    except:
                        url_logo = str(os.getcwd()) + \
                            '/static/images/onboard/profile_default.jpg'
                        url_background = str(os.getcwd(
                        )) + '/static/images/onboard/cover_default.jpg'
                        logo = save_image_from_local(shop_id, url_logo, 'logo')
                        background = save_image_from_local(
                            shop_id, url_background, 'background')
                else:
                    url_logo = str(os.getcwd()) + \
                        '/static/images/onboard/profile_default.jpg'
                    url_background = str(os.getcwd(
                    )) + '/static/images/onboard/cover_default.jpg'
                    logo = save_image_from_local(shop_id, url_logo, 'logo')
                    background = save_image_from_local(shop_id, url_background,
                                                       'background')

                business_model = request.form.get('business_model')
                api.update_shop(shop_id,
                                email=email,
                                website=website,
                                id_page=page_id,
                                access_token_page=page_access_token,
                                logo=logo,
                                background=background,
                                business_model=business_model)

                api.facebook_lead_ad(page_id=page_id,
                                     access_token_page=page_access_token)
                phone_merchant = merchant.get('phone')
                pass_merchant = merchant.get('password')
                email_merchant = merchant.get('email')
                api.insert_new_account(shop_id, phone_merchant, pass_merchant,
                                       "3", email_merchant, True)
                g.shop_id = shop_id
                session['shop_id'] = str(shop_id)
                form_settings = {
                    'phone_require': True,
                    'gender': False,
                    'phone': True,
                    'birthday': False,
                    'email': True,
                    'name': True
                }
                api.update_login_form_settings(shop_id, form_settings)
                shop = api.get_shop_info(shop_id=shop_id)
                info = {}
                info['id'] = str(shop.get('_id'))
                name = shop.get('name', '')
                if str(name.encode('utf-8')) == 'None':
                    name = ''
                info['name'] = api.remove_accents(name.encode('utf-8'))
                phone = shop.get('phone', '')
                if not phone or str(phone.encode('utf-8')) == 'None':
                    phone = ''
                info['phone'] = phone
                email = shop.get('email', '')
                if type(email) is OrderedDict or not email or str(
                        email.encode('utf-8')) == 'None':
                    email = ''
                info['email'] = email
                address = shop.get('address', '')
                if not address or str(address.encode('utf-8')) == 'None':
                    address = ''
                info['address'] = api.remove_accents(address.encode('utf-8'))
                info['gateway_mac'] = shop.get('gateway_mac', [])
                try:
                    check_res = search_engine.get_elastic('shop', info['id'])
                    if check_res and len(check_res) > 0:
                        search_engine.remove_elastic('shop', info['id'])
                        search_engine.index_elastic('shop', info['id'], info)
                    else:
                        search_engine.index_elastic('shop', info['id'], info)
                except:
                    pass
                shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
                shop_ids = [shop['_id'] for shop in shop_in_mer]
                g.shops = [api.get_shop_info(i) for i in shop_ids]
                g.merchant = merchant
                session['is_superuser'] = phone
                session['merchant_id'] = str(merchant_id)
                g.shop = g.shops[0]
                g.shop_id = g.shops[0]['_id']

                url = '/welcome/init_device/%s' % (shop_id)
                return json.dumps({'result': True, 'url': url})
            else:
                return json.dumps({'result': False})
        else:
            error = gettext(
                "Ban_da_het_so_luong_diem_duoc_tao,_vui_long_lien_he_de_nang_so_luong_dia_diem."
            )
            return json.dumps({'result': False, 'msg': error})


@app.route('/welcome/init_device/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def init_device(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)
    if request.method == 'GET':
        macs = shop.get('gateway_mac', [])
        if len(macs) > 0:
            return redirect(
                url_for('init_default_campaign',
                        shop_id_select=shop_id_select))
        return render_template('nextify/setup_third_login.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_id_select=shop_id_select)
    else:
        mac_add = request.form.get('mac_add')
        device_type = request.form.get('device_type')
        is_radius_req = request.form.get('is_radius')
        is_radius = True if is_radius_req else False
        shop_by_mac = api.get_shop_info(gateway_mac=mac_add)

        if shop_by_mac:
            error = gettext(
                "Thiet_bi_da_duoc_them_vao_tai_khoan_khac,_vui_long_go_thiet_bi_hoac_lien_he_support."
            )
            return json.dumps({'result': False, 'msg': error})

        api.update_shop(shop_id_select, gateway_mac=mac_add)
        device_id = api.insert_device(mac_add.upper(), is_radius)
        nas_id = ''
        if device_type == 'mikrotik':
            nas_id = api.gen_device_nas_id_mikrotik(mac_add)
        api.update_device_type(device_id, device_type, nas_id, is_radius)
        url = '/welcome/init_default_campaign/%s' % (shop_id_select)
        return json.dumps({'result': True, 'url': url})


@app.route('/welcome/init_default_campaign/<shop_id_select>', methods=['GET'])
@login_required
def init_default_campaign(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)
    login_form = shop_select.get('login_form', {})
    surveys_count = api.total_survey_splash(shop_id_select)
    if surveys_count == 0:
        rating.init_survey(merchant, shop_id_select,
                           get_top_domain(request.host))
    surveys = api.get_surveys_page(shop_id_select)
    return render_template('nextify/setup_four_login.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           login_form=login_form,
                           surveys=surveys,
                           shop_select=shop_select)


@app.route('/welcome/init_splash/<shop_id_select>', methods=['GET'])
@login_required
def init_splash(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)
    login_form = shop_select.get('login_form', {})
    return render_template('nextify/setup_four_login_2.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           login_form=login_form,
                           shop_select=shop_select)


@app.route('/welcome/init_slides/<shop_id_select>', methods=['GET'])
@login_required
def init_slides(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)
    default_page = api.get_splash_page_by_type(shop_id_select, 'default')
    if default_page.count() == 0:
        api.new_splash_page(shop_id_select, 'default', True, title='Mặc định')
    cards = api.get_cards(shop_id_select)
    if len(cards) == 0:
        photo = save_image_from_local(
            shop_id_select,
            str(os.getcwd()) + '/static/images/onboard/splash_default.jpg',
            'card')
        api.add_card(shop_id_select, '', '', photo, '', '', '', '')
    # hotspot_campaign_shop = api.get_all_hotspot_campaign(shop_id_select)
    camp_id_default = None
    total_hotspot = api.new_total_hotspot_campaign(shop_id_select)
    if total_hotspot == 0:
        api.init_new_campaign(shop_id_select)
    camp_default = api.get_default_camp(shop_id_select)
    if camp_default:
        camp_id_default = camp_default.get('_id')
    # if len(hotspot_campaign_shop) == 0:
    # api.init_hotspot_campaign(shop_id_select)
    pages = api.get_splash_page_by_type(shop_id_select, 'default')
    page = pages[0]
    page_id = page.get('_id')
    cards = api.get_cards(shop_id_select, mar_filter='default')
    return render_template('nextify/setup_five_login.html',
                           shop=shop,
                           user_login=user_login,
                           merchant=merchant,
                           merchant_id=merchant_id,
                           shop_id_select=shop_id_select,
                           shop_select=shop_select,
                           cards=cards,
                           pages=pages,
                           page_id=page_id,
                           camp_id_default=camp_id_default,
                           page=page)


@app.route('/welcome/init_automation/<shop_id_select>',
           methods=['GET', 'POST'])
@login_required
def init_automation(shop_id_select):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    merchant_id = shop.get('merchant_id')
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [str(shop['_id']) for shop in shop_in_mer]
    if shop_id_select not in shop_ids:
        abort(404)
    shop_select = api.get_shop_info(shop_id_select)
    if not shop_select:
        abort(404)
    if request.method == 'GET':
        image_register = session.get('image_register')
        collect_register = session.get('collect_register')
        connect_register = session.get('connect_register')
        image_return = session.get('image_return')
        survey_return = session.get('survey_return')
        connect_return = session.get('connect_return')
        campaign = request.args.get('campaign')
        if str(campaign) == "True":
            api.init_campaign_new_shop(shop_id_select, image_register,
                                       collect_register, connect_register,
                                       image_return, survey_return,
                                       connect_return)
        init_automation_template.gen_welcome_template(shop_id_select)
        init_automation_template.gen_return_template(shop_id_select)
        init_automation_template.gen_loyal_template(shop_id_select)
        init_automation_template.gen_lost_template(shop_id_select)
        init_automation_template.gen_birthday_template(shop_id_select)
        init_automation_template.gen_thank_you_template(shop_id_select)
        return render_template('nextify/setup_channel.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_id_select=shop_id_select,
                               shop_select=shop_select)
    if request.method == 'POST':
        # zalo
        zalo_oa_id = request.form.get("zalo_oa_id", '')
        zalo_app_id = request.form.get("zalo_app_id", '')
        zalo_app_secret_key = request.form.get("zalo_app_secret_key", '')
        zalo_access_token = request.form.get("zalo_access_token", '')
        api.update_shop(shop_id_select,
                        zalo_oa_id=zalo_oa_id,
                        zalo_app_id=zalo_app_id,
                        zalo_app_secret_key=zalo_app_secret_key,
                        zalo_access_token=zalo_access_token)
        # facebook
        facebook_page = request.form.get("facebook_page", '')
        id_page = request.form.get("id_page", '')
        access_token_page = request.form.get("access_token_page", '')
        facebook_pixel_id = request.form.get("facebook_pixel_id", '')
        facebook_pixel_code = request.form.get("facebook_pixel_code", '')
        api.update_shop(shop_id_select,
                        facebook_page=facebook_page,
                        id_page=id_page,
                        access_token_page=access_token_page,
                        facebook_pixel_id=facebook_pixel_id,
                        facebook_pixel_code=facebook_pixel_code)
        # email
        mail_name = ''
        mail_user = ''
        mail_pass = ''
        mail_server = ''
        mail_port = ''
        mail_ssl = ''

        mail_box = request.form.get('mail_box')

        if mail_box == "mail_gun":
            mail_name = request.form.get('mail_domain')
            mail_user = request.form.get('mail_domain')
            mail_pass = request.form.get('mail_api_key')
            mail_server = request.form.get('mail_api_url')
            mail_port = "25"
            mail_ssl = True
        #
        if mail_box == "gmail":
            mail_name = request.form.get('name_gmail')
            mail_user = mail_name
            mail_pass = request.form.get('pass_gmail')
            mail_server = "smtp.gmail.com"
            mail_port = "465"
            mail_ssl = True

        if mail_box == "mail_khac":
            mail_name = request.form.get('smtp_email')
            mail_user = request.form.get('smtp_user')
            mail_pass = request.form.get('smtp_pass')
            mail_server = request.form.get('smtp_server')
            mail_port = request.form.get('smtp_port')
            mail_ssl = request.form.get('checkbox_ssl')

        # SendGrid
        if mail_box == "sendgrid":
            mail_name = request.form.get('from_email')
            mail_user = request.form.get('from_email')
            mail_pass = request.form.get('api_key')
            mail_server = "sendgrid"

        mail_settings = {
            "mail_name": mail_name,
            "mail_user": mail_user,
            "mail_pass": mail_pass,
            "mail_server": mail_server,
            "mail_port": mail_port,
            "mail_ssl": mail_ssl
        }

        api.update_merchants(merchant_id=merchant_id,
                             mail_settings=mail_settings)
        # sms brandname
        sms_provider = request.form.get('sms_provider')
        user_sms = request.form.get('user_sms')
        pass_sms = request.form.get('pass_sms')
        brand_name = request.form.get('brand_name')
        api_key_vhat = request.form.get('api_key_vhat')
        secret_key_vhat = request.form.get('secret_key_vhat')
        quota = request.form.get('quota', '-1')
        sms_type = request.form.get('sms_type')
        brand_name_vina = {}
        if sms_provider and len(sms_provider) != 0:
            if sms_provider != "VINAPHONE":
                if not user_sms or len(user_sms) == 0:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext("Ban_chua_nhap_thong_tin_tai_khoan")
                    })

                if not pass_sms or len(pass_sms) == 0:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext("Ban_chua_nhap_thong_tin_tai_khoan")
                    })
                if not brand_name or len(brand_name) == 0:
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext("Ban_chua_nhap_thong_tin_tai_khoan")
                    })
                if sms_provider == "MOBIFONE":
                    check_info = api.check_info_brandname_mobi(
                        user_sms, pass_sms)
                    if not check_info:
                        return json.dumps({
                            'result':
                            False,
                            'error':
                            gettext(
                                "Khong_thanh_cong._Cau_hinh_SMS_Brandname_chua_chinh_xac."
                            )
                        })
            info = {}
            if sms_provider == "INCOM":
                sms_type_incom = request.form.get('sms_type_incom', '')
                username_incom = request.form.get('username_incom', '')
                password_incom = request.form.get('password_incom', '')
                command_code_incom = request.form.get('command_code_incom', '')
                prefix_id_incom = request.form.get('prefix_id_incom', '')
                api.update_merchants(merchant_id=merchant_id,
                                     sms_type_incom=sms_type_incom,
                                     username_incom=username_incom,
                                     password_incom=password_incom,
                                     command_code_incom=command_code_incom,
                                     prefix_id_incom=prefix_id_incom)
            elif sms_provider == "VINAPHONE":
                vina_label_id = request.form.get('vina_label_id')
                vina_template_id = request.form.get('vina_template_id')
                vina_contract_id = request.form.get('vina_contract_id')
                vina_agent_id = request.form.get('vina_agent_id')
                vina_api_user = request.form.get('vina_api_user')
                vina_api_pass = request.form.get('vina_api_pass')
                vina_api_url = request.form.get('vina_api_url')
                vina_user_name = request.form.get('vina_user_name')
                brand_name_vina['vina_label_id'] = vina_label_id
                brand_name_vina['vina_contract_id'] = vina_contract_id
                brand_name_vina['vina_agent_id'] = vina_agent_id
                brand_name_vina['vina_api_user'] = vina_api_user
                brand_name_vina['vina_api_url'] = vina_api_url
                brand_name_vina['vina_api_pass'] = vina_api_pass
                brand_name_vina['vina_user_name'] = vina_user_name
                api.update_merchants(merchant_id=merchant_id,
                                     sms_provider=sms_provider,
                                     brand_name_vina=brand_name_vina)

            else:
                api.update_merchants(merchant_id=merchant_id,
                                     sms_provider=sms_provider,
                                     user_sms=user_sms,
                                     pass_sms=pass_sms,
                                     api_key_vhat=api_key_vhat,
                                     secret_key_vhat=secret_key_vhat,
                                     brand_name=brand_name,
                                     quota=quota,
                                     sms_type=sms_type)
        return json.dumps({'result': True})


@app.route('/facebook/pages/<page_id>', methods=['GET'])
def get_facebook_page_info(page_id):
    access_token = request.args.get('access_token')
    page_url = settings.FACBOOK_GRAPH_API + '/%s?fields=' \
                                            'id,name,about,attire,bio,location,parking,hours,emails,website,link&access_token=%s' % (
                                                page_id, access_token)

    page_info = requests.get(url=page_url)
    result_fb = json.loads(page_info.text)
    return json.dumps({'data': result_fb})


@app.route('/auto_tags', methods=['GET', 'POST'])
@login_required
def auto_tags():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    if request.method == 'GET':
        shop_id_select = request.args.get('shop_id_select')
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        tag_list = api.get_splash_page_tag(shop_id=shop_id_select)
        return render_template('new_hotspot/auto_tags.html',
                               shop_id_select=shop_id_select,
                               tags=tags,
                               tag_list=tag_list)
    else:
        tag_id = request.form.get('tag_id')
        shop_id_select = request.form.get('shop_id_select')
        tag_group = api.get_splash_page_tag(tag_id=tag_id,
                                            shop_id=shop_id_select)
        tag_detail = api.get_tag_name_by_tag_id(tag_id)
        return render_template('new_hotspot/config_tag.html',
                               tag_detail=tag_detail,
                               shop_id_select=shop_id_select,
                               tag=tag_group)


@app.route('/fb_auth', methods=['GET'])
def fb_page_auth():
    code = request.args.get('code')
    state = request.args.get('state')
    states = state.split(',')
    redirect_uri_verify = request.url_root.replace('http', 'https') + 'fb_auth'
    url_get_token = settings.FACBOOK_GRAPH_API + "/oauth/access_token?client_id={}&redirect_uri={}&client_secret={}&code={}".format(
        settings.NEXTIFY_FACEBOOK_APP_ID, redirect_uri_verify,
        settings.NEXTIFY_FACEBOOK_APP_SECRET, code)
    result = requests.get(url_get_token)
    result = json.loads(result.text)
    access_token = result.get('access_token')
    access_token_long = fb_long_lived_user_access_token(
        settings.NEXTIFY_FACEBOOK_APP_ID, settings.NEXTIFY_FACEBOOK_APP_SECRET,
        access_token)
    root_url = states[0]
    shop_id_select = states[1]
    redirect_uri = root_url.replace(
        'http',
        'https') + 'facebook/pages?access_token=%s&shop_id_select=%s' % (
            access_token_long, shop_id_select)
    return redirect(redirect_uri)


def fb_long_lived_user_access_token(app_id, app_secret, user_access_token):
    url = settings.FACBOOK_GRAPH_API + '/oauth/access_token?grant_type=fb_exchange_token' \
                                       '&client_id={}&client_secret={}&fb_exchange_token={}'.format(app_id, app_secret,
                                                                                                    user_access_token)
    result = requests.get(url=url)
    if result.status_code != 200:
        return False
    else:
        access_token = json.loads(result.text).get(
            'access_token')  # type: object
        return access_token


@app.route('/facebook/pages', methods=['GET'])
@login_required
def facebook_pages_select():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id_select = request.args.get('shop_id_select')
    access_token = request.args.get('access_token')
    fb_pages = []
    user_id_fb = None

    if access_token:
        url_get_user_id_fb = "https://graph.facebook.com/v6.0/me?fields=id&access_token={}".format(
            access_token)
        result = requests.get(url=url_get_user_id_fb)
        user_fb = json.loads(result.text)
        user_id_fb = user_fb.get('id')

    if user_id_fb:
        get_list_fb_page_url = 'https://graph.facebook.com/v6.0/%s/accounts?access_token=%s' % (
            user_id_fb, access_token)
        result = requests.get(url=get_list_fb_page_url)
        result_fb = json.loads(result.text)
        fb_pages = result_fb.get('data')
    if len(fb_pages) == 0:
        return redirect('/')
    else:
        pages = []
        for page in fb_pages:
            real_profile_pic_url = settings.FACBOOK_GRAPH_API + '/%s/?fields=picture&type=large&redirect=false&access_token=%s' % (
                str(page['id']), str(page['access_token']))
            url_logo = real_url_fb(real_profile_pic_url)
            page['real_profile_pic'] = url_logo
            pages.append(page)
        shop_select = api.get_shop_info(shop_id=shop_id_select)
        return render_template('nextify/facebook_pages.html',
                               shop=shop,
                               user_login=user_login,
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_id_select=shop_id_select,
                               fb_pages=pages,
                               access_token=access_token,
                               get_real_url_fb=real_url_fb,
                               shop_select=shop_select)


@app.route('/facebook/<page_id>/sync', methods=['GET', 'POST'])
@login_required
def page_select_sync_ajax(page_id):
    if request.method == 'GET':
        access_token = request.args.get('access_token')
        page_url = settings.FACBOOK_GRAPH_API + '/%s?fields=' \
                                                'id,name,about,attire,bio,location,parking,hours,emails,website,link&access_token=%s' % (
                                                    page_id, access_token)

        page_info = requests.get(url=page_url)
        result_fb = json.loads(page_info.text)
        url_logo = ''
        url_background = ''
        try:
            url_logo = settings.FACBOOK_GRAPH_API + '/%s/?fields=picture&type=large&redirect=false&access_token=%s' % (
                str(page_id), str(access_token))
            url_logo = real_url_fb(url_logo)

            fb_background = settings.FACBOOK_GRAPH_API + '/%s/?fields=cover&access_token=%s' % (
                str(page_id), str(access_token))
            req_background = requests.get(fb_background)
            req_background_json = req_background.json()
            data_background = req_background_json.get('cover')
            url_background = data_background.get('source')
        except:
            url_logo = str(os.getcwd()) + \
                '/static/images/onboard/profile_default.jpg'
            url_background = str(os.getcwd()) + \
                '/static/images/onboard/cover_default.jpg'
        return render_template('nextify/facebook_sync_modal.html',
                               page=result_fb,
                               page_id=page_id,
                               url_logo=url_logo,
                               url_background=url_background,
                               access_token=access_token)
    else:
        shop_id_select = request.args.get('shop_id_select')
        active_sync = request.form.get('active_sync')
        page_access_token = request.form.get('page_access_token')
        active_sync = True if str(active_sync) == 'true' else False
        if active_sync:
            url_logo = request.form.get('url_logo')
            url_background = request.form.get('url_background')
            email = request.form.get('email')
            website = request.form.get('website')
            facebook_page = request.form.get('facebook_page')
            logo = save_image_from_url(shop_id_select, url_logo, 'logo')
            background = save_image_from_url(shop_id_select, url_background,
                                             'background')

            api.update_shop(shop_id_select,
                            email=email,
                            website=website,
                            id_page=page_id,
                            access_token_page=page_access_token,
                            logo=logo,
                            background=background,
                            facebook_page=facebook_page)

            api.facebook_lead_ad(page_id=page_id,
                                 access_token_page=page_access_token)
        else:
            facebook_page = request.form.get('facebook_page')
            api.update_shop(shop_id_select,
                            id_page=page_id,
                            access_token_page=page_access_token,
                            facebook_page=facebook_page)

            api.facebook_lead_ad(page_id=page_id,
                                 access_token_page=page_access_token)
        return json.dumps({'result': True})


def save_image_from_url(shop_id, url, prefix):
    page = requests.get(url)
    file_data = page.content
    f_name = '%s_%s_%s' % (str(shop_id), str(prefix), str(time.time()))

    logo_filename = \
        hashlib.md5(file_data).hexdigest() + '.' + f_name

    data_logo = {
        'file_name': logo_filename,
        'file_data': base64.b64encode(file_data),
        'origin_name': f_name
    }
    storage_api.save_file(data_logo)
    return logo_filename


def save_image_from_local(shop_id, url, prefix):
    logo_filename = ''
    logo_filename = storage_api.save_new_file_init(url)
    return logo_filename


@app.route('/setting_report_zalo/<shop_id_select>', methods=['POST'])
@login_required
def setting_report_zalo(shop_id_select):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id_select)
    merchant_id = shop_info.get('merchant_id')
    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    # if request.method == 'GET':
    #     return render_template('nextify/setting_report_zalo.html',
    #                            merchant=merchant)
    if request.method == 'POST':
        # phone_form = request.form.get('phone_number')
        # phones = []
        # phone_error = []
        # check_follow_OA = []
        # check_setting_zalo = shop_info.get('zalo_app_id')
        # if not check_setting_zalo or len(check_setting_zalo) < 0:
        #     error = gettext("Chua_cai_dat_cau_hinh_Zalo_OA")
        #     return json.dumps({"result": False,
        #                        'msg': error})
        # if "," in phone_form:
        #     phones = phone_form.split(',')
        # else:
        #     phones.append(phone_form)
        # if phones and len(phones) > 0 and str(phones) != 'None':
        #     for phone in phones:
        #         phone = str(phone).lower()
        #         check_phone = api.get_phone_number(phone)
        #         if check_phone == False:
        #             phone_error.append(phone)
        # if len(phone_error) > 0:
        #     text_check = ""
        #     for check_phone in phone_error:
        #         text_check = text_check + ", " + check_phone
        #     text_check = text_check.lstrip(',')
        #     error = gettext("So") + text_check + gettext(" khong_dung")
        #     return json.dumps({"result": False,
        #                        'msg': error})
        # else:
        #     user_id_zalo = []
        #     for phone in phones:

        #         phone = str(phone).lower().strip()
        #         check_follow = api.check_phone_follow_zaloOA(
        #             shop_id=shop_id_select, phone=phone)
        #         if check_follow == False:
        #             check_follow_OA.append(phone)
        #         else:
        #             user_id_zalo.append(check_follow)
        #     if len(check_follow_OA) > 0:
        #         text_check = ""
        #         for check_follow in check_follow_OA:
        #             text_check = text_check + ", " + check_follow
        #         text_check = text_check.lstrip(',')
        #         error = gettext("So") + text_check + \
        #                 gettext(" chua_follow_Zalo_OA")
        #         return json.dumps({"result": False,
        #                            "msg": error})
        #     api.save_phone_zalo_report(
        #         shop_id=shop_id_select, phones=phones, user_id_zalo=user_id_zalo)
        email_report = request.form.get('email_report')
        active_report = request.form.get('active_report')
        if active_report:
            active_report = True
        else:
            active_report = False
        api.update_shop(shop_id=shop_id_select,
                        email_report=email_report,
                        active_report=active_report)
        if active_report == True:
            producer_data = {"shop_id": str(shop_id_select), "status": "True"}
            producer.send(settings.report_consumer, producer_data)
            producer.flush()
            # api.send_report_email(shop_id_select)
        return json.dumps({'result': True})


@app.route('/preview_data_detect', methods=['GET'])
@login_required
def preview_data_detect():
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    shop_id_select = request.args.get('shop_id_select')
    if request.method == 'GET':
        page = int(request.args.get('current_page', 1))
        # luot den
        min_visit = request.args.get('min_visit')
        max_visit = request.args.get('max_visit')
        sort = request.args.get('sort', 'time_asc')
        filter_tags = request.args.get('real_tags_filter', '')
        tags_array = []
        if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
            tags_array = filter_tags.split(',')
            tags_array = [str(tag) for tag in tags_array]
        list_cus = []
        total = 0
        customers_sources = request.args.get('customers_sources')
        if customers_sources == "on":
            list_cus, real_send = api.filter_detect_customer(shop_id_select,
                                                             sort=sort,
                                                             page=page,
                                                             page_size=7)
            total = api.total_shop_customers(shop_id_select)
            min_visit = ""
            max_visit = ""
            filter_tags = ""
        else:
            list_cus, real_send = api.filter_detect_customer(
                shop_id_select,
                min_visit=min_visit,
                max_visit=max_visit,
                tags_array=tags_array,
                sort=sort,
                page=page,
                page_size=7)

            total = api.total_shop_customers(shop_id_select,
                                             min_visit=min_visit,
                                             max_visit=max_visit,
                                             tags_array=tags_array)
        total_pages = (real_send // 7) + \
            1 if real_send % 7 != 0 else real_send / 7
        return jsonify({
            "data":
            render_template("nextify/data_cus_detect.html",
                            customers=list_cus,
                            current_page=page,
                            min_visit=min_visit,
                            max_visit=max_visit,
                            total=total,
                            total_pages=total_pages,
                            real_send=real_send,
                            sub=total - real_send,
                            merchant=merchant,
                            filter_tags=tags_array),
            "real_send":
            real_send,
            "total":
            total,
            "current_page":
            page,
            "total_pages":
            total_pages
        })


@app.route('/data_cus_pagination_detect', methods=['GET'])
@login_required
def data_cus_pagination_detect():
    merchant = g.merchant
    merchant_id = merchant.get('_id')
    page = int(request.args.get('current_page', 1))
    # luot den
    min_visit = request.args.get('min_visit')
    max_visit = request.args.get('max_visit')
    filter_tags = request.args.get('real_tags_filter', '')
    shop_id_select = request.args.get('shop_id_select')
    sort = request.args.get('sort', 'time_asc')
    customers_sources = request.args.get('customers_sources')
    tags_array = []
    if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
        tags_array = filter_tags.split(',')
        tags_array = [str(tag) for tag in tags_array]
    list_cus = []
    total = 0

    if customers_sources == "on":
        list_cus, real_send = api.filter_detect_customer(shop_id_select,
                                                         sort=sort,
                                                         page=page,
                                                         page_size=7)
        total = api.total_shop_customers(shop_id_select)
        min_visit = ""
        max_visit = ""
        filter_tags = ""
    else:
        list_cus, real_send = api.filter_detect_customer(shop_id_select,
                                                         min_visit=min_visit,
                                                         max_visit=max_visit,
                                                         tags_array=tags_array,
                                                         sort=sort,
                                                         page=page,
                                                         page_size=7)

        total = api.total_shop_customers(shop_id_select,
                                         min_visit=min_visit,
                                         max_visit=max_visit,
                                         tags_array=tags_array)
    total_pages = (real_send / 7) + 1 if real_send % 7 != 0 else real_send / 7
    return render_template("nextify/data_customers_pagination.html",
                           customers=list_cus,
                           current_page=page,
                           min_visit=min_visit,
                           max_visit=max_visit,
                           real_send=real_send,
                           sub=total - real_send,
                           total=total,
                           total_pages=total_pages,
                           merchant=merchant,
                           filter_tags=tags_array)


@app.route('/save_data_detect', methods=['GET'])
@login_required
def save_data_detect():
    shop_id_select = request.args.get('shop_id_select')
    min_visit = request.args.get('min_visit')
    max_visit = request.args.get('max_visit')
    filter_tags = request.args.get('real_tags_filter', '')
    phone_form = request.args.get('phone_number_detect')
    customers_sources = request.args.get('customers_sources')
    is_birthday_notify = request.args.get('is_birthday_notify')
    is_activity = request.args.get('is_activity')
    shop_info = api.get_shop_info(shop_id=shop_id_select)
    phones = []
    phone_error = []
    check_follow_OA = []
    check_setting_zalo = shop_info.get('zalo_app_id')
    if not check_setting_zalo or len(check_setting_zalo) < 0:
        error = gettext("Chua_cai_dat_cau_hinh_Zalo_OA")
        return json.dumps({"result": False, 'msg': error})
    if "," in phone_form:
        phones = phone_form.split(',')
    else:
        phones.append(phone_form)
    if phones and len(phones) > 0 and str(phones) != 'None':
        for phone in phones:
            phone = str(phone).lower()
            check_phone = api.get_phone_number(phone)
            if check_phone == False:
                phone_error.append(phone)
    if len(phone_error) > 0:
        text_check = ""
        for check_phone in phone_error:
            text_check = text_check + ", " + check_phone
        text_check = text_check.lstrip(',')
        error = gettext("So") + text_check + gettext(" khong_dung")
        return json.dumps({"result": False, 'msg': error})
    else:
        for phone in phones:
            user_id_zalo = []
            phone = str(phone).lower().strip()
            check_follow = api.check_phone_follow_zaloOA(
                shop_id=shop_id_select, phone=phone)
            if check_follow == False:
                check_follow_OA.append(phone)
            else:
                user_id_zalo.append(check_follow)
        if len(check_follow_OA) > 0:
            text_check = ""
            for check_follow in check_follow_OA:
                text_check = text_check + ", " + check_follow
            text_check = text_check.lstrip(',')
            error = gettext("So") + text_check + \
                gettext(" chua_follow_Zalo_OA")
            return json.dumps({"result": False, "msg": error})
    tags_array = []
    if filter_tags and len(filter_tags) > 0 and str(filter_tags) != 'None':
        tags_array = filter_tags.split(',')
        tags_array = [str(tag) for tag in tags_array]
    if customers_sources == "on":
        customers = api.save_detect_customer(
            shop_id=shop_id_select,
            phones=phones,
            customers_sources=customers_sources,
            is_birthday_notify=is_birthday_notify,
            is_activity=is_activity)
    else:
        customers = api.save_detect_customer(
            shop_id=shop_id_select,
            phones=phones,
            tags_array=tags_array,
            customers_sources=customers_sources,
            is_birthday_notify=is_birthday_notify,
            min_visit=min_visit,
            max_visit=max_visit,
            is_activity=is_activity)
    return json.dumps({'result': True})


from mongobackup import backup


@app.route('/backup_db', methods=['GET'])
@basic_auth.required
def backup_db():
    export = request.args.get('export')
    if export == '1':
        backup(settings.MONGODB_USER,
               settings.MONGODB_PASSWORD,
               "/var/backups/mongo/",
               database=settings.MONGODB_NAME)
    path = os.getcwd() + "/static/backup_db"
    list_of_files = []

    for filename in os.listdir(path):
        list_of_files.append(filename)
    return render_template('nextify/backup_db.html',
                           list_of_files=list_of_files)


@app.route('/update_priority', methods=['POST'])
@login_required
def update_priority():
    if request.method == 'POST':
        data = json.loads(request.form.get('camp_id'))
        for i in range(len(data)):
            api.update_priority(data[i], i + 1)
    return json.dumps({'success': 1})


@app.route('/update_client_key', methods=['POST'])
@login_required
def update_client_key():
    if request.method == 'POST':
        shop = g.shop
        user_login = g.user
        shop_id = shop['_id']
        merchant_id = shop.get('merchant_id')
        merchant = api.get_merchant(merchant_id)
        client_key = merchant.get('client_key')
        client_key_fr = request.form.get('client_key')
        if not client_key or len(client_key) == 0:
            api.update_merchant_client_key(merchant_id, client_key_fr)
        return json.dumps({'result': True})


@app.route('/update_haravan', methods=['GET', 'POST'])
def update_haravan():
    if request.method == 'GET':
        domain = request.args.get('domain')
        access_token = request.args.get('access_token')
        haravan_id_shop = request.args.get('haravan_id_shop')
        email_haravan = request.args.get('email_haravan')
        return render_template('nextify/connect_haravan.html',
                               domain=domain,
                               access_token=access_token,
                               haravan_id_shop=haravan_id_shop,
                               email_haravan=email_haravan)
    else:
        name = request.form.get('name')
        client_key_fr = request.form.get('client_key')
        domain = request.form.get('domain')
        access_token = request.form.get('access_token')
        haravan_id_shop = request.form.get('haravan_id_shop')
        check = api.check_account_sync_haravan(name, client_key_fr, domain,
                                               access_token, haravan_id_shop)
        if not check:
            return json.dumps({
                'result': False,
                'error': "Thông tin chưa chính xác"
            })
        else:
            producer_data = {
                "task_name": "save_customers_haravan",
                "params": {
                    "domain": domain,
                    "access_token": access_token
                }
            }

            producer_data = json.dumps(producer_data).encode('utf-8')
            producer.send(settings.cms_consumer, producer_data)
            producer.flush()

            return json.dumps({'result': True})


@app.route('/redirect_haravan', methods=['GET'])
def redirect_haravan():
    if request.method == 'GET':
        base64_message = request.args.get('message')
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        code = message_bytes.decode('ascii')
        app_id = settings.APP_ID_HARAVAN
        app_secret = settings.APP_SECRET_HARAVAN
        redirect_uri = settings.REDIRECT_URI_HARAVAN
        # get access token from code
        url = "https://accounts.haravan.com/connect/token"
        payload = {
            'code': code,
            'client_id': app_id,
            'client_secret': app_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.request("POST", url, headers=headers, data=payload)
        result = response.json()
        access_token = result.get('access_token')
        # sign up webhook
        url_signup = "https://webhook.haravan.com/api/subscribe"
        header_signup = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        response_signup = requests.request("POST",
                                           url_signup,
                                           headers=header_signup)
        # get info shop on haravan
        url_info = "https://apis.haravan.com/com/shop.json"
        header = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        response_info = requests.request("GET", url_info, headers=header)
        result_info = response_info.json()
        haravan_shop = result_info.get('shop')
        haravan_domain = haravan_shop.get('domain')
        haravan_id_shop = haravan_shop.get('id')
        email_haravan = haravan_shop.get('email')
        return render_template('nextify/connect_haravan.html',
                               domain=haravan_domain,
                               access_token=access_token,
                               haravan_id_shop=haravan_id_shop,
                               email_haravan=email_haravan)


@app.route('/signup_from_haravan', methods=['POST'])
def signup_from_haravan():
    name_company = request.form.get('name_company')
    address = request.form.get('address')
    user_contact = request.form.get('user_contact')
    business = request.form.get('business')
    professional_titles = request.form.get('professional_titles')
    email_contact = request.form.get('email_contact')
    phone_contact = request.form.get('phone_contact')
    domain = request.form.get('domain')
    access_token = request.form.get('access_token')
    haravan_id_shop = request.form.get('haravan_id_shop')
    email_haravan = request.form.get('email_haravan')
    number_res = request.form.get('number_res', '')
    website = request.form.get('website', '')
    if not api.get_phone_number(phone_contact) or not \
            all([x.isdigit() for x in phone_contact]):
        error = gettext("So_dien_thoai_chua_dung_dinh_dang")
        return json.dumps({'error': error})
    is_valid = validate_email(email_contact)
    if not is_valid:
        error = gettext("Email_chua_dung_dinh_dang")
        return json.dumps({'error': error})
    ts = time.time() + 25200
    time_create = datetime.utcfromtimestamp(ts).strftime('%H:%M %d-%m-%Y')
    email_content = render_template(
        'nextify/content_register_crm_haravan.html',
        name_company=name_company,
        address=address,
        business=business,
        user_contact=user_contact,
        professional_titles=professional_titles,
        email_contact=email_contact,
        phone_contact=phone_contact,
        number_res=number_res,
        website=website,
        time_create=str(time_create))
    subject = "[Nextify]"
    list_email = settings.MAIL_REGISTER_HARAVAN
    for to_email in list_email:
        email_api.send_by_mail_gun('Nextify', to_email, subject, email_content)
    api.save_info_signup(domain, access_token, haravan_id_shop, email_haravan)
    return json.dumps({"result": True})


# @app.route('/save_haravan_info', methods=['POST'])
# @login_required
# def save_haravan_info():
#     shop = g.shop
#     merchant_id = shop.get('merchant_id')
#     email = request.form.get('email' )
#     domain, access_token = api.create_app_haravan(email, merchant_id)
#     producer_data = {
#         "task_name": "save_customers_haravan",
#         "params": {
#             "domain": domain,
#             "access_token": access_token
#         }
#     }

#     producer_data = json.dumps(producer_data).encode('utf-8')
#     producer.send(settings.cms_consumer, producer_data)
#     producer.flush()
#     return json.dumps({"result": True})


@app.route('/save_bizfly', methods=['POST'])
@login_required
def save_bizfly():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    name_app = "bizfly"
    type_app = 'CRM'
    api_key = request.form.get('api_key')
    api_secret_key = request.form.get('api_secret_key')
    project_token = request.form.get('project_token')

    acc_timestamp = int(time.time())
    string_build = str(acc_timestamp) + str(project_token)
    string_sign = hmac.new(str(api_secret_key), string_build,
                           hashlib.sha512).hexdigest()

    url = settings.API_BIZFLY + "/_api/base-table/struct"

    payload = {'table': 'data_customer'}

    headers = {
        'cb-access-key': str(api_key),
        'cb-project-token': str(project_token),
        'cb-access-timestamp': str(acc_timestamp),
        'cb-access-sign': str(string_sign)
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    if str(response_json['status']) == '-1':
        return json.dumps({'error': gettext("Thông tin chưa chính xác")})
    elif str(response_json['status']) == '1':
        api.check_sync_bizfly(merchant_id, name_app, type_app, api_key,
                              api_secret_key, project_token)
        producer_data = {
            "task_name": "save_customers_bizfly",
            "params": {
                "merchant_id": merchant_id
            }
        }

        producer_data = json.dumps(producer_data).encode('utf-8')
        producer.send(settings.cms_consumer, producer_data)
        producer.flush()
        return json.dumps({"result": "True"})


@app.route('/login_from_partner', methods=['GET'])
def login_from_partner():
    merchant_id = request.args.get('merchant_id')
    merchant = api.get_merchant(merchant_id=merchant_id)
    phone = merchant.get('phone')
    session['shop_id'] = None
    session['is_login'] = phone
    session['is_hq'] = phone
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    shop_ids = [shop['_id'] for shop in shop_in_mer]
    g.shops = [api.get_shop_info(i) for i in shop_ids]
    session['is_superuser'] = phone
    session['merchant_id'] = str(merchant_id)
    if len(shop_ids) > 0:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('setup_first_login'))


@app.route('/login_partner', methods=['GET', 'POST'])
def login_partner():
    if request.method == 'POST':
        username = request.form['phone']
        password = request.form['password']
        role = request.form.get('role')
        user = None
        partner_id = None
        if role == 'admin':
            if api.get_phone_number(username):
                user = api.DATABASE.dealers.find_one({'phone': username})
            elif validate_email(username):
                user = api.DATABASE.dealers.find_one({'email': username})
            else:
                user = api.DATABASE.dealers.find_one({'id_login': username})
        if role == 'ops':
            if api.get_phone_number(username):
                user = api.DATABASE.operations.find_one({'phone': username})
            elif validate_email(username):
                user = api.DATABASE.operations.find_one({'email': username})
            else:
                user = api.DATABASE.operations.find_one({'id_login': username})
        if role == 'sup':
            if api.get_phone_number(username):
                user = api.DATABASE.supporter.find_one({'phone': username})
            elif validate_email(username):
                user = api.DATABASE.supporter.find_one({'email': username})
            else:
                user = api.DATABASE.supporter.find_one({'id_login': username})
        error = None

        if not user:
            error = 'Tên đăng nhập không đúng.'
            return render_template('nextify/login_partner.html', error=error)
        elif not (api.check_hash(password, user.get('pass_login'))):
            error = 'Mật khẩu không đúng.'
            return render_template('nextify/login_partner.html', error=error)
        else:
            session.clear()
            if role == 'admin':
                partner_id = user.get('_id')
            else:
                partner_id = user.get('partner')
            session['logged_in'] = True
            session['partner_id'] = str(partner_id)
            session['username'] = user['id_login']
            if str(partner_id
                   ) == '5cd541ade452d5bd45cbb58d' and role == 'admin':
                session['role'] = 'super_admin'
            else:
                session['role'] = role
            return redirect(url_for('list_merchants'))

    return render_template('nextify/login_partner.html')


@app.route('/list_merchants', methods=['GET', 'POST'])
def list_merchants():
    partner_id = session.get('partner_id')
    role = session.get('role')
    page = int(request.args.get('page', 1))
    if str(partner_id) == '5cd541ade452d5bd45cbb58d' and role in [
            'admin', 'super_admin'
    ]:
        merchants = api.get_merchants(page, settings.ITEMS_PER_PAGE)
        merchants_count = api.get_merchants_count()
        partners = api.get_dealers()
    else:
        merchants = api.get_merchants_partner(partner_id, page,
                                              settings.ITEMS_PER_PAGE)
        merchants_count = api.get_merchants_partner_count(partner_id)
    pagination = Pagination(page=page,
                            total=merchants_count,
                            per_page=settings.ITEMS_PER_PAGE,
                            css_framework='bootstrap3')
    return render_template(
        'nextify/list_merchants.html',
        partner_id=partner_id,
        role=role,
        merchants=merchants,
        page=page,
        pagination=pagination,
        total=merchants_count,
    )


@app.route('/ajax_survey/<shop_id_select>', methods=['GET'])
@login_required
def ajax_survey(shop_id_select):
    page = request.args.get('page', 1)
    pages = api.list_survey_splash(shop_id_select,
                                   page=int(page),
                                   page_size=settings.ITEMS_PER_PAGE)
    pages = [{
        'id': str(page['_id']),
        'text': page['question']
    } for page in pages]

    return jsonify({'pagination': {"more": True}, 'results': pages})


@app.route('/ajax_spin/<shop_id_select>', methods=['GET'])
@login_required
def ajax_spin(shop_id_select):
    page = request.args.get('page', 1)
    pages = api.list_mini_game(shop_id_select,
                               page=int(page),
                               page_size=settings.ITEMS_PER_PAGE)
    results = []
    for page in pages:
        item = {}
        item['id'] = str(page['_id'])
        info = page.get('info')
        name = info.get('name')
        item['text'] = name
        results.append(item)

    return jsonify({'pagination': {"more": True}, 'results': results})


@app.route('/wifi_camp/<shop_id_select>/<step>', methods=['GET', 'POST'])
@login_required
def ajax_step_splash(shop_id_select, step):
    if request.method == 'POST':
        data = request.form.get('data')
        step_name = 'step_' + step
        session[step_name] = data
        return json.dumps({'result': True})
    else:
        step_name = 'step_' + step
        data = session.get(step_name)
        if data:
            return json.dumps({'result': True, 'data': data})
        else:
            return json.dumps({'result': False})


@app.route('/preview/<type_page>/<shop_id_select>/<camp_id>/<step>',
           methods=['GET', 'POST'])
@login_required
def preview_new_step(type_page, shop_id_select, camp_id, step):
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    if str(type_page) == 'collect':
        login_form = api.get_detail_step(shop_id_select, camp_id, type_page,
                                         step)
        return render_template('wifi_portal/register.html',
                               login_form=login_form,
                               shop_select=shop_select)
    if str(type_page) == 'survey':
        survey = api.get_detail_step(shop_id_select, camp_id, type_page, step)
        survey_id = survey.get('survey_id')
        survey_item = api.get_survey_splash(shop_id_select, survey_id)
        merchant_id = shop_select.get('merchant_id')
        survey_type = survey_item.get('survey_type')
        if survey_type == "multi_select":
            return render_template('wifi_portal/survey.html',
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   survey_item=survey_item)
        elif survey_type == "one_select":
            return render_template('wifi_portal/survey_single.html',
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   survey_item=survey_item)
        elif survey_type == 'rating':
            if merchant_id == "5dddd6d006e7eca17bd8e850":
                return render_template('wifi_portal/survey_rating_anvui.html',
                                       shop_select=shop_select,
                                       shop_id_select=shop_id_select,
                                       survey_item=survey_item)
            return render_template('wifi_portal/survey_rating.html',
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   survey_item=survey_item)
    if str(type_page) == 'spin':
        spin = api.get_detail_step(shop_id_select, camp_id, type_page, step)
        spin_id = spin.get('spin_id')
        url = '/game/' + spin_id
        return redirect(url)
    if type_page == '0':
        return render_template('new_hotspot/404.html')
    if type_page == 'connect_success':
        connect_success = api.get_detail_step(shop_id_select, camp_id,
                                              type_page, step)
        return render_template(
            'wifi_portal/connect_success.html',
            connect_success=connect_success,
            shop=shop_select,
        )
    card = api.get_detail_step(shop_id_select, camp_id, type_page, step)
    user = {
        "age_range": None,
        "relationship_status": None,
        "home_town": None,
        "fb_id": None,
        "phone": "0946xx0912",
        "birthday": "12-09",
        "id": "Thomas",
        "name": "Thomas",
        "gender": "",
        "email": None,
        "year_birthday": None
    }
    title = card.get('title', '')
    if title or str(title) != 'None':
        title = title.strip()
        title = title.replace('{{ name }}', user.get('name', ''))
    if str(type_page) == 'image':
        title = card.get('title_image', '')
        content = card.get('content_image', '')
        if content or str(content) != 'None':
            content = content.strip()
            content = content.replace('{{ name }}', user.get('name', ''))
        return render_template(
            'wifi_portal/event_v2.html',
            user=user,
            shop=shop_select,
            shop_id=shop_id_select,
            shop_select=shop_select,
            shop_id_select=shop_id_select,
            card=card,
            content=content,
            title=title,
        )
    if str(type_page) == 'youtube':
        title = card.get('title_youtube', '')
        content = card.get('content_youtube', '')
        content_text_youtube = card.get('content_text_youtube', '')
        if content or str(content) != 'None':
            content = content.strip()
            content = content.replace('{{ name }}', user.get('name', ''))
        return render_template('wifi_portal/event_v2.html',
                               user=user,
                               shop=shop_select,
                               shop_id=shop_id_select,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               card=card,
                               content=content,
                               title=title,
                               content_text_youtube=content_text_youtube,
                               type_page='youtube')
    if str(type_page) == 'slides':
        slides = card.get('slides')
        title_slides = card.get('title_slides')
        slides = card.get('slides')
        return render_template('wifi_portal/default.html',
                               user=user,
                               shop=shop_select,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               slides=slides,
                               shop_id=shop_id_select,
                               card=card)


@app.route('/preview_survey/<shop_id_select>/<survey_id>',
           methods=['GET', 'POST'])
@login_required
def preview_survey(shop_id_select, survey_id):
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    survey_item = api.get_survey_splash(shop_id_select, survey_id)
    merchant_id = shop_select.get('merchant_id')
    survey_type = survey_item.get('survey_type')
    if survey_type == "multi_select":
        return render_template('wifi_portal/survey.html',
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               survey_item=survey_item)
    elif survey_type == "one_select":
        return render_template('wifi_portal/survey_single.html',
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               survey_item=survey_item)
    elif survey_type == 'rating':
        if merchant_id == "5dddd6d006e7eca17bd8e850":
            return render_template('wifi_portal/survey_rating_anvui.html',
                                   shop_select=shop_select,
                                   shop_id_select=shop_id_select,
                                   survey_item=survey_item)
        return render_template('wifi_portal/survey_rating.html',
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               survey_item=survey_item)


@app.route('/close_campaign', methods=['POST'])
@login_required
def close_campaign():
    shop_id = request.form.get('shop_id')
    camp_id = request.form.get('camp_id')
    api.close_campaign(shop_id, camp_id)
    return json.dumps({'result': True})


@app.route('/files', methods=['POST'])
@login_required
def files():
    user = g.user
    files = request.files
    img_image = files.get('file')
    data = request.form.to_dict()
    type_page = data.get('type_page')
    if type_page == 'image':
        photo = None
        fid = ""
        if img_image and \
                img_image.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            # luu db
            photo = storage_api.save_new_file(img_image)
        return json.dumps({'result': True, 'new_img': photo})

    elif type_page == 'register_image' or type_page == 'return_image':
        photo = None
        if img_image and \
                img_image.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            photo = storage_api.save_new_file(img_image)
            if type_page == 'register_image':
                session['image_register'] = photo
            else:
                session['image_return'] = photo
        return json.dumps({'result': True, 'new_img': photo})

    else:
        slides = data.get('slides')
        slides = slides.replace('[', '')
        slides = slides.replace(']', '')
        slides = slides.replace("u'", '')
        slides = slides.replace("'", '')
        arr_slides = slides.split(',')
        photo = None
        if img_image and \
                img_image.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            # luu db
            photo = storage_api.save_new_file(img_image)
            arr_slides.append(photo)
        return json.dumps({
            'result': True,
            'slides': arr_slides,
            'new_img': photo
        })


@app.route('/setting_starbucks', methods=['POST'])
@login_required
def setting_starbucks():
    welcome_text_vn = request.form.get('welcome_text_vn')
    welcome_text_eng = request.form.get('welcome_text_eng')
    tcs_vn = request.form.get('tcs_vn')
    tcs_eng = request.form.get('tcs_eng')
    welcome_button_eng = request.form.get('welcome_button_eng')
    welcome_button_vn = request.form.get('welcome_button_vn')
    subject_email = request.form.get('subject_email')
    content_email = request.form.get('content_email')
    shop_id = request.form.get('shop_id')
    campaign_id = request.form.get('campaign_id')
    subject_email = request.form.get('subject_email')
    content_email = request.form.get('content_email')
    expire_authen = request.form.get('expire_authen')
    term = {
        'welcome_text_vn': welcome_text_vn,
        'welcome_text_eng': welcome_text_eng,
        'tcs_vn': tcs_vn,
        'tcs_eng': tcs_eng,
        'welcome_button_vn': welcome_button_vn,
        'welcome_button_eng': welcome_button_eng
    }
    settings_starbucks = {
        'subject_email': subject_email,
        'content_email': content_email,
        'expire_authen': expire_authen
    }
    api.update_verify_email_campaign(shop_id, campaign_id, term, subject_email,
                                     content_email)
    api.update_shop(shop_id=shop_id, settings_starbucks=settings_starbucks)

    return json.dumps({'result': True})


@app.route('/preview_tc_starbucks/<shop_id_select>/<campaign_id>',
           methods=['GET'])
@login_required
def preview_tc_starbucks(shop_id_select, campaign_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    is_HQ = True
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    lang = 'vn'
    detail = api.get_detail_step(shop_id_select, campaign_id, "terms", "1")
    return render_template('new_hotspot/tc_starbucks.html',
                           shop=shop_select,
                           lang=lang,
                           detail=detail)


@app.route('/preview_collect_starbucks/<shop_id_select>/<campaign_id>',
           methods=['GET'])
@login_required
def preview_collect_starbucks(shop_id_select, campaign_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    is_HQ = True
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    lang = 'vn'
    login_form = api.get_detail_step(shop_id_select, campaign_id, 'collect',
                                     '2')
    return render_template('new_hotspot/register_starbucks.html',
                           shop=shop_select,
                           shop_id_select=shop_id_select,
                           login_form=login_form,
                           lang=lang)


@app.route('/preview_success_starbucks/<shop_id_select>/<campaign_id>',
           methods=['GET'])
@login_required
def preview_success_starbucks(shop_id_select, campaign_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    is_HQ = True
    shop_select = api.get_shop_info(shop_id=shop_id_select)
    lang = 'vn'
    return render_template('new_hotspot/success_starbucks.html',
                           shop=shop_select,
                           lang=lang)


@app.route("/resend_verify_email/<log_id>", methods=['GET'])
@login_required
def resend_verify_email(log_id):
    shop = g.shop
    user_login = g.user
    merchant = g.merchant
    log = api.get_otp_log_by_id(log_id)
    shop_id = log.get('shop_id')
    merchant_id = log.get('merchant_id')
    user_id = log.get('user_id')
    user = api.get_customer_by_user_id(merchant_id, user_id, shop_id)
    user_name = 'customer'
    if user:
        info_user = user.get('user')
        user_name = info_user.get('name')
    shop_select = api.get_shop_info(shop_id=shop_id)
    if not shop_select:
        abort(404)
    settings_starbucks = shop.get('settings_starbucks')
    mail_settings = merchant.get('mail_settings')
    if mail_settings and settings_starbucks:
        mail_name = mail_settings.get('mail_name')
        mail_user = mail_settings.get('mail_user')
        mail_pass = mail_settings.get('mail_pass')
        mail_server = mail_settings.get('mail_server')
        mail_port = mail_settings.get('mail_port')
        mail_ssl = mail_settings.get('mail_ssl')

        subject = settings_starbucks.get('subject_email')
        email_test = log.get('reception')
        merchant_name = 'Starbucks Wifi'
        key = str(user_id) + str(time.time())
        client_key = hashlib.md5(str(key)).hexdigest()
        host_url = settings.HOST_URL_STARBUCKS
        authen_url = host_url + 'active_email?client_key'
        link = "<a href=" + authen_url + "=" + client_key + \
            ">" + authen_url + "=" + client_key + "</a>"
        email_content = settings_starbucks.get('content_email')
        email_content = email_content.replace('{{ name }}', user_name)
        email_content = email_content.replace('{{ link }}', link)

        if mail_user and len(mail_user) > 0 and mail_pass and \
                len(mail_pass) > 0 and mail_server and len(mail_server) > 0:
            activity_id = api.insert_otp_log(merchant_id, shop_id, user_id,
                                             'email', email_content,
                                             client_key, email_test)
            if 'nextify' in str(mail_server) or 'mail_gun' in mail_server:
                from_obj = '''%s <mailgun@%s>''' % (merchant_name, mail_user)
                r = requests.post(mail_server,
                                  auth=("api", mail_pass),
                                  data={
                                      "from": from_obj,
                                      "to": [email_test],
                                      "subject": subject,
                                      "html": email_content
                                  })
                if r.status_code == 200:
                    api.update_resend_activity(activity_id, True)
                    return json.dumps({'result': True})
                else:
                    api.update_resend_activity(activity_id, False)
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext(
                            "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                        )
                    })
            elif 'sendgrid' in str(mail_server):
                sg = sendgrid.SendGridAPIClient(api_key=mail_pass)
                from_email = Email(mail_user)
                to_email = To(email_test)
                subject = subject
                content = Content("text/html", email_content)
                mail = Mail(from_email, to_email, subject, content)
                try:
                    response = sg.client.mail.send.post(
                        request_body=mail.get())

                    if response.status_code == 202:
                        api.update_resend_activity(activity_id, True)
                        return json.dumps({'result': True})
                    else:
                        api.update_resend_activity(activity_id, False)
                        return json.dumps({
                            'result':
                            False,
                            'error':
                            gettext(
                                "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                            )
                        })

                except Exception as e:
                    api.update_resend_activity(activity_id, False)
                    return json.dumps({
                        'result':
                        False,
                        'error':
                        gettext(
                            "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                        )
                    })
            else:
                if 'gmail' in mail_server:
                    mail_port = 587
                    try:
                        msg = email.message.Message()
                        msg['Subject'] = subject
                        msg['From'] = mail_user
                        msg['To'] = email_test
                        msg.add_header('Content-Type', 'text/html')
                        msg.set_payload(email_content)
                        s = smtplib.SMTP(mail_server, int(mail_port))
                        s.ehlo()
                        s.starttls()
                        s.login(str(mail_user), str(mail_pass))
                        s.sendmail(mail_user, email_test, msg.as_string())
                        s.close()
                        api.update_resend_activity(activity_id, True)
                        return json.dumps({'result': True})
                    except Exception as e:
                        api.update_resend_activity(activity_id, False)
                        return json.dumps({
                            'result':
                            False,
                            'error':
                            gettext(
                                "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                            )
                        })
                else:
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = 'Starbucks Wifi'
                        msg['To'] = ', '.join([email_test])
                        msg['Subject'] = subject
                        msg.add_header('Content-Type', 'text/html')
                        msg.set_payload(email_content)

                        server = smtplib.SMTP(mail_server, int(mail_port))
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.login(mail_user, mail_pass)
                        server.sendmail(mail_user, [email_test],
                                        msg.as_string())
                        server.close()
                        api.update_resend_activity(activity_id, True)
                        return json.dumps({'result': True})
                    except Exception as e:
                        api.update_resend_activity(activity_id, False)
                        return json.dumps({
                            'result':
                            False,
                            'error':
                            gettext(
                                "Khong_thanh_cong,_vui_long_kiem_tra_lai_cau_hinh_Email."
                            )
                        })

        else:
            return json.dumps({
                'result':
                False,
                'error':
                gettext(
                    "Ban_chua_cau_hinh_Email_Server._Vui_long_cau_hinh_Email_Server_truoc."
                )
            })
    else:
        return json.dumps({
            'result':
            False,
            'error':
            gettext(
                "Ban_chua_cau_hinh_Email_Server._Vui_long_cau_hinh_Email_Server_truoc."
            )
        })


@app.route('/search_email', methods=['POST'])
@login_required
def search_email():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_id = shop.get('_id')
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    text_query = request.form.get('text_query', '')
    shop_id_select = request.form.get('shop_id_select', 'all')
    if text_query:
        text_query = text_query.strip()
    else:
        return redirect('/email_otp')
    results = []
    if shop_id_select and str(shop_id_select) != 'all':
        results = mongo_search.search_email_by_text(merchant_id, text_query)
    else:
        results = mongo_search.search_email_by_text(merchant_id, text_query)
    pagination = ''
    return render_template('nextify/search_email_result.html',
                           merchant=merchant,
                           shop=shop,
                           loc_id=shop_id_select,
                           user_login=user_login,
                           shop_in_mer=shops,
                           pagination=pagination,
                           logs=results)


@app.route('/apps/khai_bao_y_te', methods=['GET', 'POST'])
@login_required
def redirect_khai_bao_y_te():
    shop = g.shop
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    user_login = g.user
    url = '/apps/khai_bao_y_te/' + str(shop_id)
    return redirect(url)


@app.route('/apps/khai_bao_y_te/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def khai_bao_y_te(shop_id_select):
    user_login = g.user
    shop_info = api.get_shop_info(shop_id=shop_id_select)
    merchant_id = shop_info.get('merchant_id')
    merchant = ''
    if merchant_id and merchant_id != '0':
        merchant = api.get_merchant(merchant_id)
    else:
        return redirect('/')

    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        medical_declaration = {}
        medical_declaration = shop_info.get('medical_declaration')
        list_declaration = api.get_declaration_shop(shop_id_select, page,
                                                    settings.ITEMS_PER_PAGE)
        total = api.count_get_declaration_shop(shop_id_select)
        pagination = Pagination(page=page,
                                total=total,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        return render_template('nextify/khai_bao_y_te.html',
                               merchant=merchant,
                               shop_select=shop_info,
                               shop_id_select=shop_id_select,
                               user_login=user_login,
                               shop_in_mer=shops,
                               page=page,
                               page_size=settings.ITEMS_PER_PAGE,
                               medical_declaration=medical_declaration,
                               list_declaration=list_declaration)
    else:
        number_time = request.form.get('number_time')
        email_notify = request.form.get('email_notify')
        phone_notify = request.form.get('phone_notify')
        zalo_notify = request.form.get('zalo_notify')
        warning_crowded = request.form.get('warning_crowded')
        status = request.form.get('status')
        if status:
            status = True
        else:
            status = False
        info = {}
        info['number_time'] = number_time
        info['email_notify'] = email_notify
        info['phone_notify'] = phone_notify
        info['zalo_notify'] = zalo_notify
        info['warning_crowded'] = warning_crowded
        info['status'] = status
        check_setting = shop_info.get('medical_declaration')
        if not check_setting:
            info['question_1'] = True
            info['question_2'] = True
            info['question_3'] = True
            info['question_4'] = True
        else:
            info['question_1'] = check_setting.get('question_1')
            info['question_2'] = check_setting.get('question_2')
            info['question_3'] = check_setting.get('question_3')
            info['question_4'] = check_setting.get('question_4')
        api.update_shop(shop_id=shop_id_select, medical_declaration=info)

        return json.dumps({'result': True})


@app.route('/tokhaiyte/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def tokhaiyte(shop_id_select):
    shop_info = api.get_shop_info(shop_id=shop_id_select)
    check_setting = shop_info.get('medical_declaration')
    if request.method == 'GET':
        question_1 = True
        question_2 = True
        question_3 = True
        question_4 = True
        if check_setting:
            question_1 = check_setting.get('question_1')
            question_2 = check_setting.get('question_2')
            question_3 = check_setting.get('question_3')
            question_4 = check_setting.get('question_4')
        return render_template('wifi_portal_preview/tokhaiyte.html',
                               question_1=question_1,
                               question_2=question_2,
                               question_3=question_3,
                               question_4=question_4)
    else:
        question_1 = request.form.get('question_1')
        question_2 = request.form.get('question_2')
        question_3 = request.form.get('question_3')
        question_4 = request.form.get('question_4')
        if question_1:
            question_1 = True
        else:
            question_1 = False
        if question_2:
            question_2 = True
        else:
            question_2 = False
        if question_3:
            question_3 = True
        else:
            question_3 = False
        if question_4:
            question_4 = True
        else:
            question_4 = False
        info = {}
        info['number_time'] = check_setting.get('number_time')
        info['email_notify'] = check_setting.get('email_notify')
        info['phone_notify'] = check_setting.get('phone_notify')
        info['zalo_notify'] = check_setting.get('zalo_notify')
        info['warning_crowded'] = check_setting.get('warning_crowded')
        info['status'] = check_setting.get('status')
        info['question_1'] = question_1
        info['question_2'] = question_2
        info['question_3'] = question_3
        info['question_4'] = question_4
        api.update_shop(shop_id=shop_id_select, medical_declaration=info)
        return json.dumps({'result': True})


@app.route('/create_visit_log', methods=['GET', 'POST'])
@login_required
def create_visit_log():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if request.method == 'GET':
        shops = []
        if g.role == '3':
            shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                shops.append(shop_mer)
        else:
            locations = g.locations
            if len(locations) > 0:
                shops = [api.get_shop_info(shop_id=loc) for loc in locations]

        return render_template('nextify/create_visit_log.html',
                               shop=shop,
                               user_login=user_login,
                               shop_in_mer=shops,
                               merchant=merchant)
    else:
        shop_id = request.form.get('shop_select')
        client_mac = request.form.get('client_mac')
        visits = request.form.get('visits')
        user_info = api.get_user_info(client_mac=client_mac)
        if not user_info:
            user_id = api.register_client_mac(client_mac)
        else:
            user_id = user_info.get('_id')
        user_loc = api.get_user_loc(client_mac, shop_id)
        if user_loc:
            user_id = user_loc.get('user_id')
        else:
            api.create_customer(shop_id, user_id)
        api.remove_visit_shop(user_id, shop_id)
        api.create_visit_log(user_id, shop_id, visits)
        return json.dumps({'result': True})


@app.route('/wifi_ads_detail', methods=['GET', 'POST'])
@login_required
def wifi_ads_detail():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == 'GET':
        session.pop('step_1', None)
        session.pop('step_2', None)
        session.pop('step_3', None)
        session.pop('step_4', None)
        session.pop('current_step', None)
        campaign_id = request.args.get('campaign_id')
        camp_init = request.args.get('init')
        if str(campaign_id) == "add":
            campaign_id = api.create_new_wifi_ads(merchant_id)
        campaign_details = {}
        group_customer = {}
        group_distribution = {}
        detail_step_connect = []
        list_step = []
        list_tags = []
        type_camp = ''
        campaigns = api.get_all_camp_ads(merchant_id)
        if campaign_id:
            campaign_details = api.get_new_wifi_ads_by_id(campaign_id)
            type_camp = campaign_details.get('type')
            list_step = api.get_list_step_wifi_ads(campaign_id)
            group_customer = campaign_details.get('group_customer')
            group_distribution = campaign_details.get('group_distribution', {})
            if group_customer:
                for tag in group_customer.get('tags_group_customer'):
                    list_tags.append(str(tag))

            detail_step_connect = api.get_details_step_wifi_ads(
                merchant_id, campaign_id, 'connect_success', '4')
            step_1 = campaign_details.get('step_1')
            session['step_1'] = step_1
            step_2 = campaign_details.get('step_2')
            session['step_2'] = step_2
            step_3 = campaign_details.get('step_3')
            session['step_3'] = step_3
            step_4 = campaign_details.get('step_4')
            session['step_4'] = step_4
        session['current_step'] = '1'
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        return render_template('new_hotspot/wifi_ads_wizard.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               campaign_details=campaign_details,
                               shop_in_mer=shops,
                               group_customer=group_customer,
                               group_distribution=group_distribution,
                               detail_step_connect=detail_step_connect,
                               list_step=list_step,
                               campaign_id=campaign_id,
                               list_tags=list_tags,
                               camp_init=camp_init,
                               campaigns=campaigns,
                               tags=tags)
    else:
        merchant_id = request.form.get('merchant_id')
        camp_id = request.form.get('camp_id')
        step = request.form.get('step')
        prev_step = request.form.get('prev_step')
        choose_page = request.form.get('choose_page')
        if not choose_page or choose_page == "0" and ('step_' +
                                                      str(step)) in session:
            choose_page = session['step_' + str(step)]
        elif choose_page and choose_page != "0":
            choose_page = choose_page
        else:
            choose_page = "0"
        detail_step = {}
        if choose_page != '0':
            detail_step = api.get_details_step_wifi_ads(
                merchant_id, camp_id, choose_page, step)
        # list_survey_splash = api.list_survey_splash(
        #     shop_id_select, page=None, page_size=settings.ITEMS_PER_PAGE)
        # list_spin_splash = api.list_mini_game(
        #     shop_id_select, page=None, page_size=settings.ITEMS_PER_PAGE)
        list_survey_splash = api.list_survey_merchant(merchant_id)
        list_spin_splash = api.list_spin_merchant(merchant_id)
        list_templates = api.get_temps_ads_by_merchant(merchant_id)
        session['current_step'] = step
        medical_declaration = {}
        return render_template('new_hotspot/wifi_ads_each_step.html',
                               merchant=merchant,
                               step=step,
                               detail_step=detail_step,
                               list_survey_splash=list_survey_splash,
                               list_spin_splash=list_spin_splash,
                               medical_declaration=medical_declaration,
                               list_templates=list_templates,
                               choose_page=choose_page)


@app.route('/wifi_ads_config', methods=['GET', 'POST'])
@login_required
def wifi_ads_config():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == 'GET':
        return render_template('new_hotspot/wifi_ads_config.html',
                               merchant=merchant)


@app.route('/wifi_ads_config/sales', methods=['GET', 'POST'])
@login_required
def wifi_ads_config_sales():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == 'GET':
        return render_template(
            'new_hotspot/wifi_ads_config_sales.html',
            merchant=merchant,
        )


@app.route('/wifi_ads/export_report_ads', methods=['GET', 'POST'])
@login_required
def export_report_ads():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == 'GET':
        return render_template(
            'nextify/export_report_ads.html',
            merchant=merchant,
        )


@app.route('/close_wifi_ads', methods=['POST'])
@login_required
def close_wifi_ads():
    merchant_id = request.form.get('merchant_id')
    camp_id = request.form.get('camp_id')
    api.close_wifi_ads_camp(merchant_id, camp_id)
    return json.dumps({'result': True})


@app.route('/preview_survey_ads/<merchant_id>/<survey_id>',
           methods=['GET', 'POST'])
@login_required
def preview_survey_ads(merchant_id, survey_id):
    merchant = api.get_merchant(merchant_id=merchant_id)
    survey_item = api.get_survey_item(survey_id)
    survey_type = survey_item.get('survey_type')
    if survey_type == "multi_select":
        return render_template('wifi_portal/survey.html',
                               shop_select=merchant,
                               survey_item=survey_item)
    elif survey_type == "one_select":
        return render_template('wifi_portal/survey_single.html',
                               shop_select=merchant,
                               survey_item=survey_item)
    elif survey_type == 'rating':
        if merchant_id == "5dddd6d006e7eca17bd8e850":
            return render_template('wifi_portal/survey_rating_anvui.html',
                                   shop_select=merchant,
                                   survey_item=survey_item)
        return render_template('wifi_portal/survey_rating.html',
                               shop_select=merchant,
                               survey_item=survey_item)


@app.route('/preview_ads/<type_page>/<merchant_id>/<camp_id>/<step>',
           methods=['GET', 'POST'])
@login_required
def preview_ads(type_page, merchant_id, camp_id, step):
    merchant = api.get_merchant(merchant_id=merchant_id)
    if str(type_page) == 'collect':
        login_form = api.get_details_step_wifi_ads(merchant_id, camp_id,
                                                   type_page, step)
        return render_template('wifi_portal/register.html',
                               login_form=login_form,
                               shop_select=merchant)
    if str(type_page) == 'survey':
        survey = api.get_details_step_wifi_ads(merchant_id, camp_id, type_page,
                                               step)
        survey_id = survey.get('survey_id')
        survey_item = api.get_survey_item(survey_id)
        survey_type = survey_item.get('survey_type')
        if survey_type == "multi_select":
            return render_template('wifi_portal/survey.html',
                                   shop_select=merchant,
                                   survey_item=survey_item)
        elif survey_type == "one_select":
            return render_template('wifi_portal/survey_single.html',
                                   shop_select=merchant,
                                   survey_item=survey_item)
        elif survey_type == 'rating':
            if merchant_id == "5dddd6d006e7eca17bd8e850":
                return render_template('wifi_portal/survey_rating_anvui.html',
                                       shop_select=merchant,
                                       survey_item=survey_item)
            return render_template('wifi_portal/survey_rating.html',
                                   shop_select=merchant,
                                   survey_item=survey_item)
    if str(type_page) == 'spin':
        spin = api.get_details_step_wifi_ads(merchant_id, camp_id, type_page,
                                             step)
        spin_id = spin.get('spin_id')
        url = '/game/' + spin_id
        return redirect(url)

    if str(type_page) == 'template':
        temp = api.get_details_step_wifi_ads(merchant_id, camp_id, type_page,
                                             step)
        temp_id = temp.get('temp_id')
        temp = api.get_temp_wifi_ads(merchant_id, temp_id)
        return render_template('nextify/preview_temp_ads.html', temp=temp)
    if type_page == '0':
        return render_template('new_hotspot/404.html')
    if type_page == 'connect_success':
        connect_success = api.get_details_step_wifi_ads(
            merchant_id, camp_id, type_page, step)
        return render_template(
            'wifi_portal/connect_success.html',
            connect_success=connect_success,
            shop=merchant_id,
        )
    card = api.get_details_step_wifi_ads(merchant_id, camp_id, type_page, step)
    user = {
        "age_range": None,
        "relationship_status": None,
        "home_town": None,
        "fb_id": None,
        "phone": "0946xx0912",
        "birthday": "12-09",
        "id": "Thomas",
        "name": "Thomas",
        "gender": "",
        "email": None,
        "year_birthday": None
    }
    title = card.get('title', '')
    if title or str(title) != 'None':
        title = title.strip()
        title = title.replace('{{ name }}', user.get('name', ''))
    if str(type_page) == 'image':
        title = card.get('title_image', '')
        content = card.get('content_image', '')
        if content or str(content) != 'None':
            content = content.strip()
            content = content.replace('{{ name }}', user.get('name', ''))
        return render_template(
            'wifi_portal/event_v2.html',
            user=user,
            card=card,
            content=content,
            title=title,
        )
    if str(type_page) == 'youtube':
        content = card.get('content_youtube', '')
        if content or str(content) != 'None':
            content = content.strip()
            content = content.replace('{{ name }}', user.get('name', ''))
        return render_template('wifi_portal/event_v2.html',
                               user=user,
                               card=card,
                               content=content,
                               title=title,
                               type_page='youtube')
    if str(type_page) == 'slides':
        slides = card.get('slides')
        return render_template(
            'wifi_portal/default.html',
            user=user,
            slides=slides,
        )


@app.route('/save_step_wifi_ads_camp/<merchant_id>/<camp_id>',
           methods=['POST'])
@login_required
def save_step_wifi_ads_camp(merchant_id, camp_id):
    data = request.form.to_dict()
    files = request.files
    type_page = data.get('type_page')
    camp_id = data.get('camp_id')
    current_step = '0'
    details = {}

    if str(type_page) == 'collect':
        current_step = data.get('current_step')
        collect_page = json.loads(data.get('collect_page'))
        phone_visible = collect_page.get('phone_visible')
        phone_visible = True if phone_visible else False
        phone_require = collect_page.get('phone_require')
        phone_require = True if phone_require else False

        name_visible = collect_page.get('name_visible')
        name_visible = True if name_visible else False
        name_require = collect_page.get('name_require')
        name_require = True if name_require else False

        birthday_visible = collect_page.get('birthday_visible')
        birthday_visible = True if birthday_visible else False
        birthday_require = collect_page.get('birthday_require')
        birthday_require = True if birthday_require else False

        gender_visible = collect_page.get('gender_visible')
        gender_visible = True if gender_visible else False
        gender_require = collect_page.get('gender_require')
        gender_require = True if gender_require else False

        email_visible = collect_page.get('email_visible')
        email_visible = True if email_visible else False
        email_require = collect_page.get('email_require')
        email_require = True if email_require else False

        year_birthday_visible = collect_page.get('year_birthday_visible')
        year_birthday_visible = True if year_birthday_visible else False
        year_birthday_require = collect_page.get('year_birthday_require')
        year_birthday_require = True if year_birthday_require else False

        company_visible = collect_page.get('company_visible')
        company_visible = True if company_visible else False
        company_require = collect_page.get('company_require')
        company_require = True if company_require else False

        company_role_visible = collect_page.get('company_role_visible')
        company_role_visible = True if company_role_visible else False
        company_role_require = collect_page.get('company_role_require')
        company_role_require = True if company_role_require else False

        vocation = collect_page.get('vocation_visible')
        vocation = True if vocation else False
        vocation_require = collect_page.get('vocation_require')
        vocation_require = True if vocation_require else False

        connect_with_facebook = collect_page.get('connect_with_facebook')
        connect_with_facebook = True if connect_with_facebook else False

        connect_with_zalo = collect_page.get('connect_with_zalo')
        connect_with_zalo = True if connect_with_zalo else False
        allow_access_friend_zalo = collect_page.get('allow_access_friend_zalo')
        allow_access_friend_zalo = True if allow_access_friend_zalo else False

        connect_with_messenger = collect_page.get('connect_with_messenger')
        connect_with_messenger = True if connect_with_messenger else False

        welcome_text = collect_page.get('welcome_text')
        welcome_button = collect_page.get('welcome_button')
        birthday_text = collect_page.get('birthday_text')
        collect_target = collect_page.get('collect_target')
        tag_input = collect_page.get('real_tags_filter')
        tags = []
        if tag_input and len(tag_input) > 0:
            tags_split = tag_input.split(',')
            if len(tags_split) > 0:
                for tag in tags_split:
                    tag = tag.strip()
                    if len(tag) > 0:
                        tags.append(ObjectId(tag))
        otp = collect_page.get('otp')
        otp_val = True if str(otp) == 'true' else False
        image_collect = files.get('img_collect')
        photo = None
        data_logo = None
        if image_collect and \
                image_collect.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            photo = storage_api.save_new_file(image_collect)
        else:
            detail_image = api.get_details_step_wifi_ads(
                merchant_id, camp_id, type_page, current_step)
            if detail_image:
                photo = detail_image.get('background')
        details = {
            'phone': phone_visible,
            'name': name_visible,
            'birthday': birthday_visible,
            'year_birthday': year_birthday_visible,
            'gender': gender_visible,
            'email': email_visible,
            'welcome_text': welcome_text,
            'welcome_button': welcome_button,
            'birthday_text': birthday_text,
            'phone_require': phone_require,
            'name_require': name_require,
            'birthday_require': birthday_require,
            'gender_require': gender_require,
            'email_require': email_require,
            'year_birthday_require': year_birthday_require,
            'otp': otp_val,
            'company': company_visible,
            'company_require': company_require,
            'company_role': company_role_visible,
            'company_role_require': company_role_require,
            'vocation': vocation,
            'vocation_require': vocation_require,
            'connect_with_facebook': connect_with_facebook,
            'connect_with_zalo': connect_with_zalo,
            'allow_access_friend_zalo': allow_access_friend_zalo,
            'connect_with_messenger': connect_with_messenger,
            'tag': tags,
            'background': photo,
            'collect_target': collect_target
        }
    if str(type_page) == 'image':
        current_step = data.get('current_step')
        title = data.get('title_image')
        content_image = data.get('content_image')
        image_target = data.get('image_target')
        photo = data.get('img_image')
        details['title_image'] = title
        details['content_image'] = content_image
        details['photo'] = photo
        details['image_target'] = image_target
    if str(type_page) == 'youtube':
        current_step = data.get('current_step')
        youtube_page = json.loads(data.get('youtube_page'))
        link_youtube = youtube_page.get('link_youtube')
        youtube_target = youtube_page.get('youtube_target')
        if link_youtube and len(link_youtube) > 0:
            split_link = link_youtube.split('=')
            id_link = split_link[1]
            content_youtube = '<iframe height="400" src="https://www.youtube.com/embed/' + id_link + \
                              '?autoplay=1&mute=1" frameborder="0" allow="autoplay" allowfullscreen></iframe>'
            details = {
                'link_youtube': link_youtube,
                'content_youtube': content_youtube,
                'youtube_target': youtube_target
            }
    if str(type_page) == "spin":
        current_step = data.get('current_step')
        spin_id = data.get('spin_id')
        if spin_id and len(spin_id) > 0:
            details_spin = {}
            item = api.item_mini_game_by_id(spin_id)
            info_game = item.get('info')
            name_game = info_game.get('name')
            details = {'spin_id': spin_id, 'name_spin': name_game}
    if str(type_page) == "survey":
        current_step = data.get('current_step')
        survey_id = data.get('survey_id')
        if survey_id and len(survey_id) > 0:
            survey_item = api.get_survey_item(survey_id)
            question = survey_item.get('question')
            details = {'survey_id': survey_id, 'question': question}
    if str(type_page) == "template":
        current_step = data.get('current_step')
        temp_id = data.get('temp_id')
        if temp_id and len(temp_id) > 0:
            temp_item = api.get_temp_wifi_ads(merchant_id, temp_id)
            name_temp = temp_item.get('name_temp')
            details = {'temp_id': temp_id, 'name_temp': name_temp}
    if str(type_page) == "slides":
        images_slide = []
        current_step = data.get('current_step')
        number_slide = int(data.get('number_slide'))
        slide_target = data.get('slide_target')
        init = data.get('init', '')
        images = data.get('images')
        images_slide = images.split(',')
        slides = []
        for photo in images_slide:
            if photo and len(photo) > 0:
                slides.append(photo)
        if len(slides) == 0:
            slides = api.get_all_slides_wifi_ads(merchant_id, camp_id)
        if slides and len(slides) > 0:
            details = {
                'number_slide': number_slide,
                'slides': slides,
                'slide_target': slide_target
            }
        if init == "True":
            api.update_init_default_wifi_ads(merchant_id, camp_id)
    if str(type_page) == 'connect_success':
        # connect success page
        details = {}
        current_step = '4'
        connect_page = json.loads(data.get('connect_success_page'))
        content_connect = connect_page.get('content_connect')
        connect_button = connect_page.get('connect_button')

        redirect_type = connect_page.get('redirect_type')
        auto_website = connect_page.get('auto_website')
        auto_popup_ios = connect_page.get('auto_popup_ios')
        auto_popup_android = connect_page.get('auto_popup_android')
        auto_facebook_page = connect_page.get('auto_facebook_page')
        auto_popup_zalo = connect_page.get('auto_popup_zalo')
        auto_popup_insta = connect_page.get('auto_popup_insta')
        auto_facebook_mess = connect_page.get('auto_facebook_mess')
        display_coupon = False
        display_coupon_check = connect_page.get('display_coupon')
        if display_coupon_check and str(display_coupon_check) == 'on':
            display_coupon = True
        display_coupon_txt = connect_page.get('display_coupon_txt').strip()

        hotspot_method = connect_page.get('hotspot_method', 'default')
        default_code = connect_page.get('default_code', '')
        default_code = default_code.strip()
        default_code = default_code.lower()
        image_connect = files.get('img_connect')
        photo = None
        data_logo = None
        if image_connect and \
                image_connect.filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            photo = storage_api.save_new_file(image_connect)
        else:
            detail_image = api.get_details_step_wifi_ads(
                merchant_id, camp_id, type_page, current_step)
            if detail_image:
                photo = detail_image.get('background_connect', '')
        details = {
            'content_connect': content_connect,
            'connect_button': connect_button,
            'redirect_type': redirect_type,
            'auto_website': auto_website,
            'auto_popup_ios': auto_popup_ios,
            'auto_popup_android': auto_popup_android,
            'auto_facebook_page': auto_facebook_page,
            'auto_popup_zalo': auto_popup_zalo,
            'auto_popup_insta': auto_popup_insta,
            'auto_facebook_mess': auto_facebook_mess,
            'display_coupon': display_coupon,
            'display_coupon_txt': display_coupon_txt,
            'hotspot_method': hotspot_method,
            'default_code': default_code,
            'background_connect': photo
        }
    api.save_step_wifi_ads(merchant_id, camp_id, current_step, type_page,
                           details)
    return json.dumps({'result': True})


@app.route('/save_wifi_ads/<merchant_id>/<camp_id>', methods=['POST'])
@login_required
def save_wifi_ads(merchant_id, camp_id):
    data = request.form.to_dict()
    files = request.files
    # type step
    step_1 = data.get('step_1')
    step_2 = data.get('step_2')
    step_3 = data.get('step_3')
    step_4 = 'connect success'
    # sinh nhat va kich hoat
    is_birthday = data.get('birthday')
    is_birthday = True if str(is_birthday) == "true" else False
    active = data.get('active')
    active = True if str(active) == "true" else False
    name_camp = data.get('name_camp')
    # group customer
    group_customer = json.loads(data.get('group_customer'))
    tags_group = group_customer.get('camp_tags_selects')
    tags_group_customer = []
    if tags_group and type(tags_group) != list:
        tags_group_customer.append(ObjectId(tags_group))
    else:
        if tags_group and len(tags_group) > 0:
            for tag in tags_group:
                tag = tag.strip()
                if len(tag) > 0:
                    tags_group_customer.append(ObjectId(tag))
    device = group_customer.get('device')
    system = group_customer.get('system')
    device_group = []
    if device and type(device) != list:
        device_group.append(str(device))
    else:
        if device and len(device) > 0:
            for de in device:
                de = de.strip()
                if len(de) > 0:
                    device_group.append(str(de))
    sys_group = []
    if system and type(system) != list:
        sys_group.append(str(system))
    else:
        if system and len(system) > 0:
            for sys in system:
                sys = sys.strip()
                if len(sys) > 0:
                    sys_group.append(str(sys))
    min_visit = group_customer.get('min_visit')
    max_visit = group_customer.get('max_visit')
    if not min_visit and max_visit:
        min_visit = 1
    if not max_visit and min_visit:
        max_visit = 1000
    if min_visit:
        min_visit = int(min_visit)
    if max_visit:
        max_visit = int(max_visit)

    min_age = group_customer.get('min_age')
    max_age = group_customer.get('max_age')
    if not min_age and min_age:
        min_visit = 1
    if not max_age and max_age:
        max_age = 100
    if min_age:
        min_age = int(min_age)
    if max_age:
        max_age = int(max_age)
    gender = group_customer.get('gender')
    ads_seen_fr = group_customer.get('ads_seen')
    ads_seen = []
    if ads_seen_fr and type(ads_seen_fr) != list:
        ads_seen.append(ObjectId(ads_seen_fr))
    else:
        if ads_seen_fr and len(ads_seen_fr) > 0:
            for ads in ads_seen_fr:
                ads = ads.strip()
                if len(ads) > 0:
                    ads_seen.append(ObjectId(ads))

    date_type_select = group_customer.get('date_type_select')
    weekday_sun = data.get('weekday_sun_')
    weekday_sun = True if weekday_sun == "true" else False
    weekday_mon = data.get('weekday_mon_')
    weekday_mon = True if weekday_mon == "true" else False
    weekday_tue = data.get('weekday_tue_')
    weekday_tue = True if weekday_tue == "true" else False
    weekday_wed = data.get('weekday_wed_')
    weekday_wed = True if weekday_wed == "true" else False
    weekday_thu = data.get('weekday_thu_')
    weekday_thu = True if weekday_thu == "true" else False
    weekday_fri = data.get('weekday_fri_')
    weekday_fri = True if weekday_fri == "true" else False
    weekday_sat = data.get('weekday_sat_')
    weekday_sat = True if weekday_sat == "true" else False
    min_day = group_customer.get('min_day')
    max_day = group_customer.get('max_day')
    event_start_picker = group_customer.get('event_start_picker')
    event_end_picker = group_customer.get('event_end_picker')
    timestamp_start_event = 0
    if event_start_picker:
        date_start_event = datetime.strptime(event_start_picker,
                                             "%d-%m-%Y").timetuple()
        timestamp_start_event = time.mktime(date_start_event)
    timestamp_end_event = 0
    if event_end_picker:
        date_end_event = datetime.strptime(event_end_picker,
                                           "%d-%m-%Y").timetuple()
        timestamp_end_event = time.mktime(date_end_event)
    min_hour = group_customer.get('min_hour')
    max_hour = group_customer.get('max_hour')
    convert_min_hour = 0
    split_min_hour = min_hour.split(':')
    convert_min_hour = int(split_min_hour[0])
    if split_min_hour[1] == '30':
        convert_min_hour = convert_min_hour + 0.5
    convert_max_hour = 0
    split_max_hour = max_hour.split(':')
    convert_max_hour = int(split_max_hour[0])
    if split_max_hour[1] == '30':
        convert_max_hour = convert_max_hour + 0.5
    type_campaign = group_customer.get('type_campaign')
    target_campaign = int(group_customer.get('target_campaign', 0))
    details_group_customer = {
        'tags_group_customer': tags_group_customer,
        'min_visit': min_visit,
        'max_visit': max_visit,
        'date_type_select': date_type_select,
        'weekday_sun': weekday_sun,
        'weekday_mon': weekday_mon,
        'weekday_tue': weekday_tue,
        'weekday_wed': weekday_wed,
        'weekday_thu': weekday_thu,
        'weekday_fri': weekday_fri,
        'weekday_sat': weekday_sat,
        'min_day': int(min_day),
        'max_day': int(max_day),
        'event_start_picker': event_start_picker,
        'event_end_picker': event_end_picker,
        'timestamp_start_event': timestamp_start_event,
        'timestamp_end_event': timestamp_end_event,
        'min_hour': min_hour,
        'max_hour': max_hour,
        'convert_min_hour': convert_min_hour,
        'convert_max_hour': convert_max_hour,
        'device': device_group,
        'system': sys_group,
        'min_age': min_age,
        'max_age': max_age,
        'gender': gender,
        'ads_seen': ads_seen
    }
    type_camp = data.get('type_camp')
    # phan phoi dia diem
    group_distribution = json.loads(data.get('group_distribution'))
    distribution = group_distribution.get('distribution')
    distribution_tags_choose = group_distribution.get(
        'distribution_tags_choose')
    distribution_loc_choose = group_distribution.get('distribution_loc_choose')
    shops_distribution = []
    list_distribution_tags = []
    if distribution == 'distribution_tags':
        if distribution_tags_choose and type(distribution_tags_choose) != list:
            list_distribution_tags.append(ObjectId(distribution_tags_choose))
            shop_tag = api.get_shop_by_tag(distribution_tags_choose)
            for shop in shop_tag:
                shop_id = shop.get('_id')
                shops_distribution.append(shop_id)
        else:
            if distribution_tags_choose and len(distribution_tags_choose) > 0:
                for tag in distribution_tags_choose:
                    tag = tag.strip()
                    if len(tag) > 0:
                        list_distribution_tags.append(ObjectId(tag))
                        shop_tag = api.get_shop_by_tag(tag)
                        for shop in shop_tag:
                            shop_id = shop.get('_id')
                            shops_distribution.append(shop_id)

    elif distribution == 'distribution_loc':
        if distribution_loc_choose and type(distribution_loc_choose) != list:
            shops_distribution.append(ObjectId(distribution_loc_choose))
        else:
            if distribution_loc_choose and len(distribution_loc_choose) > 0:
                for loc in distribution_loc_choose:
                    loc = loc.strip()
                    if len(loc) > 0:
                        shops_distribution.append(ObjectId(loc))

    else:
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        for shop in shop_in_mer:
            shops_distribution.append(ObjectId(shop.get('_id')))
    details_group_distribution = {
        'distribution': distribution,
        'distribution_tags': list_distribution_tags,
        'distribution_loc': distribution_loc_choose
    }
    # setting camp
    setting_campaign = json.loads(data.get('setting_campaign'))
    type_campaign = setting_campaign.get('type_campaign')
    target_campaign = setting_campaign.get('target_campaign')
    if target_campaign and len(target_campaign) > 0:
        target_campaign = int(target_campaign)
    tags_campaign_fr = setting_campaign.get('tags_camp')
    tags_camp = []
    if tags_campaign_fr and type(tags_campaign_fr) != list:
        tags_camp.append(ObjectId(tags_campaign_fr))
    else:
        if tags_campaign_fr and len(tags_campaign_fr) > 0:
            for tag in tags_campaign_fr:
                tag = tag.strip()
                if len(tag) > 0:
                    tags_camp.append(ObjectId(tag))
    api.save_wifi_ads(merchant_id, camp_id, name_camp, type_camp, active,
                      is_birthday, step_1, step_2, step_3, step_4,
                      target_campaign, type_campaign, details_group_customer,
                      details_group_distribution, shops_distribution,
                      tags_camp)
    return json.dumps({'result': True})


@app.route('/preview_wifi_ads/<merchant_id>/<campaign_id>', methods=['GET'])
@login_required
def preview_wifi_ads(merchant_id, campaign_id):
    merchant = api.get_merchant(merchant_id)
    campaign_details = api.get_new_wifi_ads_by_id(campaign_id)
    if campaign_details:
        return render_template('new_hotspot/preview_wifi_ads.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               camp=campaign_details)
    else:
        abort(404)


@app.route('/setting_merchant_wifi_ads/<active>', methods=['GET', 'POST'])
@login_required
def setting_merchant_wifi_ads(active):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if request.method == "POST":
        default_wifi = request.form.get('default_wifi')
        share_rate = request.form.get('share_rate')
        api.wifi_ads_merchant(merchant_id, default_wifi, share_rate)
        return json.dumps({'result': True})
    else:
        status_ads = "False"
        if active in ["true", "True"]:
            status_ads = "True"
        api.update_merchants(merchant_id=merchant_id, status_ads=status_ads)
        return json.dumps({'result': True})


@app.route('/grandstream_report/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def grandstream_report(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    id_net = shop_select.get('id_net')
    if request.method == 'GET':

        return render_template('nextify/grand_embed.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               id_net=id_net,
                               shop_in_mer=shops)


@app.route('/device_grandstream', methods=['GET', 'POST'])
@login_required
def device_grandstream():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    if request.method == 'GET':

        return render_template('nextify/grand_dashboard.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shops)


@app.route('/grandstream_schedule/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def grandstream_schedule(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    id_net = shop_select.get('id_net')
    if request.method == 'GET':

        return render_template('nextify/grand_schedule.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               id_net=id_net,
                               shop_in_mer=shops)


@app.route('/grandstream_brandwidth/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def grandstream_brandwidth(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    id_net = shop_select.get('id_net')
    if request.method == 'GET':

        return render_template('nextify/grand_brandwidth.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               id_net=id_net,
                               shop_in_mer=shops)


@app.route('/grandstream_wifi/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def grandstream_wifi(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    id_net = shop_select.get('id_net')
    if request.method == 'GET':

        return render_template('nextify/grand_wifi.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               id_net=id_net,
                               shop_in_mer=shops)


@app.route('/grandstream_block/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def grandstream_block(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    id_net = shop_select.get('id_net')
    if request.method == 'GET':

        return render_template('nextify/grand_block.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               id_net=id_net,
                               shop_in_mer=shops)


@app.route('/grandstream_ap/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def grandstream_ap(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    id_net = shop_select.get('id_net')
    if request.method == 'GET':

        return render_template('nextify/grand_ap.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               id_net=id_net,
                               shop_in_mer=shops)


@app.route('/grandstream_clients/<shop_id_select>', methods=['GET', 'POST'])
@login_required
def grandstream_clients(shop_id_select):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]

    shop_select = api.get_shop_info(shop_id=shop_id_select)
    id_net = shop_select.get('id_net')
    if request.method == 'GET':

        return render_template('nextify/grand_clients.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_select=shop_select,
                               shop_id_select=shop_id_select,
                               id_net=id_net,
                               shop_in_mer=shops)


@app.route('/file_json', methods=['GET', 'POST'])
def file_json():
    data = '["vcard",[["version", {}, "text", "4.0"],["fn", {}, "text", "James Bond"], \
            ["n", {}, "text", ["Bond", "James", "", "", "Mr."]],\
            ["adr", {"type":"work"}, "text",\
                ["", "", "3100 Massachusetts Avenue NW", "Washington", "DC",\
                "20008", "USA"]\
            ],\
            ["email", {}, "text", "007@mi6-hq.com"],\
            ["tel", { "type": ["voice", "text", "cell"], "pref": "1" }, "uri",\
                "tel:+1-202-555-1000"],\
            ["tel", { "type": ["fax"] }, "uri", "tel:+1-202-555-1001"],\
            ["bday", {}, "date", "19241116"]\
            ["logo", {}, "uri",\
            "https://upload.wikimedia.org/wikipedia/en/c/c5/Fleming007impression.jpg"]\
            ]\
            ]'

    return json.dumps(data)


@app.route('/templates_html', methods=['GET', 'POST'])
@login_required
def templates_html():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)

    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == 'GET':
        temps = api.get_temps_ads_by_merchant(merchant_id)
        return render_template('nextify/templates_html.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               temps=temps,
                               shop_in_mer=shops)


@app.route('/templates_html/<temp_id>', methods=['GET', 'POST'])
@login_required
def templates_html_edit(temp_id):
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == 'GET':
        temp = {}
        if temp_id != "add":
            temp = api.get_temp_wifi_ads(merchant_id, temp_id)
        return render_template('nextify/templates_html_edit.html',
                               merchant=merchant,
                               merchant_id=merchant_id,
                               shop_in_mer=shops,
                               temp=temp)
    else:
        name_temp = request.form.get('name_temp')
        email_content = request.form.get('email_content')
        design = request.form.get('design')
        if temp_id != "all":
            api.update_templates_wifi_ads(merchant_id=merchant_id,
                                          name_temp=name_temp,
                                          email_content=email_content,
                                          design=design,
                                          temp_id=temp_id)
        else:
            api.update_templates_wifi_ads(merchant_id=merchant_id,
                                          name_temp=name_temp,
                                          email_content=email_content,
                                          design=design)
        return json.dumps({'result': True})


@app.route('/preview_template/<merchant_id>/<temp_id>',
           methods=['GET', 'POST'])
@login_required
def preview_template(merchant_id, temp_id):
    temp = api.get_temp_wifi_ads(merchant_id, temp_id)
    return render_template('nextify/preview_temp_ads.html', temp=temp)


@app.route('/wifi_ads/reports', methods=['GET', 'POST'])
@login_required
def wifi_ads_overview():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        total_hotspot = api.total_wifi_ads(merchant_id)
        if total_hotspot == 0:
            api.init_wifi_ads(merchant_id)

        campaigns = api.get_wifi_ads_camps(merchant_id, page,
                                           settings.ITEMS_PER_PAGE)
        total_hotspot = api.total_wifi_ads(merchant_id)
        pagination = Pagination(page=page,
                                total=total_hotspot,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        type_camp_chart = api.get_type_camp_chart(merchant_id)
        result_chart = api.get_result_camp_chart(merchant_id)
        events = []
        for camp in campaigns:
            start = ''
            end = ''
            name = camp.get("name")
            group_customer = camp.get('group_customer')
            start_time = group_customer.get('timestamp_start_event')
            end_time = group_customer.get('timestamp_end_event')
            if start_time and start_time > 0:
                start = datetime.fromtimestamp(
                    int(start_time)).strftime('%Y-%m-%d')
                if end_time and end_time > 0:
                    end = datetime.fromtimestamp(
                        int(end_time)).strftime('%Y-%m-%d')
                detail = {'title': name, 'start': start, 'end': end}
                events.append(detail)
        pagination = Pagination(page=page,
                                total=total_hotspot,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        return render_template('nextify/wifi_ads_overview.html',
                               merchant=merchant,
                               shop_in_mer=shops,
                               campaigns=campaigns,
                               total=total_hotspot,
                               type_camp_chart=json.dumps(type_camp_chart),
                               result_chart=json.dumps(result_chart),
                               events=json.dumps(events),
                               pagination=pagination,
                               tags=tags)


@app.route('/wifi_ads/campaign/report', methods=['GET', 'POST'])
@login_required
def wifi_ads_camp_report():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        total_hotspot = api.total_wifi_ads(merchant_id)
        if total_hotspot == 0:
            api.init_wifi_ads(merchant_id)

        campaigns = api.get_wifi_ads_camps(merchant_id, page,
                                           settings.ITEMS_PER_PAGE)
        total_hotspot = api.total_wifi_ads(merchant_id)
        pagination = Pagination(page=page,
                                total=total_hotspot,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        tags = [
            tag for tag in api.list_tags(merchant_id)
            if tag.get('name') and len(str(tag['name'])) > 0
        ]
        type_camp_chart = api.get_type_camp_chart(merchant_id)
        result_chart = api.get_result_camp_chart(merchant_id)
        events = []
        for camp in campaigns:
            start = ''
            end = ''
            name = camp.get("name")
            group_customer = camp.get('group_customer')
            start_time = group_customer.get('timestamp_start_event')
            end_time = group_customer.get('timestamp_end_event')
            if start_time and start_time > 0:
                start = datetime.fromtimestamp(
                    int(start_time)).strftime('%Y-%m-%d')
                if end_time and end_time > 0:
                    end = datetime.fromtimestamp(
                        int(end_time)).strftime('%Y-%m-%d')
                detail = {'title': name, 'start': start, 'end': end}
                events.append(detail)
        pagination = Pagination(page=page,
                                total=total_hotspot,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        return render_template('nextify/wifi_ads_camp_report.html',
                               merchant=merchant,
                               shop_in_mer=shops,
                               campaigns=campaigns,
                               total=total_hotspot,
                               type_camp_chart=json.dumps(type_camp_chart),
                               result_chart=json.dumps(result_chart),
                               events=json.dumps(events),
                               pagination=pagination,
                               tags=tags)


@app.route('/wifi_ads/report_settings', methods=['GET', 'POST'])
@login_required
def wifi_ads_report_settings():
    shop = g.shop
    user_login = g.user
    shop_id = shop['_id']
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shops = []
    if g.role == '3':
        shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            shops.append(shop_mer)
    else:
        locations = g.locations
        if len(locations) > 0:
            shops = [api.get_shop_info(shop_id=loc) for loc in locations]
    if request.method == "GET":
        return render_template('nextify/wifi_ads_report_setting.html',
                               merchant=merchant,
                               shop_in_mer=shops)


@app.route('/apps/abot', methods=['GET', 'POST'])
@login_required
def apps_setting_abot():
    shop = g.shop
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    shop_id = g.shop_id
    merchant = api.get_merchant(merchant_id)
    shop_in_mer = api.get_shop_by_merchant(str(merchant_id))
    if request.method == 'GET':
        try:
            app = api.get_app_synchronized(name_app='abot',
                                           merchant_id=merchant_id)
            status = app.get('status')
            user = app.get('setting').get('user')
            password = app.get('setting').get('password')
            sub_domain = app.get('setting').get('sub_domain')
        except:
            status = None
            user = None
            password = None
            sub_domain = None
        return render_template('nextify/app_setting_abot.html',
                               shop_in_mer=shop_in_mer,
                               merchant=merchant,
                               user_login=user_login,
                               status=status,
                               user=user,
                               password=password,
                               sub_domain=sub_domain)
    else:
        user = request.form.get('user')
        password = request.form.get('password')
        sub_domain = request.form.get('sub_domain')
        status = request.form.get('status')
        if not status:
            status = "False"
        else:
            status = "True"
        check_app = api.get_app_synchronized(name_app='abot',
                                             merchant_id=merchant_id)
        if not check_app:
            api.create_app_synchronized(user=user,
                                        merchant_id=merchant_id,
                                        password=password,
                                        sub_domain=sub_domain,
                                        status=status,
                                        type_app='crm',
                                        name_app='abot')
        if check_app:
            api.update_app_synchronized(user=user,
                                        merchant_id=merchant_id,
                                        password=password,
                                        sub_domain=sub_domain,
                                        status=status,
                                        type_app='crm',
                                        name_app='abot')
        if status == "True":
            try:
                producer_data = {
                    "merchant_id": str(merchant_id),
                    "task_name": "sync_abot",
                    "params": {
                        "merchant_id": str(merchant_id)
                    }
                }

                producer_data = json.dumps(producer_data).encode('utf-8')
                producer.send(settings.cms_consumer, producer_data)
                producer.flush()

            except:
                pass
        return json.dumps({'result': 'OK'})


@app.route('/wifi_partners', methods=['GET', 'POST'])
@login_required
def wifi_partners():
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    shop_select_name = merchant.get('name')

    if request.method == 'POST':
        name = request.form.get('name')
        if not name or len(name) == 0:
            return json.dumps({
                'result': False,
                'error': 'Tên đối tác không được để trống'
            })
        address = request.form.get('address')
        phone = request.form.get('phone')
        if not phone or len(phone) == 0:
            return json.dumps({
                'result': False,
                'error': 'Số điện thoại không được để trống'
            })

        number_tax = request.form.get('number_tax')
        status = request.form.get('status')
        status = True if status and str(status) != 'false' else False
        person_contact = request.form.get('person_contact')
        contact_phone = request.form.get('contact_phone')
        contact_department = request.form.get('contact_department')
        is_partner = api.find_item_wf_partners(merchant_id, phone, 'phone')
        if is_partner:
            return json.dumps({
                'result': False,
                'error': 'Số điện thoại đã tồn tại'
            })

        api.create_wifi_partner(merchant_id, name, address, phone, number_tax,
                                status, person_contact, contact_phone,
                                contact_department)
        return json.dumps({'result': True})
    else:
        page = int(request.args.get('page', 1))
        wifi_partners = api.list_item_wf(merchant_id, page,
                                         settings.ITEMS_PER_PAGE)
        total = api.total_wifi_partners(merchant_id)
        pagination = Pagination(page=page,
                                total=total,
                                per_page=settings.ITEMS_PER_PAGE,
                                css_framework='bootstrap3')
        return render_template('nextify/wifi_partners.html',
                               shop=shop,
                               user_login=user_login,
                               merchant_id=merchant_id,
                               merchant=merchant,
                               wifi_partners=wifi_partners,
                               pagination=pagination,
                               total=total,
                               shop_select_name=shop_select_name)


@app.route('/<merchant_id>/wifi_partners/<wifi_partner_id>/edit',
           methods=['GET', 'POST'])
@login_required
def edit_wifi_partner_info(merchant_id, wifi_partner_id):
    wifi_partner = api.item_wifi_partner(merchant_id, wifi_partner_id)
    return render_template('nextify/update_wifi_partner_info.html',
                           merchant_id=merchant_id,
                           wifi_partner=wifi_partner,
                           wifi_partner_id=wifi_partner_id)


@app.route('/<merchant_id>/wifi_partners/<wifi_partner_id>/location',
           methods=['GET', 'POST'])
@login_required
def location_wifi_partner_info(merchant_id, wifi_partner_id):
    wifi_partner = api.item_wifi_partner(merchant_id, wifi_partner_id)
    return render_template('nextify/location_wifi_partner_info.html',
                           merchant_id=merchant_id,
                           wifi_partner=wifi_partner,
                           wifi_partner_id=wifi_partner_id)


@app.route('/<merchant_id>/wifi_partners/<wifi_partner_id>/reports',
           methods=['GET', 'POST'])
@login_required
def report_wifi_partner_info(merchant_id, wifi_partner_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    wifi_partner = api.item_wifi_partner(merchant_id, wifi_partner_id)
    type_camp_chart = api.get_type_camp_chart(merchant_id)
    result_chart = api.get_result_camp_chart(merchant_id)
    return render_template('nextify/report_wifi_partner_info.html',
                           merchant_id=merchant_id,
                           wifi_partner=wifi_partner,
                           wifi_partner_id=wifi_partner_id,
                           type_camp_chart=json.dumps(type_camp_chart),
                           result_chart=json.dumps(result_chart),
                           shop=shop,
                           merchant=merchant,
                           shop_id=shop_id)


@app.route('/<merchant_id>/wifi_partners/<wifi_partner_id>/bills',
           methods=['GET', 'POST'])
@login_required
def bill_wifi_partner_info(merchant_id, wifi_partner_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    wifi_partner = api.item_wifi_partner(merchant_id, wifi_partner_id)
    type_camp_chart = api.get_type_camp_chart(merchant_id)
    result_chart = api.get_result_camp_chart(merchant_id)
    return render_template('nextify/billing_wifi_partner_info.html',
                           merchant_id=merchant_id,
                           wifi_partner=wifi_partner,
                           wifi_partner_id=wifi_partner_id,
                           type_camp_chart=json.dumps(type_camp_chart),
                           result_chart=json.dumps(result_chart),
                           shop=shop,
                           merchant=merchant,
                           shop_id=shop_id)


@app.route('/wifi_partners/<wifi_partner_id>/update', methods=['POST'])
@login_required
def wifi_partners_update(wifi_partner_id):
    shop = g.shop
    shop_id = g.shop_id
    user_login = g.user
    merchant_id = shop.get('merchant_id')
    merchant = api.get_merchant(merchant_id)
    name = request.form.get('name')
    if not name or len(name) == 0:
        return json.dumps({
            'result': False,
            'error': 'Tên đối tác không được để trống'
        })
    address = request.form.get('address')
    phone = request.form.get('phone')
    if not phone or len(phone) == 0:
        return json.dumps({
            'result': False,
            'error': 'Số điện thoại không được để trống'
        })
    exist_phone_number = api.check_duplicate_wifi_partners(
        merchant_id, wifi_partner_id, phone, "phone")
    if exist_phone_number:
        return json.dumps({
            'result':
            False,
            'error':
            'Số điện thoại này đã tồn tại.<br/>Vui lòng dùng số khác'
        })
    number_tax = request.form.get('number_tax')
    status = request.form.get('status')
    status = True if status and str(status) != 'None' else False
    person_contact = request.form.get('person_contact')
    contact_phone = request.form.get('contact_phone')
    contact_department = request.form.get('contact_department')
    check_update = api.update_wifi_partner(
        merchant_id,
        wifi_partner_id,
        name=name,
        address=address,
        phone=phone,
        number_tax=number_tax,
        status=status,
        person_contact=person_contact,
        contact_phone=contact_phone,
        contact_department=contact_department)
    return json.dumps({'result': True})


@app.route('/wifi_partners/<wifi_partner_id>/remove', methods=['GET'])
@login_required
def wifi_partners_remove(wifi_partner_id):
    check_remove = api.remove_wifi_partners(wifi_partner_id)
    if check_remove:
        return json.dumps({'result': True})
    return json.dumps({'result': False})


@app.route('/work', methods=['GET', 'POST'])
def test_work():
    if request.method == 'POST':
        test = request.form.get('id')
        print(test)
        return json.dumps({"status": "success", "message": "It's working!"})
    else:
        return json.dumps({"status": "success", "message": "It's working!"})


# try:
#     from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
# except ImportError:
#     from cherrypy.wsgiserver import CherryPyWSGIServer as WSGIServer, WSGIPathInfoDispatcher as PathInfoDispatcher

# d = PathInfoDispatcher({'/': app})
# server = WSGIServer(('0.0.0.0', 8096), d)
from waitress import serve
# serve(app, host='127.0.0.1', port=8096)
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8096, debug=True)
#     try:
#        server.start()
#     except KeyboardInterrupt:
#        server.stop()

# if __name__ == "__main__":
# handler = LoggingHandler(client=apm.client)
# handler.setLevel(logging.WARN)
#   app.logger.addHandler(handler)
# app.run(host='127.0.0.1', port=8096, debug=True)
# app.run()
# server.listen(("0.0.0.0", 8096))
# server.run(app)
