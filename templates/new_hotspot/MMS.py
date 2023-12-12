#! coding: utf-8
import requests
import json
def login(username, password):
    url = "http://125.212.226.74:8888/mmsapi/controller/login?username={}&password={}".format(username, password)

    payload={}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)
    res = response.json()
    print "======"
    print response.status_code
    print res
    # code = res.get("code")
    # data = json.loads(res.get("data"))
    # token = data.get("api_token")
    # return token


# login(username, password)

def createcamp(token, org_id, cp_name, start_datetime, end_datetime, sending_time, next_sending_time, alias, cp_type, mt_type, max_mt_per_day, max_mt_campaign, description, career):
    url = "http://125.212.226.74:8888/mmsapi/controller/createCampaign?token={}&org_id={}&cp_name={}&start_datetime={}&end_datetime={}&sending_time={}&next_sending_time={}&alias={}&cp_type={}&mt_type={}&max_mt_per_day={}&max_mt_campaign={}&description={}&career={}".format(token, org_id, cp_name, start_datetime, end_datetime, sending_time, next_sending_time, alias, cp_type, mt_type, max_mt_per_day, max_mt_campaign, description, career)
    print(url)
    
    payload={}
    headers = {}
    
    response = requests.request("POST", url, headers=headers, data=payload)
    res = response.json()
    code = res.get("code")
    print(code)
    


token = "eyJ0eXAiOiJKV1MiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxNzQiLCJpYXQiOjE2NDE1MjMwNTQsInN1YiI6Ik1NUyIsImlzcyI6Ik1NUyIsInVzZXJfbmFtZSI6ImhpZXV0ZXN0IiwicGFzc3dkIjoiJDJ5JDEwJFQvM1ZkL3F1b2dwQW9GV3FiMDB2OE94OVJIWFdNTXNLVGl4THRVWGJ1bkpIWlZVdDZMNmQuIiwicm9sZSI6IjMiLCJzdGF0dXMiOiIxIiwib3JnX2lkIjoiMTAwIiwiZGVzY3JpcHRpb25zIjoibnVsbCIsIm93biI6IjE2NiIsIndhbGxldF9pZCI6IjIiLCJ3YWxsZXRfcGFzc3dkIjoiMTIzZHVvbmdsdHQxIiwid2FsbGV0X3R5cGUiOiIxIiwid2FsbGV0X2Rlc2MiOiJnaGRfbW1zIiwidXVpZCI6ImYyN2EyZWM1LTk3ZDMtNDcyMy05MTUwLWU2ZDAxY2U1MTc0MSIsImNyZWF0ZWQiOjE2NDE1MjMwNTQ3OTQsImV4cCI6MTY0MTYwOTQ1NH0.pEVkqkL34ZA-QcKypZfLQe8noD5h8m_dX2O3y7RmO8k"
org_id = 100
cp_name = "Campaignhahahaha"
start_datetime = "2022-1-7 9:50:00"
end_datetime = "2022-1-7 19:00:00"
sending_time = '["16:00-16:30", "18:00-20:00"]'
next_sending_time = "2022-11-8 00:00:00"
alias = 1221
cp_type = 1
mt_type = 1
max_mt_per_day = 100
max_mt_campaign = 100
description = "Nội dung mô tả"
career = "tech"

# createcamp(token, org_id, cp_name, start_datetime, end_datetime, sending_time, next_sending_time, alias, cp_type, mt_type, max_mt_per_day, max_mt_campaign, description, career)

def addMsisdn(token, cp_id, condition):
    url = "http://125.212.226.74:8888/mmsapi/controller/addMsisdnConditionToCP?token={}&cp_id={}&condition={}".format(token, cp_id, condition)
    
    payload={}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)
    res = response.json()
    code = res.get('code')
    print(code)

token = "eyJ0eXAiOiJKV1MiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxNzQiLCJpYXQiOjE2NDE1MjMwNTQsInN1YiI6Ik1NUyIsImlzcyI6Ik1NUyIsInVzZXJfbmFtZSI6ImhpZXV0ZXN0IiwicGFzc3dkIjoiJDJ5JDEwJFQvM1ZkL3F1b2dwQW9GV3FiMDB2OE94OVJIWFdNTXNLVGl4THRVWGJ1bkpIWlZVdDZMNmQuIiwicm9sZSI6IjMiLCJzdGF0dXMiOiIxIiwib3JnX2lkIjoiMTAwIiwiZGVzY3JpcHRpb25zIjoibnVsbCIsIm93biI6IjE2NiIsIndhbGxldF9pZCI6IjIiLCJ3YWxsZXRfcGFzc3dkIjoiMTIzZHVvbmdsdHQxIiwid2FsbGV0X3R5cGUiOiIxIiwid2FsbGV0X2Rlc2MiOiJnaGRfbW1zIiwidXVpZCI6ImYyN2EyZWM1LTk3ZDMtNDcyMy05MTUwLWU2ZDAxY2U1MTc0MSIsImNyZWF0ZWQiOjE2NDE1MjMwNTQ3OTQsImV4cCI6MTY0MTYwOTQ1NH0.pEVkqkL34ZA-QcKypZfLQe8noD5h8m_dX2O3y7RmO8k"
cp_id = 6245
condition = {"param":{"gender":"1","endValue":"value2","operator":"2,2"}}

# addMsisdn(token, cp_id, condition)

def addfilemsisdn(token, cp_id): 
    url = "http://125.212.226.74:8888/mmsapi/controller/addMsisdnFileToCP?token={}&cp_id={}".format(token, cp_id)

    payload={}
    files=[
    ('content',('sdt.txt',open('C:\Users\Dell Inspiron 5570\OneDrive\Máy tính\Python_coban\sdt.txt','rb'),'text/plain'))
    ]
    headers = {
    'Content-Type': 'multipart/form-data'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    res = response.json()
    code = res.get("code")
    print(code)

token = "eyJ0eXAiOiJKV1MiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxNzQiLCJpYXQiOjE2NDE4ODM5NzEsInN1YiI6Ik1NUyIsImlzcyI6Ik1NUyIsInVzZXJfbmFtZSI6ImhpZXV0ZXN0IiwicGFzc3dkIjoiJDJ5JDEwJFQvM1ZkL3F1b2dwQW9GV3FiMDB2OE94OVJIWFdNTXNLVGl4THRVWGJ1bkpIWlZVdDZMNmQuIiwicm9sZSI6IjMiLCJzdGF0dXMiOiIxIiwib3JnX2lkIjoiMTAwIiwiZGVzY3JpcHRpb25zIjoibnVsbCIsIm93biI6IjE2NiIsIndhbGxldF9pZCI6IjIiLCJ3YWxsZXRfcGFzc3dkIjoiMTIzZHVvbmdsdHQxIiwid2FsbGV0X3R5cGUiOiIxIiwid2FsbGV0X2Rlc2MiOiJnaGRfbW1zIiwidXVpZCI6IjZhYTU3MjZmLWM0ZDQtNDBlZS05OGUwLTk5Yjc4NDdjOTkzYyIsImNyZWF0ZWQiOjE2NDE4ODM5NzE2MTMsImV4cCI6MTY0MTk3MDM3MX0.SymdtPhVsBHeh0R-uZv8G9AXUlNRAN0Y8GWMYO6Q75Q"
cp_id = 6249

# addfilemsisdn(token, cp_id)


def createTempMMS():
    username = 'Testdaily02'
    password = 'Admin@123'
    token = login(username, password)
    print token
    subject = 'campaign_test'
    url = "http://125.212.226.74:8888/mmsapi/controller/createTemplateMMS"

    payload={
        'token': token,
        'subject': 'Chiến Dịch Quảng Cáo Thu Đông',
        'type': '1',
        'mmstype': '0',
        'params': '',
        'catid': 'tc_01',
        'cp_id': '6253'
    }
    files=[
        ('content',('bg_bvnn.jpg',open('/Users/nguyenson/Desktop/bg_bvnn.jpg','rb'),'image/jpeg')),
        ('content',('requirements.txt',open('/Users/nguyenson/Downloads/requirements.txt','rb'),'text/plain'))
    ]
    headers = {
        'Content-Type': 'multipart/form-data' 
    }
    response = requests.post( url, headers=headers, data=payload, files=files)

    print response.status_code
    print response

# createTempMMS()


def getCarrer():
    username = 'Testdaily02'
    password = 'Admin@123'
    token = login(username, password)
    url = "http://125.212.226.74:8888/mmsapi/controller/viewCareerConfig?token={}".format(token)
    payload={}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload)

    result = response.json()
    data = json.loads(result.get('data'))

    print type(data)
    for dat in data:
        print "==============="
        print dat.get('career')

username = 'Testdaily02'
password = 'Admin@12'
login(username, password)
