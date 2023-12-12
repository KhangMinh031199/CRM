import api
import unicodecsv
import os
import io

merchants = api.get_merchants()
list_cus = []
header_item = ['khach hang', 'so dien thoai', 'so dia diem']
list_cus.append(header_item)

for rec in merchants:
    item = []
    name = rec.get('name')
    name = api.remove_accents(name)
    phone = rec.get('phone')
    locations = api.get_shop_by_merchant(str(rec.get('_id')))
    item.append(name)
    item.append(phone)
    item.append(len(locations))
    list_cus.append(item)

file_name = 'merchant.csv'
path_file = str(os.getcwd()) + '/%s' % (file_name)

with io.open(path_file, "wb") as f:
    writer = unicodecsv.writer(f, encoding='utf-8')
    writer.writerows(list_cus)
