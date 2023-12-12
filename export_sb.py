from pymongo import MongoClient
from collections import OrderedDict, defaultdict
from bson.objectid import ObjectId
import arrow
import unidecode
import user_agents
import xlsxwriter
from datetime import datetime
import time


def remove_accents(s):
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    return unidecode.unidecode(s)


Mongodb = MongoClient(
    '10.28.12.130',
    27017,
    document_class=OrderedDict,
    maxPoolSize=200,
    serverSelectionTimeoutMS=90000)

DATABASE = Mongodb['nextify']
DATABASE.authenticate(
    'develop',
    'g5i4dI8KzYmXs0K',
    source='nextify')
from_date = '12-06-2022'
from_obj = datetime.strptime(from_date, '%d-%m-%Y'). \
            replace(hour=0, minute=0)
from_tmp = time.mktime(from_obj.timetuple())
to_date = '12-06-2022'
to_obj = datetime.strptime(to_date, '%d-%m-%Y'). \
            replace(hour=23, minute=59)
to_tmp = time.mktime(to_obj.timetuple())

info = {}
info['merchant_id'] = ObjectId('60e5f654a375457c8680756b')
info['last_visit'] = {}
info['last_visit']['$gte'] = from_tmp
info['last_visit']['$lte'] = to_tmp
recs = DATABASE.customers.find(
    info, no_cursor_timeout=True).sort('last_visit', -1)

print(recs.count())
list_cus = []
header_item = ['Ten', 'Phone', 'Email', 'Loai may', 'He dieu hanh', 'Dia chi MAC', 'Sinh nhat', 'Nam sinh',
               'Gioi tinh',
               'Luot den', 'Lan cuoi']
list_cus.append(header_item)
results = [rec for rec in recs]
for rec in results:
    item = []
    user = rec.get('user')
    if user:
        name = user.get('name')
        if name and len(name) > 0:
            name = remove_accents(name).upper()
        item.append(name)
        item.append(user.get('phone'))
        item.append(user.get('email'))
        birthday = user.get('birthday', '')
        year_birthday = user.get('year_birthday', '')
        list_client_mac = ''
        list_device = ''
        list_os = ''
        client_mac = user.get('client_mac')

        if client_mac and len(client_mac) > 0:
            if len(client_mac) > 1:
                for data in client_mac:
                    list_client_mac = list_client_mac + str(data) + '\n'
                    access_log_user = DATABASE.access_log.find_one(
                        {'client_mac': data})
                    if access_log_user:
                        device_detail = str(user_agents.parse(
                            access_log_user.get('user_agent', '')))
                        list_device = list_device + \
                            str(device_detail.split('/')[0]) + "\n"
                        list_os = list_os + \
                            str(device_detail.split('/')[1]) + "\n"
            else:
                list_client_mac = client_mac[0]
                access_log_user = DATABASE.access_log.find_one(
                    {'client_mac': client_mac[0]})
                if access_log_user:
                    device_detail = str(user_agents.parse(
                        access_log_user.get('user_agent', '')))
                    list_device = str(device_detail.split('/')[0])
                    list_os = list_os + \
                        str(device_detail.split('/')[1]) + "\n"

        item.append(list_device)
        item.append(list_os)
        item.append(list_client_mac)
        item.append(birthday)
        item.append(year_birthday)
        gender = user.get('gender', '')
        item.append(gender)
        item.append(rec.get('total_visit'))
        last_visit = rec.get('last_visit')
        if last_visit:
            item.append(arrow.get(last_visit).to('Asia/Saigon').format(
                'DD-MM-YYYY HH:mm:ss'))
        else:
            item.append('')
        list_cus.append(item)


with xlsxwriter.Workbook('sb.xlsx') as workbook:
    worksheet = workbook.add_worksheet()

    for row_num, data in enumerate(list_cus):
        worksheet.write_row(row_num, 0, data)
