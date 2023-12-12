#! coding: utf-8
from flask import Flask
import settings

from flask import (Flask, request, render_template, session, redirect, g,
                   Blueprint, url_for, abort, Response, send_from_directory)
# lib connect mongo
from pymongo import MongoClient
from collections import OrderedDict

#kafka
from kafka import KafkaProducer

app = Flask(__name__)

# connect mongo
MONGODB = MongoClient(
    settings.MONGODB_HOST,
    settings.MONGODB_PORT,
    document_class=OrderedDict,
    maxPoolSize=200,
    serverSelectionTimeoutMS=90000)
DATABASE = MONGODB[settings.MONGODB_NAME]
DATABASE.authenticate(
    settings.MONGODB_USER,
    settings.MONGODB_PASSWORD,
    source=settings.MONGO_NAME_AUTHEN)

# kafka producer
def get_kafka_producer():
    return KafkaProducer(bootstrap_servers=settings.KAFKA_IP + ":9092")

producer = get_kafka_producer()



@app.route('/')
def hello_world():
    package = DATABASE.package.find({})
    return 'Hello, World!'

@app.route('/ex_kafka')
def ex_kafka():
    producer_data = {
        "shop_id": str(loc_id),
        "task_name": "update_customers_all_locations",
        "params": {"merchant_id": str(merchant_id),
                   "user_id": str(user_id)
                   }
    }

    producer_data = json.dumps(producer_data)
    producer.send(settings.cms_consumer, producer_data)
    producer.flush()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8096, debug=True)