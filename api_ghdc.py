#! coding: utf-8
import requests
import json
import os
import settings

# GHDC_domain = settings.GHDC_domain
GHDC_domain = settings.GHDC_domain_test
def get_token(username, password):
    url = GHDC_domain + "controller/login?username={}&password={}".format(username, password)
    print("============url")
    print(url)
    payload={}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)
    print("---------res")
    print(response)
    res = response.json()
    code = res.get("code")
    data = json.loads(res.get("data"))
    token = data.get("api_token")
    org_id = data.get('org_id')
    return token, org_id

def createcamp(token, org_id, cp_name, start_datetime, end_datetime, sending_time, next_sending_time, alias, cp_type, mt_type, max_mt_per_day, max_mt_campaign, description, career):
    url =  GHDC_domain + "controller/createCampaign?token={}&org_id={}&cp_name={}&start_datetime={}&end_datetime={}&sending_time={}&next_sending_time={}&alias={}&cp_type={}&mt_type={}&max_mt_per_day={}&max_mt_campaign={}&description={}&career={}".format(token, org_id, cp_name, start_datetime, end_datetime, sending_time, next_sending_time, alias, cp_type, mt_type, max_mt_per_day, max_mt_campaign, description, career)   
    payload={}
    headers = {}   
    response = requests.request("POST", url, headers=headers, data=payload)
    res = response.json()
    code = res.get("code")
    cp_id = None
    if str(code) == "0":
        data = json.loads(res.get('data'))
        cp_id = data.get('cp_id')
    return cp_id


def create_tempSMS(token, cp_id, content, type_sms, price, brandname):
    temp_id = None
    url = GHDC_domain + "controller/createSMSTemp?token={}&cp_id={}&content={}&type={}&price={}&channel={}".format(token, cp_id, content, type_sms, price, brandname)
    payload={}
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    res = response.json()
    code = res.get("code")
    if str(code) == "0":
        temp_id = res.get('tempId')
    return temp_id

def get_career(token):
    list_career = []
    url = GHDC_domain + 'controller/viewCareerConfig?token={}'.format(token)
    payload={}
    headers = {}
    response = requests.post(url, headers=headers, data=payload)
    res = response.json()
    code = res.get("code")
    if str(code) == "0":
        data = json.loads(res.get('data'))
        for dat in data:
            career = dat.get('career')
            list_career.append(career)

    return list_career


# def add_phone_file_to_camp(cp_id, username, password): 
def add_phone_file_to_camp(cp_id, token):
    url = GHDC_domain + "controller/addMsisdnFileToCP?token={}&cp_id={}".format(token, cp_id)
    path_file = str(os.getcwd()) + '/static/sdttest.txt'
    payload={}
    files=[
        ('content',('sdttest.txt',open(path_file,'rb'),'text/plain'))
    ]
    headers = {}

    response = requests.post(url, headers=headers, data=payload, files=files)
    res = response.json()
    code = res.get("code")
