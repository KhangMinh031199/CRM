#! coding: utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import os
import io
import smtplib
import time
from os.path import basename
from bson.objectid import ObjectId
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import api
import unicodecsv
import arrow
import zalo_api
import storage_api
import base64
import gift_card_api
import settings
import user_agents
import xlsxwriter


def export_customers_hq(merchant_id, shop_id=None, from_date=None,
                        to_date=None, min_visit=None, max_visit=None,
                        sort=None, bday_from_date=None, bday_to_date=None,
                        gender=None, filter_tags=None, lost_day=None, is_ads=None):
    merchant = api.get_merchant(merchant_id)
    results = []
    shop = None
    if shop_id and str(shop_id) != 'all':
        shop = api.get_shop_info(shop_id=shop_id)
        results = api.get_shop_customers(merchant_id,
                                         shop_id,
                                         from_date=from_date,
                                         to_date=to_date,
                                         min_visit=min_visit,
                                         max_visit=max_visit,
                                         lost_day=lost_day,
                                         gender=gender,
                                         sort=sort,
                                         bday_from_date=bday_from_date,
                                         bday_to_date=bday_to_date,
                                         tags_array=filter_tags,
                                         page=None,
                                         page_size=settings.ITEMS_PER_PAGE)
    else:
        results = api.get_merchant_customers(merchant_id,
                                             from_date=from_date,
                                             to_date=to_date,
                                             min_visit=min_visit,
                                             max_visit=max_visit,
                                             lost_day=lost_day,
                                             gender=gender,
                                             sort=sort,
                                             bday_from_date=bday_from_date,
                                             bday_to_date=bday_to_date,
                                             tags_array=filter_tags,
                                             page=None,
                                             page_size=settings.ITEMS_PER_PAGE)
    zalo_cus = []
    facebook_cus = []
    list_cus = []
    header_item = ['Ten', 'Phone', 'Email', 'Loai may', 'He dieu hanh', 'Dia chi MAC', 'Sinh nhat', 'Nam sinh', 'Gioi tinh',
                   'Luot den', 'Lan cuoi']
    list_cus.append(header_item)

    for rec in results:
        item = []
        user = rec.get('user')
        if user:
            name = user.get('name')
            if name and len(name) > 0:
                name = api.remove_accents(name).upper()
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
                        access_log_user = api.DATABASE.access_log.find_one({'client_mac': data})
                        if access_log_user:
                            device_detail = str(user_agents.parse(access_log_user.get('user_agent', '')))
                            list_device = list_device + str(device_detail.split('/')[0]) + "\n"
                            list_os = list_os + str(device_detail.split('/')[1]) + "\n"
                else:
                    list_client_mac = client_mac[0]
                    access_log_user = api.DATABASE.access_log.find_one({'client_mac': client_mac[0]})
                    if access_log_user:
                        device_detail = str(user_agents.parse(access_log_user.get('user_agent', '')))
                        list_device = str(device_detail.split('/')[0])
                        list_os = list_os + str(device_detail.split('/')[1]) + "\n"

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
            if is_ads and len(is_ads) > 0 and 'zalo' in is_ads:
                if user:
                    phone = user.get('phone')
                    if phone and str(phone) != 'None':
                        zalo_cus.append(phone)

    if is_ads and len(is_ads) > 0 and 'facebook' in is_ads:
        fb_header_item = ['email', 'email', 'email', 'phone', 'phone', 'phone', 'madid', 'fn', 'ln', 'zip', 'ct', 'st',
                          'country', 'dob', 'doby', 'gen', 'age', 'uid']
        facebook_cus.append(fb_header_item)
        for rec in results:
            item = []
            user = rec.get('user')
            email = user.get('email', '')
            if not email and str(email) == 'None':
                email = ''
            item.append(email)
            item.append(email)
            item.append(email)
            phone = user.get('phone', '')
            if phone and str(phone) != 'None':
                phone = str(phone).lstrip('0')
                phone = '+84' + str(phone)
            else:
                phone = ''
            item.append(phone)
            item.append(phone)
            item.append(phone)
            item.append('')
            name = user.get('name', '')
            if name and len(name) > 0:
                name = api.remove_accents(name).upper()
            item.append(name)
            item.append('')
            item.append('')
            item.append('')
            item.append('')
            item.append('VN')
            item.append('')
            item.append('')
            gender = user.get('gender', '')
            if gender and str(gender) != 'None':
                if gender == '1':
                    item.append('M')
                if gender == '2':
                    item.append('F')
            item.append('')
            item.append('')
            if len(email) > 0 or len(phone) > 0:
                facebook_cus.append(item)
    merchant_name = merchant.get('name')
    merchant_name = api.remove_accents(merchant_name)
    merchant_name = merchant_name.replace("'", "_")
    shop_name = ''
    if shop:
        shop_name = shop.get('name')
        shop_name = api.remove_accents(shop_name)
        shop_name = shop_name.replace("'", "_")
    file_name = 'file_' + str(merchant_name) + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.xlsx'
    if shop_name and len(shop_name) > 0:
        file_name = 'file_' + str(shop_name) + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.xlsx'
    path_file = str(os.getcwd()) + '/static/export_file/%s' % (file_name)
    static_path = '/export_file/%s' % (file_name)

    with xlsxwriter.Workbook(path_file) as workbook:
        worksheet = workbook.add_worksheet()

        for row_num, data in enumerate(list_cus):
            worksheet.write_row(row_num, 0, data)

    with open(path_file) as f:
        file_data = f.read()
        data_logo = {
            'file_name': file_name,
            'file_data': base64.b64encode(file_data),
            'origin_name': file_name,
            'mimetype': 'application/xls'
        }
        storage_api.save_file(data_logo)
        os.remove(path_file)
        api.save_file_export_user(merchant_id, static_path)

    if len(zalo_cus) > 0:
        file_name_zalo = 'zalo_' + str(merchant_name) + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.txt'
        if shop_name and len(shop_name) > 0:
            file_name_zalo = 'zalo_' + str(shop_name) + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.txt'
        path_file_zalo = str(os.getcwd()) + '/static/export_file/%s' % (file_name_zalo)
        static_path_zalo = '/export_file/%s' % (file_name_zalo)
        with open(path_file_zalo, "w") as outfile:
            outfile.write("\n".join(zalo_cus))

        with open(path_file_zalo) as f:
            file_data = f.read()
            data_file_zalo = {
                'file_name': file_name,
                'file_data': base64.b64encode(file_data),
                'origin_name': file_name,
                'mimetype': 'application/txt'
            }
            storage_api.save_file(data_file_zalo)
            os.remove(path_file_zalo)
            api.save_file_export_user(merchant_id, static_path_zalo)

    if len(facebook_cus) > 0:
        facebook_file_name = 'facebook_' + str(merchant_name) + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.csv'
        if shop_name and len(shop_name) > 0:
            facebook_file_name = 'facebook_' + str(facebook_file_name) + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.csv'
        facebook_path_file = str(os.getcwd()) + '/static/export_file/%s' % (facebook_file_name)
        facebook_static_path = '/export_file/%s' % (facebook_file_name)
        with io.open(facebook_path_file, "wb") as f:
            writer = unicodecsv.writer(f, encoding='utf-8')
            writer.writerows(facebook_cus)
        with open(facebook_path_file) as f:
            file_data = f.read()
            data_file_zalo = {
                'file_name': facebook_file_name,
                'file_data': base64.b64encode(file_data),
                'origin_name': facebook_file_name,
                'mimetype': 'application/csv'
            }
            storage_api.save_file(data_file_zalo)
            os.remove(facebook_path_file)
            api.save_file_export_user(merchant_id, facebook_static_path)


def format_price(price):
    price = int(str(price).replace('.00', ''))
    return "{:,}".format(price)


def export_customers_fb(shop_id, from_date=None, to_date=None,
                        min_visit=None, max_visit=None, sort=None,
                        bday_from_date=None, bday_to_date=None,
                        ranks=None, gender=None, min_cash=None,
                        max_cash=None, min_points=None, max_points=None,
                        filter_tags=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    shops = []
    shops.append(shop_id)
    shop = api.get_shop_info(shop_id=shop_id)
    merchant_id = shop.get('merchant_id')
    isHQ = True if merchant_id and merchant_id != '0' else False
    recs = api.list_customers(shops, shop_id, merchant_id, from_date=from_date,
                              to_date=to_date, min_visit=min_visit,
                              max_visit=max_visit, sort=sort,
                              bday_from_date=bday_from_date,
                              bday_to_date=bday_to_date,
                              ranks=ranks,
                              gender=gender,
                              min_cash=min_cash,
                              max_cash=max_cash,
                              min_points=min_points,
                              max_points=max_points,
                              filter_tags=filter_tags,
                              page=None,
                              page_size=settings.ITEMS_PER_PAGE)
    list_cus = []
    header_item = ['Ten', 'Phone', 'Sinh nhat', 'Luot den', 'Gioi tinh', 'Email',
                   'Tich Vi', 'Diem', 'Hang', 'Thoi gian den']
    list_cus.append(header_item)
    for rec in recs:
        item = []
        name = rec.get('name')
        if name and len(name) > 0:
            name = api.remove_accents(name).upper()
        item.append(name)
        item.append(rec.get('phone'))
        item.append(rec.get('birthday'))
        item.append(rec.get('visit_count'))
        item.append(rec.get('gender'))
        item.append(rec.get('email'))
        credit_amount = 0
        if rec.get('credit_amount'):
            credit_amount = rec.get('credit_amount')
        item.append(credit_amount)
        item.append(rec.get('points'))
        item.append(rec.get('rank'))
        item.append(rec.get('local_visit'))
        list_cus.append(item)
    file_name = str(shop_id) + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.csv'
    path_file = str(os.getcwd()) + '/static/export_file/%s' % (file_name)

    with io.open(path_file, "wb") as f:
        writer = unicodecsv.writer(f, encoding='utf-8')
        writer.writerows(list_cus)
    static_path = '/static/export_file/%s' % (file_name)
    api.save_file_export_user(merchant_id, static_path)
    # send_email_export_fb(shop_id, path_file)


def send_email_export_fb(shop_id, path_file):
    s = smtplib.SMTP('smtp.econet.co', 25)
    shop = api.get_shop_info(shop_id=shop_id)
    email_recip = shop.get('email')
    html = """Nextify gửi bạn danh sách khách hàng tại: {} \n""".format(
        shop.get('name')
    )
    html += """Vui lòng tải file đính kèm hoặc download tại đây: <a href="http://crm.nextify.co/{}"/>Download</a>""".format(
        path_file
    )
    msg = MIMEMultipart()
    # msg = MIMEText(html, 'html', 'utf-8')
    s.starttls()
    sender = settings.EMAIL_SENDER
    s.login(settings.EMAIL_SENDER, settings.EMAIL_SENDER_PASS)
    recipients = [email_recip]
    msg['Subject'] = Header(
        "Danh sách khách hàng từ NextifyCRM tại : {} đến {}".format(
            shop.get('name'), time.strftime("%d_%m_%Y_%H_%M_%s")
        ), 'utf-8'
    )
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    with open(path_file, "rb") as fil:
        part = MIMEApplication(fil.read(), Name=basename(path_file))
        part['Content-Disposition'
        ] = 'attachment; filename="%s"' % basename(path_file)
        msg.attach(part)
    s.sendmail(sender, recipients, msg.as_string())


def send_email_export_hq(merchant_id, path_file):
    merchant = api.get_merchant(merchant_id)
    email_recip = merchant.get('email')
    if email_recip and str(email_recip) != 'None':
        s = smtplib.SMTP('smtp.zoho.com', 465)
        html = """Nextify gửi bạn danh sách khách hàng tại: {} \n""".format(
            merchant.get('name')
        )
        html += """Vui lòng tải file đính kèm hoặc download tại đây: <a href="http://crm.nextify.co/{}"/>Download</a>""".format(
            path_file
        )
        msg = MIMEMultipart()
        # msg = MIMEText(html, 'html', 'utf-8')
        s.starttls()
        sender = settings.EMAIL_SENDER
        s.login(settings.EMAIL_SENDER, settings.EMAIL_SENDER_PASS)
        if email_recip:
            recipients = [email_recip]
            merchant = api.get_merchant(merchant_id)
            msg['Subject'] = Header(
                "Khách hàng truy cập WIFI Nextify tại : {} đến {}".format(
                    merchant.get('name'), time.strftime("%d_%m_%Y_%H_%M_%s")
                ), 'utf-8'
            )
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            with open(path_file, "rb") as fil:
                part = MIMEApplication(fil.read(), Name=basename(path_file))
                part['Content-Disposition'
                ] = 'attachment; filename="%s"' % basename(path_file)
                msg.attach(part)
            s.sendmail(sender, recipients, msg.as_string())


def sync_zalo_user(shop_id, zalo_oa_id, zalo_oa_key):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    query = [
        {
            '$match': {
                'shop_id': shop_id,
            }
        }, {
            '$group': {
                "_id": '$user_id',
                'averageIndex': {
                    '$avg': "$index"
                }
            }
        }, {
            '$lookup': {
                "from": "user_zalo_oa",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        }, {
            '$match': {
                "user": {
                    '$eq': []
                }
            }
        }
    ]
    recs = api.DATABASE.visit_log.aggregate(query)
    for rec in recs:
        user = api.get_user_info(user_id=rec['_id'])
        if user:
            zalo_api.update_user_with_zalo(
                user, zalo_oa_id, zalo_oa_key, shop_id
            )

    zalo_api.update_zalo_sync_process(shop_id, 'done')


def export_coupon(merchant_id, shop_id, filter, coupon_type_id, user_phone):
    if filter == 'all':
        coupons = gift_card_api.get_coupon_manual(
            merchant_id=merchant_id,
            shop_id=shop_id,
            is_redeem=False,
            is_map_user=False,
            coupon_type_id=coupon_type_id,
            user_phone=user_phone,
            all=True,
            page=None,
            page_size=settings.ITEMS_PER_PAGE
        )
    elif filter == 'redeem':
        coupons = gift_card_api.get_coupon_manual(
            merchant_id=merchant_id,
            shop_id=shop_id,
            is_redeem=True,
            is_map_user=True,
            coupon_type_id=coupon_type_id,
            user_phone=user_phone,
            all=True,
            page=None,
            page_size=settings.ITEMS_PER_PAGE
        )

    else:
        coupons = gift_card_api.get_coupon_manual(
            merchant_id=merchant_id,
            shop_id=shop_id,
            is_redeem=False,
            is_map_user=True,
            coupon_type_id=coupon_type_id,
            user_phone=user_phone,
            all=True,
            page=None,
            page_size=settings.ITEMS_PER_PAGE
        )
    data_export = []
    item_header = ['Code', 'Phone', 'Loai', 'Prefix', 'Money', 'Discount']
    data_export.append(item_header)
    for coup in coupons:
        item = []
        item.append(coup.get('code'))
        phone = ''
        if coup.get('user_info'):
            phone = coup['user_info']['phone']
        item.append(phone)
        item.append(coup['coupon_type_info']['name'])
        item.append(coup['coupon_type_info']['code'])
        money_exchange = ''
        if coup['coupon_type_info'].get('money_exchange'):
            money_exchange = coup['coupon_type_info'].get('money_exchange')
        discount_percent = ''
        if coup['coupon_type_info'].get('discount_percent'):
            discount_percent = coup['coupon_type_info'].get('discount_percent')
        item.append(money_exchange)
        item.append(discount_percent)
        data_export.append(item)

    file_name = str(shop_id) + '_coupon_' + str(time.strftime("%d_%m_%Y_%H_%M_%s")) + '.csv'
    path_file = str(os.getcwd()) + '/static/export_file/%s' % (file_name)

    with io.open(path_file, "wb") as f:
        writer = unicodecsv.writer(f, encoding='utf-8')
        writer.writerows(data_export)

    send_email_coupons_hq(merchant_id, path_file)


def send_email_coupons_hq(merchant_id, path_file):
    s = smtplib.SMTP('smtp.econet.co', 25)
    merchant = api.get_merchant(merchant_id)
    email_recip = merchant.get('email')
    html = """Danh sách coupons từ Nextify: {} \n""".format(
        merchant.get('name')
    )
    html += """Vui lòng tải file đính kèm hoặc download tại đây: <a href="http://crm.nextify.co/{}"/>Download</a>""".format(
        path_file
    )
    msg = MIMEMultipart()
    # msg = MIMEText(html, 'html', 'utf-8')
    s.starttls()
    sender = settings.EMAIL_SENDER
    s.login(settings.EMAIL_SENDER, settings.EMAIL_SENDER_PASS)
    if not email_recip:
        email_recip = 'tung@nextify.co'
    recipients = [email_recip]
    # recipients = ['tung@wsoft.co', 'tuanvq@wsoft.co', 'thanhdl@wsoft.co']
    merchant = api.get_merchant(merchant_id)
    msg['Subject'] = Header(
        "Danh sách coupons từ Nextify", 'utf-8'
    )
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    with open(path_file, "rb") as fil:
        part = MIMEApplication(fil.read(), Name=basename(path_file))
        part['Content-Disposition'
        ] = 'attachment; filename="%s"' % basename(path_file)
        msg.attach(part)
    s.sendmail(sender, recipients, msg.as_string())


def count_predict_message_campaign(camp_id, merchant_id, shop_id, is_hq):
    total = api.count_total_customer_in_campaign(camp_id,
                                                 merchant_id=merchant_id,
                                                 shop_id=shop_id,
                                                 is_hq=is_hq)

    api.update_sms_camp_predict_message(merchant_id, shop_id, camp_id, total,
                                        is_hq)


def register_fpt_campaign(merchant_id, shop_id, camp_id,
                          user_sms, pass_sms,
                          camp_code, brand_name,
                          message, schedule_time, predict_message):
    campaign_code = api.create_campaign_fpt_gateway(user_sms,
                                                    pass_sms,
                                                    'send_brandname',
                                                    camp_code,
                                                    brand_name,
                                                    message,
                                                    schedule_time,
                                                    predict_message)

    api.update_sms_campaign_hq_fpt(merchant_id, shop_id, camp_id,
                                   campaign_code)


def register_fpt_campaign_shop(merchant_id, shop_id, camp_id,
                               user_sms, pass_sms,
                               camp_code, brand_name,
                               message, schedule_time, predict_message):
    campaign_code = api.create_campaign_fpt_gateway(user_sms,
                                                    pass_sms,
                                                    'send_brandname',
                                                    camp_code,
                                                    brand_name,
                                                    message,
                                                    schedule_time,
                                                    predict_message)

    api.update_sms_campaign_fpt(shop_id, camp_id, campaign_code)
