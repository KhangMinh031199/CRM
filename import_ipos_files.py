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


def read_customers_sample(merchant_id, shop_id, tags_array, file_name, is_employee):
	url = 'http://static.nextify.vn/static/uploads/%s' % file_name
	path_file = str(os.getcwd()) + '/static/minio_files/%s' % (file_name)
	r = requests.get(url, allow_redirects=True)
	open(path_file, 'wb').write(r.content)
	records = xlrd.open_workbook(path_file)
	sheet = records.sheet_by_index(0)
	for rec in range(1,sheet.nrows):
		user = {}
		phone = sheet.row(rec)[4]
		if phone:
			phone = str(phone).encode('utf-8')
			if len(str(phone)) > 0:
				phone = phone.split('.')[0]
				phone = phone.lstrip('0')
				phone = phone.replace('+84', '0')
				x = phone.split(':')[1].split("'")
				phone = x[1 if len(x)>1 else 0]
				if phone.startswith('0') == False:
					phone = '0' +  phone
			else:
				phone = ''
		else:
			phone = ''
		if api.get_phone_number(phone):
			user['phone'] = phone

		email = sheet.row(rec)[7]
		if email:
			email = str(email).encode('utf-8')
			if len(str(email)) > 0 and validate_email(email):
				user['email'] = str(email)
		if 'phone' in user and len(user['phone']) > 0 or 'email' in user and \
				len(user['email']) \
				> 0:
			name = sheet.row(rec)[1]
			if name:
				name =str(name).encode('utf-8').strip()
				user['name'] = name

			dob = sheet.row(rec)[3]
			if dob:
				dob = str(dob).encode('utf-8')
				if len(str(dob)) > 0:
					bod = str(dob).split('/')
					print bod
					if len(bod) == 3:
						b_day = str(bod[0])
						b_month = str(bod[1])
						birth = ''
						if len(str(b_day)) > 0 and len(str(b_month)) > 0 and \
								str(b_day).isdigit() \
								and \
								str(b_month).isdigit():
							birth = '{}-{}'.format(str(b_month), str(b_day))
							_birthday = dateparser.parse(birth)
							if _birthday:
								birth = '{}-{}'.format(str(b_month).lstrip("0"),
													   str(b_day).lstrip("0"))
						user['birth'] = birth
						b_year = str(bod[2])
						user['year_birthday'] = str(b_year)
			if len(user) > 0:
				email = user.get('email', '')
				name = user.get('name', '')
				gender = user.get('gender', '')
				phone = user.get('phone', '')
				birthday = user.get('birth', '')
				note = user.get('note', '')
				address = user.get('address', '')
				facebook = user.get('facebook', '')
				year_birthday =  user.get('year_birthday', '')
				user_id = None
				print(user)

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

# merchant_id = '5a616f383fd79c2db9147c6a'
# shop_id = '5b6c08069f573c166cbe9eb0'
# tags_array = []
# file_path = 'static/sample/ipos_sample.xls'
# read_customers_sample(merchant_id, shop_id, tags_array, file_path)