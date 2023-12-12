# ! coding: utf-8
from pymongo import MongoClient
from collections import OrderedDict
import os
import requests
import tempfile
import base64
import storage_api

Mongodb = MongoClient(
    '127.0.0.1',
    27017,
    document_class=OrderedDict,
    maxPoolSize=200,
    serverSelectionTimeoutMS=90000)

DATABASE = Mongodb['nextify']
DATABASE.authenticate(
    'develop',
    'g5i4dI8KzYmXs0K',
    source='nextify')

URL_FID = 'http://103.226.250.83:9333/dir/assign'
URL_UPLOAD = 'http://103.226.250.83:8089/'


def move_file(photo):
    img = storage_api.get_file(photo)
    file_data = img.get('file_data')
    file_data = str(file_data)
    file_data = base64.b64decode(str(file_data))
    fid = ''
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(file_data)
            response = requests.get(URL_FID)
            result = response.json()
            fid = result.get('fid')
            url1 = URL_UPLOAD + fid
            headers = {}
            payload = {}
            files = [
                ('file', (photo, open(str(path), 'rb'), 'jpeg'))
            ]
            response1 = requests.post(url1, headers=headers, data=payload, files=files)
            fid = fid.replace(',', '/')
    finally:
        os.remove(path)
    return fid


# surveys = DATABASE.survey_splash_page.find({})
# for survey in surveys:
#     survey_id = survey.get('_id')
#     photo = survey.get('photo')
#     if photo and len(photo) > 0 and len(photo) != 12:
#         photo_conv = move_file(photo)
#         DATABASE.survey_splash_page.update({'_id': survey_id}, {'$set': {'photo': photo_conv}})
