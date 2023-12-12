#! coding: utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import requests
from pymongo import MongoClient
from collections import OrderedDict, defaultdict
from bson.objectid import ObjectId
import json

MONGODB_NAME = 'nextify'
MONGODB_HOST = os.getenv('MONGODB_HOST', '171.244.57.184')
MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
MONGODB_USER = 'develop'
MONGODB_PASSWORD = 'g5i4dI8KzYmXs0K'
MONGO_NAME_AUTHEN = 'nextify'

MONGODB = MongoClient(
    MONGODB_HOST,
    MONGODB_PORT,
    document_class=OrderedDict,
    maxPoolSize=200,
    serverSelectionTimeoutMS=90000)
DATABASE = MONGODB[MONGODB_NAME]
DATABASE.authenticate(
    MONGODB_USER,
    MONGODB_PASSWORD,
    source=MONGO_NAME_AUTHEN)

def login(user_name, pass_word):
    username = driver.find_elements_by_xpath('//input[@placeholder="Email/Login name"]'); 
    password = driver.find_elements_by_xpath('//input[@placeholder="Password"]'); 
    username[0].send_keys(user_name)
    password[0].send_keys(pass_word)
    print "----------logins"
    driver.find_element_by_class_name("cookiescript_reject").click() 
    driver.find_element_by_class_name("signInSubmit").click() 

def craw_ap(name_network):
    print "------------------aos"
    click_ap = driver.find_elements_by_xpath("//a[text()='Access Points']")
    click_ap[0].click()
    time.sleep(3)
    click_status = driver.find_elements_by_xpath("//li[contains(text(), 'Status')]")
    click_status[0].click()
    time.sleep(3)
    list_mac = []
    for row in driver.find_elements_by_css_selector("tr.el-table__row"):
        print "---------"
        cells = row.find_elements_by_tag_name("td")
        contacts = cells[0].find_elements_by_xpath(".//div[contains(@title, 'Online')]/span")
        active = 'apStatus apOffline'
        for contact in contacts:
            active = contact.get_attribute("class")
        model = cells[1].text
        mac = cells[2].text
        name = cells[3].text
        ip_address = cells[4].text
        firmware = cells[5].text
        uptime = cells[6].text
        clients = cells[8].text
        save_grandstream(mac, name_network, active=active, model=model, name=name, ip_address=ip_address, firmware=firmware, uptime=uptime, clients=clients)
        list_mac.append(mac.lower())
        pass
    remove_mac_network(name_network, list_mac)

def find_and_crawl_ap():
    time.sleep(3)
    click_net = driver.find_elements_by_xpath("//span[text()='Network']")
    click_net[0].click()
    sub_nets = driver.find_elements_by_class_name("networks")
    for sub in sub_nets:
        name_network = sub.text
        network_gr = save_grandstream_network(name_network)
        sub.click() 
        print "111111111"
        time.sleep(2)
        # click_net = driver.find_elements_by_xpath("//span[text()='Network']")
        print "222222222"
        # click_net[0].click()
        print "44444444444"
        craw_ap(network_gr)
        time.sleep(3)
        find_summary_clients(network_gr)
        time.sleep(3)
        click_net = driver.find_elements_by_xpath("//span[text()='Network']")
        print "222222222"
        click_net[0].click()
        time.sleep(2)
def save_grandstream(mac, network, active=None, model=None, name=None, ip_address=None, firmware=None, uptime=None, clients=None):
    info = {}
    mac = mac.lower()
    info['mac'] = mac.lower()
    if not isinstance(network, ObjectId):
        network = ObjectId(network)
    info['network'] = network
    if active and active == "apStatus apOnline":
        info['active'] = True
    if model:
        info['model'] = model
    if name:
        info['name'] = name
    if ip_address:
        info['ip_address'] = ip_address
    if firmware:
        info['firmware'] = firmware
    if uptime:
        info['uptime'] = uptime
    if clients:
        info['clients'] = clients
    check = DATABASE.grandstream.find_one({'mac': mac})
    if check:
        DATABASE.grandstream.update({'mac': mac}, {'$set': info})
    else:
        DATABASE.grandstream.insert(info)

def remove_mac_network(name_network, list_mac):
    DATABASE.grandstream.remove({'network': name_network, 'mac': { '$nin': list_mac}})

def save_grandstream_network(name_network):
    check = DATABASE.network_grandstream.find_one({'name': name_network})
    if check:
        return check.get('_id')
    else:
        return DATABASE.network_grandstream.insert({'name': name_network})

def find_summary_clients(network_gr):
    str_cookie = ""
    val_AWSELBCORS = ""
    val_AWSELB = ""
    val_SESSION = ""
    time.sleep(3)
    click_ap = driver.find_elements_by_xpath("//a[text()='Clients']")
    click_ap[0].click()
    time.sleep(3)
    click_status = driver.find_elements_by_xpath("//li[contains(text(), 'Summary')]")
    click_status[2].click()
    time.sleep(3)
    all_cookies=driver.get_cookies()
    for co in all_cookies:
        name = co.get('name')
        if name == "SESSION":
            val_SESSION = co.get('value')
        if name == "AWSELBCORS":
            val_AWSELBCORS = co.get('value')
        if name == "AWSELB":
            val_AWSELB = co.get('value')
        str_cookie = "AWSELB=" + val_AWSELB + ";AWSELBCORS=" + val_AWSELBCORS + ";SESSION=" + val_SESSION
        print "======"
        print str_cookie
        print network_gr
        integrated(network_gr, str_cookie)
        bandwidth(network_gr, str_cookie)
        pie(network_gr, str_cookie)

def integrated(network_gr, cookie):
    try:
        url = "https://www.gwn.cloud/app/client/statistics/integrated"
        headers = {
            "Content-Type": "application/json",
            "Cookie": cookie
        }
        data = {
            "ssidId": "all_ssid",
            "type": 1
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        response = json.loads(response.text)
        retCode = response.get('retCode')
        if retCode == 0:
            print "22222222s"
            data = response.get('data')
            returnNum = data.get('returnNum')
            newNum = data.get('newNum')
            totalNum = data.get('totalNum')
            avgDuration = data.get('avgDuration')
            save_overview(network_gr, newNum=newNum, returnNum=returnNum, totalNum=totalNum, avgDuration=avgDuration)
    except:
        pass
def bandwidth(network_gr, cookie):
    try:
        url = "https://www.gwn.cloud/app/statistics/bandwidth"
        headers = {
            "Content-Type": "application/json",
            "Cookie": cookie
        }
        data = {
            "ssidId": "all_ssid",
            "type": 1
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        response = json.loads(response.text)
        retCode = response.get('retCode')
        if retCode == 0:
            data = response.get('data')
            rxTotal = data.get('rxTotal')
            txTotal = data.get('txTotal')
            downrate = float(int(rxTotal)/1074000000)
            uprate = float(int(txTotal)/1074000000)
            save_overview(network_gr, downrate=downrate, uprate=uprate)

    except:
        pass

def pie(network_gr, cookie):
    try:
        url = "https://www.gwn.cloud/app/client/statistics/pie"
        headers = {
            "Content-Type": "application/json",
            "Cookie": cookie
        }
        data = {
            "ssidId": "all_ssid",
            "type": 1
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        response = json.loads(response.text)
        retCode = response.get('retCode')
        if retCode == 0:
            data = response.get('data')
            manufacture = data.get('manufacture')
            samsung = 0
            apple = 0
            xiaomi = 0
            oppo = 0
            other_man = 0
            categories_man = manufacture.get('categories')
            for cate in categories_man:
                name_man = cate.get("name")
                if name_man == "SAMSUNG":
                    samsung = float(cate.get("value"))
                elif name_man == "APPLE":
                    apple = float(cate.get("value"))
                elif name_man == "XIAOMI":
                    xiaomi = float(cate.get("value"))
                elif name_man == "OPPO":
                    oppo = float(cate.get("value"))
            other_man = 100 - samsung - apple - xiaomi - oppo
            os = data.get('os')
            Windows = 0
            Android = 0
            macOS = 0
            Linux = 0
            IOS = 0
            other_os = 0
            categories_os = os.get('categories')
            for cate in categories_os:
                name_os = cate.get("name")
                if name_os == "Windows":
                    Windows = float(cate.get("value"))
                elif name_os == "Android":
                    Android = float(cate.get("value"))
                elif name_os == "macOS":
                    macOS = float(cate.get("value"))
                elif name_os == "IOS":
                    IOS = float(cate.get("value"))
                elif name_os == "Linux":
                    Linux = float(cate.get("value"))
            other_os = 100 - Windows - Android - macOS - Linux - IOS

            save_overview(network_gr, samsung=samsung, apple=apple, xiaomi=xiaomi, oppo=oppo, other_man=other_man, Windows=Windows, Android=Android, macOS=macOS, IOS=IOS, Linux=Linux, other_os=other_os)
    except:    
        pass
def save_overview(network, newNum=None, returnNum=None, totalNum=None, avgDuration=None, downrate=None, uprate=None,
                    samsung=None, apple=None, xiaomi=None, oppo=None, other_man=None, Windows=None, Android=None, macOS=None, IOS=None, Linux=None, other_os=None):
    if not isinstance(network, ObjectId):
        network = ObjectId(network)
    info = {}
    if newNum:
        info['newNum'] = int(newNum)
    if returnNum:
        info['returnNum'] = int(returnNum)
    if totalNum:
        info['totalNum'] = int(totalNum)
    if returnNum:
        info['avgDuration'] = int(avgDuration)
    if downrate:
        info['downrate'] = downrate
    if uprate:
        info['uprate'] = uprate
    if samsung:
        info['samsung'] = samsung
    if apple:
        info['apple'] = apple
    if xiaomi:
        info['xiaomi'] = xiaomi
    if oppo:
        info['oppo'] = oppo
    if other_man:
        info['other_man'] = other_man
    if Windows:
        info['Windows'] = Windows
    if Android:
        info['Android'] = Android
    if macOS:
        info['macOS'] = macOS
    if IOS:
        info['IOS'] = IOS
    if Linux:
        info['Linux'] = Linux
    if other_os:
        info['other_os'] = other_os
    print "--------------------999999999s"
    check_exists = DATABASE.grandstream_overview.find_one({'network': network })
    if check_exists:
        DATABASE.grandstream_overview.update({'network': network }, {'$set': info})
    else:
        info['network'] = network
        DATABASE.grandstream_overview.insert(info)

user_name = 'admin'
pass_word = '861812abcA@'
driver = webdriver.Chrome(executable_path = '/usr/bin/chromedriver')
try:
    print "---------in try"
    driver.get("https://grandstream.nextify.vn:8443/login")
    # time.sleep(3)
    print "--------------loading...."
    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '.signInSubmit'))
    WebDriverWait(driver, 10).until(element_present)
    time.sleep(3)
    login(user_name, pass_word)
    time.sleep(3)
    # find_summary_clients()
    find_and_crawl_ap()
except Exception as e:
    print "Timed out waiting for page to load"
    print e
