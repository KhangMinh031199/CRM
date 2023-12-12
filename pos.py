#! coding: utf-8
import requests
import json
import sys
import api
reload(sys)
sys.setdefaultencoding('utf-8')


def send_data_by_visit_id(visit_id):
    visit = api.get_visit_by_id(visit_id)
    if visit:
        user_id = visit.get('user_id')
        shop_id = visit.get('shop_id')
        shop = api.get_shop_info(shop_id=shop_id)

        if shop:
            pos_id = shop.get('pos_id')
            merchant_id = shop.get('merchant_id')
            check_app = api.check_app_synchronized_pos(merchant_id)

            if check_app and pos_id and str(check_app.get('name_app')) == 'loop':

                access_token = check_app.get('setting').get('api_key')
                user = api.get_user_info(user_id=user_id)
                name = user.get('name')
                email = user.get('email')
                phone_number = user.get('phone')
                birthday = user.get('birthday')
                gender = user.get('gender')
                note = user.get('note')
                address = user.get('address')

                add_member_loop(shop_id_loop=pos_id,
                                access_token=access_token,
                                address=address,
                                note=note,
                                gender=gender,
                                birthday=birthday,
                                name=name,
                                email=email,
                                phone_number=phone_number)
            elif check_app and pos_id and str(check_app.get('name_app')) == 'kiotviet' and str(check_app.get('setting').get('kind')) == 'Retailer':
                secret_id = check_app.get('setting').get('secret_id')
                client_id = check_app.get('setting').get('client_id')
                name_shop = check_app.get('setting').get('name_shop')
                user = api.get_user_info(user_id=user_id)
                name = user.get('name')
                email = user.get('email')
                phone_number = user.get('phone')
                birthday = user.get('birthday')
                gender = user.get('gender')
                note = user.get('note')
                address = user.get('address')
                add_customer_retailer_kiotviet(retailer=name_shop,
                                               client_id=client_id,
                                               client_secret=secret_id,
                                               kiotviet_id=pos_id,
                                               name=name,
                                               email=email,
                                               gender=gender,
                                               contactNumber=phone_number,
                                               birthDate=birthday,
                                               comment=note)
            elif check_app and pos_id and str(check_app.get('name_app')) == 'kiotviet' and str(check_app.get('setting').get('kind')) == 'Fnb':
                secret_id = check_app.get('setting').get('secret_id')
                client_id = check_app.get('setting').get('client_id')
                name_shop = check_app.get('setting').get('name_shop')
                user = api.get_user_info(user_id=user_id)
                # note = user.get('note')
                # address = user.get('address')
                data = {}
                data['contactNumber'] = user.get('phone')
                data['email'] = user.get('email')
                data['name'] = user.get('name')
                data['gender'] = user.get('gender')
                data['birthDate'] = user.get('birthday')
                add_customer_retailer_kiotviet(retailer=name_shop,
                                               client_id=client_id,
                                               client_secret=secret_id,
                                               data=data)


def access_token_retailer(client_id, client_secret):

    scope = 'PublicApi.Access'

    url_get_token = 'https://id.kiotviet.vn/connect/token'
    data = {
        "scopes": scope,
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    token = ''
    result = requests.post(
        url_get_token, data=data, headers=headers)
    if result and result.status_code == 200:
        return result


def access_token_fnb(client_id, client_secret):
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
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    result = requests.post(url_get_token, data=data, headers=headers)
    ACCESS_TOKEN = json.loads(result.text)
    token = str('Bearer ' + ACCESS_TOKEN['access_token'])
    return token


def add_customer_retailer_kiotviet(retailer, client_id, client_secret, kiotviet_id, name, email, gender, contactNumber, birthDate, comment):
    token = access_token_retailer(client_id, client_secret)
    ACCESS_TOKEN = json.loads(token.text)['access_token']
    url_add = 'https://public.kiotapi.com/customers'
    data = {
        "branchId": kiotviet_id,
        "name": name,
        "contactNumber": contactNumber,
        "email": email,
        "gender": gender,
        "birthDate": birthDate,
        "comment": comment
    }

    headers = {
    "Retailer": retailer,
    "Authorization": "Bearer " + str(ACCESS_TOKEN)
    }
    result = requests.post(
        url_add, data=data, headers=headers)
    print result.content
    if result and result.status_code == 200:
        return result


def add_customer_retailer_fnb(data = None,
                              retailer = None,
                              client_id = None,
                              client_secret = None):
    ''' Ham them moi customer vao kiotviet.
    Method: POST
    Args: Data{
        'name' : name
        'email' : email
        ...
    }
    Return: Status of the request.
    '''
    token = access_token_fnb(client_id, client_secret)
    url_service =  'https://publicfnb.kiotapi.com/customers'
    headers = {
        "Retailer" : retailer,
        "Authorization" : token}
    result = requests.post(url_service, headers=headers, data=data)
    return  result.text


def add_member_loop(shop_id_loop,
                    access_token,
                    address,
                    note,
                    gender,
                    birthday,
                    name,
                    email,
                    phone_number):
    data = {}
    if gender == '1':
        gender = True
    elif gender == '2':
        gender = False
    else:
        gender = True

    try:
        list_name = name.split(' ')
        if len(list_name) > 1:
            first_name = list_name[len(list_name) - 1]
            last_name = list_name[0]
        elif name != '':
            first_name = name
            last_name = 'None'
        else:
            first_name = 'None'
            last_name = 'None'
    except:
        first_name = 'None'
        last_name = 'None'

    data['Address'] = address
    data['Notes'] = note
    data['Gender'] = gender
    data['DateOfBirth'] = birthday
    data['FirstName'] = first_name
    data['LastName'] = last_name
    data['Email'] = email
    data['PhoneNumber'] = phone_number
    url = 'https://beta-api.loop.vn/v2/members/{}'.format(shop_id_loop)
    key = 'Bearer ' + str(access_token)
    headers = {'Authorization': key, 'Content-Type': 'application/json'}

    return requests.post(url=url, data=json.dumps(data), headers=headers).text


# shop_id_loop = 123456
# accees_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJMUElEIjoiNmZkZWVhY2YtNTc4Yi00NjA4LWJhYjItNmE0YzhkNzJlY2IyIiwiTFRZIjoiMCIsImlhdCI6IjE1Njk1ODQzODIiLCJuYmYiOiIxNTY5NTg0MzgyIiwiZXhwIjoiMTYwMTIwNjc4MiIsImF1ZCI6IlBla28uU2VjdXJpdHkiLCJpc3MiOiJQZWtvLlNlY3VyaXR5In0.9HA2tsgRsLq124x1mbGY1AegbCsA_V8OrGp6hAKl3iY'
# address = None
# note = None
# gender = None
# birthday = None
# name = None
# email = None
# phone_number = ''
#
# print add_member_loop(shop_id_loop=shop_id_loop, access_token=accees_token,
#            address=address, note=note, gender=gender, birthday=birthday, name=name, email=email, phone_number=phone_number)

# visit_id = '5dcd041d4e4dddf76a6a0afb'
# print send_data_by_visit_id(visit_id)