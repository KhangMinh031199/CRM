from elasticsearch import Elasticsearch
from datetime import datetime
from collections import OrderedDict
import requests
import settings
from pymongo import MongoClient
import settings
from collections import OrderedDict
from bson.objectid import ObjectId
import unidecode
es = Elasticsearch([settings.ELASTICSEARCH_SERVER],
                   http_auth=(settings.ELASTICSEARCH_USER,
                              settings.ELASTICSEARCH_PASSWORD),
                   scheme="http",
                   port=9200,
                   timeout=3000,
                   max_retries=10,
                   retry_on_timeout=True)

MONGODB = MongoClient(
    settings.MONGODB_HOST,
    settings.MONGODB_PORT,
    document_class=OrderedDict,
    maxPoolSize=200,
    serverSelectionTimeoutMS=90000)
DATABASE = MONGODB[settings.MONGODB_NAME]
DATABASE.authenticate(
    settings.MONGODB_USER,
    settings.MONGODB_PASSWORD,
    source=settings.MONGO_NAME_AUTHEN)

def search_mechant_by_text(regex):

    query_search = {
        '$or': [
            {
                "name": {
                    '$regex': regex,
                    '$options': 'i'
                }
            },
            {
                "phone": {
                    '$regex': regex,
                    '$options': 'i'
                }
            },
            {
                "email": {
                    '$regex': regex,
                    '$options': 'i'
                }
            },
        ]
    }

    recs = DATABASE.merchants.find(query_search).sort('when', -1)
    total = recs.count()
    return recs, total

def get_device_info(gateway_mac):
    gateway_mac = [gateway_mac, gateway_mac.upper(), gateway_mac.lower()]
    return DATABASE.devices.find_one({'gateway_mac': {"$in": gateway_mac}})

def get_shop_info(shop_id=None, gateway_mac=None, check_shop_id=None, device_type=None):
    if shop_id:
        if not isinstance(shop_id, ObjectId):
            shop_id = ObjectId(shop_id)
        return DATABASE.shop.find_one({'_id': shop_id})
    elif gateway_mac:
        if isinstance(gateway_mac, list):
            gateway_mac = gateway_mac[0]
        if device_type and device_type == "ruijie_gw":
            return DATABASE.shop.find_one({'gateway_mac': gateway_mac})
        else:
            gateway_mac = normalize(gateway_mac)
            return DATABASE.shop.find_one({'gateway_mac': gateway_mac})


def get_merchant_info(merchant_id=None):
    if merchant_id:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.merchants.find_one({'_id': merchant_id})

def get_merchant(merchant_id):
    try:
        if not isinstance(merchant_id, ObjectId):
            merchant_id = ObjectId(merchant_id)
        return DATABASE.merchants.find_one({'_id': merchant_id})
    except:
        return False

def get_user_info(user_id=None, client_mac=None, phone_number=None):
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

def remove_accents(s):
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    return unidecode.unidecode(s)

def search_location_by_text(regex):

    query_search = {
        '$or': [
            {
                "name": {
                    '$regex': regex,
                    '$options': 'i'
                }
            },
            {
                "phone": {
                    '$regex': regex,
                    '$options': 'i'
                }
            },
            {
                "email": {
                    '$regex': regex,
                    '$options': 'i'
                }
            },
            {
                "gateway_mac": {
                    '$regex': regex,
                    '$options': 'i'
                }
            },
        ]
    }

    recs = DATABASE.shop.find(query_search).sort('created_at', -1)
    total = recs.count()
    return recs, total


def index_elastic(index_name, index_id, data):
    res = es.index(index=index_name,
                   doc_type=index_name,
                   id=str(index_id),
                   body=data)
    es.indices.refresh(index=index_name)
    return res


def remove_elastic(index_name, index_id):
    res = es.delete(index=index_name, id=str(index_id))
    es.indices.refresh(index=index_name)
    return res


def get_elastic(index_name, index_id):
    try:
        res = es.get(index=index_name, id=str(index_id))
        return res
    except:
        return ''


def elas_find(index_name, doc_name, field_name, str_query):
    search_url = ':9200/%s/%s/_search?pretty' % (index_name, doc_name)
    search_url = 'http://' + settings.ELASTICSEARCH_SERVER + search_url
    body_query = {"query": {"match": {field_name: str_query}}}
    r = requests.post(search_url, json=body_query)
    if r.status_code == 200:
        try:
            r_json = r.json()
            hits = r_json.get('hits')
            if hits and len(hits) > 0:
                total = hits.get('total')
                value = total.get('value')
                if int(value) > 0:
                    shops = []
                    for hit in hits['hits']:
                        source = hit["_source"]
                        shop_id = source.get('id')
                        if index_name == 'shop':
                            shop = get_shop_info(shop_id=shop_id)
                            if shop:
                                shops.append(shop)
                        else:
                            merchant = get_merchant(shop_id)
                            if merchant:
                                shops.append(merchant)
                    return shops, int(value)
                else:
                    return [], 0
            else:
                return [], 0
        except:
            return [], 0
    else:
        return [], 0


def search_merchants(search_query):
    merchants, total = elas_find('merchant', 'merchant', 'name', search_query)
    return merchants, total


def search_merchants_by_email(search_query):
    merchants, total = elas_find('merchant', 'merchant', 'email', search_query)
    return merchants, total


def search_merchants_by_phone(search_query):
    merchants, total = elas_find('merchant', 'merchant', 'phone', search_query)
    return merchants, total


def search_locations(search_query):
    shops, total = elas_find('shop', 'shop', 'name', search_query)
    return shops, total


def search_locations_by_mac(search_query):
    shops, total = elas_find('shop', 'shop', 'gateway_mac', search_query)
    return shops, total


def search_locations_by_email(search_query):
    shops, total = elas_find('shop', 'shop', 'email', search_query)
    return shops, total


def search_locations_by_phone(search_query):
    shops, total = elas_find('shop', 'shop', 'phone', search_query)
    return shops, total


def search_locations_by_address(search_query):
    shops, total = elas_find('shop', 'shop', 'address', search_query)
    return shops, total


def search_device(search_query):
    shops = []
    search_query = "*" + search_query + "*"
    res = es.search(index="shop",
                    body={"query": {
                        "query_string": {
                            'query': search_query
                        }
                    }})
    total = res['hits']['total']['value']
    devices = []
    if int(total) > 0:
        for hit in res['hits']['hits']:
            source = hit["_source"]
            shop_id = source.get('id')
            shop = get_shop_info(shop_id=shop_id)
            search_query_ = search_query
            if shop:
                merchant_id = shop.get('merchant_id')
                merchant = get_merchant_info(merchant_id=merchant_id)
                search_query_ = search_query_.strip("*").split(' ')
                if len(search_query_) == 6:
                    search_query = ":".join(search_query_)
                    device = get_device_info(search_query)
                    if device:
                        shop_gwm = get_shop_info(
                            gateway_mac=search_query, )
                        device['shop_device'] = shop_gwm
                        devices.append(device)
                else:
                    shop_info = get_shop_info(shop.get('_id'))
                    gateway_macs = shop_info.get('gateway_mac')
                    if gateway_macs and len(gateway_macs) > 0:
                        for gateway_mac in gateway_macs:
                            device = get_device_info(
                                str(gateway_mac).lower())
                            if device:
                                device['shop_device'] = shop_info
                                devices.append(device)
    return devices, len(devices)


def search_user(search_query):
    users = []
    total = 0
    try:
        search_query = "*" + search_query + "*"
        res = es.search(
            index="users",
            body={"query": {
                "query_string": {
                    'query': search_query
                }
            }})
        total = res['hits']['total']['value']
        if int(total) > 0:
            for hit in res['hits']['hits']:
                source = hit["_source"]
                user_id = source.get('id')
                user = get_user_info(user_id=user_id)
                if user:
                    users.append(user)
    except:
        pass
    return users, total


def index_merchant_item(mer):
    info = {}
    info['id'] = str(mer.get('_id'))
    info['name'] = remove_accents(mer.get('name', ''))
    info['phone'] = mer.get('phone')
    info['email'] = mer.get('email')
    info['businessman'] = mer.get('businessman', '')
    info['businessman'] = mer.get('partner', '')
    check_merchant_index = get_elastic('merchant', info['id'])
    if check_merchant_index and len(check_merchant_index) > 0:
        remove_elastic('merchant', info['id'])
        index_elastic('merchant', info['id'], info)
    else:
        index_elastic('merchant', info['id'], info)


def index_shop_item(shop):
    info = {}
    info['id'] = str(shop.get('_id'))
    name = shop.get('name', '')
    if str(name.encode('utf-8')) == 'None':
        name = ''
    info['name'] = remove_accents(name.encode('utf-8'))
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
    info['address'] = remove_accents(address.encode('utf-8'))
    gateway_macs = shop.get('gateway_mac', [])
    info['gateway_mac'] = ''
    if len(gateway_macs) > 0:
        for mac in gateway_macs:
            if mac and str(mac) != 'None':
                mac = mac.replace(':', ' ')
                info['gateway_mac'] = info['gateway_mac'] + ' ' + str(mac)
    check_res = get_elastic('shop', info['id'])
    if check_res and len(check_res) > 0:
        remove_elastic('shop', info['id'])
        index_elastic('shop', info['id'], info)
    else:
        index_elastic('shop', info['id'], info)
