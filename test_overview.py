from datetime import datetime
import overview
import xlsxwriter
import api
import settings
import os
merchant_id = '62d7b3a6e45c127af0da5c71'
shops = api.get_shop_by_merchant(merchant_id)

for shop in shops:
    print(shop.get('name'))
    shop_id = shop.get('_id')
    total_customers, graph_report = overview.count_customers(
        merchant_id, start_time=datetime.now(), shop_id=shop_id, time_range='all', is_report=True)
    total_visit, graph_report_visit = overview.count_vists(
                merchant_id, start_time=datetime.now(), shop_id=shop_id, time_range='all', is_report=True)
    new_customers, graph_report_new = overview.count_new_customers(
                merchant_id, start_time=datetime.now(), shop_id=shop_id, time_range='all', is_report=True)
    return_customers, graph_report_return = overview.count_return_customers(
                merchant_id, start_time=datetime.now(), shop_id=shop_id, time_range='all', is_report=True)
    
    cus_by_visit = overview.count_customers_by_visits(
            merchant_id, start_time=datetime.now(), shop_id=shop_id, time_range='all')
    cus_by_hours = overview.count_customers_by_hours(
            merchant_id, start_time=datetime.now(), shop_id=shop_id, time_range='all')
    cus_by_day = overview.count_customers_by_day(
            merchant_id, start_time=datetime.now(), shop_id=shop_id, time_range='all')
    print (cus_by_hours)
    list_cus = []
    header_item =['Khach hang', 'Luot den', 'Khach moi', 'Quay lai']
    list_cus.append(header_item)
    list_cus.append([total_customers, total_visit, new_customers, return_customers ])
    list_cus.append(['Theo luot den'])
    device_header = []
    device_val = []
    for cus_by_visits in cus_by_visit:
        device_header.append(list(cus_by_visits.keys())[0])
        device_val.append(list(cus_by_visits.values())[0])
    list_cus.append(device_header)
    list_cus.append(device_val)
    list_cus.append(['Theo khung gio'])
    hour_header = []
    hour_val = []
    for cus_by_hour in cus_by_hours:
        print(cus_by_hour)
        hour_header.append(cus_by_hour[0])
        hour_val.append(cus_by_hour[1])
    list_cus.append(hour_header)
    list_cus.append(hour_val)
    list_cus.append(['Theo ngay trong tuan'])
    day_header = []
    day_val = []
    for cus_day in cus_by_day:
        print(cus_day)
        day_header.append(settings.DAY_IN_WEEEK.get(str(cus_day.get('_id'))))
        day_val.append(cus_day.get('count'))
    list_cus.append(day_header)
    list_cus.append(day_val)
    print (list_cus)
    file_name = api.remove_accents(shop.get('name')).replace(' ', '_')
    path_file = str(os.getcwd()) + '/static/export_file/%s.xlsx' % (file_name)
    

    with xlsxwriter.Workbook(path_file) as workbook:
        worksheet = workbook.add_worksheet()

        for row_num, data in enumerate(list_cus):
            worksheet.write_row(row_num, 0, data)