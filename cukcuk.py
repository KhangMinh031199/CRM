#! coding: utf-8
from datetime import datetime
from collections import OrderedDict
import requests
import hmac
import hashlib
import json

URL_GRAPH_CUCKCUK = 'https://graphapi.cukcuk.vn/'


def login_token(cukcuk_domain, app_id, secret_key):
    URL = URL_GRAPH_CUCKCUK + 'api/Account/login'
    login_time = datetime.utcnow().isoformat() + 'Z'
    login_info = {'AppID':app_id,
                  'Domain':cukcuk_domain,
                  'LoginTime':login_time
                  }
    json_login = json.dumps(login_info, sort_keys=True, separators=(',',':'))
    signature = hmac.new(secret_key, json_login,  hashlib.sha256).hexdigest()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'AppID': app_id,
            'Domain': cukcuk_domain,
            'LoginTime': login_time,
            'SignatureInfo': signature
            }

    json_data = json.dumps(data)
    r = requests.post(URL, data=json.dumps(data), headers=headers)

    result = r.json()
    data = result.get('Data')
    if data:
        access_token = data.get('AccessToken')
        print access_token
        return access_token
    return ''

def get_all_branch(token, CompanyCode):
    URL = URL_GRAPH_CUCKCUK + 'api/v1/branchs/all'
    headers = {'Content-type': 'application/json', 
                'Authorization': 'Bearer ' + token,
                'CompanyCode' : CompanyCode
                }
    r = requests.get(URL, headers=headers)
    result = r.json()
    print result

def customer_to_cukcuk(token, CompanyCode):
    URL = URL_GRAPH_CUCKCUK + 'api/v1/customer/'
    headers = {'Content-type': 'application/json', 
                'Authorization': 'Bearer ' + token,
                'CompanyCode' : CompanyCode
                }
    data = {
            "Code": "KH000010",
            "Name": "Nguyễn Văn A",
            "Tel": "03423546412",
            "Birthday": "1998-11-25T00:00:00",
            "Address": "Trần Quốc Vượng, Dịch Vọng Hậu, Cầu Giấy, Hà Nội",
            "Description": "",
            "Inactive": False
        }
    r = requests.post(url=URL, data=data, headers=headers)
    print r
    result = r.json()
    print result


def get_customer_from_cukcuk(token, CompanyCode):
    URL = URL_GRAPH_CUCKCUK + 'api/v1/customers/paging'
    headers = {'Content-type': 'application/json', 
                'Authorization': 'Bearer ' + token,
                'CompanyCode' : CompanyCode
                }
    data = {
        'Page': 1,
        'Limit': 10
    }
    r = requests.post(url=URL, data=json.dumps(data), headers=headers)
    result = r.json()
    data = result.get("Data")
    for dat in data:
        name = dat.get('Name')
        print "------"
        print name

cukcuk_domain = 'cafequancoc'
app_id = 'CUKCUKOpenPlatform'
secret_key = 'e29a421aab80c693dfec50decf1680a19612235b39dab0e02d759d03cf286c3b'
token = 'CimZkrFOw7jwqDRNLtZnG3vzmND0AAmV1gtC8vUZy4ZJnjqTSLY92ZkL_J_Efl9mLWJOeM83ELxaiCqXvNWPghzCrB4eyt1A5vgBGjx2DohTW5b8kSCntVsujNaj9stM7t1n-ZIctR3jOFFhn87Z7JbZ7cmrBcUuoEArrLPnItZeEm4nnzEPmvfqbk20QR4ZGPswHPNmeBkr7CQ_Cj4v8tG0NFAZn8pQMZdthkgZrm1860DsP4rUk5YGuvPB1Q1r_tIqSJN2O3Hn75u0zRLYBQ'
CompanyCode = 'cafequancoc'
# login_token(cukcuk_domain, app_id, secret_key)

# get_all_branch(token, CompanyCode)
# respone get all branch
# {
#     u'Code': 200, 
#     u'Data': [
#         {
#             u'Code': u'cafequancoc', 
#             u'Tel': u'097021269', 
#             u'Description': u'', 
#             u'Inactive': False, 
#             u'LicenseCode': u'cafequancoc_B001', 
#             u'Address': u'Ha Noi', 
#             u'IsBaseDepot': False, 
#             u'Id': u'994c6fe5-da83-441b-a0e8-57a6fed98fb2', 
#             u'Name': u'cafequancoc'
#         }
#     ], 
#     u'Success': True, 
#     u'Total': 0
# }
# customer_to_cukcuk(token, CompanyCode)
# get_customer_from_cukcuk(token, CompanyCode)