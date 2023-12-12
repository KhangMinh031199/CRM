#! coding: utf-8
from datetime import datetime, timedelta
import time
from bson.objectid import ObjectId
import api
import settings
import overview

def export_file_re(merchant_id, shop_id_select, range_time):
    print "---=======----"
    total_customer = 0
    total_visit = 0
    new_cus = 0
    return_cus = 0
    message = 0
    return_mess = 0
    total_windows = 0
    total_iphone = 0
    total_android = 0
    total_mac = 0
    total_linux = 0
    total_first_visit = 0
    total_second_visit = 0
    total_loyal_visit = 0
    graph_report = {}
    gateway_macs = []
    if range_time != 'all':
        print "-----------range time"
        range_time = int(range_time)
        ex_start_time = datetime.now() - timedelta(days=int(range_time))
        end_time = timedelta(days=range_time)
        start_time = datetime.now()
        start_date = start_time.strftime("%d-%m-%Y")
        end_date = (start_time - end_time).strftime("%d-%m-%Y")
        if shop_id_select != 'all':
            shop = api.get_shop_info(shop_id=shop_id_select)
            gateway_macs.extend(shop.get('gateway_mac', []))
            total_customers, graph_report = overview.count_customers(merchant_id, start_time=datetime.now(
            ), shop_id=shop_id_select, time_range=range_time, is_report=True)
            total_visit, graph_report = overview.count_vists(merchant_id, start_time=datetime.now(
            ), shop_id=shop_id_select, time_range=range_time, is_report=True)
            new_cus, graph_report = overview.count_new_customers(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            return_cus, graph_report = overview.count_return_customers(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            message, graph_report = overview.count_message_send(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            return_mess, graph_report = overview.count_walk_throughs(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            #thiet bi
            total_windows = api.total_access_log_by_os(gateway_macs, 'Windows',
                                                   from_date=end_date,
                                                   to_date=start_date)
            total_iphone = api.total_access_log_by_os(gateway_macs, 'iPhone',
                                                    from_date=end_date,
                                                    to_date=start_date)
            total_android = api.total_access_log_by_os(gateway_macs, 'Android',
                                                    from_date=end_date,
                                                    to_date=start_date)
            total_mac = api.total_access_log_by_os(gateway_macs, 'Macintosh',
                                                from_date=end_date,
                                                to_date=start_date)
            total_linux = api.total_access_log_by_os(gateway_macs, 'Linux',
                                                    from_date=end_date,
                                                    to_date=start_date)
            #luot den
            total_first_visit = api.total_shop_customers(shop_id_select,
                                                         min_visit='1',
                                                         max_visit='1',
                                                         from_date=end_date,
                                                         to_date=start_date)
            total_second_visit = api.total_shop_customers(shop_id_select,
                                                          min_visit='2',
                                                          max_visit='9',
                                                          from_date=end_date,
                                                          to_date=start_date)
            total_loyal_visit = api.total_shop_customers(shop_id_select,
                                                         min_visit='10',
                                                         from_date=end_date,
                                                         to_date=start_date)
        else:
            shop_in_mer = api.get_shop_by_merchant(merchant_id)
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                gateway_mac = shop_mer.get('gateway_mac', [])
                gateway_macs.extend(gateway_mac)

            total_customers, graph_report = overview.count_customers(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            total_visit, graph_report = overview.count_vists(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            new_cus, graph_report = overview.count_new_customers(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            return_cus, graph_report = overview.count_return_customers(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            message, graph_report = overview.count_message_send(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            return_mess, graph_report = overview.count_walk_throughs(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            #thiet bi
            total_windows = api.total_access_log_by_os(gateway_macs, 'Windows',
                                                   from_date=end_date,
                                                   to_date=start_date)
            total_iphone = api.total_access_log_by_os(gateway_macs, 'iPhone',
                                                    from_date=end_date,
                                                    to_date=start_date)
            total_android = api.total_access_log_by_os(gateway_macs, 'Android',
                                                    from_date=end_date,
                                                    to_date=start_date)
            total_mac = api.total_access_log_by_os(gateway_macs, 'Macintosh',
                                                from_date=end_date,
                                                to_date=start_date)
            total_linux = api.total_access_log_by_os(gateway_macs, 'Linux',
                                                    from_date=end_date,
                                                    to_date=start_date)
            #luot den
            total_first_visit = api.total_merchant_customers(merchant_id,
                                                             min_visit='1',
                                                             max_visit='1',
                                                             from_date=end_date,
                                                             to_date=start_date)
            total_second_visit = api.total_merchant_customers(merchant_id,
                                                              min_visit='2',
                                                              max_visit='9',
                                                              from_date=end_date,
                                                              to_date=start_date)
            total_loyal_visit = api.total_merchant_customers(merchant_id,
                                                             min_visit='10',
                                                             from_date=end_date,
                                                             to_date=start_date)
    else:
        if shop_id_select != 'all':
            shop = api.get_shop_info(shop_id=shop_id_select)
            gateway_macs.extend(shop.get('gateway_mac', []))
            total_customers, graph_report = overview.count_customers(merchant_id, start_time=datetime.now(
            ), shop_id=shop_id_select, time_range=range_time, is_report=True)
            total_visit, graph_report = overview.count_vists(merchant_id, start_time=datetime.now(
            ), shop_id=shop_id_select, time_range=range_time, is_report=True)
            new_cus, graph_report = overview.count_new_customers(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            return_cus, graph_report = overview.count_return_customers(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            message, graph_report = overview.count_message_send(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            return_mess, graph_report = overview.count_walk_throughs(
                merchant_id, start_time=datetime.now(), shop_id=shop_id_select, time_range=range_time, is_report=True)
            #thiet bi
            total_windows = api.total_access_log_by_os(gateway_macs, 'Windows')
            total_iphone = api.total_access_log_by_os(gateway_macs, 'iPhone')
            total_android = api.total_access_log_by_os(gateway_macs, 'Android')
            total_mac = api.total_access_log_by_os(gateway_macs, 'Macintosh')
            total_linux = api.total_access_log_by_os(gateway_macs, 'Linux')
            #luot den
            total_first_visit = api.total_shop_customers(shop_id_select,
                                                         min_visit='1',
                                                         max_visit='1')
            total_second_visit = api.total_shop_customers(shop_id_select,
                                                          min_visit='2',
                                                          max_visit='9')
            total_loyal_visit = api.total_shop_customers(shop_id_select,
                                                         min_visit='10')
        else:
            shop_in_mer = api.get_shop_by_merchant(merchant_id)
            for shop_mer in shop_in_mer:
                if not isinstance(shop_mer['_id'], ObjectId):
                    shop_mer['_id'] = ObjectId(shop_mer['_id'])
                gateway_mac = shop_mer.get('gateway_mac', [])
                gateway_macs.extend(gateway_mac)

            total_customers, graph_report = overview.count_customers(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            total_visit, graph_report = overview.count_vists(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            new_cus, graph_report = overview.count_new_customers(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            return_cus, graph_report = overview.count_return_customers(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            message, graph_report = overview.count_message_send(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            return_mess, graph_report = overview.count_walk_throughs(
                merchant_id, start_time=datetime.now(), shop_id=None, time_range=range_time, is_report=True)
            #thiet bi
            total_windows = api.total_access_log_by_os(gateway_macs, 'Windows')
            total_iphone = api.total_access_log_by_os(gateway_macs, 'iPhone')
            total_android = api.total_access_log_by_os(gateway_macs, 'Android')
            total_mac = api.total_access_log_by_os(gateway_macs, 'Macintosh')
            total_linux = api.total_access_log_by_os(gateway_macs, 'Linux')
            #luot den
            total_first_visit = api.total_merchant_customers(merchant_id,
                                                             min_visit='1',
                                                             max_visit='1')
            total_second_visit = api.total_merchant_customers(merchant_id,
                                                              min_visit='2',
                                                              max_visit='9')
            total_loyal_visit = api.total_merchant_customers(merchant_id,
                                                             min_visit='10')
    