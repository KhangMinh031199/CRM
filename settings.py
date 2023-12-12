#! coding: utf-8

import os

SENTRY_DSN = 'https://91e4183832f74370a5ae642241c42cef:1eb87e474a054f308797be59b1feddc6@sentry.nextify.vn/3'

MONGODB_NAME = 'nextify'
MONGODB_HOST = os.getenv('MONGODB_HOST', '123.31.12.64')
# MONGODB_HOST = os.getenv('MONGODB_HOST', '125.212.225.71')
MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
MONGODB_USER = 'develop'
MONGODB_PASSWORD = 'g5i4dI8KzYmXs0K'
MONGO_NAME_AUTHEN = 'nextify'


# MONGODB_NAME = 'nextify'
# MONGODB_HOST = os.getenv('MONGODB_HOST', '127.0.0.1')
# MONGODB_PORT = int(os.getenv('MONGODB_PORT', 28017))
# MONGODB_USER = 'nextify'
# MONGODB_PASSWORD = 'nextify'
# MONGO_NAME_AUTHEN = 'admin'

# REDIS_HOST = os.getenv('REDIS_HOST', '171.244.57.184')
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = 'Mh1dzbxs3O'

CARBON_HOST = os.getenv('CARBON_HOST', '127.0.0.1')
CARBON_PORT = int(os.getenv('CARBON_PORT', 2003))

ITEMS_PER_PAGE = 20
ITEMS_PER_PAGE_CALL = 10
ITEMS_PER_PAGE_OMICALL = 5
#
NODOGSPLASH_URL = 'http://172.16.99.1/'

MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', '127.0.0.1')
MEMCACHED_PORT = int(os.getenv('MEMCACHED_PORT', 11211))

roles_lo = [
    {"value": "1", "title": "Manager"},
    {"value": "2", "title": "ຜູ້ເກັບເງິນ"},
    {"value": "3", "title": "Admin"},
    {"value": "4", "title": "Marketing"},
]

roles = [
    {"value": "1", "title": "Manager"},
    {"value": "2", "title": "Thu ngân"},
    {"value": "3", "title": "Admin"},
    {"value": "4", "title": "Marketing"},
]

EMAIL_SENDER = "info@nextify.vn"
EMAIL_SENDER_PASS = "Q7D&7o&eNSb#3tx"

FCM_URL = 'https://fcm.googleapis.com/fcm/send'
FCM_KEY = 'AIzaSyBVy-YAjT-txN1_iuUYBmly8B_CoQNzEiM'

BLACK_LIST_SHOP = [
    # '594d2c1e47dd464ae7495509',
    # '5951dd5247dd46cc6b3d4e03',
    # '59830c9247dd46329ea2e2b8',
    # '5951ddf747dd46cc6b3d4e07',
    # '5951dd7447dd46cc6c5a88fd',
    # '5951ddb847dd46cc6e1d4641',
]

HOURS_VISIT_RANGE = [
    {
        'name': 'range1',
        'min': '08:00',
        'max': '10:59',
        'min_vi': '01:00',
        'max_vi': '03:59'
    },
    {
        'name': 'range2',
        'min': '11:00',
        'max': '13:59',
        'min_vi': '04:00',
        'max_vi': '06:59'
    },
    {
        'name': 'range3',
        'min': '14:00',
        'max': '17:59',
        'min_vi': '07:00',
        'max_vi': '10:59'
    },
    {
        'name': 'range4',
        'min': '18:00',
        'max': '20:59',
        'min_vi': '11:00',
        'max_vi': '13:59'
    },
    {
        'name': 'range5',
        'min': '21:00',
        'max': '23:59',
        'min_vi': '14:00',
        'max_vi': '16:59'
    },
    {
        'name': 'range6',
        'min': '00:00',
        'max': '07:59',
        'min_vi': '17:00',
        'max_vi': '23:59'
    },
]

COUNT_VISIT_RANGE = [
    {
        'name': 'range1',
        'text': '1',
        'data': ['1','1']
    },
    {
        'name': 'range2',
        'text': '2',
        'data': ['2', '2']
    },
    {
        'name': 'range3',
        'text': '3-9',
        'data': ['3', '9']
    },
    {
        'name': 'range4',
        'text': '10+',
        'type': 'great',
        'data': ['10', '10']
    },

]

BOOKING_TABLE_SOURCE=[
    {'name': 'APP', 'id': 'app'},
    {'name': 'Website', 'id': 'web'},
    {'name': 'PassGo', 'id': 'pasgo'},
    {'name': 'Foody', 'id': 'foody'},
    {'name': 'Other', 'id': 'other'},
]

BOOKING_TABLE_STATUS=[
    {'name': 'Đang xử lý', 'id': '1'},
    {'name': 'Thành công', 'id': '2'},
    {'name': 'Đã huỷ', 'id': '3'}
]

PORTAL_SETTINGS_BUCKET = 'wifi-portal-settings'
EXPORT_FILE_BUCKET = 'kien-bucket'
#email

MAIL_SUBJECT = '[NEXTIFY]'

MAIL_FROM = 'Support'

# MYSQL_HOST = '127.0.0.1'
MYSQL_HOST = '171.244.57.184'
MYSQL_PORT = 3306
MYSQL_USER = 'radius'
MYSQL_PASSWORD = '@radiusnextify@'
MYSQL_DB = 'radius'

BITLY_API_USER = 'o_1kkmvh6so8'
BITLY_API_KEY = 'R_910a3fdb39384ed9bd83cdcea0d88967'
KAFKA_IP = '125.212.225.71'


ELASTICSEARCH_SERVER = '125.212.225.71'
ELASTICSEARCH_USER = 'elastic'
ELASTICSEARCH_PASSWORD = '@aicungbiet@'

SOCIAL_DETECT_API = 'http://127.0.0.1:5000/social_detect/'
SOCIAL_DETECT_API_USER = 'nextify'
SOCIAL_DETECT_API_PASS = '@detectionapi@2020'

NEXTIFY_FACEBOOK_APP_ID = '611214335939430'
NEXTIFY_FACEBOOK_APP_SECRET = 'ae4f0c5a72fd43da8ed2de7bcd8e9255'

FACBOOK_GRAPH_API = 'https://graph.facebook.com/v6.0'
GOOGLE_PROJECT_ID = 'app-nextify-1586838771570'
GOOGLE_API_URL = 'https://mybusiness.googleapis.com/v4/'
GOOGLE_OAUTH_ID = '1038097275819-leod4fnu1h1n5h09ilrcm5bjub5ajh33.apps.googleusercontent.com'

API_URL = "https://api.nextify.vn"

MAIL_REGISTER_ZALO_PAY = 'minhnvb@vng.com.vn'

MAIL_REGISTER_HARAVAN = ["apps@haravan.com", "tuan.tranminh@haravan.com"]

API_BIZFLY = "https://crm.bizfly.vn"

ZALO_ME = 'https://zalo.me/'

URL_VIETGUY = 'https://cloudsms.vietguys.biz:4438/api/index.php'

APP_ID_HARAVAN = '1a59a59bed0cd259e6b6e6ec2899acfa'
APP_SECRET_HARAVAN = '1dc3b75669a575d8457f62fe63c69523cad977302c9b0f2af326e9d2cc0f7a7e'
REDIRECT_URI_HARAVAN = "https://api.nextify.vn/redirect_haravan"

DAY_IN_WEEEK = {
    '1': 'Chủ nhật',
    '2': 'Thứ hai',
    '3': 'Thứ ba',
    '4': 'Thứ tư',
    '5': 'Thứ năm',
    '6': 'Thứ sáu',
    '7': 'Thứ bảy'
}

PATH_FILE = os.path.dirname(os.path.abspath(__file__))
cms_consumer = "cms_consumer"

lost_consumer = "lost_customers"
birthday_consumer = "birthday_message"
thankyou_consumer = "thankyou_visit"
report_consumer = "report_everyweek"

HOST_URL_STARBUCKS = 'http://portal.nextify.vn/'

VIETTEL_USER_SMS = '7b678623828fEad6d8A6b5c9681ba5b84fbcf325'
VIETTEL_PASS_SMS = '1Eff24b202C8a3483f51d045a21d3af467fe0e1abA9b28c3E00a5e465B7bd64478d73929'
VIETTEL_BRAND_NAME ='VIETTEL'
VIETTEL_MESSAGE = 'Mật khẩu mới của bạn là: '

GHDC_domain_test = "http://125.212.226.74:8888/mmsapi/"
GHDC_domain = 'https://mms.viettel.vn/mmsapi/'