#! coding: utf-8
import os
import dateparser
import time
import pyexcel as p
import xlrd
import requests
from validate_email import validate_email
import api
import handle_customers
import save_customers
import report_graphql
import report_graphql_shop
import pos
from bson import ObjectId
import datetime


def read_customers_sample(merchant_id, shop_id, tags_array, file_name, is_employee):
    # merchant_id = "5a616f383fd79c2db9147c6a"
    # shop_id = ObjectId("597fe18647dd46ce3e554089")
    # tags_array = [ObjectId('5ebceaa0b573f61f9d90433c'), ObjectId('5ebe4b64b573f633bbd2799d')]
    # is_employee = "False"
    url = 'http://static.nextify.vn/static/uploads/%s' % file_name
    path_file = str(os.getcwd()) + '/static/minio_files/%s' % (file_name)
    r = requests.get(url, allow_redirects=True)
    open(path_file, 'wb').write(r.content)
    records = p.get_sheet(file_name=path_file, start_row=1)
    for rec in records:
        user = {}
        first_name = rec[1]
        last_name = rec[0]
        name = first_name + " " + last_name
        phone = str(rec[15])
        if phone:
            if api.get_phone_number(phone):
                user['phone'] = phone
        else:
            user['phone'] = ""
        company = rec[3]
        email = rec[2]
        address = rec[4] + " " + rec[6] + " " + rec[8] + " " + rec[10]
        gender_data = str(rec[25])
        gender = ""
        if gender_data == "Nam":
            gender = "1"
        elif gender_data == "Nữ":
            gender = "2"
        else:
            gender = "0"
        birthday = ""
        birthday_data = str(rec[23])
        if birthday_data and len(birthday_data) > 0:
            birthday = datetime.datetime.strptime(birthday_data, "%Y-%m-%d").strftime("%m-%d")
        print birthday, type(birthday)
        if email:
            email = str(email).encode('utf-8')
            if len(str(email)) > 0 and validate_email(email):
                user['email'] = str(email)
        user_id = None
        if phone and len(phone) > 0 and str(phone) != 'None':
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
                    address=address,
                    company=company,
                    is_employee=is_employee
                    )
                    
            else:
                api.register_with_id(
                    id_user=user_id,
                    name=name,
                    phone=phone,
                    gender=gender,
                    birthday=birthday,
                    email=email,
                    address=address,
                    company=company,
                    is_employee=is_employee
                )
        else:
            user_id = api.register(
                name=name,
                phone=phone,
                gender=gender,
                birthday=birthday,
                email=email,
                address=address,
                company=company,
                is_employee=is_employee
            )
        api.create_user_tags(merchant_id, shop_id, user_id, tags_array)
        visit_id = api.save_visit_log(user_id, shop_id)
        if visit_id:
            save_customers.handle_customer_update(visit_id)
            report_graphql.update_report_graphql(visit_id)
            report_graphql_shop.update_report_graphql_shop(visit_id)
            pos.send_data_by_visit_id(visit_id)
        else:
            save_customers.update_customers(merchant_id, shop_id, user_id, time.time())
    p.free_resources() 

# read_customers_sample()