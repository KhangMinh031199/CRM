#! coding: utf-8
import time
import os
import pyexcel as p
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
	records = p.iget_records(file_name=path_file, start_row=1)
	for rec in records:
		user = {}
		name = rec.values()[1]
		phone = rec.values()[3]
		email = rec.values()[7]
		address = rec.values()[8]
		note = rec.values()[9]
		if len(str(phone)) > 0:
			phone = str(phone).replace('+84', '0')
			phone = str(phone).lstrip('0')
			phone = '0' + str(phone)
			if len(str(phone)) > 0 and str(phone).isdigit() and \
                    api.get_phone_number(str(phone)):
				user['phone'] = str(phone)
		if len(str(email)) > 0 and validate_email(email):
			user['email'] = email
		if 'phone' in user and len(user['phone']) > 0 or 'email' in user and \
                len(user['email'])  > 0:
				name =  u''.join(name).encode('utf-8').strip()
				name = name.strip()
				user['name'] = name
				address =  u''.join(address).encode('utf-8').strip()
				address = address.strip()
				user['address'] = address
				note =  u''.join(note).encode('utf-8').strip()
				note = note.strip()
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

