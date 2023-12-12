import datetime
import time
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta
import api
import settings


def range_date_count(start_time, days):
    report_arrays = []
    day = start_time - datetime.timedelta(days=int(days))
    report_arrays.append(day.strftime("%d-%m-%Y"))
    if int(days) < 365:
        report_arrays.append(day.strftime("%d-%m-%Y"))
        while day < start_time:
            day = day + relativedelta(days=+1)
            report_arrays.append(day.strftime("%d-%m-%Y"))
            report_arrays.append(day.strftime("%d-%m-%Y"))
    else:
        if int(days) == 365:
            while day < start_time:
                day = day + relativedelta(months=+1)
                report_arrays.append(day.strftime("%d-%m-%Y"))
                if day != start_time:
                    report_arrays.append((day + relativedelta(days=+1)).strftime("%d-%m-%Y"))

        else:
            while day.year < start_time.year - 1:
                day = day + relativedelta(years=+1)
                report_arrays.append(day.strftime("%d-%m-%Y"))
                report_arrays.append((day + relativedelta(days=+1)).strftime("%d-%m-%Y"))
            report_arrays.append(start_time.strftime("%d-%m-%Y"))
    return report_arrays


def range_all_time_merchant(start_time, merchant_id):
    merchant = api.get_merchant(merchant_id)
    shops = api.DATABASE.shop.find({'merchant_id': merchant_id, 'created_at': {"$exists": True}}).sort('created_at',
                                                                                                       1).limit(1)

    first_visit = api.get_first_time_visit_merchant(merchant_id)
    if first_visit:
        first_visit = first_visit[0]
        first_visit = first_visit.get('last_visit')
        if not first_visit or str(first_visit) == 'None':
            if shops.count() > 0:
                first_visit = [shop for shop in shops][0].get('created_at')
            else:
                first_visit = merchant.get('when')
    else:
        if shops.count() > 0:
            first_visit = [shop for shop in shops][0].get('created_at')
        else:
            first_visit = merchant.get('when')

    days = start_time - datetime.datetime.fromtimestamp(first_visit)
    return range_date_count(start_time, days.days)


def range_all_time_shop_id(start_time, shop_id):
    shop = api.get_shop_info(shop_id=shop_id)
    first_visit = api.get_first_time_visit_shop(shop_id)
    if first_visit:
        first_visit = first_visit[0]
        first_visit = first_visit.get('last_visit')
        if not first_visit or str(first_visit) == 'None':
            first_visit = shop.get('created_at')
    else:
        first_visit = shop.get('created_at')

    days = start_time - datetime.datetime.fromtimestamp(first_visit)
    return range_date_count(start_time, days.days)


def count_customers(merchant_id, start_time=None, shop_id=None, time_range=None, is_report=None):
    total = 0
    range_report = []
    graph_count = {}
    if shop_id:
        if time_range == 'all':
            total = api.total_shop_customers(shop_id)
            range_report = range_all_time_shop_id(start_time, shop_id)

        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total = api.total_shop_customers(shop_id,
                                             from_date=end_date,
                                             to_date=start_date)
            range_report = range_date_count(start_time, time_range)
    else:
        if time_range == 'all':
            total = api.total_merchant_customers(merchant_id)
            range_report = range_all_time_merchant(start_time, merchant_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total = api.total_merchant_customers(merchant_id,
                                                 from_date=end_date,
                                                 to_date=start_date)
            range_report = range_date_count(start_time, time_range)
    label = []
    data = []
    average = 0
    if total > 0 and len(range_report) > 0 and is_report:

        for _range in range(0, len(range_report), 2):
            label.append(range_report[_range])
            if shop_id:
                total_in_range = api.total_shop_customers(shop_id,
                                                          from_date=range_report[_range],
                                                          to_date=range_report[_range + 1])
                data.append(total_in_range)
            else:
                total_in_range = api.total_merchant_customers(merchant_id,
                                                              from_date=range_report[_range],
                                                              to_date=range_report[_range + 1])
                data.append(total_in_range)
        _start_time = datetime.datetime.strptime(range_report[0], "%d-%m-%Y")
        diff_days = (start_time - _start_time).days
        average = int(round(total / diff_days))
    graph_count = {'label': label, 'data': data, 'average': average}
    return total, graph_count


def count_vists(merchant_id, start_time=None, shop_id=None, time_range=None, is_report=None):
    total = 0
    range_report = []
    graph_count = {}
    if shop_id:
        if time_range == 'all':
            total = api.total_visit_log(shop_id)
            range_report = range_all_time_shop_id(start_time, shop_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            end_date = start_time.strftime("%d-%m-%Y")
            start_date = (start_time - end_time).strftime("%d-%m-%Y")
            from_obj = datetime.datetime.strptime(
                start_date, '%d-%m-%Y').replace(hour=0, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())

            to_obj = datetime.datetime.strptime(
                end_date, '%d-%m-%Y').replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            total = api.total_visit_log(
                shop_id, merchant_id=None, start_time=from_tmp, end_time=to_tmp)
            range_report = range_date_count(start_time, time_range)
    else:
        if time_range == 'all':
            total = api.total_visit_log(shop_id, merchant_id=merchant_id)
            range_report = range_all_time_merchant(start_time, merchant_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            end_date = start_time.strftime("%d-%m-%Y")
            start_date = (start_time - end_time).strftime("%d-%m-%Y")
            from_obj = datetime.datetime.strptime(
                start_date, '%d-%m-%Y').replace(hour=0, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())

            to_obj = datetime.datetime.strptime(
                end_date, '%d-%m-%Y').replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            total = api.total_visit_log(
                shop_id, merchant_id=merchant_id, start_time=from_tmp, end_time=to_tmp)
            range_report = range_date_count(start_time, time_range)
    label = []
    data = []
    average = 0
    if total > 0 and len(range_report) > 0 and is_report:
        for _range in range(0, len(range_report), 2):
            label.append(range_report[_range])
            from_obj = datetime.datetime.strptime(
                range_report[_range], '%d-%m-%Y').replace(hour=0, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())

            to_obj = datetime.datetime.strptime(
                range_report[_range + 1], '%d-%m-%Y').replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            if shop_id:

                total_in_range = api.total_visit_log(
                    shop_id, merchant_id=None, start_time=from_tmp, end_time=to_tmp)
                data.append(total_in_range)
            else:
                total_in_range = api.total_visit_log(
                    shop_id, merchant_id=merchant_id, start_time=from_tmp, end_time=to_tmp)
                data.append(total_in_range)
        _start_time = datetime.datetime.strptime(range_report[0], "%d-%m-%Y")
        diff_days = (start_time - _start_time).days
        average = int(round(total / diff_days))
    graph_count = {'label': label, 'data': data, 'average': average}
    return total, graph_count


def count_new_customers(merchant_id, start_time=None, shop_id=None, time_range=None, is_report=None):
    total = 0
    range_report = []
    graph_count = {}
    if shop_id:
        if time_range == 'all':
            total = api.total_shop_customers(shop_id,
                                             min_visit='1',
                                             max_visit='1')
            range_report = range_all_time_shop_id(start_time, shop_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total = api.total_shop_customers(shop_id,
                                             from_date=end_date,
                                             to_date=start_date,
                                             min_visit='1',
                                             max_visit='1')
            range_report = range_date_count(start_time, time_range)
    else:
        if time_range == 'all':
            total = api.total_merchant_customers(merchant_id,
                                                 min_visit='1',
                                                 max_visit='1')
            range_report = range_all_time_merchant(start_time, merchant_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total = api.total_merchant_customers(merchant_id,
                                                 from_date=end_date,
                                                 to_date=start_date,
                                                 min_visit='1',
                                                 max_visit='1')
            range_report = range_date_count(start_time, time_range)
    label = []
    data = []
    average = 0
    if total > 0 and len(range_report) > 0 and is_report:

        for _range in range(0, len(range_report), 2):
            label.append(range_report[_range])
            if shop_id:
                total_in_range = api.total_shop_customers(shop_id,
                                                          from_date=range_report[_range],
                                                          to_date=range_report[_range + 1],
                                                          min_visit='1',
                                                          max_visit='1')
                data.append(total_in_range)
            else:
                total_in_range = api.total_merchant_customers(merchant_id,
                                                              from_date=range_report[_range],
                                                              to_date=range_report[_range + 1],
                                                              min_visit='1',
                                                              max_visit='1')
                data.append(total_in_range)
        _start_time = datetime.datetime.strptime(range_report[0], "%d-%m-%Y")
        diff_days = (start_time - _start_time).days
        average = int(round(total / diff_days))
    graph_count = {'label': label, 'data': data, 'average': average}
    return total, graph_count


def count_return_customers(merchant_id, start_time=None, shop_id=None, time_range=None, is_report=None):
    total = 0
    range_report = []
    graph_count = {}
    average = 0
    if shop_id:
        if time_range == 'all':
            total = api.total_shop_customers(shop_id,
                                             min_visit='2')
            range_report = range_all_time_shop_id(start_time, shop_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total = api.total_shop_customers(shop_id,
                                             from_date=end_date,
                                             to_date=start_date,
                                             min_visit='2')
            range_report = range_date_count(start_time, time_range)
    else:
        if time_range == 'all':
            total = api.total_merchant_customers(merchant_id,
                                                 min_visit='2')
            range_report = range_all_time_merchant(start_time, merchant_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total = api.total_merchant_customers(merchant_id,
                                                 from_date=end_date,
                                                 to_date=start_date,
                                                 min_visit='2')
            range_report = range_date_count(start_time, time_range)
    label = []
    data = []
    if total > 0 and len(range_report) > 0 and is_report:

        for _range in range(0, len(range_report), 2):
            label.append(range_report[_range])
            if shop_id:
                total_in_range = api.total_shop_customers(shop_id,
                                                          from_date=range_report[_range],
                                                          to_date=range_report[_range + 1],
                                                          min_visit='2')
                data.append(total_in_range)
            else:
                total_in_range = api.total_merchant_customers(merchant_id,
                                                              from_date=range_report[_range],
                                                              to_date=range_report[_range + 1],
                                                              min_visit='2')
                data.append(total_in_range)
        _start_time = datetime.datetime.strptime(range_report[0], "%d-%m-%Y")
        diff_days = (start_time - _start_time).days
        average = int(round(total / diff_days))
    graph_count = {'label': label, 'data': data, 'average': average}
    return total, graph_count


def count_message_send(merchant_id, start_time=None, shop_id=None, time_range=None, is_report=None):
    total = 0
    range_report = []
    graph_count = {}
    if shop_id:
        if time_range == 'all':
            total = api.total_activity_smart_message(shop_id)
            range_report = range_all_time_shop_id(start_time, shop_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            end_date = start_time.strftime("%d-%m-%Y")
            start_date = (start_time - end_time).strftime("%d-%m-%Y")
            from_obj = datetime.datetime.strptime(
                start_date, '%d-%m-%Y').replace(hour=0, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())

            to_obj = datetime.datetime.strptime(
                end_date, '%d-%m-%Y').replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            total = api.total_activity_smart_message(shop_id,
                                                     start_time=from_tmp,
                                                     end_time=to_tmp)
            range_report = range_date_count(start_time, time_range)

    else:
        if time_range == 'all':
            total = api.total_activity_smart_message(
                shop_id, merchant_id=merchant_id)
            range_report = range_all_time_merchant(start_time, merchant_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            end_date = start_time.strftime("%d-%m-%Y")
            start_date = (start_time - end_time).strftime("%d-%m-%Y")
            from_obj = datetime.datetime.strptime(
                start_date, '%d-%m-%Y').replace(hour=0, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())

            to_obj = datetime.datetime.strptime(
                end_date, '%d-%m-%Y').replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            total = api.total_activity_smart_message(shop_id,
                                                     merchant_id=merchant_id,
                                                     start_time=from_tmp,
                                                     end_time=to_tmp)
            range_report = range_date_count(start_time, time_range)

    label = []
    data = []
    average = 0
    if int(total) > 0 and len(range_report) > 0 and is_report:

        for _range in range(0, len(range_report), 2):
            label.append(range_report[_range])
            from_obj = datetime.datetime.strptime(
                range_report[_range], '%d-%m-%Y').replace(hour=0, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())

            to_obj = datetime.datetime.strptime(
                range_report[_range + 1], '%d-%m-%Y').replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            if shop_id:

                total_in_range = api.total_activity_smart_message(shop_id,
                                                                  start_time=from_tmp,
                                                                  end_time=to_tmp)
                data.append(total_in_range)
            else:

                total_in_range = api.total_activity_smart_message(shop_id,
                                                                  merchant_id=merchant_id,
                                                                  start_time=from_tmp,
                                                                  end_time=to_tmp)
                data.append(total_in_range)

        _start_time = datetime.datetime.strptime(range_report[0], "%d-%m-%Y")
        diff_days = (start_time - _start_time).days
        average = int(round(total / diff_days))
    graph_count = {'label': label, 'data': data, 'average': average}
    return total, graph_count


def count_walk_throughs(merchant_id, start_time=None, shop_id=None, time_range=None, is_report=None):
    visit_walkthrought = 0
    range_report = []
    graph_count = {}
    shop_ids = []
    if shop_id:
        shop_ids.append(shop_id)
    else:
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shop_ids.append(shop_mer['_id'])

    if time_range == 'all':
        visit_walkthrought_count = api.count_visit_walkthrough(shop_ids)
        if len(visit_walkthrought_count) > 0:
            _walk = visit_walkthrought_count[0]
            visit_walkthrought = _walk.get('count')
        if shop_id:
            range_report = range_all_time_shop_id(start_time, shop_id)
        else:
            range_report = range_all_time_merchant(start_time, merchant_id)
    else:
        end_time = datetime.timedelta(days=int(time_range))
        end_date = start_time.strftime("%d-%m-%Y")
        start_date = (start_time - end_time).strftime("%d-%m-%Y")
        from_obj = datetime.datetime.strptime(
            start_date, '%d-%m-%Y').replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())

        to_obj = datetime.datetime.strptime(
            end_date, '%d-%m-%Y').replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        visit_walkthrought_count = api.count_visit_walkthrough(
            shop_ids, start_time=from_tmp, end_time=to_tmp)
        if len(visit_walkthrought_count) > 0:
            _walk = visit_walkthrought_count[0]
            visit_walkthrought = _walk.get('count')
        range_report = range_date_count(start_time, time_range)

    label = []
    data = []
    average = 0
    if visit_walkthrought > 0 and len(range_report) > 0 and is_report:
        for _range in range(0, len(range_report), 2):
            label.append(range_report[_range])
            from_obj = datetime.datetime.strptime(
                range_report[_range], '%d-%m-%Y').replace(hour=0, minute=0)
            from_tmp = time.mktime(from_obj.timetuple())

            to_obj = datetime.datetime.strptime(
                range_report[_range + 1], '%d-%m-%Y').replace(hour=23, minute=59)
            to_tmp = time.mktime(to_obj.timetuple())
            total_in_range = 0
            visit_walkthrought_count = api.count_visit_walkthrough(shop_ids, start_time=from_tmp, end_time=to_tmp)
            if len(visit_walkthrought_count) > 0:
                _walk = visit_walkthrought_count[0]
                total_in_range = _walk.get('count')
            data.append(total_in_range)

        _start_time = datetime.datetime.strptime(range_report[0], "%d-%m-%Y")
        diff_days = (start_time - _start_time).days
        average = int(round(visit_walkthrought / diff_days))
    graph_count = {'label': label, 'data': data, 'average': average}
    return visit_walkthrought, graph_count


def count_customers_by_locations(merchant_id, start_time=None, shop_id=None, time_range=None):
    cus_by_location = []
    if shop_id:
        if time_range == 'all':
            total = api.total_shop_customers(shop_id)
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total = api.total_shop_customers(shop_id,
                                             from_date=end_date,
                                             to_date=start_date)
        shop = api.get_shop_info(shop_id=shop_id)
        shop_name = shop.get('name')
        cus_by_location.append({
            str(shop_name): total
        })
    else:
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        if time_range == 'all':
            for shop in shop_in_mer:
                shop_name = shop.get('name')
                total = api.total_shop_customers(shop.get('_id'))
                cus_by_location.append({
                    str(shop_name): total
                })
        else:
            for shop in shop_in_mer:
                end_time = datetime.timedelta(days=int(time_range))
                start_date = start_time.strftime("%d-%m-%Y")
                end_date = (start_time - end_time).strftime("%d-%m-%Y")
                shop_name = shop.get('name')
                total = api.total_shop_customers(shop.get('_id'),
                                                 from_date=end_date,
                                                 to_date=start_date)
                cus_by_location.append({
                    str(shop_name): total
                })
        if len(cus_by_location) > 0:
            cus_by_location.sort(key=lambda d: sorted(list(d.keys()), reverse=True))
            if len(cus_by_location) > 4:
                new_cus_location = cus_by_location[:3]
                other_cus = cus_by_location[3:]
                total_other = sum(list(item.values())[0] for item in other_cus)
                new_cus_location.append({
                    'Other': total_other
                })
                cus_by_location = new_cus_location
    return cus_by_location


def count_customers_by_device(merchant_id, start_time=None, shop_id=None, time_range=None):
    total = []
    gateway_macs = []

    if shop_id:
        shop = api.get_shop_info(shop_id=shop_id)
        gateway_macs.extend(shop.get('gateway_mac', []))

    else:
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            gateway_mac = shop_mer.get('gateway_mac', [])
            gateway_macs.extend(gateway_mac)

    if time_range == 'all':
        total_windows = api.total_access_log_by_os(gateway_macs, 'Windows')
        total_iphone = api.total_access_log_by_os(gateway_macs, 'iPhone')
        total_android = api.total_access_log_by_os(gateway_macs, 'Android')
        total_mac = api.total_access_log_by_os(gateway_macs, 'Macintosh')
        total_linux = api.total_access_log_by_os(gateway_macs, 'Linux')
        total = [
            {'Windows': total_windows},
            {'IPhone': total_iphone},
            {'Android': total_android},
            {'Mac OS': total_mac},
            {'Linux': total_linux}]
    else:
        end_time = datetime.timedelta(days=int(time_range))
        start_date = start_time.strftime("%d-%m-%Y")
        end_date = (start_time - end_time).strftime("%d-%m-%Y")
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
        total = [
            {'Windows': total_windows},
            {'IPhone': total_iphone},
            {'Android': total_android},
            {'Mac OS': total_mac},
            {'Linux': total_linux}]
    return total


def count_customers_by_visits(merchant_id, start_time=None, shop_id=None, time_range=None):
    total_first_visit = 0
    total_second_visit = 0
    total_loyal_visit = 0
    if shop_id:
        if time_range == 'all':
            total_first_visit = api.total_shop_customers(shop_id,
                                                         min_visit='1',
                                                         max_visit='1')
            total_second_visit = api.total_shop_customers(shop_id,
                                                          min_visit='2',
                                                          max_visit='9')
            total_loyal_visit = api.total_shop_customers(shop_id,
                                                         min_visit='10')
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
            total_first_visit = api.total_shop_customers(shop_id,
                                                         min_visit='1',
                                                         max_visit='1',
                                                         from_date=end_date,
                                                         to_date=start_date)
            total_second_visit = api.total_shop_customers(shop_id,
                                                          min_visit='2',
                                                          max_visit='9',
                                                          from_date=end_date,
                                                          to_date=start_date)
            total_loyal_visit = api.total_shop_customers(shop_id,
                                                         min_visit='10',
                                                         from_date=end_date,
                                                         to_date=start_date)
    else:
        if time_range == 'all':
            total_first_visit = api.total_merchant_customers(merchant_id,
                                                             min_visit='1',
                                                             max_visit='1')
            total_second_visit = api.total_merchant_customers(merchant_id,
                                                              min_visit='2',
                                                              max_visit='9')
            total_loyal_visit = api.total_merchant_customers(shop_id,
                                                             min_visit='10')
        else:
            end_time = datetime.timedelta(days=int(time_range))
            start_date = start_time.strftime("%d-%m-%Y")
            end_date = (start_time - end_time).strftime("%d-%m-%Y")
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

    return [{'1': total_first_visit},
            {'2-9': total_second_visit},
            {'10+': total_loyal_visit}]


def count_customers_by_day(merchant_id, start_time=None, shop_id=None, time_range=None):
    visit_days = []
    shop_ids = []
    if shop_id:
        shop_ids.append(shop_id)
    else:
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shop_ids.append(shop_mer['_id'])
    if time_range == 'all':
        visit_days = api.count_visit_by_weekday(shop_ids)
    else:
        end_time = datetime.timedelta(days=int(time_range))
        end_date = start_time.strftime("%d-%m-%Y")
        start_date = (start_time - end_time).strftime("%d-%m-%Y")
        from_obj = datetime.datetime.strptime(
            start_date, '%d-%m-%Y').replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())

        to_obj = datetime.datetime.strptime(
            end_date, '%d-%m-%Y').replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        visit_days = api.count_visit_by_weekday(
            shop_ids, start_time=from_tmp, end_time=to_tmp)

    return [day for day in visit_days]


def count_customers_by_hours(merchant_id, start_time=None, shop_id=None, time_range=None):
    visit_hour = []
    shop_ids = []
    if shop_id:
        shop_ids.append(shop_id)
    else:
        shop_in_mer = api.get_shop_by_merchant(merchant_id)
        for shop_mer in shop_in_mer:
            if not isinstance(shop_mer['_id'], ObjectId):
                shop_mer['_id'] = ObjectId(shop_mer['_id'])
            shop_ids.append(shop_mer['_id'])
    if time_range == 'all':
        for range_hour in settings.HOURS_VISIT_RANGE:
            min_range = range_hour.get('min')
            max_range = range_hour.get('max')
            min_range_vi = range_hour.get('min_vi')
            max_range_vi = range_hour.get('max_vi')
            range_ = range_hour.get('name')
            count_visit = 0
            if range_ == "range6":
                count_visit = api.count_log_by_hour(shop_ids, min_range_vi, max_range_vi, range_=range_)
            else:
                count_visit = api.count_log_by_hour(shop_ids, min_range_vi, max_range_vi)
            item = []
            range_str = str(min_range) + '-' + str(max_range)
            item.append(range_str)
            item.append(count_visit)
            visit_hour.append(item)
    else:
        end_time = datetime.timedelta(days=int(time_range))
        end_date = start_time.strftime("%d-%m-%Y")
        start_date = (start_time - end_time).strftime("%d-%m-%Y")
        from_obj = datetime.datetime.strptime(
            start_date, '%d-%m-%Y').replace(hour=0, minute=0)
        from_tmp = time.mktime(from_obj.timetuple())

        to_obj = datetime.datetime.strptime(
            end_date, '%d-%m-%Y').replace(hour=23, minute=59)
        to_tmp = time.mktime(to_obj.timetuple())
        for range_hour in settings.HOURS_VISIT_RANGE:
            min_range = range_hour.get('min')
            max_range = range_hour.get('max')
            min_range_vi = range_hour.get('min_vi')
            max_range_vi = range_hour.get('max_vi')
            range_ = range_hour.get('name')
            count_visit = 0
            if range_ == "range6":
                count_visit = api.count_log_by_hour(
                    shop_ids, min_range_vi, max_range_vi, start_time=from_tmp, end_time=to_tmp, range_=range_)
            else:
                count_visit = api.count_log_by_hour(
                    shop_ids, min_range_vi, max_range_vi, start_time=from_tmp, end_time=to_tmp)
            item = []
            range_str = str(min_range) + '-' + str(max_range)
            item.append(range_str)
            item.append(count_visit)
            visit_hour.append(item)
    return visit_hour

# print (count_customers('5a616f383fd79c2db9147c6a',
#                       start_time=datetime.datetime.now(), shop_id=None, time_range='all'))

# print (count_vists('5a616f383fd79c2db9147c6a',
#                    start_time=datetime.datetime.now(), shop_id=None, time_range=31))

# print (count_new_customers('5a616f383fd79c2db9147c6a',
#                    start_time=datetime.datetime.now(), shop_id=None, time_range=31))

# print (count_return_customers('5a616f383fd79c2db9147c6a',
#                    start_time=datetime.datetime.now(), shop_id=None, time_range=31))

# print (count_message_send('5a616f383fd79c2db9147c6a',
#                    start_time=datetime.datetime.now(), shop_id='597fe18647dd46ce3e554089', time_range='all' , is_report=True))

# print (count_customers_by_locations('5a616f383fd79c2db9147c6a',
# start_time=datetime.datetime.now(), shop_id=None, time_range='all'))

# print (count_customers_by_device('5a616f383fd79c2db9147c6a',
#  start_time=datetime.datetime.now(), shop_id='597fe18647dd46ce3e554089', time_range='all'))

# print (count_customers_by_visits('5a616f383fd79c2db9147c6a',
#                                  start_time=datetime.datetime.now(), shop_id='597fe18647dd46ce3e554089', time_range='all'))


# print (count_customers_by_hours('5a616f383fd79c2db9147c6a',
#                                 start_time=datetime.datetime.now(), shop_id=None, time_range=31))
# print (count_customers_by_day('5a616f383fd79c2db9147c6a',
#                                 start_time=datetime.datetime.now(), shop_id=None, time_range='all'))

# print (count_walk_throughs('5a616f383fd79c2db9147c6a',
#     start_time=datetime.datetime.now(), shop_id='597fe18647dd46ce3e554089', time_range='all'))

# from bson.objectid import ObjectId

# visit_log = api.DATABASE.send_activity_log.aggregate(
#     [
#         {"$match": {"shop_id": ObjectId('597fe18647dd46ce3e554089')}},
#         {"$lookup":
#          {
#              "from": "visit_log",
#              "let": {
#                  'customer_id': "$customer_id",
#                  'when': "$when"
#              }, 'pipeline': [
#                  {'$match':  {'$expr':
#                               {'$and':
#                                   [
#                                       {'$eq': ["$user_id",  "$$customer_id"]},
#                                       {'$gte': ["$timestamp", "$$when"]},
#                                       {'$lte': ["$timestamp", {
#                                           '$add': ["$$when", 7]}]}
#                                   ]
#                                }
#                               }}
#              ],
#              "as": "visits"
#          }},

#         {"$match": {'visits': { "$exists": True, "$ne": [] }}},
#         { '$group': {'_id': '$customer_id'}},
#         { '$count': 'count'}
#     ])

# for day in visit_log:
#     print (day)
