import sys
import time
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import email.message
import requests
import api
import send_activity
from bson.objectid import ObjectId

MAILGUN_DOMAIN = 'services.nextify.vn'
MAILGUN_API_KEY = '657ff353959c84654a97548a31e0baf9-4412457b-64f7c8bf'

import sendgrid
from sendgrid.helpers.mail import *


def send_by_mail_gun(merchant_name, to_obj, subject, email_content, activity_id=None):
    from_obj = '''%s <mailgun@services.nextify.vn>''' % (merchant_name)
    api_url = "https://api.mailgun.net/v3/%s/messages" % (MAILGUN_DOMAIN)
    r = requests.post(
        api_url,
        auth=("api", MAILGUN_API_KEY),
        data={"from": from_obj,
              "to": [to_obj],
              "subject": subject,
              "html": email_content})
    if activity_id:
        if r.status_code == 200:
            send_activity.update_send_activity(activity_id, True)
        else:
            send_activity.update_send_activity(activity_id, False)


def send_by_sendgrid(api_key, from_email, to_emails, subject, content, activity_id=None, camp_id=None, shop_id=None):
    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email(from_email)
    to_email = To(to_emails)
    subject = subject
    content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code == 202:
            if activity_id:
                send_activity.update_send_activity(activity_id, True)
            if camp_id and shop_id:
                if not isinstance(shop_id, ObjectId):
                    camp_id = ObjectId(camp_id)
                if not isinstance(shop_id, ObjectId):
                    shop_id = ObjectId(shop_id)
                api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                  'shop_id': shop_id,
                                                  'email': to_emails},
                                                 {'$set': {'status': 1,
                                                           'update_at': time.time()}})
        else:
            send_activity.update_send_activity(activity_id, False)
            if camp_id and shop_id:
                if not isinstance(shop_id, ObjectId):
                    camp_id = ObjectId(camp_id)
                if not isinstance(shop_id, ObjectId):
                    shop_id = ObjectId(shop_id)
                api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                  'shop_id': shop_id,
                                                  'email': to_emails},
                                                 {'$set': {'status': 2,
                                                           'update_at': time.time()}})

    except Exception as e:
        send_activity.update_send_activity(activity_id, False)
        if camp_id and shop_id:
            if not isinstance(shop_id, ObjectId):
                camp_id = ObjectId(camp_id)
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                              'shop_id': shop_id,
                                              'email': to_emails},
                                             {'$set': {'status': 2,
                                                       'update_at': time.time()}})


def mailgun_service(mail_api_key, mail_api_domain, mail_api_url,
                    merchant_name, to_obj, subject,
                    email_content, activity_id=None, camp_id=None, shop_id=None):
    from_obj = '''%s <mailgun@%s>''' % (merchant_name, mail_api_domain)
    r = requests.post(
        mail_api_url,
        auth=("api", mail_api_key),
        data={"from": from_obj,
              "to": [to_obj],
              "subject": subject,
              "html": email_content})
    if r.status_code == 200:
        if activity_id:
            send_activity.update_send_activity(activity_id, True)
        if camp_id and shop_id:
            if not isinstance(shop_id, ObjectId):
                camp_id = ObjectId(camp_id)
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                              'shop_id': shop_id,
                                              'email': to_obj},
                                             {'$set': {'status': 1,
                                                       'update_at': time.time()}})
    else:
        if activity_id:
            send_activity.update_send_activity(activity_id, False)
        if camp_id and shop_id:
            if not isinstance(shop_id, ObjectId):
                camp_id = ObjectId(camp_id)
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                              'shop_id': shop_id,
                                              'email': to_obj},
                                             {'$set': {'status': 2,
                                                       'update_at': time.time()}})


def send_mail_smtp(mail_server, mail_port, mail_user, mail_pass,
                   subject, recipients, mail_content, activity_id=None, camp_id=None, shop_id=None):
    try:
        if mail_server == 'smtp.gmail.com':
            mail_port = 587
        # msg = email.message.Message()
        # msg['Subject'] = subject
        # msg['From'] = mail_user
        # msg['To'] = recipients
        # msg.add_header('Content-Type', 'text/html')
        # msg.set_payload(mail_content)
        # s = smtplib.SMTP_SSL(mail_server, int(mail_port))
        # s.ehlo()
        # s.login(str(mail_user), str(mail_pass))
        # s.sendmail(mail_user, recipients, msg.as_string())
        # s.close()
        msg = MIMEMultipart()
        msg['From'] = mail_user
        msg['To'] = ', '.join([recipients])
        msg['Subject'] = subject
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(mail_content)

        server = smtplib.SMTP(mail_server, int(mail_port))
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, [recipients], msg.as_string())
        server.close()

        if activity_id:
            send_activity.update_send_activity(activity_id, True)
        if camp_id and shop_id:
            if not isinstance(shop_id, ObjectId):
                camp_id = ObjectId(camp_id)
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                              'shop_id': shop_id,
                                              'email': recipients},
                                             {'$set': {'status': 1,
                                                       'update_at': time.time()}}
                                             )
    except:
        if activity_id:
            send_activity.update_send_activity(activity_id, False)
        if camp_id and shop_id:
            if not isinstance(shop_id, ObjectId):
                camp_id = ObjectId(camp_id)
            if not isinstance(shop_id, ObjectId):
                shop_id = ObjectId(shop_id)
            api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                              'shop_id': shop_id,
                                              'email': recipients},
                                             {'$set': {'status': 2, 'update_at': time.time()}})


def count_email_logs_by_status(shop_id, camp_id, status):
    if not isinstance(shop_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    return api.DATABASE.campaign_log.find({'camp_id': camp_id,
                                           'shop_id': shop_id,
                                           'status': status}).count()


def send_email_nextify(merchant, subject, mail_content, recipients, activity_id):
    mail_settings = merchant.get('mail_settings')
    mail_name = mail_settings.get('mail_name')
    mail_user = mail_settings.get('mail_user')
    mail_pass = mail_settings.get('mail_pass')
    mail_server = mail_settings.get('mail_server')
    mail_port = mail_settings.get('mail_port')
    mail_ssl = mail_settings.get('mail_ssl')
    merchant_name = merchant.get('name', '')
    if len(mail_user) > 1 and len(mail_pass) > 1 and len(
            mail_server) > 1:
        if 'nextify' in mail_server or 'mail_gun' in mail_server:
            mailgun_service(mail_pass, mail_user, mail_server,
                            merchant_name, recipients, subject,
                            mail_content, activity_id)
        else:
            send_mail_smtp(mail_server, mail_port, mail_user, mail_pass,
                           subject, recipients, mail_content, activity_id)


def get_email_data_camp(merchant_id, camp_id, shop_id):
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    customers_sources = camp.get('customers_sources')
    list_cus = []
    if customers_sources == "on":
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       is_email=True)

    else:
        from_date = camp.get('visit_from_date')
        to_date = camp.get('visit_to_date')
        min_visit = camp.get('min_visit')
        max_visit = camp.get('max_visit')
        lost_day = camp.get('lost_day')
        bday_from_date = camp.get('b_day_from_date')
        bday_to_date = camp.get('b_day_to_date')
        gender = camp.get('gender')
        filter_tags = camp.get('tags')
        list_cus = api.filter_campaign(merchant_id,
                                       shop_id=shop_id,
                                       from_date=from_date,
                                       is_email=True,
                                       to_date=to_date,
                                       min_visit=min_visit,
                                       max_visit=max_visit,
                                       lost_day=lost_day,
                                       gender=gender,
                                       bday_from_date=bday_from_date,
                                       bday_to_date=bday_to_date,
                                       tags_array=filter_tags)
    if len(list_cus) > 0:
        for cus in list_cus:
            user = cus.get('user')
            if user:
                email = user.get('email')
                name = user.get('name', '')
                user_id = user.get('_id')
                if name and len(name) > 0 and str(name) == 'None':
                    name = ''
                if email and len(email) > 0 and str(email) != 'None':
                    if not isinstance(camp_id, ObjectId):
                        camp_id = ObjectId(camp_id)
                    if not isinstance(shop_id, ObjectId):
                        shop_id = ObjectId(shop_id)
                    if not isinstance(user_id, ObjectId):
                        user_id = ObjectId(user_id)
                    check_log_email_camp = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                               'shop_id': shop_id,
                                                                               'email': email})
                    if not check_log_email_camp:
                        api.DATABASE.campaign_log.insert({
                            'camp_id': camp_id,
                            'shop_id': shop_id,
                            'email': email,
                            'name': name,
                            'user_id': user_id,
                            'status': 0
                        })
                    else:
                        api.DATABASE.campaign_log.update({'camp_id': camp_id,
                                                          'shop_id': shop_id,
                                                          'email': email,
                                                          'user_id': user_id},
                                                         {'$set': {'name': name}})


def send_email_campaign(merchant_id, camp_id, shop_id):
    if not isinstance(shop_id, ObjectId):
        camp_id = ObjectId(camp_id)
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    merchant = api.get_merchant(merchant_id)
    camp = api.get_sms_campaign_hq(merchant_id, camp_id, shop_id=shop_id)
    if merchant and camp:
        email_content = camp.get('email_content')
        email_title = camp.get('email_title')
        if email_title and len(email_title) > 0 and len(email_content) > 0:
            email_logs = api.DATABASE.campaign_log.find({
                'camp_id': camp_id,
                'shop_id': shop_id,
                'status': 0
            })
            for email_log in email_logs:
                email = email_log.get('email')
                name = email_log.get('name')
                user_id = email_log.get('user_id')

                if email and len(email) > 0:
                    mail_settings = merchant.get('mail_settings')
                    mail_name = mail_settings.get('mail_name')
                    mail_user = mail_settings.get('mail_user')
                    mail_pass = mail_settings.get('mail_pass')
                    mail_server = mail_settings.get('mail_server')
                    mail_port = mail_settings.get('mail_port')
                    mail_ssl = mail_settings.get('mail_ssl')
                    merchant_name = merchant.get('name', '')
                    if name and len(name) > 0 and str(name) != 'None':
                        email_content = email_content.replace('{{ name }}', name)
                        email_title = email_title.replace('{{ name }}', name)
                    if len(mail_user) > 1 and len(mail_pass) > 1 and len(
                            mail_server) > 1:
                        check_is_log = api.DATABASE.campaign_log.find_one({'camp_id': camp_id,
                                                                           'shop_id': shop_id,
                                                                           'email': email})
                        status = check_is_log.get('status')
                        if status == 0:
                            if 'nextify' in mail_server or 'mail_gun' in mail_server:
                                mailgun_service(mail_pass, mail_user, mail_server,
                                                merchant_name, email, email_title,
                                                email_content, activity_id=None, camp_id=camp_id, shop_id=shop_id)
                            elif 'sendgrid' in mail_server:  # Use SendGrid service
                                send_by_sendgrid(mail_pass, mail_user, email, email_title, email_content,
                                                 activity_id=None, camp_id=camp_id, shop_id=shop_id)
                            else:
                                send_mail_smtp(mail_server, mail_port, mail_user, mail_pass,
                                               email_title, email, email_content, activity_id=None, camp_id=camp_id,
                                               shop_id=shop_id)
                            send_activity.insert_send_activity(merchant_id, shop_id, user_id, 'email',
                                                               email_title, 'campaign', camp_id)
    api.update_shop_camp_status(shop_id, camp_id, 2)


def list_email_logs(shop_id, camp_id, page=None, page_size=None):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return api.DATABASE.campaign_log.find({'camp_id': camp_id,
                                           'shop_id': shop_id,
                                           'status': {'$in': [1, 2]}}).sort('update_at', -1).skip(
        page_size * (page - 1)).limit(
        page_size)


def total_list_email_logs(shop_id, camp_id):
    if not isinstance(shop_id, ObjectId):
        shop_id = ObjectId(shop_id)
    if not isinstance(camp_id, ObjectId):
        camp_id = ObjectId(camp_id)
    return api.DATABASE.campaign_log.find({'camp_id': camp_id,
                                           'shop_id': shop_id,
                                           'status': {'$in': [1, 2]
                                                      }}).count()
