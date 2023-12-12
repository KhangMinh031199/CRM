#! coding: utf-8
import sys
import time
from bson.objectid import ObjectId
from base64 import b64encode, b64decode
import requests
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from uuid import uuid4
import json
from hashlib import md5
import time
import api
import send_activity
import uuid
import settings

DATABASE = api.DATABASE


def send_sms_bluesea(merchant_id,
                     user_sms,
                     pass_sms,
                     brand_name,
                     phone_number,
                     message,
                     activity_id=None,
                     message_type=None,
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
    print(phone_number)
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
    session = requests.Session()
    session.auth = HTTPBasicAuth(User_Name, Password)
    client = Client(
        BLUESEA, transport=Transport(session=session))
    result = client.service.sendMT(User_ID, Message, Service_ID,
                                   Command_Code, Message_Type,
                                   Request_ID, Total_Message,
                                   Message_Index, IsMore,
                                   Content_Type)

    if result == 0:
        return True
    else:
        return False


def send_sms_vht(merchant_id, VHT_USER_API, VHT_PASS_API, VHT_BRANDNAME, phone, message, activity_id=None,
                 camp_id=None):
    VHT_SERVICE_DOMAIN = "http://sms3.vht.com.vn"
    URL_SEND_SMS = VHT_SERVICE_DOMAIN + "/ccsms/Sms/SMSService.svc/ccsms/json"
    data = {"submission":
                {"api_secret": VHT_PASS_API, "api_key": VHT_USER_API,
                 "sms": [{"text": message, "brandname": VHT_BRANDNAME, "id": str(phone), "to": phone}]}}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = requests.post(URL_SEND_SMS, json=data, headers=headers)
    if result and result.status_code == 200:
        return True
    else:
        return False


def send_sms_vhat(merchant_id, VHAT_API_KEY, VHAT_SECRET_KEY, VHAT_SMS_TYPE, VHAT_BRANDNAME,
                  phone, message, activity_id=None, camp_id=None):
    VHAT_SERVICE_DOMAIN = "http://rest.esms.vn/"
    URL_SEND_SMS = VHAT_SERVICE_DOMAIN + "MainService.svc/json/SendMultipleMessage_V4_post_json/"
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
        return True
    else:
        return False


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
    headers = {
        'Content-type': 'application/json',
        'Accept': 'text/plain'
    }
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
                         activity_id=None,
                         camp_id=None):
    # Không gửi SMS nội dung giống nhau đến 1 user trong 1 ngày
    expire = 86400
    url_send = ''
    access_token = ''
    phone = phone.lstrip('0')
    phone = '84' + phone
    message_not_base_64 = message
    message = (b64encode(message.encode("utf-8"))).decode("utf-8") 
    url_send = 'http://service.sms.fpt.net/api/push-brandname-otp'
    token = get_access_fpt_gateway(client_id, client_secret,
                                   scope)
    access_token = token.get('access_token')
    if access_token and len(access_token) > 0 and len(
            url_send) > 0:
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
        if result and result.status_code == 200:
            return True
            # if result == 0:
            #
            #     return True
            # else:
            #
            #     return False
        else:
            return False


def send_sms_viettel(merchant_id, user_sms, pass_sms, brand_name, phone_number, message, activity_id=None,
                     camp_id=None):
    phone_number = phone_number.lstrip('0')
    phone_number = '84' + phone_number
    URL = 'http://ams.tinnhanthuonghieu.vn:8009/bulkapi?wsdl'
    client = Client(URL)
    request_id = 1
    merchant = api.get_merchant(merchant_id)
    USER_API = merchant.get('user_sms')
    PASS_API = merchant.get('pass_sms')
    BRANDNAME = merchant.get('brand_name')
    CP_CODE = merchant.get('cp_code')

    result = client.service.wsCpMt(USER_API, PASS_API, CP_CODE, request_id,
                                   phone_number, phone_number, BRANDNAME,
                                   'bulksms', message, 0)
    
    if 'result' in result:
        _result = result.get("result")
        if '1' in str(_result):
            return True
        else:
            return False
    else:
        return False


def send_sms_mobi(merchant_id, user_sms, pass_sms, brand_name, phone_number, message, activity_id=None,
                     camp_id=None):
    phone = api.get_phone_number(phone_number)
    URL_LOGIN = "http://smsbrandname.mobifone.vn/smsg/login.jsp?userName={}&password={}&bindMode=T".format(user_sms, pass_sms)
    response_login = requests.get(url=URL_LOGIN)
    result_login = json.loads(response_login.text)
    status_login = result_login.get('status')
    if status_login == "200":
      sid = result_login.get('sid')
      URL = "http://smsbrandname.mobifone.vn/smsg/send_2.jsp?enCoding=ALPHA_UCS2&sid={}&sender={}&recipient={}&content={}".format(sid, brand_name, phone, message)
      response = requests.get(url=URL)
      result = json.loads(response.text)
      status = result_login.get('status')
      if status == "200":
        return True
      else:
        return False
    else:
      return False

def send_sms_vietguy(merchant_id, user_sms, pass_sms, brand_name, phone_number, message, activity_id=None,
                     camp_id=None):
    phone_number = phone_number.lstrip('0')
    phone_number = '84' + phone_number
    url_vietguy = settings.URL_VIETGUY
    bid = str(uuid.uuid4())
    URL =   url_vietguy + '?u={}&pwd={}&from={}&phone={}&sms={}&bid=bid&type=8&json=1'.format(user_sms, pass_sms, brand_name, phone_number, message)             
    r = requests.get(url=URL)
    results =  r.text
    if 'Gui thanh cong' in results:
        return True
    else:
        return False

def send_sms_vinaphone(merchant_id, phone_number, message, activity_id=None, camp_id=None):
    merchant = api.get_merchant(merchant_id)
    info_brand_name = merchant.get('brand_name_vina')
    LABELID = info_brand_name.get('vina_label_id')
    CONTRACTID = info_brand_name.get('vina_contract_id')
    TEMPLATEID = message
    AGENTID = info_brand_name.get('vina_agent_id')
    APIUSER = info_brand_name.get('vina_api_user')
    APIPASS = info_brand_name.get('vina_api_pass')
    APIURL = info_brand_name.get('vina_api_url')
    USERNAME = info_brand_name.get('vina_user_name')
    phone_number = phone_number.lstrip('0')
    phone_number = '84' + phone_number
    url = APIURL
    headers = {
        'Content-Type' : 'application/json;charset=UTF-8'
    }
    data = {
            "RQST": {
                "name": "send_sms_list",
                "REQID": str(uuid.uuid4()),
                "LABELID": LABELID,
                "CONTRACTTYPEID": "1",
                "CONTRACTID": CONTRACTID,
                "TEMPLATEID": TEMPLATEID,
                "PARAMS": [],
                "SCHEDULETIME": "",
                "MOBILELIST": phone_number,
                "ISTELCOSUB": "0",
                "AGENTID": AGENTID,
                "APIUSER": APIUSER,
                "APIPASS": APIPASS,
                "USERNAME": USERNAME,
                "DATACODING": "0"
                }
            }
    result = requests.post(url=url, headers=headers, data=json.dumps(data))
    if result and "\"ERROR\":\"0\"" in result.text:
      return True
    else:
      return False


def get_sms_data_camp(merchant_id, camp_id, shop_id):
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    customers_sources = camp.get('customers_sources')
    list_cus = []
    if customers_sources == "on":
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       is_sms=True)

    else:
        from_date = camp.get('visit_from_date')
        to_date = camp.get('visit_to_date')
        min_visit = camp.get('min_visit')
        max_visit = camp.get('max_visit')
        lost_day = camp.get('lost_day')
        bday_from_date = camp.get('b_day_from_date')
        bday_to_date = camp.get('b_day_to_date')
        gender = camp.get('gender')
        filter_tags = camp.get('tags')
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       from_date=from_date,
                                       is_sms=True,
                                       to_date=to_date,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       lost_day=lost_day,
                                       gender=gender,
                                       bday_from_date=bday_from_date,
                                       bday_to_date=bday_to_date,
                                       tags_array=filter_tags)
    if len(list_cus) > 0:
        for cus in list_cus:
            user = cus.get('user')
            if user:
                phone = user.get('phone')
                name = user.get('name', '')
                user_id = user.get('_id')
                if name and len(name) > 0 and str(name) == 'None':
                    name = ''
                if phone and len(phone) > 0 and str(phone) != 'None':
                    if not isinstance(camp_id, ObjectId):
                        camp_id = ObjectId(camp_id)
                    if not isinstance(shop_id, ObjectId):
                        shop_id = ObjectId(shop_id)
                    if not isinstance(user_id, ObjectId):
                        user_id = ObjectId(user_id)
                    check_log_email_camp = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                               'shop_id': shop_id,
                                                                               'phone': phone})
                    if not check_log_email_camp:
                        api.DATABASE.campaign_log.insert({
                            'camp_id': camp_id,
                            'shop_id': shop_id,
                            'phone': phone,
                            'name': name,
                            'user_id': user_id,
                            'status': 0
                        })
                    else:
                        api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                          'shop_id': shop_id,
                                                          'phone': phone},
                                                         {'$set': {'name': name}})


def send_sms_campaign(merchant_id, camp_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    merchant = api.get_merchant(merchant_id)
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    if merchant and camp:
        check_config = False
        message = camp.get('message')
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
          if message and len(message) > 0 and LABELID and len(LABELID) > 0\
            and USERNAME and len(USERNAME) > 0 and APIUSER and len(APIUSER) > 0\
            and APIPASS and len(APIPASS) > 0 and AGENTID and len(AGENTID) > 0\
            and CONTRACTID and len(CONTRACTID) > 0 and APIURL and len(APIURL) > 0:
            check_config = True
        else:
            if message and len(message) > 0 and sms_provider and len(sms_provider) > 0 and user_sms \
                    and len(user_sms) > 0 and pass_sms and len(pass_sms) > 0 and brand_name and len(brand_name) > 0:
                check_config = True

        if check_config:
            message = api.remove_accents(message)

            sms_logs = api.DATABASE.campaign_log.find({
                'camp_id': camp_id,
                'shop_id': shop_id,
                'status': 0
            })
            for sms_log in sms_logs:
                phone_number = sms_log.get('phone')
                name = sms_log.get('name')
                user_id = sms_log.get('user_id')

                if phone_number and len(phone_number) > 0 and str(phone_number) != 'None':
                    check_is_log = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                               'shop_id': shop_id,
                                                                               'phone': phone_number})
                    status = check_is_log.get('status')
                    if status == 0:
                        message = message.replace('{{ name }}', name)
                        result = True
                        if sms_provider.upper() == 'BLUESEA':
                            result = send_sms_bluesea(merchant_id,
                                                      user_sms,
                                                      pass_sms,
                                                      brand_name,
                                                      phone_number,
                                                      message)

                        elif sms_provider.upper() == 'VHT':
                            result = send_sms_vht(merchant_id, user_sms, pass_sms, brand_name, phone_number,
                                                  message,
                                                  activity_id=None, camp_id=None)
                        elif sms_provider.upper() == 'VHAT':
                            VHAT_API_KEY = merchant.get('api_key_vhat')
                            VHAT_SECRET_KEY = merchant.get('secret_key_vhat')
                            VHAT_SMS_TYPE = merchant.get('sms_type')
                            if VHAT_API_KEY and len(VHAT_API_KEY) > 0 and VHAT_SECRET_KEY and len(VHAT_SECRET_KEY) > 0:
                                result = send_sms_vhat(merchant_id, VHAT_API_KEY, VHAT_SECRET_KEY,
                                                       VHAT_SMS_TYPE, brand_name,
                                                       phone_number, message, activity_id=None, camp_id=None)
                            else:
                                result = False
                        elif sms_provider.upper() == 'VIETTEL':
                            result = send_sms_viettel(merchant_id, user_sms, pass_sms, brand_name, phone_number,
                                                      message, activity_id=None, camp_id=None)
                        elif sms_provider.upper() == 'MOBIFONE':
                            result = send_sms_mobi(merchant_id, user_sms, pass_sms, brand_name, phone_number,
                                                      message, activity_id=None, camp_id=None)
                        elif sms_provider.upper() == 'VIETGUY':
                            result = send_sms_vietguy(merchant_id, user_sms, pass_sms, brand_name, phone_number,
                                                      message, activity_id=None, camp_id=None)
                        elif sms_provider.upper() == 'FPT':
                            result = send_sms_fpt_gateway(merchant_id,
                                                          user_sms,
                                                          pass_sms,
                                                          phone_number,
                                                          brand_name,
                                                          'send_brandname_otp',
                                                          message,
                                                          activity_id=None,
                                                          camp_id=None)
                        elif sms_provider.upper() == 'VINAPHONE':
                          result = send_sms_vinaphone(merchant_id, phone_number, message, activity_id=None, camp_id=None)
                        else:
                            result = False

                        if result:
                            if not isinstance(shop_id, ObjectId):
                                camp_id = ObjectId(camp_id)
                            if not isinstance(shop_id, ObjectId):
                                shop_id = ObjectId(shop_id)
                            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                              'shop_id': shop_id,
                                                              'phone': phone_number},
                                                             {'$set': {'status': 1,
                                                                       'message': message,
                                                                       'update_at': time.time()}}
                                                             )
                            send_activity.insert_send_activity(merchant_id, shop_id, user_id, 'sms', message,
                                                               'campaign', camp_id)
                        else:
                            if not isinstance(shop_id, ObjectId):
                                camp_id = ObjectId(camp_id)
                            if not isinstance(shop_id, ObjectId):
                                shop_id = ObjectId(shop_id)
                            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                              'shop_id': shop_id,
                                                              'phone': phone_number},
                                                             {'$set': {'status': 2, 'message': message,
                                                                       'update_at': time.time()}})

    api.update_shop_camp_status(shop_id, camp_id, 2)


def get_zalo_oa_data_camp(merchant_id, camp_id, shop_id):
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    customers_sources = camp.get('customers_sources')
    list_cus = []
    if customers_sources == "on":
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       is_zalo=True,
                                       active_zns="off")

    else:
        from_date = camp.get('visit_from_date')
        to_date = camp.get('visit_to_date')
        min_visit = camp.get('min_visit')
        max_visit = camp.get('max_visit')
        lost_day = camp.get('lost_day')
        bday_from_date = camp.get('b_day_from_date')
        bday_to_date = camp.get('b_day_to_date')
        gender = camp.get('gender')
        filter_tags = camp.get('tags')
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       from_date=from_date,
                                       is_zalo=True,
                                       to_date=to_date,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       lost_day=lost_day,
                                       gender=gender,
                                       bday_from_date=bday_from_date,
                                       bday_to_date=bday_to_date,
                                       tags_array=filter_tags,
                                       active_zns="off")
    if len(list_cus) > 0:
        for cus in list_cus:
            user = cus.get('user')
            if user:
                phone = user.get('phone')
                name = user.get('name', '')
                user_id = user.get('_id')
                user_id_zalo = user.get('user_id_zalo')
                if name and len(name) > 0 and str(name) == 'None':
                    name = ''
                if user_id_zalo and len(str(user_id_zalo)) > 0 and phone and len(phone) > 0 and str(phone) != 'None':
                    if not isinstance(camp_id, ObjectId):
                        camp_id = ObjectId(camp_id)
                    if not isinstance(shop_id, ObjectId):
                        shop_id = ObjectId(shop_id)
                    if not isinstance(user_id, ObjectId):
                        user_id = ObjectId(user_id)
                    check_log_zalo_camp = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                                 'shop_id': shop_id,
                                                                                 'phone': phone})
                    if not check_log_zalo_camp:
                        api.DATABASE.campaign_log.insert({
                            'camp_id': camp_id,
                            'shop_id': shop_id,
                            'phone': phone,
                            'name': name,
                            'user_id': user_id,
                            'status': 0,
                            'user_id_zalo': user_id_zalo
                        })
                    else:
                        api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                          'shop_id': shop_id,
                                                          'phone': phone,
                                                          'user_id_zalo': user_id_zalo},
                                                         {'$set': {'name': name}})

def send_zalo_oa_campaign(merchant_id, camp_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shop_select = api.get_shop_info(shop_id=shop_id)
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    if shop_select and camp:
        message = camp.get('message')
        active_zns = camp.get('active_zns')
        access_token = shop_select.get('zalo_access_token')
        attachment_id = camp.get('attachment_id')
        if access_token and len(access_token) > 0 and active_zns == "off":
            message = api.remove_accents(message)
            sms_logs = api.DATABASE.campaign_log.find({
                'camp_id': camp_id,
                'shop_id': shop_id,
                'status': 0
            })
            for sms_log in sms_logs:
                phone_number = sms_log.get('phone')
                name = sms_log.get('name')
                user_id = sms_log.get('user_id')
                user_id_zalo = sms_log.get('user_id_zalo')
                if user_id_zalo and len(str(user_id_zalo)) > 0 and phone_number and len(phone_number) > 0 and str(phone_number) != 'None':
                    check_is_log = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                               'shop_id': shop_id,
                                                                               'phone': phone_number,
                                                                               'user_id_zalo': user_id_zalo})

                    status = check_is_log.get('status')
                    if status == 0 and user_id_zalo:
                        result = send_sms_zalo_oa(access_token, message, user_id_zalo, attachment_id)
                        if result:
                            if not isinstance(shop_id, ObjectId):
                                camp_id = ObjectId(camp_id)
                            if not isinstance(shop_id, ObjectId):
                                shop_id = ObjectId(shop_id)
                            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                              'shop_id': shop_id,
                                                              'phone': phone_number,
                                                              'user_id_zalo': user_id_zalo},
                                                             {'$set': {'status': 1,
                                                                       'message': message,
                                                                       'update_at': time.time()}}
                                                             )
                            send_activity.insert_send_activity(merchant_id, shop_id, user_id, 'sms', message,
                                                               'campaign', camp_id)
                        else:
                            if not isinstance(shop_id, ObjectId):
                                camp_id = ObjectId(camp_id)
                            if not isinstance(shop_id, ObjectId):
                                shop_id = ObjectId(shop_id)
                            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                              'shop_id': shop_id,
                                                              'phone': phone_number,
                                                              'user_id_zalo': user_id_zalo},
                                                             {'$set': {'status': 2, 'message': message,
                                                                       'update_at': time.time()}})
    api.update_shop_camp_status(shop_id, camp_id, 2)                    

def send_sms_zalo_oa(access_token, message, user_id_zalo, att_id):
  url = "https://openapi.zalo.me/v2.0/oa/message?access_token={}".format(access_token)
  headers = {'Content-type': 'application/json'}
  data = {}
  if att_id:
    data =  {
      "recipient": {
        "user_id": user_id_zalo
      },
      "message": {
        "text": message,
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "media",
                "elements": [{
                    "media_type": "image",
                    "attachment_id": att_id
                }]
              }
            }
          }
        } 
  else:
    data = {"recipient": {
                "user_id": user_id_zalo
              },
                "message": {
                    "text": message
                }
            }

  r = requests.post(
      url=url, data=json.dumps(data), headers=headers)
  result = json.loads(r.text)
  status = result.get('error')
  if str(status) == "0":
    return True
  else:
    return False


def get_zns_data_camp(merchant_id, camp_id, shop_id):
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    customers_sources = camp.get('customers_sources')
    list_cus = []
    if customers_sources == "on":
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       is_sms=True,
                                       active_zns="on")

    else:
        from_date = camp.get('visit_from_date')
        to_date = camp.get('visit_to_date')
        min_visit = camp.get('min_visit')
        max_visit = camp.get('max_visit')
        lost_day = camp.get('lost_day')
        bday_from_date = camp.get('b_day_from_date')
        bday_to_date = camp.get('b_day_to_date')
        gender = camp.get('gender')
        filter_tags = camp.get('tags')
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       from_date=from_date,
                                       is_sms=True,
                                       to_date=to_date,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       lost_day=lost_day,
                                       gender=gender,
                                       bday_from_date=bday_from_date,
                                       bday_to_date=bday_to_date,
                                       tags_array=filter_tags)
    if len(list_cus) > 0:
        for cus in list_cus:
            user = cus.get('user')
            if user:
                phone = user.get('phone')
                name = user.get('name', '')
                user_id = user.get('_id')
                if name and len(name) > 0 and str(name) == 'None':
                    name = ''
                if phone and len(phone) > 0 and str(phone) != 'None':
                    if not isinstance(camp_id, ObjectId):
                        camp_id = ObjectId(camp_id)
                    if not isinstance(shop_id, ObjectId):
                        shop_id = ObjectId(shop_id)
                    if not isinstance(user_id, ObjectId):
                        user_id = ObjectId(user_id)
                    check_log_email_camp = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                               'shop_id': shop_id,
                                                                               'phone': phone})
                    if not check_log_email_camp:
                        api.DATABASE.campaign_log.insert({
                            'camp_id': camp_id,
                            'shop_id': shop_id,
                            'phone': phone,
                            'name': name,
                            'user_id': user_id,
                            'status': 0
                        })
                    else:
                        api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                          'shop_id': shop_id,
                                                          'phone': phone},
                                                         {'$set': {'name': name}})


def send_zns_campaign(merchant_id, camp_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    merchant = api.get_merchant(merchant_id)
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    shop_select = api.get_shop_info(shop_id=shop_id)
    if shop_select and camp:
        temp_id = camp.get('temp_id')
        access_token = shop_select.get('zalo_access_token')
        if temp_id and len(temp_id) > 0 and access_token and len(access_token) > 0:
          sms_logs = api.DATABASE.campaign_log.find({
              'camp_id': camp_id,
              'shop_id': shop_id,
              'status': 0
          })
          for sms_log in sms_logs:
              phone_number = sms_log.get('phone')
              name = sms_log.get('name', 'bạn')
              user_id = sms_log.get('user_id')

              if phone_number and len(phone_number) > 0 and str(phone_number) != 'None':
                  check_is_log = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                             'shop_id': shop_id,
                                                                             'phone': phone_number})
                  status = check_is_log.get('status')
                  if status == 0:
                    result = send_zns(temp_id, access_token, name, phone_number)
                    if result:
                        if not isinstance(shop_id, ObjectId):
                            camp_id = ObjectId(camp_id)
                        if not isinstance(shop_id, ObjectId):
                            shop_id = ObjectId(shop_id)
                        api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                          'shop_id': shop_id,
                                                          'phone': phone_number},
                                                         {'$set': {'status': 1,
                                                                   'message': temp_id,
                                                                   'update_at': time.time()}}
                                                         )
                        send_activity.insert_send_activity(merchant_id, shop_id, user_id, 'sms', temp_id,
                                                           'campaign', camp_id)
                    else:
                        if not isinstance(shop_id, ObjectId):
                            camp_id = ObjectId(camp_id)
                        if not isinstance(shop_id, ObjectId):
                            shop_id = ObjectId(shop_id)
                        api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                          'shop_id': shop_id,
                                                          'phone': phone_number},
                                                         {'$set': {'status': 2, 'message': temp_id,
                                                                   'update_at': time.time()}})
    api.update_shop_camp_status(shop_id, camp_id, 2)


def send_zns(temp_id, access_token, name, phone_number):
  if str(phone_number).startswith('0'):
        pnumber = str(phone_number).lstrip('0')
  phone = "84" + pnumber
  url = 'https://business.openapi.zalo.me/message/template?access_token={}'.format(access_token)
  payload = {
  'phone': phone,
  'template_id': temp_id,
  'template_data': {
    'customer_name': name,
  },
  'tracking_id': str(uuid4())
}
  headers = { 
      'Content-type': 'application/json',
  }
  response = requests.post(url=url, data=json.dumps(payload), headers=headers)
  results = json.loads(response.text)
  codeResult = results.get('error')
  if str(codeResult) == "0":
    return True
  else:
    return False
  
