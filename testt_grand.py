#! coding: utf-8
# import requests
# import os
# import time
# import hashlib
# import json
# from datetime import datetime
# import certifi
# import ssl
# import sendgrid
# from sendgrid.helpers.mail import *
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context
# print "1111111"
# # mail_pass = "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"
# # mail_user = "sonnv@nextify.co"
# mail_pass = "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"
# mail_user = "starbuckswifi@starbucksrewards.com.vn"
# email_test = "nguyenvanson147ah@gmail.com"
# subject = "Xác nhận tài khoản / Verification for Wifi"
# email_content = "<html><body><h2>sdafhdghgriohkfdsfklgoigh</h2></body></html>"
# sg = sendgrid.SendGridAPIClient(api_key=mail_pass)
# from_email = Email(mail_user)
# to_email = To(email_test)
# subject = subject
# content = Content("text/html", email_content)
# mail = Mail(from_email, to_email, subject, content)
# # try:
# print "======================"
# response = sg.client.mail.send.post(request_body=mail.get())
# if response.status_code == 202:
#     print "=====done"
# else:
#     print "=====not done"
# print "------------"
# print response
