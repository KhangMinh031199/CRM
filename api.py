#! coding: utf-8
from user_agents import parse
import time
import urllib.request
import urllib.parse
import urllib.error
import redis
import random
import socket
import requests
import unidecode
import simplejson
import dateparser
import user_agents
import arrow
import collections
import time
import hashlib
import hmac
from os import urandom
from base64 import b64encode, b64decode

from zeep import Client
from zeep.transports import Transport
import mimetypes
import re
import pandas
import pytz
from uuid import uuid4
from hashlib import md5
from datetime import date, datetime
from slugify import slugify
from pymongo import MongoClient, DESCENDING, errors
from bson.objectid import ObjectId
from collections import OrderedDict, defaultdict
from calendar import monthrange
from pbkdf2 import pbkdf2_bin
from requests import Session
from datetime import timedelta
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from hashids import Hashids
import dateutil.parser
import storage_api
import email_api
from bs4 import BeautifulSoup
import json
import wifimedia_radius
import avinit
import bitly
import handle_customers
from mongo_connect import *
from mailchimp3 import MailChimp
import send_activity
from flask import request
import save_customers
import search_engine

CARBON = (settings.CARBON_HOST, settings.CARBON_PORT)

REDIS = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0)

# Each process creates its own instance of MongoClient.


MONGODB = mongodb_create()
DATABASE = MONGODB[settings.MONGODB_NAME]
hotspot_campaign = DATABASE['hotspot_campaign']
CACHE = DATABASE.cache
MERCHANTS = DATABASE.merchants


def ensure_index(collection_name, field_name):
    try:
        return DATABASE[collection_name].create_index(
            [(field_name, DESCENDING)], background=True)
    except errors.OperationFailure:
        return False


ensure_index('user', 'phone')
ensure_index('user', 'client_mac')
ensure_index('shop', 'phone_numbers')
ensure_index('shop', 'gateway_mac')
ensure_index('card', 'shop_id')
ensure_index('card', 'timestamp')
ensure_index('coupon', 'shop_id')
ensure_index('coupon', 'user_id')
ensure_index('sms_log', 'shop_id')
ensure_index('visit_log', 'user_id')
ensure_index('visit_log', 'shop_id')
ensure_index('visit_log', 'timestamp')
ensure_index('access_log', 'gateway_mac')
ensure_index('access_log', 'client_mac')
ensure_index('access_log', 'user_agent')
ensure_index('access_log', 'timestamp')
ensure_index('access_log', 'os')
ensure_index('user', '_id')
ensure_index('loyalty_point', 'user_id')
ensure_index('credit_amount', 'user_id')
ensure_index('user', 'birthday')
ensure_index('user', 'gender')
ensure_index('customers', 'user_id')
ensure_index('customers', 'last_visit')
ensure_index('customers', 'total_visit')
ensure_index('customers', 'merchant_id')
ensure_index('customers', 'user')
ensure_index('customers_location', 'user_id')
ensure_index('customers_location', 'last_visit')
ensure_index('customers_location', 'total_visit')
ensure_index('customers_location', 'shop_id')
ensure_index('customers_location', 'user')
ensure_index('customers', 'text')
ensure_index('customers', 'user.phone')
ensure_index('customers', 'user.email')
ensure_index('customers', 'user.name')
ensure_index('survey_result', 'shop_id')
ensure_index('survey_result', 'survey_id')
ensure_index('survey_result', 'survey_type')
ensure_index('survey_result', 'answers')


def get_age(born):
    if not born:
        return -1
    born = dateparser.parse(born)
    today = date.today()
    return today.year - born.year - \
        ((today.month, today.day) < (born.month, born.day))


def remove_accents_anvui(ques):
    s = ques[0]
    if not isinstance(s, str):
        s = s.decode('utf-8')
    return unidecode.unidecode(s)


def remove_accents(s):
    if not isinstance(s, str):
        s = s.decode('utf-8')
    return unidecode.unidecode(s)


def normalize(mac_addr):
    # Determine which delimiter style out input is using
    if '.' in mac_addr:
        delimiter = '.'
    elif ':' in mac_addr:
        delimiter = ':'
    elif '-' in mac_addr:
        delimiter = '-'
    else:
        delimiter = None

    # Eliminate the delimiter
    m = mac_addr.replace(delimiter, '') if delimiter else mac_addr

    m = m.strip().lower()
    return ':'.join(['%s%s' % (m[i], m[i + 1]) for i in range(0, 12, 2)])


def is_mac_addr(mac_addr):
    mac_addr = normalize(mac_addr)
    if not mac_addr:
        return False

    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_addr):
        return True
    else:
        return False


def is_captive_portal_popup(referer):
    """
    http://serverfault.com/questions/679393/captive-portal-popups-the-definitive-guide

    """
    if not referer:
        return False

    if not referer.startswith('http'):
        return False

    referer = str(referer)

    mimetype = mimetypes.guess_type(referer)
    if mimetype[0] and (mimetype[0].startswith('image/') or
                        mimetype[0].startswith('video/') or
                        mimetype[0].startswith('audio/') or
                        mimetype[0].startswith('application/')):
        return False

    # Trường hợp iOS hơi chuối, thỉnh thoảng nó check bằng http://www.apple.com/
    if referer == 'http://www.apple.com/':
        return True

    # Apple devices
    if referer.startswith('http://captive.apple.com/') or \
            referer.startswith('http://attwifi.apple.com/') or \
            referer.startswith('http://www.itools.info/') or \
            referer.startswith('http://www.ibook.info/') or \
            referer.startswith('http://www.airport.us/') or \
            referer.startswith('http://www.thinkdifferent.us/') or \
            referer.startswith('http://www.appleiphonecell.com/') or \
            '.apple.com.edgekey.net' in referer or \
            '.akamaiedge.net' in referer or \
            '.akamaitechnologies.com' in referer:
        return True

    # Android
    if referer.endswith('/generate_204'):
        return True

    # Windows Phone
    if '.msftconnecttest.com/' in referer or \
            '.msftncsi.com/' in referer or \
            'http://go.microsoft.com/fwlink/?LinkID=219472&clcid=0x409' in referer:
        return True

    # HTC One_M8
    if 'http://hla2.safemovedm.com/webping-s.html' in referer:
        return True

    # UCBrowser
    if 'http://down4.ucweb.com/wifi/vi/wifi.html' in referer:
        return True

    # Firefox
    if 'http://detectportal.firefox.com/success.txt' in referer:
        return True

    # BlackBerry
    if 'http://www.blackberry.com/select/wifiloginsuccess/' in referer:
        return True

    # Nokia
    if 'http://connectivity-test.ext.nokia.com/' in referer:
        return True

    info = CACHE.find_one({'referer': referer})
    if info:
        return info.get('is_captive_portal_popup')

    try:
        r = requests.get(referer, timeout=3, allow_redirects=False)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

    # Android/Chrome
    if r.status_code == 204:
        CACHE.update(
            {
                'referer': referer
            }, {'$set': {
                'is_captive_portal_popup': True
            }},
            upsert=True)
        return True

    # Windows
    elif r.content == 'Microsoft NCSI':
        CACHE.update(
            {
                'referer': referer
            }, {'$set': {
                'is_captive_portal_popup': True
            }},
            upsert=True)
        return True

    # Debian
    elif r.content == 'NetworkManager is online':
        CACHE.update(
            {
                'referer': referer
            }, {'$set': {
                'is_captive_portal_popup': True
            }},
            upsert=True)
        return True

    # Windows 8.1
    # http://go.microsoft.com/fwlink/?LinkID=219472&clcid=0x409
    elif '?ocid=wispr' in r.headers.get('Location', ''):
        CACHE.update(
            {
                'referer': referer
            }, {'$set': {
                'is_captive_portal_popup': True
            }},
            upsert=True)
        return True

    # MacOS/iOS
    elif '<HTML><HEAD><TITLE>Success</TITLE></HEAD>' \
         '<BODY>Success</BODY></HTML>' in r.content:
        CACHE.update(
            {
                'referer': referer
            }, {'$set': {
                'is_captive_portal_popup': True
            }},
            upsert=True)
        return True

    # Kindle
    elif '<title>Kindle Reachability Probe Page</title>' in r.content and \
            '81ce4465-7167-4dcb-835b-dcc9e44c112a' in r.content:
        CACHE.update(
            {
                'referer': referer
            }, {'$set': {
                'is_captive_portal_popup': True
            }},
            upsert=True)
        return True

    else:
        CACHE.update(
            {
                'referer': referer
            }, {'$set': {
                'is_captive_portal_popup': True
            }},
            upsert=True)
        return False


def get_shop_is_sms_announ():
    shop_ids = []
    for shop in DATABASE.shop.find({}):
        sms = shop.get('sms', {})
        if sms.get('manual_announcement'):
            manual_announ = sms.get("manual_announcement")
            message_announ = manual_announ.get("message", '').strip()
            if len(message_announ) > 0:
                shop_ids.append(shop['name'])
    return shop_ids


def update_last_send_sms(shop_id, type_mess):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()
    last_send = DATABASE.last_sms.find({
        'shop_id': shop_id,
        'type_mess': type_mess
    })
    if not last_send:
        DATABASE.last_sms.insert({
            'shop_id': shop_id,
            'type_mess': type_mess,
            'when': when
        })
    else:
        DATABASE.last_sms.update(
            {
                'shop_id': shop_id,
                'type_mess': type_mess
            }, {'$set': {
                'when': when
            }},
            upsert=True)


def get_ssid_cloud(gateway_mac):
    record = DATABASE.devices.find_one({'gateway_mac': gateway_mac})
    return record.get('ssid_cloud') if record else None


def get_last_send_sms(shop_id, type_mess):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.last_sms.find_one({
        'shop_id': shop_id,
        'type_mess': type_mess
    })


def get_shop_ids(phone_number=None):
    if phone_number:
        # phone_number = get_phone_number(phone_number)
        shops = DATABASE.shop.find({'phone_numbers': phone_number},
                                   {'_id': True}) \
            .sort('updated_at', -1)
    else:
        shops = DATABASE.shop.find({}, {'_id': True}) \
            .sort('updated_at', -1)
    return [shop['_id'] for shop in shops]


def get_shops_hq(phone_number=None):
    if phone_number:
        # phone_number = get_phone_number(phone_number)
        shops = DATABASE.shop.find({'hqstaffs': phone_number},
                                   {'_id': True}) \
            .sort('updated_at', -1)
        return [shop['_id'] for shop in shops]
    else:
        return []


def get_shop_by_emp(phone_number):
    # phone_number = get_phone_number(phone_number)
    shops = DATABASE.shop.find({'emps': phone_number}, {'_id': True}) \
        .sort('updated_at', -1)
    return [shop['_id'] for shop in shops]


def get_shop_info(shop_id=None, gateway_mac=None):
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.shop.find_one({'_id': shop_id})
    elif gateway_mac:
        if isinstance(gateway_mac, list):
            gateway_mac = gateway_mac[0]
        gateway_mac = normalize(gateway_mac)
        return DATABASE.shop.find_one({'gateway_mac': gateway_mac})


def get_shop_by_slug(slug):
    shop = DATABASE.shop.find_one({'slug': slug})
    if shop:
        shop['_id'] = str(shop['_id'])
    return shop


def get_user_info(user_id=None, client_mac=None, phone_number=None, email=None):
    if user_id:
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        return DATABASE.user.find_one({'_id': user_id})
    elif client_mac:
        if isinstance(client_mac, list):
            client_mac = client_mac[0]
        client_mac = normalize(client_mac)
        return DATABASE.user.find_one({'client_mac': client_mac})
    elif phone_number:
        # phone_number = get_phone_number(phone_number)
        return DATABASE.user.find_one({'phone': phone_number})
    elif email:
        return DATABASE.user.find_one({'email': email})


def save_access_log(gateway_mac, client_mac, user_agent=None):
    if not gateway_mac or not client_mac:
        return False

    info = {
        'gateway_mac': normalize(gateway_mac),
        'client_mac': normalize(client_mac),
        'user_agent': user_agent,
        'timestamp': time.time()
    }
    DATABASE.access_log.insert(info)

    shop = get_shop_info(gateway_mac=gateway_mac)
    # if shop:
    #     shop_id = shop['_id']

    #     os_family = user_agents.parse(user_agent)\
    #                            .os.family.lower().replace(' ', '-')

    #     update_metric(shop_id, 'access.count', 1)
    #     update_metric(shop_id, 'device.os.{}.count'.format(os_family), 1)

    return True


def get_access_log(gateway_macs, page, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(gateway_macs, list):
        raise ValueError

    _records = DATABASE.access_log \
        .find({'gateway_mac': {'$in': gateway_macs}}) \
        .sort('timestamp', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)
    records = []
    for _record in _records:
        ua = user_agents.parse(_record.get('user_agent', ''))

        if ua and ua.device.family != 'Other':
            _record['device'] = ua.device.family

        if ua and ua.os.family != 'Other':
            _record['os'] = ua.os.family + ' ' + ua.os.version_string

        shop = get_shop_info(gateway_mac=_record['gateway_mac'])
        if shop:
            _record['shop'] = shop.get('name')
        _record['when'] = arrow.get(_record['timestamp']). \
            format('HH:mm DD-MM-YYYY')

        records.append(_record)
    return records


def total_access_log_by_os(gateway_macs, os_string, from_date=None, to_date=None):
    info = {'gateway_mac': {'$in': gateway_macs}}
    if os_string == "Linux":
        info = {'gateway_mac': {'$in': gateway_macs},
                '$and': [
                    {'user_agent': {'$regex': os_string}},
                    {'user_agent': {'$not': re.compile('Androi')}}
        ]}
    else:
        info = {'gateway_mac': {'$in': gateway_macs},
                'user_agent': {'$regex': os_string}
                }
    if from_date and from_date != 'None':
        info['timestamp'] = {}
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())

        info['timestamp']['$gte'] = from_tmp

    if to_date and to_date != 'None':
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        info['timestamp']['$lte'] = to_tmp
    return DATABASE.access_log.find(info).count()


def total_access_log(gateway_macs, from_date=None, to_date=None):
    if not isinstance(gateway_macs, list):
        raise ValueError
    info = {'gateway_mac': {'$in': gateway_macs}}
    if from_date and from_date != 'None':
        info['timestamp'] = {}
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())

        info['timestamp']['$gte'] = from_tmp

    if to_date and to_date != 'None':
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        info['timestamp']['$lte'] = to_tmp
    return DATABASE.access_log \
        .find(info).count()


def get_shops_clients(page=None,
                      page_size=settings.ITEMS_PER_PAGE,
                      dealer=None):
    info = {}

    if dealer:
        info['dealer_id'] = dealer
    results = []
    if page:
        return DATABASE.shop.find(info) \
            .sort('created_at', -1).skip(page_size * (page - 1)) \
            .limit(page_size)
    else:
        return DATABASE.shop.find(info) \
            .sort('created_at', -1)


def total_shops_clients(dealer=None):
    info = {}

    if dealer:
        info['dealer_id'] = dealer

    return DATABASE.shop.find(info, {'_id': True}).count()


def get_access_count(gateway_mac):
    return DATABASE.access_log \
        .find({'gateway_mac': {'$in': gateway_mac}}) \
        .count()


def get_phone_number(number):
    number = number.strip().replace(' ', '')
    num_prefix = [
        {
            'num': '98',
            'net': 'vt'
        },
        {
            'num': '97',
            'net': 'vt'
        },
        {
            'num': '168',
            'net': 'vt'
        },
        {
            'num': '169',
            'net': 'vt'
        },
        {
            'num': '167',
            'net': 'vt'
        },
        {
            'num': '166',
            'net': 'vt'
        },
        {
            'num': '165',
            'net': 'vt'
        },
        {
            'num': '161',
            'net': 'vt'
        },
        {
            'num': '164',
            'net': 'vt'
        },
        {
            'num': '163',
            'net': 'vt'
        },
        {
            'num': '162',
            'net': 'vt'
        },
        {
            'num': '91',
            'net': 'vn'
        },
        {
            'num': '94',
            'net': 'vn'
        },
        {
            'num': '123',
            'net': 'vn'
        },
        {
            'num': '23',
            'net': 'vn'
        },
        {
            'num': '124',
            'net': 'vn'
        },
        {
            'num': '125',
            'net': 'vn'
        },
        {
            'num': '81',
            'net': 'vn'
        },
        {
            'num': '82',
            'net': 'vn'
        },
        {
            'num': '83',
            'net': 'vn'
        },
        {
            'num': '84',
            'net': 'vn'
        },
        {
            'num': '85',
            'net': 'vn'
        },
        {
            'num': '127',
            'net': 'vn'
        },
        {
            'num': '129',
            'net': 'vn'
        },
        {
            'num': '90',
            'net': 'mb'
        },
        {
            'num': '93',
            'net': 'mb'
        },
        {
            'num': '122',
            'net': 'mb'
        },
        {
            'num': '126',
            'net': 'mb'
        },
        {
            'num': '121',
            'net': 'mb'
        },
        {
            'num': '128',
            'net': 'mb'
        },
        {
            'num': '120',
            'net': 'mb'
        },
        {
            'num': '70',
            'net': 'mb'
        },
        {
            'num': '79',
            'net': 'mb'
        },
        {
            'num': '77',
            'net': 'mb'
        },
        {
            'num': '76',
            'net': 'mb'
        },
        {
            'num': '78',
            'net': 'mb'
        },
        {
            'num': '92',
            'net': 'vnm'
        },
        {
            'num': '188',
            'net': 'other'
        },
        {
            'num': '99',
            'net': 'other'
        },
        {
            'num': '199',
            'net': 'other'
        },
        {
            'num': '96',
            'net': 'vt'
        },
        {
            'num': '95',
            'net': 'other'
        },
        {
            'num': '186',
            'net': 'other'
        },
        {
            'num': '86',
            'net': 'vt'
        },
        {
            'num': '88',
            'net': 'vn'
        },
        {
            'num': '32',
            'net': 'vt'
        },
        {
            'num': '33',
            'net': 'vt'
        },
        {
            'num': '34',
            'net': 'vt'
        },
        {
            'num': '35',
            'net': 'vt'
        },
        {
            'num': '36',
            'net': 'vt'
        },
        {
            'num': '37',
            'net': 'vt'
        },
        {
            'num': '38',
            'net': 'vt'
        },
        {
            'num': '39',
            'net': 'vt'
        },
        {
            'num': '56',
            'net': 'vnm'
        },
        {
            'num': '58',
            'net': 'vnm'
        },
        {
            'num': '59',
            'net': 'gtel'
        },
        {
            'num': '89',
            'net': 'mb'
        },
        {
            'num': '8',
            'net': 'tl'
        },
        {
            'num': '9',
            'net': 'tl'
        },
        {
            'num': '6',
            'net': 'tl'
        },
        {
            'num': '86',
            'net': 'vt'
        },
        {
            'num': '2',
            'net': 'mbc'
        },
        {
            'num': '24',
            'net': 'mbhn'
        },
        {
            'num': '28',
            'net': 'mbhcm'
        },
    ]

    if str(number).startswith('84'):
        pnumber = number[2:]
    elif str(number).startswith('+84'):
        pnumber = number[3:]
    elif str(number).startswith('+66'):
        pnumber = number[3:]
    elif str(number).startswith('8'):
        pnumber = number
    elif str(number).startswith('9'):
        pnumber = number
    elif str(number).startswith('1'):
        pnumber = number
    elif str(number).startswith('02'):
        pnumber = number[1:]
    elif str(number).startswith('0'):
        pnumber = str(number).lstrip('0')

    else:
        return False
    for prefix in num_prefix:
        if str(pnumber).startswith(prefix['num']):
            cnumber = pnumber[len(prefix['num']):]
            print("cnumber:", cnumber)
            if prefix['net'] in ['mbc']:
                if len(cnumber) != 9:
                    return False
            elif prefix['net'] in ['mbhn'] or prefix['net'] in ['mbhcm']:
                if len(cnumber) != 8:
                    return False
            elif prefix['net'] in ['tl']:
                if len(cnumber) != 8:
                    return False
            else:
                if len(cnumber) != 7:
                    return False

            if not cnumber.isdigit():
                return False

            return '0' + pnumber
    return False


def create_campaign_fpt_gateway(client_id, client_secret, scope, campaign_name,
                                brand_name, message, schedule_time, quota):
    url_camp = 'http://service.sms.fpt.net/api/create-campaign'
    session_id = str(uuid4())
    token = get_access_fpt_gateway(
        client_id, client_secret, scope, session_id=session_id)
    access_token = token.get('access_token')

    campaign_code = ''
    message = remove_accents(message)
    if access_token and len(access_token) > 0:
        data = {
            "access_token": access_token,
            "session_id": session_id,
            "CampaignName": campaign_name,
            "BrandName": brand_name,
            "Message": message,
            "ScheduleTime": schedule_time,
            "Quota": quota
        }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        result = requests.post(
            url_camp, data=json.dumps(data), headers=headers)

        if result and result.status_code == 200:
            campaign_code = result.json().get('CampaignCode')
    return campaign_code


def send_campaign_fpt_gateway(merchant_id, client_id, client_secret, scope,
                              campaign_code, message, phone_list, camp_id):
    url_send = 'http://service.sms.fpt.net/api/push-brandname-ads'
    session_id = str(uuid4())
    token = get_access_fpt_gateway(
        client_id, client_secret, scope, session_id=session_id)
    access_token = token.get('access_token')
    if access_token and len(access_token) > 0:
        data = {
            "access_token": access_token,
            "session_id": session_id,
            "CampaignCode": campaign_code,
            "PhoneList": phone_list
        }

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        result = requests.post(
            url_send, data=json.dumps(data), headers=headers)

        if result and result.status_code == 200:
            for phone in phone_list.split(','):
                info = {
                    'phone_number': phone,
                    'message': message,
                    'timestamp': time.time(),
                    'merchant_id': str(merchant_id),
                    'camp_id': str(camp_id),
                    'campaign_code': campaign_code
                }

                DATABASE.sms_log.insert(info)


def create_app_synchronized(client_id=None,
                            secret_id=None,
                            name_shop=None,
                            merchant_id_app=None,
                            kind=None,
                            name_app=None,
                            status=None,
                            url_login=None,
                            api_key=None,
                            pos_parent=None,
                            access_token=None,
                            token=None,
                            type_app=None,
                            merchant_id=None,
                            src_logo=None,
                            chatbot_id=None,
                            chatfuel_token=None,
                            ahachat_token=None,
                            api_secret=None,
                            user_vcall=None,
                            password_vcall=None,
                            account_role=None,
                            authen_name=None,
                            vcall_token=None,
                            extension=None,
                            status_account=None,
                            role_account=None,
                            app_name=None,
                            domain=None,
                            account_id=None,
                            extentions=None,
                            app_access_token=None,
                            shop_id=None,
                            id_list=None,
                            mailchimp_user=None,
                            mailchimp_api_key=None,
                            last_sync_mailchimp=None,
                            company_id_anvui=None,
                            company_name_zalo_pay=None,
                            brand_name_zalo_pay=None,
                            bussiness_type_zalo_pay=None,
                            phone_number_zalo_pay=None,
                            email_zalo_pay=None,
                            haravan_id_shop=None,
                            api_key_biz=None,
                            api_secret_key_biz=None,
                            project_token_biz=None,
                            zalo_oa_id=None,
                            username=None,
                            password=None,
                            active_mms=None,
                            active_sms=None,
                            user=None,
                            sub_domain=None
                            ):
    when = time.time()
    if str(name_app) == "chatfuel":
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'status': status,
            'type_app': 'chatbot',
            'name_app': name_app,
            'src_logo': src_logo,
            'setting': {
                'chatbot_id': chatbot_id,
                'chatfuel_token': chatfuel_token
            }}
    elif str(name_app) == "ahachat":
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'status': status,
            'type_app': 'chatbot',
            'name_app': name_app,
            'src_logo': src_logo,
            'setting': {
                'chatbot_id': chatbot_id,
                'ahachat_token': ahachat_token
            }}
    elif str(name_app) == 'vcall':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'status': "True",
            'type_app': type_app,
            'name_app': name_app,
            'src_logo': src_logo,
            'setting': {
                'client_id': client_id,
                'secret_id': secret_id,
                'url_login': url_login,
                'api_secret': api_secret,
                'extension': extension,
                'kind': kind,
                'api_key': api_key,
                'merchant_id_app': merchant_id_app,
                'access_token': access_token,
                'name_shop': name_shop,
                'pos_parent': pos_parent,
                'info': [
                    {
                        'account_id': account_role,
                        'user_name': user_vcall,
                        'pass_word': password_vcall,
                        'token': vcall_token,
                        'authen_name': authen_name,
                        'role_account': role_account,
                        'status_account': status_account,
                        'app_name': app_name
                    }
                ]
            }}
    elif str(name_app) == 'mailchimp':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'update_at': when,
            'type_app': type_app,
            'status': "True",
            'name_app': name_app,
            'last_sync_mailchimp': last_sync_mailchimp,
            'setting': {
                'id_list': id_list,
                'mailchimp_user': mailchimp_user,
                'mailchimp_api_key': mailchimp_api_key
            }
        }
    elif str(name_app) == 'anvui':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'type_app': type_app,
            'status': status,
            'name_app': name_app,
            'setting': {
                'company_id': company_id_anvui
            }
        }
    elif str(name_app) == 'haravan':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'type_app': type_app,
            'name_app': name_app,
            'setting': {
                'access_token': access_token,
                'domain': domain,
                'id_shop': haravan_id_shop
            }
        }
    elif str(name_app) == 'zalo_pay':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'type_app': type_app,
            'status': True,
            'name_app': name_app,
            'setting': {
                'company_name_zalo_pay': company_name_zalo_pay,
                'brand_name_zalo_pay': brand_name_zalo_pay,
                'bussiness_type_zalo_pay': bussiness_type_zalo_pay,
                'phone_number_zalo_pay': phone_number_zalo_pay,
                'email_zalo_pay': email_zalo_pay
            }
        }
    elif str(name_app) == 'bizfly':
        info = {
            'merchant_id': merchant_id,
            'create_at': when,
            'update_at': when,
            'name_app': name_app,
            'type_app': type_app,
            'setting': {
                'api_key': api_key_biz,
                'api_secret_key': api_secret_key_biz,
                'project_token': project_token_biz
            }
        }
    elif str(name_app) == 'GHDC':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'type_app': type_app,
            'status': status,
            'name_app': name_app,
            'setting': {
                'username': username,
                'password': password,
                'active_mms': active_mms,
                'active_sms': active_sms
            }
        }
    elif str(name_app) == 'callbot':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'type_app': type_app,
            'status': status,
            'name_app': name_app,
            'setting': {
                'api_key': api_key
            }
        }
    elif str(name_app) == 'abot':
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'type_app': type_app,
            'status': status,
            'name_app': name_app,
            'setting': {
                'user': user,
                "password": password,
                "sub_domain": sub_domain
            }
        }
    else:
        info = {
            'create_at': when,
            'merchant_id': merchant_id,
            'update_at': when,
            'status': status,
            'type_app': type_app,
            'name_app': name_app,
            'src_logo': src_logo,
            'app_access_token': app_access_token,
            'setting': {
                'client_id': client_id,
                'secret_id': secret_id,
                'url_login': url_login,
                'api_secret': api_secret,
                'user_vcall': user_vcall,
                'password_vcall': password_vcall,
                'extension': extension,
                'kind': kind,
                'api_key': api_key,
                'merchant_id_app': merchant_id_app,
                'access_token': access_token,
                'token': token,
                'name_shop': name_shop,
                'pos_parent': pos_parent
            }}

    return DATABASE.app_synchronized.insert(info)


def update_app_synchronized(client_id=None,
                            secret_id=None,
                            name_shop=None,
                            status=None,
                            url_login=None,
                            merchant_id_app=None,
                            api_key=None,
                            kind=None,
                            app_id=None,
                            merchant_id=None,
                            chatbot_id=None,
                            chatfuel_token=None,
                            ahachat_token=None,
                            type_app=None,
                            name_app=None,
                            api_secret=None,
                            user_vcall=None,
                            password_vcall=None,
                            extension=None,
                            pos_parent=None,
                            access_token=None,
                            token=None,
                            account_role=None,
                            authen_name=None,
                            vcall_token=None,
                            status_account=None,
                            role_account=None,
                            app_name=None,
                            domain=None,
                            extentions=None,
                            account_id=None,
                            app_access_token=None,
                            shop_id=None,
                            id_list=None,
                            mailchimp_user=None,
                            mailchimp_api_key=None,
                            last_sync_mailchimp=None,
                            company_id_anvui=None,
                            haravan_id_shop=None,
                            api_key_biz=None,
                            api_secret_key_biz=None,
                            project_token_biz=None,
                            zalo_oa_id=None,
                            username=None,
                            password=None,
                            active_mms=None,
                            active_sms=None,
                            user=None,
                            sub_domain=None
                            ):
    when = time.time()
    if str(name_app) == 'chatfuel':
        info = {'update_at': when,
                'status': status,
                'setting': {
                    'chatbot_id': chatbot_id,
                    'chatfuel_token': chatfuel_token
                }}
        DATABASE.app_synchronized.update({'type_app': type_app, 'merchant_id': merchant_id, 'name_app': name_app},
                                         {'$set': info})
    elif str(name_app) == 'ahachat':
        info = {'update_at': when,
                'status': status,
                'setting': {
                    'chatbot_id': chatbot_id,
                    'ahachat_token': ahachat_token
                }}
        DATABASE.app_synchronized.update({'type_app': type_app, 'merchant_id': merchant_id, 'name_app': name_app},
                                         {'$set': info})
    elif str(name_app) == 'vcall':
        DATABASE.app_synchronized.update_one({'merchant_id': merchant_id,
                                              'name_app': name_app,
                                              'setting.info.account_id': account_role},
                                             {'$set': {
                                                 'status': "True",
                                                 'update_at': time.time(),
                                                 'setting.info.$.user_name': user_vcall,
                                                 'setting.info.$.pass_word': password_vcall,
                                                 'setting.api_secret': api_secret,
                                                 'setting.api_key': api_key,
                                                 'setting.info.$.token': vcall_token,
                                                 'setting.info.$.authen_name': authen_name,
                                                 'setting.info.$.status_account': status_account,
                                                 'setting.info.$.role_account': role_account,
                                                 'setting.info.$.app_name': app_name,
                                             }})
    elif str(name_app) == 'mailchimp':
        DATABASE.app_synchronized.update_one({'merchant_id': str(merchant_id),
                                              'name_app': name_app,
                                              'shop_id': str(shop_id)},
                                             {'$set': {
                                                 'status': "True",
                                                 'update_at': time.time(),
                                                 'setting.id_list': id_list,
                                                 'setting.mailchimp_user': mailchimp_user,
                                                 'setting.mailchimp_api_key': mailchimp_api_key,
                                                 'last_sync_mailchimp': last_sync_mailchimp
                                             }})
    elif str(name_app) == 'anvui':
        DATABASE.app_synchronized.update_one({'merchant_id': str(merchant_id),
                                              'name_app': name_app},
                                             {'$set': {
                                                 'status': status,
                                                 'update_at': time.time(),
                                                 'setting.company_id': company_id_anvui
                                             }})
    elif str(name_app) == 'GHDC':
        DATABASE.app_synchronized.update_one({'merchant_id': str(merchant_id),
                                              'name_app': name_app},
                                             {'$set': {
                                                 'status': status,
                                                 'update_at': time.time(),
                                                 'setting.username': username,
                                                 'setting.password': password,
                                                 'active_mms': active_mms,
                                                 'active_sms': active_sms
                                             }})
    elif str(name_app) == 'haravan':
        DATABASE.app_synchronized.update_one({'merchant_id': str(merchant_id),
                                              'name_app': name_app},
                                             {'$set': {
                                                 'update_at': time.time(),
                                                 'setting.access_token': access_token,
                                                 'setting.domain': domain,
                                                 'setting.id_shop': haravan_id_shop
                                             }})
    elif str(name_app) == 'bizfly':
        DATABASE.app_synchronized.update_one({'merchant_id': str(merchant_id),
                                              'name_app': name_app,
                                              'type_app': type_app},
                                             {
                                                 '$set': {
                                                     'update_at': time.time(),
                                                     'setting.api_key': api_key_biz,
                                                     'setting.api_secret_key': api_secret_key_biz,
                                                     'setting.project_token': project_token_biz,
                                                 }
        }
        )
    elif str(name_app) == 'callbot':
        DATABASE.app_synchronized.update_one({'merchant_id': str(merchant_id),
                                              'name_app': name_app},
                                             {'$set': {
                                                 'status': status,
                                                 'update_at': time.time(),
                                                 'setting.api_key': api_key
                                             }})
    elif str(name_app) == 'abot':
        DATABASE.app_synchronized.update_one({'merchant_id': str(merchant_id),
                                              'name_app': name_app},
                                             {'$set': {
                                                 'status': status,
                                                 'update_at': time.time(),
                                                 'setting.user': user,
                                                 'setting.password': password,
                                                 'setting.sub_domain': sub_domain
                                             }})
    else:
        info = {'update_at': when,
                'status': status,
                'type_app': type_app,
                'name_app': name_app,
                'app_access_token': app_access_token,
                'setting': {
                    'pos_parent': pos_parent,
                    'access_token': access_token,
                    'token': token,
                    'api_secret': api_secret,
                    'user_vcall': user_vcall,
                    'password_vcall': password_vcall,
                    'extension': extension,
                    'api_key': api_key,
                    'url_login': url_login,
                    'client_id': client_id,
                    'secret_id': secret_id,
                    'merchant_id_app': merchant_id_app,
                    'name_shop': name_shop,
                    'kind': kind
                }
                }

        DATABASE.app_synchronized.update({'type_app': type_app, 'merchant_id': merchant_id, 'name_app': name_app},
                                         {'$set': info})


def chatfuel_broadcasting(token, user_id, chatbot_id, block_name):
    url = 'https://api.chatfuel.com/bots/' + chatbot_id + '/users/' + user_id + '/send?chatfuel_token=' \
          + token + '&chatfuel_block_name=' + block_name
    headers = {"Content-Type": "application/json"}
    result = requests.post(url, headers=headers)
    return result


def get_chatfuel_customer_by_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    cus = DATABASE.customers.find({
        'merchant_id': ObjectId(merchant_id),
        'user.messenger_id': {'$exists': True}
    })
    if str(cus) == 'None':
        return False
    else:
        return cus


def get_app_synchronized_by_id(client_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    return DATABASE.app_synchronized.find_one({'_id': client_id})


def get_app_synchronized(name_app=None, merchant_id=None, kind=None, type_app=None, status=None, shop_id=None):
    if str(kind) != "None":
        return DATABASE.app_synchronized.find_one(
            {'name_app': name_app, 'merchant_id': str(merchant_id), 'setting.kind': kind})
    elif str(type_app) != "None":
        if str(status) != "None":
            return DATABASE.app_synchronized.find_one(
                {'type_app': type_app, 'merchant_id': str(merchant_id), 'status': status})
        else:
            return DATABASE.app_synchronized.find_one({'type_app': type_app, 'merchant_id': str(merchant_id)})
    elif str(name_app) != "None":
        if name_app == 'mailchimp':
            return DATABASE.app_synchronized.find_one({'name_app': name_app, 'merchant_id': str(merchant_id),
                                                       'shop_id': str(shop_id)})
        else:
            return DATABASE.app_synchronized.find_one({'name_app': name_app, 'merchant_id': str(merchant_id)})
    else:
        return ""


def count_active_chatbot(merchant_id=None, name_app=None):
    return DATABASE.app_synchronized.count({'merchant_id': merchant_id, 'status': 'True', 'name_app': name_app})


def get_access_token_api_retailer(client_id, client_secret):
    scope = 'PublicApi.Access'

    url_get_token = 'https://id.kiotviet.vn/connect/token'
    data = {
        "scopes": scope,
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token = ''
    result = requests.post(
        url_get_token, data=data, headers=headers)
    return result


def get_access_token_api_fnb(client_id, client_secret):
    '''
    Lay token de truy cap vao API cua kiotViet
    Return:
        token (string): Dinh dang "Bearer+token"
    '''
    scope = 'PublicApi.Access.FNB'
    url_get_token = 'https://id.kiotviet.vn/connect/token'
    data = {
        "scopes": scope,
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    result = requests.post(url_get_token, data=data, headers=headers)
    return result


def check_url_service(url_service,
                      username=None,
                      password=None
                      ):
    para = urllib.parse.urlencode({'count': '1'})
    url = url_service + '/GetMembershipTop?{}'.format(para)

    try:
        test = requests.get(url=url)
    except:
        return False
    return True if test.status_code == 200 else False


def get_app_synchronized_by_url_service(url_service):
    return DATABASE.app_synchronized.find_one({'setting': {'url_service': url_service}})


def get_access_fpt_gateway(client_id, client_secret, scope, session_id=None):
    if not session_id:
        session_id = str(uuid4())
    url_get_token = 'http://service.sms.fpt.net/oauth2/token'
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "session_id": session_id
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    token = ''
    result = requests.post(
        url_get_token, data=json.dumps(data), headers=headers)
    if result and result.status_code == 200:
        token = result.json()
    return token


def send_sms_fpt_gateway(merchant_id,
                         client_id,
                         client_secret,
                         phone,
                         brand_name,
                         scope,
                         message,
                         activity_id,
                         camp_id=None):
    # Không gửi SMS nội dung giống nhau đến 1 user trong 1 ngày
    expire = 86400
    key = md5('{}{}'.format(phone, message)).hexdigest()
    if REDIS.get(key):
        return False
    url_send = ''
    access_token = ''
    phone = phone.lstrip('0')
    phone = '84' + phone
    message_not_base_64 = message
    message = b64encode(message)
    url_send = 'http://service.sms.fpt.net/api/push-brandname-otp'
    token = get_access_fpt_gateway(client_id, client_secret,
                                   scope)
    access_token = token.get('access_token')
    if access_token and len(access_token) > 0 and len(
            url_send) > 0:
        print('OK')
        data = {
            "access_token": access_token,
            "session_id": str(uuid4()),
            "BrandName": brand_name,
            "Phone": phone,
            "Message": message
        }
        headers = {
            'Content-type':
                'application/json',
            'Accept':
                'text/plain'
        }
        result = requests.post(
            url_send,
            data=json.dumps(data),
            headers=headers)
        print(result.content)
        if result and result.status_code == 200:
            info = {
                'phone_number':
                    phone,
                'message':
                    message_not_base_64,
                'timestamp':
                    time.time(),
                'merchant_id':
                    str(merchant_id
                        ),
                'camp_id':
                    str(camp_id)
            }

            DATABASE.sms_log.insert(
                info)

            if result == 0:
                REDIS.set(
                    key,
                    True
                )
                REDIS.expire(
                    key,
                    expire
                )
                send_activity.update_send_activity(activity_id, True)
                return True
            else:
                send_activity.update_send_activity(activity_id, False)
                return False

        else:
            send_activity.update_send_activity(activity_id, False)
            return False


def send_sms_bluesea(merchant_id,
                     user_sms,
                     pass_sms,
                     brand_name,
                     phone_number,
                     message,
                     activity_id,
                     message_type,
                     expire=86400,
                     shop_id=None,
                     is_spam=None,
                     camp_id=None,
                     client_capture=None):
    BLUESEA = 'http://sms.8x77.vn:8077/mt-services/MTService?WSDL'
    if not phone_number:
        return False
    phone_number = phone_number.lstrip('0')
    phone_number = '84' + phone_number
    if not message.strip():
        return False
    User_Name = user_sms
    Password = pass_sms
    Service_ID = user_sms
    Command_Code = brand_name
    Message_Type = '0'
    Request_ID = '123456'
    Total_Message = '1'
    Message_Index = '1'
    IsMore = '1'
    Content_Type = '0'
    User_ID = phone_number
    Message = b64encode(message)
    session = Session()
    session.auth = HTTPBasicAuth(User_Name, Password)
    client = Client(
        BLUESEA, transport=Transport(session=session))
    result = client.service.sendMT(User_ID, Message, Service_ID,
                                   Command_Code, Message_Type,
                                   Request_ID, Total_Message,
                                   Message_Index, IsMore,
                                   Content_Type)

    info = {
        'phone_number': phone_number,
        'message': message,
        'timestamp': time.time(),
        'merchant_id': str(merchant_id),
        'camp_id': str(camp_id)
    }

    if result == 0:
        DATABASE.sms_log.insert(info)
        # if shop_id:
        #     sms_count = int(shop_info.get('sms_count', 0))
        #     if sms_count > 1:
        #             sms_count = sms_count - 1
        #             update_sms_count(shop_id, sms_count)
        send_activity.update_send_activity(activity_id, True)
        return True
    else:
        send_activity.update_send_activity(activity_id, False)
        return False


def send_sms_cuon(merchant_id,
                  phone_number,
                  message,
                  expire=86400,
                  shop_id=None,
                  is_spam=None,
                  camp_id=None):
    BLUESEA = 'http://sms.8x77.vn:8077/mt-services/MTService?WSDL'

    if not phone_number:
        return False
    phone_number = phone_number.lstrip('0')
    phone_number = '84' + phone_number
    if not message.strip():
        return False

    User_Name = 'cuonnroll'
    Password = 'cuonnroll@!231'
    Service_ID = 'cuonnroll'
    Command_Code = 'CUONNROLL'
    Message_Type = '0'
    Request_ID = '123456'
    Total_Message = '1'
    Message_Index = '1'
    IsMore = '1'
    Content_Type = '0'
    User_ID = phone_number
    Message = b64encode(message)

    # Không gửi SMS nội dung giống nhau đến 1 user trong 1 ngày
    key = md5('{}{}'.format(phone_number, message)).hexdigest()
    if REDIS.get(key):
        return False
    session = Session()
    session.auth = HTTPBasicAuth(User_Name, Password)
    client = Client(BLUESEA, transport=Transport(session=session))
    result = client.service.sendMT(User_ID, Message, Service_ID, Command_Code,
                                   Message_Type, Request_ID, Total_Message,
                                   Message_Index, IsMore, Content_Type)
    info = {
        'phone_number': phone_number,
        'message': message,
        'timestamp': time.time(),
        'merchant_id': str(merchant_id),
        'camp_id': str(camp_id)
    }

    if result == 0:
        REDIS.set(key, True)
        REDIS.expire(key, expire)
        DATABASE.sms_log.insert(info)
        # if shop_id:
        #     sms_count = int(shop_info.get('sms_count', 0))
        #     if sms_count > 1:
        #             sms_count = sms_count - 1
        #             update_sms_count(shop_id, sms_count)
        return True
    else:
        return False


def send_noah_sms(user_sms,
                  pass_sms,
                  brand_name,
                  phone,
                  message,
                  expire=86400,
                  shop_id=None,
                  merchant_id=None,
                  camp_id=None,
                  is_spam=None):
    shop_info = None
    if shop_id:
        shop_info = get_shop_info(shop_id=shop_id)

    if not message.strip():
        return False

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    url_send = ''
    data = {
        "UserName": user_sms,
        "Password": md5(pass_sms).hexdigest(),
        "BrandName": brand_name,
        "SmsContent": message,
        "TimeSend": "",
        "Phones": phone,
        "ClientId": str(uuid4()),
        "CheckSum": ""
    }
    if not is_spam or is_spam == False or is_spam == 'care':
        # Không gửi SMS nội dung giống nhau đến 1 user trong 1 ngày
        key = md5('{}{}'.format(phone, message)).hexdigest()
        if REDIS.get(key):
            return False
        url_send = 'http://br.noahsms.com/api/SendSms/SendSmsCskhWithoutChecksum'
        r = requests.post(url_send, data=json.dumps(data), headers=headers)
        if r and r.status_code == 200 and r.json() and \
                isinstance(r.json(), list) and len(r.json()) == 1 and \
                r.json()[0]['code'] == 1:
            info = {
                'phone_number': phone,
                'message': message,
                'timestamp': time.time(),
                'merchant_id': str(merchant_id),
                'camp_id': str(camp_id)
            }
            REDIS.set(key, True)
            REDIS.expire(key, expire)
            DATABASE.sms_log.insert(info)
            # if shop_id:
            #     sms_count = int(shop_info.get('sms_count', 0))
            #     if sms_count > 1:
            #             sms_count = sms_count - 1
            #             update_sms_count(shop_id, sms_count)
            return True
        else:
            return False
    else:
        url_send = 'http://br.noahsms.com/api/SendSms/SendSmsQc'
        r = requests.post(url_send, data=json.dumps(data), headers=headers)
        if r and r.status_code == 200 and r.json() and \
                isinstance(r.json(), list) and len(r.json()) == 1 and \
                r.json()[0]['code'] == 1:
            for ph in phone.split(','):
                key = md5('{}{}'.format(ph, message)).hexdigest()
                if REDIS.get(key):
                    return False
                info = {
                    'phone_number': ph,
                    'message': message,
                    'timestamp': time.time(),
                    'merchant_id': str(merchant_id),
                    'camp_id': str(camp_id)
                }
                REDIS.set(key, True)
                REDIS.expire(key, expire)
                DATABASE.sms_log.insert(info)
            # if shop_id:
            #     sms_count = int(shop_info.get('sms_count', 0))
            #     if sms_count > 1:
            #             sms_count = sms_count - 1
            #             update_sms_count(shop_id, sms_count)
            return True
        else:
            return False


def handle_sms_large(customers):
    if len(customers) > 1000:
        return list(chunks(customers, 900))
    else:
        return customers


def send_sms_viettel(merchant_id, phone_number, message, activity_id, camp_id=None):
    phone_number = phone_number.lstrip('0')
    phone_number = '84' + phone_number
    URL = 'http://ams.tinnhanthuonghieu.vn:8009/bulkapi?wsdl'
    client = Client(URL)
    merchant = get_merchant(merchant_id)
    USER_API = merchant.get('user_sms')
    PASS_API = merchant.get('pass_sms')
    BRANDNAME = merchant.get('brand_name')
    request_id = 1
    CP_CODE = 'WIFIMARKETING'

    result = client.service.wsCpMt(
        USER_API, PASS_API, CP_CODE, request_id, phone_number, phone_number, BRANDNAME, 'bulksms', message, 0
    )

    if 'OK' in result:
        info = {
            'phone_number':
                phone_number,
            'message':
                message,
            'timestamp':
                time.time(),
            'merchant_id':
                str(merchant_id
                    ),
            'camp_id':
                str(camp_id)
        }

        DATABASE.sms_log.insert(
            info)

        send_activity.update_send_activity(activity_id, True)
        return True
    else:
        send_activity.update_send_activity(activity_id, False)
        return False


def send_sms_vht(merchant_id, phone, message, activity_id, camp_id=None):
    VHT_SERVICE_DOMAIN = "http://sms3.vht.com.vn"
    merchant = get_merchant(merchant_id)
    user = handle_customers.get_user_merchant_by_phone(merchant_id, phone)
    user_id = None
    if user:
        user_id = user.get('user_id')
    VHT_USER_API = merchant.get('user_sms')
    VHT_PASS_API = merchant.get('pass_sms')
    VHT_BRANDNAME = merchant.get('brand_name')
    URL_SEND_SMS = VHT_SERVICE_DOMAIN + "/ccsms/Sms/SMSService.svc/ccsms/json"
    data = {"submission":
            {"api_secret": VHT_PASS_API, "api_key": VHT_USER_API,
             "sms": [{"text": message, "brandname": VHT_BRANDNAME, "id": str(user_id), "to": phone}]}}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = requests.post(URL_SEND_SMS, json=data, headers=headers)

    if result and result.status_code == 200:
        info = {
            'phone_number':
                phone,
            'message':
                message,
            'timestamp':
                time.time(),
            'merchant_id':
                str(merchant_id
                    ),
            'camp_id':
                str(camp_id)
        }

        DATABASE.sms_log.insert(
            info)

        send_activity.update_send_activity(activity_id, True)
        return True
    else:
        send_activity.update_send_activity(activity_id, False)
        return False


def send_sms_vhat(merchant_id, phone, message, activity_id, camp_id=None):
    VHAT_SERVICE_DOMAIN = "http://rest.esms.vn/"
    merchant = get_merchant(merchant_id)
    # user = handle_customers.get_user_merchant_by_phone(merchant_id, phone)
    # user_id = user.get('user_id')
    VHAT_API_KEY = merchant.get('api_key_vhat')
    VHAT_SECRET_KEY = merchant.get('secret_key_vhat')
    VHAT_SMS_TYPE = merchant.get('sms_type')
    VHAT_BRANDNAME = merchant.get('brand_name')
    URL_SEND_SMS = VHAT_SERVICE_DOMAIN + \
        "MainService.svc/json/SendMultipleMessage_V4_post_json/"
    data = {
        "ApiKey": VHAT_API_KEY,
        "SecretKey": VHAT_SECRET_KEY,
        "Content": message,
        "Phone": phone,
        "SmsType": VHAT_SMS_TYPE,
        "Brandname": VHAT_BRANDNAME
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = requests.post(URL_SEND_SMS, json=data, headers=headers)
    if result and result.status_code == 200:
        info = {
            'phone_number':
                phone,
            'message':
                message,
            'timestamp':
                time.time(),
            'merchant_id':
                str(merchant_id
                    ),
            'camp_id':
                str(camp_id)
        }

        DATABASE.sms_log.insert(
            info)

        send_activity.update_send_activity(activity_id, True)
        return True
    else:
        send_activity.update_send_activity(activity_id, False)
        return False


def send_sms_hq(merchant_id,
                phone_number,
                message,
                activity_id,
                is_spam=None,
                camp_id=None,
                scope=None,
                phone_list=None,
                campaign_code=None,
                expire=None,
                client=None):
    message = remove_accents(message)
    merchant = get_merchant(merchant_id)
    sms_provider = merchant.get('sms_provider')
    user_sms = merchant.get('user_sms')
    pass_sms = merchant.get('pass_sms')
    brand_name = merchant.get('brand_name')
    message_quota = merchant.get('quota')
    if message_quota:
        if str(message_quota) == '-1' or int(message_quota) > 0:
            if sms_provider and len(sms_provider) > 0 and user_sms \
                    and len(user_sms) > 0 and pass_sms and len(pass_sms) > 0:
                if sms_provider.upper() == 'BLUESEA':
                    print("BLUESEA{}".format(phone_number))
                    send_sms_bluesea(
                        merchant_id,
                        user_sms,
                        pass_sms,
                        brand_name,
                        phone_number,
                        message,
                        activity_id,
                        '0',
                        expire=86400,
                        shop_id=None,
                        is_spam=is_spam,
                        camp_id=camp_id,
                        client_capture=client
                    )

                elif sms_provider.upper() == 'VHT':
                    send_sms_vht(merchant_id, phone_number,
                                 message, activity_id, camp_id=None)
                elif sms_provider.upper() == 'VHAT':
                    send_sms_vhat(merchant_id, phone_number,
                                  message, activity_id, camp_id=None)
                # elif sms_provider.upper() == 'INCOM':
                #     send_sms_incom(merchant_id, phone_number, message, activity_id, camp_id=None)
                elif sms_provider.upper() == 'VIETTEL':
                    send_sms_viettel(merchant_id, phone_number,
                                     message, activity_id, camp_id=None)
                elif sms_provider.upper() == 'FPT':
                    if phone_list and len(
                            phone_list
                    ) > 0 and is_spam == 'spam':
                        send_campaign_fpt_gateway(
                            merchant_id,
                            user_sms,
                            pass_sms,
                            scope,
                            campaign_code,
                            message,
                            phone_list,
                            camp_id
                        )
                    else:
                        send_sms_fpt_gateway(
                            merchant_id,
                            user_sms,
                            pass_sms,
                            phone_number,
                            brand_name,
                            scope,
                            message,
                            activity_id,
                            camp_id=camp_id
                        )
                else:
                    pass
                update_merchant_message_quota(merchant_id)
            else:
                pass


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def send_sms(phone_number,
             message,
             expire=86400,
             shop_id=None,
             merchant_id=None,
             is_spam=None):
    """
    expire: Không cho phép gửi SMS nội dung giống nhau đến cùng 1 số trong
            khoảng thời gian này. Đơn vị: giây
    """
    shop_info = None
    if shop_id:
        shop_info = get_shop_info(shop_id=shop_id)

    phone_number = get_phone_number(phone_number)
    if not phone_number:
        return False

    if not message.strip():
        return False

    # Không gửi SMS nội dung giống nhau đến 1 user trong 1 ngày
    key = md5('{}{}'.format(phone_number, message)).hexdigest()
    if REDIS.get(key):
        return False

    message = 'VCC ' + message
    data = {
        'message': message,
        'brandname': '0901800288',
        'recipients': [{
            'message_id': str(uuid4()),
            'number': phone_number
        }]
    }
    # if shop_info:
    #     data['brandname'] = shop_info.get('name')

    data['username'] = 'fbs'
    data['password'] = 'GYdh=oi'
    r = requests.post(
        'http://103.69.194.60:8001/api/send',
        data=simplejson.dumps(data),
        headers={'Content-Type': 'application/json'})
    if r and r.status_code == 200 and r.json() and \
            isinstance(r.json(), list) and len(r.json()) == 1 and \
            r.json()[0]['status'] == 'SENT':
        REDIS.set(key, True)
        REDIS.expire(key, expire)

        info = {
            'phone_number': phone_number,
            'message': message,
            'timestamp': time.time()
        }
        if shop_id:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            info['shop_id'] = shop_id

        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            info['merchant_id'] = merchant_id

        DATABASE.sms_log.insert(info)
        if shop_id:
            sms_count = int(shop_info.get('sms_count', 0))
            if sms_count > 1:
                sms_count = sms_count - 1
                update_sms_count(shop_id, sms_count)
        return True
    else:
        return False


def new_user_id(name, phone_number):
    num_digits = 4
    while True:
        text = slugify(name.split()[-1]) if name else 'U'
        user_id = text.upper()
        if phone_number:
            user_id += phone_number[-num_digits:]
        if DATABASE.user.find_one({'id': user_id}):
            num_digits += 1
            continue
        return user_id


def new_phone_verification_code():
    # Không để code bắt đầu bằng 0 và 5 (cho rõ ràng)
    # - 0 dễ hiểu là không cần nhập cũng được
    # - 5 trùng với chữ "5 chữ số"
    digits = [random.choice([1, 2, 3, 4, 6, 7, 8, 9])]
    digits.extend(random.sample(range(0, 9), 4))
    return ''.join([str(i) for i in digits])


def register(name=None,
             phone=None,
             gender=None,
             birthday=None,
             client_mac=None,
             email=None,
             fb_id=None,
             age_range=None,
             home_town=None,
             relationship_status=None,
             first_name=None,
             middle_name=None,
             last_name=None,
             year_birthday=None,
             note=None,
             address=None,
             twitter=None,
             facebook=None,
             company=None,
             company_role=None,
             is_employee=None):
    # if phone:
    #     phone = get_phone_number(phone)
    #     if not phone:
    #         return False
    if name:
        name = name.strip()
    if client_mac:
        client_mac = normalize(client_mac) if client_mac else None
    if phone:
        user = DATABASE.user.find_one({'phone': phone})
    else:
        user = DATABASE.user.find_one({'email': email})

    if not user:
        user_id = new_user_id(name, phone)
        info = {
            'id': user_id,
            'name': name,
            'phone': phone,
            'gender': gender,
            'birthday': birthday,
            'year_birthday': year_birthday,
            'created_at': time.time(),
            'email': email,
            'fb_id': fb_id,
            'age_range': age_range,
            'home_town': home_town,
            'relationship_status': relationship_status,
            'is_employee': is_employee,
        }
        if client_mac:
            info['client_mac'] = [client_mac]
        if first_name:
            info['first_name'] = first_name
        if middle_name:
            info['middle_name'] = middle_name
        if last_name:
            info['last_name'] = last_name
        if note:
            info['note'] = note
        if address:
            info['address'] = address
        if facebook:
            info['facebook'] = facebook
        if twitter:
            info['twitter'] = twitter
        if company and len(company) > 0:
            info['company'] = company
        if company_role and len(company_role) > 0:
            info['company_role'] = company_role
        user_id = DATABASE.user.insert(info)
        return user_id
    else:

        if client_mac:
            # Xóa client mac khỏi các tài khoản cũ
            DATABASE.user.update(
                {
                    'client_mac': client_mac
                }, {'$pull': {
                    'client_mac': client_mac
                }},
                multi=True)

            # Lưu client mac sang tài khoản mới
            if phone:
                DATABASE.user.update({
                    'phone': phone
                }, {'$addToSet': {
                    'client_mac': client_mac
                }})
            else:
                DATABASE.user.update({
                    'email': email
                }, {'$addToSet': {
                    'client_mac': client_mac
                }})
        user_id = user.get('_id')
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)

        info = {}

        if name and len(name) > 0:
            info['name'] = name
        if phone and len(phone) > 0:
            info['phone'] = phone
        if gender and len(str(gender)) > 0:
            info['gender'] = gender
        if birthday and len(birthday) > 0:
            info['birthday'] = birthday
        if year_birthday and len(str(year_birthday)) > 0:
            info['year_birthday'] = year_birthday
        if email and len(email) > 0:
            info['email'] = email
        if fb_id and len(str(fb_id)) > 0:
            info['fb_id'] = fb_id
        if age_range and len(age_range) > 0:
            info['age_range'] = age_range
        if home_town and len(home_town) > 0:
            info['home_town'] = home_town
        if relationship_status and len(relationship_status) > 0:
            info['relationship_status'] = relationship_status
        if note and len(note) > 0:
            info['note'] = note
        if address and len(address) > 0:
            info['address'] = address
        if facebook and len(facebook) > 0:
            info['facebook'] = facebook
        if twitter and len(twitter) > 0:
            info['twitter'] = twitter
        if company and len(company) > 0:
            info['company'] = company
        if company_role and len(company_role) > 0:
            info['company_role'] = company_role
        if is_employee:
            info['is_employee'] = is_employee
        info['updated_at'] = time.time()
        # Update thông tin user
        DATABASE.user.update({'_id': user_id}, {'$set': info})

        return user_id


def update_user_by_id(user_id,
                      name=None,
                      phone=None,
                      gender=None,
                      birthday=None,
                      email=None,
                      fb_id=None,
                      age_range=None,
                      home_town=None,
                      relationship_status=None,
                      first_name=None,
                      middle_name=None,
                      last_name=None,
                      avatar=None,
                      user_id_zalo=None,
                      note=None,
                      address=None,
                      facebook=None,
                      twitter=None,
                      year_birthday=None,
                      company=None,
                      company_role=None,
                      is_employee=None,
                      ):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    info = {}
    if name and len(name) > 0:
        info['name'] = name
    if phone and len(phone) > 0:
        info['phone'] = phone
    if gender and len(str(gender)) > 0:
        info['gender'] = gender
    if birthday and len(birthday) > 0:
        info['birthday'] = birthday
    if year_birthday and len(str(year_birthday)) > 0:
        info['year_birthday'] = year_birthday
    if email and len(email) > 0:
        info['email'] = email
    if fb_id and len(str(fb_id)) > 0:
        info['fb_id'] = fb_id
    if age_range and len(age_range) > 0:
        info['age_range'] = age_range
    if home_town and len(home_town) > 0:
        info['home_town'] = home_town
    if relationship_status and len(relationship_status) > 0:
        info['relationship_status'] = relationship_status
    if note and len(note) > 0:
        info['note'] = note
    if address and len(address) > 0:
        info['address'] = address
    if facebook and len(facebook) > 0:
        info['facebook'] = facebook
    if twitter and len(twitter) > 0:
        info['twitter'] = twitter
    if user_id_zalo and len(user_id_zalo) > 0:
        info['user_id_zalo'] = user_id_zalo
    if company and len(company) > 0:
        info['company'] = company
    if company_role and len(company_role) > 0:
        info['company_role'] = company_role
    if is_employee:
        info['is_employee'] = is_employee
    info['updated_at'] = time.time()
    DATABASE.user.update({'_id': user_id}, {'$set': info})


def get_devices(non_shop=None):
    devices = []
    for device in DATABASE.devices.find().sort('ssid', 1):
        try:
            now = time.time()
            if now - device['last_heartbeat'] < 120:
                device['state'] = 'success'
            elif now - device['last_heartbeat'] < 300:
                device['state'] = 'warning'
            else:
                device['state'] = 'danger'
            shop_info = get_shop_info(gateway_mac=device['gateway_mac'])
            device['shop'] = {}
            if non_shop:
                if not shop_info:
                    devices.append(device)
            else:
                if shop_info:
                    device['shop'] = shop_info
                devices.append(device)
        except Exception:
            continue
    return devices


def update_user(phone, name=None, gender=None, birthday=None, email=None):
    info = {}
    if name:
        info['name'] = name
    if gender:
        info['gender'] = gender
    if birthday:
        info['birthday'] = birthday
    if email:
        info['email'] = email

    if phone:
        # phone = get_phone_number(phone)
        # if not phone:
        #     return False
        info['updated_at'] = time.time()
        DATABASE.user.update({'phone': phone}, {'$set': info})


def update_password_merchant(merchant_id, password):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    pass_hash = make_hash(password.encode('utf-8'))
    return DATABASE.merchants.update({'_id': merchant_id}, {'$set': {'password': pass_hash,
                                                                     'update_at': time.time(),
                                                                     'update_password': time.time()}})


def update_password_user(shop_id, phone, password):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    # phone = get_phone_number(phone)
    user = get_user_info(phone_number=phone)
    password = make_hash(password.encode('utf-8'))
    user_id = user.get('_id')
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_pass = DATABASE.user_pass.find_one({
        'shop_id': shop_id,
        'user_id': user_id
    })
    if user_pass:
        DATABASE.user_pass.update({
            'shop_id': shop_id,
            'user_id': user_id
        }, {'$set': {
            'password': password,
            'update': time.time()
        }})
    else:
        DATABASE.user_pass.insert({
            'shop_id': shop_id,
            'user_id': user_id,
            'password': password,
            'update': time.time()
        })


def user_pass_login(shop_id, phone, password):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    user = get_user_info(phone_number=phone)
    if not user:
        return False
    user_id = user.get('_id')
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_pass = DATABASE.user_pass.find_one({
        'shop_id': shop_id,
        'user_id': user_id
    })
    if user_pass:
        pass_hash = user_pass.get('password')
        if check_hash(password, pass_hash):
            return user_pass
        else:
            return False
    else:
        return False


def get_user_pass(shop_id, user_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user = DATABASE.user_pass.find_one({
        'shop_id': shop_id,
        'user_id': user_id
    })
    if user:
        user['shop_id'] = str(user['shop_id'])
        user['user_id'] = str(user['user_id'])
        user['_id'] = str(user['_id'])
        return user
    else:
        return False


def user_pass_token_key(shop_id, user_id, token_key):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    DATABASE.user_pass.update({
        'shop_id': shop_id,
        'user_id': user_id
    }, {'$set': {
        'token': token_key
    }})


def update_user_fb(user_id,
                   name,
                   gender=None,
                   birthday=None,
                   email=None,
                   fb_id=None,
                   age_range=None,
                   home_town=None,
                   relationship_status=None):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    info = {
        'name': name,
        'gender': gender,
        'birthday': birthday,
        'created_at': time.time(),
        'email': email,
        'fb_id': fb_id,
        'age_range': age_range,
        'home_town': home_town,
        'relationship_status': relationship_status,
        'updated_at': time.time()
    }
    DATABASE.user.update({'_id': user_id}, {'$set': info})


def get_shop_by_pos_id(pos_id):
    return DATABASE.shop.find_one({'pos_id': pos_id})


def get_shop_has_pos_id(merchant_id):
    list_shop_crm = DATABASE.shop.find({"pos_id": {"$exists": True},
                                        "merchant_id": merchant_id})
    return [shop.get('pos_id') for shop in list_shop_crm]


def mapping_shop_app(merchant_id, list_shop_app):
    def get_name_shop_app(list_shop_app, pos_id):

        try:
            for item in list_shop_app:
                if str(item['id']) == str(pos_id):
                    return item.get('locationName')
        except:
            return ""

    list_shop_crm = DATABASE.shop.find({"pos_id": {"$exists": True},
                                        "merchant_id": merchant_id})
    result = []
    for shop in list_shop_crm:
        result.append([shop.get("name"), get_name_shop_app(
            list_shop_app, shop.get("pos_id"))])
    return result


def mapping_shop_app_id(merchant_id, merchant_id_app):
    def get_name_shop_app(merchant_id, merchant_id_app, pos_id):
        list_shop_app = DATABASE.list_shop_app.find_one(
            {"merchant_id": merchant_id, 'merchant_id_app': merchant_id_app})
        try:
            result = ""
            shop_app = list_shop_app.get("list_shop_app")
            for item in shop_app:
                if pos_id in item:
                    return str(list(item.keys())[0])
        except:
            return ""

    list_shop_crm = DATABASE.shop.find({"pos_id": {"$exists": True},
                                        "merchant_id": merchant_id})
    result = []
    for shop in list_shop_crm:
        result.append([str(shop.get("_id")), get_name_shop_app(
            merchant_id, merchant_id_app, shop.get("pos_id"))])
    return result


def get_list_shop_app(merchant_id, merchant_id_app):
    result = DATABASE.list_shop_app.find_one({"merchant_id": merchant_id,
                                              "merchant_id_app": merchant_id_app})
    if result:
        return result.get("list_shop_app")
    else:
        return ""


def save_list_shop_kiot(list_shop_kiot, merchant_id, merchant_id_app):
    check = DATABASE.list_shop_app.find_one({"merchant_id": merchant_id,
                                             "merchant_id_app": merchant_id_app})
    try:
        if not check:
            DATABASE.list_shop_app.insert({
                'merchant_id': merchant_id,
                'merchant_id_app': merchant_id_app,
                'list_shop_app': list_shop_kiot,
            })
        else:
            DATABASE.list_shop_app.update_one({
                'merchant_id': merchant_id,
                'merchant_id_app': merchant_id_app},
                {'$set': {'list_shop_app': list_shop_kiot, }}
            )
        return True
    except:
        return False


def get_list_loc_pos(retailer, client_id, secret_id):
    def get_access_token(client_id, secret_id):
        scope = 'PublicApi.Access'
        url_get_token = 'https://id.kiotviet.vn/connect/token'
        data = {
            "scopes": scope,
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": secret_id
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token = ''
        result = requests.post(
            url_get_token, data=data, headers=headers)
        if result and result.status_code == 200:
            return result

    def get_location(retailer):
        token = get_access_token(client_id, secret_id)
        ACCESS_TOKEN = json.loads(token.text)['access_token']
        url_customer = 'https://public.kiotapi.com/branches'
        headers = {
            "Retailer": retailer,
            "Authorization": "Bearer " + str(ACCESS_TOKEN)
        }
        result = requests.get(url_customer, headers=headers)
        if result and result.status_code == 200:
            return result

    def list_location():
        loc = get_location(retailer)
        list_loc = json.loads(loc.text)
        result = []
        for loc in list_loc['data']:
            result.append({str(loc['id']): loc['branchName']})
        return result

    return list_location()


def update_tag_for_merchant(merchant_id, id_mer_kas, tag):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    info = {'tag': tag,
            'merchant_id_app': id_mer_kas,
            'update_at': time.time()}
    DATABASE.merchants.update_one({'_id': merchant_id}, {'$set': info})


def update_tag_merchant(merchant_id, tags):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    DATABASE.merchants.update_one({'_id': merchant_id}, {'$set': tags})


def update_setting_detection(merchant_id, active_detection, top5_detection, timing_detection, time_=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    active_detection = active_detection
    top5_detection = top5_detection
    timing_detection = timing_detection

    DATABASE.merchants.update({"_id": merchant_id}, {"$set": {
        'active_detection': active_detection,
        'top5_detection': top5_detection,
        'timing_detection': timing_detection,
        'hour_detection': time_,
        'update_at': time.time()
    }})
    pass


def update_merchants(merchant_id=None,
                     average_earnings=None,
                     time_after_send=None,
                     name=None,
                     phone=None,
                     password=None,
                     email=None,
                     avatar=None,
                     sms_provider=None,
                     user_sms=None,
                     pass_sms=None,
                     fcm_key_ios=None,
                     fcm_key_android=None,
                     brand_name=None,
                     user_hq=None,
                     pass_hq=None,
                     db_hq=None,
                     server_hq=None,
                     quota=None,
                     zalo_oa_id=None,
                     zalo_oa_key=None,
                     category=None,
                     telco=None,
                     alias_id=None,
                     pricing_plan=None,
                     package=None,
                     mail_settings=None,
                     business_model_id=None,
                     identity=None,
                     role=None,
                     time_per_visit=None,
                     time_user_connect=None,
                     agent=None,
                     sms_type_incom=None,
                     username_incom=None,
                     password_incom=None,
                     command_code_incom=None,
                     prefix_id_incom=None,
                     api_key_vhat=None,
                     secret_key_vhat=None,
                     sms_type=None,
                     brand_name_vina=None,
                     status_ads=None,
                     cp_code=None
                     ):
    when = time.time()

    if merchant_id:
        acc = get_merchant(merchant_id)
        if acc:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            info = {}
            if name and len(name) > 0:
                slug = slugify(name)
                merchant_by_slug = get_merchant_by_slug(slug)
                if not merchant_by_slug:
                    info['name'] = name
                    info['slug'] = slug
            if phone and len(phone) > 0:
                info['phone'] = phone
            if password and len(password) > 0:
                pass_hash = make_hash(password.encode('utf-8'))
                info['password'] = pass_hash
            if sms_provider:
                info['sms_provider'] = sms_provider
            if user_sms:
                info['user_sms'] = user_sms
            if pass_sms:
                info['pass_sms'] = pass_sms
            if sms_provider:
                info['sms_provider'] = sms_provider
            if brand_name:
                info['brand_name'] = brand_name
            if sms_type_incom:
                info['sms_type_incom'] = sms_type_incom
            if username_incom:
                info['username_incom'] = username_incom
            if password_incom:
                info['password_incom'] = password_incom
            if command_code_incom:
                info['command_code_incom'] = command_code_incom
            if prefix_id_incom:
                info['prefix_id_incom'] = prefix_id_incom
            if api_key_vhat:
                info['api_key_vhat'] = api_key_vhat
            if secret_key_vhat:
                info['secret_key_vhat'] = secret_key_vhat
            if sms_type:
                info['sms_type'] = sms_type
            if fcm_key_ios:
                info['fcm_key_ios'] = fcm_key_ios
            if fcm_key_android:
                info['fcm_key_android'] = fcm_key_android
            if brand_name:
                info['brand_name'] = brand_name
            if category:
                info['category'] = category
            if telco:
                info['telco'] = telco
            if alias_id:
                info['alias_id'] = alias_id
            if server_hq:
                info['server_hq'] = server_hq
            if user_hq:
                info['user_hq'] = user_hq
            if db_hq:
                info['db_hq'] = db_hq
            if pass_hq:
                info['pass_hq'] = pass_hq
            if quota:
                info['quota'] = quota
            if zalo_oa_id:
                info['zalo_oa_id'] = zalo_oa_id
            if zalo_oa_key:
                info['zalo_oa_key'] = zalo_oa_key
            info['email'] = email if email and len(email) > 0 else ''
            if avatar:
                info['avatar'] = avatar
            if package and len(package) > 0:
                info['package'] = package
            if mail_settings:
                info['mail_settings'] = mail_settings
            if business_model_id:
                info['business_model_id'] = business_model_id
            if identity:
                info['identity'] = identity
            if role:
                info['role'] = role
            if agent:
                info['agent'] = agent
            if brand_name_vina:
                info['brand_name_vina'] = brand_name_vina
            if cp_code:
                info['cp_code'] = cp_code
            info['average_earnings'] = average_earnings
            info['time_after_send'] = time_after_send
            info['time_per_visit'] = time_per_visit
            info['time_user_connect'] = time_user_connect

            info['update_at'] = when
            if status_ads:
                status_wifi_ads = False
                if status_ads == "True":
                    status_wifi_ads = True
                info['wifi_ads'] = status_wifi_ads
            DATABASE.merchants.update({'_id': merchant_id}, {'$set': info})
            try:
                search_engine.index_merchant_item(acc)
            except:
                pass
    else:
        if not pricing_plan:
            pricing_plan = 'trial'
        slug = slugify(name)
        pass_hash = make_hash(password.encode('utf-8'))
        merchant_id = DATABASE.merchants.insert({
            'name': name,
            'phone': phone,
            'email': email,
            'password': pass_hash,
            'slug': slug,
            'when': when,
            'pricing_plan': pricing_plan,
            'mail_settings': mail_settings,
            'business_model_id': business_model_id,
            'identity': identity,
            'role': role,
            'agent': agent
        })
        init_tags_merchant(merchant_id)
        acc = get_merchant(merchant_id)
        if acc:
            try:
                search_engine.index_merchant_item(acc)
            except:
                pass


def update_merchant_message_quota(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    merchant = get_merchant(merchant_id)
    quota = merchant.get('quota')
    if str(quota) != '-1' and int(quota) > 1:
        DATABASE.merchants.update({
            '_id': merchant_id
        }, {'$inc': {
            'order_count': -1
        }})


def update_merchant_bitly_token(merchant_id, access_token):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'bitly_access_token': access_token,
        'update_at': time.time()
    }})


def update_merchant_client_key(merchant_id, client_key):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'client_key': client_key,
        'update_at': time.time()
    }})

def update_merchant_haravan(merchant_id, email_haravan, token_haravan, callbot_api_key):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'email_haravan': email_haravan,
        'token_haravan': token_haravan,
        'callbot_api_key': callbot_api_key,
        'update_at': time.time()
    }})

def update_merchant_haravan_callbot(merchant_id, callbot_order_web, callbot_order_ecom, campaign_id_web, campaign_id_ecom):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'haravan': {
            'callbot_order_web': callbot_order_web,
            'callbot_order_ecom': callbot_order_ecom,
            'campaign_id_web': campaign_id_web,
            'campaign_id_ecom': campaign_id_ecom
        },
        'update_at': time.time()
    }})


def update_merchant_haravan_shop(merchant_id, haravan_domain, haravan_id_shop):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'haravan_domain': haravan_domain,
        'haravan_id_shop': haravan_id_shop,
        'update_at': time.time()
    }})

def get_all_merchants():
    return DATABASE.merchants.find()


def check_pos_id(pos_id, shop_id):
    try:
        shop_id_ = DATABASE.shop.find_one({'pos_id': pos_id}).get("_id")
        if str(shop_id_) != str(shop_id):
            return True
        else:
            return False
    except:
        return False


def check_mer_id_app(merchant_id_app, merchant_id):
    try:
        merchant_id_ = DATABASE.app_synchronized.find_one({'setting.merchant_id_app': merchant_id_app}).get(
            'merchant_id')
        if str(merchant_id_) != str(merchant_id):
            return True
        else:
            return False
    except:
        return False


def get_merchants(page, page_size=settings.ITEMS_PER_PAGE):
    return DATABASE.merchants.find().sort('when', -1).skip(
        page_size * (page - 1)).limit(page_size)


def get_merchants_by_partner_all(partner_id):
    return DATABASE.merchants.find({'partner': partner_id})


def get_merchants_count():
    return DATABASE.merchants.find().count()


def get_email_sample_template(page, page_size=settings.ITEMS_PER_PAGE):
    return DATABASE.email_sample_template.find().sort('when', -1).skip(
        page_size * (page - 1)).limit(page_size)


def get_email_sample_template_count():
    return DATABASE.email_sample_template.find().count()


def get_email_sample_template_item(email_id):
    if not isinstance(email_id, ObjectId):
        email_id = ObjectId(email_id)
    return DATABASE.email_sample_template.find_one({'_id': email_id})


def update_sample_template_item(email_id,
                                name=None,
                                thumb=None,
                                code=None,
                                design=None):
    if email_id == 'add':
        DATABASE.email_sample_template.insert({
            'name': name,
            'thumb': thumb,
            'code': code,
            'design': design,
            'when': time.time()
        })
    else:
        if not isinstance(email_id, ObjectId):
            email_id = ObjectId(email_id)
        info = {}
        if thumb:
            info['thumb'] = thumb
        if name:
            info['name'] = name
        if code:
            info['code'] = code
        if design:
            info['design'] = design
        info['when'] = time.time()
        DATABASE.email_sample_template.update({
            '_id': email_id}, {
            '$set': info
        })


def get_merchant_by_phone(phone):
    return DATABASE.merchants.find_one({'phone': phone})


def get_merchant_by_email(email):
    return DATABASE.merchants.find_one({'email': email})


def get_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.find_one({'_id': merchant_id})


def get_email_by_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    x = DATABASE.merchants.find_one({'_id': merchant_id})
    return x.get('email')


def get_merchant_by_slug(slug):
    return DATABASE.merchants.find_one({'slug': slug})


def create_shop(name,
                logo=None,
                address=None,
                background=None,
                merchant_id=None,
                facebook_page=None,
                city=None):
    info = {}
    info['name'] = name
    info['logo'] = logo
    info['address'] = address
    info['background'] = background
    info['merchant_id'] = merchant_id
    info['facebook_page'] = facebook_page
    info['created_at'] = time.time()
    info['city'] = city
    info['sms'] = {
        'welcome': {},
        'return': {},
        'loyal': {},
        'lost': {},
        'happy_birthday': {},
        'announcement': {}
    }
    info['email_template'] = {
        'welcome': {},
        'return': {},
        'loyal': {},
        'lost': {},
        'happy_birthday': {},
        'announcement': {}
    }
    shop = DATABASE.shop.insert(info)
    info_shop = get_shop_info(shop_id=shop)
    if info_shop:
        try:
            search_engine.index_shop_item(info_shop)
        except:
            pass
    return shop


def update_shop_zalo_info(shop_id,
                          zalo_oa_id=None,
                          zalo_app_id=None,
                          zalo_access_token=None):
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
    info = {}
    info['updated_at'] = time.time()
    if str(zalo_oa_id) != 'None':
        info['zalo_oa_id'] = zalo_oa_id
    if str(zalo_app_id) != 'None':
        info['zalo_app_id'] = zalo_app_id
    if str(zalo_access_token) != 'None':
        info['zalo_access_token'] = zalo_access_token
    DATABASE.shop.update({'_id': shop_id}, {'$set': info})


def update_config_channel(shop_id, all_channel, channel_list):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {'send_settings': {
        'all': all_channel,
        'top': channel_list
    }}
    DATABASE.shop.update({'_id': shop_id}, {'$set': info})


def update_shop(shop_id,
                name=None,
                phone=None,
                gateway_mac=None,
                geolocation=None,
                logo=None,
                background=None,
                facebook_page=None,
                hotline=None,
                address=None,
                email=None,
                staffs=None,
                website=None,
                page_id=None,
                emps=None,
                is_sms=None,
                sms_count=None,
                pricing_pkg=None,
                hqstaffs=None,
                merchant_id=None,
                email_order=None,
                order_per_emp=None,
                dealer_id=None,
                date_contract_start=None,
                date_contract_end=None,
                multi_gw=None,
                splash_lang=None,
                facebook_pixel_code=None,
                facebook_pixel_id=None,
                zalo_oa_id=None,
                zalo_oa_key=None,
                zalo_app_id=None,
                zalo_app_secret_key=None,
                zalo_access_token=None,
                zalo_refesh_token=None,
                auto_popup=None,
                ignore_register=None,
                address_lat=None,
                address_long=None,
                google_pixel_code=None,
                connect_button=None,
                wifi_access_code=None,
                is_radius=None,
                welcome_member_text_splash=None,
                wifi_access_code_default=None,
                hotspot_method=None,
                company_id_anvui=None,
                id_page=None,
                place_id=None,
                access_token_page=None,
                type_pos=None,
                id_app_facebook=None,
                app_facebook_secret=None,
                id_facebook_page=None,
                facebook_page_token=None,
                facebook_user_token=None,
                content_messenger=None,
                business_model=None,
                tripadvisor=None,
                tiktok_pixel_code=None,
                ga_id=None,
                pos_id=None,
                link_woay=None,
                shop_id_woay=None,
                new_camp=None,
                tags=None,
                settings_starbucks=None,
                email_report=None,
                active_report=None,
                medical_declaration=None,
                nextify_tracking_code=None,
                unifi_controller=None):
    if str(shop_id) != 'None':
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
    else:
        shop_id = None

    phone_numbers = []
    if str(phone) != 'None' and len(phone) > 0:
        phone_numbers = list(
            set([
                get_phone_number(line) for line in phone.split('\n')
                if get_phone_number(line)
            ]))

    if str(gateway_mac) != 'None' and not multi_gw:
        gateway_mac = normalize(gateway_mac) if gateway_mac else None

    info = {'phone_numbers': phone_numbers}

    if str(name) != 'None':
        info['name'] = name.strip()
        info['slug'] = slugify(info['name'])

    if str(facebook_page) != 'None':
        info['facebook_page'] = facebook_page
    if str(hotline) != 'None':
        info['hotline'] = hotline
    if str(address) != 'None':
        info['address'] = address
    if str(geolocation) != 'None':
        info['geolocation'] = geolocation
    if logo and str(logo) != 'None':
        info['logo'] = logo
    if str(email) != 'None':
        info['email'] = email
    if str(pricing_pkg) != 'None':
        info['pricing_pkg'] = pricing_pkg
    if str(merchant_id) != 'None':
        info['merchant_id'] = merchant_id
    if str(ignore_register) != 'None':
        info['ignore_register'] = ignore_register
    if str(wifi_access_code) != 'None':
        info['wifi_access_code'] = wifi_access_code
    if str(connect_button) != 'None':
        info['connect_button'] = connect_button
    if business_model and str(business_model) != 'None':
        info['business_model'] = business_model
    if place_id and str(place_id) != 'None':
        info['place_id'] = place_id
    if tripadvisor and str(tripadvisor) != 'None':
        info['tripadvisor'] = tripadvisor
    if str(facebook_pixel_code) != 'None':
        info['facebook_pixel_code'] = facebook_pixel_code
    if str(google_pixel_code) != 'None':
        info['google_pixel_code'] = google_pixel_code
    if str(tiktok_pixel_code) != 'None':
        info['tiktok_pixel_code'] = tiktok_pixel_code
    if str(facebook_pixel_id) != 'None':
        info['facebook_pixel_id'] = facebook_pixel_id
    if str(zalo_oa_id) != 'None':
        info['zalo_oa_id'] = zalo_oa_id
    if str(zalo_oa_key) != 'None':
        info['zalo_oa_key'] = zalo_oa_key
    if str(zalo_app_id) != 'None':
        info['zalo_app_id'] = zalo_app_id
    if str(zalo_app_secret_key) != 'None':
        info['zalo_app_secret_key'] = zalo_app_secret_key
    if str(zalo_access_token) != 'None':
        info['zalo_access_token'] = zalo_access_token
    if str(zalo_refesh_token) != 'None':
        info['zalo_refesh_token'] = zalo_refesh_token
    if str(ga_id) != 'None':
        info['ga_id'] = ga_id
    if str(type_pos) != 'None':
        info['type_pos'] = type_pos
    if str(link_woay) != 'None':
        info['link_woay'] = link_woay
    if str(shop_id_woay) != 'None':
        info['shop_id_woay'] = shop_id_woay
    if str(hotspot_method) != 'None':
        info['hotspot_method'] = hotspot_method
    if str(new_camp) != 'None':
        info['new_camp'] = True
    if str(email_report) != 'None':
        info['email_report'] = email_report
    if str(active_report) != 'None':
        info['active_report'] = active_report
    if unifi_controller and str('unifi_controller') != 'None' and len(str('unifi_controller')) > 0:
        info['unifi_controller'] = unifi_controller
    if str(nextify_tracking_code) != 'None':
        info['nextify_tracking_code'] = nextify_tracking_code
    info['tags'] = tags
    if str(staffs) != 'None':
        info['staffs'] = list(
            set([
                get_phone_number(line) for line in staffs.split('\n')
                if get_phone_number(line)
            ]))

    if str(emps) != 'None':
        info['emps'] = list(
            set([
                get_phone_number(line) for line in emps.split('\n')
                if get_phone_number(line)
            ]))

    if str(hqstaffs) != 'None':
        info["hqstaffs"] = list(
            set([
                get_phone_number(line) for line in hqstaffs.split('\n')
                if get_phone_number(line)
            ]))
    if str(website) != 'None':
        info['website'] = website
    if str(page_id) != 'None':
        info['page_id'] = page_id
    if str(auto_popup) != 'None':
        info['auto_popup'] = auto_popup
    if background and str(background) != 'None':
        info['background'] = background
    if str(is_sms) != 'None':
        info['is_sms'] = is_sms
    if str(sms_count) != 'None':
        info['sms_count'] = sms_count

    if str(date_contract_start) != 'None':
        info['date_contract_start'] = date_contract_start

    if str(date_contract_end) != 'None':
        info['date_contract_end'] = date_contract_end

    if str(email_order) != 'None':
        info['email_order'] = email_order

    if str(id_page) != 'None':
        info['id_page'] = id_page

    if str(access_token_page) != 'None':
        info['access_token_page'] = access_token_page

    if str(order_per_emp) != 'None':
        info['order_per_emp'] = order_per_emp

    if str(splash_lang) != 'None':
        info['splash_lang'] = splash_lang

    if str(pos_id) != 'None':
        info['pos_id'] = pos_id

    info['company_id_anvui'] = company_id_anvui
    if str(dealer_id) != 'None':
        info['dealer_id'] = dealer_id
    if str(address_lat) != 'None':
        info['address_lat'] = address_lat
    if str(address_long) != 'None':
        info['address_long'] = address_long
    if str(is_radius) != 'None':
        info['is_radius'] = is_radius
    if str(wifi_access_code_default) != 'None':
        info['wifi_access_code_default'] = wifi_access_code_default
    if str(welcome_member_text_splash) != 'None':
        info['welcome_member_text_splash'] = welcome_member_text_splash
    info['app_messenger'] = {}
    if str(id_app_facebook) != 'None':
        info['app_messenger']['id_app_facebook'] = id_app_facebook
    if str(app_facebook_secret) != 'None':
        info['app_messenger']['app_facebook_secret'] = app_facebook_secret
    if str(id_facebook_page) != 'None':
        info['app_messenger']['id_facebook_page'] = id_facebook_page
    if str(settings_starbucks) != 'None':
        info['settings_starbucks'] = settings_starbucks
    if str(facebook_page_token) != 'None':
        url1 = "https://graph.facebook.com/v6.0/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}".format(
            id_app_facebook, app_facebook_secret, facebook_page_token)
        result1 = requests.get(url=url1)
        result1 = json.loads(result1.text)
        token_page = result1.get('access_token')
        info['app_messenger']['facebook_page_token'] = token_page
    if str(facebook_user_token) != 'None':
        url = "https://graph.facebook.com/v6.0/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}".format(
            id_app_facebook, app_facebook_secret, facebook_user_token)
        result = requests.get(url=url)
        result = json.loads(result.text)
        token = result.get('access_token')
        info['app_messenger']['facebook_user_token'] = token
    if str(content_messenger) != 'None':
        info['app_messenger']['content_messenger'] = content_messenger
    if str(medical_declaration) != 'None':
        info['medical_declaration'] = medical_declaration
    if not shop_id:
        info['created_at'] = time.time()
        if gateway_mac and not multi_gw:
            info['gateway_mac'] = [gateway_mac]
        elif gateway_mac and multi_gw:
            gw_macs = []
            for gw_mac in gateway_mac:
                gw_mac = normalize(gw_mac) if gw_mac else None
                gw_macs.append(gw_mac)
            info['gateway_mac'] = gw_macs
        info['sms'] = {
            'welcome': {},
            'return': {},
            'loyal': {},
            'lost': {},
            'happy_birthday': {},
            'announcement': {}
        }
        shop = DATABASE.shop.insert(info)
        info_shop = get_shop_info(shop_id=shop)
        if info_shop:
            try:
                search_engine.index_shop_item(info_shop)
            except:
                pass
        return shop

    else:
        info['updated_at'] = time.time()
        if gateway_mac is not None and not multi_gw:
            DATABASE.shop.update(
                {
                    'gateway_mac': gateway_mac
                }, {'$pull': {
                    'gateway_mac': gateway_mac
                }},
                multi=True)

            DATABASE.shop.update({
                '_id': shop_id
            }, {'$addToSet': {
                'gateway_mac': gateway_mac
            }})
        elif gateway_mac is not None and multi_gw:
            if len(gateway_mac) == 0:
                DATABASE.shop.update({
                    '_id': shop_id
                }, {'$set': {
                    'gateway_mac': gateway_mac
                }})
            else:
                gw_macs = []
                for gw_mac in gateway_mac:
                    gw_mac = normalize(gw_mac) if gw_mac else None
                    gw_macs.append(gw_mac)
                DATABASE.shop.update({
                    '_id': shop_id
                }, {'$set': {
                    'gateway_mac': gw_macs
                }})
        try:
            DATABASE.shop.update({'_id': shop_id}, {'$set': info})
            DATABASE.shop.update({'_id': shop_id},
                                 {'$set': {'login_form.welcome_button': connect_button,
                                           'plus_login_form.welcome_button': connect_button}})
        except:
            pass
        info_shop = get_shop_info(shop_id=shop_id)
        if info_shop:
            try:
                search_engine.index_shop_item(info_shop)
            except:
                pass
        return DATABASE.shop.find_one({'_id': shop_id})


def update_login_form_shop(shop_id, login_form, plus_login_form, priority_splash, priority_splash_status,
                           hotspot_method, default_code):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {}
    info['hotspot_method'] = hotspot_method
    info['wifi_access_code_default'] = default_code
    info['login_form'] = login_form
    info['plus_login_form'] = plus_login_form
    info['priority_splash'] = priority_splash
    info['priority_splash_status'] = priority_splash_status
    info['updated_at'] = time.time()
    return DATABASE.shop.update_one({'_id': shop_id}, {'$set': info})


def get_gen_shop_by_merchant(merchant_id, page=None, page_size=settings.ITEMS_PER_PAGE):
    return DATABASE.shop.find({'merchant_id': str(merchant_id)}) \
        .sort('when', -1).skip(page_size * (int(page) - 1)) \
        .limit(page_size)


def get_shop_by_merchant(merchant_id):
    results = []
    recs = DATABASE.shop.find({'merchant_id': merchant_id})
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        results.append(rec)
    return results


def total_shop_in_merchant(merchant_id):
    return DATABASE.shop.find({'merchant_id': merchant_id}).count()


def get_shop_by_merchant_commet(merchant_id):
    results = []
    recs = DATABASE.shop.find({'merchant_id': merchant_id})
    for rec in recs:
        results.append(rec.get("_id"))
    return results


def get_shop_by_accounts(phone):
    results = []
    recs = DATABASE.accounts.find({'phone': phone})
    for rec in recs:
        shop = get_shop_info(shop_id=rec['shop_id'])
        results.append(shop)
    return results


def get_merchants_by_accounts_phone(phone):
    recs = DATABASE.accounts.find_one({'phone': phone, 'roles': '3'})
    return recs


def update_sms_count(shop_id, sms_count):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'sms_count': sms_count,
        'updated_at': time.time()
    }})


def update_pos_settings(shop_id,
                        pos_patner,
                        merchant_id,
                        pos_id=None,
                        server_hq=None,
                        user_hq=None,
                        db_hq=None,
                        pass_hq=None,
                        access_token=None,
                        pass_ipos=None,
                        pos_parent=None,
                        pos_id_ipos=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    pos_settings = {
        'pos_id': pos_id,
        'server_hq': server_hq,
        'user_hq': user_hq,
        'db_hq': db_hq,
        'pass_hq': pass_hq,
        'access_token': access_token,
        'pass_ipos': pass_ipos,
        'pos_parent': pos_parent,
        'pos_id_ipos': pos_id_ipos
    }

    return DATABASE.shop.update({
        '_id': shop_id
    }, {
        '$set': {
            'pos_patner': pos_patner,
            'merchant_id': merchant_id,
            'pos_settings': pos_settings,
            'updated_at': time.time()
        }
    })


def update_pos_id(shop_id, pos_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'pos_id': pos_id,
        'updated_at': time.time()
    }})


def remove_pos_id(pos_id):
    return DATABASE.shop.update_many({'pos_id': pos_id}, {'$set': {'pos_id': None, 'updated_at': time.time()}})


def update_sms_templates(shop_id, sms_templates):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'sms': sms_templates,
        'updated_at': time.time()
    }})


def update_sms_templates_by_type(shop_id, sms_templates, type_sms):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    key_sms = 'sms.%s' % (type_sms)
    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        key_sms: sms_templates.get(type_sms),
        'updated_at': time.time()
    }})


def update_sms_templates_active(shop_id, type_sms, active):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if type_sms == 'anoun':
        type_sms = "announcement"
    key_sms = 'sms.%s.status' % (type_sms)
    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        key_sms: active,
        'updated_at': time.time()
    }})


def update_automation_mess_method(shop_id, mar_type, mess_method, mess_value):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    key_sms = 'sms.%s.%s' % (mar_type, mess_method)
    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        key_sms: mess_value,
        'updated_at': time.time()
    }})


def update_sms_templates_hq(merchant_id, sms_templates):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'sms': sms_templates,
        'update_at': time.time()
    }})


def update_sms_templates_hq_by_type(merchant_id, sms_templates, type_sms):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    key_sms = 'sms.%s' % (type_sms)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        key_sms: sms_templates.get(type_sms),
        'update_at': time.time()
    }})


def update_email_content_sms_templates_hq_by_type(merchant_id, sms_templates,
                                                  type_sms):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    key_sms = 'email_template.{0}.email_content'.format(type_sms)
    return DATABASE.merchants.update({
        '_id': merchant_id,
    }, {'$set': {
        key_sms: sms_templates,
        'update_at': time.time()
    }})


def update_email_shop_automation(shop_id, sms_templates, type_sms):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    key_sms = 'email_template.{0}.email_content'.format(type_sms)
    return DATABASE.shop.update({
        '_id': shop_id,
    }, {'$set': {
        key_sms: sms_templates,
        'updated_at': time.time()
    }})


def user_birthday_marketing(user_phone, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.user_birthday.find_one({
        'phone': user_phone,
        'shop_id': shop_id
    })


def user_birthday_marketing_hq(user_phone, merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.user_birthday_hq.find_one({
        'phone': user_phone,
        'merchant_id': merchant_id
    })


def insert_user_birthday_marketing_hq(user_phone, merchant_id, message):
    when = time.time()
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    user = user_birthday_marketing_hq(user_phone, merchant_id)
    if user:
        DATABASE.user_birthday_hq.update({
            'phone': user_phone,
            'merchant_id': merchant_id,
            'message': message,
        }, {'$set': {
            'when': when
        }})
    else:
        return DATABASE.user_birthday_hq.insert({
            'phone': user_phone,
            'merchant_id': merchant_id,
            'when': when,
            'message': message
        })


def insert_user_birthday_marketing(user_phone, shop_id, message):
    when = time.time()
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    user = user_birthday_marketing(user_phone, shop_id)
    if user:
        DATABASE.user_birthday.update({
            'phone': user_phone,
            'shop_id': shop_id,
            'message': message
        }, {'$set': {
            'when': when
        }})
    else:
        return DATABASE.user_birthday.insert({
            'phone': user_phone,
            'shop_id': shop_id,
            'when': when,
            'message': message
        })


def update_coupon_expire(shop_id, coupon_expire):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'coupon_expire': coupon_expire,
        'updated_at': time.time()
    }})


def update_coupon_expire_hq(merchant_id, coupon_expire):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'coupon_expire': coupon_expire,
        'update_at': time.time()
    }})


def update_coupon_info(shop_id, coupon_info):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'coupon_info': coupon_info,
        'updated_at': time.time()
    }})


def update_coupon_info_hq(merchant_id, coupon_info):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'coupon_info': coupon_info,
        'update_at': time.time()
    }})


def update_coupon_active(shop_id, coupon_active):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'coupon_active': coupon_active,
        'updated_at': time.time()
    }})


def update_coupon_active_hq(merchant_id, coupon_active):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update({
        '_id': merchant_id
    }, {'$set': {
        'coupon_active': coupon_active,
        'update_at': time.time()
    }})


def update_social_info(shop_id, social_info):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'social': social_info,
        'updated_at': time.time()
    }})


def update_login_form_settings(shop_id, form_settings):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'login_form': form_settings,
        'updated_at': time.time()
    }})


def update_login_form_background(shop_id, filename):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'login_form.background': filename,
        'updated_at': time.time()
    }})


def update_plus_login_form_settings(shop_id, form_settings):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.shop.update({
        '_id': shop_id
    }, {'$set': {
        'plus_login_form': form_settings,
        'updated_at': time.time()
    }})


def search_user(keyword):
    # phone = get_phone_number(keyword)
    user = DATABASE.user.find_one({'phone': keyword})
    return user


def search_hq_user(merchant_id, keyword):
    info = {'merchant_id': str(merchant_id), 'phone': keyword}
    return DATABASE.hq_shops.find_one(info)


def get_visit_by_id(visit_id):
    if not isinstance(visit_id, ObjectId):
        visit_id = ObjectId(visit_id)

    return DATABASE.visit_log.find_one({'_id': visit_id})


def save_visit_log(user_id, shop_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    user = get_user_info(user_id=user_id)
    phone = user.get('phone')
    email = user.get('email')
    time_stamp = time.time()
    time_hour = str(datetime.fromtimestamp(time_stamp))
    hour = time_hour[11:16]
    visit_id = DATABASE.visit_log.insert({
        'phone': phone,
        'email': email,
        'user_id': user_id,
        'shop_id': shop_id,
        'timestamp': time_stamp,
        'time_hour': hour,
        'timestamp_date': datetime.fromtimestamp(time_stamp)
    })

    return visit_id


def save_visit_from_pos(user_id, shop_id, update_date):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not update_date or update_date == 'None':
        update_date = time.time()

    DATABASE.visit_log.insert({
        'user_id': user_id,
        'shop_id': shop_id,
        'timestamp': update_date,
        'timestamp_date': datetime.fromtimestamp(update_date)
    })


def save_visit_with_phone(phone, shop_id, update_date=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    user = get_user_info(phone_number=phone)
    if not update_date or update_date == 'None':
        update_date = time.time()
    # Lưu visit log (4 tiếng không có activity gì thì tính là 1 lượt visit)
    # key = '{}|{}'.format(user['_id'], shop_id)
    # if REDIS.get(key):
    #     REDIS.expire(key, 4 * 3600)  # 4 hours
    #     return False

    DATABASE.visit_log.insert({
        'phone': phone,
        'shop_id': shop_id,
        'user_id': user.get('_id'),
        'timestamp': update_date,
        'timestamp_date': datetime.fromtimestamp(update_date)
    })
    # REDIS.set(key, True)
    # REDIS.expire(key, 4 * 3600)  # 4 hours


def remove_visit_log(user_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    DATABASE.visit_log.remove({'shop_id': shop_id, 'user_id': user_id})


def get_user_vists_logs(user_id,
                        shop_id,
                        page,
                        page_size=settings.ITEMS_PER_PAGE):
    if not user_id or not shop_id:
        return None

    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    query = {'user_id': user_id, 'shop_id': shop_id}
    recs = DATABASE.visit_log.find(query).sort('timestamp', -1).skip(
        page_size * (page - 1)).limit(page_size)
    results = []
    for rec in recs:
        time_date = time.strftime("%D %H:%M",
                                  time.localtime(int(rec['timestamp'])))
        time_date_split = time_date.split(' ')
        rec['_id'] = str(rec['_id'])
        rec['user_id'] = str(rec['user_id'])
        rec['shop_id'] = str(rec['shop_id'])
        rec['time_day'] = time_date_split[0]
        rec['time_hour'] = time_date_split[1]
        rec['time_ago'] = arrow.get(rec['timestamp']).humanize(locale='vi_vn')
        results.append(rec)
    return results


def get_user_vists_logs_phone(user_id,
                              shop_id,
                              page,
                              page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    query = {'phone': user_id, 'shop_id': shop_id}
    recs = DATABASE.visit_log.find(query).sort('timestamp', -1).skip(
        page_size * (page - 1)).limit(page_size)
    results = []
    for rec in recs:
        time_date = time.strftime("%D %H:%M",
                                  time.localtime(int(rec['timestamp'])))
        time_date_split = time_date.split(' ')
        rec['_id'] = str(rec['_id'])
        rec['phone'] = str(rec['phone'])
        rec['shop_id'] = str(rec['shop_id'])
        rec['time_day'] = time_date_split[0]
        rec['time_hour'] = time_date_split[1]
        rec['time_ago'] = arrow.get(rec['timestamp']).humanize(locale='vi_vn')
        results.append(rec)
    return results


def get_visit_phone(phone, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    query = {'phone': phone, 'shop_id': shop_id}

    return DATABASE.visit_log.find(query).count()


def get_visit_by_user_id(user_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    query = {'user_id': user_id, 'shop_id': shop_id}

    return DATABASE.visit_log.find(query)


def get_user_activity_visit(user_id,
                            shops,
                            page,
                            page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    query = {'user_id': user_id, 'shop_id': {'$in': shops}}
    recs = DATABASE.visit_log.find(query).sort('timestamp', -1).skip(
        page_size * (page - 1)).limit(page_size)
    shop = shops[0]
    shop_info = get_shop_info(shop_id=shop)
    merchant_id = shop_info.get('merchant_id')
    results = []
    for rec in recs:
        user_id = rec.get('user_id')
        user = handle_customers.get_user_merchant_by_user_id(
            merchant_id, user_id)
        if not user:
            user = get_user_info(user_id=user_id)
        else:
            user = user.get('user', {})
        if user:
            time_date = time.strftime("%D %H:%M",
                                      time.localtime(int(rec['timestamp'])))
            time_date_split = time_date.split(' ')
            rec['_id'] = str(rec['_id'])
            rec['phone'] = str(user.get('phone'))
            rec['shop_id'] = str(rec['shop_id'])
            shop = get_shop_info(shop_id=rec['shop_id'])
            rec['shop_name'] = shop['name']
            # rec['time_day'] = time_date_split[0]
            day = time_date_split[0].split('/')
            rec['time_day'] = day[1] + '/' + day[0] + '/' + day[2]
            # time_hour = time_date_split[1].split(':')
            # rec['time_hour'] = str(int(time_hour[0]) + 7) + ':' + time_hour[1]
            rec['time_hour'] = time_date_split[1]
            rec['time_ago'] = arrow.get(
                rec['timestamp']).humanize(locale='vi_vn')
            results.append(rec)
    return results


def get_user_activity_visit_count(user_id, shops, time_ranges=None):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    query = {'user_id': user_id, 'shop_id': {'$in': shops}}
    if time_ranges:
        query['timestamp'] = {'$gte': time_ranges['from']}
        query['timestamp'] = {'$lte': time_ranges['to']}

    return DATABASE.visit_log.find(query).count()


def get_user_merchant_by_id(merchant_id, user_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    return DATABASE.customers.find_one({
        'merchant_id': merchant_id,
        'user_id': user_id
    })


def get_last_send_log(user_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    result = DATABASE.send_activity_log.find(
        {'customer_id': user_id, 'result': True}).sort('when', -1).limit(1)
    kq = [item for item in result]
    if len(kq) == 0:
        return False
    else:
        when = kq[0].get('when')
        return when


def get_user_shop_by_id(shop_id, user_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    return DATABASE.customers_location.find_one({
        'shop_id': shop_id,
        'user_id': user_id
    })


def get_visit_phone_hq(phone, merchant_id):
    shop_mer = get_shop_by_merchant(merchant_id)
    counts = 0
    for shop_in_mer in shop_mer:
        count = get_visit_phone(phone, shop_in_mer['_id'])
        counts += count
    return counts


def get_visit_count(user_id, shop_id, all=None):
    if not user_id or not shop_id:
        return None

    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    query = {'user_id': user_id, 'shop_id': shop_id}
    if not all:
        query['timestamp'] = {'$gte': time.time() - 30 * 86400}

    return DATABASE.visit_log.find(query).count()


def get_visit_count_hq(user_id, merchant_id, all=None):
    if not user_id or not merchant_id:
        return None

    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    merchant = get_merchant(merchant_id)
    shops = get_shop_by_merchant(merchant_id)
    user = get_user_info(user_id=user_id)
    total_visit = 0
    for shop in shops:
        shop_id = shop['_id']
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        query = {'user_id': user_id, 'shop_id': shop_id}
        if not all:
            query['timestamp'] = {'$gte': time.time() - 30 * 86400}

        total_visit += int(DATABASE.visit_log.find(query).count())
    return total_visit


def get_last_visit(user_id, shop_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    query = {'user_id': user_id, 'shop_id': shop_id}
    records = \
        list(DATABASE.visit_log.find(query).sort('timestamp', -1).limit(1))
    if records:
        return records[0]['timestamp']


def get_users(first_visit=None, last_visit=None, visit_count=None):
    pass


def deactive_other_event(shop_id, event_id, active):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(event_id, ObjectId):
        event_id = ObjectId(event_id)

    if active == "1":
        list_db = DATABASE.event.find({
            '_id': {
                '$ne': event_id
            },
            'shop_id': shop_id
        })
        for item in list_db:
            DATABASE.event.update(
                {
                    '_id': item["_id"]
                }, {'$set': {
                    "active": "0"
                }}, upsert=True)


def add_event(shop_id, title, content, photo, slug, active, name, link_share,
              social):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    info = {
        'shop_id': shop_id,
        'title': title,
        'content': content,
        'photo': photo,
        'timestamp': time.time(),
        'slug': slug,
        'active': active,
        'name': name,
        'link_share': link_share,
        'type': social
    }

    return DATABASE.event.insert(info)


def update_event(shop_id, event_id, title, content, photo, slug, active, name,
                 link_share, social):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(event_id, ObjectId):
        event_id = ObjectId(event_id)

    info = {
        'shop_id': shop_id,
        'title': title,
        'content': content,
        'photo': photo,
        'timestamp': time.time(),
        'slug': slug,
        'active': active,
        'name': name,
        'link_share': link_share,
        'type': social
    }

    if photo:
        info['photo'] = photo

    return DATABASE.event.update({
        '_id': event_id,
        'shop_id': shop_id
    }, {'$set': info})


def change_event_status(shop_id, event_id, status):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(event_id, ObjectId):
        event_id = ObjectId(event_id)

    return DATABASE.event.update({
        '_id': event_id,
        'shop_id': shop_id
    }, {'$set': {
        "active": status
    }})


def get_event(shop_id, event_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(event_id, ObjectId):
        event_id = ObjectId(event_id)

    return DATABASE.event.find_one({'_id': event_id, 'shop_id': shop_id})


def get_event_active(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.event.find_one({'active': "1", 'shop_id': shop_id})


def get_events(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return list(
        DATABASE.event.find({
            'shop_id': shop_id
        }).sort('timestamp', -1))


def get_cards(shop_id, mar_filter=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {'shop_id': shop_id}
    if mar_filter and mar_filter != 'default':
        info['auto_mar'] = mar_filter
    return list(DATABASE.card.find(info).sort('timestamp', -1))


def get_card_auto_mar(shop_id, type_mess):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.card.find_one({'shop_id': shop_id, 'auto_mar': type_mess})


def add_card(shop_id, title, content, photo, slug, price, auto_mar,
             link_share):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    info = {
        'shop_id': shop_id,
        'title': title,
        'content': content,
        'photo': photo,
        'timestamp': time.time(),
        'slug': slug,
        'price': price,
        'auto_mar': auto_mar,
        'link_share': link_share
    }

    return DATABASE.card.insert(info)


def remove_card_new_portal(card_id):
    if not isinstance(card_id, ObjectId):
        card_id = ObjectId(card_id)
    DATABASE.card_new_portal.remove({'_id': card_id})


def get_card_new_portal_by_card(card_id):
    if not isinstance(card_id, ObjectId):
        card_id = ObjectId(card_id)
    item = DATABASE.card_new_portal.find_one({'_id': card_id})
    return item.get('shop_id')


def get_card_new_portal(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    card_new_portal = DATABASE.card_new_portal.find({'shop_id': shop_id})
    cards = []
    if card_new_portal.count() > 0:
        for card in card_new_portal:
            cards.append(card)
    if len(cards) < 6:
        for i in range(0, 6 - len(cards)):
            cards.append("")
    return cards


def add_card_new_portal(shop_id, title, content, photo, slug, price, auto_mar,
                        link_share):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    info = {
        'shop_id': shop_id,
        'title': title,
        'content': content,
        'photo': photo,
        'timestamp': time.time(),
        'slug': slug,
        'price': price,
        'auto_mar': auto_mar,
        'link_share': link_share
    }

    return DATABASE.card_new_portal.insert(info)


def update_card(shop_id, card_id, title, content, photo, slug, price, auto_mar,
                link_share):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(card_id, ObjectId):
        card_id = ObjectId(card_id)

    info = {
        'shop_id': shop_id,
        'title': title,
        'content': content,
        'timestamp': time.time(),
        'slug': slug,
        'price': price,
        'auto_mar': auto_mar,
        'link_share': link_share
    }

    if photo:
        info['photo'] = photo

    return DATABASE.card.update({'_id': card_id}, {'$set': info})


def get_card(shop_id, card_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(card_id, ObjectId):
        card_id = ObjectId(card_id)

    return DATABASE.card.find_one({'_id': card_id, 'shop_id': shop_id})


def get_card_by_slug(shop_id, card_slug):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.card.find_one({'slug': card_slug, 'shop_id': shop_id})


def remove_card(shop_id, card_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(card_id, ObjectId):
        card_id = ObjectId(card_id)

    return DATABASE.card.remove({'_id': card_id, 'shop_id': shop_id})


def remove_cards(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.card.remove({'shop_id': shop_id})


def get_shop_visit_log(shop_id, page, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    shop = DATABASE.shop.find_one({'_id': shop_id}, {'staffs': True})
    records = DATABASE.visit_log.find({'shop_id': shop_id}) \
        .sort('timestamp', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)
    visit_log = []
    for record in records:
        record['_id'] = str(record['_id'])
        record['user'] = get_user_info(user_id=record['user_id'])
        record['user_id'] = str(record['user_id'])
        record['shop_id'] = str(record['shop_id'])
        if record['user']:
            record['user']['_id'] = str(record['user']['_id'])
            if record['user']['phone'] in shop.get('staffs', []):
                continue
            record['timestamp_str'] = arrow.get(record['timestamp']).humanize(
                locale='vi_vn')
            if 'birthday' in record['user']:
                record['user']['birthday'] = str(record['user']['birthday'])
            visit_log.append(record)

    return visit_log


def update_history_trans_credit(merchant_id, shop_id, user_id, real_credit,
                                sale, type):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    return DATABASE.history_trans_credit.insert({
        'merchant_id': merchant_id,
        'shop_id': shop_id,
        'credit': real_credit,
        'sale': sale,
        'type': type,
        'user_id': user_id,
        'when': time.time()
    })


def total_list_history_trans_by_user(merchant_id,
                                     user_id,
                                     page=None,
                                     page_size=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    info = {'merchant_id': merchant_id, 'user_id': user_id}
    return DATABASE.history_trans_credit.find(info).sort('when', -1).count()


def list_history_trans_by_user(merchant_id, user_id, page=None,
                               page_size=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    info = {'merchant_id': merchant_id, 'user_id': user_id}
    response = []
    trans = DATABASE.history_trans_credit.find(info).sort('when', -1).skip(
        page_size * (page - 1)).limit(page_size)
    for tran in trans:
        shop = get_shop_info(shop_id=tran['shop_id'])
        user = get_user_info(user_id=tran['user_id'])
        tran['shop'] = shop
        tran['user'] = user
        response.append(tran)
    return response


def list_history_trans_credit(merchant_id,
                              shop_id,
                              typef,
                              from_date=None,
                              to_date=None,
                              phone=None,
                              page=None,
                              min_cash=None,
                              max_cash=None,
                              shop_order=None,
                              page_size=None):
    response = []
    trans = []
    if merchant_id and merchant_id != '0':
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        info = {'merchant_id': merchant_id}
        if typef:
            info['type'] = typef
        info_when = {}
        if from_date and from_date != 'None':
            from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
                replace(hour=1, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())
            info_when['$gte'] = from_tmp

        if to_date and to_date != 'None':
            to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
                replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            info_when['$lte'] = to_tmp
        if len(info_when) > 0:
            info['when'] = info_when
        if shop_order and len(shop_order) > 0 and str(shop_order) != 'None':
            if not isinstance(shop_order, ObjectId):
                shop_order = ObjectId(shop_order)
            info['shop_id'] = shop_order
        if phone and len(phone) > 0 and str(phone) != 'None':
            user = get_user_info(phone_number=phone)
            info['user_id'] = user.get('_id')
        info_credit = {}
        if min_cash and len(min_cash) > 0:
            try:
                min_cash = int(min_cash)
                info_credit['$gte'] = int(min_cash)
            except Exception as e:
                print(e.message)
        if max_cash and len(max_cash) > 0:
            try:
                max_cash = int(max_cash)
                info_credit['$lte'] = int(max_cash)
            except Exception as e:
                print(e.message)
        if len(info_credit) > 0:
            info['credit'] = info_credit
        if typef == 'redeem':
            trans = DATABASE.history_trans_credit.find(info).sort(
                'when', -1).skip(page_size * (page - 1)).limit(page_size)
        else:
            trans = DATABASE.history_trans_credit.find(info).sort(
                'sale.UpdateDate', -1).skip(page_size *
                                            (page - 1)).limit(page_size)
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        info = {'shop_id': shop_id}
        if typef:
            info['type'] = typef
        info_when = {}
        if from_date and from_date != 'None':
            from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
                replace(hour=1, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())
            info_when['$gte'] = from_tmp

        if to_date and to_date != 'None':
            to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
                replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            info_when['$lte'] = to_tmp
        if len(info_when) > 0:
            info['when'] = info_when
        if shop_order and len(shop_order) > 0 and str(shop_order) != 'None':
            if not isinstance(shop_order, ObjectId):
                shop_order = ObjectId(shop_order)
            info['shop_id'] = shop_order
        if phone and len(phone) > 0 and str(phone) != 'None':
            user = get_user_info(phone_number=phone)
            info['user_id'] = user.get('_id')
        info_credit = {}
        if min_cash and len(min_cash) > 0:
            try:
                min_cash = int(min_cash)
                info_credit['$gte'] = int(min_cash)
            except Exception as e:
                print(e.message)
        if max_cash and len(max_cash) > 0:
            try:
                max_cash = int(max_cash)
                info_credit['$lte'] = int(max_cash)
            except Exception as e:
                print(e.message)
        if len(info_credit) > 0:
            info['credit'] = info_credit
        if typef == 'redeem':
            trans = DATABASE.history_trans_credit.find(info).sort(
                'when', -1).skip(page_size * (page - 1)).limit(page_size)
        else:
            trans = DATABASE.history_trans_credit.find(info).sort(
                'sale.UpdateDate', -1).skip(page_size *
                                            (page - 1)).limit(page_size)
    for tran in trans:
        shop = get_shop_info(shop_id=tran['shop_id'])
        user = get_user_info(user_id=tran['user_id'])
        tran['shop'] = shop
        tran['user'] = user
        response.append(tran)
    return response


def get_shop_visit_count(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.visit_log.find({'shop_id': shop_id}).count()


def get_shop_visit_count_today(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    today = datetime(datetime.now().year,
                     datetime.now().month, datetime.now().day)
    time_today = time.mktime(today.timetuple())
    return DATABASE.visit_log.find({
        'shop_id': shop_id,
        'timestamp': {
            '$gte': time_today
        }
    }).count()


def get_sms_log(shop_id, page, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    records = DATABASE.sms_log.find({'shop_id': shop_id}) \
        .sort('timestamp', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)
    return list(records)


def get_sms_count(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.sms_log.find({'shop_id': shop_id}).count()


def get_sms_log_hq(merchant_id, page, page_size=settings.ITEMS_PER_PAGE):
    records = DATABASE.sms_log.find({'merchant_id': merchant_id}) \
        .sort('timestamp', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)
    sms_log = []
    for rec in records:
        last_visit = rec["timestamp"]
        local = pytz.timezone("Asia/Bangkok")
        timestamp = datetime.fromtimestamp(last_visit)
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        naive = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        rec["timestamp_str"] = arrow.get(utc_dt).humanize(locale='vi_vn')
        sms_log.append(rec)
    return sms_log


def user_must_not_in_sms_log_today_hq(merchant_id, phone):
    date_start = datetime.strptime(date.today().strftime("%Y-%m-%d"),
                                   '%Y-%m-%d').replace(
        hour=1, minute=00, second=00)
    time_start = time.mktime(date_start.timetuple())
    date_end = datetime.strptime(date.today().strftime("%Y-%m-%d"),
                                 '%Y-%m-%d').replace(
        hour=23, minute=59, second=59)
    time_end = time.mktime(date_end.timetuple())

    return DATABASE.sms_log.find_one({
        'merchant_id': merchant_id,
        'phone_number': phone,
        'timestamp': {
            '$gte': time_start,
            '$lte': time_end
        }
    })


def get_sms_count_hq(merchant_id, from_date=None, to_date=None):
    query = {'merchant_id': merchant_id}
    query_timestamp = {}
    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=1, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        query_timestamp['$gte'] = from_tmp

    if to_date and to_date != 'None':
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        query_timestamp['$lte'] = to_tmp
    if len(query_timestamp) > 0:
        query['timestamp'] = query_timestamp
    return DATABASE.sms_log.find(query).count()


def extract_coupon_code(sms_message):
    sms_message = ''.join(c for c in sms_message if c.isalnum() or c == ' ')
    words = sms_message.split()
    coupons = set()
    for i in range(1, len(words)):
        word = words[i]

        # Mã coupon là mã viết HOA, đứng độc lập,
        # không liền với các chữ HOA khác
        if word.isupper() and \
                not words[i - 1].isupper() and \
                not words[i + 1].isupper():
            coupons.add(word)

    if len(coupons) == 1:
        coupon_code = list(coupons)[0]
        return coupon_code


def add_coupon_code(user_id, shop_id, coupon_code, detail, type_message,
                    expire):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    code_unique = gen_random_coupon(shop_id)

    coupon_random = coupon_code + code_unique[0]["code"]

    info = {
        'user_id': user_id,
        'shop_id': shop_id,
        'coupon': coupon_random,
        "coupon_type": type_message
    }
    if detail:
        info['detail'] = detail
    coupon = DATABASE.coupon.find_one(info)
    expire_time = time.time() + int(expire) * 86400
    if coupon:
        info['last_updated'] = time.time()
        info['expire_time'] = expire_time
        DATABASE.coupon.update({'_id': coupon['_id']}, {'$set': info})
    else:
        info['created_at'] = time.time()
        info['expire_time'] = expire_time
        DATABASE.coupon.insert(info)
    return coupon_random


def add_coupon_code_hq(user_id, merchant_id, coupon_code, detail, type_message,
                       expire):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    code_unique = gen_random_coupon(merchant_id, is_hq=True)

    coupon_random = coupon_code + code_unique[0]["code"]

    info = {
        'user_id': user_id,
        'merchant_id': merchant_id,
        'coupon': coupon_random,
        "coupon_type": type_message
    }
    if detail:
        info['detail'] = detail
    coupon = DATABASE.coupon.find_one(info)
    expire_time = time.time() + int(expire) * 86400
    if coupon:
        info['last_updated'] = time.time()
        info['expire_time'] = expire_time
        DATABASE.coupon.update({'_id': coupon['_id']}, {'$set': info})
    else:
        info['created_at'] = time.time()
        info['expire_time'] = expire_time
        DATABASE.coupon.insert(info)
    return coupon_random


def get_coupon_codes(user_id, shop_id):
    date_end = datetime.strptime(date.today().strftime("%Y-%m-%d"),
                                 '%Y-%m-%d').replace(
        hour=23, minute=59, second=59)
    time_end = time.mktime(date_end.timetuple())

    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    records = DATABASE.coupon.find({
        'shop_id': shop_id,
        'user_id': user_id,
        'redeemed': {
            '$ne': True
        },
        'expire_time': {
            '$gte': time_end
        }
    })

    coupons = []
    for record in records:
        record[''] = ''
        record['_id'] = str(record['_id'])
        record['user_id'] = str(record['user_id'])
        record['shop_id'] = str(record['shop_id'])
        record['expire_str'] = arrow.get(record['expire_time']). \
            format('DD-MM-YYYY')
        record['create_str'] = arrow.get(record['created_at']).humanize(
            locale='vi_vn')
        coupons.append(record)

    return coupons


def get_coupon_by_shop(shop_id,
                       coupon_type,
                       page,
                       page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    date_end = datetime.strptime(date.today().strftime("%Y-%m-%d"),
                                 '%Y-%m-%d').replace(
        hour=23, minute=59, second=59)
    time_end = time.mktime(date_end.timetuple())
    info = {
        'shop_id': ObjectId(shop_id),
        'redeemed': {
            '$ne': True
        },
        'expire_time': {
            '$gte': time_end
        }
    }
    if coupon_type and coupon_type != "all":
        info['coupon_type'] = coupon_type

    records = DATABASE.coupon.find(info).sort('created_at', -1).skip(
        page_size * (page - 1)).limit(page_size)

    coupons = []
    for record in records:
        record[''] = ''
        user = get_user_info(user_id=record['user_id'])
        if user:
            record['shop_id'] = str(record['shop_id'])
            record['_id'] = str(record['_id'])
            record['user'] = user
            record['user']['_id'] = str(record['user']['_id'])
            record['create_str'] = time.strftime(
                "%D %H:%M", time.localtime(int(record['created_at'])))

            record['expire_str'] = time.strftime(
                "%D", time.localtime(int(record['expire_time'])))
            coupons.append(record)

    return coupons


def get_coupon_code(shop_id, coupon_code):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    coupon = DATABASE.coupon.find_one({
        'shop_id': shop_id,
        'redeemed': {
            '$ne': True
        },
        'coupon': coupon_code
    })

    if coupon:
        user = get_user_info(user_id=coupon['user_id'])
        coupon['user'] = user
        coupon['create_str'] = arrow.get(coupon['created_at']).humanize(
            locale='vi_vn')

    return coupon


def get_coupon_redeem_by_shop(shop_id, page,
                              page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    records = DATABASE.coupon.find({
        'shop_id': ObjectId(shop_id),
        'redeemed': True
    }).sort('created_at', -1).skip(page_size * (page - 1)).limit(page_size)

    coupons = []
    for record in records:
        record[''] = ''
        user = get_user_info(user_id=record['user_id'])
        record['user'] = user
        if user:
            record['shop_id'] = str(record['shop_id'])
            record['user_id'] = str(record['user_id'])
            record['_id'] = str(record['_id'])
            record['user'] = user
            record['user']['_id'] = str(record['user']['_id'])
            if 'redeemed_at' in record:
                record['redeemed_str'] = time.strftime(
                    "%D %H:%M", time.localtime(int(record['redeemed_at'])))

            record['create_str'] = time.strftime(
                "%D %H:%M", time.localtime(int(record['created_at'])))
            coupons.append(record)
    return coupons


def total_coupon_shop(shop_id, coupon_type):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    date_end = datetime.strptime(date.today().strftime("%Y-%m-%d"),
                                 '%Y-%m-%d').replace(
        hour=23, minute=59, second=59)
    time_end = time.mktime(date_end.timetuple())
    info = {
        'shop_id': ObjectId(shop_id),
        'redeemed': {
            '$ne': True
        },
        'expire_time': {
            '$gte': time_end
        }
    }
    if coupon_type and coupon_type != "all":
        info['coupon_type'] = coupon_type
    results = []
    records = DATABASE.coupon.find(info)
    for record in records:
        if get_user_info(user_id=record['user_id']):
            results.append(record['_id'])

    return len(results)


def total_coupon_redeem_shop(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    records = DATABASE.coupon.find({
        'shop_id': shop_id,
        'redeemed': True
    }).count()

    return records


def redeem_coupon(user_id, shop_id, coupon_code, phone_emp=None):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    info = {'user_id': user_id, 'shop_id': shop_id, 'coupon': coupon_code}
    now = time.time()
    return DATABASE.coupon.update(info, {
        '$set': {
            'redeemed': True,
            'redeemed_at': now,
            'redeem_by': phone_emp
        }
    })


def update_emp_redeem_coupon(shop_id, coupon_id, phone_emp):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(coupon_id, ObjectId):
        coupon_id = ObjectId(coupon_id)
    info = {'shop_id': shop_id, '_id': coupon_id}
    return DATABASE.coupon.update(info, {'$set': {'redeem_by': phone_emp}})


def insert_lead_merchant(name, store, phone, email):
    when = time.time()
    return DATABASE.lead_merchant.insert({
        "name": name,
        "store": store,
        "phone": phone,
        "email": email,
        "when": when
    })


def list_lead_merchant(page, page_size=settings.ITEMS_PER_PAGE):
    records = DATABASE.lead_merchant.find({}).sort('when', -1).skip(
        page_size * (page - 1)).limit(page_size)
    merchants = []
    for record in records:
        item = {}
        item["info"] = record
        item["timestamp_str"] = arrow.get(record['when']).humanize(
            locale='vi_vn')
        merchants.append(item)
    return merchants


def list_lead_merchant_count():
    return DATABASE.lead_merchant.count()


def gen_random_coupon(shop_id, is_hq=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if is_hq:
        list_code = DATABASE.random_code.find({'merchant_id': shop_id})
        codes = [code['code'] for code in list_code]
        code_done = True
        while code_done:
            code = '{:04d}'.format(random.randint(0, 9999))
            if code not in codes:
                when = time.time()
                DATABASE.random_code.insert({
                    'merchant_id': shop_id,
                    'code': code,
                    'when': when
                })
                code_done = False
                break
        return DATABASE.random_code.find({
            'merchant_id': shop_id
        }).limit(1).sort('when', -1)
    else:
        list_code = DATABASE.random_code.find({'shop_id': shop_id})
        codes = [code['code'] for code in list_code]
        code_done = True
        while code_done:
            code = '{:04d}'.format(random.randint(0, 9999))
            if code not in codes:
                when = time.time()
                DATABASE.random_code.insert({
                    'shop_id': shop_id,
                    'code': code,
                    'when': when
                })
                code_done = False
                break
        return DATABASE.random_code.find({
            'shop_id': shop_id
        }).limit(1).sort('when', -1)


def get_visit_group_by_date(shop_id, days=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not days:
        days = 30

    records = DATABASE.visit_log.find({
        'shop_id': shop_id,
        'timestamp': {
            '$gte': time.time() - days * 86400
        }
    })
    recs = []
    list_date = []
    for _rec in records:
        _rec['date_string'] = datetime.fromtimestamp(int(_rec[
            'timestamp'])).strftime('%d-%m-%Y')
        list_date.append(_rec['date_string'])
        recs.append(_rec)
    counter_visit = collections.Counter([d['date_string'] for d in recs])
    counter_visit_sort = sorted(
        list(counter_visit.items()), key=lambda i: i[0])
    list_visit = []
    for date_str in counter_visit_sort:
        list_visit.append(list(date_str))
    return list_visit


def get_visit_log_report(shop_id, prev_month=None, days=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not days:
        days = 30

    info = {'shop_id': shop_id}
    if not prev_month:
        info['timestamp'] = {'$gte': time.time() - days * 86400}
    else:
        info['timestamp'] = {
            '$lte': time.time() - days * 86400,
            '$gte': time.time() - days * 2 * 86400
        }

    total_visit = DATABASE.visit_log.find(info).count()

    query = [{
        '$match': info
    }, {
        '$group': {
            "_id": '$user_id',
            "lastvisit": {
                '$last': "$timestamp"
            },
            "count": {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            "lastvisit": -1
        }
    }, {
        '$match': {
            "count": 1
        }
    }]
    recs = DATABASE.visit_log.aggregate(query, allowDiskUse=True)
    new_visit = len(list(recs))
    return_visit = total_visit - new_visit

    return total_visit, new_visit, return_visit


def get_old_customer_report(shop_id, days=30):
    recs = DATABASE.visit_log.aggregate(
        [{
            '$match': {
                'shop_id': shop_id,
                'timestamp': {
                    '$lte': time.time() - days * 86400
                }
            }
        }, {
            '$group': {
                "_id": '$user_id'
            }
        }, {
            '$limit': 5
        }],
        allowDiskUse=True)

    users = []
    for rec in recs:
        users.append(get_user_info(rec["_id"]))

    return users


def list_customers(shops,
                   shop_id,
                   merchant_id,
                   from_date=None,
                   to_date=None,
                   min_visit=None,
                   max_visit=None,
                   sort=None,
                   bday_from_date=None,
                   bday_to_date=None,
                   ranks=None,
                   gender=None,
                   is_zalo=None,
                   filter_tags=None,
                   min_cash=None,
                   max_cash=None,
                   min_points=None,
                   max_points=None,
                   page=None,
                   page_size=None):
    # if not isinstance(shop_id, ObjectId):
    #     shop_id = ObjectId(shop_id)

    shop = get_shop_info(shop_id=shop_id)
    isHQ = True if merchant_id and merchant_id != '0' else False
    info_match = {}
    info_group_match = {}
    info_match['$match'] = {'shop_id': {'$in': shops}}
    info_group_match['$match'] = {}

    if from_date and from_date != 'None':
        if not 'timestamp' in info_match['$match']:
            info_match['$match']['timestamp'] = {}
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        info_match['$match']['timestamp']['$gte'] = from_tmp

    if to_date and to_date != 'None':
        if not 'timestamp' in info_match['$match']:
            info_match['$match']['timestamp'] = {}
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        info_match['$match']['timestamp']['$lte'] = to_tmp

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        if not 'count' in info_group_match['$match']:
            info_group_match['$match']['count'] = {}
        info_group_match['$match']['count']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0:
        if not 'count' in info_group_match['$match']:
            info_group_match['$match']['count'] = {}
        info_group_match['$match']['count']['$lte'] = int(max_visit)

    info_sort = {}
    if sort == 'time_asc':
        info_sort = {'$sort': {"lastvisit": -1}}
    elif sort == 'time_desc':
        info_sort = {'$sort': {"lastvisit": 1}}
    elif sort == 'visit_asc':
        info_sort = {'$sort': {"count": -1}}
    else:
        info_sort = {'$sort': {"count": 1}}

    look_up_user = {
        '$lookup': {
            "from": "user",
            "localField": "_id",
            "foreignField": "_id",
            "as": "user"
        }
    }
    info_birthday_match = {}
    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)

        info_birthday_match = {'$match': {'user.birthday': {'$in': days}}}

    query = [
        info_match, {
            '$sort': {
                "timestamp": -1
            }
        }, {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$max': '$timestamp_date'
                },
                "count": {
                    '$sum': 1
                },
                'averageIndex': {
                    '$avg': "_id"
                }
            }
        }, info_sort, info_group_match
    ]

    query.append(look_up_user)
    if len(look_up_user) > 0 and len(info_birthday_match) > 0:
        query.append(info_birthday_match)
    if gender and len(gender) > 0 and str(gender) != 'None':
        info_gender_match = {'$match': {'user.gender': {'$in': gender}}}
        query.append(info_gender_match)
    if filter_tags and len(filter_tags) > 0:
        look_up_user_tags = {
            '$lookup': {
                "from": "user_tags",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "user_tags"
            }
        }

        info_tags_match = {'$match': {'user_tags.tags': {'$in': filter_tags}}}
        query.append(look_up_user_tags)
        query.append(info_tags_match)

    if ranks and str(ranks) != 'None' and str(ranks) != 'all':
        info_ranks = {
            '$lookup': {
                "from": "loyalty_point",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "loyalty"
            }
        }

    if page:
        if not page_size:
            page_size = settings.ITEMS_PER_PAGE
        query.append({'$skip': page_size * (page - 1)})
        query.append({'$limit': page_size})
    recs = [
        rec for rec in DATABASE.visit_log.aggregate(
            query, allowDiskUse=True)
    ]
    users = []
    for rec in recs:
        user_info = get_user_info(user_id=rec["_id"])
        if user_info:
            user_info['_id'] = str(user_info['_id'])
            phone = user_info.get('phone')
            last_visit = rec["lastvisit"]
            local = pytz.timezone("Asia/Bangkok")
            last_visit_arr = str(last_visit).split('.')
            naive = datetime.strptime(last_visit_arr[0], "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            user_info["timestamp_str"] = arrow.get(utc_dt).humanize(
                locale='vi_vn')
            user_info['local_visit'] = utc_dt
            user_info['lastvisit'] = rec['lastvisit']
            birthday = ''
            if user_info.get('birthday') and len(user_info.get(
                    'birthday')) > 0 and user_info.get('birthday') != 'None':
                birthday_arr = user_info['birthday'].split('-')
                if len(birthday_arr) == 2:
                    birthday = birthday_arr[1].lstrip("0") + '-' + \
                        birthday_arr[0].lstrip("0")
                    if user_info.get('year_birthday') and len(
                            user_info.get('year_birthday')) > 0 \
                            and str(user_info.get('year_birthday')) != 'None':
                        birthday = birthday + '-' + \
                            str(user_info.get('year_birthday'))

            shops = get_shop_by_merchant(merchant_id)
            total_sales = 0
            if isHQ:
                for shop in shops:
                    shop_total_sales = 0
                    shop_sales = get_total_sales_user(shop['_id'],
                                                      user_info['phone'])
                    if shop_sales:
                        shop_total_sales = shop_sales.get('total_sales')
                    total_sales += shop_total_sales

            total_sales_shop = 0
            sales_shop = get_total_sales_user(shop_id, user_info['phone'])
            if sales_shop:
                total_sales_shop = sales_shop.get('total_sales')
            user_info['birthday'] = birthday
            visit_count = get_visit_phone(user_info['phone'], shop_id)
            user_info['total_sales'] = total_sales
            user_info['total_sales_shop'] = total_sales_shop
            user_info['visit_count'] = rec['count']

            is_zalo_follow = get_user_zalo_oa(user_info['_id'], shop_id)
            zalo = True if is_zalo_follow else False
            user_info['zalo'] = zalo
            user_tags_details = []
            user_tags = get_user_tags(merchant_id, rec["_id"])
            if user_tags:
                user_tag = user_tags.get('tags')
                if len(user_tags) > 0:

                    for tag in user_tag:
                        tag_db = get_tag_by_tag_id(merchant_id, tag)
                        if tag_db:
                            user_tags_details.append(tag_db)
            user_info['user_tags_details'] = user_tags_details
            users.append(user_info)

    return users


def remove_customers_visit(merchant_id, user_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    shop_in_mer = get_shop_by_merchant(str(merchant_id))
    for shop_mer in shop_in_mer:
        if not isinstance(shop_mer['_id'], ObjectId):
            shop_mer['_id'] = ObjectId(shop_mer['_id'])

        remove_customers_location_visit(shop_mer['_id'], user_id)
    DATABASE.customers.remove({
        'merchant_id': merchant_id,
        'user_id': user_id
    })
    DATABASE.user_tags.remove({
        'merchant_id': merchant_id,
        'user_id': user_id
    })


def save_splash_page_tags(
        merchant_id=None,
        tag_name=None,
        shop_id=None,
        settings=settings,
        tag_id=None,
        tag_type=None
):
    when = time.time()
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.tag_for_gr_user.insert({
        'merchant_id': merchant_id,
        'tag_name': tag_name,
        'tag_id': tag_id,
        'shop_id': shop_id,
        'create_at': when,
        'update_at': when,
        'settings': settings,
        'tag_type': tag_type
    })
    return True


def get_splash_page_tag(tag_id=None, shop_id=None):
    if shop_id and tag_id:
        return DATABASE.tag_for_gr_user.find_one({'tag_id': tag_id, 'shop_id': ObjectId(shop_id)})
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.tag_for_gr_user.find({'shop_id': shop_id})


def update_splash_page_tags(
        tag_id,
        shop_id=None,
        tag_name=None,
        settings=settings,
        tag_type=None
):
    when = time.time()
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.tag_for_gr_user.update({'tag_id': tag_id, 'shop_id': shop_id},
                                    {'$set': {'settings': settings,
                                              'tag_type': tag_type,
                                              'tag_name': tag_name,
                                              'update_at': when}})
    return True


def get_tag(tag_id):
    if not isinstance(tag_id, ObjectId):
        tag_id = ObjectId(tag_id)
    return DATABASE.tags.find({'_id': tag_id})


def remove_tag_for_gr_user(tag_id):
    if not isinstance(tag_id, ObjectId):
        tag_id = ObjectId(tag_id)
    try:
        DATABASE.tag_for_gr_user.remove({'_id': tag_id})
    except:
        return False
    return True


def remove_tag(tag_id):
    if not isinstance(tag_id, ObjectId):
        tag_id = ObjectId(tag_id)
    try:
        DATABASE.tags.remove({'_id': tag_id})
    except:
        return False
    return True


def remove_customers_location_visit(shop_id, user_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = get_shop_info(shop_id=shop_id)
    gateway_mac = shop.get('gateway_mac')
    user = DATABASE.customers_location.find_one({
        'shop_id': shop_id,
        'user_id': user_id
    })
    if user:
        user_info = user.get('user')
        client_macs = user_info.get('client_mac')
        if client_macs and len(client_macs) > 0:
            for mac in client_macs:
                mac_upper = mac.upper()
                mac_lower = mac.lower()
                DATABASE.survey_result.remove({
                    'shop_id': shop_id,
                    'client_mac': {"$in": [mac_upper, mac_lower, mac]}
                })
                DATABASE.access_log.remove({
                    'gateway_mac': {'$in': gateway_mac},
                    'client_mac': {"$in": [mac_upper, mac_lower, mac]}
                })

    DATABASE.customers_location.remove({
        'shop_id': shop_id,
        'user_id': user_id
    })
    DATABASE.visit_log.remove({
        'shop_id': shop_id,
        'user_id': user_id
    })
    DATABASE.user_tags.remove({
        'shop_id': shop_id,
        'user_id': user_id
    })

def get_contacts(merchant_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    recs = DATABASE.customers.find({
            "merchant_id": merchant_id,
           "$or" : [
    { "user.phone": { "$ne": None } },
    { "user.email" : { "$ne": None } }
  ]
      }).sort('update_at', -1).skip(page_size * (page - 1)) \
                .limit(page_size)
    return recs

def total_contacts(merchant_id):
    return DATABASE.customers.find({
            "merchant_id": merchant_id,
           "$or" : [
    { "user.phone": { "$ne": None } },
    { "user.email" : { "$ne": None } }
  ]
      }).count()

def get_merchant_customers(merchant_id,
                           from_date=None,
                           to_date=None,
                           min_visit=None,
                           max_visit=None,
                           lost_day=None,
                           employee=None,
                           gender=None,
                           sort=None,
                           bday_from_date=None,
                           bday_to_date=None,
                           tags_array=None,
                           page=None,
                           page_size=None,
                           phone_filter=None,
                           email_filter=None,
                           zalo_filter=None,
                           fb_filter=None):

    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    info = {}
    info['merchant_id'] = merchant_id

    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0) + timedelta(hours=-7)
        from_tmp = time.mktime(from_obj.timetuple())
        info['last_visit'] = {}
        info['last_visit']['$gte'] = from_tmp

    if to_date and to_date != 'None' and 'last_visit' in info:
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59) + timedelta(hours=-7)
        to_tmp = time.mktime(to_obj.timetuple())
        info['last_visit']['$lte'] = to_tmp

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)

    if min_visit and str(min_visit) != 'None' and len(min_visit) == 0:
        if max_visit and str(max_visit) != 'None' and len(max_visit) > 0:
            info['total_visit'] = {}
            info['total_visit']['$lte'] = int(max_visit)

    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)
        info['user.birthday'] = {'$in': days}

    if lost_day and str(lost_day) != 'None' and int(lost_day) > 0:
        lost_day_start = time.time() - int(lost_day) * 86400
        info['last_visit'] = {'$lte': lost_day_start}

    if gender and len(gender) > 0 and str(gender) != 'None':
        info['user.gender'] = {'$in': gender}
    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'

    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
    if phone_filter and len(phone_filter) > 0 and str(phone_filter) != 'None':
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if email_filter and len(email_filter) > 0 and str(email_filter) != 'None':
        info['user.email'] = {'$exists': True, "$nin": [None, ""]}
    if zalo_filter and len(zalo_filter) > 0 and str(zalo_filter) != 'None':
        info['user.user_id_zalo'] = {'$exists': True, "$nin": [None, ""]}
    if fb_filter and len(fb_filter) > 0 and str(fb_filter) != 'None':
        info['user.messenger_id'] = {'$exists': True, "$nin": [None, ""]}
    if str(merchant_id) == '638ac8cdd8f0a65ccc2fbaa5':
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}

    recs = []
    if not page:
        recs = DATABASE.customers.find(
            info, no_cursor_timeout=True).sort('last_visit', -1)
    else:
        if sort and sort == 'visit_asc':
            recs = DATABASE.customers.find(info).sort('total_visit', -1).skip(page_size * (page - 1)) \
                .limit(page_size)
        else:
            recs = DATABASE.customers.find(info).sort('last_visit', -1).skip(page_size * (page - 1)) \
                .limit(page_size)
    return [rec for rec in recs]


def total_merchant_customers(merchant_id,
                             is_email=None,
                             is_sms=None,
                             is_zalo=None,
                             from_date=None,
                             to_date=None,
                             min_visit=None,
                             max_visit=None,
                             lost_day=None,
                             gender=None,
                             employee=None,
                             sort=None,
                             bday_from_date=None,
                             bday_to_date=None,
                             tags_array=None,
                             is_has_phone=None,
                             is_has_email=None,
                             is_has_zalo=None,
                             is_has_messenger_id=None,
                             active_zns=None,
                             phone_filter=None,
                             email_filter=None,
                             zalo_filter=None,
                             fb_filter=None
                             ):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    info = {}
    info['merchant_id'] = merchant_id

    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)+ timedelta(hours=-7)
        from_tmp = time.mktime(from_obj.timetuple())
        info['last_visit'] = {}
        info['last_visit']['$gte'] = from_tmp

    if to_date and to_date != 'None' and 'last_visit' in info:
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)+ timedelta(hours=-7)
        to_tmp = time.mktime(to_obj.timetuple())
        info['last_visit']['$lte'] = to_tmp

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)

    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)
        info['user.birthday'] = {'$in': days}

    if lost_day and str(lost_day) != 'None' and int(lost_day) > 0:
        lost_day_start = time.time() - int(lost_day) * 86400
        info['last_visit'] = {'$lte': lost_day_start}
    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'

    if gender and len(gender) > 0 and str(gender) != 'None':
        info['user.gender'] = {'$in': gender}

    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
    null_arr = ['', 'null', 'None', 'none', None]
    if isinstance(is_email, bool) and not isinstance(is_sms, bool):
        if is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
    elif isinstance(is_sms, bool) and not isinstance(is_email, bool):
        if is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    else:
        if is_email and is_sms:
            info['$or'] = [
                {'user.phone': {'$exists': True, '$nin': null_arr}},
                {'user.email': {'$exists': True, '$nin': null_arr}}
            ]
        elif is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
        elif is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
        elif is_zalo:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    if is_has_phone:
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_email:
        info['user.email'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_zalo:
        info['user.user_id_zalo'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_messenger_id:
        info['user.messenger_id'] = {'$exists': True, "$nin": [None, ""]}
    if phone_filter and len(phone_filter) > 0 and str(phone_filter) != 'None':
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if email_filter and len(email_filter) > 0 and str(email_filter) != 'None':
        info['user.email'] = {'$exists': True, "$nin": [None, ""]}
    if zalo_filter and len(zalo_filter) > 0 and str(zalo_filter) != 'None':
        info['user.user_id_zalo'] = {'$exists': True, "$nin": [None, ""]}
    if fb_filter and len(fb_filter) > 0 and str(fb_filter) != 'None':
        info['user.messenger_id'] = {'$exists': True, "$nin": [None, ""]}
    if str(merchant_id) == '638ac8cdd8f0a65ccc2fbaa5':
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if is_zalo and active_zns == "off":
        result = []
        customers = DATABASE.customers.find(info).sort('last_visit', -1)
        for rec in customers:
            cus_phone = rec.get('user').get('phone')
            user_id_zalo = rec.get('user').get('user_id_zalo')
            if cus_phone and user_id_zalo and len(str(user_id_zalo)) > 0:
                result.append(rec)
        return len(result)
    return DATABASE.customers.find(info).count()


def get_shop_customers(merchant_id,
                       shop_id,
                       from_date=None,
                       to_date=None,
                       min_visit=None,
                       max_visit=None,
                       lost_day=None,
                       gender=None,
                       sort=None,
                       bday_from_date=None,
                       employee=None,
                       bday_to_date=None,
                       tags_array=None,
                       page=None,
                       page_size=None,
                       phone_filter=None,
                       email_filter=None,
                       zalo_filter=None,
                       fb_filter=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {}
    info['shop_id'] = shop_id

    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)+ timedelta(hours=-7)
        from_tmp = time.mktime(from_obj.timetuple())
        info['last_visit'] = {}
        info['last_visit']['$gte'] = from_tmp

    if to_date and to_date != 'None' and 'last_visit' in info:
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)+ timedelta(hours=-7)
        to_tmp = time.mktime(to_obj.timetuple())
        info['last_visit']['$lte'] = to_tmp

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)

    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)
        info['user.birthday'] = {'$in': days}

    if lost_day and str(lost_day) != 'None' and int(lost_day) > 0:
        lost_day_start = time.time() - int(lost_day) * 86400
        info['last_visit'] = {'$lte': lost_day_start}
    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'

    if gender and len(gender) > 0 and str(gender) != 'None':
        info['user.gender'] = {'$in': gender}
    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
    if phone_filter and len(phone_filter) > 0 and str(phone_filter) != 'None':
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if email_filter and len(email_filter) > 0 and str(email_filter) != 'None':
        info['user.email'] = {'$exists': True, "$nin": [None, ""]}
    if zalo_filter and len(zalo_filter) > 0 and str(zalo_filter) != 'None':
        info['user.user_id_zalo'] = {'$exists': True, "$nin": [None, ""]}
    if fb_filter and len(fb_filter) > 0 and str(fb_filter) != 'None':
        info['user.messenger_id'] = {'$exists': True, "$nin": [None, ""]}
    recs = []
    if not page:
        recs = DATABASE.customers_location.find(info).sort('last_visit', -1)
    else:
        if sort and sort == 'visit_asc':
            recs = DATABASE.customers_location.find(info).sort('total_visit', -1).skip(page_size * (page - 1)) \
                .limit(page_size)
        else:
            recs = DATABASE.customers_location.find(info).sort('last_visit', -1).skip(page_size * (page - 1)) \
                .limit(page_size)
    return [rec for rec in recs]


def get_first_time_visit_shop(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    rec = DATABASE.customers_location.find({
        'shop_id': shop_id
    }).sort('last_visit', 1).limit(1)
    if rec.count() > 0:
        return [_rec for _rec in rec]
    else:
        return False


def get_first_time_visit_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    rec = DATABASE.customers.find({
        'merchant_id': merchant_id
    }).sort('last_visit', 1).limit(1)
    if rec.count() > 0:
        return [_rec for _rec in rec]
    else:
        return False


def total_shop_customers(shop_id,
                         from_date=None,
                         to_date=None,
                         min_visit=None,
                         max_visit=None,
                         lost_day=None,
                         gender=None,
                         employee=None,
                         sort=None,
                         bday_from_date=None,
                         bday_to_date=None,
                         tags_array=None,
                         is_has_phone=None,
                         is_has_email=None,
                         is_has_zalo=None,
                         is_has_messenger_id=None,
                         is_email=None,
                         is_sms=None,
                         is_zalo=None,
                         active_zns=None,
                         phone_filter=None,
                         email_filter=None,
                         zalo_filter=None,
                         fb_filter=None
                         ):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {}
    info['shop_id'] = shop_id

    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        info['last_visit'] = {}
        info['last_visit']['$gte'] = from_tmp

    if to_date and to_date != 'None' and 'last_visit' in info:
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        info['last_visit']['$lte'] = to_tmp

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)

    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)
        info['user.birthday'] = {'$in': days}

    if lost_day and str(lost_day) != 'None' and int(lost_day) > 0:
        lost_day_start = time.time() - int(lost_day) * 86400
        info['last_visit'] = {'$lte': lost_day_start}
    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'

    if gender and len(gender) > 0 and str(gender) != 'None':
        info['user.gender'] = {'$in': gender}
    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
    if is_has_phone:
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_email:
        info['user.email'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_zalo:
        info['user.user_id_zalo'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_messenger_id:
        info['user.messenger_id'] = {'$exists': True, "$nin": [None, ""]}
    null_arr = ['', 'null', 'None', 'none', None]
    if isinstance(is_email, bool) and not isinstance(is_sms, bool):
        if is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
    elif isinstance(is_sms, bool) and not isinstance(is_email, bool):
        if is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    elif isinstance(is_zalo, bool) and not isinstance(is_zalo, bool):
        if is_zalo:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    else:
        if is_email and is_sms:
            info['$or'] = [
                {'user.phone': {'$exists': True, '$nin': null_arr}},
                {'user.email': {'$exists': True, '$nin': null_arr}}
            ]
        elif is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
        elif is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
        elif is_zalo:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    if is_zalo and active_zns == "off":
        result = []
        customers = DATABASE.customers_location.find(
            info).sort('last_visit', -1)
        for rec in customers:
            cus_phone = rec.get('user').get('phone')
            user_id_zalo = rec.get('user').get('user_id_zalo')
            # check_follow_oa = check_phone_follow_zaloOA(shop_id, str(cus_phone))
            # if check_follow_oa:
            if cus_phone and user_id_zalo and len(str(user_id_zalo)) > 0:
                result.append(rec)
        return len(result)
    return DATABASE.customers_location.find(info).count()


def list_users(page, page_size=settings.ITEMS_PER_PAGE):
    return DATABASE.user.find().sort('created_at', -1).skip(
        page_size * (page - 1)).limit(page_size)


def get_users_count():
    return DATABASE.user.find().count()


def get_range_days():
    today = date.today()
    num_days = monthrange(today.year, today.month)[1]
    first_day = str(today.month) + '-1'
    last_day = str(today.month) + '-' + str(num_days)
    return first_day, last_day


def get_user_birthday_in_day_hq(merchant_id, time_birthday):
    now_obj = datetime.fromtimestamp(int(time_birthday)).strftime('%d-%m')
    now_arr = now_obj.split('-')
    b_day = now_arr[1].lstrip("0") + '-' + now_arr[0].lstrip("0")
    recs = DATABASE.hq_shops.find({'user_info.birthday': b_day})
    users = []
    for rec in recs:
        user_info = get_user_info(user_id=rec['user_info']["_id"])
        users.append(user_info)
    return users


def get_user_birthday_in_day(shop_id, list_user_ids_staffs, time_birthday):
    now_obj = datetime.fromtimestamp(int(time_birthday)).strftime('%d-%m')
    now_arr = now_obj.split('-')
    b_day = now_arr[1].lstrip("0") + '-' + now_arr[0].lstrip("0")
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    query = [
        {
            '$match': {
                'shop_id': shop_id,
                'user_id': {
                    '$nin': list_user_ids_staffs
                }
            }
        },
        {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        },
        {
            '$lookup': {
                "from": "user",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            '$match': {
                'user.birthday': b_day
            }
        },
    ]
    recs = DATABASE.visit_log.aggregate(query, allowDiskUse=True)
    users = []
    for rec in recs:
        user_info = get_user_info(rec["_id"])
        users.append(user_info)
    return users


def get_customers_birthday(shop_id, cus_sort, page=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    first_day, last_day = get_range_days()
    query = [
        {
            '$match': {
                'shop_id': shop_id,
            }
        },
        {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        },
        {
            '$lookup': {
                "from": "user",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            '$match': {
                'user.birthday': {
                    '$gte': first_day,
                    '$lte': last_day
                }
            }
        },
    ]
    if cus_sort == 'time':
        query.append({'$sort': {"lastvisit": -1}})
    else:
        query.append({'$sort': {"count": -1}})
    if page:
        query.append({'$skip': settings.ITEMS_PER_PAGE * (page - 1)})
        query.append({'$limit': settings.ITEMS_PER_PAGE})

    recs = DATABASE.visit_log.aggregate(query, allowDiskUse=True)
    users = []
    for rec in recs:
        user_info = get_user_info(rec["_id"])
        if user_info:
            user_info['_id'] = str(user_info['_id'])
            user_info["visit_count"] = rec["count"]
            user_info["timestamp_str"] = arrow.get(rec["lastvisit"]).humanize(
                locale='vi_vn')
            if 'birthday' in user_info:
                user_info['birthday'] = str(user_info['birthday'])
            users.append(user_info)
    return users


def total_user_birthday(shop_id, list_user_ids_staffs):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    first_day, last_day = get_range_days()
    query = [
        {
            '$match': {
                'shop_id': shop_id,
                'user_id': {
                    '$nin': list_user_ids_staffs
                }
            }
        },
        {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                }
            }
        },
        {
            '$lookup': {
                "from": "user",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            '$match': {
                'user.birthday': {
                    '$gte': first_day,
                    '$lte': last_day
                }
            }
        },
        {
            '$sort': {
                "lastvisit": -1
            }
        },
    ]
    recs = DATABASE.visit_log.aggregate(query, allowDiskUse=True)
    return len(list(recs))


def total_customer_new(shop_id, list_user_ids_staffs, days=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {'shop_id': shop_id}
    if days:
        info["timestamp"] = {'$gte': time.time() - days * 86400}
    info['user_id'] = {'$nin': list_user_ids_staffs}
    recs = DATABASE.visit_log.aggregate(
        [{
            '$match': info
        }, {
            '$group': {
                "_id": '$user_id',
                "count": {
                    '$sum': 1
                }
            }
        }, {
            "$sort": {
                "sum": -1
            }
        }, {
            '$match': {
                "count": 1
            }
        }],
        allowDiskUse=True)
    return len(list(recs))


def total_customer_loyal(shop_id, list_user_ids_staffs, days=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {'shop_id': shop_id}
    if days:
        info["timestamp"] = {'$gte': time.time() - days * 86400}
    info['user_id'] = {'$nin': list_user_ids_staffs}
    recs = DATABASE.visit_log.aggregate(
        [{
            '$match': info
        }, {
            '$group': {
                "_id": '$user_id',
                "count": {
                    '$sum': 1
                }
            }
        }, {
            '$match': {
                "count": {
                    "$gte": 3
                }
            }
        }],
        allowDiskUse=True)
    return len(list(recs))


def total_customer_lost(shops, shop_id, merchant_id, lost_count):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    shop = get_shop_info(shop_id=shop_id)
    isHQ = True if merchant_id and merchant_id != '0' else False
    info_match = {}
    info_group_match = {}
    info_match['$match'] = {'shop_id': {'$in': shops}}
    date_from = (
        datetime.now() - timedelta(days=int(lost_count))).strftime("%d-%m-%Y")
    from_obj = datetime.strptime(date_from, '%d-%m-%Y'). \
        replace(hour=0, minute=0)
    from_tmp = time.mktime(from_obj.timetuple())
    query = [
        info_match, {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$max': '$timestamp'
                },
                "count": {
                    '$sum': 1
                },
                'averageIndex': {
                    '$avg': "$index"
                }
            }
        }, {
            '$match': {
                'lastvisit': {
                    '$lte': from_tmp
                }
            }
        }
    ]
    recs = DATABASE.visit_log.aggregate(query, allowDiskUse=True)
    counts = [rec for rec in recs]
    if len(counts) > 0:
        return len(counts)
    else:
        return 0


def total_customers(shops,
                    shop_id,
                    merchant_id,
                    from_date=None,
                    to_date=None,
                    min_visit=None,
                    max_visit=None,
                    sort=None,
                    bday_from_date=None,
                    bday_to_date=None,
                    ranks=None,
                    gender=None,
                    is_zalo=None,
                    min_cash=None,
                    max_cash=None,
                    min_points=None,
                    max_points=None,
                    filter_tags=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    shop = get_shop_info(shop_id=shop_id)
    isHQ = True if merchant_id and merchant_id != '0' else False
    info_match = {}
    info_group_match = {}
    info_match['$match'] = {'shop_id': {'$in': shops}}
    info_group_match['$match'] = {}

    if from_date and from_date != 'None':
        if not 'timestamp' in info_match['$match']:
            info_match['$match']['timestamp'] = {}
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        info_match['$match']['timestamp']['$gte'] = from_tmp

    if to_date and to_date != 'None':
        if not 'timestamp' in info_match['$match']:
            info_match['$match']['timestamp'] = {}
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        info_match['$match']['timestamp']['$lte'] = to_tmp

    if min_visit and min_visit != 'None' and len(min_visit) > 0:
        if not 'count' in info_group_match['$match']:
            info_group_match['$match']['count'] = {}
        info_group_match['$match']['count']['$gte'] = int(min_visit)

    if max_visit and max_visit != 'None' and len(max_visit) > 0:
        if not 'count' in info_group_match['$match']:
            info_group_match['$match']['count'] = {}
        info_group_match['$match']['count']['$lte'] = int(max_visit)

    info_sort = {}
    if sort == 'time_asc':
        info_sort = {'$sort': {"lastvisit": -1}}
    elif sort == 'time_desc':
        info_sort = {'$sort': {"lastvisit": 1}}
    elif sort == 'visit_asc':
        info_sort = {'$sort': {"count": -1}}
    else:
        info_sort = {'$sort': {"count": 1}}

    look_up_user = {
        '$lookup': {
            "from": "user",
            "localField": "_id",
            "foreignField": "_id",
            "as": "user"
        }
    }
    info_birthday_match = {}
    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)

        info_birthday_match = {'$match': {'user.birthday': {'$in': days}}}

    query = [
        info_match,
        {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$max': '$timestamp_date'
                },
                "count": {
                    '$sum': 1
                },
                'averageIndex': {
                    '$avg': "$index"
                }
            }
        },
        info_group_match,
        info_sort,
    ]
    query.append(look_up_user)
    if len(look_up_user) > 0 and len(info_birthday_match) > 0:
        query.append(info_birthday_match)
    if gender and len(gender) > 0 and str(gender) != 'None':
        info_gender_match = {'$match': {'user.gender': {'$in': gender}}}
        query.append(info_gender_match)
    if filter_tags and len(filter_tags) > 0:
        look_up_user_tags = {
            '$lookup': {
                "from": "user_tags",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "user_tags"
            }
        }

        info_tags_match = {'$match': {'user_tags.tags': {'$in': filter_tags}}}
        query.append(look_up_user_tags)
        query.append(info_tags_match)
    info_ranks = {}
    info_ranks_match = {}
    if ranks and str(ranks) != 'None' and str(ranks) != 'all':
        info_ranks = {
            '$lookup': {
                "from": "loyalty_point",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "loyalty"
            }
        }

    query.append({'$group': {'_id': None, 'count': {'$sum': 1}}})

    counts = [
        rec for rec in DATABASE.visit_log.aggregate(
            query, allowDiskUse=True)
    ]
    if len(counts) > 0:
        return counts[0].get('count')
    else:
        return 0


def coupons_report(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {'shop_id': ObjectId(shop_id), }
    total_coupons = DATABASE.coupon.find(info).count()
    return total_coupons


def get_sms_report(shop_id, days=30):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    records = DATABASE.sms_log.find({
        'shop_id': shop_id,
        'timestamp': {
            '$gte': time.time() - days * 86400
        }
    })

    return records.count()


def get_devices_log_report(gateway_macs, from_date=None, to_date=None):
    query = {'gateway_mac': {'$in': gateway_macs}}
    if from_date and to_date:
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=0)
        to_tmp = time.mktime(to_obj.timetuple())
        query['timestamp'] = {'$gte': from_tmp, '$lte': to_tmp}
    _records = DATABASE.access_log.find(query)

    android = 0
    ios = 0
    windows = 0
    other = 0
    for _record in _records:
        device = {}
        ua = ''
        try:
            ua = user_agents.parse(_record.get('user_agent', ''))
        except Exception as e:
            pass
            print(e.message)
        if ua and ua.os.family != 'Other':
            device['os'] = ua.os.family + ' ' + ua.os.version_string
        if device.get("os"):
            if "iOS" in device["os"]:
                ios += 1
            elif "Android" in device["os"]:
                android += 1
            elif "Windows" in device["os"]:
                windows += 1
            else:
                other += 1
        else:
            other += 1
    return android, ios, windows, other


def get_api_patner(api_key):
    return DATABASE.api_patner.find_one({'api_key': api_key})


def get_shops_patner(patner_id):
    if not isinstance(patner_id, ObjectId):
        patner_id = ObjectId(patner_id)
    recs = DATABASE.shop_api_patner.find({'patner_id': patner_id})
    results = []
    for rec in recs:
        if not isinstance(rec['shop_id'], ObjectId):
            rec['shop_id'] = ObjectId(rec['shop_id'])
        shop = get_shop_info(shop_id=rec['shop_id'])
        shop['_id'] = str(shop['_id'])
        results.append(shop)
    return results


def get_shop_patner(patner_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(patner_id, ObjectId):
        patner_id = ObjectId(patner_id)
    shop_patner = DATABASE.shop_api_patner.find_one({
        'patner_id': patner_id,
        'shop_id': shop_id
    })
    if shop_patner:
        return DATABASE.shop.find_one({'_id': shop_id})
    return False


def data_export(
        shop_id,
        cus_filter,
        staffs,
        emps,
        phone_numbers, ):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if cus_filter == "new":
        query = [
            {
                '$match': {
                    'shop_id': shop_id
                }
            },
            {
                '$group': {
                    "_id": '$user_id',
                    "lastvisit": {
                        '$last': "$timestamp"
                    },
                    "count": {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    "lastvisit": -1
                }
            },
            {
                '$match': {
                    "count": 1
                }
            },
        ]

    elif cus_filter == "top":
        query = [{
            '$match': {
                'shop_id': shop_id
            }
        }, {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                "count": -1
            }
        }]
    elif cus_filter == "loyal":
        query = [{
            '$match': {
                'shop_id': shop_id
            }
        }, {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                "lastvisit": -1
            }
        }, {
            '$match': {
                "count": {
                    "$gte": 3
                }
            }
        }]
    elif cus_filter == "7d":
        query = [{
            '$match': {
                'shop_id': shop_id,
                'timestamp': {
                    '$gte': time.time() - 7 * 86400
                }
            }
        }, {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                "lastvisit": -1
            }
        }]

    elif cus_filter == "30d":
        query = [{
            '$match': {
                'shop_id': shop_id,
                'timestamp': {
                    '$gte': time.time() - 30 * 86400
                }
            }
        }, {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                "lastvisit": -1
            }
        }]
    elif cus_filter == "lost":
        query = [{
            '$match': {
                'shop_id': shop_id,
                'timestamp': {
                    '$lte': time.time() - 30 * 86400
                }
            }
        }, {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                "lastvisit": -1
            }
        }]
    else:
        query = [
            {
                '$match': {
                    'shop_id': shop_id
                }
            },
            {
                '$group': {
                    "_id": '$user_id',
                    "lastvisit": {
                        '$last': "$timestamp"
                    },
                    "count": {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    "lastvisit": -1
                }
            },
        ]
    recs = DATABASE.visit_log.aggregate(query, allowDiskUse=True)

    users = []
    for rec in recs:
        user_info = get_user_info(rec["_id"])
        if user_info:
            if user_info['phone'] not in staffs and \
                    user_info['phone'] not in emps and \
                    user_info['phone'] not in phone_numbers:

                user_info['_id'] = str(user_info['_id'])
                if 'birthday' in user_info:
                    user_info['birthday'] = str(user_info['birthday'])

                user_data = []
                user_data.append(user_info['phone'])
                user_data.append(user_info['name'])
                user_data.append(rec["count"])
                user_data.append(user_info['birthday'])
                user_data.append(rec["lastvisit"])
                users.append(user_data)
    return users


def data_export_birthday(shop_id, staffs, emps, phone_numbers):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    first_day, last_day = get_range_days()
    query = [
        {
            '$match': {
                'shop_id': shop_id
            }
        },
        {
            '$group': {
                "_id": '$user_id',
                "lastvisit": {
                    '$last': "$timestamp"
                },
                "count": {
                    '$sum': 1
                }
            }
        },
        {
            '$lookup': {
                "from": "user",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            '$match': {
                'user.birthday': {
                    '$gte': first_day,
                    '$lte': last_day
                }
            }
        },
        {
            '$sort': {
                "lastvisit": -1
            }
        },
    ]

    recs = DATABASE.visit_log.aggregate(query, allowDiskUse=True)
    users = []
    for rec in recs:
        user_info = get_user_info(rec["_id"])
        if user_info:
            if user_info['phone'] not in staffs and \
                    user_info['phone'] not in emps and \
                    user_info['phone'] not in phone_numbers:
                user_info['_id'] = str(user_info['_id'])
                if 'birthday' in user_info:
                    user_info['birthday'] = str(user_info['birthday'])
                user_data = []
                user_data.append(user_info['phone'])
                user_data.append(user_info['name'])
                user_data.append(rec["count"])
                user_data.append(user_info['birthday'])
                user_data.append(rec["lastvisit"])

                users.append(user_data)
    return users


def insert_device(gateway_mac, is_radius):
    if not get_device_info(gateway_mac):
        gateway_mac = normalize(gateway_mac) if gateway_mac else None
        gateway_mac = gateway_mac.upper()
        info = {}
        info['gateway_mac'] = gateway_mac
        info['is_radius'] = is_radius

        return DATABASE.devices.insert(info)


def update_device_type(device_id, device_type, nas_id, is_radius):
    if not isinstance(device_id, ObjectId):
        device_id = ObjectId(device_id)
    DATABASE.devices.update({
        '_id': device_id
    }, {'$set': {
        'device_type': device_type,
        'nas_id': nas_id,
        'is_radius': is_radius
    }})

def update_radius_device(device_id, is_radius):
    if not isinstance(device_id, ObjectId):
        device_id = ObjectId(device_id)
    DATABASE.devices.update({
        '_id': device_id
    }, {'$set': {
        'is_radius': is_radius
    }})


def gen_device_nas_id_mikrotik(gateway_mac):
    return hashlib.md5(gateway_mac.encode()).hexdigest()


def update_device(device_id, mac_add, ssid):
    if not isinstance(device_id, ObjectId):
        device_id = ObjectId(device_id)
    DATABASE.devices.update({
        '_id': device_id
    }, {'$set': {
        'gateway_mac': mac_add,
        'ssid_cloud': ssid
    }})


def get_device_info(gateway_mac):
    return DATABASE.devices.find_one({'gateway_mac': gateway_mac})


def get_device_by_id(device_id):
    if not isinstance(device_id, ObjectId):
        device_id = ObjectId(device_id)
    return DATABASE.devices.find_one({'_id': device_id})


def count_total_clients(shop_gateway):
    total = 0
    for gateway_mac in shop_gateway:
        info = get_device_info(str(gateway_mac))
        clients = int(info['num_clients'])
        total += clients
    return total


def get_list_user_ids_staffs(staffs, emps, phone_numbers):
    user_ids = []
    for staff in staffs:
        if get_user_info(phone_number=staff):
            user_ids.append(get_user_info(phone_number=staff)['_id'])
    for emp in emps:
        if get_user_info(phone_number=emp):
            user_ids.append(get_user_info(phone_number=emp)['_id'])
    for phone in phone_numbers:
        if get_user_info(phone_number=phone):
            user_ids.append(get_user_info(phone_number=phone)['_id'])
    return user_ids


def insert_new_account(shop_id, phone, password, roles, email, is_hash=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    acc = get_account(shop_id, phone)
    when = time.time()
    if acc:
        DATABASE.accounts.update({
            'shop_id': shop_id,
            'phone': phone
        }, {'$set': {
            'when': when,
            'roles': roles,
            'email': email
        }})
    else:
        if not is_hash:
            password = make_hash(password.encode('utf-8'))
        DATABASE.accounts.insert({
            'shop_id': shop_id,
            'phone': phone,
            'password': password,
            'roles': roles,
            'email': email,
            'when': when
        })


def check_acc_merchant(merchant_id, phone):
    return DATABASE.accounts.find_one({
        'merchant_id': merchant_id,
        'phone': phone,
    })


def insert_new_account_merchant(merchant_id,
                                phone,
                                password,
                                roles,
                                email,
                                shops):
    when = time.time()
    password_hash = make_hash(password.encode('utf-8'))
    return DATABASE.accounts.insert({
        'merchant_id': merchant_id,
        'phone': phone,
        'password': password_hash,
        'roles': roles,
        'email': email,
        'when': when,
        'shops': shops
    })


def update_account_merchant_not_pass(account_id,
                                     merchant_id,
                                     phone,
                                     password=None,
                                     roles=None,
                                     email=None,
                                     shops=None,
                                     is_hash=None):
    when = time.time()

    return DATABASE.accounts.update(
        {'_id': ObjectId(account_id)}, {'$set': {
            'merchant_id': merchant_id,
            'phone': phone,
            'roles': roles,
            'email': email,
            'when': when,
            'shops': shops
        }}
    )


def update_account_merchant(account_id,
                            merchant_id,
                            phone,
                            password,
                            roles,
                            email,
                            shops,
                            is_hash=None):
    when = time.time()
    if not is_hash:
        password = make_hash(password.encode('utf-8'))
        return DATABASE.accounts.update(
            {'_id': ObjectId(account_id)}, {'$set': {
                'merchant_id': merchant_id,
                'phone': phone,
                'password': password,
                'roles': roles,
                'email': email,
                'when': when,
                'shops': shops
            }}
        )


def remove_account(shop_id, phone):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.accounts.remove({'shop_id': shop_id, 'phone': phone})
    return True


def remove_account_by_id(merchant_id, account_id):
    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)
    DATABASE.accounts.remove({'merchant_id': merchant_id, '_id': account_id})
    return True


def update_account_staff(shop_id, phone, roles, email):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.accounts.update({
        'shop_id': shop_id,
        'phone': phone
    }, {'$set': {
        'when': time.time(),
        'roles': roles,
        'email': email
    }})


def update_account_staff_merchant(merchant_id, account_id, phone, roles, email,
                                  shops):
    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)
    DATABASE.accounts.update({
        'merchant_id': merchant_id,
        '_id': account_id
    }, {
        '$set': {
            'when': time.time(),
            'phone': phone,
            'roles': roles,
            'email': email,
            'shops': shops
        }
    })


def get_account(shop_id, phone):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.accounts.find_one({'shop_id': shop_id, 'phone': phone})


def get_account_merchant(merchant_id, account_id):
    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)
    return DATABASE.accounts.find_one({
        'merchant_id': merchant_id,
        '_id': account_id
    })


def get_account_merchant_phone(merchant_id, phone):
    return DATABASE.accounts.find_one({
        'merchant_id': merchant_id,
        'phone': phone
    })


def get_account_merchant_email(merchant_id, email):
    return DATABASE.accounts.find_one({
        'merchant_id': merchant_id,
        'email': email
    })


def get_account_email(shop_id, email):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.accounts.find_one({'shop_id': shop_id, 'email': email})


def get_account_by_id_str(account_id):
    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)
    return DATABASE.accounts.find_one({'_id': account_id})


def get_token_account_vcall(username, password, app_name):
    url = 'https://acd-api.vht.com.vn/rest/softphones/login'
    headers = {
        'AppPlatform': 'Web',
        'AppName': app_name,
        'AppVersion': '1.0',
        'Content-Type': 'application/json'
    }
    data = {
        'username': username,
        'password': password
    }
    result = requests.post(url=url, headers=headers, data=json.dumps(data))
    if result.status_code != 200:
        return False
    else:
        return json.loads(result.text)


def get_account_by_email(account_id):
    return DATABASE.accounts.find_one({'email': account_id})


def get_account_by_id(shop_id, account_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)

    return DATABASE.accounts.find_one({'shop_id': shop_id, '_id': account_id})


def get_super_user():
    return DATABASE.accounts.find_one({'phone': '0902185580'})


def get_accounts(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    recs = []
    for rec in DATABASE.accounts.find({'shop_id': shop_id}):
        rec['role_name'] = [
            _ for _ in settings.roles if _['value'] == rec['roles']
        ][0].get('title')
        rec['update_str'] = arrow.get(rec["when"]).humanize(locale='vi_vn')
        recs.append(rec)
    return recs


def get_accounts_merchants(merchant_id):
    recs = []
    accounts_db = DATABASE.accounts.find(
        {'merchant_id': str(merchant_id)}).sort('when', -1)
    for rec in accounts_db:
            roles = [_ for _ in settings.roles if _['value'] == rec['roles']]
            if len(roles) > 0:
                role = roles[0]
                rec['role_name'] = role.get('title')
                rec['update_str'] = arrow.get(
                    rec["when"]).humanize(locale='vi_vn')
                recs.append(rec)
    return recs


def get_accounts_with_roles(shop_id, roles):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.accounts.find({'shop_id': shop_id, 'roles': roles})


def get_accounts_order_process(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = get_shop_info(shop_id=shop_id)
    order_emp = 10
    shop_order_emp = shop.get('order_per_emp')
    if shop_order_emp and int(shop_order_emp) > 0:
        order_emp = shop_order_emp
    recs = []
    for rec in DATABASE.accounts.find({'shop_id': shop_id, 'roles': '5'}):
        order_process = get_order_count_process(shop_id, rec['_id'])
        order_count = 0
        if order_process:
            order_count = order_process.get('order_count')
        if order_count < order_emp:
            recs.append(rec)
    return recs


def insert_super_user():
    for shop_id in get_shop_ids():
        insert_new_account(shop_id, "0902185580", "@aicungbiet89@", '3')


def sign_in_by_phone(shop_id, phone, password):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    user = DATABASE.accounts.find_one({'shop_id': shop_id, 'phone': phone})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def sign_in_staff_by_phone(merchant_id, phone, password):
    user = DATABASE.accounts.find_one({
        'merchant_id': merchant_id,
        'phone': phone
    })
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def ICO_person(id_login, pass_login, merchant_id):
    find_sale = DATABASE.sale_men.find_one({
        'id_login': id_login,
        'merchant_id': merchant_id
    })
    pass_hash = None
    if find_sale:
        pass_hash = find_sale.get('pass_login')
    if find_sale and check_hash(pass_login, pass_hash):
        return find_sale
    else:
        return False


def check_is_sales_person(id_login, pass_login):
    find_sale = DATABASE.sale_men.find_one({'id_login': id_login})
    pass_hash = None
    if find_sale:
        pass_hash = find_sale.get('pass_login')
    if find_sale and check_hash(pass_login, pass_hash):
        return find_sale
    else:
        return False


def get_sale_by_id(id_login):
    return DATABASE.sale_men.find_one({'id_login': id_login})


def sign_in_staff_by_email(merchant_id, email, password):
    user = DATABASE.accounts.find_one({
        'merchant_id': merchant_id,
        'email': email
    })
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def sign_in_dealer(phone, password):
    user = DATABASE.dealers.find_one({'phone': phone})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def hq_sign_in_by_phone(merchant_id, phone, password):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    user = DATABASE.merchants.find_one({'_id': merchant_id, 'phone': phone})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def hq_sign_in_by_phone_acc(merchant_id, phone, password):
    user = DATABASE.accounts.find_one(
        {'merchant_id': str(merchant_id), 'phone': phone})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def validate_slug(slug):
    if slug.isdigit() == False:
        return True


def hq_sign_in_by_id(merchant_id, password):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    user = DATABASE.merchants.find_one({'_id': merchant_id})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def hq_sign_in_by_slug(merchant_id, slug, password):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    user = DATABASE.merchants.find_one({'_id': merchant_id, 'slug': slug})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def hq_sign_in_by_email(merchant_id, email, password):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    user = DATABASE.merchants.find_one({'_id': merchant_id, 'email': email})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def sign_in_by_account_phone(merchant_id, phone, password):
    user = DATABASE.accounts.find_one(
        {'merchant_id': merchant_id, 'phone': phone})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False


def sign_in_by_account_email(merchant_id, email, password):
    user = DATABASE.accounts.find_one(
        {'merchant_id': merchant_id, 'email': email})
    pass_hash = None
    if user:
        pass_hash = user.get('password')
    if user and check_hash(password, pass_hash):
        return user
    else:
        return False

def get_merchant_by_sup_account_email(merchant_id, email):
    return  DATABASE.accounts.find_one(
        {'merchant_id': merchant_id, 'email': email})

def get_merchant_by_sup_account_phone(merchant_id, phone):
    return  DATABASE.accounts.find_one(
        {'merchant_id': merchant_id, 'phone': phone})

def get_users_staff_merchant(shops):
    users = []
    recs = DATABASE.accounts.find({'shop_id': {'$in': shops}})
    for rec in recs:
        user = {
            'shop_id': rec['shop_id'],
            'phone': rec['phone'],
            'password': rec['password']
        }
        users.append(user)
    return users


# Parameters to PBKDF2. Only affect new passwords.
SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'  # Must be in hashlib.
# Linear to the hashing time. Adjust to be high but take a reasonable
# amount of time on your server. Measure with:
# python -m timeit -s 'import passwords as p' 'p.make_hash("something")'
COST_FACTOR = 10000


def make_hash(password):
    """Generate a random salt and return a new hash for the password."""
    try:
        password = password.strip()
        password = password.encode('utf-8')
    except:
        pass
    salt = b64encode(urandom(SALT_LENGTH))
    new_pass = pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                       getattr(hashlib, HASH_FUNCTION))
    new_pass = new_pass.encode('utf-8')                   
    return 'PBKDF2${}${}${}${}'.format(
        HASH_FUNCTION, COST_FACTOR, salt,
        b64encode(new_pass))



def save_info_fb_setting(merchant_id, user_id_fb, data, access_token):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    merchant_setting = DATABASE.facebook_setting.find_one(
        {"merchant_id": merchant_id, "user_id_fb": str(user_id_fb)})
    data['merchant_id'] = merchant_id
    if merchant_setting:
        DATABASE.facebook_setting.update(
            {'merchant_id': merchant_id, "user_id_fb": str(user_id_fb)}, {"$set": data})
        DATABASE.facebook_setting.update_many({"user_id_fb": str(user_id_fb)}, {
                                              "$set": {"access_token": access_token}})
    else:
        DATABASE.facebook_setting.insert(data)


def get_post_fb(user_id_fb, page=1, page_size=5, created_time_ts=None, completed_time_ts=None):
    if not isinstance(user_id_fb, str):
        user_id_fb = str(user_id_fb)
    if not created_time_ts or not completed_time_ts:
        fb_ads = DATABASE.fb_ads.find({"fb_user_id": user_id_fb, 'impressions': {"$exists": True}}).sort(
            "created_time_ts", -1).skip(page_size * (page - 1)).limit(page_size)
    else:
        fb_ads = DATABASE.fb_ads.find({"fb_user_id": user_id_fb,
                                       "created_time_ts": {"$gte": int(created_time_ts)},
                                       "completed_time_ts": {"$lte": int(completed_time_ts)}
                                       }).sort("created_time_ts", -1).skip(page_size * (page - 1)).limit(page_size)
    result = []
    post_engagement_total = 0
    impressions = 0
    clicks = 0
    for item in fb_ads:
        data = {}
        creative = item.get('creative')
        if creative:
            thumbnail = creative.get('thumbnail')
            if thumbnail:
                data['photo'] = thumbnail
            else:
                data['avatar'] = avinit.get_avatar_data_url("Quang Cao")
            title = creative.get('title')
            data['title'] = title if title else None
            body = creative.get('body')
            if body:
                body_arr = body.split('.')
                data['body_name'] = body_arr[0]
        data['name'] = item.get("name")
        created_time = time.mktime(dateutil.parser.parse(
            item.get("created_time")).timetuple())
        data['create_time'] = datetime.fromtimestamp(
            created_time).strftime('%d-%m-%Y')
        data['status'] = str(item.get("status"))
        data['id'] = str(item.get('_id'))
        data['tracking_specs'] = ""
        data['completed_time'] = ""
        if item.get('completed_time'):
            data['completed_time'] = datetime.strptime(
                item.get('completed_time'), "%Y-%m-%d").strftime("%d-%m-%Y")
        if item.get('impressions'):
            data['impressions'] = item.get('impressions')['total']
            impressions = impressions + int(item.get('impressions')['total'])
        else:
            data['impressions'] = " "
        if item.get('clicks'):
            data['clicks'] = item.get("clicks")['total']
            clicks = clicks + int(item.get("clicks")['total'])
        else:
            data['clicks'] = " "
        tracking_specs = item.get("tracking_specs")
        if tracking_specs:
            action_type = tracking_specs[0].get("action_type")[0]
            data['tracking_specs'] = action_type
        if item.get('post_engagement'):
            data['post_engagement'] = item.get("post_engagement")['total']
            post_engagement_total = post_engagement_total + \
                int(item.get("post_engagement")['total'])
        else:
            data['post_engagement'] = " "
        result.append(data)

    return {
        'result': result,
        'post_engagement_total': post_engagement_total,
        'impressions': impressions,
        'clicks': clicks
    }


def insights_all_ads(user_id_fb, created_time_ts=None, completed_time_ts=None):
    if not isinstance(user_id_fb, str):
        user_id_fb = str(user_id_fb)
    if not created_time_ts or not completed_time_ts:
        fb_ads = DATABASE.fb_ads.find(
            {"fb_user_id": user_id_fb, 'impressions': {"$exists": True}})
    else:
        fb_ads = DATABASE.fb_ads.find({"fb_user_id": user_id_fb,
                                       "created_time_ts": {"$gte": int(created_time_ts)},
                                       "completed_time_ts": {"$lte": int(completed_time_ts)}
                                       })
    ads = [ad for ad in fb_ads]
    dates = [[item.get('date') for item in items.get('impressions').get('date')] for items in ads if
             items.get('impressions')]
    dates_conversation = []
    for impression in dates:
        dates_conversation.extend(impression)
    dates_conversation = sorted(list(dict.fromkeys(dates_conversation)),
                                key=lambda x: datetime.strptime(x, '%d-%m-%Y'))
    dates_info = []
    total_impressison = 0
    total_clicks = 0
    total_post = 0
    for date in dates_conversation:
        date_info = {'date': str(date)}
        impressions_per_date = sum(
            sum(item.get('value') for item in items.get('impressions').get(
                'date') if item.get('date') == str(date))
            for items in ads if items.get('impressions'))
        total_impressison = total_impressison + impressions_per_date
        clicks_per_date = sum(
            sum(item.get('value') for item in items.get('clicks').get(
                'date') if item.get('date') == str(date))
            for items in ads if items.get('clicks'))
        total_clicks = total_clicks + clicks_per_date
        post_engagement_per_date = sum(
            sum(item.get('value') for item in items.get('post_engagement').get(
                'date') if item.get('date') == str(date))
            for items in ads if items.get('post_engagement'))
        total_post = total_post + post_engagement_per_date
        date_info['impressions'] = impressions_per_date
        date_info['clicks'] = clicks_per_date
        date_info['post_engagement'] = post_engagement_per_date
        dates_info.append(date_info)
    result = {'insights_all_ads': dates_info,
              'total_impressison': total_impressison,
              'total_clicks': total_clicks,
              'total_post': total_post,
              }
    return result


def get_post_fb_by_id(ads_id):
    if not isinstance(ads_id, ObjectId):
        ads_id = ObjectId(ads_id)
    item = DATABASE.fb_ads.find_one({'_id': ads_id})
    ads_id_filter = item.get("ads_id")
    data = {}
    creative = item.get('creative')
    if creative:
        thumbnail = creative.get('thumbnail')
        data['permalink_url'] = creative.get('permalink_url')
        if thumbnail:
            data['photo'] = thumbnail
        else:
            data['avatar'] = avinit.get_avatar_data_url("Quang Cao")
        title = creative.get('title')
        data['title'] = title if title else None
        body = creative.get('body')
        if body:
            body_arr = body.split('.')
            data['body_name'] = body_arr[0]
    data['name'] = item.get("name")
    created_time = time.mktime(dateutil.parser.parse(
        item.get("created_time")).timetuple())
    data['create_time'] = datetime.fromtimestamp(
        created_time).strftime('%d-%m-%Y')
    if item.get('completed_time'):
        data['completed_time'] = datetime.strptime(
            item.get('completed_time'), "%Y-%m-%d").strftime("%d-%m-%Y")
    else:
        data['completed_time'] = ""
    data['status'] = str(item.get("status"))
    data['id'] = str(item.get('_id'))
    data['tracking_specs'] = ""
    data['impressions'] = item.get(
        'impressions') if item.get('impressions') else " "
    data['clicks'] = item.get("clicks") if item.get('clicks') else " "
    tracking_specs = item.get("tracking_specs")
    if tracking_specs:
        action_type = tracking_specs[0].get("action_type")[0]
        data['tracking_specs'] = action_type
    actions = item.get("actions")
    if actions:
        post_engagement = [item.get('value') for item in actions if item.get(
            'action_type') == 'post_engagement']
        data['post_engagement'] = post_engagement[0]
    else:
        data['post_engagement'] = ''
    item_filter = item
    data['detail'] = item_filter
    data['detail']['_id'] = ""
    return data


def get_total_post_fb(user_id_fb, created_time_ts=None, completed_time_ts=None):
    if not isinstance(user_id_fb, str):
        user_id_fb = str(user_id_fb)
    if not created_time_ts or not completed_time_ts:
        fb_ads = DATABASE.fb_ads.find(
            {"fb_user_id": user_id_fb, 'impressions': {"$exists": True}})
    else:
        fb_ads = DATABASE.fb_ads.find({"fb_user_id": user_id_fb,
                                       "created_time_ts": {"$gte": int(created_time_ts)},
                                       "completed_time_ts": {"$lte": int(completed_time_ts)}})

    return fb_ads.count()


def get_info_fb_setting(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    merchant_setting = DATABASE.facebook_setting.find_one(
        {"merchant_id": merchant_id, "status_login": True})
    return merchant_setting


# def check_hash(password, hash_):
#     """Check a password against an existing hash."""
#     if isinstance(password, str):
#         password = password.encode('utf-8')
#     algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')
#     assert algorithm == 'PBKDF2'
#     hash_a = b64decode(hash_a)
#     hash_b = pbkdf2_bin(password, salt,
#                         int(cost_factor),
#                         len(hash_a), getattr(hashlib, hash_function))
#     assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
#     # Same as "return hash_a == hash_b" but takes a constant time.
#     # See http://carlos.bueno.org/2011/10/timing.html
#     diff = 0
#     for char_a, char_b in zip(hash_a, hash_b):
#         diff |= ord(char_a) ^ ord(char_b)
#     return diff == 0

def check_hash(password, hash_):
    """Check a password against an existing hash."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')
    assert algorithm == 'PBKDF2'
    hash_a = b64decode(hash_a).decode('iso-8859-1')
    hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                        getattr(hashlib, hash_function))
    assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
    # Same as "return hash_a == hash_b" but takes a constant time.
    # See http://carlos.bueno.org/2011/10/timing.html
    diff = 0
    for char_a, char_b in zip(hash_a, hash_b):
        diff |= ord(char_a) ^ ord(char_b)
    return diff == 0


def new_survey_splash_page_anvui(shop_id, survey_type, question, answers, comment, min_point, max_point, active,
                                 auto_popup, photo_name, title_anvui, content_anvui, merchant_id, connect_button):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()

    if min_point and str(min_point) != 'None':
        min_point = int(min_point)
    if max_point and str(max_point) != 'None':
        max_point = int(max_point)
    if len(question) <= 0:
        question = ['Tổng đài và dịch vụ trả lời trước khi lên xe?', ]
    question_accent = remove_accents_anvui(question)
    slug = slugify(question_accent.decode('utf-8'))
    # if not hotspot_method:
    #     hotspot_method = 'default'
    # if not default_code:
    #     default_code = ''

    return DATABASE.survey_splash_page.insert({
        'shop_id': shop_id,
        'survey_type': survey_type,
        'question': question,
        'answers': answers,
        'comment': comment,
        'min_point': min_point,
        'max_point': max_point,
        'active': active,
        'auto_popup': auto_popup,
        'photo': photo_name,
        'slug': slug,
        'when': when,
        'connect_button': connect_button,
        'title_anvui': title_anvui,
        'content_anvui': content_anvui,
        'merchant_id': merchant_id
    })


def new_survey_splash_page(shop_id, survey_type, question, answers, comment, min_point, max_point, active,
                           auto_popup, photo_name, connect_button, connect_button_color, active_comment):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()

    if min_point and str(min_point) != 'None':
        min_point = int(min_point)
    if max_point and str(max_point) != 'None':
        max_point = int(max_point)
    question_accent = remove_accents(question)
    slug = slugify(question_accent)
    # if not hotspot_method:
    #     hotspot_method = 'default'
    # if not default_code:
    #     default_code = ''
    return DATABASE.survey_splash_page.insert({
        'shop_id': shop_id,
        'survey_type': survey_type,
        'question': question,
        'answers': answers,
        'comment': comment,
        'min_point': min_point,
        'max_point': max_point,
        'active': active,
        'auto_popup': auto_popup,
        'photo': photo_name,
        'connect_button': connect_button,
        'connect_button_color': connect_button_color,
        'active_comment': active_comment,
        'slug': slug,
        'when': when
    })


def update_survey_item(shop_id, survey_id, question=None, answers=None, comment=None, min_point=None, max_point=None,
                       photo=None, connect_button=None, connect_button_color=None, active_comment=None, phone_reply=None, cus_reply=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    when = time.time()
    info = {}
    if question:
        info['question'] = question
        question_accent = remove_accents(question)
        slug = slugify(question_accent)
        info['slug'] = slug
    if answers:
        info['answers'] = answers
    if comment:
        info['comment'] = comment
    if min_point:
        info['min_point'] = min_point
    if max_point:
        info['max_point'] = max_point
    if photo:
        info['photo'] = photo
    if connect_button:
        info['connect_button'] = connect_button
    if connect_button_color:
        info['connect_button_color'] = connect_button_color
    if not phone_reply:
        phone_reply = ""
    info ['phone_reply'] = phone_reply
    info ['cus_reply'] = cus_reply
    info['active_comment'] = active_comment

    DATABASE.survey_splash_page.update({'shop_id': shop_id,
                                        '_id': survey_id}, {
        '$set': info
    })


def update_bitly_url(shop_id, survey_id, bitly_token, long_url):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    try:
        bitly_url = bitly.shorten_url_bitly(bitly_token, long_url)
    except:
        pass
    DATABASE.survey_splash_page.update({
        'shop_id': shop_id,
        '_id': survey_id
    }, {
        '$set': {
            'bitly_url': bitly_url
        }
    })


def remove_survey_splash_page(shop_id, survey_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    return DATABASE.survey_splash_page.remove({
        'shop_id': shop_id,
        '_id': survey_id})


def update_survey_splash_page(shop_id, survey_id, survey_type=None,
                              question=None, answers=None, comment=None, min_point=None,
                              max_point=None, active=None, choose_status=None, step=None, unique_id=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)

    when = time.time()

    if min_point and str(min_point) != 'None':
        min_point = int(min_point)
    if max_point and str(max_point) != 'None':
        max_point = int(max_point)
    info = {}
    if survey_type:
        info['survey_type'] = survey_type
    if question:
        info['question'] = question
    if answers:
        info['answers'] = answers
    if comment:
        info['comment'] = comment
    if min_point:
        info['min_point'] = min_point
    if max_point:
        info['max_point'] = max_point
    if str(active) != 'None':
        info['active'] = active
    info['when'] = when
    if str(choose_status) != 'None' and str(step) != 'None':
        info['choose_step_' + str(step)] = choose_status
    if unique_id:
        info['unique_id'] = unique_id
    return DATABASE.survey_splash_page.update({
        'shop_id': shop_id,
        '_id': survey_id},
        {'$set': info})


def count_result_survery(survey_id, survey_type, shop_id, ans):
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    return DATABASE.survey_result.find({'shop_id': shop_id,
                                        'survey_id': survey_id,
                                        'survey_type': survey_type,
                                        'answers': str(ans)}).count()


def count_result_survey_by_survey_id(survey_id, survey_type, shop_id):
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.survey_result.find({'shop_id': shop_id,
                                        'survey_id': survey_id,
                                        'survey_type': survey_type}).count()


def list_mini_game(shop_id, page=None, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if page:
        return DATABASE.mini_game_page.find({'shop_id': shop_id}) \
            .sort('when', -1).skip(page_size * (page - 1)) \
            .limit(page_size)
    else:
        return DATABASE.mini_game_page.find({'shop_id': shop_id})


def total_mini_game(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.mini_game_page.find({'shop_id': shop_id}).count()


def list_survey_splash(shop_id, page=None, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if page:
        return DATABASE.survey_splash_page.find({'shop_id': shop_id}) \
            .sort('when', -1).skip(page_size * (page - 1)) \
            .limit(page_size)
    else:
        return DATABASE.survey_splash_page.find({'shop_id': shop_id})


def list_id_survey_splash(shop_id, page=None, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    list_survey_splash = DATABASE.survey_splash_page.find({'shop_id': shop_id})
    list_id = []
    for item in list_survey_splash:
        list_id.append(str(item["_id"]))
    return list_id


def total_survey_splash(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.survey_splash_page.find({'shop_id': shop_id}).count()


def get_survey_item(survey_id):
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    return DATABASE.survey_splash_page.find_one({'_id': survey_id})


def remove_survey_item(shop_id, survey_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    return DATABASE.survey_splash_page.remove({'_id': survey_id, 'shop_id': shop_id})


def get_survey_by_slug(survey_slug, shop_id):
    return DATABASE.survey_splash_page.find_one({'slug': survey_slug,
                                                 'shop_id': ObjectId(shop_id)})


def list_mini_game_results(shop_id, page_id, page=None, page_size=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(page_id, ObjectId):
        page_id = ObjectId(page_id)
    results = DATABASE.spin_splash_log.find({'shop_id': shop_id, 'page_id': page_id}) \
        .sort('spin_log', -1).skip(page_size * (int(page) - 1)).limit(page_size)
    list_result = []
    for item in results:
        shop_id_item = item.get('shop_id')
        client_mac = item.get('client_mac')
        user = DATABASE.customers_location.find_one({'shop_id': shop_id_item,
                                                     'user.client_mac': {
                                                         "$in": [client_mac, client_mac.lower(), client_mac.upper()]}})
        if user:
            item['user'] = user.get('user')
        list_result.append(item)
    return list_result


def total_game_results(shop_id, page_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(page_id, ObjectId):
        page_id = ObjectId(page_id)
    return DATABASE.spin_splash_log.find({'shop_id': shop_id, 'page_id': page_id}).count()


def list_survey_results(shop_id, survey_id, page=None, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    survey = []
    results = DATABASE.survey_result.find({'shop_id': shop_id, 'survey_id': survey_id}) \
        .sort('when', -1).skip(page_size * (page - 1)) \
        .limit(page_size)

    for rec in results:
        user = {}
        if 'phone' in rec:
            phone_number = rec.get('phone')
            customer = DATABASE.customers.find_one(
                {'user.phone': phone_number})

        elif 'email' in rec:
            email = rec.get('email')
            customer = DATABASE.customers.find_one({'user.email': email})

        else:
            client_mac = rec.get('client_mac')
            customer = DATABASE.customers.find_one(
                {'user.client_mac': client_mac})
        if customer:
            user = customer.get('user')
            rec['user'] = user
            survey_type = rec.get('survey_type')
            survey_id = rec.get('survey_id')
            answers = rec.get('answers')
            survey_item = DATABASE.survey_splash_page.find_one(
                {'_id': survey_id})
            survey_result_obj = survey_item.get('answers')
            result_items = []

            if survey_type == 'one_select':
                for res in survey_result_obj:
                    try:
                        if res.get('id') == int(answers):
                            result_items.append(res)
                    except:
                        pass
            if survey_type == 'multi_select':
                for res in survey_result_obj:
                    try:
                        if str(res.get('id')) in answers:
                            result_items.append(res)
                    except:
                        pass
            rec['results'] = result_items
            survey.append(rec)
    return survey


def total_survey_results_single(shop_id, survey_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    recs = DATABASE.survey_result.find(
        {'shop_id': shop_id, 'survey_id': survey_id}).count()
    return recs


def get_splash_id(shop_id, type_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if type_page == "hour":
        hour_splash = DATABASE.splash_page.find(
            {'shop_id': shop_id, 'type_page': "hour"})
        result = []
        for page in hour_splash:
            result.append(page.get("_id"))
        return result
    if type_page == "promotion":
        promotion_splash = DATABASE.splash_page.find(
            {'shop_id': shop_id, 'type_page': "promotion"})
        result = []
        for page in promotion_splash:
            result.append(page.get("_id"))
        return result
    if type_page == "tags":
        tag_splash = DATABASE.splash_page.find(
            {'shop_id': shop_id, 'type_page': "tag"})
        result = []
        for page in tag_splash:
            result.append(page.get("_id"))
        return result
    if type_page == "loyal":
        loyal_splash = DATABASE.splash_page.find(
            {'shop_id': shop_id, 'type_page': "loyal"})
        result = []
        for page in loyal_splash:
            result.append(page.get("_id"))
        return result
    if type_page == "weekday":
        weekday_splash = DATABASE.splash_page.find(
            {'shop_id': shop_id, 'type_page': "weekday"})
        result = []
        for page in weekday_splash:
            result.append(page.get("_id"))
        return result


def get_survey_splash(shop_id, survey_id=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not survey_id:
        survey_splash = DATABASE.survey_splash_page.find({'shop_id': shop_id})
        result = []
        for page in survey_splash:
            result.append(page.get("_id"))
        return result
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
        return DATABASE.survey_splash_page.find_one({'_id': survey_id})


def active_splash_weekday(page_id, action):
    if not isinstance(page_id, ObjectId):
        page_id = ObjectId(page_id)
    page = DATABASE.splash_page.find_one({"_id": page_id})
    active = page.get("active")
    active = not active
    DATABASE.splash_page.update({"_id": page_id}, {
        '$set': {"active": active}
    })


def new_splash_page_weekday(shop_id_select, type_page, active,
                            week_id,
                            weekday,
                            title=None,
                            content=None,
                            photo=None,
                            connect_button=None,
                            auto_popup=None):
    if not isinstance(shop_id_select, ObjectId):
        shop_id = ObjectId(shop_id_select)
    when = time.time()
    return DATABASE.splash_page.insert({
        'shop_id': shop_id,
        "week_id": week_id,
        "weekday": weekday,
        'type_page': type_page,
        'active': active,
        'title': title,
        'content': content,
        'photo': photo,
        'when': when,
        'connect_button': connect_button,
        'auto_popup': auto_popup
    })


def update_splash_page_weekday(shop_id_select, page_id, type_page, active,
                               week_id,
                               weekday,
                               title=None,
                               content=None,
                               photo=None,
                               connect_button=None,
                               auto_popup=None):
    if not isinstance(shop_id_select, ObjectId):
        shop_id = ObjectId(shop_id_select)
    if not isinstance(page_id, ObjectId):
        page_id = ObjectId(page_id)
    when = time.time()
    info = {}
    if photo:
        info['photo'] = photo
    if week_id:
        info['week_id'] = week_id
    if weekday:
        info['weekday'] = weekday
    info['update_at'] = when
    info['title'] = title
    info['content'] = content
    info['auto_popup'] = auto_popup
    info['photo'] = photo
    info['active'] = active
    info['connect_button'] = connect_button
    try:
        DATABASE.splash_page.update({
            '_id': page_id,
            'shop_id': shop_id
        }, {
            '$set': info
        })
        return True
    except:
        return False


def new_splash_page(shop_id,
                    type_page,
                    active,
                    title=None,
                    tag=None,
                    content=None,
                    photo=None,
                    slug=None,
                    price=None,
                    link_share=None,
                    loyal_count=None,
                    loyal_count_max=None,
                    date_from=None,
                    hour_to=None,
                    hour_from=None,
                    date_to=None,
                    visits_by=None,
                    auto_popup=None,
                    week_id=None,
                    weekday=None,
                    connect_button=None,
                    link_youtube=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()
    if loyal_count_max and str(loyal_count_max) != 'None' and str(loyal_count_max).isdigit():
        loyal_count_max = int(loyal_count_max)
    if loyal_count and str(loyal_count) != 'None' and str(loyal_count).isdigit():
        loyal_count = int(loyal_count)
    # if not hotspot_method:
    #     hotspot_method = 'default'
    # if not default_code:
    #     default_code = ''
    if type_page == "youtube":
        split_link = link_youtube.split('=')
        id_link = split_link[1]
        content = '<iframe height="400" src="https://www.youtube.com/embed/' + id_link + \
            '?autoplay=1&mute=1" frameborder="0" allow="autoplay" allowfullscreen></iframe>'

    return DATABASE.splash_page.insert({
        'shop_id': shop_id,
        'hour_to': hour_to,
        'hour_from': hour_from,
        'type_page': type_page,
        'active': active,
        'title': title,
        'tag': tag,
        'content': content,
        'photo': photo,
        'slug': slug,
        'price': price,
        'link_share': link_share,
        'when': when,
        'connect_button': connect_button,
        'loyal_count': loyal_count,
        'loyal_count_max': loyal_count_max,
        'date_from': date_from,
        'date_to': date_to,
        'visits_by': visits_by,
        'auto_popup': auto_popup,
        'week_id': week_id,
        'weekday': weekday,
        'link_youtube': link_youtube
    })


def update_splash_page(shop_id,
                       item_id,
                       type_page,
                       active,
                       title=None,
                       content=None,
                       hour_to=None,
                       hour_from=None,
                       photo=None,
                       tag=None,
                       slug=None,
                       price=None,
                       link_share=None,
                       loyal_count=None,
                       loyal_count_max=None,
                       date_from=None,
                       date_to=None,
                       visits_by=None,
                       auto_popup=None,
                       connect_button=None,
                       link_youtube=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)
    when = time.time()
    if loyal_count_max and str(loyal_count_max) != 'None' and str(loyal_count_max).isdigit():
        loyal_count_max = int(loyal_count_max)
    if loyal_count and str(loyal_count) != 'None' and str(loyal_count).isdigit():
        loyal_count = int(loyal_count)
    info = {
        'type_page': type_page,
        'when': when,
    }
    if tag and len(tag) > 0:
        info['tag'] = tag
    if photo:
        info['photo'] = photo
    if loyal_count:
        info['loyal_count'] = loyal_count
    if loyal_count_max:
        info['loyal_count_max'] = loyal_count_max
    if date_from:
        info['date_from'] = date_from
    if hour_from:
        info['hour_from'] = hour_from
    if hour_to:
        info['hour_to'] = hour_to
    if date_to:
        info['date_to'] = date_to
    if link_share:
        info['link_share'] = link_share
    if price:
        info['price'] = price
    if slug:
        info['slug'] = slug
    if connect_button:
        info['connect_button'] = connect_button
    if title:
        info['title'] = title
    if content:
        info['content'] = content
    if link_youtube:
        split_link = link_youtube.split('=')
        id_link = split_link[1]
        iframe_youtube = '<iframe height="400" src="https://www.youtube.com/embed/' + id_link + \
            '?autoplay=1&mute=1" frameborder="0" allow="autoplay" allowfullscreen></iframe>'
        info['link_youtube'] = link_youtube
        info['content'] = iframe_youtube
    if visits_by:
        info['visits_by'] = visits_by
    # if hotspot_method:
    #     info['hotspot_method'] = hotspot_method
    # if str(default_code) != None:
    #     info['default_code'] = default_code
    if auto_popup:
        info['auto_popup'] = auto_popup
    info['active'] = active

    DATABASE.splash_page.update({
        '_id': item_id,
        'shop_id': shop_id
    }, {
        '$set': info
    })


def get_splash_page(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.splash_page.find({'shop_id': shop_id})


def get_surveys_page(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.survey_splash_page.find({'shop_id': shop_id})


def remove_splash_pages(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.splash_page.remove({'shop_id': shop_id})


def remove_survey_pages(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.survey_splash_page.remove({'shop_id': shop_id})


def get_splash_page_by_type(shop_id, type_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    pages = DATABASE.splash_page.find({
        'shop_id': shop_id,
        'type_page': type_page
    })
    return pages


def get_splash_page_weekday(shop_id, type_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    result = []
    for week_id in range(7):
        page = DATABASE.splash_page.find_one({
            'shop_id': shop_id,
            'type_page': type_page,
            'week_id': week_id
        })
        if page:
            result.append(page)
        else:
            result.append({})
    return result


def total_splash_page_by_type(shop_id, type_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.splash_page.find({
        'shop_id': shop_id,
        'type_page': type_page
    }).count()


def get_splash_page_by_id(shop_id, item_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)
    return DATABASE.splash_page.find_one({'_id': item_id, 'shop_id': shop_id})


def get_splash_page_active(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    recs = DATABASE.splash_page.find({
        'shop_id': shop_id,
        'active': True,
        'type_page': {
            '$ne': 'default'
        }
    })
    records = [rec for rec in recs]
    return records


def active_splash_page(shop_id, item_id, active):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)
    DATABASE.splash_page.update({
        '_id': item_id,
        'shop_id': shop_id
    }, {'$set': {
        'active': active
    }})


def remove_splash_page(shop_id, card_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(card_id, ObjectId):
        card_id = ObjectId(card_id)

    return DATABASE.splash_page.remove({'_id': card_id, 'shop_id': shop_id})


def get_splash_page_by_count(shop_id, loyal_count):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.splash_page.find({
        'shop_id': shop_id,
        'loyal_count': {
            '$gte': str(loyal_count)
        }
    })


def get_splash_page_promo_today(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    today = date.today().strftime("%d/%m/%Y")
    return DATABASE.splash_page.find({
        'shop_id': shop_id,
        'date_from': {
            '$lte': today
        },
        'date_to': {
            '$gte': today
        }
    })


def insert_sms_send_unique(shop_id, phone, mess, type_mess, expire):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()
    DATABASE.sms_unique.insert({
        'shop_id': shop_id,
        'phone': phone,
        'mess': mess,
        'type': type_mess,
        'expire': expire,
        'when': when
    })


def insert_sms_send_unique_hq(merchant_id, phone, mess, type_mess, expire):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    when = time.time()
    DATABASE.sms_unique.insert({
        'merchant_id': merchant_id,
        'phone': phone,
        'mess': mess,
        'type': type_mess,
        'expire': expire,
        'when': when
    })


def update_sms_send_unique(shop_id, phone, mess, type_mess, expire):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()
    DATABASE.sms_unique.update({
        'shop_id': shop_id,
        'phone': phone,
        'type': type_mess
    }, {'$set': {
        'mess': mess,
        'expire': expire,
        'when': when
    }})


def update_sms_send_unique_hq(merchant_id, phone, mess, type_mess, expire):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    when = time.time()
    DATABASE.sms_unique.update({
        'merchant_id': merchant_id,
        'phone': phone,
        'type': type_mess
    }, {'$set': {
        'mess': mess,
        'expire': expire,
        'when': when
    }})


def get_sms_send_unique(shop_id, phone, type_mess):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.sms_unique.find_one({
        'shop_id': shop_id,
        'phone': phone,
        'type': type_mess
    })


def get_sms_send_unique_hq(merchant_id, phone, type_mess):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.sms_unique.find_one({
        'merchant_id': merchant_id,
        'phone': phone,
        'type': type_mess
    })


def insert_sms_campaign_hq(merchant_id=None,
                           shop_id=None,
                           code=None,
                           desc=None,
                           message=None,
                           gender=None,
                           from_date=None,
                           to_date=None,
                           type_coupon=None,
                           min_visit=None,
                           max_visit=None,
                           visit_from_date=None,
                           visit_to_date=None,
                           is_sms=None,
                           all_customers=None,
                           is_push_app=None,
                           is_zalo=None,
                           is_email=None,
                           expire_coupon=None,
                           ranks=None,
                           code_fpt=None,
                           is_spam=None,
                           lost_day=None,
                           date_send=None,
                           tags=None,
                           camp_locations=None,
                           visit_by=None,
                           predict_message=None,
                           email_design=None,
                           email_content=None,
                           email_title=None,
                           from_time=None,
                           to_time=None,
                           active_zns=None,
                           temp_id=None,
                           image=None,
                           attachment_id=None):
    when = time.time()
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not active_zns:
        active_zns = "off"
    if not temp_id:
        temp_id = ""
    camp_id = DATABASE.sms_campaign.insert({
        'merchant_id': merchant_id,
        'shop_id': shop_id,
        'code': code,
        'desc': desc,
        'message': message,
        'gender': gender,
        'b_day_from_date': from_date,
        'b_day_to_date': to_date,
        'expire_coupon': expire_coupon,
        'type_coupon': type_coupon,
        'min_visit': min_visit,
        'max_visit': max_visit,
        'visit_from_date': visit_from_date,
        'visit_to_date': visit_to_date,
        'when': when,
        'is_push_app': is_push_app,
        'is_sms': is_sms,
        'is_zalo': is_zalo,
        'active': False,
        'code_fpt': code_fpt,
        'ranks': ranks,
        'is_spam': is_spam,
        'date_send': date_send,
        'tags': tags,
        'shop_select': camp_locations,
        'predict_message': predict_message,
        'all_customers': all_customers,
        'lost_day': lost_day,
        'is_email': is_email,
        'visit_by': visit_by,
        'email_design': email_design,
        'email_content': email_content,
        'email_title': email_title,
        'from_time': from_time,
        'to_time': to_time,
        'active_zns': active_zns,
        'temp_id': temp_id,
        'image': image,
        'attachment_id': attachment_id
    })
    return camp_id


def update_sms_campaign_hq(merchant_id=None,
                           shop_id=None,
                           camp_id=None,
                           code=None,
                           desc=None,
                           message=None,
                           gender=None,
                           from_date=None,
                           to_date=None,
                           type_coupon=None,
                           min_visit=None,
                           max_visit=None,
                           visit_from_date=None,
                           visit_to_date=None,
                           is_sms=None,
                           is_push_app=None,
                           lost_day=None,
                           all_customers=None,
                           is_zalo=None,
                           expire_coupon=None,
                           ranks=None,
                           code_fpt=None,
                           is_spam=None,
                           is_email=None,
                           date_send=None,
                           tags=None,
                           camp_locations=None,
                           visit_by=None,
                           email_design=None,
                           predict_message=None,
                           email_content=None,
                           email_title=None,
                           from_time=None,
                           to_time=None,
                           active_zns=None,
                           temp_id=None,
                           image=None,
                           attachment_id=None):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()
    if not active_zns:
        active_zns = "off"
    if not temp_id:
        active_zns = ""
    if not image:
        info = DATABASE.sms_campaign.find_one(
            {'merchant_id': merchant_id, 'shop_id': shop_id, '_id': camp_id})
        image = info.get('image')
    DATABASE.sms_campaign.update({
        'merchant_id': merchant_id,
        'shop_id': shop_id,
        '_id': camp_id
    }, {
        '$set': {
            'code': code,
            'desc': desc,
            'message': message,
            'gender': gender,
            'b_day_from_date': from_date,
            'b_day_to_date': to_date,
            'expire_coupon': expire_coupon,
            'type_coupon': type_coupon,
            'min_visit': min_visit,
            'max_visit': max_visit,
            'visit_from_date': visit_from_date,
            'visit_to_date': visit_to_date,
            'all_customers': all_customers,
            'lost_day': lost_day,
            'when': when,
            'is_push_app': is_push_app,
            'is_sms': is_sms,
            'is_zalo': is_zalo,
            'predict_message': predict_message,
            'code_fpt': code_fpt,
            'ranks': ranks,
            'is_spam': is_spam,
            'is_email': is_email,
            'date_send': date_send,
            'tags': tags,
            'shop_select': camp_locations,
            'visit_by': visit_by,
            'email_design': email_design,
            'email_content': email_content,
            'email_title': email_title,
            'from_time': from_time,
            'to_time': to_time,
            'active_zns': active_zns,
            'temp_id': temp_id,
            'image': image,
            'attachment_id': attachment_id
        }
    })


def update_sms_campaign_fpt(shop_id, camp_id, campaign_code):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.sms_campaign.update({
        'shop_id': shop_id,
        '_id': camp_id
    }, {'$set': {
        'campaign_code': campaign_code
    }})


def update_sms_campaign_hq_fpt(merchant_id, shop_id, camp_id, campaign_code):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if merchant_id and str(merchant_id) != '0':
        DATABASE.sms_campaign.update({
            'merchant_id': merchant_id,
            '_id': camp_id
        }, {'$set': {
            'campaign_code': campaign_code
        }})
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        DATABASE.sms_campaign.update({
            'shop_id': shop_id,
            '_id': camp_id
        }, {'$set': {
            'campaign_code': campaign_code
        }})


def insert_sms_campaign(shop_id,
                        code=None,
                        desc=None,
                        message=None,
                        gender=None,
                        from_date=None,
                        to_date=None,
                        type_coupon=None,
                        min_visit=None,
                        max_visit=None,
                        visit_from_date=None,
                        visit_to_date=None,
                        is_sms=None,
                        is_push_app=None,
                        is_email=None,
                        is_zalo=None,
                        expire_coupon=None,
                        ranks=None,
                        is_spam=None,
                        date_send=None,
                        tags=None):
    when = time.time()
    camp_id = DATABASE.sms_campaign.insert({
        'shop_id': shop_id,
        'code': code,
        'desc': desc,
        'message': message,
        'gender': gender,
        'b_day_from_date': from_date,
        'b_day_to_date': to_date,
        'expire_coupon': expire_coupon,
        'type_coupon': type_coupon,
        'min_visit': min_visit,
        'max_visit': max_visit,
        'visit_from_date': visit_from_date,
        'visit_to_date': visit_to_date,
        'when': when,
        'is_push_app': is_push_app,
        'is_sms': is_sms,
        'is_zalo': is_zalo,
        'active': False,
        'ranks': ranks,
        'is_spam': is_spam,
        'date_send': date_send,
        'tags': tags,
        'is_email': is_email
    })
    return camp_id


def update_sms_camp_fb_active(shop_id, camp_id, active):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()
    DATABASE.sms_campaign.update({
        'shop_id': shop_id,
        '_id': camp_id
    }, {'$set': {
        'active': active,
        'when': when
    }})


def update_sms_camp_fb_status(shop_id, camp_id, status):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    when = time.time()
    DATABASE.sms_campaign.update({
        'shop_id': shop_id,
        '_id': camp_id
    }, {'$set': {
        'status': status,
        'when': when
    }})


def update_sms_campaign(shop_id,
                        camp_id,
                        code=None,
                        desc=None,
                        message=None,
                        gender=None,
                        from_date=None,
                        to_date=None,
                        type_coupon=None,
                        min_visit=None,
                        max_visit=None,
                        visit_from_date=None,
                        visit_to_date=None,
                        is_sms=None,
                        is_push_app=None,
                        is_email=None,
                        is_zalo=None,
                        expire_coupon=None,
                        ranks=None,
                        is_spam=None,
                        date_send=None,
                        tags=None,
                        code_fpt=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    when = time.time()
    info = {}
    DATABASE.sms_campaign.update({
        'shop_id': shop_id,
        '_id': camp_id
    }, {
        '$set': {
            'code': code,
            'desc': desc,
            'message': message,
            'gender': gender,
            'b_day_from_date': from_date,
            'b_day_to_date': to_date,
            'expire_coupon': expire_coupon,
            'type_coupon': type_coupon,
            'min_visit': min_visit,
            'max_visit': max_visit,
            'visit_from_date': visit_from_date,
            'visit_to_date': visit_to_date,
            'when': when,
            'is_push_app': is_push_app,
            'is_sms': is_sms,
            'is_zalo': is_zalo,
            'code_fpt': code_fpt,
            'ranks': ranks,
            'is_spam': is_spam,
            'date_send': date_send,
            'tags': tags,
            'is_email': is_email
        }
    })


def update_sms_camp_active(merchant_id, camp_id, active):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    when = time.time()
    DATABASE.sms_campaign.update({
        'merchant_id': merchant_id,
        '_id': camp_id
    }, {'$set': {
        'active': active
    }})


def update_sms_camp_status(merchant_id, camp_id, status):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    when = time.time()
    DATABASE.sms_campaign.update({
        'merchant_id': merchant_id,
        '_id': camp_id
    }, {'$set': {
        'status': status
    }})


def update_shop_camp_status(shop_id, camp_id, status):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    when = time.time()
    DATABASE.sms_campaign.update({
        'shop_id': shop_id,
        '_id': camp_id
    }, {'$set': {
        'status': status
    }})


def update_sms_camp_predict_message(merchant_id, shop_id, camp_id, total,
                                    is_hq):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    when = time.time()
    if is_hq:
        DATABASE.sms_campaign.update({
            'merchant_id': str(merchant_id),
            '_id': camp_id
        }, {'$set': {
            'predict_message': total
        }})
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        DATABASE.sms_campaign.update({
            'shop_id': shop_id,
            '_id': camp_id
        }, {'$set': {
            'predict_message': total
        }})


def get_sms_campaign(shop_id, camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.sms_campaign.find_one({'shop_id': shop_id, '_id': camp_id})


def get_sms_campaign_hq(merchant_id, camp_id, shop_id=None):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not shop_id or str(shop_id) == 'all':
        return DATABASE.sms_campaign.find_one({
            'merchant_id': merchant_id,
            '_id': camp_id
        })
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.sms_campaign.find_one({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            '_id': camp_id
        })


def remove_sms_campaign_hq(merchant_id, camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.sms_campaign.remove({
        'merchant_id': merchant_id,
        '_id': camp_id
    })


def register_sms_campaign_hq(merchant_id, camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.sms_campaign.update({
        'merchant_id': merchant_id,
        '_id': camp_id
    }, {
        '$set': {
            'active': False,
            'status': '1'
        }
    })


def get_list_sms_campaign_hq(merchant_id,
                             shop_id=None,
                             page=None,
                             is_hq=None,
                             is_email=None,
                             is_sms=None,
                             is_zalo=None,
                             is_mms=None,
                             page_size=settings.ITEMS_PER_PAGE):
    records = []
    info = {}
    info['merchant_id'] = str(merchant_id)

    if not shop_id or str(shop_id) == 'all':
        if is_email:
            info['is_email'] = True
        if is_sms:
            info['is_sms'] = True
        if is_zalo:
            info['is_zalo'] = True
        if is_mms:
            info['is_mms'] = True
        recs = DATABASE.sms_campaign.find(info).sort(
            'when', -1).skip(page_size * (page - 1)).limit(page_size)
        for rec in recs:
            rec['when_str'] = arrow.get(rec['when']).humanize(locale='vi_vn')
            records.append(rec)

    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        if is_email:
            info['is_email'] = True
        if is_sms:
            info['is_sms'] = True
        if is_zalo:
            info['is_zalo'] = True
        if is_mms:
            info['is_mms'] = True
        info['shop_id'] = shop_id
        recs = DATABASE.sms_campaign.find(info).sort(
            'when', -1).skip(page_size * (page - 1)).limit(page_size)
        for rec in recs:
            camp_id = rec.get('_id')
            if is_email or is_sms or is_zalo or is_mms:
                is_send = email_api.count_email_logs_by_status(
                    shop_id, camp_id, 1)
                not_send = email_api.count_email_logs_by_status(
                    shop_id, camp_id, 0)
                fail = email_api.count_email_logs_by_status(
                    shop_id, camp_id, 2)
                rec['mail_send'] = is_send
                rec['mail_not_send'] = not_send
                rec['fail'] = fail

            rec['when_str'] = arrow.get(rec['when']).humanize(locale='vi_vn')
            records.append(rec)
    return records


def total_sms_campaign_hq(merchant_id, shop_id=None, is_email=None, is_sms=None, is_zalo=None, is_mms=None):
    info = {}
    info['merchant_id'] = str(merchant_id)
    total = 0
    if not shop_id or str(shop_id) == 'all':
        if is_email:
            info['is_email'] = True
        if is_sms:
            info['is_sms'] = True
        if is_zalo:
            info['is_zalo'] = True
        if is_mms:
            info['is_mms'] = True
        total = DATABASE.sms_campaign.find(info).sort('when', -1).count()
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        if is_sms:
            info['is_sms'] = True
        if is_email:
            info['is_email'] = True
        if is_zalo:
            info['is_zalo'] = True
        if is_mms:
            info['is_mms'] = True
        info['shop_id'] = shop_id
        total = DATABASE.sms_campaign.find(info).sort('when', -1).count()
    return total


def get_list_sms_campaign(shop_id, page, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    recs = DATABASE.sms_campaign.find({
        'shop_id': shop_id
    }).sort('when', -1).skip(page_size * (page - 1)).limit(page_size)
    records = []
    for rec in recs:
        rec['when_str'] = arrow.get(rec['when']).humanize(locale='vi_vn')
        records.append(rec)
    return records


def count_total_customer_in_campaign(camp_id,
                                     merchant_id=None,
                                     shop_id=None,
                                     is_hq=None):
    camp = {}
    customers = 0
    shops = []
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)

    if is_hq:
        camp = get_sms_campaign_hq(str(merchant_id), camp_id)
        shop_in_mer = get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shops.append(shop_mer['_id'])
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        camp = get_sms_campaign(shop_id, camp_id)
        shops = [shop_id]
    from_date = camp.get('visit_from_date', None)
    to_date = camp.get('visit_to_date', None)
    min_visit = camp.get('min_visit').strip() if camp.get(
        'min_visit') else None
    max_visit = camp.get('max_visit').strip() if camp.get(
        'max_visit') else None
    bday_from_date = camp.get('b_day_from_date', None)
    bday_to_date = camp.get('b_day_to_date', None)
    is_zalo = camp.get('is_zalo', None)
    ranks = camp.get('ranks', 'all')
    gender = camp.get('gender', 'None')
    sort = 'time_asc'
    tags = camp.get('tags', [])

    tags_array = [str(tag) for tag in tags]
    customers = total_customers(
        shops,
        shop_id,
        merchant_id,
        from_date=from_date,
        to_date=to_date,
        min_visit=min_visit,
        max_visit=max_visit,
        sort=sort,
        bday_from_date=bday_from_date,
        bday_to_date=bday_to_date,
        ranks=ranks,
        filter_tags=tags_array,
        gender=gender,
        is_zalo=None)

    return customers


def find_sale_by_id(sale_id):
    if not isinstance(sale_id, ObjectId):
        sale_id = ObjectId(sale_id)
    return DATABASE.user_sale.find_one({'_id': sale_id})


def total_sms_campaign(shops,
                       from_date=None,
                       to_date=None,
                       is_type=None,
                       is_channel=None):
    query = {'shop_id': {'$in': shops}}
    query['when'] = {}
    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=1, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        query['when']['$gte'] = from_tmp

    if to_date and to_date != 'None':
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        query['when']['$lte'] = to_tmp

    if is_type and str(is_type) != 'None':
        query['is_spam'] = is_type

    if is_channel and str(is_channel) != 'None':
        if is_channel == 'is_sms':
            query['is_sms'] = True
        elif is_channel == 'is_push_app':
            query['is_push_app'] = True
        elif is_channel == 'is_zalo':
            query['is_zalo'] = True

    return DATABASE.sms_campaign.find(query).count()


def update_cat_product_from_pos(shop_id, pos_id, categories):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = get_shop_info(shop_id=shop_id)
    merchant_id = shop.get('merchant_id')
    for cat in categories:
        if cat['UpdateDate'] == 'None':
            cat['UpdateDate'] = time.time()
        cat['CategoryName'] = str(''.join(cat['CategoryName']))
        slug = slugify(cat['CategoryName'])
        cat_db = DATABASE.cat_products.find_one({
            'merchant_id': merchant_id,
            'category_id': cat['CategoryId']
        })
        if not cat_db:
            try:
                DATABASE.cat_products.insert({
                    'shop_id': shop_id,
                    'pos_id': pos_id,
                    'category_id': cat['CategoryId'],
                    'item_type_id': cat['ItemTypeId'],
                    'category_name': cat['CategoryName'],
                    'category_code': cat['CategoryCode'],
                    'slug': slug,
                    'active': cat['Active'],
                    'update_date': cat['UpdateDate'],
                    'when': time.time(),
                    'merchant_id': merchant_id
                })
            except Exception as e:
                print(e.message)
        else:
            try:
                DATABASE.cat_products.update({
                    'merchant_id': merchant_id,
                    'category_id': cat['CategoryId']
                }, {
                    '$set': {
                        'shop_id': shop_id,
                        'item_type_id': cat['ItemTypeId'],
                        'category_name': cat['CategoryName'],
                        'category_code': cat['CategoryCode'],
                        'active': cat['Active'],
                        'slug': slug,
                        'update_date': cat['UpdateDate'],
                        'when': time.time(),
                        'merchant_id': merchant_id
                    }
                })
            except Exception as e:
                print(e.message)


def update_cat_products(merchant_id, shop_id, cat_id, name, desc, active,
                        photo):
    slug = slugify(name)
    if cat_id:
        if shop_id:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
        if not isinstance(cat_id, ObjectId):
            cat_id = ObjectId(cat_id)
        cat_pro = None
        if merchant_id:
            cat_pro = DATABASE.cat_products.find_one({
                'merchant_id': merchant_id,
                '_id': cat_id
            })
            if cat_pro:
                DATABASE.cat_products.update({
                    'merchant_id': merchant_id,
                    '_id': cat_id
                }, {
                    '$set': {
                        'shop_id': shop_id,
                        'merchant_id': merchant_id,
                        'category_name': name,
                        'desc': desc,
                        'active': active,
                        'slug': slug,
                        'photo': photo,
                        'when': time.time(),
                    }
                })
        else:
            cat_pro = DATABASE.cat_products.find_one({
                'shop_id': shop_id,
                '_id': cat_id
            })
            if cat_pro:
                DATABASE.cat_products.update({
                    'shop_id': shop_id,
                    '_id': cat_id
                }, {
                    '$set': {
                        'shop_id': shop_id,
                        'merchant_id': merchant_id,
                        'category_name': name,
                        'desc': desc,
                        'slug': slug,
                        'active': active,
                        'photo': photo,
                        'when': time.time(),
                    }
                })
    else:
        if shop_id:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
        DATABASE.cat_products.insert({
            'shop_id': shop_id,
            'merchant_id': merchant_id,
            'category_name': name,
            'desc': desc,
            'active': active,
            'slug': slug,
            'photo': photo,
            'when': time.time(),
        })


def get_cat_products(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    recs = DATABASE.cat_products.find({'shop_id': shop_id}).sort('when', 1)
    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
        results.append(rec)
    return results


def total_cat_products(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.cat_products.find({'shop_id': shop_id}).count()


def get_cat_products_hq(merchant_id):
    recs = DATABASE.cat_products.find({
        'merchant_id': merchant_id
    }).sort('when', 1)
    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
        results.append(rec)
    return results


def get_cat_product_by_id(cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    rec = {}
    rec = DATABASE.cat_products.find_one({'_id': cat_id})
    if rec:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
    return rec


def get_cat_product(shop_id, cat_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    rec = {}
    rec = DATABASE.cat_products.find_one({'shop_id': shop_id, '_id': cat_id})
    if rec:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
    return rec


def get_cat_product_hq(merchant_id, cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    rec = {}
    rec = DATABASE.cat_products.find_one({
        'merchant_id': merchant_id,
        '_id': cat_id
    })
    if rec:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
    return rec


def update_img_cat_product_from_crm(shop_id, cat_id, photo):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.cat_products.update({
        'shop_id': shop_id,
        'category_id': cat_id
    }, {'$set': {
        'photo': photo
    }})


def update_is_home_cat_product_from_crm(shop_id, cat_id, is_home):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.cat_products.update({
        'shop_id': shop_id,
        'category_id': cat_id
    }, {'$set': {
        'is_home': is_home
    }})


def update_is_priority_product_from_crm(shop_id, prod_id, is_priority):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.products.update({
        'shop_id': shop_id,
        'product_id': prod_id
    }, {'$set': {
        'is_priority': is_priority
    }})


def update_is_priority_new_from_crm(merchant_id, shop_id, item_id,
                                    is_priority):
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)

    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        DATABASE.blog_news.update({
            'merchant_id': merchant_id,
            '_id': item_id
        }, {'$set': {
            'is_priority': is_priority
        }})
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)

        DATABASE.blog_news.update({
            'shop_id': shop_id,
            '_id': item_id
        }, {'$set': {
            'is_priority': is_priority
        }})


def update_is_priority_app_new_from_crm(merchant_id, shop_id, item_id,
                                        is_priority):
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)

    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        DATABASE.app_blog_news.update({
            'merchant_id': merchant_id,
            '_id': item_id
        }, {'$set': {
            'is_priority': is_priority
        }})
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)

        DATABASE.app_blog_news.update({
            'shop_id': shop_id,
            '_id': item_id
        }, {'$set': {
            'is_priority': is_priority
        }})


def total_products_by_shop(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.products.find({'shop_id': shop_id}).count()


def get_products_by_cat(cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    results = []
    recs = DATABASE.products.find({'cat_id': cat_id})
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        rec['cat_id'] = str(rec['cat_id'])
        if not rec.get('photo'):
            rec['photo'] = '7d85f3e910eb03d1db39eb0b247449ff.jpeg'
        results.append(rec)
    return results


def get_products_by_cat_hq(merchant_id, cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    results = []
    recs = DATABASE.products.find({'merchant_id': merchant_id, '_id': cat_id})
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
        if not rec.get('photo'):
            rec['photo'] = '7d85f3e910eb03d1db39eb0b247449ff.jpeg'
        results.append(rec)
    return results


def total_products_by_cat_hq(merchant_id, cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    return DATABASE.products.find({
        'merchant_id': merchant_id,
        '_id': cat_id
    }).count()


def total_products_by_cat(cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    return DATABASE.products.find({'cat_id': cat_id, }).count()


def update_product_from_pos(shop_id, pos_id, products):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = get_shop_info(shop_id=shop_id)
    merchant_id = shop.get('merchant_id')
    for product in products:
        prod = DATABASE.products.find_one({
            'merchant_id': merchant_id,
            'product_id': product['ItemId']
        })
        item_slug = slugify(product['ItemDesc'])
        if not prod:
            try:
                DATABASE.products.insert({
                    'shop_id': shop_id,
                    'pos_id': pos_id,
                    'product_id': product['ItemId'],
                    'update_date': product['UpdateDate'],
                    'retail_price': product['RetailPrice'],
                    'manual_price': product['ManualPrice'],
                    'last_unit_cost': product['LastUnitCost'],
                    'last_init_cost': product['LastInitCost'],
                    'kitchen_id': product['KitchenId'],
                    'item_unit_stock': product['ItemUnitInStock'],
                    'item_type_id': product['ItemTypeId'],
                    'item_picture': product['ItemPicture'],
                    'item_expire_date': product['ItemExpireDate'],
                    'item_desc': product['ItemDesc'],
                    'item_cost': product['ItemCost'],
                    'item_code': product['ItemCode'],
                    'is_tax_inclusive_cost': product['IsTaxInclusiveCost'],
                    'is_tax_inclusive': product['IsTaxInclusive'],
                    'is_delivery': product['IsDelivery'],
                    'is_combo': product['IsCombo'],
                    'init_price': product['InitPrice'],
                    'inc_all_price': product['IncAllPrice'],
                    'category_id': product['CategoryId'],
                    'brand_id': product['BrandId'],
                    'active': product['Active'],
                    'when': time.time(),
                    'slug': item_slug,
                    'merchant_id': merchant_id
                })
            except Exception as e:
                print(e.message)
        else:
            try:
                DATABASE.products.update({
                    'merchant_id': merchant_id,
                    'product_id': product['ItemId']
                }, {
                    '$set': {
                        'update_date': product['UpdateDate'],
                        'retail_price': product['RetailPrice'],
                        'manual_price': product['ManualPrice'],
                        'last_unit_cost': product['LastUnitCost'],
                        'last_init_cost': product['LastInitCost'],
                        'kitchen_id': product['KitchenId'],
                        'item_unit_stock': product['ItemUnitInStock'],
                        'item_type_id': product['ItemTypeId'],
                        'item_picture': product['ItemPicture'],
                        'item_expire_date': product['ItemExpireDate'],
                        'item_desc': product['ItemDesc'],
                        'item_cost': product['ItemCost'],
                        'item_code': product['ItemCode'],
                        'is_tax_inclusive_cost': product['IsTaxInclusiveCost'],
                        'is_tax_inclusive': product['IsTaxInclusive'],
                        'is_delivery': product['IsDelivery'],
                        'is_combo': product['IsCombo'],
                        'init_price': product['InitPrice'],
                        'inc_all_price': product['IncAllPrice'],
                        'category_id': product['CategoryId'],
                        'brand_id': product['BrandId'],
                        'active': product['Active'],
                        'when': time.time(),
                        'slug': item_slug,
                        'merchant_id': merchant_id
                    }
                })
            except Exception as e:
                print(e.message)


def get_products_from_pos(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    results = []
    recs = DATABASE.products.find({'shop_id': shop_id})
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
        results.append(rec)
    return results


def get_products_from_pos_paging(shop_id,
                                 page,
                                 page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    results = []
    recs = DATABASE.products.find({
        'shop_id': shop_id
    }).skip(page_size * (page - 1)).limit(page_size)
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        rec['shop_id'] = str(rec['shop_id'])
        if not rec.get('photo'):
            rec['photo'] = '7d85f3e910eb03d1db39eb0b247449ff.jpeg'
        results.append(rec)
    return results


def count_product_from_pos(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.products.find({'shop_id': shop_id}).count()


def get_product_from_pos(shops, product_id):
    return DATABASE.products.find_one({
        'shop_id': {
            '$in': shops
        },
        'product_id': product_id
    })


def get_product_from_pos_hq(merchant_id, product_id):
    return DATABASE.products.find_one({
        'merchant_id': merchant_id,
        'product_id': product_id
    })


def get_product_by_id(cat_id, product_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    if not isinstance(product_id, ObjectId):
        product_id = ObjectId(product_id)
    return DATABASE.products.find_one({'cat_id': cat_id, '_id': product_id})


def update_product_from_crm(cat_id, pro_id, item_desc, retail_price, active,
                            photo, description, detail_product, discount_price,
                            type_discount_price, code):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    slug = slugify(item_desc)
    if pro_id:
        if not isinstance(pro_id, ObjectId):
            pro_id = ObjectId(pro_id)
        DATABASE.products.update({
            'cat_id': cat_id,
            '_id': pro_id
        }, {
            '$set': {
                'item_desc': item_desc,
                'retail_price': retail_price,
                'active': active,
                'when': time.time(),
                'slug': slug,
                'photo': photo,
                'description': description,
                'detail_product': detail_product,
                'discount_price': discount_price,
                'type_discount_price': type_discount_price,
                'code': code
            }
        })
        return pro_id
    else:
        pro_id = DATABASE.products.insert({
            'cat_id': cat_id,
            'item_desc': item_desc,
            'retail_price': retail_price,
            'active': active,
            'when': time.time(),
            'slug': slug,
            'photo': photo,
            'description': description,
            'detail_product': detail_product,
            'discount_price': discount_price,
            'type_discount_price': type_discount_price,
            'code': code
        })
        return pro_id


def get_total_sales_user(shop_id, phone):
    # print phone
    if phone:
        phone = phone.replace('+84', '0')
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.user_total_sales.find_one({
        'shop_id': shop_id,
        'phone': phone
    })


def update_new_blog_category(merchant_id,
                             shop_id,
                             title,
                             desc,
                             active,
                             cat_id=None):
    slug = slugify(title)
    when = time.time()
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
    if not cat_id:
        DATABASE.blog_category.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'title': title,
            'desc': desc,
            'active': active,
            'slug': slug,
            'when': when
        })
    else:
        if not isinstance(cat_id, ObjectId):
            cat_id = ObjectId(cat_id)
        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            DATABASE.blog_category.update({
                'merchant_id': merchant_id,
                '_id': cat_id
            }, {
                '$set': {
                    'title': title,
                    'desc': desc,
                    'active': active,
                    'slug': slug,
                    'when': when
                }
            })
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            DATABASE.blog_category.update({
                'shop_id': shop_id,
                '_id': cat_id
            }, {
                '$set': {
                    'title': title,
                    'desc': desc,
                    'active': active,
                    'slug': slug,
                    'when': when
                }
            })


def get_employee_by_mer(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    result = DATABASE.employee_merchant.find_one({"merchant_id": merchant_id})
    if result:
        return result.get("total_employee")
    else:
        return 0


def get_time_detective_employee(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    result = DATABASE.employee_merchant.find_one({"merchant_id": merchant_id})
    if result:
        return result.get("time_caculator")
    else:
        return 0


def update_app_new_blog_category(merchant_id,
                                 shop_id,
                                 title,
                                 desc,
                                 active,
                                 cat_id=None):
    slug = slugify(title)
    when = time.time()
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
    if not cat_id:
        DATABASE.app_blog_category.insert({
            'merchant_id': merchant_id,
            'shop_id': shop_id,
            'title': title,
            'desc': desc,
            'active': active,
            'slug': slug,
            'when': when
        })
    else:
        if not isinstance(cat_id, ObjectId):
            cat_id = ObjectId(cat_id)
        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            DATABASE.app_blog_category.update({
                'merchant_id': merchant_id,
                '_id': cat_id
            }, {
                '$set': {
                    'title': title,
                    'desc': desc,
                    'active': active,
                    'slug': slug,
                    'when': when
                }
            })
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            DATABASE.app_blog_category.update({
                'shop_id': shop_id,
                '_id': cat_id
            }, {
                '$set': {
                    'title': title,
                    'desc': desc,
                    'active': active,
                    'slug': slug,
                    'when': when
                }
            })


def get_blogs_category(merchant_id, shop_id):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.blog_category.find({'merchant_id': merchant_id})
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.blog_category.find({'shop_id': shop_id})


def get_app_blogs_category(merchant_id, shop_id):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.app_blog_category.find({'merchant_id': merchant_id})
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.app_blog_category.find({'shop_id': shop_id})


def get_blogs_category_active(merchant_id, shop_id):
    recs = []
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        recs = DATABASE.blog_category.find({
            'merchant_id': merchant_id,
            'active': True
        })
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        recs = DATABASE.blog_category.find({
            'shop_id': shop_id,
            'active': True
        })

    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        if 'shop_id' in rec:
            rec['shop_id'] = str(rec['shop_id'])
        if 'merchant_id' in rec:
            rec['merchant_id'] = str(rec['merchant_id'])
        results.append(rec)
    return results


def get_app_blogs_category_active(merchant_id, shop_id):
    recs = []
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        recs = DATABASE.app_blog_category.find({
            'merchant_id': merchant_id,
            'active': True
        })
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        recs = DATABASE.app_blog_category.find({
            'shop_id': shop_id,
            'active': True
        })

    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        if 'shop_id' in rec:
            rec['shop_id'] = str(rec['shop_id'])
        if 'merchant_id' in rec:
            rec['merchant_id'] = str(rec['merchant_id'])
        results.append(rec)
    return results


def get_blog_category(merchant_id, shop_id, cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.blog_category.find_one({
            'merchant_id': merchant_id,
            '_id': cat_id
        })
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.blog_category.find_one({
            'shop_id': shop_id,
            '_id': cat_id
        })


def get_app_blog_category(merchant_id, shop_id, cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.app_blog_category.find_one({
            'merchant_id': merchant_id,
            '_id': cat_id
        })
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.app_blog_category.find_one({
            'shop_id': shop_id,
            '_id': cat_id
        })


def get_blogs_news(merchant_id,
                   shop_id,
                   page,
                   page_size=settings.ITEMS_PER_PAGE):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.blog_news.find({
            'merchant_id': merchant_id
        }).skip(page_size * (page - 1)).limit(page_size)
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.blog_news.find({
            'shop_id': shop_id
        }).skip(page_size * (page - 1)).limit(page_size)


def get_app_blogs_news(merchant_id,
                       shop_id,
                       page,
                       page_size=settings.ITEMS_PER_PAGE):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.app_blog_news.find({
            'merchant_id': merchant_id
        }).sort('when', -1).skip(page_size * (page - 1)).limit(page_size)
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.app_blog_news.find({
            'shop_id': shop_id
        }).skip(page_size * (page - 1)).limit(page_size)


def get_blogs_news_active(merchant_id,
                          shop_id,
                          page,
                          page_size=settings.ITEMS_PER_PAGE):
    recs = []
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        recs = DATABASE.blog_news.find({
            'merchant_id': merchant_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        recs = DATABASE.blog_news.find({
            'shop_id': shop_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        if 'shop_id' in rec:
            rec['shop_id'] = str(rec['shop_id'])
        if 'merchant_id' in rec:
            rec['merchant_id'] = str(rec['merchant_id'])
        results.append(rec)
    return results


def get_app_blogs_news_active(merchant_id,
                              shop_id,
                              page,
                              page_size=settings.ITEMS_PER_PAGE):
    recs = []
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        recs = DATABASE.app_blog_news.find({
            'merchant_id': merchant_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        recs = DATABASE.app_blog_news.find({
            'shop_id': shop_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        if 'shop_id' in rec:
            rec['shop_id'] = str(rec['shop_id'])
        if 'merchant_id' in rec:
            rec['merchant_id'] = str(rec['merchant_id'])
        results.append(rec)
    return results


def get_blogs_news_by_cat_active(merchant_id,
                                 shop_id,
                                 cat_id,
                                 page,
                                 page_size=settings.ITEMS_PER_PAGE):
    recs = []
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        recs = DATABASE.blog_news.find({
            'merchant_id': merchant_id,
            'cat_id': cat_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        recs = DATABASE.blog_news.find({
            'shop_id': shop_id,
            'cat_id': cat_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        if 'shop_id' in rec:
            rec['shop_id'] = str(rec['shop_id'])
        if 'merchant_id' in rec:
            rec['merchant_id'] = str(rec['merchant_id'])
        rec['cat_id'] = str(rec['cat_id'])
        results.append(rec)
    return results


def get_app_blogs_news_by_cat_active(merchant_id,
                                     shop_id,
                                     cat_id,
                                     page,
                                     page_size=settings.ITEMS_PER_PAGE):
    recs = []
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        recs = DATABASE.app_blog_news.find({
            'merchant_id': merchant_id,
            'cat_id': cat_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        recs = DATABASE.app_blog_news.find({
            'shop_id': shop_id,
            'cat_id': cat_id,
            'active': True
        }).skip(page_size * (page - 1)).limit(page_size)
    results = []
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        if 'shop_id' in rec:
            rec['shop_id'] = str(rec['shop_id'])
        if 'merchant_id' in rec:
            rec['merchant_id'] = str(rec['merchant_id'])
        rec['cat_id'] = str(rec['cat_id'])
        results.append(rec)
    return results


def get_blogs_news_item(merchant_id, shop_id, item_id):
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.blog_news.find_one({
            'merchant_id': merchant_id,
            '_id': item_id
        })
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.blog_news.find_one({
            'shop_id': shop_id,
            '_id': item_id
        })


def get_app_blogs_news_item(merchant_id, shop_id, item_id):
    if not isinstance(item_id, ObjectId):
        item_id = ObjectId(item_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.app_blog_news.find_one({
            'merchant_id': merchant_id,
            '_id': item_id
        })
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.app_blog_news.find_one({
            'shop_id': shop_id,
            '_id': item_id
        })


def count_blogs_news(merchant_id, shop_id):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.blog_news.find({'merchant_id': merchant_id}).count()
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.blog_news.find({'shop_id': shop_id}).count()


def count_app_blogs_news(merchant_id, shop_id):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.app_blog_news.find({
            'merchant_id': merchant_id
        }).count()
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.app_blog_news.find({'shop_id': shop_id}).count()


def count_blogs_news_active(merchant_id, shop_id):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.blog_news.find({
            'merchant_id': merchant_id,
            'active': True
        }).count()
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.blog_news.find({
            'shop_id': shop_id,
            'active': True
        }).count()


def count_app_blogs_news_active(merchant_id, shop_id):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.app_blog_news.find({
            'merchant_id': merchant_id,
            'active': True
        }).count()
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.app_blog_news.find({
            'shop_id': shop_id,
            'active': True
        }).count()


def count_blogs_news_by_cat_active(merchant_id, shop_id, cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.blog_news.find({
            'merchant_id': merchant_id,
            'cat_id': cat_id,
            'active': True
        }).count()
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.blog_news.find({
            'shop_id': shop_id,
            'cat_id': cat_id,
            'active': True
        }).count()


def count_app_blogs_news_by_cat_active(merchant_id, shop_id, cat_id):
    if not isinstance(cat_id, ObjectId):
        cat_id = ObjectId(cat_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.app_blog_news.find({
            'merchant_id': merchant_id,
            'cat_id': cat_id,
            'active': True
        }).count()
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.app_blog_news.find({
            'shop_id': shop_id,
            'cat_id': cat_id,
            'active': True
        }).count()


def update_new_blog_item(merchant_id,
                         shop_id,
                         title,
                         desc,
                         cat_id,
                         content,
                         active,
                         photo,
                         item_id=None):
    slug = slugify(title)
    if not item_id:
        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            DATABASE.blog_news.insert({
                'merchant_id': merchant_id,
                'title': title,
                'desc': desc,
                'cat_id': cat_id,
                'content': content,
                'active': active,
                'photo': photo,
                'slug': slug,
                'when': time.time()
            })
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            DATABASE.blog_news.insert({
                'shop_id': shop_id,
                'title': title,
                'desc': desc,
                'cat_id': cat_id,
                'content': content,
                'active': active,
                'photo': photo,
                'slug': slug,
                'when': time.time()
            })
    else:
        info = {}
        if title:
            info['title'] = title
        if desc:
            info['desc'] = desc
        if cat_id:
            info['cat_id'] = cat_id
        if content:
            info['content'] = content
        if active:
            info['active'] = active
        if photo:
            info['photo'] = photo
        if slug:
            info['slug'] = slug
        if info:
            info['when'] = time.time()
        if not isinstance(item_id, ObjectId):
            item_id = ObjectId(item_id)
        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            DATABASE.blog_news.update({
                'merchant_id': merchant_id,
                '_id': item_id
            }, {'$set': info})
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            DATABASE.blog_news.update({
                'shop_id': shop_id,
                '_id': item_id
            }, {'$set': info})


def update_app_new_blog_item(merchant_id,
                             shop_id,
                             title,
                             desc,
                             cat_id,
                             content,
                             active,
                             photo,
                             is_hot,
                             is_fav,
                             start_deal_date,
                             end_deal_date,
                             item_id=None):
    slug = slugify(title)
    if not item_id:
        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            DATABASE.app_blog_news.insert({
                'merchant_id': merchant_id,
                'title': title,
                'desc': desc,
                'cat_id': cat_id,
                'content': content,
                'active': active,
                'photo': photo,
                'slug': slug,
                'is_hot': is_hot,
                'is_fav': is_fav,
                'start_deal_date': start_deal_date,
                'end_deal_date': end_deal_date,
                'when': time.time()
            })
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            DATABASE.app_blog_news.insert({
                'shop_id': shop_id,
                'title': title,
                'desc': desc,
                'cat_id': cat_id,
                'content': content,
                'active': active,
                'photo': photo,
                'is_hot': is_hot,
                'is_fav': is_fav,
                'slug': slug,
                'start_deal_date': start_deal_date,
                'end_deal_date': end_deal_date,
                'when': time.time()
            })
    else:
        info = {}
        if title:
            info['title'] = title
        if desc:
            info['desc'] = desc
        if cat_id:
            info['cat_id'] = cat_id
        if content:
            info['content'] = content
        info['active'] = active
        if photo:
            info['photo'] = photo
        info['is_hot'] = is_hot
        info['is_fav'] = is_fav
        if slug:
            info['slug'] = slug
        if info:
            info['when'] = time.time()
        if start_deal_date:
            info['start_deal_date'] = start_deal_date

        if end_deal_date:
            info['end_deal_date'] = end_deal_date

        if not isinstance(item_id, ObjectId):
            item_id = ObjectId(item_id)
        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            DATABASE.app_blog_news.update({
                'merchant_id': merchant_id,
                '_id': item_id
            }, {'$set': info})
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            DATABASE.app_blog_news.update({
                'shop_id': shop_id,
                '_id': item_id
            }, {'$set': info})


def get_slides_website(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.slides.find({"shop_id": shop_id})


def update_slide_website(shop_id,
                         name,
                         link,
                         image,
                         desc,
                         active,
                         slide_id=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if slide_id:
        if not isinstance(slide_id, ObjectId):
            slide_id = ObjectId(slide_id)
        DATABASE.slides.update({
            '_id': slide_id,
            'shop_id': shop_id
        }, {
            '$set': {
                'name': name,
                'link': link,
                'image': image,
                'desc': desc,
                'active': active,
                'update': time.time()
            }
        })
    else:
        DATABASE.slides.insert({
            'shop_id': shop_id,
            'name': name,
            'link': link,
            'image': image,
            'desc': desc,
            'active': active,
            'update': time.time()
        })


def get_slide_website(shop_id, slide_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(slide_id, ObjectId):
        slide_id = ObjectId(slide_id)
    return DATABASE.slides.find_one({"shop_id": shop_id, '_id': slide_id})


def set_last_sync_customer_from_pos(merchant_id, phone, cus_id, shop_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    last_sync = DATABASE.last_sync_cus_pos.find_one({
        'merchant_id': merchant_id,
        'shop_id': shop_id
    })
    if not last_sync:
        DATABASE.last_sync_cus_pos.insert({
            'merchant_id': merchant_id,
            'phone': phone,
            'cus_id': cus_id,
            'update': time.time(),
            'shop_id': shop_id
        })
    else:
        DATABASE.last_sync_cus_pos.update({
            'merchant_id': merchant_id,
            'shop_id': shop_id
        }, {
            '$set': {
                'cus_id': cus_id,
                'phone': phone,
                'update': time.time(),
            }
        })


def get_last_sync_customer_form_pos(merchant_id, shop_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.last_sync_cus_pos.find_one({
        'merchant_id': merchant_id,
        'shop_id': shop_id
    })


def set_last_sync_customer_from_crm(merchant_id, phone):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    last_sync = DATABASE.last_sync_cus_crm.find_one({
        'merchant_id': merchant_id
    })
    if not last_sync:
        DATABASE.last_sync_cus_crm.insert({
            'merchant_id': merchant_id,
            'phone': phone,
            'update': time.time()
        })
    else:
        DATABASE.last_sync_cus_crm.update({
            'merchant_id': merchant_id
        }, {'$set': {
            'phone': phone,
            'update': time.time()
        }})


def get_last_sync_customer_from_crm(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    # if not isinstance(shop_id, ObjectId):
    #     shop_id = ObjectId(shop_id)
    return DATABASE.last_sync_cus_crm.find_one({'merchant_id': merchant_id})


def update_order_process(shop_id, account_id, incr=True):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)
    order_process = get_order_count_process(shop_id, account_id)
    if not order_process:
        DATABASE.order_process.insert({
            'shop_id': shop_id,
            'account_id': account_id,
            'when': time.time(),
            'order_count': 1
        })
    else:
        if incr:
            DATABASE.order_process.update({
                'shop_id': shop_id,
                'account_id': account_id
            }, {'$inc': {
                'order_count': 1
            }})
        else:
            order_count = order_process.get('order_count')
            if order_count > 1:
                DATABASE.order_process.update({
                    'shop_id': shop_id,
                    'account_id': account_id
                }, {'$inc': {
                    'order_count': -1
                }})
            else:
                DATABASE.order_process.update({
                    'shop_id': shop_id,
                    'account_id': account_id
                }, {'$set': {
                    'order_count': 0
                }})


def get_order_count_process(shop_id, account_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if not isinstance(account_id, ObjectId):
        account_id = ObjectId(account_id)

    return DATABASE.order_process.find_one({
        'shop_id': shop_id,
        'account_id': account_id
    })


def get_ssid(gateway_mac):
    record = DATABASE.ssid.find_one({'gateway_mac': normalize(gateway_mac)})
    return record.get('ssid') if record else None


def set_ssid(gateway_mac, ssid):
    return DATABASE.ssid.update(
        {
            'gateway_mac': normalize(gateway_mac)
        }, {'$set': {
            'ssid': ssid,
            'updated_at': time.time()
        }},
        upsert=True)


def set_note(gateway_mac, note):
    return DATABASE.devices.update({
        'gateway_mac': normalize(gateway_mac)
    }, {'$set': {
        'note': note
    }})


def get_dealers():
    return DATABASE.dealers.find({})


def insert_dealer(name, phone, password):
    password = make_hash(password.encode('utf-8'))
    return DATABASE.dealers.insert({
        'phone': phone,
        'name': name,
        'password': password
    })


def get_dealer(phone):
    return DATABASE.dealers.find_one({'phone': phone})


def get_dealer_by_id(dealer_id):
    if not isinstance(dealer_id, ObjectId):
        dealer_id = ObjectId(dealer_id)
    return DATABASE.dealers.find_one({'_id': dealer_id})


def update_dealer(deal_id, name, phone, password):
    info = {}
    if name:
        info['name'] = name
    if phone:
        info['phone'] = phone

    if password and len(password) > 0:
        password = make_hash(password.encode('utf-8'))
        info['password'] = password

    if not isinstance(deal_id, ObjectId):
        deal_id = ObjectId(deal_id)

    DATABASE.dealers.update({'_id': deal_id}, {'$set': info})


def push_notify(fcm_key, reg_id, title, body):
    url = settings.FCM_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": "key={}".format(fcm_key)
    }
    data = {'to': reg_id, 'notification': {"title": title, "body": body}}

    r = requests.get(url, headers=headers, data=data)
    return r


def gen_date_in_range(from_date, to_date, format=None):
    if not format:
        format = '%d-%m-%Y'
    from_obj = datetime.strptime(from_date, format)
    to_obj = datetime.strptime(to_date, format)
    delta = to_obj - from_obj
    all_days = []
    for i in range(delta.days + 1):
        day_in = from_obj + timedelta(days=i)
        day_obj = str(day_in).split(' ')
        day_full = day_obj[0].split('-')
        _day = day_full[2].lstrip('0') + '-' + day_full[1].lstrip('0')
        all_days.append(_day)
        _day_not_strip = day_full[2] + '-' + day_full[1]

        all_days.append(_day_not_strip)
    return all_days


def gen_full_date_in_range(from_date, to_date, format=None, lstrip=None):
    if not format:
        format = '%d-%m-%Y'
    from_obj = datetime.strptime(from_date, format)
    to_obj = datetime.strptime(to_date, format)
    delta = to_obj - from_obj
    all_days = []
    for i in range(delta.days + 1):
        day_in = from_obj + timedelta(days=i)
        day_obj = str(day_in).split(' ')
        day_full = day_obj[0].split('-')
        if lstrip:
            _day = day_full[2].lstrip('0') + '/' + day_full[1].lstrip(
                '0') + '/' + day_full[0]
            all_days.append(_day)
        else:
            _day = day_full[2] + '/' + day_full[1] + '/' + day_full[0]
            all_days.append(_day)
    return all_days


def get_hour_in_range(start_time, end_time):
    start_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')
    pand = pandas.date_range(start_time, end_time, freq="1min")
    hours_range = []
    for pan in pand:
        hours_range.append(pan.strftime('%H:%M'))
    return hours_range


def get_app_reviews(shops, page, page_size):
    recs = DATABASE.reviews.find({'shop_id': {'$in': shops}}).sort('when', -1) \
        .skip(page_size * (page - 1)) \
        .limit(page_size)
    return recs


def total_reviews(shops):
    return DATABASE.reviews.find({'shop_id': {'$in': shops}}).count()


def gen_invite_code_by_phone(phone_number):
    hash_ids = Hashids(min_length=8, salt=str(phone_number))
    last_nums = list(str(phone_number)[-3:])
    invite_code = hash_ids.encode(
        int(last_nums[0]), int(last_nums[1]), int(last_nums[2]))
    invite_code = invite_code.lower()
    return invite_code


def get_user_by_invite_code(invite_code):
    return DATABASE.user.find_one({'invite_code': invite_code})


def zalo_user_oa(user_id, shop_id, user_id_zalo, userIdByApp, zalo_oa_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    exist_zalo = DATABASE.user_zalo_oa.find_one({
        'user_id': user_id,
        'shop_id': shop_id
    })
    if not exist_zalo:
        DATABASE.user_zalo_oa.insert({
            'user_id': user_id,
            'shop_id': shop_id,
            'user_id_zalo': user_id_zalo,
            'userIdByApp': userIdByApp,
            'zalo_oa_id': zalo_oa_id,
            'when': time.time()
        })
    else:
        DATABASE.user_zalo_oa.update({
            'user_id': user_id,
            'shop_id': shop_id
        }, {
            '$set': {
                'user_id_zalo': user_id_zalo,
                'userIdByApp': userIdByApp,
                'zalo_oa_id': zalo_oa_id,
                'when': time.time()
            }
        })


def get_user_zalo_oa(user_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    return DATABASE.user_zalo_oa.find_one({
        'user_id': user_id,
        'shop_id': shop_id
    })


def get_splash_page_by_birthday(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.splash_page.find({
        'shop_id': shop_id,
        'type_page': 'birthday'
    }).sort('when', -1).limit(1)


def get_firebase_token_merchant(user_id, merchant_id):
    return DATABASE.user_device.find_one({
        'user_id': user_id,
        'merchant_id': merchant_id
    })


def user_logs_count_by_hour(user_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    info = {'user_id': user_id, 'shop_id': shop_id}
    ranges = settings.HOURS_VISIT_RANGE
    visit_hour = []
    for range_hour in ranges:
        min_range = range_hour.get('min')
        max_range = range_hour.get('max')
        info['time_hour'] = {'$lte': max_range, '$gte': min_range}
        count_visit = DATABASE.visit_log.find(info).count()
        item = []
        range_str = str(min_range) + '-' + str(max_range)
        item.append(range_str)
        item.append(count_visit)
        visit_hour.append(item)
    return visit_hour


def count_log_by_hour(shop_ids, min_range, max_range, start_time=None, end_time=None, range_=None):
    shop_ids = [ObjectId(shop_id) for shop_id in shop_ids]
    info = {}
    if range_ and range_ == "range6":
        info = {'shop_id': {'$in': shop_ids},
                '$or': [
                    {'time_hour': {'$lte': max_range, '$gte': min_range}},
                    {'time_hour': {'$lte': '00:59', '$gte': '00:00'}}
        ]}
    else:
        info = {'shop_id': {'$in': shop_ids}}
        info['time_hour'] = {'$lte': max_range, '$gte': min_range}
    if start_time and end_time:
        info['timestamp'] = {'$gte': start_time, '$lte': end_time}
    count_visit = DATABASE.visit_log.find(info).count()
    return count_visit


def create_tags(merchant_id, name, description, tag_id=None, shop_id=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not tag_id or tag_id == 'add':
        if shop_id:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(merchant_id)
            return DATABASE.tags.insert({
                'shop_id': shop_id,
                'merchant_id': merchant_id,
                'name': name,
                'description': description,
                'when': time.time()
            })
        else:
            return DATABASE.tags.insert({
                'merchant_id': merchant_id,
                'name': name,
                'description': description,
                'when': time.time()
            })
    else:
        if not isinstance(tag_id, ObjectId):
            tag_id = ObjectId(tag_id)

        return DATABASE.tags.update({
            '_id': tag_id,
            'merchant_id': merchant_id
        }, {
            '$set': {
                'name': name,
                'description': description,
                'when': time.time()
            }
        })


def init_tags_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    check_wifi_tag = DATABASE.tags.find_one({
        'merchant_id': merchant_id,
        'name': 'wifi'
    })
    if not check_wifi_tag:
        DATABASE.tags.insert({
            'merchant_id': merchant_id,
            'name': 'wifi',
            'description': 'Wifi customers',
            'when': time.time()
        })

    check_zalo_tag = DATABASE.tags.find_one({
        'merchant_id': merchant_id,
        'name': 'zalo'
    })
    if not check_zalo_tag:
        DATABASE.tags.insert({
            'merchant_id': merchant_id,
            'name': 'zalo',
            'description': 'Zalo customers',
            'when': time.time()
        })

    check_fb_tag = DATABASE.tags.find_one({
        'merchant_id': merchant_id,
        'name': 'facebook'
    })
    if not check_fb_tag:
        DATABASE.tags.insert({
            'merchant_id': merchant_id,
            'name': 'facebook',
            'description': 'Facebook customers',
            'when': time.time()
        })

    check_website_tag = DATABASE.tags.find_one({
        'merchant_id': merchant_id,
        'name': 'website'
    })
    if not check_website_tag:
        DATABASE.tags.insert({
            'merchant_id': merchant_id,
            'name': 'website',
            'description': 'Website customers',
            'when': time.time()
        })


def get_tag_by_tag_name(merchant_id, tag_name):
    try:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.tags.find_one({'merchant_id': merchant_id, 'name': tag_name})
    except:
        return False


def get_tag_name_by_tag_id(tag_id):
    if not isinstance(tag_id, ObjectId):
        tag_id = ObjectId(tag_id)
    return DATABASE.tags.find_one({'_id': tag_id})


def check_tag_name(name, merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    tag = DATABASE.tags.find(
        {'name': name, 'merchant_id': merchant_id}).count()
    if not tag:
        return False
    else:
        return DATABASE.tags.find_one({'name': name, 'merchant_id': merchant_id}).get('_id')


def list_item_tags(merchant_id, page, page_size):
    results = []
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    tags = DATABASE.tags.find({'merchant_id': merchant_id}).sort('when', -1). \
        skip(page_size * (page - 1)).limit(page_size)
    for tag in tags:
        results.append(tag)
    return results


def list_tags(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.tags.find({'merchant_id': merchant_id})

def list_tags_by_regex(merchant_id, regex):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.tags.find({'merchant_id': merchant_id, 'name': {'$regex': regex}})

def total_tags(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.tags.find({'merchant_id': merchant_id}).count()


def get_tag_by_id(tag_id):
    try:
        if not isinstance(tag_id, ObjectId):
            tag_id = ObjectId(tag_id)
        return DATABASE.tags.find_one({'_id': tag_id})
    except:
        return ''


def get_tag_by_tag_id(merchant_id, tag_id):
    try:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        if not isinstance(tag_id, ObjectId):
            tag_id = ObjectId(tag_id)
        return DATABASE.tags.find_one({'merchant_id': merchant_id, '_id': tag_id})
    except:
        return ''


def update_user_item(user_id,
                     name=None,
                     phone=None,
                     gender=None,
                     birthday=None,
                     client_mac=None,
                     email=None,
                     fb_id=None,
                     age_range=None,
                     home_town=None,
                     relationship_status=None,
                     first_name=None,
                     middle_name=None,
                     last_name=None,
                     year_birthday=None,
                     note=None,
                     address=None,
                     facebook=None,
                     twitter=None,
                     company=None,
                     company_role=None,
                     is_employee=None,
                     ):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    info = {}
    if name and len(name) > 0:
        info['name'] = name
    if phone and len(phone) > 0:
        info['phone'] = phone
    if gender and len(gender) > 0:
        info['gender'] = gender
    if birthday and len(birthday) > 0:
        info['birthday'] = birthday
    if email and len(email) > 0:
        info['email'] = email
    if fb_id and len(fb_id) > 0:
        info['fb_id'] = fb_id
    if age_range and len(age_range) > 0:
        info['age_range'] = age_range
    if home_town and len(home_town) > 0:
        info['home_town'] = home_town
    if relationship_status and len(relationship_status) > 0:
        info['relationship_status'] = relationship_status
    if first_name and len(first_name) > 0:
        info['first_name'] = first_name
    if middle_name and len(middle_name) > 0:
        info['middle_name'] = middle_name
    if last_name and len(last_name) > 0:
        info['last_name'] = last_name
    if year_birthday and len(year_birthday) > 0:
        info['year_birthday'] = year_birthday
    if note and len(note) > 0:
        info['note'] = note
    if address and len(address) > 0:
        info['address'] = address
    if facebook and len(facebook) > 0:
        info['facebook'] = facebook
    if twitter and len(twitter) > 0:
        info['twitter'] = twitter
    if company and len(company) > 0:
        info['company'] = company
    if company_role and len(company_role) > 0:
        info['company_role'] = company_role
    if is_employee:
        info['is_employee'] = is_employee
    DATABASE.user.update({'_id': user_id}, {'$set': info})
    if client_mac:
        DATABASE.user.update({
            '_id': user_id
        }, {'$addToSet': {
            'client_mac': client_mac
        }})


def remove_user_tags(merchant_id, user_id, tag_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_tag = DATABASE.user_tags.find_one({
        'merchant_id': merchant_id,
        'user_id': user_id
    })
    if user_tag:
        list_tag = user_tag.get("tags")
    if len(list_tag) > 0:
        for item in list_tag:
            if item == tag_id:
                list_tag.remove(item)
    DATABASE.user_tags.update({
        'merchant_id': merchant_id,
        'user_id': user_id
    },
        {'$set': {"tags": list_tag}}
    )


def create_user_tags_update(merchant_id, user_id, tags):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_tag = DATABASE.user_tags.find_one({
        'merchant_id': merchant_id,
        'user_id': user_id
    })
    if not user_tag:
        DATABASE.user_tags.insert({
            'merchant_id': merchant_id,
            'user_id': user_id,
            'tags': tags,
            'when': time.time()
        })
    else:
        check_tag = DATABASE.user_tags.find_one({
            'merchant_id': merchant_id,
            'user_id': user_id,
            'tags': tags
        })
        if not check_tag:
            DATABASE.user_tags.update({
                'merchant_id': merchant_id,
                'user_id': user_id
            }, {'$set': {
                'tags': tags,
            }})


def create_user_tags_merchant(merchant_id, user_id, tags):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_tag = DATABASE.user_tags.find_one({
        'merchant_id': merchant_id,
        'user_id': user_id
    })
    if not user_tag:
        DATABASE.user_tags.insert({
            'merchant_id': merchant_id,
            'user_id': user_id,
            'tags': tags,
            'when': time.time()
        })
    else:
        for tag in tags:
            check_tag = DATABASE.user_tags.find_one({
                'merchant_id': merchant_id,
                'user_id': user_id,
                'tags': tag
            })
            if not check_tag:
                DATABASE.user_tags.update({
                    'merchant_id': merchant_id,
                    'user_id': user_id
                }, {'$push': {
                    'tags': tag,
                }})


def create_user_tags(merchant_id, shop_id, user_id, tags):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    user_tag = DATABASE.user_tags.find_one({
        'merchant_id': merchant_id,
        'user_id': user_id
    })
    if not user_tag:
        DATABASE.user_tags.insert({
            'merchant_id': merchant_id,
            'user_id': user_id,
            'shop_id': shop_id,
            'tags': tags,
            'when': time.time()
        })
    else:
        check_tag = DATABASE.user_tags.find_one({
            'merchant_id': merchant_id,
            'user_id': user_id,
            'tags': tags
        })
        if not check_tag:
            DATABASE.user_tags.update({
                'merchant_id': merchant_id,
                'user_id': user_id
            }, {'$push': {
                'tags': tags,

            }})


def get_user_tags(merchant_id, user_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)

    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    return DATABASE.user_tags.find_one({
        'merchant_id': merchant_id,
        'user_id': user_id
    })


def save_file_export_user(merchant_id, static_path):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    DATABASE.merchant_file.insert({
        'merchant_id': merchant_id,
        'static_path': static_path,
        'when': time.time()
    })


def get_file_export_user(merchant_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    files = DATABASE.merchant_file.find({
        'merchant_id': merchant_id
    }).sort('when', -1). \
        skip(page_size * (page - 1)).limit(page_size)
    results = []
    for file in files:
        file['time_string'] = arrow.get(file['when']).humanize(locale='vi_vn')
        results.append(file)
    return results


def total_file_export_user(merchant_id):
    return DATABASE.merchant_file.find({'merchant_id': merchant_id}).count()


def find_package_fee_by_id(pack_id):
    if not isinstance(pack_id, ObjectId):
        pack_id = ObjectId(pack_id)
    return DATABASE.package.find_one({'_id': pack_id})


def list_package_fee():
    return DATABASE.package.find()


def list_email_template(merchant_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.email_sample_template.find().sort('when', -1). \
        skip(page_size * (page - 1)).limit(page_size)


def count_email_template(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.email_sample_template.find().count()


def merchant_email_template_item(merchant_id, email_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(email_id, ObjectId):
        email_id = ObjectId(email_id)
    return DATABASE.email_sample_template.find_one({'_id': email_id})


def merchant_email_template_item_remove(merchant_id, email_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(email_id, ObjectId):
        email_id = ObjectId(email_id)
    return DATABASE.email_templates.remove({'_id': email_id, 'merchant_id': merchant_id})


def update_email_merchant_template_item(merchant_id,
                                        email_id,
                                        name=None,
                                        note=None,
                                        code=None,
                                        design=None
                                        ):
    when = time.time()
    if email_id == 'add':
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        DATABASE.email_templates.insert({
            'merchant_id': merchant_id,
            'name': name,
            'note': note,
            'code': code,
            'design': design,
            'when': when
        })
    else:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        if not isinstance(email_id, ObjectId):
            email_id = ObjectId(email_id)
        info = {}
        if note:
            info['note'] = note
        if name:
            info['name'] = name
        if code:
            info['code'] = code
        if design:
            info['design'] = design
        info['when'] = when
        DATABASE.email_templates.update({
            '_id': email_id,
            'merchant_id': merchant_id}, {
            '$set': info
        })


def business_model(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.business_model.find_one({'_id': merchant_id})


def business_model_list():
    return DATABASE.business_model.find()


def gen_user_radius(merchant_id, profile_slug):
    total = total_wifi_profiles(merchant_id)
    user_radius = str(merchant_id) + '_' + profile_slug + '_' + str(total)
    return user_radius


def check_wifi_profile_by_slug(merchant_id, slug):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.wifi_profile.find_one({'slug': slug,
                                           'merchant_id': merchant_id})


def check_wifi_profile_by_id(merchant_id, profile_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(profile_id, ObjectId):
        profile_id = ObjectId(profile_id)
    return DATABASE.wifi_profile.find_one({'_id': profile_id,
                                           'merchant_id': merchant_id})


def item_wifi_profile(merchant_id,
                      profile_id=None,
                      name=None,
                      session_timeout=None,
                      down_bw=None,
                      up_bw=None,
                      profile_type=None,
                      pricing=None,
                      tags=None,
                      active=None,
                      expire=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if profile_id == 'add':
        slug = slugify(name)
        group_radius = str(merchant_id) + '_group_' + str(slug)
        user_radius = str(merchant_id) + '_user_' + str(slug)
        info = {}
        info['merchant_id'] = merchant_id
        info['name'] = name
        info['slug'] = slug
        if group_radius:
            info['group_radius'] = group_radius
        if user_radius:
            info['user_radius'] = user_radius
        if session_timeout:
            info['session_timeout'] = session_timeout
        if down_bw:
            try:
                info['down_bw'] =  int(down_bw)
            except:
                pass
        if up_bw:
            try:
                info['up_bw'] =  int(up_bw)
            except:
                pass
        if profile_type:
            try:
                info['profile_type'] =  profile_type
            except:
                pass   
        if pricing:
            try:
                info['pricing'] =  pricing
            except:
                pass   
        if tags:
            try:
                info['tags'] =  tags
            except:
                pass
        if active:
            try:
                info['active'] =  active
            except:
                pass
        if expire:
            try:
                info['expire'] =  expire
            except:
                pass
        DATABASE.wifi_profile.insert(info)

        check_user_rd_cleartext = wifimedia_radius.get_client_radius_by_attr(
            user_radius, 'Cleartext-Password')
        if not check_user_rd_cleartext:
            wifimedia_radius.insert_client_radius(
                user_radius, 'Cleartext-Password', 'Accept', ':=')

        if not wifimedia_radius.check_profile_radius(user_radius):
            wifimedia_radius.insert_profile_radius(user_radius)

        check_user_in_group = wifimedia_radius.check_user_in_group(
            user_radius, group_radius)
        if not check_user_in_group:
            wifimedia_radius.add_clients_to_radius_group(
                user_radius, group_radius, 1)
        if up_bw and down_bw:
            try:
                up_bw = int(up_bw) * 1000000
                down_bw = int(down_bw) * 1000000
                session_timeout = int(session_timeout) * 60
                check_group_reply_session_timeout = wifimedia_radius.check_group_reply(
                    group_radius, 'Session-Timeout')
                if not check_group_reply_session_timeout:
                    wifimedia_radius.add_radius_group_reply(
                        group_radius, 'Session-Timeout', session_timeout)
                check_group_reply_up_bw = wifimedia_radius.check_group_reply(
                    group_radius, 'WISPr-Bandwidth-Max-Up')
                if not check_group_reply_up_bw:
                    wifimedia_radius.add_radius_group_reply(
                        group_radius, 'WISPr-Bandwidth-Max-Up', up_bw)
                check_group_reply_down_bw = wifimedia_radius.check_group_reply(
                    group_radius, 'WISPr-Bandwidth-Max-Down')
                if not check_group_reply_down_bw:
                    wifimedia_radius.add_radius_group_reply(
                        group_radius, 'WISPr-Bandwidth-Max-Down', down_bw)
                check_group_reply_fall = wifimedia_radius.check_group_reply(
                    group_radius, 'Fall-Through')
                if not check_group_reply_fall:
                    wifimedia_radius.add_radius_group_reply(
                        group_radius, 'Fall-Through', 'Yes')
            except:
                pass
    else:
        if not isinstance(profile_id, ObjectId):
            profile_id = ObjectId(profile_id)
        info = {}
        if name and len(name) > 0:
            info['name'] = name
            slug = slugify(name)
            group_radius = str(merchant_id) + '_group_' + str(slug)
            user_radius = str(merchant_id) + '_user_' + str(slug)
            info['slug'] = slug
            info['group_radius'] = group_radius
            info['user_radius'] = user_radius
            check_user_rd_cleartext = wifimedia_radius.get_client_radius_by_attr(
                user_radius, 'Cleartext-Password')
            if not check_user_rd_cleartext:
                wifimedia_radius.insert_client_radius(
                    user_radius, 'Cleartext-Password', 'Accept', ':=')

            if not wifimedia_radius.check_profile_radius(user_radius):
                wifimedia_radius.insert_profile_radius(user_radius)

            check_user_in_group = wifimedia_radius.check_user_in_group(
                user_radius, group_radius)
            if not check_user_in_group:
                wifimedia_radius.add_clients_to_radius_group(
                    user_radius, group_radius, 1)
            if up_bw and down_bw:
                try:
                    up_bw_rad = int(up_bw) * 1000000
                    down_bw_rad = int(down_bw) * 1000000
                    session_timeout_rad = int(session_timeout) * 60
                    check_group_reply_session_timeout = wifimedia_radius.check_group_reply(
                        group_radius, 'Session-Timeout')
                    if not check_group_reply_session_timeout:
                        wifimedia_radius.add_radius_group_reply(
                            group_radius, 'Session-Timeout', session_timeout_rad)
                    check_group_reply_up_bw = wifimedia_radius.check_group_reply(
                        group_radius, 'WISPr-Bandwidth-Max-Up')
                    if not check_group_reply_up_bw:
                        wifimedia_radius.add_radius_group_reply(
                            group_radius, 'WISPr-Bandwidth-Max-Up', up_bw_rad)
                    check_group_reply_down_bw = wifimedia_radius.check_group_reply(
                        group_radius, 'WISPr-Bandwidth-Max-Down')
                    if not check_group_reply_down_bw:
                        wifimedia_radius.add_radius_group_reply(
                            group_radius, 'WISPr-Bandwidth-Max-Down', down_bw_rad)
                    check_group_reply_fall = wifimedia_radius.check_group_reply(
                        group_radius, 'Fall-Through')
                    if not check_group_reply_fall:
                        wifimedia_radius.add_radius_group_reply(
                            group_radius, 'Fall-Through', 'Yes')
                    wifimedia_radius.update_radius_group_reply(
                        group_radius, session_timeout_rad, up_bw_rad, down_bw_rad)
                except:
                    pass

        if session_timeout and len(session_timeout) > 0:
            info['session_timeout'] = session_timeout
        if down_bw and len(down_bw) > 0:
            info['down_bw'] = int(down_bw)
        if up_bw and len(up_bw) > 0:
            info['up_bw'] = int(up_bw)
        if profile_type and len(profile_type) > 0:
            info['profile_type'] = profile_type
        if pricing and len(pricing) > 0:
            info['pricing'] = pricing
        if tags and len(tags) > 0:
            info['tags'] = tags
        if active:
            info['active'] = active
        if expire:
            info['expire'] = expire

        DATABASE.wifi_profile.update({
            '_id': profile_id,
        }, {'$set': info})


def remove_wifi_profile_by_id(merchant_id, profile_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(profile_id, ObjectId):
        profile_id = ObjectId(profile_id)
    DATABASE.wifi_profile.remove(
        {'_id': profile_id, 'merchant_id': merchant_id})


def list_wifi_profiles(merchant_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.wifi_profile.find({'merchant_id': merchant_id}).sort('when', -1). \
        skip(page_size * (page - 1)).limit(page_size)


def list_all_wifi_profiles(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.wifi_profile.find({'merchant_id': merchant_id}).sort('when', -1)


def total_wifi_profiles(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.wifi_profile.find({'merchant_id': merchant_id}).count()


def list_wifi_profiles_code(merchant_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    output = []
    codes = DATABASE.wifi_profile_code.find({'merchant_id': merchant_id}).sort('when', -1). \
        skip(page_size * (page - 1)).limit(page_size)
    for code in codes:
        profile_id = code.get('profile')
        if not isinstance(profile_id, ObjectId):
            profile_id = ObjectId(profile_id)
        profile = DATABASE.wifi_profile.find_one({'_id': profile_id})
        code['profile'] = {}
        if profile:
            code['profile'] = profile

        shop_id = code.get('shop_id')
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        shop = get_shop_info(shop_id=shop_id)
        if shop:
            code['shop'] = shop
        output.append(code)
    return output


def total_wifi_profiles_code(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.wifi_profile_code.find({'merchant_id': merchant_id}).count()


def gen_access_wifi_code_profile():
    when = str(time.time()).replace('.', '')
    hash_ids = Hashids(min_length=3, salt=str(when))
    last_nums = list(str(when)[-3:])
    random_code = hash_ids.encode(
        int(last_nums[0]), int(last_nums[1]), int(last_nums[2]))
    return random_code


def insert_wifi_profiles_code(merchant_id, shop_id, profile, phone, email):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    wifi_code = gen_access_wifi_code_profile()
    wifi_code = wifi_code.lower()
    profile_item = check_wifi_profile_by_id(merchant_id, profile)
    expire = profile_item.get('expire')
    expire_at = 0
    if expire:
        expire_at = time.time() + int(expire) * 3600

    DATABASE.wifi_profile_code.insert({'merchant_id': merchant_id,
                                       'shop_id': shop_id,
                                       'profile': profile,
                                       'phone': phone,
                                       'email': email,
                                       'when': time.time(),
                                       'code': wifi_code,
                                       'expire_at': expire_at
                                       })
    return wifi_code


def save_survey_results(shop_id, survey_id, survey_type, client_mac, answers, comment=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    return DATABASE.survey_result.insert({
        'shop_id': shop_id,
        'survey_id': survey_id,
        'survey_type': survey_type,
        'client_mac': client_mac,
        'answers': answers,
        'comment': comment,
        'when': time.time()
    })


def update_survey_result(shop_id, survey_result_id, phone, email, name):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_result_id, ObjectId):
        survey_result_id = ObjectId(survey_result_id)
    DATABASE.survey_result.update({
        'shop_id': shop_id,
        '_id': survey_result_id
    }, {
        '$set': {
            'phone': phone,
            'email': email,
            'name': name
        }
    })


def get_email_count_hq(merchant_id, from_date=None, to_date=None):
    query = {'merchant_id': merchant_id}
    query_timestamp = {}
    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=1, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        query_timestamp['$gte'] = from_tmp

    if to_date and to_date != 'None':
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        query_timestamp['$lte'] = to_tmp
    if len(query_timestamp) > 0:
        query['timestamp'] = query_timestamp
    return DATABASE.email_log.find(query).count()


def register_with_id(
        id_user=None,
        name=None,
        phone=None,
        gender=None,
        birthday=None,
        client_mac=None,
        email=None,
        fb_id=None,
        age_range=None,
        home_town=None,
        relationship_status=None,
        first_name=None,
        middle_name=None,
        last_name=None,
        year_birthday=None,
        note=None,
        address=None,
        twitter=None,
        is_employee=None,
        company=None,
        facebook=None):
    if name:
        name = name.strip()
    client_mac = normalize(client_mac) if client_mac else None

    info = {
        '_id': ObjectId(id_user),
        'created_at': time.time()
    }
    if client_mac:
        info['client_mac'] = [client_mac]
    if name:
        info['name'] = name
    if phone:
        info['phone'] = phone
    if gender:
        info['gender'] = gender
    if birthday:
        info['birthday'] = birthday
    if year_birthday:
        info['year_birthday'] = year_birthday
    if email:
        info['email'] = email
    if fb_id:
        info['fb_id'] = fb_id
    if age_range:
        info['age_range'] = age_range
    if home_town:
        info['home_town'] = home_town
    if relationship_status:
        info['relationship_status'] = relationship_status
    if first_name:
        info['first_name'] = first_name
    if middle_name:
        info['middle_name'] = middle_name
    if last_name:
        info['last_name'] = last_name
    if note:
        info['note'] = note
    if address:
        info['address'] = address
    if facebook:
        info['facebook'] = facebook
    if twitter:
        info['twitter'] = twitter
    if is_employee:
        info['is_employee'] = is_employee
    if company:
        info['company'] = company
    return DATABASE.user.insert(info)


def get_shop_acvity_smart_message(merchant_id, shop_id, page=None, page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    results = []
    recs = DATABASE.send_activity_log.find({'shop_id': shop_id}) \
        .sort('when', -1).skip(page_size * (page - 1)) \
        .limit(page_size)
    for rec in recs:
        customer_id = rec.get('customer_id')
        customer = handle_customers.get_user_merchant_by_user_id(
            merchant_id, customer_id)
        if customer:
            rec['customer'] = customer
        results.append(rec)
    return results


def total_mess_shop(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.send_activity_log.find_one({'shop_id': shop_id, 'id_type': {'$exists': False}})


def total_activity_smart_message(shop_id, merchant_id=None, start_time=None, end_time=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop_ids = []
    if merchant_id:
        shop_in_mer = get_shop_by_merchant(str(merchant_id))
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shop_ids.append(shop_mer['_id'])
    else:
        shop_ids.append(shop_id)
    if start_time and end_time:
        return DATABASE.send_activity_log.find(
            {'shop_id': {'$in': shop_ids}, 'result': True, 'when': {'$gte': start_time, '$lte': end_time}}).count()
    else:
        return DATABASE.send_activity_log.find({'shop_id': {'$in': shop_ids}, 'result': True}).count()


def total_automation_by_type(shop_id, send_type, id_type):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.send_activity_log.find({'shop_id': shop_id, 'send_type': send_type, 'id_type': id_type}).count()


def total_automation_by_channel(shop_id, send_type, start_time=None, end_time=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    if start_time and end_time:
        return DATABASE.send_activity_log.find({'shop_id': shop_id,
                                                'send_type': send_type,
                                                'when': {'$gte': start_time, '$lte': end_time}}).count()
    else:
        return DATABASE.send_activity_log.find({'shop_id': shop_id,
                                                'send_type': send_type}).count()


def list_router_firmware(page=None, page_size=settings.ITEMS_PER_PAGE):
    results = []
    recs = DATABASE.router_firmware.find({}) \
        .sort('created_at', -1).skip(page_size * (page - 1)) \
        .limit(page_size)
    for rec in recs:
        results.append(rec)
    return results


def total_router_firmware():
    return DATABASE.router_firmware.find({}).count()


def router_firmware_guide_item(router_id):
    if not isinstance(router_id, ObjectId):
        router_id = ObjectId(router_id)

    return DATABASE.router_firmware.find_one({
        '_id': router_id
    })


def check_accout_vcall(merchant_id, account_id):
    return DATABASE.app_synchronized.find_one({'merchant_id': merchant_id,
                                               'name_app': 'vcall',
                                               'setting.info.account_id': account_id})


def update_account_vcall(username, password, account_id, merchant_id, authen_name, status_account, role_account, token,
                         api_key, api_secret, app_name):
    DATABASE.app_synchronized.update_one({'merchant_id': merchant_id, 'name_app': 'vcall'},
                                         {'$set': {
                                             'update_at': time.time(),
                                             'status': "True",
                                             'setting.api_secret': api_secret,
                                             'setting.api_key': api_key
                                         }})
    info = {
        'authen_name': authen_name,
        'token': token,
        'pass_word': password,
        'user_name': username,
        'account_id': account_id,
        'role_account': role_account,
        'status_account': status_account,
        'app_name': app_name
    }
    DATABASE.app_synchronized.update_one({'merchant_id': merchant_id, 'name_app': 'vcall'},
                                         {'$addToSet': {
                                             'status': "True",
                                             'setting.info': info
                                         }})


def get_authen_name_vcall(merchant_id, account_id):
    return DATABASE.app_synchronized.find_one({'merchant_id': merchant_id,
                                               'name_app': 'vcall',
                                               'setting.info.account_id': account_id}).get('authen_name')


def get_token_vcall(merchant_id, account_id):
    return DATABASE.app_synchronized.find_one({'merchant_id': merchant_id,
                                               'name_app': 'vcall',
                                               'setting.info.account_id': account_id}).get('token')


def get_list_calls(merchant_id, call_type, from_phone, to_phone, from_date, to_date, page, page_limit):
    setting = get_app_synchronized(merchant_id=merchant_id, name_app='vcall')
    if not setting:
        return False
    else:
        api_key = setting.get('setting').get('api_key')
        api_secret = setting.get('setting').get('api_secret')
        filter_ = '?sort_by=time_started&sort_type=DESC&limit={}&page={}'.format(
            page_limit, page)
        if str(call_type) == 'call_out':
            filter_ = filter_ + '&direction=3'
        if str(call_type) == 'call_in':
            filter_ = filter_ + '&direction=1'
        if from_phone:
            filter_ = filter_ + '&from_number={}'.format(from_phone)
        if to_phone:
            filter_ = filter_ + '&to_number={}'.format(to_phone)
        if from_date and to_date:
            from_date_ = time.mktime(datetime.strptime(
                from_date, "%d-%m-%Y").timetuple())
            to_date_ = time.mktime(datetime.strptime(
                to_date, "%d-%m-%Y").timetuple()) + 86400
            filter_ = filter_ + \
                '&date_started={}'.format(
                    from_date_) + '&date_ended={}'.format(to_date_)
        url = 'https://acd-api.vht.com.vn/rest/cdrs{}'.format(filter_)
        token = b64encode(str(api_key) + ':' + str(api_secret))
        headers = {
            'Authorization': 'Basic ' + token
        }
        result = requests.get(url=url, headers=headers)
        if str(result.status_code) != '200':
            return False
        else:
            return json.loads(result.text)


def check_employee(user_id, shop_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.employee_merchant.find_one({'employee_id.shop_id': shop_id,
                                                'employee_id.employee_id': user_id})


def check_report_graphql(when, merchant_id=None, shop_id=None):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.merchant_report_graphql.find_one({"merchant_id": merchant_id,
                                                          "when": when})
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.shop_report_graphql.find_one({"shop_id": shop_id,
                                                      "when": when})


def get_user_current(user_id, merchant_id=None, shop_id=None):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        result = DATABASE.customers.find_one({
            'merchant_id': merchant_id,
            'user_id': user_id})
        return result
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        result = DATABASE.customers_location.find_one({
            'shop_id': shop_id,
            'user_id': user_id})
        return result


def get_device_log_user(client_mac):
    client_mac_up = client_mac.upper()
    client_mac_lo = client_mac.lower()
    DATABASE.access_log.create_index([('client_mac', 1)])
    result = DATABASE.access_log.find_one({'client_mac': client_mac})
    if not result:
        result = DATABASE.access_log.find_one({"client_mac": client_mac_up})
        if not result:
            result = DATABASE.access_log.find_one(
                {"client_mac": client_mac_lo})
    if result:
        device_user = None
        if isinstance(result.get('user_agent'), str) or isinstance(result.get('user_agent'), str):
            user_agent = parse(result.get('user_agent'))
            if 'iOS' in str(user_agent.os.family):
                device_user = 'iOS'
            elif 'Mac OS X' in str(user_agent.os.family):
                device_user = 'Mac OS'
            elif 'Android' in str(user_agent.os.family):
                device_user = 'Android'
            elif 'Windows' in str(user_agent.os.family):
                device_user = 'Windows'
            elif 'Linux' in str(user_agent.os.family):
                device_user = 'Linux'
            else:
                device_user = 'Other'
            return device_user
        else:
            return False
    else:
        return False


def update_report_graphql(when, info, merchant_id=None, shop_id=None):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        try:
            DATABASE.merchant_report_graphql.update({'merchant_id': merchant_id,
                                                     'when': when},
                                                    {'$set': info})
            return True
        except:
            return False
    else:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        try:
            DATABASE.shop_report_graphql.update({'shop_id': shop_id,
                                                 'when': when},
                                                {'$set': info})
            return True
        except:
            return False


def insert_report_graphql(info, merchant_id=None, shop_id=None):
    if merchant_id:
        try:
            DATABASE.merchant_report_graphql.insert(info)
            return True
        except:
            return False
    else:
        try:
            DATABASE.shop_report_graphql.insert(info)
            return True
        except:
            return False


def check_user_in_report(user_id, timestamp, time_day, shop_id=None, merchant_id=None):
    if merchant_id:
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        shops = DATABASE.shop.distinct('_id', {'merchant_id': merchant_id})
        time_start_day = time.mktime(
            datetime.strptime(time_day, "%m/%d/%y").timetuple())
        users_in_report = DATABASE.visit_log.distinct('user_id', {'shop_id': {'$in': shops},
                                                                  'timestamp': {'$gte': time_start_day,
                                                                                '$lt': timestamp}})
        if user_id in users_in_report:
            return False
        else:
            return True
    else:
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        time_start_day = time.mktime(
            datetime.strptime(time_day, "%m/%d/%y").timetuple())
        users_in_report = DATABASE.visit_log.distinct('user_id', {'shop_id': shop_id,
                                                                  'timestamp': {'$gte': time_start_day,
                                                                                '$lt': timestamp}})
        if ObjectId(user_id) in users_in_report:
            return False
        else:
            return True


def check_key_account_vcall(api_key, api_secret):
    url = 'https://acd-api.vht.com.vn/rest/cdrs'
    token = b64encode(str(api_key) + ':' + str(api_secret))
    headers = {
        'Authorization': 'Basic ' + token
    }
    result = requests.get(url=url, headers=headers)
    if str(result.status_code) != '200':
        return False
    else:
        return True


def check_app_pos(merchant_id=None, name_app=None, type_app=None):
    return DATABASE.app_synchronized.find_one(
        {'type_app': type_app, 'name_app': name_app, 'merchant_id': str(merchant_id)})


def check_access_token_loop(access_token):
    url = 'https://api.loop.vn/v2.1/partners/verify/{}'.format(access_token)
    key = 'Bearer ' + str(access_token)
    headers = {'Authorization': key, 'Content-Type': 'application/json'}

    result = requests.post(url=url, headers=headers)
    if result.status_code != 200:
        return False
    else:
        return True


def get_access_token_loop(access_token):
    url = 'https://beta-api.loop.vn/v2.1/partners/access-token?token={}'.format(
        access_token)
    result = requests.get(url=url)
    try:
        return result.text.strip('"')
    except:
        return result.text


def check_app_synchronized_pos(merchant_id):
    app = DATABASE.app_synchronized.find_one({'merchant_id': merchant_id,
                                              'type_app': 'POS',
                                              'status': 'True'})
    if app:
        return app
    else:
        return False


def update_shop_priority_splash(shop_id, data):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.shop.update_one({'_id': shop_id}, {'$set': {'priority_splash': data,
                                                                'updated_at': time.time()}})


def update_shop_priority_splash_with_status(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    priority_splash = DATABASE.shop.find_one(
        {'_id': shop_id}).get('priority_splash')
    result = ['register']
    if priority_splash:
        for splash in priority_splash:
            type_page = splash.get('type_page')
            if type_page == 'survey':
                survey = DATABASE.survey_splash_page.find_one(
                    {'shop_id': shop_id, 'active': True})
                if survey:
                    result.append(type_page)
            elif type_page == 'plus_register':
                plus_login_form = DATABASE.shop.find_one(
                    {'_id': shop_id}).get('plus_login_form')
                if plus_login_form and plus_login_form.get('status'):
                    result.append('plus_register')
            else:
                page = DATABASE.splash_page.find_one(
                    {'shop_id': shop_id, 'type_page': type_page, 'active': True})
                if page:
                    result.append(type_page)
    else:
        priority_splash = ['survey', 'birthday', 'weekday', 'hour', 'promotion', 'tag', 'loyal', 'plus_register',
                           'default']
        result = []
        for splash in priority_splash:
            type_page = splash
            if type_page == 'survey':
                survey = DATABASE.survey_splash_page.find_one(
                    {'shop_id': shop_id, 'active': True})
                if survey:
                    result.append(type_page)
            elif type_page == 'plus_register':
                plus_login_form = DATABASE.shop.find_one(
                    {'_id': shop_id}).get('plus_login_form')
                if plus_login_form and plus_login_form.get('status'):
                    result.append('plus_register')
            else:
                page = DATABASE.splash_page.find_one(
                    {'shop_id': shop_id, 'type_page': type_page, 'active': True})
                if page:
                    result.append(type_page)
    ignore_register = DATABASE.shop.find_one(
        {'_id': shop_id}).get('ignore_register')
    if ignore_register and ignore_register == 'True':
        try:
            result.remove('register')
            result.remove('plus_register')
        except:
            pass
    return DATABASE.shop.update_one({'_id': shop_id}, {'$set': {'priority_splash_status': result,
                                                                'updated_at': time.time()}})


def get_priority_splash_by_shop_id(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = DATABASE.shop.find_one({'_id': shop_id})
    if shop:
        priority_splash = shop.get('priority_splash')
        if priority_splash:
            return priority_splash
        else:
            return False
    else:
        return False


def get_comment_anvui(
        shop_id=None,
        survey_id=None,
        page=None,
        page_size=settings.ITEMS_PER_PAGE_CALL):
    comments = []
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(survey_id, ObjectId):
        survey_id = ObjectId(survey_id)
    recs = DATABASE.survey_result.find({'shop_id': shop_id, 'survey_id': survey_id}).sort('when', -1).skip(
        page_size * (int(page) - 1)).limit(page_size)
    for rec in recs:
        kq = {}
        client_mac = rec.get('client_mac')
        comment = rec.get('comment')
        answers = rec.get('answers')
        timestamp = rec.get('when')
        info = get_user_info(client_mac=client_mac)
        name = info.get('name', " ")
        phone = info.get('phone', " ")
        time = arrow.get(timestamp).humanize(locale='vi_vn')
        if name and phone:
            if not comment or str(comment) == 'None' or str(comment) == 'none':
                comment = ''
            kq['name'] = name
            kq['phone'] = phone
            kq['comment'] = comment
            kq['time'] = time
            kq['answers'] = answers
            comments.append(kq)
    return comments


def get_comment(merchant_id, shop_id, source, page, page_size, star):
    comments = []
    recs = None
    if not star:
        # if source == 'all':
        if shop_id == 'all':
            shops = get_shop_by_merchant_commet(merchant_id)
            recs = DATABASE.survey_result.find(
                {'shop_id': {"$in": shops}, 'survey_type': 'rating', 'source': None}).sort('when', -1).skip(
                page_size * (int(page) - 1)).limit(page_size)
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            recs = DATABASE.survey_result.find({'shop_id': shop_id, 'survey_type': 'rating', 'source': None}).sort(
                'when', -1).skip(
                page_size * (int(page) - 1)).limit(page_size)
        # else:
        #     if shop_id == 'all':
        #         if source == 'Wifi':
        #             shops = get_shop_by_merchant_commet(merchant_id)
        #             recs = DATABASE.survey_result.find(
        #                 {'shop_id': {"$in": shops}, "survey_type": "rating", "source": None}).sort('when', -1).skip(
        #                 page_size * (int(page) - 1)).limit(page_size)
        #         else:
        #             shops = get_shop_by_merchant_commet(merchant_id)
        #             recs = DATABASE.survey_result.find(
        #                 {'shop_id': {"$in": shops}, "survey_type": "rating", "source": source}).sort('when', -1).skip(
        #                 page_size * (int(page) - 1)).limit(page_size)
        #     else:
        #         if source == "Wifi":
        #             if not isinstance(shop_id, ObjectId):
        #                 shop_id = ObjectId(shop_id)
        #             recs = DATABASE.survey_result.find(
        #                 {'shop_id': shop_id, "survey_type": "rating", "source": None}).sort('when', -1).skip(
        #                 page_size * (int(page) - 1)).limit(page_size)
        #         else:
        #             if not isinstance(shop_id, ObjectId):
        #                 shop_id = ObjectId(shop_id)
        #             recs = DATABASE.survey_result.find(
        #                 {'shop_id': shop_id, "survey_type": "rating", "source": source}).sort('when', -1).skip(
        #                 page_size * (int(page) - 1)).limit(page_size)
    else:
        # if source == 'all':
        if shop_id == 'all':
            shops = get_shop_by_merchant_commet(merchant_id)
            recs = DATABASE.survey_result.find(
                {'shop_id': {"$in": shops}, 'survey_type': 'rating', 'source': None,
                 "answers": {"$in": [str(star), int(star)]}}) \
                .sort('when', -1).skip(page_size * (int(page) - 1)).limit(page_size)
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            recs = DATABASE.survey_result.find(
                {'shop_id': shop_id, 'survey_type': 'rating', 'source': None,
                 "answers": {"$in": [str(star), int(star)]}}) \
                .sort('when', -1).skip(
                page_size * (int(page) - 1)).limit(page_size)
        # else:
        #     if shop_id == 'all':
        #         if source == 'Wifi':
        #             shops = get_shop_by_merchant_commet(merchant_id)
        #             recs = DATABASE.survey_result.find(
        #                 {'shop_id': {"$in": shops}, "survey_type": "rating", "source": None,
        #                  "answers": {"$in": [str(star), int(star)]}}) \
        #                 .sort('when', -1).skip(page_size * (int(page) - 1)).limit(page_size)
        #         else:
        #             shops = get_shop_by_merchant_commet(merchant_id)
        #             recs = DATABASE.survey_result.find(
        #                 {'shop_id': {"$in": shops}, "survey_type": "rating", "source": source,
        #                  "answers": {"$in": [str(star), int(star)]}}) \
        #                 .sort('when', -1).skip(page_size * (int(page) - 1)).limit(page_size)
        #     else:
        #         if source == "Wifi":
        #             if not isinstance(shop_id, ObjectId):
        #                 shop_id = ObjectId(shop_id)
        #             recs = DATABASE.survey_result.find({'shop_id': shop_id, "survey_type": "rating", "source": None,
        #                                                 "answers": {"$in": [str(star), int(star)]}}) \
        #                 .sort('when', -1).skip(
        #                 page_size * (int(page) - 1)).limit(page_size)
        #         else:
        #             if not isinstance(shop_id, ObjectId):
        #                 shop_id = ObjectId(shop_id)
        #             recs = DATABASE.survey_result.find({'shop_id': shop_id, "survey_type": "rating", "source": source,
        #                                                 "answers": {"$in": [str(star), int(star)]}}) \
        #                 .sort('when', -1).skip(
        #                 page_size * (int(page) - 1)).limit(page_size)
    for rec in recs:
        client_mac = rec.get('client_mac')
        answers = int(rec.get('answers')[0]) if isinstance(
            rec.get('answers'), list) else int(rec.get('answers'))
        rec['answers'] = answers
        timestamp = rec.get('when')
        if client_mac:
            info_user = handle_customers.get_user_merchant_by_mac(
                merchant_id=merchant_id, client_mac=client_mac)
            if info_user:
                info = info_user.get("user")
                name = info.get('name', " ")
                email = info.get('email')
                avatar = info.get('avatar', '')
                phone = info.get('phone', " ")
                rec['name'] = name
                rec['email'] = email
                rec['phone'] = phone
                rec['avatar'] = avatar
            time = arrow.get(timestamp + 7 * 3600).humanize(locale='vi_vn')
            rec['time_create'] = time
            rec['human_time'] = datetime.utcfromtimestamp(
                timestamp + 7 * 3600).strftime('%H:%M  %d-%m-%Y')
        else:
            if rec.get('source') == "Facebook":
                time_create = arrow.get(
                    timestamp + 7 * 3600).humanize(locale='vi_vn')
                rec['time_create'] = time_create
                human_time = rec.get('human_time')
                # Data truoc khi chua sua function get_detail_view_fb chua co field human_time
                if not human_time:
                    rec['human_time'] = datetime.utcfromtimestamp(
                        timestamp + 7 * 3600).strftime('%H:%M  %d-%m-%Y')
            if rec.get('source') == "Google":
                time_create = arrow.get(
                    timestamp + 7 * 3600).humanize(locale='vi_vn')
                rec['time_create'] = time_create
        comments.append(rec)
    return comments


def get_total_rating(merchant_id, shop_id, source, star):
    if not star:
        # if source == 'all':
        if shop_id == 'all':
            shop_in_mer = get_shop_by_merchant_commet(merchant_id)
            total_rating = DATABASE.survey_result.find(
                {'shop_id': {"$in": shop_in_mer}, 'survey_type': 'rating', 'source': None}).count()
            return total_rating
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            total_rating = DATABASE.survey_result.find(
                {'shop_id': shop_id, 'survey_type': 'rating', 'source': None}).count()
            return total_rating
        # else:
        #     if shop_id == 'all':
        #         shop_in_mer = get_shop_by_merchant_commet(merchant_id)
        #         total_rating = DATABASE.survey_result.find(
        #             {'shop_id': {"$in": shop_in_mer}, "survey_type": "rating", "source": source}).count()
        #         return total_rating
        #     else:
        #         if not isinstance(shop_id, ObjectId):
        #             shop_id = ObjectId(shop_id)
        #         total_rating = DATABASE.survey_result.find(
        #             {'shop_id': shop_id, "survey_type": "rating", "source": source}).count()
        #         return total_rating
    else:
        # if source == 'all':
        if shop_id == 'all':
            shop_in_mer = get_shop_by_merchant_commet(merchant_id)
            total_rating = DATABASE.survey_result.find(
                {'shop_id': {"$in": shop_in_mer}, 'survey_type': 'rating', 'source': None,
                 "answers": {"$in": [str(star), int(star)]}}).count()
            return total_rating
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            total_rating = DATABASE.survey_result.find(
                {'shop_id': shop_id, 'survey_type': 'rating', 'source': None,
                 "answers": {"$in": [str(star), int(star)]}}).count()
            return total_rating
        # else:
        #     if shop_id == 'all':
        #         shop_in_mer = get_shop_by_merchant_commet(merchant_id)
        #         total_rating = DATABASE.survey_result.find(
        #             {'shop_id': {"$in": shop_in_mer}, "survey_type": "rating", "source": source,
        #              "answers": {"$in": [str(star), int(star)]}}).count()
        #         return total_rating
        #     else:
        #         if not isinstance(shop_id, ObjectId):
        #             shop_id = ObjectId(shop_id)
        #         total_rating = DATABASE.survey_result.find(
        #             {'shop_id': shop_id, "survey_type": "rating", "source": source,
        #              "answers": {"$in": [str(star), int(star)]}}).count()
        #         return total_rating


def sum_rating(merchant_id, shop_id, source, star):
    if not star:
        # if source == 'all':
        if shop_id == 'all':
            shop_in_mer = get_shop_by_merchant_commet(merchant_id)
            survey_result = DATABASE.survey_result.find(
                {'shop_id': {"$in": shop_in_mer}, 'survey_type': 'rating', 'source': None})
            sum_rating = 0
            for survey in survey_result:
                answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
                    survey.get('answers'))
                sum_rating += answers
            return sum_rating
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            survey_result = DATABASE.survey_result.find(
                {'shop_id': shop_id, 'survey_type': 'rating', 'source': None})
            sum_rating = 0
            for survey in survey_result:
                answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
                    survey.get('answers'))
                sum_rating += answers
            return sum_rating
        # else:
        #     if shop_id == 'all':
        #         shop_in_mer = get_shop_by_merchant_commet(merchant_id)
        #         survey_result = DATABASE.survey_result.find(
        #             {'shop_id': {"$in": shop_in_mer}, "survey_type": "rating", "source": source})
        #         sum_rating = 0
        #         for survey in survey_result:
        #             answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
        #                 survey.get('answers'))
        #             sum_rating += answers
        #         return sum_rating
        #     else:
        #         if not isinstance(shop_id, ObjectId):
        #             shop_id = ObjectId(shop_id)
        #         survey_result = DATABASE.survey_result.find(
        #             {'shop_id': shop_id, "survey_type": "rating", "source": source})
        #         sum_rating = 0
        #         for survey in survey_result:
        #             answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
        #                 survey.get('answers'))
        #             sum_rating += answers
        #         return sum_rating
    else:
        # if source == 'all':
        if shop_id == 'all':
            shop_in_mer = get_shop_by_merchant_commet(merchant_id)
            survey_result = DATABASE.survey_result.find(
                {'shop_id': {"$in": shop_in_mer}, 'survey_type': 'rating', 'source': None,
                 "answers": {"$in": [str(star), int(star)]}})
            sum_rating = 0
            for survey in survey_result:
                answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
                    survey.get('answers'))
                sum_rating += answers
            return sum_rating
        else:
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            survey_result = DATABASE.survey_result.find(
                {'shop_id': shop_id, 'survey_type': 'rating', 'source': None,
                 "answers": {"$in": [str(star), int(star)]}})
            sum_rating = 0
            for survey in survey_result:
                answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
                    survey.get('answers'))
                sum_rating += answers
            return sum_rating
        # else:
        #     if shop_id == 'all':
        #         shop_in_mer = get_shop_by_merchant_commet(merchant_id)
        #         survey_result = DATABASE.survey_result.find(
        #             {'shop_id': {"$in": shop_in_mer}, "survey_type": "rating", "source": source,
        #              "answers": {"$in": [str(star), int(star)]}})
        #         sum_rating = 0
        #         for survey in survey_result:
        #             answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
        #                 survey.get('answers'))
        #             sum_rating += answers
        #         return sum_rating
        #     else:
        #         if not isinstance(shop_id, ObjectId):
        #             shop_id = ObjectId(shop_id)
        #         survey_result = DATABASE.survey_result.find(
        #             {'shop_id': shop_id, "survey_type": "rating", "source": source,
        #              "answers": {"$in": [str(star), int(star)]}})
        #         sum_rating = 0
        #         for survey in survey_result:
        #             answers = int(survey.get('answers')[0]) if isinstance(survey.get('answers'), list) else int(
        #                 survey.get('answers'))
        #             sum_rating += answers
        #         return sum_rating


def delete_app(app_id):
    if not isinstance(app_id, ObjectId):
        app_id = ObjectId(app_id)
    DATABASE.app_synchronized.delete_one({"_id": app_id})


def update_status_account(name_app, merchant_id, account_id):
    DATABASE.app_synchronized.update_one({'merchant_id': merchant_id,
                                          'name_app': name_app,
                                          'setting.info.account_id': account_id},
                                         {'$set': {
                                             'status': "False",
                                             'setting.info.$.status_account': "False"
                                         }
    })


def save_page_facebook(merchant_id, fb_user_id, access_token):
    url = "https://graph.facebook.com/v5.0/{}/accounts?access_token={}".format(
        fb_user_id, access_token)
    result = requests.get(url=url)
    data = json.loads(result.text).get('data')
    for subdata in data:
        access_token_page = subdata.get('access_token')
        name_page = subdata.get('name')
        id_page = subdata.get('id')
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        info = {'merchant_id': merchant_id,
                'id_user_fb': fb_user_id,
                'page': [{'id_page': id_page,
                          'name_page': name_page,
                          'access_token_page': access_token_page}]
                }
        check_mer = DATABASE.fb_info_pages.find_one(
            {'merchant_id': merchant_id})
        if check_mer:
            check_user = DATABASE.fb_info_pages.find_one(
                {'id_user_fb': fb_user_id})
            if check_user:
                check_merchant = check_mer.get('merchant_id')
                user = check_user.get('id_user_fb')
                if check_merchant == merchant_id and user == fb_user_id:
                    check_name_page = check_mer.get('page')
                    check_pages = []
                    for check_page in check_name_page:
                        check_id_page = check_page.get('id_page')
                        check_pages.append(check_id_page)
                    if str(id_page) in check_pages:
                        DATABASE.fb_info_pages.update({'page.id_page': id_page},
                                                      {'$set': {'page.$.name_page': name_page,
                                                                'page.$.access_token_page': access_token_page}})
                    else:
                        DATABASE.fb_info_pages.update({'merchant_id': merchant_id},
                                                      {'$addToSet': {'page': {'id_page': id_page,
                                                                              'name_page': name_page,
                                                                              'access_token_page': access_token_page}}})
                if check_merchant == merchant_id and user != fb_user_id:
                    DATABASE.fb_info_pages.insert(info)
            else:
                DATABASE.fb_info_pages.update({'merchant_id': merchant_id}, {"$set": {'id_user_fb': fb_user_id,
                                                                                      'page': [{'id_page': id_page,
                                                                                                'name_page': name_page,
                                                                                                'access_token_page': access_token_page}]}})
        else:
            DATABASE.fb_info_pages.insert(info)


def get_pagefb_by_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    recs = DATABASE.fb_info_pages.find_one({'merchant_id': merchant_id})
    pages = ""
    if recs:
        pages = recs.get('page')
    return pages


def get_access_token_page(id_page):
    recs = DATABASE.fb_info_pages.find_one({'page.id_page': id_page})
    if recs:
        pages = recs.get('page')
        for page in pages:
            check_id_page = page.get('id_page')
            if str(check_id_page) == str(id_page):
                return page.get('access_token_page')


def get_detail_review_fb(shop_id, access_token_page, id_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info_shop = DATABASE.shop.find_one({'_id': shop_id})
    if info_shop:
        merchant_id = info_shop.get('merchant_id')
        url = settings.FACBOOK_GRAPH_API + '/{}/ratings?fields=created_time,recommendation_type,rating,review_text,{}&access_token={}'.format(
            id_page, "reviewer{picture,name}", access_token_page)
        result = requests.get(url=url)
        if result.status_code == 200:
            data = json.loads(result.text).get('data')
            if data:
                for sub in data:
                    name = sub.get('reviewer').get('name')
                    picture = sub.get('reviewer').get(
                        'picture').get('data').get('url')
                    try:
                        user_profile_picture = picture
                        picture_reading = requests.get(
                            url=user_profile_picture)
                        user_profile_photo = picture_reading.content
                        profile_picture_init_name = str(
                            shop_id) + '_' + str(time.time())
                        profile_photo_origin_name = 'profile_photo_{}.jpg'.format(
                            profile_picture_init_name)
                        profile_photo_name = \
                            md5(user_profile_photo).hexdigest() + '.' + \
                            profile_photo_origin_name.rsplit('.', 1)[1]
                        profile_photo_data = {
                            'file_name': profile_photo_name,
                            'file_data': b64encode(user_profile_photo),
                            'origin_name': profile_photo_origin_name
                        }
                        storage_api.save_file(profile_photo_data)
                        avatar = "https://static.nextify.vn/images/" + \
                            profile_photo_name + "/thumb/original"
                    except Exception as e:
                        print(e)
                        avatar = picture
                        pass
                    text = sub.get('review_text')
                    when = time.mktime(dateutil.parser.parse(
                        sub.get("created_time")).timetuple())
                    human_time = datetime.utcfromtimestamp(
                        when).strftime('%H:%M  %d-%m-%Y')
                    id_reviewer = sub.get('reviewer').get('id')
                    type_comment = sub.get('recommendation_type')
                    rating = sub.get('rating')
                    if not rating and type_comment == "negative":
                        rating = 1
                    if not rating and type_comment == "positive":
                        rating = 5
                    if not isinstance(merchant_id, ObjectId):
                        merchant_id = ObjectId(merchant_id)
                    info = {'merchant_id': merchant_id,
                            'shop_id': shop_id,
                            'id_page': id_page,
                            'name': name,
                            'avatar': avatar,
                            'human_time': human_time,
                            'when': when,
                            'comment': text,
                            'id_reviewer': id_reviewer,
                            'type_comment': type_comment,
                            'answers': rating,
                            'source': "Facebook",
                            'survey_type': 'rating'}

                    check_rating = DATABASE.survey_result.find_one(
                        {'id_reviewer': id_reviewer, 'merchant_id': merchant_id})
                    if not check_rating:
                        DATABASE.survey_result.insert(info)


def get_merchant_mobio(mobio_id_merchant):
    merchant = DATABASE.merchants.find_one(
        {'mobio_id_merchant': mobio_id_merchant})
    return merchant


def get_dealers_by_api_key(api_key):
    dealer = DATABASE.dealers.find_one({'nextify_key': api_key})
    return dealer


def get_detail_review_google(shop_id, place_id):
    key_google_map = "AIzaSyDKheYh904BxCfN4E-6hr4URz8Bx5oFrsc"
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info_shop = DATABASE.shop.find_one({'_id': shop_id})
    if info_shop:
        place_id = info_shop.get('place_id')
        merchant_id = info_shop.get('merchant_id')
        url = "https://maps.googleapis.com/maps/api/place/details/json?place_id={}&fields=name,rating,formatted_phone_number,reviews&key={}".format(
            place_id, key_google_map)
        result = requests.get(url=url)
        if result.status_code == 200:
            try:
                data = json.loads(result.text).get('result').get('reviews')
                if data:
                    for review in data:
                        name = review.get('author_name')
                        picture = review.get('profile_photo_url')
                        text = review.get('text')
                        when = review.get('time')
                        human_time = datetime.utcfromtimestamp(
                            when + 7 * 3600).strftime('%H:%M  %d-%m-%Y')
                        rating = review.get('rating')
                        id_reviewer = review.get('author_url')
                        info = {'merchant_id': merchant_id,
                                'shop_id': shop_id,
                                'place_id': place_id,
                                'name': name,
                                'avatar': picture,
                                'human_time': human_time,
                                'when': when,
                                'comment': text,
                                'id_reviewer': id_reviewer,
                                'answers': rating,
                                'source': "Google",
                                'survey_type': 'rating'}
                        check_rating = DATABASE.survey_result.find_one(
                            {'id_reviewer': id_reviewer})
                        if check_rating:
                            continue
                        else:
                            DATABASE.survey_result.insert(info)
            except:
                pass


def check_double_fb(id_page=None, shop_id_select=None, place_id=None):
    if not isinstance(shop_id_select, ObjectId):
        shop_id_select = ObjectId(shop_id_select)
    if id_page:
        info_shop = DATABASE.shop.find_one({'id_page': id_page})
    if place_id:
        info_shop = DATABASE.shop.find_one({'place_id': place_id})
    if info_shop:
        shop_id = info_shop.get('_id')
        if str(shop_id) == str(shop_id_select):
            return True
        else:
            return False
    else:
        return True


def check_facebook_has_page(id_page):
    info_shop = DATABASE.shop.find_one({'id_page': id_page})
    if info_shop:
        return True
    else:
        return False


def facebook_lead_ad(page_id, access_token_page):
    url = "https://graph.facebook.com/v5.0/{}/subscribed_apps?subscribed_fields=leadgen,leadgen_fat&access_token={}".format(
        page_id, access_token_page)
    requests.post(url=url)


def delete_all_app(merchant_id, type_app):
    return DATABASE.app_synchronized.delete_many({'merchant_id': merchant_id, 'type_app': type_app})


def update_all_merchant_id_app(merchant_id_app):
    merchants = DATABASE.merchants.find({'merchant_id_app': merchant_id_app})
    for merchant in merchants:
        _id = merchant.get('_id')
        DATABASE.merchants.update_one(
            {'_id': _id}, {'$set': {'merchant_id_app': ''}})


def update_merchant_id_app(merchant_id, merchant_id_app):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.merchants.update_one({'_id': merchant_id},
                                         {'$set': {'merchant_id_app': merchant_id_app, 'update_at': time.time()}})


def save_botup_setting(merchant_id, data_shop):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    for shop_id in data_shop:
        DATABASE.shop.update({'_id': ObjectId(str(shop_id.get('shop_id')))}, {'$set': {'bot_up': {
            'active': shop_id.get('active'),
            'link': shop_id.get('link'),
            'updated_at': time.time()
        }}})
        if shop_id.get('active') and len(shop_id.get('link')) == 0:
            DATABASE.shop.update({'_id': ObjectId(str(shop_id.get('shop_id')))}, {'$set': {'bot_up': {
                'active': False,
                'link': shop_id.get('link'),
                'updated_at': time.time()
            }}})


def apply_merchant_botup(merchant_id, data):
    shop_in_mer = get_shop_by_merchant(str(merchant_id))
    if len(data) > 0:
        for shop in shop_in_mer:
            DATABASE.shop.update({'_id': ObjectId(str(shop.get('_id')))}, {'$set': {'bot_up': {
                'active': True,
                'link': data,
                'updated_at': time.time()
            }}})
    else:
        for shop in shop_in_mer:
            DATABASE.shop.update({'_id': ObjectId(str(shop.get('_id')))}, {'$set': {'bot_up': {
                'active': False,
                'link': data,
                'updated_at': time.time()
            }}})


def get_cus_by_id(cus_id, merchant_id=None):
    if not isinstance(cus_id, ObjectId):
        cus_id = ObjectId(cus_id)
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        DATABASE.customers.find_one(
            {'_id': cus_id, 'merchant_id': merchant_id})
    return DATABASE.customers.find_one({'_id': cus_id})


def get_cus_loc_by_id(cus_id):
    if not isinstance(cus_id, ObjectId):
        cus_id = ObjectId(cus_id)
    return DATABASE.customers_location.find_one({'_id': cus_id})


def update_connect_success(shop_id, content, connect_button, auto_popup, hotspot_method,
                           default_code, display_coupon, display_coupon_txt):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {}
    if str(content) != 'None':
        info['content'] = content
    if str(connect_button) != 'None':
        info['connect_button'] = connect_button
    if str(auto_popup) != 'None':
        info['auto_popup'] = auto_popup
    if str(hotspot_method) != 'None':
        info['hotspot_method'] = hotspot_method
    if str(default_code) != 'None':
        info['default_code'] = default_code
    if str(display_coupon) != 'None':
        info['display_coupon'] = display_coupon
    if str(display_coupon_txt) != 'None':
        info['display_coupon_txt'] = display_coupon_txt
    return DATABASE.shop.update_one({'_id': shop_id}, {'$set': {'connect_success': info, 'updated_at': time.time()}})


def update_method_shop(shop_id, welcome_member_text_splash=None, connect_button=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.shop.update_one(
        {'_id': shop_id},
        {'$set': {
            'welcome_member_text_splash': welcome_member_text_splash,
            'connect_button': connect_button,
            'updated_at': time.time()
        }})


def save_setting_rating(merchant_id,
                        shop_id,
                        url_facebook=None,
                        url_google=None,
                        url_tripadvisor=None,
                        content_rating=None,
                        check_facebook=None,
                        check_google=None,
                        check_tripadvisor=None):
    info = {}
    info['url_facebook'] = url_facebook
    info['url_google'] = url_google
    info['url_tripadvisor'] = url_tripadvisor
    info['content_rating'] = content_rating
    info['check_facebook'] = check_facebook
    info['check_google'] = check_google
    info['check_tripadvisor'] = check_tripadvisor
    if len(info['url_facebook']) == 0:
        info['check_facebook'] = 'false'
    if len(info['url_google']) == 0:
        info['check_google'] = "false"
    if len(info['url_tripadvisor']) == 0:
        info['check_tripadvisor'] = "false"
    if shop_id != "all":
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.shop.update_one({'_id': shop_id}, {'$set': {'setting_rating': info}})
    if shop_id == "all":
        shops = DATABASE.shop.find({'merchant_id': str(merchant_id)})
        for shop in shops:
            id_shop = shop.get('_id')
            DATABASE.shop.update_one({'_id': id_shop}, {
                                     '$set': {'setting_rating': info, 'updated_at': time.time()}})


def filter_campaign(merchant_id,
                    shop_id=None,
                    from_date=None,
                    to_date=None,
                    is_email=None,
                    is_sms=None,
                    is_zalo=None,
                    min_visit=None,
                    max_visit=None,
                    lost_day=None,
                    employee=None,
                    gender=None,
                    sort=None,
                    bday_from_date=None,
                    bday_to_date=None,
                    tags_array=None,
                    page=None,
                    active_zns=None,
                    page_size=None):
    info = {}
    if shop_id or str(shop_id) != 'all':
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        info['shop_id'] = shop_id
    else:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        info['merchant_id'] = merchant_id

    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        info['last_visit'] = {}
        info['last_visit']['$gte'] = from_tmp

    if to_date and to_date != 'None' and 'last_visit' in info:
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        info['last_visit']['$lte'] = to_tmp

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)

    if min_visit and str(min_visit) != 'None' and len(min_visit) == 0:
        if max_visit and str(max_visit) != 'None' and len(max_visit) > 0:
            info['total_visit'] = {}
            info['total_visit']['$lte'] = int(max_visit)

    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)
        info['user.birthday'] = {'$in': days}

    if lost_day and str(lost_day) != 'None' and int(lost_day) > 0:
        lost_day_start = time.time() - int(lost_day) * 86400
        info['last_visit'] = {'$lte': lost_day_start}

    if gender and len(gender) > 0 and str(gender) != 'None':
        info['user.gender'] = {'$in': gender}
    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'

    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
    null_arr = ['', 'null', 'None', 'none', None]
    if isinstance(is_email, bool) and not isinstance(is_sms, bool):
        if is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
    elif isinstance(is_sms, bool) and not isinstance(is_email, bool):
        if is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    elif isinstance(is_zalo, bool) and not isinstance(is_zalo, bool):
        if is_zalo:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    else:
        if is_email and is_sms:
            info['$or'] = [
                {'user.phone': {'$exists': True, '$nin': null_arr}},
                {'user.email': {'$exists': True, '$nin': null_arr}}
            ]
        elif is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
        elif is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
        elif is_zalo:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    recs = []
    if not page:
        if not shop_id or str(shop_id) == 'all':
            recs = DATABASE.customers.find(
                info, no_cursor_timeout=True).sort('last_visit', -1)
        else:
            recs = DATABASE.customers_location.find(
                info, no_cursor_timeout=True).sort('last_visit', -1)
            if is_zalo and active_zns == "off":
                result = []
                for rec in recs:
                    cus_phone = rec.get('user').get('phone')
                    user_id_zalo = rec.get('user').get('user_id_zalo')
                    # check_follow_oa = check_phone_follow_zaloOA(shop_id, str(cus_phone))
                    # if check_follow_oa:
                    if cus_phone and user_id_zalo and len(str(user_id_zalo)) > 0:
                        result.append(rec)
                return result
        return [rec for rec in recs]
    else:
        if sort and sort == 'visit_asc':
            if not shop_id or str(shop_id) == 'all':
                recs = DATABASE.customers.find(info).sort('total_visit', -1).skip(page_size * (page - 1)) \
                    .limit(page_size)
                real = DATABASE.customers.count(info)
                return [rec for rec in recs], real
            else:
                recs = DATABASE.customers_location.find(info).sort('total_visit', -1).skip(page_size * (page - 1)) \
                    .limit(page_size)
                real = DATABASE.customers_location.count(info)
                if is_zalo and active_zns == "off":
                    result = []
                    customers = DATABASE.customers_location.find(
                        info).sort('last_visit', -1)
                    for rec in customers:
                        cus_phone = rec.get('user').get('phone')
                        user_id_zalo = rec.get('user').get('user_id_zalo')
                        # check_follow_oa = check_phone_follow_zaloOA(shop_id, str(cus_phone))
                        # if check_follow_oa:
                        if cus_phone and user_id_zalo and len(str(user_id_zalo)) > 0:
                            result.append(rec)
                    return result[(page - 1) * page_size: page * page_size - 1], len(result)
                return [rec for rec in recs], real
        else:
            if not shop_id or str(shop_id) == 'all':
                recs = DATABASE.customers.find(info).sort('last_visit', -1).skip(page_size * (page - 1)) \
                    .limit(page_size)
                real = DATABASE.customers.count(info)
                return [rec for rec in recs], real
            else:
                recs = DATABASE.customers_location.find(info).sort('last_visit', -1).skip(page_size * (page - 1)) \
                    .limit(page_size)
                real = DATABASE.customers_location.count(info)
                if is_zalo and active_zns == "off":
                    result = []
                    customers = DATABASE.customers_location.find(
                        info).sort('last_visit', -1)
                    for rec in customers:
                        cus_phone = rec.get('user').get('phone')
                        user_id_zalo = rec.get('user').get('user_id_zalo')
                        # check_follow_oa = check_phone_follow_zaloOA(shop_id, str(cus_phone))
                        # if check_follow_oa:
                        if cus_phone and user_id_zalo and len(str(user_id_zalo)) > 0:
                            result.append(rec)
                    return result[(page - 1) * page_size: page * page_size - 1], len(result)
                return [rec for rec in recs], real


def email_example_by_type(select_branch, page=None):
    page_size = 8
    if select_branch == "all":
        return DATABASE.email_sample_template.find().sort('when', -1).skip(page_size * (page - 1)).limit(page_size)
    else:
        return DATABASE.email_sample_template.find({"type_branch": select_branch}).sort('when', -1).skip(
            page_size * (page - 1)).limit(page_size)


def count_email_example(select_branch):
    if select_branch == "all":
        return DATABASE.email_sample_template.find().count()
    else:
        return DATABASE.email_sample_template.find({'type_branch': select_branch}).count()


def remove_survey_result(remove_survey_result_id):
    if not isinstance(remove_survey_result_id, ObjectId):
        remove_survey_result_id = ObjectId(remove_survey_result_id)
    DATABASE.survey_result.remove({'_id': remove_survey_result_id})


def arr_splash(data):
    try:
        arr_uni = data[1:len(data) - 1]
        result = [str(item.strip().strip('"')) for item in arr_uni.split(",")]
    except:
        result = []
    return result


def save_hotspot_campaign(shop_id,
                          status_campaign,
                          name_camp,
                          step_1,
                          step_2,
                          step_3,
                          survey_step_1,
                          survey_step_2,
                          survey_step_3,
                          spin_step_1,
                          spin_step_2,
                          spin_step_3,
                          min_visit=None,
                          max_visit=None,
                          camp_tags_selects=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'name': name_camp,
        'created_at': time.time(),
        'shop_id': shop_id,
        'step_1': step_1,
        'step_2': step_2,
        'step_3': step_3,
        'status': status_campaign,
        'step_4': 'connect_success',
        'campaign_type': 'default',
        'min_visit': min_visit,
        'max_visit': max_visit,
        'camp_tags_selects': camp_tags_selects
    }
    if min_visit and str(min_visit) != 'None':
        info['min_visit'] = min_visit
    if max_visit and str(max_visit) != 'None':
        info['max_visit'] = max_visit
    if camp_tags_selects and str(camp_tags_selects) != 'None':
        info['camp_tags_selects'] = camp_tags_selects
    if str(step_1) == 'survey' and survey_step_1:
        info['survey_step_1'] = survey_step_1
    if str(step_2) == 'survey' and survey_step_2:
        info['survey_step_2'] = survey_step_2
    if str(step_3) == 'survey' and survey_step_3:
        info['survey_step_3'] = survey_step_3
    if str(step_1) == 'spin' and spin_step_1:
        info['spin_step_1'] = spin_step_1
    if str(step_2) == 'spin' and spin_step_2:
        info['spin_step_2'] = spin_step_2
    if str(step_3) == 'spin' and spin_step_3:
        info['spin_step_3'] = spin_step_3
    if status_campaign:
        max_sequence = DATABASE.hotspot_campaign.find(
            {'shop_id': shop_id, 'campaign_type': 'default', 'status': True}).count()
        info['sequence'] = max_sequence
    camp_id = DATABASE.hotspot_campaign.insert(info)
    # if status_campaign:
    #     camps = [camp_id]
    #     DATABASE.hotspot_campaign.update_many({'_id': {'$nin': camps}, 'campaign_type': 'default', 'shop_id': shop_id},
    #                                           {'$set': {'status': False}})


def update_hotspot_campaign(camp_id,
                            shop_id,
                            status=None,
                            name_camp=None,
                            step_1=None,
                            step_2=None,
                            step_3=None,
                            survey_step_1=None,
                            survey_step_2=None,
                            survey_step_3=None,
                            auto_popup=None,
                            spin_step_1=None,
                            spin_step_2=None,
                            spin_step_3=None,
                            min_visit=None,
                            max_visit=None,
                            camp_tags_selects=None,
                            status_campaign=None,
                            ):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = {
        'updated_at': time.time(),
        'step_4': 'connect_success',
    }
    if str(status) != 'None':
        info['status'] = status

    if str(name_camp) != 'None':
        info['name'] = name_camp

    if str(auto_popup) != 'None':
        info['auto_popup'] = auto_popup
    info['step_1'] = step_1

    info['step_2'] = step_2

    info['step_3'] = step_3

    info['survey_step_1'] = survey_step_1
    info['survey_step_2'] = survey_step_2
    info['survey_step_3'] = survey_step_3
    info['spin_step_1'] = spin_step_1
    info['spin_step_2'] = spin_step_2
    info['spin_step_3'] = spin_step_3
    info['min_visit'] = min_visit
    info['max_visit'] = max_visit
    info['camp_tags_selects'] = camp_tags_selects
    info['status'] = status_campaign
    DATABASE.hotspot_campaign.update_one({'_id': camp_id}, {'$set': info})
    # campaign = get_hotspot_campaign_by_id(camp_id)
    # campaign_type = campaign.get('campaign_type')
    # if campaign_type == 'default':
    #     camps = [camp_id]
    #     if not isinstance(shop_id, ObjectId):
    #         shop_id = ObjectId(shop_id)
    #     DATABASE.hotspot_campaign.update_many({'_id': {'$nin': camps}, 'campaign_type': 'default', 'shop_id': shop_id},
    #                                           {'$set': {'status': False}})


def active_hotspot_campaign(camp_id,
                            shop_id,
                            status):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if status:
        # check exist visit when activation
        data_visit = DATABASE.hotspot_campaign.find_one({'_id': camp_id},
                                                        {'min_visit': 1, 'max_visit': 1, 'campaign_type': 1})
        min_visit = data_visit.get('min_visit')
        max_visit = data_visit.get('max_visit')
        if (min_visit):
            check_visit = check_exist_visit(
                shop_id, camp_id, min_visit, max_visit)
            if check_visit:
                return check_visit
        if data_visit.get('campaign_type'):
            DATABASE.hotspot_campaign.update({'_id': camp_id, 'shop_id': shop_id},
                                             {'$set': {'status': status}})

        max_sequence = DATABASE.hotspot_campaign.find(
            {'shop_id': shop_id, 'campaign_type': 'default', 'status': True}).count()
        DATABASE.hotspot_campaign.update({'_id': camp_id, 'shop_id': shop_id},
                                         {'$set': {'status': status, 'sequence': max_sequence + 1}})
    else:
        DATABASE.hotspot_campaign.update({'_id': camp_id, 'shop_id': shop_id},
                                         {'$set': {'status': status}})


def get_camp_default_active(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.hotspot_campaign.find_one(
        {'shop_id': shop_id, 'campaign_type': 'default', 'status': True})


def count_active_hotspot_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.hotspot_campaign.find({'shop_id': shop_id, 'status': True}).count()


def total_hotspot_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.hotspot_campaign.find({'shop_id': shop_id}).count()


def new_total_hotspot_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.campaigns.find({'shop_id': shop_id}).count()


def new_total_hotspot_campaign_not_default(shop_id, not_default):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.campaigns.find({'shop_id': shop_id, '_id': {'$nin': not_default}}).count()


def get_all_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    campaigns = DATABASE.campaigns.find({'shop_id': shop_id})
    camps = []
    for camp in campaigns:
        camps.append(camp)
    return camps


def get_all_hotspot_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    campaigns = []
    campaign_register = DATABASE.hotspot_campaign.find(
        {'shop_id': shop_id, 'campaign_type': 'register'})
    for camp in campaign_register:
        campaigns.append(camp)
    campaigns_default_active = DATABASE.hotspot_campaign.find(
        {'shop_id': shop_id, 'campaign_type': 'default', 'status': True})

    if campaigns_default_active:
        for i in campaigns_default_active:
            campaigns.append(i)
    campaigns_default = DATABASE.hotspot_campaign.find(
        {'shop_id': shop_id, 'campaign_type': 'default', 'status': False}).sort('created_at', -1)
    for camp in campaigns_default:
        campaigns.append(camp)
    if len(campaigns) > 0:
        for camp in campaigns:
            step_1 = camp.get('step_1')
            step_2 = camp.get('step_2')
            step_3 = camp.get('step_3')

            # step 1
            if step_1 == '0':
                camp['step_1_id'] = '0'
            elif step_1 == 'default':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_1)
                pages = [page for page in pages]
                if len(pages) > 0:
                    page = pages[0]
                    page_id = page.get('_id')
                    camp['step_1_id'] = page_id
            elif step_1 == 'survey':
                survey_step_1 = camp.get('survey_step_1')
                if survey_step_1 and len(survey_step_1) == 24:
                    camp['step_1_id'] = survey_step_1
            elif step_1 == 'birthday':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_1)
                if pages.count() > 0:
                    page = pages[0]
                    page_id = page.get('_id')
                    camp['step_1_id'] = page_id
                else:
                    camp['step_1_id'] = '0'
            elif step_1 == 'youtube':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_1)
                if pages.count() > 0:
                    page = pages[0]
                    page_id = page.get('_id')
                    camp['step_1_id'] = page_id
                else:
                    camp['step_1_id'] = '0'
            elif step_1 == 'hour':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_1)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_1_id'] = page_active_random
                else:
                    camp['step_1_id'] = '0'
            elif step_1 == 'promotion':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_1)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_1_id'] = page_active_random
                else:
                    camp['step_1_id'] = '0'
            elif step_1 == 'tags':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page='tag')
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_1_id'] = page_active_random
                else:
                    camp['step_1_id'] = '0'
            elif step_1 == 'loyal':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_1)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_1_id'] = page_active_random
                else:
                    camp['step_1_id'] = '0'
            elif step_1 == 'weekday':
                pages = get_splash_page_weekday(shop_id=shop_id,
                                                type_page=step_1)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_1_id'] = page_active_random
                else:
                    camp['step_1_id'] = '0'

            # step 2
            if step_2 == '0':
                camp['step_2_id'] = '0'
            elif step_2 == 'default':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_2)
                page = pages[0]
                page_id = page.get('_id')
                camp['step_2_id'] = page_id
            elif step_2 == 'survey':
                survey_step_2 = camp.get('survey_step_1')
                if survey_step_2 and len(survey_step_2) == 24:
                    camp['step_2_id'] = survey_step_2
            elif step_2 == 'birthday':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_2)
                if pages.count() > 0:
                    page = pages[0]
                    page_id = page.get('_id')
                    camp['step_2_id'] = page_id
                else:
                    camp['step_2_id'] = '0'
            elif step_2 == 'youtube':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_2)
                if pages.count() > 0:
                    page = pages[0]
                    page_id = page.get('_id')
                    camp['step_2_id'] = page_id
                else:
                    camp['step_2_id'] = '0'
            elif step_2 == 'hour':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_2)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_2_id'] = page_active_random
                else:
                    camp['step_2_id'] = '0'
            elif step_2 == 'promotion':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_2)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_2_id'] = page_active_random
                else:
                    camp['step_2_id'] = '0'
            elif step_2 == 'tags':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page='tag')
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_2_id'] = page_active_random
                else:
                    camp['step_2_id'] = '0'
            elif step_2 == 'loyal':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_2)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_2_id'] = page_active_random
                else:
                    camp['step_2_id'] = '0'
            elif step_2 == 'weekday':
                pages = get_splash_page_weekday(shop_id=shop_id,
                                                type_page=step_2)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_2_id'] = page_active_random
                else:
                    camp['step_2_id'] = '0'

            # step 3
            if step_3 == '0':
                camp['step_3_id'] = '0'
            elif step_3 == 'default':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_3)
                page = pages[0]
                page_id = page.get('_id')
                camp['step_3_id'] = page_id
            elif step_3 == 'survey':
                survey_step_3 = camp.get('survey_step_1')
                if survey_step_3 and len(survey_step_3) == 24:
                    camp['step_3_id'] = survey_step_3
            elif step_3 == 'birthday':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_3)
                if pages.count() > 0:
                    page = pages[0]
                    page_id = page.get('_id')
                    camp['step_3_id'] = page_id
                else:
                    camp['step_3_id'] = '0'
            elif step_3 == 'youtube':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_3)
                if pages.count() > 0:
                    page = pages[0]
                    page_id = page.get('_id')
                    camp['step_3_id'] = page_id
                else:
                    camp['step_3_id'] = '0'
            elif step_3 == 'hour':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_3)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_3_id'] = page_active_random
                else:
                    camp['step_3_id'] = '0'
            elif step_3 == 'promotion':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_3)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_3_id'] = page_active_random
                else:
                    camp['step_3_id'] = '0'
            elif step_3 == 'tags':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page='tag')
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_3_id'] = page_active_random
                else:
                    camp['step_3_id'] = '0'
            elif step_3 == 'loyal':
                pages = get_splash_page_by_type(shop_id=shop_id,
                                                type_page=step_3)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_3_id'] = page_active_random
                else:
                    camp['step_3_id'] = '0'
            elif step_3 == 'weekday':
                pages = get_splash_page_weekday(shop_id=shop_id,
                                                type_page=step_3)
                pages = [page for page in pages]
                page_active_random_arr = [
                    page.get('_id') for page in pages if str(page.get('active')) == 'True']
                page_active_random = ''
                if len(page_active_random_arr) > 0:
                    page_active_random = page_active_random_arr[0]
                    camp['step_3_id'] = page_active_random
                else:
                    camp['step_3_id'] = '0'
    return campaigns


def get_hotspot_campaign_by_id(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.hotspot_campaign.find_one({'_id': camp_id})


def get_new_campaign_by_id(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    camp = DATABASE.campaigns.find_one({'_id': camp_id})
    return camp


def update_config_spin(shop_id=None, info=None, reset=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    DATABASE.shop.update_one(
        {'_id': shop_id}, {'$set': {'spin': info, 'updated_at': time.time()}})
    if str(reset) == 'true':
        DATABASE.spin_splash_log_momen.remove({'shop_id': shop_id})


def create_or_update_mini_game(shop_id=None, camp_id=None, info=None, game_type=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    name = info.get('name')
    info['slug'] = slugify(name)
    if camp_id:
        if not isinstance(camp_id, ObjectId):
            camp_id = ObjectId(camp_id)
        ex_camp = DATABASE.mini_game_page.find_one({
            'shop_id': shop_id,
            '_id': camp_id
        })
        if ex_camp:
            ex_info = ex_camp.get('info')
            if info['slug'] != ex_info.get('slug'):
                unique_string = str(shop_id) + str(camp_id) + str(time.time())
                unique_id = info['slug'] + '_' + \
                    hashlib.md5(str(unique_string).encode("utf-8")).hexdigest()

                DATABASE.mini_game_page.update({
                    'shop_id': shop_id,
                    '_id': camp_id
                }, {'$set': {
                    'info': info,
                    'unique_id': unique_id,
                    'when': time.time()
                }})
            else:
                DATABASE.mini_game_page.update({
                    'shop_id': shop_id,
                    '_id': camp_id
                }, {'$set': {
                    'info': info,
                    'when': time.time()
                }})
    else:
        camp_id = DATABASE.mini_game_page.insert({
            'shop_id': shop_id,
            'info': info,
            'game_type': game_type,
            'when': time.time()
        })
        unique_string = str(shop_id) + str(camp_id) + str(time.time())
        unique_id = info['slug'] + '_' + \
            hashlib.md5(str(unique_string).encode('utf-8')).hexdigest()
        if not isinstance(camp_id, ObjectId):
            camp_id = ObjectId(camp_id)
        DATABASE.mini_game_page.update({
            'shop_id': shop_id,
            '_id': camp_id
        }, {'$set': {
            'unique_id': unique_id,
            'when': time.time()
        }})


def item_mini_game(shop_id, camp_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.mini_game_page.find_one({
        'shop_id': shop_id,
        '_id': camp_id
    })


def item_mini_game_by_id(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.mini_game_page.find_one({
        '_id': camp_id
    })


def item_mini_game_by_unique_id(camp_id):
    return DATABASE.mini_game_page.find_one({
        'unique_id': camp_id,
    })


def init_hotspot_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    exists_camps = get_all_hotspot_campaign(shop_id)
    if len(exists_camps) == 0:
        if str(request.cookies.get("langs")) == 'lo':
            name_return_camp = "ກັບຄືນກິດຈະກຳຂອງລູກຄ້າ"
            name_new_cus_camp = "ຂະບວນການລູກຄ້າໃໝ່"
        else:
            name_return_camp = "Chiến dịch khách hàng quay trở lại"
            name_new_cus_camp = "Chiến dịch khách hàng mới"
        DATABASE.hotspot_campaign.insert_one({
            'shop_id': shop_id,
            'campaign_type': 'default',
            'step_1': 'default',
            'step_2': '0',
            'step_3': '0',
            'step_4': 'connect_success',
            'created_at': time.time(),
            'group_customer': {},
            'status': True,
            'init': True,
            'name': name_return_camp
        })
        DATABASE.hotspot_campaign.insert_one({
            'shop_id': shop_id,
            'campaign_type': 'register',
            'step_1': 'register',
            'step_2': '0',
            'step_3': '0',
            'step_4': 'connect_success',
            'group_customer': {},
            'created_at': time.time(),
            'status': True,
            'init': True,
            'name': name_new_cus_camp
        })


def init_new_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if str(request.cookies.get("langs")) == 'lo':
        name_return_camp = "ກັບຄືນກິດຈະກຳຂອງລູກຄ້າ"
        name_new_cus_camp = "ຂະບວນການລູກຄ້າໃໝ່"
    else:
        name_return_camp = "Chiến dịch khách hàng quay trở lại"
        name_new_cus_camp = "Chiến dịch khách hàng mới"
    info_register = {
        'shop_id': shop_id,
        'type': 'register',
        'step_1': 'collect',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
        },
        'create_at': time.time(),
        'update_at': time.time(),
        'status': True,
        'is_birthday': False,
        'name': name_new_cus_camp
    }

    new_register_camp = DATABASE.campaigns.insert(info_register)

    details = {
        'content_connect': '',
        'connect_button': '',
        'display_coupon': False,
        'display_coupon_txt': '',
        'hotspot_method': 'default',
        'default_code': '',
        'redirect_type': '',
        'auto_website': '',
        'auto_popup_ios': '',
        'auto_popup_android': '',
        'auto_facebook_page': '',
        'auto_popup_zalo': '',
        'auto_popup_insta': '',
        'auto_facebook_mess': ''
    }
    info_connect = {
        'camp_id': new_register_camp,
        'type_page': "connect_success",
        'shop_id': shop_id,
        'step': '4',
        'details': details
    }
    shop_select = get_shop_info(shop_id)
    login_form = shop_select.get('login_form', {})
    info_collect = {
        'camp_id': new_register_camp,
        'type_page': "collect",
        'shop_id': shop_id,
        'step': '1',
        'details': login_form
    }
    DATABASE.details_step_campaign.insert(info_collect)
    DATABASE.details_step_campaign.insert(info_connect)
    info_default = {
        'shop_id': shop_id,
        'type': 'default',
        'step_1': '0',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'create_at': time.time(),
        'update_at': time.time(),
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
            'convert_min_hour': 0,
            'convert_max_hour': 23.5,
            'timestamp_start_event': 0,
            'timestamp_end_event': 0
        },
        'status': True,
        'is_birthday': False,
        'name': name_return_camp
    }
    new_default_camp = DATABASE.campaigns.insert(info_default)
    info_connect = {
        'camp_id': new_default_camp,
        'type_page': "connect_success",
        'shop_id': shop_id,
        'step': '4',
        'details': details
    }
    DATABASE.details_step_campaign.insert(info_connect)


def get_result_spin_splash(merchant_id, page_size, page):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    list_log = DATABASE.spin_splash_log.find(
        {'merchant_id': merchant_id}).sort('spin_log', -1)
    list_result = []
    for item in list_log:
        shop_id_item = item.get('shop_id')
        client_mac = item.get('client_mac')
        user = DATABASE.customers_location.find_one({'shop_id': shop_id_item,
                                                     'user.client_mac': {
                                                         "$in": [client_mac, client_mac.lower(), client_mac.upper()]}})
        if not user:
            user = DATABASE.customers.find_one({'merchant_id': merchant_id,
                                                'user.client_mac': {
                                                    "$in": [client_mac, client_mac.lower(), client_mac.upper()]}})
        if not user:
            continue
        item['user'] = user.get('user')
        list_result.append(item)
    total = len(list_result)
    return list_result[(page - 1) * page_size: page * page_size], total


# def get_total_result_spin_splash(merchant_id):
#     if not isinstance(merchant_id, ObjectId):
#         merchant_id = ObjectId(merchant_id)
#     list_log = DATABASE.spin_splash_log.find({'merchant_id': merchant_id})
#     list_result = 0
#     for item in list_log:
#         shop_id_item = item.get('shop_id')
#         client_mac = item.get('client_mac')
#         user = DATABASE.customers_location.find_one({'shop_id': shop_id_item,
#                                                      'user.client_mac': {"$in": [client_mac, client_mac.lower(), client_mac.upper()]}})
#         if not user:
#             user = DATABASE.customers.find_one({'merchant_id': merchant_id,
#                                                 'user.client_mac': {"$in": [client_mac, client_mac.lower(), client_mac.upper()]}})
#         if not user:
#             continue
#         print list_result, item.get('gateway_mac'), client_mac
#         list_result = list_result + 1
#     return list_result


def remove_hotspot_campaign(campaign_id):
    if not isinstance(campaign_id, ObjectId):
        campaign_id = ObjectId(campaign_id)
    return DATABASE.hotspot_campaign.remove({'_id': campaign_id})


def get_user_activity_visit_ex(user_id, merchant_id):
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    shops = []
    for _id in get_shop_by_merchant(merchant_id):
        shops.append(ObjectId(str(_id.get('_id'))))
    query = {'user_id': user_id, 'shop_id': {'$in': shops}}
    recs = DATABASE.visit_log.find(query).sort('timestamp', -1)
    results = []
    for rec in recs:
        user_id = rec.get('user_id')
        user = handle_customers.get_user_merchant_by_user_id(
            merchant_id, user_id)
        if not user:
            user = get_user_info(user_id=user_id)
        else:
            user = user.get('user', {})
        if user:
            time_date = time.strftime("%d/%m/%Y %H:%M",
                                      time.localtime(int(rec['timestamp'])))
            rec['_id'] = str(rec['_id'])
            rec['phone'] = str(user.get('phone'))
            rec['shop_id'] = str(rec['shop_id'])
            shop = get_shop_info(shop_id=rec['shop_id'])
            rec['shop_name'] = shop['name']
            rec['time_day'] = time_date
            rec['time_ago'] = arrow.get(
                rec['timestamp']).humanize(locale='vi_vn')
            results.append(rec)
    return results


def sync_mailchimp(shop_id=None, name_app=None):
    check_mailchimp = DATABASE.app_synchronized.find_one(
        {'shop_id': shop_id, 'name_app': name_app})
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if check_mailchimp:
        customers = DATABASE.customers_location.find({"shop_id": shop_id})
        last_sync_mailchimp = check_mailchimp.get('last_sync_mailchimp')
        mailchimp_user = check_mailchimp.get('setting').get('mailchimp_user')
        mailchimp_api_key = check_mailchimp.get(
            'setting').get('mailchimp_api_key')
        id_list = check_mailchimp.get('setting').get('id_list')
        if customers:
            operations = []
            for cus in customers:
                cus_detail = cus.get("user")
                cus_email = cus_detail.get("email")
                if cus_email and len(str(cus_email)) > 0:
                    tags = []
                    tags_details = cus_detail.get("user_tags_details")
                    if tags_details:
                        for tag in tags_details:
                            tag_name = tag.get("name")
                            tags.append(tag_name)
                    databody_item = {
                        "email_address": cus_email,
                        "status": "subscribed",
                        "tags": tags
                    }
                    operation_item = {"method": "POST", "path": "/lists/%s/members/" % (id_list),
                                      "body": json.dumps(databody_item)}
                    operations.append(operation_item)
            client = MailChimp(mc_user=mailchimp_user,
                               mc_api=mailchimp_api_key)
            batch = client.batches.create(data={"operations": operations})


def get_mailchimp_info(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.sync_mailchimp.find_one({'shop_id': shop_id})


def check_phone_follow_zaloOA(shop_id, phone):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop_info = DATABASE.shop.find_one({'_id': shop_id})
    access_token = shop_info.get('zalo_access_token')
    url = "https://openapi.zalo.me/v2.0/oa/getprofile?access_token={}&data={}".format(
        access_token, {'user_id': phone})
    result = requests.get(url=url)
    result = json.loads(result.text)
    check = result.get('error')
    if check == 0:
        user_id_by_zalo = result.get('data').get('user_id_by_app')
        return user_id_by_zalo
    else:
        return False


def save_phone_zalo_report(shop_id, phones, user_id_zalo):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    check_setting = DATABASE.setting_report.find_one({'shop_id': shop_id})
    setting = DATABASE.shop.find_one({"_id": shop_id})
    info = {}
    info['create_at'] = time.time()
    info['phones'] = phones
    info['user_id_zalo'] = user_id_zalo
    info['shop_id'] = shop_id
    info['name'] = setting.get('name')
    info['zalo_oa_id'] = setting.get('zalo_oa_id')
    info['zalo_app_id'] = setting.get('zalo_app_id')
    info['zalo_access_token'] = setting.get('zalo_access_token')
    if not check_setting:
        DATABASE.setting_report.insert(info)
    else:
        DATABASE.setting_report.update({'shop_id': shop_id}, {'$set': info})


def get_phones_report_zalo(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    setting_report = DATABASE.setting_report.find_one({'shop_id': shop_id})
    text_phone = ""
    if setting_report:
        phones = setting_report.get('phones')
        for phone in phones:
            text_phone = text_phone + ", " + phone
        text_phone = text_phone.lstrip(',')
    return text_phone


def filter_detect_customer(shop_id,
                           min_visit=None,
                           max_visit=None,
                           tags_array=None,
                           sort=None,
                           page=None,
                           employee=None,
                           page_size=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    info = {}
    info['shop_id'] = shop_id

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)

    if min_visit and str(min_visit) != 'None' and len(min_visit) == 0:
        if max_visit and str(max_visit) != 'None' and len(max_visit) > 0:
            info['total_visit'] = {}
            info['total_visit']['$lte'] = int(max_visit)

    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'

    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
    null_arr = ['', 'null', 'None', 'none', None]
    recs = []
    if not page:
        recs = DATABASE.customers_location.find(
            info, no_cursor_timeout=True).sort('last_visit', -1)
    else:
        if sort and sort == 'visit_asc':
            recs = DATABASE.customers_location.find(info).sort('total_visit', -1).skip(page_size * (page - 1)) \
                .limit(page_size)
            real = DATABASE.customers_location.count(info)
        else:
            recs = DATABASE.customers_location.find(info).sort('last_visit', -1).skip(page_size * (page - 1)) \
                .limit(page_size)
            real = DATABASE.customers_location.count(info)
    return [rec for rec in recs], real


def total_shop_customers(shop_id,
                         is_email=None,
                         is_sms=None,
                         is_zalo=None,
                         from_date=None,
                         to_date=None,
                         min_visit=None,
                         max_visit=None,
                         lost_day=None,
                         gender=None,
                         employee=None,
                         sort=None,
                         bday_from_date=None,
                         bday_to_date=None,
                         tags_array=None,
                         is_has_phone=None,
                         is_has_email=None,
                         is_has_zalo=None,
                         active_zns=None,
                         is_has_messenger_id=None,
                         phone_filter=None,
                         email_filter=None,
                         zalo_filter=None,
                         fb_filter=None
                         ):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {}
    info['shop_id'] = shop_id

    if from_date and from_date != 'None':
        from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())
        info['last_visit'] = {}
        info['last_visit']['$gte'] = from_tmp

    if to_date and to_date != 'None' and 'last_visit' in info:
        to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        info['last_visit']['$lte'] = to_tmp

    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)

    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)

    if bday_from_date and bday_from_date != 'None' and bday_to_date \
            and bday_to_date != 'None':
        days = gen_date_in_range(bday_from_date, bday_to_date)
        info['user.birthday'] = {'$in': days}

    if lost_day and str(lost_day) != 'None' and int(lost_day) > 0:
        lost_day_start = time.time() - int(lost_day) * 86400
        info['last_visit'] = {'$lte': lost_day_start}
    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'

    if gender and len(gender) > 0 and str(gender) != 'None':
        info['user.gender'] = {'$in': gender}

    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
    null_arr = ['', 'null', 'None', 'none', None]
    if isinstance(is_email, bool) and not isinstance(is_sms, bool):
        if is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
    elif isinstance(is_sms, bool) and not isinstance(is_email, bool):
        if is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    else:
        if is_email and is_sms:
            info['$or'] = [
                {'user.phone': {'$exists': True, '$nin': null_arr}},
                {'user.email': {'$exists': True, '$nin': null_arr}}
            ]
        elif is_email:
            info['user.email'] = {'$exists': True, '$nin': null_arr}
        elif is_sms:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
        elif is_zalo:
            info['user.phone'] = {'$exists': True, '$nin': null_arr}
    if is_has_phone:
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_email:
        info['user.email'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_zalo:
        info['user.user_id_zalo'] = {'$exists': True, "$nin": [None, ""]}
    if is_has_messenger_id:
        info['user.messenger_id'] = {'$exists': True, "$nin": [None, ""]}
    if phone_filter and len(phone_filter) > 0 and str(phone_filter) != 'None':
        info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    if email_filter and len(email_filter) > 0 and str(email_filter) != 'None':
        info['user.email'] = {'$exists': True, "$nin": [None, ""]}
    if zalo_filter and len(zalo_filter) > 0 and str(zalo_filter) != 'None':
        info['user.user_id_zalo'] = {'$exists': True, "$nin": [None, ""]}
    if fb_filter and len(fb_filter) > 0 and str(fb_filter) != 'None':
        info['user.messenger_id'] = {'$exists': True, "$nin": [None, ""]}
    if is_zalo and active_zns == "off":
        result = []
        customers = DATABASE.customers_location.find(
            info).sort('last_visit', -1)
        for rec in customers:
            cus_phone = rec.get('user').get('phone')
            user_id_zalo = rec.get('user').get('user_id_zalo')
            # check_follow_oa = check_phone_follow_zaloOA(shop_id, str(cus_phone))
            # if check_follow_oa:
            if cus_phone and user_id_zalo and len(str(user_id_zalo)) > 0:
                result.append(rec)
        return len(result)
    return DATABASE.customers_location.find(info).count()


def save_detect_customer(shop_id,
                         min_visit=None,
                         max_visit=None,
                         employee=None,
                         tags_array=None,
                         phones=None,
                         customers_sources=None,
                         is_birthday_notify=None,
                         is_activity=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {}
    customers_detect = []
    info['shop_id'] = shop_id
    if min_visit and str(min_visit) != 'None' and len(min_visit) > 0:
        info['total_visit'] = {}
        info['total_visit']['$gte'] = int(min_visit)
    if max_visit and str(max_visit) != 'None' and len(max_visit) > 0 and 'total_visit' in info:
        info['total_visit']['$lte'] = int(max_visit)
    info['user.is_employee'] = {"$ne": 'True'}
    if employee and len(employee) > 0 and str(employee) != 'None':
        info['user.is_employee'] = 'True'
    if tags_array and len(tags_array) > 0:
        tags_array = [ObjectId(tag) for tag in tags_array]
        info['user.user_tags_details._id'] = {'$in': tags_array}
        tags_array = [str(tag) for tag in tags_array]
    content = {}
    content['shop_id'] = shop_id
    content['min_visit'] = min_visit
    content['max_visit'] = max_visit
    content['tags_array'] = tags_array
    content['phones'] = phones
    content['all_customers'] = customers_sources
    content['is_birthday_notify'] = is_birthday_notify
    content['is_activity'] = is_activity
    check_setting = DATABASE.automation_detect_report.find_one(
        {'shop_id': shop_id})
    if not check_setting:
        DATABASE.automation_detect_report.insert(content)
    else:
        DATABASE.automation_detect_report.update(
            {'shop_id': shop_id}, {"$set": content})


def get_phones_detect_customer(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    setting_report = DATABASE.automation_detect_report.find_one(
        {'shop_id': shop_id})
    text_phone = ""
    if setting_report:
        phones = setting_report.get('phones')
        for phone in phones:
            text_phone = text_phone + ", " + phone
        text_phone = text_phone.lstrip(',')
    return text_phone


def get_info_detect_zalo(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.automation_detect_report.find_one({'shop_id': shop_id})


def send_report_zalo(shop_id, name_shop, access_token, users_id_zalo):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    end = time.time()
    start = end - 604800
    date_start = datetime.utcfromtimestamp(start).strftime('%d/%m/%Y')
    date_end = datetime.utcfromtimestamp(end).strftime('%d/%m/%Y')
    customer = DATABASE.customers_location.find({'shop_id': shop_id,
                                                 "last_visit": {'$gte': start, '$lte': end}})
    total_customer = customer.count()
    new_customer = DATABASE.customers_location.find(
        {'shop_id': shop_id, "last_visit": {'$gte': start, '$lte': end}, 'total_visit': 1})
    num_new_customer = new_customer.count()
    comeback_customer = total_customer - num_new_customer

    url = "https://openapi.zalo.me/v2.0/oa/message?access_token={}".format(
        access_token)
    headers = {'Content-type': 'application/json'}
    content = "BÁO CÁO KHÁCH HÀNG" + "\n" \
                                     "Tuần: " + str(date_start) + " đến " + str(date_end) + "\n" \
                                                                                            "Địa điểm: " + str(
                                         name_shop) + "\n" \
        "Tổng số khách hàng: " + str(total_customer) + "\n" \
        "Khách hàng mới: " + str(
                                         num_new_customer) + "\n" \
        "Khách quay trở lại: " + str(comeback_customer)
    for user_id in users_id_zalo:
        data = {"recipient": {
            "user_id": user_id
        },
            "message": {
                "text": content
        }
        }
        requests.post(
            url=url, data=json.dumps(data), headers=headers)


def send_report_email(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop = DATABASE.shop.find_one({'_id': shop_id})
    if shop:
        merchant_id = shop.get('merchant_id')
        if merchant_id:
            if not isinstance(merchant_id, ObjectId):
                merchant_id = ObjectId(merchant_id)
            merchant = DATABASE.merchants.find_one({'_id': merchant_id})
            partner_id = merchant.get('partner')
            if partner_id:
                if not isinstance(partner_id, ObjectId):
                    partner_id = ObjectId(partner_id)
                partner = DATABASE.dealers.find_one({'_id': partner_id})
                if partner:
                    mail_name = partner.get('mail_domain')
                    mail_user = partner.get('mail_domain')
                    mail_pass = partner.get('mail_api_key')
                    mail_server = partner.get('mail_api_url')
                    mail_port = partner.get('mail_port')
                    mail_ssl = partner.get('mail_ssl')
                    merchant_name = partner.get('name', '')
                shop_name = shop.get('name')
                recipients = shop.get('email_report')
                subject = "Báo cáo hàng tuần"
                end = time.time()
                start = end - 604800
                date_start = datetime.utcfromtimestamp(
                    start).strftime('%d/%m/%Y')
                date_end = datetime.utcfromtimestamp(end).strftime('%d/%m/%Y')
                customer = DATABASE.customers_location.find({'shop_id': shop_id,
                                                             "last_visit": {'$gte': start, '$lte': end}})
                total_customer = customer.count()
                new_customer = DATABASE.customers_location.find(
                    {'shop_id': shop_id, "last_visit": {'$gte': start, '$lte': end}, 'total_visit': 1})
                num_new_customer = new_customer.count()
                comeback_customer = total_customer - num_new_customer
                mail_content = "<html><body><h3>BÁO CÁO HÀNG TUẦN.</h3><p>Tuần từ: " + str(date_start) + " đến " + str(date_end) + "</p><p>Địa điểm: " + str(shop_name) + "</p><p>Tổng số khách hàng: " + str(
                    total_customer) + "</p><p>Khách hàng mới: " + str(num_new_customer) + "</p><p>Khách hàng quay lại: " + str(comeback_customer) + "</p></body></html>"
                if len(mail_user) > 1 and len(mail_pass) > 1 and len(mail_server) > 1:
                    if 'nextify' in mail_server or 'mail_gun' in mail_server:
                        email_api.mailgun_service(mail_pass, mail_user, mail_server,
                                                  merchant_name, recipients, subject,
                                                  mail_content)
                    else:
                        email_api.send_mail_smtp(mail_server, mail_port, mail_user, mail_pass,
                                                 subject, recipients, mail_content)


def save_shop_birthday_remind(shop_id, status):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop_birthday = DATABASE.shop_birthday_remind.find_one(
        {'shop_id': shop_id})
    if not shop_birthday:
        DATABASE.shop_birthday_remind.insert({
            'shop_id': shop_id,
            'status': status,
            'update_at': time.time()
        })
    else:
        DATABASE.shop_birthday_remind.update({
            'shop_id': shop_id
        }, {'$set': {
            'status': status,
            'update_at': time.time()
        }})


def save_lost_remind(shop_id, status):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop_lost = DATABASE.shop_lost_remind.find_one({'shop_id': shop_id})
    if not shop_lost:
        DATABASE.shop_lost_remind.insert({
            'shop_id': shop_id,
            'status': status,
            'update_at': time.time()
        })
    else:
        DATABASE.shop_lost_remind.update({
            'shop_id': shop_id
        }, {'$set': {
            'status': status,
            'update_at': time.time()
        }})


def get_time_register_zalo_pay(app_id):
    if not isinstance(app_id, ObjectId):
        app_id = ObjectId(app_id)
    info = DATABASE.app_synchronized.find_one({'_id': app_id})
    if info:
        time_create = info.get('create_at')
        return datetime.utcfromtimestamp(int(time_create) + 25200).strftime('%H:%M %d-%m-%Y')


def get_hotspot_campaign(shop_id, status):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    campaigns = DATABASE.hotspot_campaign.find(
        {'shop_id': shop_id, 'status': status}).sort('sequence', 1)
    return campaigns


# Update priority after ordering campaign
def update_priority(campaign_id, sequence_number):
    if not isinstance(campaign_id, ObjectId):
        campaign_id = ObjectId(campaign_id)
    DATABASE.hotspot_campaign.update_one({
        '_id': campaign_id
    }, {'$set': {
        'sequence': sequence_number
    }})


# Update priority after deactive campaign
def update_priority_after_deactive(camp_id):
    if not isinstance(camp_id, ObjectId):
        campaign_id = ObjectId(camp_id)
    sequence_deactive = DATABASE.hotspot_campaign.find_one(
        {'_id': campaign_id}, {'sequence': 1})
    DATABASE.hotspot_campaign.update_one(
        {'_id': campaign_id},
        {'$set': {'sequence': None}}
    )
    datas = DATABASE.hotspot_campaign.find(
        {'sequence': {'$gt': sequence_deactive.get('sequence')}}, {'_id': 1})
    for i in datas:
        id = i.get('_id')
        DATABASE.hotspot_campaign.update_one({
            '_id': id
        },
            {'$inc': {'sequence': -1}})


def check_exist_visit(shop_id=None, campaign_id=None, min_visit=0, max_visit=0):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if campaign_id != 'None':
        if not isinstance(campaign_id, ObjectId):
            campaign_id = ObjectId(campaign_id)
        check_visit = DATABASE.hotspot_campaign.find_one(
            {
                'shop_id': shop_id,
                'status': True,
                '$or': [
                    {
                        '$or': [
                            {'$and': [
                                {'min_visit': {'$lte': min_visit}},
                                {'max_visit': {'$gte': min_visit}}
                            ]},
                            {'$and': [
                                {'min_visit': {'$lte': max_visit}},
                                {'max_visit': {'$gte': max_visit}}
                            ]},

                        ]
                    },
                    {
                        '$and': [
                            {'min_visit': {'$gte': min_visit}},
                            {'max_visit': {'$lte': max_visit}},
                        ]
                    }
                ]
            },
            {'name': 1, '_id': 1}
        )

        if check_visit:
            if check_visit.get('_id') == campaign_id:
                return
            else:
                return check_visit
        return
    check_visit = DATABASE.hotspot_campaign.find_one(
        {'shop_id': shop_id,
         '$or': [
             {
                 '$or': [
                     {'$and': [
                         {'min_visit': {'$lte': min_visit}},
                         {'max_visit': {'$gte': min_visit}}
                     ]},
                     {'$and': [
                         {'min_visit': {'$lte': max_visit}},
                         {'max_visit': {'$gte': max_visit}}
                     ]},

                 ]
             },
             {
                 '$and': [
                     {'min_visit': {'$gte': min_visit}},
                     {'max_visit': {'$lte': max_visit}},
                 ]
             }
         ]

         },
        {'name': 1}
    )
    return check_visit


def check_api_key_omicrm(api_key):
    url = 'https://public-v1-stg.omicrm.com/api/auth?apiKey={}'.format(api_key)
    result = requests.get(url=url)
    if json.loads(result.text).get('status_code') != 9999:
        return False
    else:
        access_token = json.loads(result.text).get(
            'payload').get('access_token')
        return access_token


def check_account_sync_haravan(name, client_key, domain, access_token, haravan_id_shop):
    check_account = DATABASE.merchants.find_one(
        {'phone': name, 'client_key': client_key})
    if not check_account:
        check_account = DATABASE.merchants.find_one(
            {'email': name, 'client_key': client_key})
    if check_account:
        name_app = "haravan"
        merchant_id = check_account.get("_id")
        check_app = get_app_synchronized(
            name_app=name_app, merchant_id=str(merchant_id))
        if not check_app:
            create_app_synchronized(name_app=name_app, merchant_id=str(merchant_id), access_token=access_token,
                                    type_app="web", domain=domain, haravan_id_shop=haravan_id_shop)
        else:
            update_app_synchronized(name_app=name_app, merchant_id=str(merchant_id), access_token=access_token,
                                    domain=domain, haravan_id_shop=haravan_id_shop)
        return True
    else:
        return False


def save_customers_haravan(domain, access_token):
    app = DATABASE.app_synchronized.find_one(
        {'name_app': 'haravan', 'setting.domain': domain, 'setting.access_token': access_token})
    if app:
        merchant_id = app.get('merchant_id')
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        # lay tong so khach
        url = "https://apis.haravan.com/com/customers/count.json"
        payload = {}
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }

        response = requests.get(url=url, headers=headers, data=payload)
        result = json.loads(response.text)
        count = result.get('count')
        num_pages = count / 50
        # lay thong tin khach hang
        page = 1
        while page < num_pages + 2:
            url = "https://apis.haravan.com/com/customers.json?fields=phone,email,birthday,first_name,last_name,gender,tags,orders_count&page={}".format(
                page)
            payload = {}
            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }

            response = requests.get(url=url, headers=headers, data=payload)
            if response.status_code == 200:
                result = json.loads(response.text)
                customers = result.get('customers')
                for cus in customers:
                    orders_count = 0
                    email = cus.get('email')
                    phone = cus.get('phone')
                    birthday = cus.get('birthday')
                    first_name = cus.get('first_name', '')
                    last_name = cus.get('last_name', '')
                    tags = cus.get('tags')
                    id_haravan = cus.get('id')
                    gender = cus.get('gender')
                    orders_count = cus.get('orders_count')
                    name = str(last_name) + " " + str(first_name)
                    if phone and len(phone) > 0 or email and len(email) > 0:
                        if birthday and len(birthday) > 0:
                            birthday = datetime.strptime(
                                birthday, "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d")
                        user_id = None
                        if phone and len(phone) > 0 and str(phone) != 'None':
                            phone = str(phone).lower()
                            phone = phone.replace('+84', '0')
                            phone = get_phone_number(phone)
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
                            update_user_by_id(user_id=user_id, email=email, phone=phone, name=name,
                                              first_name=first_name,
                                              last_name=last_name, gender=gender, birthday=birthday)
                        else:
                            user_id = register_with_id(email=email, phone=phone, name=name, first_name=first_name,
                                                       last_name=last_name, gender=gender, birthday=birthday)
                        # gan tag
                        if not tags:
                            tags = "haravan"
                        if not "haravan" in tags:
                            tags = tags + ", haravan"
                        if tags and len(tags) > 0:
                            list_tags = []
                            list_tag = tags.split(',')
                            for tag in list_tag:
                                tag = tag.strip()
                                tag_lower = tag.lower()
                                tag_upper = tag.upper()
                                check_tag = DATABASE.tags.find_one(
                                    {'merchant_id': merchant_id, 'name': {'$in': [tag, tag_lower, tag_upper]}})
                                if not check_tag:
                                    id_tags = create_tags(
                                        merchant_id=merchant_id, name=tag, description=tag)
                                else:
                                    id_tags = check_tag.get("_id")
                                list_tags.append(id_tags)
                            create_user_tags_merchant(
                                merchant_id, user_id, list_tags)
                        # luu customer
                        save_customers.update_customers_merchant(merchant_id=merchant_id, user_id=user_id,
                                                                 last_visit=time.time(), id_haravan=id_haravan)
                        # Neu khach cu luu them trong customers_location
                        check_loc = DATABASE.customers_location.find_one(
                            {'user_id': user_id})
                        if check_loc:
                            shop_id = check_loc.get('shop_id')
                            if not isinstance(shop_id, ObjectId):
                                shop_id = ObjectId(shop_id)
                            shops = []
                            shop_in_mer = get_shop_by_merchant(
                                str(merchant_id))
                            for shop_mer in shop_in_mer:
                                if not isinstance(shop_mer['_id'], ObjectId):
                                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                                shops.append(shop_mer['_id'])
                            if shop_id in shops:
                                save_customers.update_customers_location(merchant_id=merchant_id, shop_id=shop_id,
                                                                         user_id=user_id, last_visit=time.time(),
                                                                         id_haravan=id_haravan)
                        if orders_count > 0:
                            if phone and len(phone) > 0:
                                get_orders_customer_haravan(merchant_id=merchant_id, user_id=user_id,
                                                            access_token=access_token, info=phone)
                            elif email and len(email) > 0:
                                get_orders_customer_haravan(merchant_id=merchant_id, user_id=user_id,
                                                            access_token=access_token, info=email)
                            else:
                                pass
            page = page + 1


def check_sync_bizfly(merchant_id, name_app, type_app, api_key, api_secret_key, project_token):
    check_bizfly = DATABASE.app_synchronized.find_one(
        {'merchant_id': str(merchant_id), 'name_app': name_app})
    if not check_bizfly:
        create_app_synchronized(merchant_id=merchant_id, name_app=name_app, type_app=type_app, api_key_biz=api_key,
                                api_secret_key_biz=api_secret_key, project_token_biz=project_token)
    else:
        update_app_synchronized(merchant_id=merchant_id, name_app=name_app, type_app=type_app, api_key_biz=api_key,
                                api_secret_key_biz=api_secret_key, project_token_biz=project_token)
    return True


def save_customers_bizfly(merchant_id=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    app = DATABASE.app_synchronized.find_one(
        {'merchant_id': str(merchant_id), 'name_app': "bizfly"})
    api_key = app.get('setting').get('api_key')
    api_secret_key = app.get('setting').get('api_secret_key')
    project_token = app.get('setting').get('project_token')
    acc_timestamp = int(time.time())
    string_build = str(acc_timestamp) + str(project_token)
    string_sign = hmac.new(str(api_secret_key),
                           string_build, hashlib.sha512).hexdigest()
    url_cus = "https://crm.bizfly.vn/_api/base-table/find"
    headers = {
        'cb-access-key': str(api_key),
        'cb-project-token': str(project_token),
        'cb-access-timestamp': str(acc_timestamp),
        'cb-access-sign': str(string_sign)
    }
    payload = {"table": "data_customer",
               "skip": 0,
               "select": [],
               "output": "default", }
    response = requests.request("POST", url_cus, headers=headers, data=payload)
    total = response.json()['total']
    limit = 20
    page_nums = total / limit + 2
    page = 1
    while page < page_nums:
        payload = {"table": "data_customer",
                   "skip": (page - 1) * limit,
                   "limit": limit,
                   "select": ["phones", "name", "emails", "tags"],
                   "output": "default", }
        response = requests.request(
            "POST", url_cus, headers=headers, data=payload)
        data_json = response.json()['data']
        for data in data_json:
            id_bizfly = ''
            emails = []
            phones = []
            name = ""
            tags = []
            for k in data:
                if k['key'] == 'id':
                    id_bizfly = k['value']
                if k['key'] == 'emails':
                    emails = []
                    list_emails = k['value']
                    for i in list_emails:
                        email = i['value']
                        emails.append(email)
                if k['key'] == 'phones':
                    phones = []
                    list_phones = k['value']
                    for i in list_phones:
                        phone = i['value']
                        phones.append(phone)
                if k['key'] == 'name':
                    name = k['value']['value']
                if k['key'] == 'tags':
                    list_tag = k['value']
                    tags = []
                    for i in list_tag:
                        tag = i['value']
                        tags.append(tag)
                    if not 'bizfly' in tags:
                        tags.append('bizfly')
            user_id = ""
            if phones and len(phones) > 0:
                for phone in phones:
                    phone = str(phone).lower()
                    phone = phone.replace('+84', '0')
                    phone = get_phone_number(phone)
                    if phone and str(phone) != 'None':
                        user_by_phone = handle_customers.get_user_merchant_by_phone(
                            merchant_id, phone)
                        if user_by_phone:
                            user_id = user_by_phone.get('user_id')
            elif emails and len(emails) > 0:
                for email in emails:
                    user_by_email = handle_customers.get_user_merchant_by_email(
                        merchant_id, email)
                    if user_by_email:
                        user_id = user_by_email.get('user_id')
            fone = phones[0]
            fone = str(fone).lower()
            fone = fone.replace("+84", "0")
            if user_id:
                update_user_by_id(user_id=user_id, phone=fone,
                                  email=emails[0], name=name)
            else:
                user_id = register_with_id(
                    phone=fone, email=emails[0], name=name)
            if tags and len(tags) > 0:
                list_tags = []
                for tag in tags:
                    tag_lower = tag.lower()
                    tag_upper = tag.upper()
                    check_tag = DATABASE.tags.find_one(
                        {'merchant_id': merchant_id, 'name': {'$in': [tag, tag_lower, tag_upper]}})
                    if not check_tag:
                        id_tags = create_tags(
                            merchant_id=merchant_id, name=tag, description=tag)
                    else:
                        id_tags = check_tag.get("_id")
                        print(id_tags)
                    list_tags.append(id_tags)
                create_user_tags_merchant(merchant_id, user_id, list_tags)
            # luu customer
            save_customers.update_customers_merchant(merchant_id=merchant_id, user_id=user_id, last_visit=time.time(),
                                                     id_bizfly=id_bizfly)
            # Neu khach cu luu them trong customers_location
            check_loc = DATABASE.customers_location.find_one(
                {'user_id': user_id})
            if check_loc:
                shop_id = check_loc.get('shop_id')
                if not isinstance(shop_id, ObjectId):
                    shop_id = ObjectId(shop_id)
                shops = []
                shop_in_mer = get_shop_by_merchant(str(merchant_id))
                for shop_mer in shop_in_mer:
                    if not isinstance(shop_mer['_id'], ObjectId):
                        shop_mer['_id'] = ObjectId(shop_mer['_id'])
                    shops.append(shop_mer['_id'])
                if shop_id in shops:
                    save_customers.update_customers_location(merchant_id=merchant_id, shop_id=shop_id, user_id=user_id,
                                                             last_visit=time.time(), id_bizfly=id_bizfly)
        page += 1


def save_info_signup(domain, access_token, haravan_id_shop, email_haravan):
    check_app = DATABASE.info_haravan.find_one({'email': email_haravan})
    info = {}
    info['domain'] = domain
    info['access_token'] = access_token
    info['haravan_id_shop'] = haravan_id_shop
    info['email'] = email_haravan
    if not check_app:
        DATABASE.info_haravan.insert(info)
    else:
        DATABASE.info_haravan.update({"email": email_haravan}, {"$set": info})


def check_sign_haravan(email):
    check_app = DATABASE.info_haravan.find_one({'email': email})
    if check_app:
        access_token = check_app.get('access_token')
        url_info = "https://apis.haravan.com/com/shop.json"
        header = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        response_info = requests.request("GET", url_info, headers=header)
        result_info = response_info.json()
        haravan_shop = result_info.get('shop')
        if haravan_shop:
            name_shop = haravan_shop.get('name')
            return name_shop
        else:
            return False
    return False


def create_app_haravan(email, merchant_id):
    check_app = DATABASE.info_haravan.find_one({'email': email})
    domain = check_app.get('domain')
    access_token = check_app.get('access_token')
    haravan_id_shop = check_app.get('haravan_id_shop')
    name_app = "haravan"
    check_app = get_app_synchronized(
        name_app=name_app, merchant_id=str(merchant_id))
    if not check_app:
        create_app_synchronized(name_app=name_app, merchant_id=str(merchant_id), access_token=access_token,
                                type_app="web", domain=domain, haravan_id_shop=haravan_id_shop)
    else:
        update_app_synchronized(name_app=name_app, merchant_id=str(merchant_id), access_token=access_token,
                                domain=domain, haravan_id_shop=haravan_id_shop)
    return domain, access_token


def get_email_register_haravan(haravan_id_shop):
    check_app = DATABASE.info_haravan.find_one(
        {"haravan_id_shop": haravan_id_shop})
    if check_app:
        email = check_app.get('email')
        if email:
            return email
        else:
            return False
    return False


def get_package_by_merchant_id(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    info = DATABASE.merchants.find_one({"_id": merchant_id})
    package = info.get("package")
    return str(package)


def get_name_package_by_merchant_id(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    info = DATABASE.merchants.find_one({"_id": merchant_id})
    package = info.get("package")
    if package:
        if not isinstance(package, ObjectId):
            package = ObjectId(package)
        info_package = DATABASE.package.find_one({'_id': package})
        name_package = info_package.get('name')
        return name_package
    return False


def get_orders_customer_haravan(merchant_id, user_id, access_token, info):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    url = "https://apis.haravan.com/com/orders.json?query={}".format(info)
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers, data=payload)
    result = json.loads(response.text)
    orders = result.get("orders")
    for order in orders:
        info = {}
        id_or = order.get('id')
        source_or = order.get('source')
        name = order.get('name')
        total_price = order.get('total_price')
        created_at = order.get('created_at')
        time_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        time_stamp = float(time_date.strftime("%s"))
        cus_id = order.get('customer').get("id")
        items = order.get('line_items')
        total_line_items_price = order.get('total_line_items_price')
        total_discounts = order.get('total_discounts')
        other_fees = total_price - (total_line_items_price - total_discounts)
        list_items = []
        for item in items:
            info_item = {}
            name_pr = item.get('name')
            price = item.get("price")
            quantity = item.get('quantity')
            id_pr = item.get('id')
            info_item['id_product'] = id_pr
            info_item['name_product'] = name_pr
            info_item['price'] = price
            info_item['quantity'] = quantity
            list_items.append(info_item)
        info['merchant_id'] = merchant_id
        info['user_id'] = user_id
        info['id_order'] = id_or
        info['name'] = name
        info['source_order'] = source_or
        info['total_price'] = total_price
        info['time_order'] = time_stamp
        info['list_items'] = list_items
        info['id_customer_haravan'] = cus_id
        info['source'] = "haravan"
        info['total_line_items_price'] = total_line_items_price
        info['total_discounts'] = total_discounts
        info['other_fees'] = other_fees
        info['update_at'] = time.time()
        check_order = DATABASE.order_bill.find_one({"id_order": id_or})
        if not check_order:
            info['created_at'] = time.time()
            DATABASE.order_bill.insert(info)
        else:
            DATABASE.order_bill.update({"id_order": id_or}, {'$set': info})


def get_total_amount_spent(merchant_id, user_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    total_spent = 0
    orders = DATABASE.order_bill.find(
        {'merchant_id': merchant_id, 'user_id': user_id})
    if orders:
        for order in orders:
            total_price = order.get('total_price')
            total_spent = total_spent + total_price
    return total_spent


def get_total_order_customer(merchant_id, user_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    total = DATABASE.order_bill.find(
        {'merchant_id': merchant_id, 'user_id': user_id}).count()
    return total


def get_last_purchase(merchant_id, user_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    orders = DATABASE.order_bill.find(
        {'merchant_id': merchant_id, 'user_id': user_id})
    list_time = []
    if orders:
        for order in orders:
            time_order = int(order.get('time_order')) + 25200
            if time_order:
                time_date = datetime.utcfromtimestamp(
                    time_order).strftime('%H:%M %d-%m-%Y')
                list_time.append(time_date)
                return max(list_time)
            else:
                return ""
    else:
        return ""


def get_orders_customer(merchant_id, user_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    orders = DATABASE.order_bill.find({'merchant_id': merchant_id, 'user_id': user_id}).sort('time_order', -1).skip(
        page_size * (page - 1)).limit(page_size)
    list_order = []
    for order in orders:
        time_order = int(order.get('time_order')) + 25200
        if time_order:
            time_date = datetime.fromtimestamp(
                time_order).strftime('%H:%M %d-%m-%Y')
            order['date_create_order'] = time_date
        list_order.append(order)
    return list_order


def check_info_brandname_mobi(user_name, password):
    url = "http://smsbrandname.mobifone.vn/smsg/login.jsp?userName={}&password={}&bindMode=T".format(user_name,
                                                                                                     password)
    response = requests.get(url)
    result = json.loads(response.text)
    status = result.get('status')
    if status == "200":
        return True
    else:
        return False


def get_attachment_id_image_zalo(access_token, data_file):
    body = {
        'file': data_file
    }
    url = "https://openapi.zalo.me/v2.0/oa/upload/image?access_token={}".format(
        access_token)
    headers = {
        'Content-type': 'multipart/form-data',
    }
    result = requests.post(url=url, files=body)
    result = json.loads(result.text)
    status = result.get('error')
    if str(status) == "0":
        data = result.get('data')
        if data:
            att_id = data.get('attachment_id')
            return att_id
        else:
            return False
    else:
        return False


def detect_is_phone_zalo_first_time(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    shop_in_mer = get_shop_by_merchant(str(merchant_id))
    shop_ids = [ObjectId(shop['_id']) for shop in shop_in_mer]
    info = {}
    info['merchant_id'] = ObjectId(merchant_id)
    info['user.phone'] = {'$exists': True, "$nin": [None, ""]}
    results = DATABASE.customers.find(info)
    if results.count() > 0:
        for rec in results:
            user_id = rec.get('user_id')
            user = DATABASE.user.find_one({'_id': user_id})
            if user:
                phone = user.get('phone')
                if phone and len(phone) > 0:
                    is_check_zalo = is_check_zalo_oa(phone)
                    if not is_check_zalo:
                        url = settings.ZALO_ME + "{}".format(phone)
                        response = requests.get(url)
                        html = response.text.encode('utf8')
                        parsed_html = BeautifulSoup(html)
                        is_phone_zalo = parsed_html.body.find(
                            'img', attrs={'class': 'content__avatar'})
                        if is_phone_zalo:
                            link_avatar = parsed_html.body.find(
                                'img', attrs={'class': 'content__avatar'}).get('src')
                            if link_avatar:
                                status = "USAGE"
                                update_user_by_id(
                                    user_id=user_id, avatar=link_avatar)
                                check_cus = DATABASE.customers.find_one(
                                    {'merchant_id': merchant_id, 'user_id': user_id})
                                if check_cus:
                                    DATABASE.customers.update({'merchant_id': merchant_id, 'user_id': user_id},
                                                              {'$set': {'user.avatar': link_avatar}})
                                check_cus_loc = DATABASE.customers_location.find(
                                    {'shop_id': {"$in": shop_ids}, 'user_id': user_id})
                                if check_cus_loc:
                                    for user_loc in check_cus_loc:
                                        shop_id = user_loc.get('shop_id')
                                        DATABASE.customers_location.update({'shop_id': shop_id, 'user_id': user_id},
                                                                           {'$set': {'user.avatar': link_avatar}})
                                update_identity_phone_zalo(phone, status)
                        else:
                            status = "NO_USAGE"
                            update_identity_phone_zalo(phone, status)
            time.sleep(3)
        DATABASE.merchants.update({"_id": merchant_id}, {
                                  '$set': {'detect_zalo': True, 'update_at': time.time()}})


def update_identity_phone_zalo(phone, status):
    phone = str(phone).lstrip('0')
    phone = "84" + phone
    rec = DATABASE.identity.find_one({'identity': phone})
    info = {}
    if not rec:
        info['identity'] = phone
        info['created'] = time.time()
        info['social'] = {}
        info['social']['Zalo'] = status
        DATABASE.identity.insert(info)
    else:
        DATABASE.identity.update({'identity': phone}, {'$set': {'updated': time.time(),
                                                                'social.Zalo': status}})


def is_check_zalo_oa(phone):
    phone = str(phone).lstrip('0')
    phone = "84" + phone
    rec = DATABASE.identity.find_one({'identity': phone})
    if rec:
        is_check_zalo = rec.get('social').get('Zalo')
        if is_check_zalo and len(is_check_zalo) > 0:
            return True
        else:
            return False
    return False


def is_detect_zalo_phone_first_time(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    info_merchant = DATABASE.merchants.find_one({"_id": merchant_id})
    detect_zalo = info_merchant.get('detect_zalo')
    if detect_zalo:
        return True
    else:
        return False


def check_token_zns(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop_select = get_shop_info(shop_id)
    access_token = shop_select.get('zalo_access_token')
    if access_token and len(access_token) > 0:
        url = 'https://business.openapi.zalo.me/template/all?access_token={}&offset=10&limit=50'.format(
            access_token)
        headers = {
            'Content-type': 'application/json'
        }
        response = requests.get(url=url, headers=headers)
        result = json.loads(response.text)
        codeResult = result.get('error')
        if str(codeResult) == '0':
            return True
        else:
            return False
    else:
        return False


def update_merchant_app_id(merchant_id, merchant_id_app):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    DATABASE.merchants.update({'_id': merchant_id},
                              {'$set': {'merchant_id_app': merchant_id_app, 'update_at': time.time()}})


def get_merchants_partner(partner_id, page, page_size=settings.ITEMS_PER_PAGE):
    return DATABASE.merchants.find({'partner': partner_id}).sort('when', -1).skip(
        page_size * (page - 1)).limit(page_size)


def get_merchants_partner_count(partner_id):
    return DATABASE.merchants.find({'partner': partner_id}).count()


def get_background_register(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    info = DATABASE.shop.find_one({'_id': shop_id})
    login_form = info.get('login_form')
    background = login_form.get('background')
    if background and len(background) > 0:
        return background
    else:
        return None


def get_background_register_plus(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)

    info = DATABASE.shop.find_one({'_id': shop_id})
    login_form = info.get('plus_login_form')
    background = login_form.get('background')
    if background and len(background) > 0:
        return background
    else:
        return False


def total_visit_log(shop_id, merchant_id=None, start_time=None, end_time=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shops = []
    if merchant_id:
        shop_mer = get_shop_by_merchant(merchant_id)
        for shop_in_mer in shop_mer:
            shops.append(ObjectId(shop_in_mer['_id']))
    else:
        shops.append(ObjectId(shop_id))
    if start_time and end_time:
        return DATABASE.visit_log.find({'shop_id': {'$in': shops},
                                        'timestamp': {'$gte': start_time, '$lte': end_time}}).count()
    else:
        return DATABASE.visit_log.find({'shop_id': {'$in': shops}}).count()


def save_new_campaign(shop_id, name_camp, type_camp, active, is_birthday, step_1, step_2, step_3, step_4,
                      details_survey, details_spin, details_connect, details_group_customer):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    details_camp = {}
    details_camp['name'] = name_camp
    details_camp['shop_id'] = shop_id
    details_camp['type'] = type_camp
    details_camp['status'] = active
    details_camp['is_birthday'] = is_birthday
    details_camp['group_customer'] = details_group_customer
    details_camp['update_at'] = time.time()
    details_camp['create_at'] = time.time()
    details_camp['step_4'] = 'connect_success'
    details_camp['details_4'] = details_connect

    if str(step_1) == 'collect':
        details_camp['step_1'] = 'collect'
    elif str(step_1) == 'survey':
        details_camp['step_1'] = 'survey'
    elif str(step_1) == 'youtube':
        details_camp['step_1'] = 'youtube'
    elif str(step_1) == 'image':
        details_camp['step_1'] = 'image'
    elif str(step_1) == 'slides':
        details_camp['step_1'] = 'slides'
    elif str(step_1) == 'spin':
        details_camp['step_1'] = 'spin'
    elif str(step_1) == 'woay':
        details_camp['step_1'] = 'woay'
    else:
        details_camp['step_1'] = '0'
        details_camp['details_1'] = {}

    if str(step_2) == 'collect':
        details_camp['step_2'] = 'collect'
    elif str(step_2) == 'survey':
        details_camp['step_2'] = 'survey'
    elif str(step_2) == 'youtube':
        details_camp['step_2'] = 'youtube'
    elif str(step_2) == 'image':
        details_camp['step_2'] = 'image'
    elif str(step_2) == 'slides':
        details_camp['step_2'] = 'slides'
    elif str(step_2) == 'spin':
        details_camp['step_2'] = 'spin'
    elif str(step_2) == 'woay':
        details_camp['step_2'] = 'woay'
    else:
        details_camp['step_2'] = '0'

    if str(step_3) == 'collect':
        details_camp['step_3'] = 'collect'
    elif str(step_3) == 'survey':
        details_camp['step_3'] = 'survey'
    elif str(step_3) == 'youtube':
        details_camp['step_3'] = 'youtube'
    elif str(step_3) == 'image':
        details_camp['step_3'] = 'image'
    elif str(step_3) == 'slides':
        details_camp['step_3'] = 'slides'
    elif str(step_3) == 'spin':
        details_camp['step_3'] = 'spin'
    elif str(step_3) == 'woay':
        details_camp['step_3'] = 'woay'
    else:
        details_camp['step_3'] = '0'
    DATABASE.campaigns.insert(details_camp)


def update_new_campaign(shop_id, camp_id, name_camp, type_camp, active, is_birthday, step_1, step_2, step_3, step_4,
                        details_group_customer):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    details_camp = {}
    details_camp['name'] = name_camp
    details_camp['shop_id'] = shop_id
    details_camp['type'] = type_camp
    details_camp['status'] = active
    details_camp['is_birthday'] = is_birthday
    if type_camp == "register":
        details_camp['status'] = True
        details_camp['is_birthday'] = False
    details_camp['group_customer'] = details_group_customer
    details_camp['update_at'] = time.time()
    details_camp['step_4'] = 'connect_success'

    if str(step_1) == 'collect':
        details_camp['step_1'] = 'collect'
    elif str(step_1) == 'survey':
        details_camp['step_1'] = 'survey'
    elif str(step_1) == 'youtube':
        details_camp['step_1'] = 'youtube'
    elif str(step_1) == 'image':
        details_camp['step_1'] = 'image'
    elif str(step_1) == 'slides':
        details_camp['step_1'] = 'slides'
    elif str(step_1) == 'spin':
        details_camp['step_1'] = 'spin'
    elif str(step_1) == 'woay':
        details_camp['step_1'] = 'woay'
    elif str(step_1) == 'khai_bao_y_te':
        details_camp['step_1'] = 'khai_bao_y_te'
    else:
        details_camp['step_1'] = '0'

    if str(step_2) == 'collect':
        details_camp['step_2'] = 'collect'
    elif str(step_2) == 'survey':
        details_camp['step_2'] = 'survey'
    elif str(step_2) == 'youtube':
        details_camp['step_2'] = 'youtube'
    elif str(step_2) == 'image':
        details_camp['step_2'] = 'image'
    elif str(step_2) == 'slides':
        details_camp['step_2'] = 'slides'
    elif str(step_2) == 'spin':
        details_camp['step_2'] = 'spin'
    elif str(step_2) == 'woay':
        details_camp['step_2'] = 'woay'
    elif str(step_2) == 'khai_bao_y_te':
        details_camp['step_2'] = 'khai_bao_y_te'
    else:
        details_camp['step_2'] = '0'

    if str(step_3) == 'collect':
        details_camp['step_3'] = 'collect'
    elif str(step_3) == 'survey':
        details_camp['step_3'] = 'survey'
    elif str(step_3) == 'youtube':
        details_camp['step_3'] = 'youtube'
    elif str(step_3) == 'image':
        details_camp['step_3'] = 'image'
    elif str(step_3) == 'slides':
        details_camp['step_3'] = 'slides'
    elif str(step_3) == 'spin':
        details_camp['step_3'] = 'spin'
    elif str(step_3) == 'woay':
        details_camp['step_3'] = 'woay'
    elif str(step_3) == 'khai_bao_y_te':
        details_camp['step_3'] = 'khai_bao_y_te'
    else:
        details_camp['step_3'] = '0'

    DATABASE.campaigns.update({'_id': camp_id, 'shop_id': shop_id}, {
                              '$set': details_camp})
    remove_detail_step_campaign(shop_id, camp_id, '1', step_1)
    remove_detail_step_campaign(shop_id, camp_id, '2', step_2)
    remove_detail_step_campaign(shop_id, camp_id, '3', step_3)


def remove_detail_step_campaign(shop_id, camp_id, step, type_page_camp):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    steps = DATABASE.details_step_campaign.find(
        {'camp_id': camp_id, 'shop_id': shop_id, 'step': step})
    for step in steps:
        step_id = step.get('_id')
        type_page = step.get('type_page')
        if type_page != type_page_camp:
            DATABASE.details_step_campaign.remove({'_id': step_id})


def close_campaign(shop_id, camp_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    camp = DATABASE.campaigns.find_one({"_id": camp_id})
    step_1 = camp.get('step_1')
    step_2 = camp.get('step_2')
    step_3 = camp.get('step_3')
    remove_detail_step_campaign(shop_id, camp_id, '1', step_1)
    remove_detail_step_campaign(shop_id, camp_id, '2', step_2)
    remove_detail_step_campaign(shop_id, camp_id, '3', step_3)


def save_step_campaign(shop_id, camp_id, step, type_page, details_step):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    details = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': camp_id, 'type_page': type_page, 'step': step})
    info = {}
    info['shop_id'] = shop_id
    info['camp_id'] = camp_id
    info['type_page'] = type_page
    info['details'] = details_step
    info['step'] = step
    if not details:
        info['create_at'] = time.time()
        info['update_at'] = time.time()
        DATABASE.details_step_campaign.insert(info)
    else:
        info['update_at'] = time.time()
        DATABASE.details_step_campaign.update(
            {'shop_id': shop_id, 'camp_id': camp_id,
                'type_page': type_page, 'step': step},
            {'$set': {'details': details_step}})


def get_detail_all_step(shop_id, camp_id, type_page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': camp_id, 'type_page': str(type_page)})
    if info:
        details = info.get('details')
        return details


def get_detail_step(shop_id, camp_id, type_page, step):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': camp_id, 'type_page': str(type_page), 'step': str(step)})
    if info:
        details = info.get('details')
        return details


def get_new_detail_step(shop_id, camp_id, type_page, step):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': camp_id, 'type_page': str(type_page), 'step': str(step)})
    if info:
        details = info.get('details')
        return details


def total_access_campaign(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.access_campaign_log.find({'camp_id': camp_id}).count()


def get_new_campaigns_default(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    camps = DATABASE.campaigns.find(
        {'shop_id': shop_id}).sort('create_at', 1).limit(2)
    campaigns = []
    for camp in camps:
        camp_id = camp.get('_id')
        total_access = total_access_campaign(camp_id)
        camp['total_access'] = total_access
        total_step = 1
        step_1 = camp.get('step_1')
        step_2 = camp.get('step_2')
        step_3 = camp.get('step_3')
        if step_1 != '0':
            total_step += 1
        if step_2 != '0':
            total_step += 1
        if step_3 != '0':
            total_step += 1
        camp['total_step'] = total_step
        campaigns.append(camp)
    return campaigns


def get_new_campaigns(shop_id, page, page_size, not_default=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    camps = []
    if not not_default:
        camps = DATABASE.campaigns.find({'shop_id': shop_id}).sort('update_at', -1).skip(page_size * (page - 1)) \
            .limit(page_size)
    else:
        camps = DATABASE.campaigns.find({'shop_id': shop_id, '_id': {'$nin': not_default}}).sort('update_at',
                                                                                                 -1).skip(
            page_size * (page - 1)) \
            .limit(page_size)
    campaigns = []
    for camp in camps:
        camp_id = camp.get('_id')
        total_access = total_access_campaign(camp_id)
        camp['total_access'] = total_access
        total_step = 1
        step_1 = camp.get('step_1')
        step_2 = camp.get('step_2')
        step_3 = camp.get('step_3')
        if step_1 != '0':
            total_step += 1
        if step_2 != '0':
            total_step += 1
        if step_3 != '0':
            total_step += 1
        camp['total_step'] = total_step
        campaigns.append(camp)
    return campaigns


def get_list_step(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    camp = DATABASE.campaigns.find_one({"_id": camp_id})
    list_step = []
    step_1 = camp.get('step_1')
    list_step.append(step_1)
    step_2 = camp.get('step_2')
    list_step.append(step_2)
    step_3 = camp.get('step_3')
    list_step.append(step_3)
    step_4 = camp.get('step_4')
    list_step.append(step_4)
    return list_step


def remove_image_slides(shop_id, camp_id, photo):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': camp_id, 'type_page': 'slides'})
    details = info.get('details')
    slides = details.get('slides')
    slides.remove(photo)
    DATABASE.details_step_campaign.update({'shop_id': shop_id, 'camp_id': camp_id, 'type_page': 'slides'},
                                          {'$set': {'details.slides': slides}})


def get_all_slides(shop_id, camp_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': camp_id, 'type_page': 'slides'})
    if info:
        details = info.get('details')
        if details:
            slides = details.get('slides')
            return slides
        else:
            return False
    else:
        return False


def create_new_camp(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    group_customer = {
        'date_type_select': 'week_day',
        'weekday_sun': True,
        'weekday_mon': True,
        'weekday_tue': True,
        'weekday_wed': True,
        'weekday_thu': True,
        'weekday_fri': True,
        'weekday_sat': True,
        'tags_group_customer': []
    }
    info = {
        'status': False,
        'step_1': '0',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'group_customer': group_customer,
        'type': 'default',
        'shop_id': shop_id,
        'name': 'Chưa đặt tên chiến dịch',
        'is_birthday': False,
        'create_at': time.time(),
        'update_at': time.time()
    }
    camp_id = DATABASE.campaigns.insert(info)
    info_connect_success = {
        'type_page': 'connect_success',
        'step': '4',
        'shop_id': shop_id,
        'details': {
            'display_coupon': False,
            'hotspot_method': 'default',
            'display_coupon_txt': '',
            'auto_popup': '',
            'default_code': '',
            'content_connect': '',
            'connect_button': '',

        },
        'camp_id': camp_id
    }
    connect_sucess = DATABASE.details_step_campaign.insert(
        info_connect_success)
    return camp_id


def remove_new_campaign(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    camps = DATABASE.campaigns.find({'shop_id': shop_id})
    for camp in camps:
        camp_id = camp.get('_id')
        step_1 = camp.get('step_1')
        step_2 = camp.get('step_2')
        step_3 = camp.get('step_3')
        status = camp.get('status')
        if (step_1 == '0' and step_2 == '0' and step_3 == '0' and str(status) == 'False'):
            DATABASE.campaigns.remove({'_id': camp_id})
            DATABASE.details_step_campaign.remove({'camp_id': camp_id})


def update_status_new_camp(camp_id, status):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    DATABASE.campaigns.update({'_id': camp_id}, {'$set': {'status': status}})


def update_birthday_new_camp(camp_id, status):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    DATABASE.campaigns.update(
        {'_id': camp_id}, {'$set': {'is_birthday': status}})


def num_camp_active(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    count = 0
    camps = DATABASE.campaigns.find({'shop_id': shop_id, 'type': 'default'})
    for camp in camps:
        status = camp.get('status')
        if str(status) == 'True':
            count = count + 1
    return count


def remove_new_campaign_by_id(shop_id, camp_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    campaign = DATABASE.campaigns.remove({'shop_id': shop_id, '_id': camp_id})
    DATABASE.details_step_campaign.remove(
        {'shop_id': shop_id, 'camp_id': camp_id})


def get_default_camp(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    campaign = DATABASE.campaigns.find({'shop_id': shop_id, 'type': 'default'}).sort(
        'sequence', 1).limit(1)
    if campaign.count() > 0:
        camp = campaign[0]
        return camp


def update_init_default_camp(shop_id, camp_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    DATABASE.campaigns.update({'_id': camp_id, 'shop_id': shop_id}, {
                              '$set': {'step_1': 'slides'}})


def count_visit_by_weekday(shop_ids, start_time=None, end_time=None):
    shop_ids = [ObjectId(shop_id) for shop_id in shop_ids]
    visit_log = []
    if start_time and end_time:
        visit_log = DATABASE.visit_log.aggregate(
            [
                {"$match": {"shop_id": {'$in': shop_ids},
                            "timestamp": {'$gte': start_time, '$lte': end_time}}},
                {
                    "$project":
                        {

                            "dayOfWeek": {"$dayOfWeek": "$timestamp_date"}
                        }
                },
                {
                    "$group": {
                        '_id': '$dayOfWeek',
                        'count': {'$sum': 1}
                    }
                }])
    else:
        visit_log = DATABASE.visit_log.aggregate(
            [
                {"$match": {"shop_id": {'$in': shop_ids}}},
                {
                    "$project":
                        {

                            "dayOfWeek": {"$dayOfWeek": "$timestamp_date"}
                        }
                },
                {
                    "$group": {
                        '_id': '$dayOfWeek',
                        'count': {'$sum': 1}
                    }
                }])
    return visit_log


def count_visit_walkthrough(shop_ids, start_time=None, end_time=None):
    shop_ids = [ObjectId(shop_id) for shop_id in shop_ids]
    if start_time and end_time:
        visit_log = DATABASE.send_activity_log.aggregate(
            [
                {"$match": {"shop_id": {'$in': shop_ids},
                            "when": {'$gte': start_time, '$lte': end_time}}},
                {"$lookup":
                    {
                        "from": "visit_log",
                        "let": {
                            'customer_id': "$customer_id",
                            'when': "$when"
                        }, 'pipeline': [
                            {'$match': {'$expr':
                                        {'$and':
                                         [
                                             {'$eq': ["$user_id",
                                                      "$$customer_id"]},
                                             {'$gte': [
                                                 "$timestamp", "$$when"]},
                                             {'$lte': ["$timestamp", {
                                                 '$add': ["$$when", 7]}]}
                                         ]
                                         }
                                        }}
                        ],
                        "as": "visits"
                    }},

                {"$match": {'visits': {"$exists": True, "$ne": []}}},
                {'$group': {'_id': '$customer_id'}},
                {'$count': 'count'}
            ])
        return [log for log in visit_log]

    else:
        visit_log = DATABASE.send_activity_log.aggregate(
            [
                {"$match": {"shop_id": {'$in': shop_ids}}},
                {"$lookup":
                    {
                        "from": "visit_log",
                        "let": {
                            'customer_id': "$customer_id",
                            'when': "$when"
                        }, 'pipeline': [
                            {'$match': {'$expr':
                                        {'$and':
                                         [
                                             {'$eq': ["$user_id",
                                                      "$$customer_id"]},
                                             {'$gte': [
                                                 "$timestamp", "$$when"]},
                                             {'$lte': ["$timestamp", {
                                                 '$add': ["$$when", 7]}]}
                                         ]
                                         }
                                        }}
                        ],
                        "as": "visits"
                    }},

                {"$match": {'visits': {"$exists": True, "$ne": []}}},
                {'$group': {'_id': '$customer_id'}},
                {'$count': 'count'}
            ])
        return [log for log in visit_log]


def check_reset_password(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    result = None
    merchant = get_merchant(merchant_id)
    last_update = merchant.get('update_password')
    if last_update:
        now = time.time()
        if now - int(last_update) > 90 * 86400:
            result = True
            return result
    return False


def init_verify_email_camp(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    new_register_camp = 'Chiến dịch xác thực email'
    info_camp = {
        'shop_id': shop_id,
        'type': 'verify_email',
        'step_1': '0',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
        },
        'create_at': time.time(),
        'update_at': time.time(),
        'status': False,
        'is_birthday': False,
        'name': new_register_camp
    }
    details = {
        'content_connect': '',
        'connect_button': '',
        'display_coupon': False,
        'display_coupon_txt': '',
        'hotspot_method': 'default',
        'default_code': '',
        'redirect_type': '',
        'auto_website': '',
        'auto_popup_ios': '',
        'auto_popup_android': '',
        'auto_facebook_page': '',
        'auto_popup_zalo': '',
        'auto_popup_insta': '',
        'auto_facebook_mess': ''
    }

    info_connect = {
        'camp_id': new_register_camp,
        'type_page': "connect_success",
        'shop_id': shop_id,
        'step': '4',
        'details': details
    }
    new_register_camp = DATABASE.campaigns.insert(info_camp)
    DATABASE.details_step_campaign.insert(info_connect)


def has_verify_email_camp(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    camps = DATABASE.campaigns.find({'shop_id': shop_id})
    verify_email = False
    for camp in camps:
        type_camp = camp.get('type')
        if str(type_camp) == 'verify_email':
            verify_email = True
    return verify_email


def update_verify_email_campaign(shop_id, campaign_id, term, subject_email, content_email):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(campaign_id, ObjectId):
        campaign_id = ObjectId(campaign_id)
    DATABASE.campaigns.update({'_id': campaign_id}, {
                              '$set': {'step_1': 'terms', 'step_2': 'collect'}})
    check = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': campaign_id, 'step': '1', 'type_page': 'terms'})
    check_collect = DATABASE.details_step_campaign.find_one(
        {'shop_id': shop_id, 'camp_id': campaign_id, 'step': '2', 'type_page': 'collect'})
    info_step = {
        'step': '1',
        'shop_id': shop_id,
        'type_page': 'terms',
        'camp_id': campaign_id,
        'details': term
    }

    detail_collect = {
        'phone': False,
        'name': True,
        'birthday': False,
        'year_birthday': False,
        'gender': False,
        'email': True,
        'welcome_text': '',
        'welcome_button': False,
        'birthday_text': False,
        'phone_require': False,
        'name_require': True,
        'birthday_require': False,
        'gender_require': False,
        'email_require': True,
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
        'background': ''
    }
    info_collect = {
        'step': '2',
        'shop_id': shop_id,
        'type_page': 'collect',
        'camp_id': campaign_id,
        'details': detail_collect
    }
    if not check_collect:
        DATABASE.details_step_campaign.insert(info_collect)
    if not check:
        DATABASE.details_step_campaign.insert(info_step)
    else:
        DATABASE.details_step_campaign.update(
            {'shop_id': shop_id, 'camp_id': campaign_id, 'step': '1'}, {'$set': {'details': term}})


def get_customer_by_user_id(merchant_id, user_id, shop_id=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.customers_location.find_one({'user_id': user_id, 'shop_id': shop_id})
    else:
        return DATABASE.customers.find_one({'user_id': user_id, 'merchant_id': merchant_id})


def get_otp_log(merchant_id, page, page_size, shop_id=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    customers = []
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        logs = DATABASE.otp_log.find({'merchant_id': merchant_id, 'shop_id': shop_id}).sort(
            'when', -1).skip(page_size * (page - 1)).limit(page_size)
        for log in logs:
            user_id = log.get('user_id')
            user = get_customer_by_user_id(
                merchant_id=merchant_id, user_id=user_id, shop_id=shop_id)
            if user:
                info_user = user.get('user')
                name = info_user.get('name')
                log['name'] = name
            customers.append(log)
    else:
        logs = DATABASE.otp_log.find({'merchant_id': merchant_id}).sort(
            'when', -1).skip(page_size * (page - 1)).limit(page_size)
        for log in logs:
            user_id = log.get('user_id')
            user = get_customer_by_user_id(
                merchant_id=merchant_id, user_id=user_id)
            if user:
                info_user = user.get('user')
                name = info_user.get('name', '')
                log['name'] = name
            customers.append(log)
    return customers


def get_total_otp_log(merchant_id, shop_id=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    total = 0
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        total = DATABASE.otp_log.find(
            {'merchant_id': merchant_id, 'shop_id': shop_id}).count()

    else:
        total = DATABASE.otp_log.find({'merchant_id': merchant_id}).count()

    return total


def get_otp_log_by_id(log_id):
    if not isinstance(log_id, ObjectId):
        log_id = ObjectId(log_id)
    return DATABASE.otp_log.find_one({'_id': log_id})


def insert_otp_log(merchant_id, shop_id, user_id, send_type, message, client_key, email_otp):
    if not isinstance(
            merchant_id,
            ObjectId):
        merchant_id = ObjectId(
            merchant_id
        )
    if not isinstance(
            shop_id,
            ObjectId):
        shop_id = ObjectId(
            shop_id
        )
    if not isinstance(
            user_id,
            ObjectId):
        user_id = ObjectId(
            user_id
        )
    info = {
        'merchant_id': merchant_id,
        'shop_id': shop_id,
        'send_type': send_type,
        'user_id': user_id,
        'message': message,
        'reception': email_otp,
        'client_key': client_key,
        'when': time.time(),
        'verify_email': False,
    }
    activity_id = DATABASE.otp_log.insert(info)
    return activity_id


def update_resend_activity(activity_id, result):
    if not isinstance(
            activity_id,
            ObjectId):
        activity_id = ObjectId(
            activity_id
        )
    DATABASE.otp_log.update({
        '_id': activity_id
    }, {'$set': {
        'result': result
    }})


def get_declaration_shop(shop_id, page, page_size):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    result = []
    response = DATABASE.declaration_results.find({'shop_id': shop_id}).skip(page_size * (page - 1)) \
        .limit(page_size)
    for res in response:
        status = []
        rep = {}
        client_mac = res.get('client_mac')
        info = DATABASE.customers_location.find_one(
            {'user.client_mac': client_mac})
        if info:
            user = info.get('user')
            rep['name'] = user.get('name')
            rep['phone'] = user.get('phone')
            rep['email'] = user.get('email')
            rep['time'] = res.get('when')
            res_1 = res.get('res_1')
            res_2 = res.get('res_2')
            res_3 = res.get('res_3')
            res_4 = res.get('res_4')
            if res_1:
                status.append('có triệu chứng')
            if res_2:
                status.append('có tiếp xúc')
            if res_3:
                status.append('có di chuyển')
            if res_4:
                status.append('ở vùng dịch')
            if len(status) == 0:
                status.append('bình thường')
            rep['status'] = status
            result.append(rep)
    return result


def count_get_declaration_shop(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    response = DATABASE.declaration_results.find({'shop_id': shop_id}).count()
    return response


def register_client_mac(client_mac):
    info = {}
    if client_mac:
        client_mac = normalize(client_mac) if client_mac else None
    if client_mac:
        info['client_mac'] = [client_mac]
    return DATABASE.user.insert(info)


def get_user_loc(client_mac, shop_id):
    client_mac_lower = client_mac.lower()
    client_mac_upper = client_mac.upper()
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return DATABASE.customers_location.find_one({
        'shop_id': shop_id,
        'user.client_mac': {'$in': [client_mac, client_mac_upper, client_mac_lower]}
    })


def remove_visit_shop(user_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    DATABASE.visit_log.remove({'shop_id': shop_id, 'user_id': user_id})


def create_visit_log(user_id, shop_id, visits):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    shop = get_shop_info(shop_id=shop_id)
    merchant_id = shop.get('merchant_id')
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    b = time.time() - 86400
    a = time.time() - 86400 * 7
    i = 1
    last_visit = int(a)
    while i <= int(visits):
        timestamp = random.randint(int(a), int(b))
        time_date = time.strftime("%D %H:%M", time.localtime(int(timestamp)))
        time_date_split = time_date.split(' ')
        time_day = time_date_split[0]
        time_hour = time_date_split[1]
        visit_id = DATABASE.visit_log.insert({
            'shop_id': shop_id,
            'user_id': user_id,
            'timestamp': timestamp,
            'time_day': time_day,
            'time_hour': time_hour,
            'timestamp_date': datetime.fromtimestamp(timestamp)
        })
        if last_visit < int(timestamp):
            info_mer = {}
            info_mer['last_visit'] = timestamp
            info_mer['update_at'] = timestamp
            info_mer['total_visit'] = int(visits)
            DATABASE.customers.update(
                {'user_id': user_id, 'merchant_id': merchant_id}, {'$set': info_mer})
            DATABASE.customers_location.update(
                {'user_id': user_id, 'shop_id': shop_id}, {'$set': info_mer})
        i += 1


def create_customer(shop_id, user_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)
    shop = get_shop_info(shop_id=shop_id)
    merchant_id = shop.get('merchant_id')
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    user_info = get_user_info(user_id=user_id)
    info_mer = {}
    info_mer['merchant_id'] = merchant_id
    info_mer['last_visit'] = time.time() - 86400 * 7
    info_mer['update_at'] = time.time() - 86400 * 7
    info_mer['user_id'] = user_id
    info_mer['user'] = user_info
    info_mer['total_visit'] = 0
    DATABASE.customers.insert(info_mer)
    info = {}
    info['shop_id'] = shop_id
    info['last_visit'] = time.time() - 86400 * 7
    info['update_at'] = time.time() - 86400 * 7
    info['user_id'] = user_id
    info['user'] = user_info
    info['total_visit'] = 0
    DATABASE.customers_location.insert(info)


def total_wifi_ads(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.wifi_ads.find({'merchant_id': merchant_id}).count()


def init_wifi_ads(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if str(request.cookies.get("langs")) == 'lo':
        name_return_camp = "ກັບຄືນກິດຈະກຳຂອງລູກຄ້າ"
        name_new_cus_camp = "ຂະບວນການລູກຄ້າໃໝ່"
    else:
        name_return_camp = "Chiến dịch khách hàng quay trở lại"
        name_new_cus_camp = "Chiến dịch khách hàng mới"
    info_register = {
        'merchant_id': merchant_id,
        'type': 'register',
        'step_1': 'collect',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
        },
        'create_at': time.time(),
        'update_at': time.time(),
        'status': True,
        'is_birthday': False,
        'name': name_new_cus_camp
    }

    new_register_camp = DATABASE.wifi_ads.insert(info_register)

    details = {
        'content_connect': '',
        'connect_button': '',
        'display_coupon': False,
        'display_coupon_txt': '',
        'hotspot_method': 'default',
        'default_code': '',
        'redirect_type': '',
        'auto_website': '',
        'auto_popup_ios': '',
        'auto_popup_android': '',
        'auto_facebook_page': '',
        'auto_popup_zalo': '',
        'auto_popup_insta': '',
        'auto_facebook_mess': ''
    }
    info_connect = {
        'camp_id': new_register_camp,
        'type_page': "connect_success",
        'merchant_id': merchant_id,
        'step': '4',
        'details': details
    }
    # shop_select = get_shop_info(shop_id)
    # login_form = shop_select.get('login_form', {})
    login_form = {}
    info_collect = {
        'camp_id': new_register_camp,
        'type_page': "collect",
        'merchant_id': merchant_id,
        'step': '1',
        'details': login_form
    }
    DATABASE.details_step_wifi_ads.insert(info_collect)
    DATABASE.details_step_wifi_ads.insert(info_connect)
    info_default = {
        'merchant_id': merchant_id,
        'type': 'default',
        'step_1': '0',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'create_at': time.time(),
        'update_at': time.time(),
        'group_customer': {
            'tags_group_customer': [],
            'min_visit': '',
            'max_visit': '',
            'date_type_select': 'week_day',
            'weekday_sun': True,
            'weekday_mon': True,
            'weekday_tue': True,
            'weekday_wed': True,
            'weekday_thu': True,
            'weekday_fri': True,
            'weekday_sat': True,
            'min_day': '',
            'max_day': '',
            'event_start_picker': '',
            'event_end_picker': '',
            'min_hour': '00:00',
            'max_hour': '23:30',
            'convert_min_hour': 0,
            'convert_max_hour': 23.5,
            'timestamp_start_event': 0,
            'timestamp_end_event': 0
        },
        'status': True,
        'is_birthday': False,
        'name': name_return_camp
    }
    new_default_camp = DATABASE.wifi_ads.insert(info_default)
    info_connect = {
        'camp_id': new_default_camp,
        'type_page': "connect_success",
        'merchant_id': merchant_id,
        'step': '4',
        'details': details
    }
    DATABASE.details_step_wifi_ads.insert(info_connect)


def get_wifi_ads_camps(merchant_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    camps = DATABASE.wifi_ads.find({'merchant_id': merchant_id}).sort('update_at', -1).skip(page_size * (page - 1)) \
        .limit(page_size)

    campaigns = []
    for camp in camps:
        camp_id = camp.get('_id')
        total_access = total_access_campaign(camp_id)
        camp['total_access'] = total_access
        total_step = 1
        step_1 = camp.get('step_1')
        step_2 = camp.get('step_2')
        step_3 = camp.get('step_3')
        if step_1 != '0':
            total_step += 1
        if step_2 != '0':
            total_step += 1
        if step_3 != '0':
            total_step += 1
        camp['total_step'] = total_step
        total_shops = 0
        try:
            total_shops = len(camp.get('shops_distribution'))
        except:
            total_shops = 0
        camp['total_shops'] = total_shops
        target_campaign = 0
        try:
            target_campaign = camp.get('target_campaign', 0)
            if not target_campaign:
                target_campaign = 0
        except:
            target_campaign = 0
        print (total_access)
        print (target_campaign)
        if int(total_access) >= int(target_campaign):
            camp['result'] = True
        else:
            camp['result'] = False
        campaigns.append(camp)
    return campaigns


def create_new_wifi_ads(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    group_customer = {
        'date_type_select': 'week_day',
        'weekday_sun': True,
        'weekday_mon': True,
        'weekday_tue': True,
        'weekday_wed': True,
        'weekday_thu': True,
        'weekday_fri': True,
        'weekday_sat': True,
        'tags_group_customer': []
    }
    info = {
        'status': False,
        'step_1': '0',
        'step_2': '0',
        'step_3': '0',
        'step_4': 'connect_success',
        'group_customer': group_customer,
        'type': 'default',
        'merchant_id': merchant_id,
        'name': 'Chưa đặt tên chiến dịch',
        'is_birthday': False,
        'create_at': time.time(),
        'update_at': time.time()
    }
    camp_id = DATABASE.wifi_ads.insert(info)
    info_connect_success = {
        'type_page': 'connect_success',
        'step': '4',
        'merchant_id': merchant_id,
        'details': {
            'display_coupon': False,
            'hotspot_method': 'default',
            'display_coupon_txt': '',
            'auto_popup': '',
            'default_code': '',
            'content_connect': '',
            'connect_button': '',

        },
        'camp_id': camp_id
    }
    connect_sucess = DATABASE.details_step_wifi_ads.insert(
        info_connect_success)
    return camp_id


def get_new_wifi_ads_by_id(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    camp = DATABASE.wifi_ads.find_one({'_id': camp_id})
    return camp


def get_list_step_wifi_ads(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    camp = DATABASE.wifi_ads.find_one({"_id": camp_id})
    list_step = []
    step_1 = camp.get('step_1')
    list_step.append(step_1)
    step_2 = camp.get('step_2')
    list_step.append(step_2)
    step_3 = camp.get('step_3')
    list_step.append(step_3)
    step_4 = camp.get('step_4')
    list_step.append(step_4)
    return list_step


def get_details_step_wifi_ads(merchant_id, camp_id, type_page, step):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = DATABASE.details_step_wifi_ads.find_one(
        {'merchant_id': merchant_id, 'camp_id': camp_id, 'type_page': str(type_page), 'step': str(step)})
    if info:
        details = info.get('details')
        return details


def close_wifi_ads_camp(merchant_id, camp_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    camp = DATABASE.wifi_ads.find_one({"_id": camp_id})
    step_1 = camp.get('step_1')
    step_2 = camp.get('step_2')
    step_3 = camp.get('step_3')
    remove_detail_step_wifi_ads(merchant_id, camp_id, '1', step_1)
    remove_detail_step_wifi_ads(merchant_id, camp_id, '2', step_2)
    remove_detail_step_wifi_ads(merchant_id, camp_id, '3', step_3)


def remove_detail_step_wifi_ads(merchant_id, camp_id, step, type_page_camp):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    steps = DATABASE.details_step_wifi_ads.find(
        {'camp_id': camp_id, 'merchant_id': merchant_id, 'step': step})
    for step in steps:
        step_id = step.get('_id')
        type_page = step.get('type_page')
        if type_page != type_page_camp:
            DATABASE.details_step_wifi_ads.remove({'_id': step_id})


def get_all_slides_wifi_ads(merchant_id, camp_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = DATABASE.details_step_campaign.find_one(
        {'merchant_id': merchant_id, 'camp_id': camp_id, 'type_page': 'slides'})
    if info:
        details = info.get('details')
        if details:
            slides = details.get('slides')
            return slides
        else:
            return False
    else:
        return False


def update_init_default_wifi_ads(merchant_id, camp_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    DATABASE.campaigns.update({'_id': camp_id, 'merchant_id': merchant_id}, {
                              '$set': {'step_1': 'slides'}})


def save_step_wifi_ads(merchant_id, camp_id, step, type_page, details_step):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    details = DATABASE.details_step_wifi_ads.find_one(
        {'merchant_id': merchant_id, 'camp_id': camp_id, 'type_page': type_page, 'step': step})
    info = {}
    info['merchant_id'] = merchant_id
    info['camp_id'] = camp_id
    info['type_page'] = type_page
    info['details'] = details_step
    info['step'] = step
    if not details:
        info['create_at'] = time.time()
        info['update_at'] = time.time()
        DATABASE.details_step_wifi_ads.insert(info)
    else:
        info['update_at'] = time.time()
        DATABASE.details_step_wifi_ads.update(
            {'merchant_id': merchant_id, 'camp_id': camp_id,
                'type_page': type_page, 'step': step},
            {'$set': {'details': details_step}})


def save_wifi_ads(merchant_id, camp_id, name_camp, type_camp, active, is_birthday, step_1, step_2, step_3, step_4, target_campaign,
                  type_campaign, details_group_customer, details_group_distribution, shops_distribution, tags_camp):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    details_camp = {}
    details_camp['name'] = name_camp
    details_camp['merchant_id'] = merchant_id
    details_camp['type'] = type_camp
    details_camp['status'] = active
    details_camp['is_birthday'] = is_birthday
    details_camp['target_campaign'] = target_campaign
    details_camp['type_campaign'] = type_campaign
    details_camp['tags'] = tags_camp
    if type_camp == "register":
        details_camp['status'] = True
        details_camp['is_birthday'] = False
    details_camp['group_customer'] = details_group_customer
    details_camp['update_at'] = time.time()
    details_camp['group_distribution'] = details_group_distribution
    details_camp['shops_distribution'] = shops_distribution
    details_camp['step_4'] = 'connect_success'

    if str(step_1) == 'collect':
        details_camp['step_1'] = 'collect'
    elif str(step_1) == 'survey':
        details_camp['step_1'] = 'survey'
    elif str(step_1) == 'template':
        details_camp['step_1'] = 'template'
    elif str(step_1) == 'youtube':
        details_camp['step_1'] = 'youtube'
    elif str(step_1) == 'image':
        details_camp['step_1'] = 'image'
    elif str(step_1) == 'slides':
        details_camp['step_1'] = 'slides'
    elif str(step_1) == 'spin':
        details_camp['step_1'] = 'spin'
    elif str(step_1) == 'woay':
        details_camp['step_1'] = 'woay'
    elif str(step_1) == 'khai_bao_y_te':
        details_camp['step_1'] = 'khai_bao_y_te'
    else:
        details_camp['step_1'] = '0'

    if str(step_2) == 'collect':
        details_camp['step_2'] = 'collect'
    elif str(step_2) == 'survey':
        details_camp['step_2'] = 'survey'
    elif str(step_2) == 'template':
        details_camp['step_2'] = 'template'
    elif str(step_2) == 'youtube':
        details_camp['step_2'] = 'youtube'
    elif str(step_2) == 'image':
        details_camp['step_2'] = 'image'
    elif str(step_2) == 'slides':
        details_camp['step_2'] = 'slides'
    elif str(step_2) == 'spin':
        details_camp['step_2'] = 'spin'
    elif str(step_2) == 'woay':
        details_camp['step_2'] = 'woay'
    elif str(step_2) == 'khai_bao_y_te':
        details_camp['step_2'] = 'khai_bao_y_te'
    else:
        details_camp['step_2'] = '0'

    if str(step_3) == 'collect':
        details_camp['step_3'] = 'collect'
    elif str(step_3) == 'survey':
        details_camp['step_3'] = 'survey'
    elif str(step_3) == 'template':
        details_camp['step_3'] = 'template'
    elif str(step_3) == 'youtube':
        details_camp['step_3'] = 'youtube'
    elif str(step_3) == 'image':
        details_camp['step_3'] = 'image'
    elif str(step_3) == 'slides':
        details_camp['step_3'] = 'slides'
    elif str(step_3) == 'spin':
        details_camp['step_3'] = 'spin'
    elif str(step_3) == 'woay':
        details_camp['step_3'] = 'woay'
    elif str(step_3) == 'khai_bao_y_te':
        details_camp['step_3'] = 'khai_bao_y_te'
    else:
        details_camp['step_3'] = '0'

    DATABASE.wifi_ads.update({'_id': camp_id, 'merchant_id': merchant_id}, {
                             '$set': details_camp})
    remove_detail_step_wifi_ads(merchant_id, camp_id, '1', step_1)
    remove_detail_step_wifi_ads(merchant_id, camp_id, '2', step_2)
    remove_detail_step_wifi_ads(merchant_id, camp_id, '3', step_3)


def update_wifi_ads(camp_id, status=None, is_birthday=None):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    info = {}
    if status:
        info['status'] = status
    if is_birthday:
        info['is_birthday'] = is_birthday
    DATABASE.wifi_ads.update({'_id': camp_id}, {'$set': info})


def remove_wifi_ads_by_id(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    campaign = DATABASE.wifi_ads.remove({'_id': camp_id})
    DATABASE.details_step_wifi_ads.remove({'camp_id': camp_id})


def list_survey_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    shop_in_mer = get_shop_by_merchant(str(merchant_id))
    list_id_shop = []
    result = []
    for shop in shop_in_mer:
        shop_id = shop.get('_id')
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        list_id_shop.append(shop_id)
    return DATABASE.survey_splash_page.find({'shop_id': {'$in': list_id_shop}})


def list_spin_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    shop_in_mer = get_shop_by_merchant(str(merchant_id))
    list_id_shop = []
    for shop in shop_in_mer:
        shop_id = shop.get('_id')
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        list_id_shop.append(shop_id)
    return DATABASE.mini_game_page.find({'shop_id': {'$in': list_id_shop}})


def get_shop_by_tag(tag_id):
    if not isinstance(tag_id, ObjectId):
        tag_id = ObjectId(tag_id)
    shop = DATABASE.shop.find({'tags': tag_id})
    return shop


def filter_wifi_ads(page=None,
                    min_impressions=None,
                    max_impressions=None,
                    status_filter=None,
                    min_target=None,
                    max_target=None,
                    tags_filter=None,
                    from_create=None,
                    to_create=None,
                    from_perform=None,
                    to_perform=None,
                    result_filter=None,
                    loc_filter=None,
                    type_campaign_filter=None):
    info = {}
    if type_campaign_filter and type_campaign_filter != "type_campaign_all":
        info['type_campaign'] = type_campaign_filter
    if status_filter and status_filter != "status_all":
        if status_filter == "status_yes":
            info['status'] = True
        else:
            info['status'] = False
    if from_create and len(from_create) > 0:
        time_from_create = time.mktime(
            datetime.strptime(from_create, "%d-%m-%Y").timetuple())
        info['create_at']['$gte'] = time_from_create
    if to_create and len(to_create) > 0:
        time_to_create = time.mktime(
            datetime.strptime(to_create, "%d-%m-%Y").timetuple())
        info['create_at']['$lte'] = time_to_create
    if loc_filter and len(loc_filter) > 0:
        list_loc = []
        for loc in loc_filter:
            if not isinstance(loc, ObjectId):
                loc = ObjectId(loc)
            list_loc.append(loc)
        info['shops_distribution'] = {'$in': list_loc}
    if min_target and len(min_target) > 0:
        info['target_campaign']['$gte'] = int(min_target)
    if max_target and len(max_target) > 0:
        info['target_campaign']['$lte'] = int(max_target)
    if tags_filter and len(tags_filter) > 0:
        list_tag = []
        for tag in tags_filter:
            if not isinstance(tag, ObjectId):
                tag = ObjectId(tag)
            list_tag.append(tag)
        info['tags'] = {'$in': list_tag}
    camps = []
    campaigns = DATABASE.wifi_ads.find(info)
    if not min_impressions:
        min_impressions = 0
    if not max_impressions:
        max_impressions = 1000000000
    if campaigns:
        from_per = 0
        to_per = 0
        if from_perform and len(from_perform) > 0:
            from_per = time.mktime(datetime.strptime(
                from_perform, "%d-%m-%Y").timetuple())
        if to_perform and len(to_perform) > 0:
            to_per = time.mktime(datetime.strptime(
                to_perform, "%d-%m-%Y").timetuple())
        for camp in campaigns:
            camp_id = camp.get('_id')
            target_campaign = camp.get('target_campaign', 0)
            total_visit = 0
            if from_per != 0 and to_per != 0:
                total_visit = DATABASE.access_campaign_log.find(
                    {'camp_id': camp_id, 'create_at': {'$gte': from_per, '$lte': to_per}}).count()
            else:
                total_visit = DATABASE.access_campaign_log.find(
                    {'camp_id': camp_id}).count()
            if total_visit >= min_impressions and total_visit <= max_impressions:
                if result_filter == "result_yes" and total_visit >= target_campaign:
                    camps.append(camp)
                elif result_filter == "result_no" and total_visit < target_campaign:
                    camps.append(camp)
                elif result_filter == "result_all":
                    camps.append(camp)
                else:
                    pass
    return camps


def wifi_ads_merchant(merchant_id, default_wifi, share_rate):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    DATABASE.merchants.update({'_id': merchant_id}, {
                              '$set': {'default_wifi': default_wifi, 'share_rate': share_rate}})


def get_total_grandstream(network):
    if network == "all":
        return DATABASE.grandstream.find({})
    else:
        if not isinstance(network, ObjectId):
            network = ObjectId(network)
        return DATABASE.grandstream.find({'network': network})


def total_grandstream(network):
    if network == "all":
        return DATABASE.grandstream.find({}).count()
    else:
        if not isinstance(network, ObjectId):
            network = ObjectId(network)
        return DATABASE.grandstream.find({'network': network}).count()


def grandstream_online(network):
    if network == "all":
        return DATABASE.grandstream.find({'active': True}).count()
    else:
        if not isinstance(network, ObjectId):
            network = ObjectId(network)
        return DATABASE.grandstream.find({'network': network}).count()


def get_networks():
    return DATABASE.network_grandstream.find({})


def add_months(sourcedate, months):
    month = sourcedate.month + months
    year = sourcedate.year + month // 12
    if month > 12:
        month = month % 12
        if month == 0:
            month = 12
    day = sourcedate.day
    date1 = str(day) + '-' + str(month) + '-' + str(year)
    end_contract = datetime.strptime(date1, '%d-%m-%Y')
    return end_contract


def get_shop_by_merchant_active(merchant_id):
    results = []
    recs = DATABASE.shop.find({'merchant_id': merchant_id})
    for rec in recs:
        rec['_id'] = str(rec['_id'])
        active = rec.get('active')
        date_start_contract = rec.get('date_start_contract')
        contract_period = rec.get('contract_period')
        if active and date_start_contract and contract_period:
            to_day = datetime.today()
            sourcedate = datetime.strptime(date_start_contract, '%d-%m-%Y')
            end_contract = add_months(sourcedate, int(contract_period))
            if end_contract > to_day:
                results.append(rec)
    return results


def grandstream_overview(network):
    if network == "all":
        return []
    else:
        if not isinstance(network, ObjectId):
            network = ObjectId(network)
        return DATABASE.grandstream_overview.find_one({'network': network})


def save_access(merchant_id, list_phone, list_identity):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    arr_phone = []
    arr_identity = []
    if list_phone:
        phones = list_phone.split(',')
        for phone in phones:
            phone = phone.strip()
            arr_phone.append(phone)
    if list_identity:
        identities = list_identity.split(',')
        for iden in identities:
            iden = iden.strip()
            arr_identity.append(iden)
    DATABASE.merchants.update({'_id': merchant_id}, {'$set': {
                              'arr_phone': arr_phone, 'arr_identity': arr_identity, 'list_phone': list_phone, 'list_identity': list_identity}})


def get_type_camp_chart(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    monoploy = DATABASE.wifi_ads.find(
        {'merchant_id': merchant_id, 'type_campaign': 'monopoly'}).count()
    share = DATABASE.wifi_ads.find(
        {'merchant_id': merchant_id, 'type_campaign': 'share'}).count()
    default = DATABASE.wifi_ads.find(
        {'merchant_id': merchant_id, 'type_campaign': 'default'}).count()
    partner = DATABASE.wifi_ads.find(
        {'merchant_id': merchant_id, 'type_campaign': 'partner'}).count()
    return [monoploy, share, default, partner]


def get_result_camp_chart(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    camps = DATABASE.wifi_ads.find({'merchant_id': merchant_id})
    total_camp = camps.count()
    complete_camp = 0
    for camp in camps:
        camp_id = camp.get('_id')
        target_campaign = camp.get('target_campaign')
        if not target_campaign or str(target_campaign) == 'None':
            target_campaign = 0
        total_visit = DATABASE.access_campaign_log.find(
            {'camp_id': camp_id}).count()
        if int(total_visit) >= int(target_campaign):
            complete_camp = complete_camp + 1
    return [complete_camp, total_camp - complete_camp]


def filter_camp_report(loc_filter=None, tags_filter=None):
    info = {}
    camps = []
    if loc_filter and len(loc_filter) > 0:
        list_loc = []
        for loc in loc_filter:
            if not isinstance(loc, ObjectId):
                loc = ObjectId(loc)
            list_loc.append(loc)
        info['shops_distribution'] = {'$in': list_loc}
    if tags_filter and len(tags_filter) > 0:
        list_tag = []
        for tag in tags_filter:
            if not isinstance(tag, ObjectId):
                tag = ObjectId(tag)
            list_tag.append(tag)
        info['tags'] = {'$in': list_tag}
    campaigns = DATABASE.wifi_ads.find(info)
    if campaigns:
        for camp in campaigns:
            camp_id = camp.get('_id')
            target_campaign = 0
            try:
                target_campaign = camp.get('target_campaign', 0)
            except:
                target_campaign = 0
            total_visit = DATABASE.access_campaign_log.find(
                {'camp_id': camp_id}).count()
            camp['total_access'] = total_visit
            if total_visit >= target_campaign:
                camp['result'] = True
            else:
                camp['result'] = False
            total_shops = 0
            try:
                total_shops = len(camp.get('shops_distribution'))
            except:
                total_shops = 0
            camp['total_shops'] = total_shops
            camps.append(camp)
    return camps


def update_templates_wifi_ads(merchant_id, name_temp, email_content, design, temp_id=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if temp_id:
        if not isinstance(temp_id, ObjectId):
            temp_id = ObjectId(temp_id)
        DATABASE.templates_wifi_ads.update({'_id': temp_id, 'merchant_id': merchant_id}, {'$set': {
                                           'name_temp': name_temp, 'email_content': email_content, 'design': design, 'update_time': time.time()}})
    else:
        DATABASE.templates_wifi_ads.insert({'merchant_id': merchant_id, 'name_temp': name_temp,
                                            'email_content': email_content, 'design': design, 'update_time': time.time(), 'create_time': time.time()})


def get_temps_ads_by_merchant(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.templates_wifi_ads.find({'merchant_id': merchant_id})


def get_temp_wifi_ads(merchant_id, temp_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(temp_id, ObjectId):
        temp_id = ObjectId(temp_id)
    return DATABASE.templates_wifi_ads.find_one({'merchant_id': merchant_id, '_id': temp_id})


def remove_camp_ads(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    camps = DATABASE.wifi_ads.find({'merchant_id': merchant_id})
    for camp in camps:
        camp_id = camp.get('_id')
        step_1 = camp.get('step_1')
        step_2 = camp.get('step_2')
        step_3 = camp.get('step_3')
        name = camp.get('name')
        if step_1 == '0' and step_2 == '0' and step_3 == '0' and name == 'Chưa đặt tên chiến dịch':
            if not isinstance(camp_id, ObjectId):
                camp_id = ObjectId(camp_id)
            detail_step = DATABASE.details_step_wifi_ads.find_one(
                {'camp_id': camp_id, 'type_page': 'connect_success'})
            if detail_step:
                detail = detail_step.get('details')
                if 'auto_facebook_page' not in detail:
                    DATABASE.wifi_ads.remove({'_id': camp_id})
                    DATABASE.details_step_wifi_ads.remove({'camp_id': camp_id})


def remove_campaigns(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    camps = DATABASE.campaigns.find({'shop_id': shop_id})
    for camp in camps:
        camp_id = camp.get('_id')
        step_1 = camp.get('step_1')
        step_2 = camp.get('step_2')
        step_3 = camp.get('step_3')
        name = camp.get('name')
        active = camp.get('status')
        if step_1 == '0' and step_2 == '0' and step_3 == '0' and name == 'Chưa đặt tên chiến dịch' and active == False:
            if not isinstance(camp_id, ObjectId):
                camp_id = ObjectId(camp_id)
            detail_step = DATABASE.details_step_campaign.find_one(
                {'camp_id': camp_id, 'type_page': 'connect_success'})
            if detail_step:
                detail = detail_step.get('details')
                if 'auto_facebook_page' not in detail:
                    DATABASE.campaigns.remove({'_id': camp_id})
                    DATABASE.details_step_campaign.remove({'camp_id': camp_id})


def get_all_camp_ads(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    camps = DATABASE.wifi_ads.find({'merchant_id': merchant_id})
    return camps


def login_ghdc(username, password):
    url = settings.GHDC_domain + \
        "mmsapi/controller/login?username={}&password={}".format(
            username, password)

    payload = {}
    headers = {}
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            res = response.json()
            code = res.get("code")
            if code == 0:
                data = json.loads(res.get("data"))
                token = data.get("api_token")
                return token
            else:
                return False
        else:
            return False
    except:
        return False


def check_ghdc(merchant_id):
    return DATABASE.app_synchronized.find_one({'merchant_id': str(merchant_id), 'name_app': 'GHDC', 'status': True})


def insert_ghdc_campaign(merchant_id=None,
                         shop_id=None,
                         type_sms=None,
                         name_camp=None,
                         visit_from_date=None,
                         visit_to_date=None,
                         from_date=None,
                         to_date=None,
                         min_visit=None,
                         max_visit=None,
                         lost_day=None,
                         all_customers=None,
                         message=None,
                         date_start_send=None,
                         date_end_send=None,
                         brandname=None,
                         career=None,
                         type_cskh=None,
                         type_qc=None,
                         price=None,
                         desc_camp=None,
                         predict_message=None,
                         tags_array=None,
                         gender_array=None,
                         cp_type=None,
                         mt_type=None,
                         sending_time=None,
                         max_mt_per_day=None,
                         max_mt_campaign=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    camp_id = DATABASE.ghdc_campaign.insert({
        'merchant_id': merchant_id,
        'shop_id': shop_id,
        'type_sms': type_sms,
        'name_camp': name_camp,
        'visit_from_date': visit_from_date,
        'visit_to_date': visit_to_date,
        'from_date': from_date,
        'to_date': to_date,
        'min_visit': min_visit,
        'max_visit': max_visit,
        'lost_day': lost_day,
        'all_customers': all_customers,
        'message': message,
        'date_start_send': date_start_send,
        'date_end_send': date_end_send,
        'brandname': brandname,
        'career': career,
        'type_cskh': type_cskh,
        'type_qc': type_qc,
        'price': price,
        'desc_camp': desc_camp,
        'predict_message': predict_message,
        'tags_array': tags_array,
        'gender_array': gender_array,
        'cp_type': cp_type,
        'mt_type': mt_type,
        'sending_time': sending_time,
        'max_mt_per_day': max_mt_per_day,
        'max_mt_campaign': max_mt_campaign,
        'when': time.time()
    })
    return camp_id


def get_list_ghdc_campaign(merchant_id,
                           shop_id,
                           type_sms=None,
                           page=None,
                           page_size=settings.ITEMS_PER_PAGE):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'merchant_id': merchant_id,
        'type_sms': type_sms,
        'shop_id': shop_id
    }
    recs = DATABASE.ghdc_campaign.find().sort(
        'when', -1).skip(page_size * (page - 1)).limit(page_size)
    return recs


def total_ghdc_campaign(merchant_id, shop_id, type_sms=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    info = {
        'merchant_id': merchant_id,
        'type_sms': type_sms,
        'shop_id': shop_id
    }
    return DATABASE.ghdc_campaign.find().count()


def get_ghdc_camp(camp_id):
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return DATABASE.ghdc_campaign.find_one({'_id': camp_id})


def save_register_brandname(merchant_id, photo_name, website_name, company_name, brandname, type_message, feilds):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    check_acc = DATABASE.register_brandname.find_one(
        {'merchant_id': merchant_id})
    status = 'pending'
    info = {
        'create_at': time.time(),
        'update_at': time.time(),
        'merchant_id':  merchant_id,
        'photo': photo_name,
        'website': website_name,
        'company_name': company_name,
        'brandname': brandname,
        'type_message': type_message,
        'feilds': feilds,
        'status': status
    }
    if not check_acc:
        DATABASE.register_brandname.insert(info)
    else:
        info['update_at'] = time.time()
        DATABASE.register_brandname.update(
            {'merchant_id': merchant_id}, {'$set': info})
    return True


def check_register_brandname(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.register_brandname.find_one({'merchant_id': merchant_id})


def save_buy_message(merchant_id, amount_new, type_mess):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    status = 'pending'
    info = {
        'merchant_id': merchant_id,
        'amount':  amount_new,
        'type_mess': type_mess,
        'when': time.time(),
        'status': status
    }
    DATABASE.buy_mess.insert(info)
    return True


def create_wifi_partner(merchant_id, name, address, phone, number_tax, status, person_contact, contact_phone, contact_department):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    wifi_partners_item = DATABASE.wifi_partners.insert_one({
        'merchant_id': merchant_id,
        'name': name,
        'address': address,
        'phone': phone,
        'number_tax': number_tax,
        'status': status,
        'person_contact': person_contact,
        'contact_phone': contact_phone,
        'contact_department': contact_department,
        'when': time.time()
    })
    return wifi_partners_item

def item_wifi_partner(merchant_id, item_id): 
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    
    wifi_partners_item = DATABASE.wifi_partners.find_one({
        'merchant_id': merchant_id,
        '_id': ObjectId(item_id)
    })
    return wifi_partners_item

def update_wifi_partner(merchant_id,
                        wifi_partner_id, 
                        name=None, 
                        address=None, 
                        phone=None, 
                        number_tax=None, 
                        status=None, 
                        person_contact=None,
                        contact_phone=None,
                        contact_department=None):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if not isinstance(wifi_partner_id, ObjectId):
        wifi_partner_id = ObjectId(wifi_partner_id)
    info = {}
    if name:
        info['name'] = name
    if address:
        info['address'] = address
    if phone:
        info['phone'] = phone
    if number_tax:
        info['number_tax'] = number_tax
    if person_contact:
        info['person_contact'] = person_contact 
    if contact_phone:
        info['contact_phone'] = contact_phone
    if contact_department:
        info['contact_department'] = contact_department
    info['status'] = status
    info['update_at'] = time.time()
    wifi_partners_item = DATABASE.wifi_partners.update_one({'_id': wifi_partner_id, 'merchant_id': merchant_id}, {'$set': info})
    return wifi_partners_item

def check_duplicate_wifi_partners(merchant_id, wifi_partner_id, data, type_data):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if type_data == "phone":
        return DATABASE.wifi_partners.find({'merchant_id': merchant_id, '_id': {'$ne':ObjectId(wifi_partner_id)},'phone': data}).count()
    elif type_data == "number_tax":
        return DATABASE.wifi_partners.find({'merchant_id': merchant_id, '_id': {'$ne':ObjectId(wifi_partner_id)},'number_tax': data}).count()
    else:
        return DATABASE.wifi_partners.find({'merchant_id': merchant_id, '_id': {'$ne':ObjectId(wifi_partner_id)},'contact_phone': data}).count()

def total_wifi_partners(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.wifi_partners.find({'merchant_id': merchant_id}).count()

def find_item_wf_partners(merchant_id, data, type_data):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    if type_data == "phone":
        return DATABASE.wifi_partners.find_one({'merchant_id': merchant_id, 'phone': data})
    elif type_data == "number_tax":
        return DATABASE.wifi_partners.find_one({'merchant_id': merchant_id, 'number_tax': data})
    else:
        return DATABASE.wifi_partners.find_one({'merchant_id': merchant_id, 'contact_phone': data})


def list_item_wf(merchant_id, page, page_size):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    results = []
    wifi_partners = DATABASE.wifi_partners.find({'merchant_id': merchant_id}).sort('when', -1). \
        skip(page_size * (page - 1)).limit(page_size)
    for wifi_partner in wifi_partners:
        results.append(wifi_partner)
    return results


def remove_wifi_partners(wifi_partner_id):
    if not isinstance(wifi_partner_id, ObjectId):
        wifi_partner_id = ObjectId(wifi_partner_id)
    result = True
    try:
        DATABASE.wifi_partners.remove({'_id': wifi_partner_id})
    except:
        result = False
    return result

def total_ads_banner_log(shop_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    total = DATABASE.ads_banner_visit.find({'shop_id': shop_id}).count()
    return total

def total_ads_banner_banner(shop_id, banner_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    total = DATABASE.ads_banner_visit.find({'shop_id': shop_id, 'interactive_banner_id': banner_id}).count()
    return total

def list_ads_banner_log(shop_id, page):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    logs = DATABASE.ads_banner_visit.find({'shop_id': shop_id}).sort('timestamp', -1).skip(settings.ITEMS_PER_PAGE * (page - 1)) \
                    .limit(settings.ITEMS_PER_PAGE)    
    return logs