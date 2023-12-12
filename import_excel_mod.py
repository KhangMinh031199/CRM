#! coding: utf-8
import time
import os
import requests
import pyexcel as p
from validate_email import validate_email
import api
import dateparser
import handle_customers
import save_customers
import settings
import pos
from datetime import datetime


# merchant_id = '5a616f383fd79c2db9147c6a'
# shop_id = '5b6c08069f573c166cbe9eb0'
# tags_array = []
# file_path = 'static/sample/customers_sample_crmx_test.xlsx'

def read_customers_sample(merchant_id, shop_id, tags_array, file_name, is_employee):
    try:
        url = 'http://static.nextify.vn/static/uploads/%s' % file_name
        path_file = str(os.getcwd()) + '/static/minio_files/%s' % (file_name)
        r = requests.get(url, allow_redirects=True)
        open(path_file, 'wb').write(r.content)
        records = p.iget_records(file_name=path_file)

        for rec in records:
            user = {}
            phone = rec['Phone']
            if len(str(phone)) > 0:
                phone = str(phone).replace('+84', '0')
                phone = str(phone).lstrip('0')
                phone = '0' + str(phone)
                if len(str(phone)) > 0 and str(phone).isdigit() and \
                        api.get_phone_number(str(phone)):
                    user['phone'] = str(phone)
            email = rec['Email']
            if len(str(email)) > 0 and validate_email(str(email)):
                user['email'] = str(email)
            if 'phone' in user and len(user['phone']) > 0 or 'email' in user and \
                    len(user['email']) \
                    > 0:
                first_name = rec.get('Ho', '')
                if not first_name:
                    first_name = ''
                middle_name = rec.get('Dem', '')
                if not middle_name or str(middle_name) == 'None':
                    middle_name = ''
                last_name = rec.get('Ten', '')
                if not last_name or str(last_name) == 'None':
                    last_name = ''
                first_name = first_name.encode('utf-8')
                middle_name = middle_name.encode('utf-8')
                last_name = last_name.encode('utf-8')
                name = str(first_name) + ' ' + str(middle_name) + ' ' + str(last_name)
                name = name.strip()
                user['name'] = str(name)

                b_day = rec.get('Ngaysinh', '')
                if not b_day or str(b_day) == 'None':
                    b_day = ''
                b_month = rec.get('Thangsinh', '')
                if not b_month or str(b_month) == 'None':
                    b_month = ''
                birth = ''
                if len(str(b_day)) > 0 and len(str(b_month)) > 0 and \
                        str(b_day).isdigit() \
                        and \
                        str(b_month).isdigit():
                    birth = '{}-{}'.format(str(b_month), str(b_day))
                    format = "%m-%d"
                    try:
                        datetime.strptime(birth, format)
                        birth = '{}-{}'.format(str(b_month).lstrip("0"),
                                               str(b_day).lstrip("0"))
                    except:
                        birth = ''
                user['birth'] = birth
                b_year = rec.get('Namsinh', '')
                if not b_year or str(b_year) == 'None':
                    b_year = ''
                user['year_birthday'] = str(b_year)

                gender = rec.get('Gioitinh', '0')
                if not gender:
                    gender = '0'
                else:
                    gender = str(gender)
                user['gender'] = gender
                address = rec.get('Diachi', '')
                user['address'] = address
                facebook = rec.get('Facebook', '')
                user['facebook'] = facebook
                note = rec.get('Ghichu', '')
                user['note'] = note
            if len(user) > 0:
                email = user.get('email', '')
                name = user.get('name', '')
                gender = user.get('gender', '')
                phone = user.get('phone', '')
                birthday = user.get('birth', '')
                note = user.get('note', '')
                address = user.get('address', '')
                facebook = user.get('facebook', '')
                year_birthday = user.get('year_birthday', '')
                user_id = None

                if phone and len(phone) > 0 and str(phone) != 'None':
                    phone = str(phone).lower()
                    phone = phone.replace('+84', '0')
                    phone = api.get_phone_number(phone)
                    if phone:
                        user_by_phone = handle_customers.get_user_merchant_by_phone(merchant_id, phone)
                        if user_by_phone:
                            user_id = user_by_phone.get('user_id')
                elif email and len(email) > 0 and str(email) != 'None':
                    email = email.lower()
                    user_by_email = handle_customers.get_user_merchant_by_email(merchant_id, email)
                    if user_by_email:
                        user_id = user_by_email.get('user_id')

                if user_id:
                    user = api.get_user_info(user_id=user_id)
                    if user:
                        api.update_user_item(
                            user_id,
                            name=name,
                            phone=phone,
                            gender=gender,
                            birthday=birthday,
                            email=email,
                            year_birthday=year_birthday,
                            note=note,
                            address=address,
                            is_employee=is_employee,
                            facebook=facebook)
                    else:
                        api.register_with_id(
                            id_user=user_id,
                            name=name,
                            phone=phone,
                            gender=gender,
                            birthday=birthday,
                            email=email,
                            year_birthday=year_birthday,
                            note=note,
                            address=address,
                            is_employee=is_employee,
                            facebook=facebook
                        )
                else:
                    user_id = api.register(
                        name=name,
                        phone=phone,
                        gender=gender,
                        birthday=birthday,
                        email=email,
                        year_birthday=year_birthday,
                        note=note,
                        address=address,
                        is_employee=is_employee,
                        facebook=facebook
                    )
                visit_id = api.save_visit_log(user_id, shop_id)
                api.create_user_tags(merchant_id, shop_id, user_id, tags_array)
                if visit_id:
                    save_customers.handle_customer_update(visit_id)
                    pos.send_data_by_visit_id(visit_id)
                else:
                    save_customers.update_customers(merchant_id, shop_id, user_id, time.time())
        p.free_resources()
    except Exception as e:
        pass

# read_customers_sample(merchant_id, shop_id, tags_array, path_file, is_employee)
