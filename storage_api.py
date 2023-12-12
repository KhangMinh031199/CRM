import psycopg2
import requests
import os
import settings
import tempfile
import base64
from PIL import Image
from io import BytesIO
import unidecode

DB_NAME = 'storage'
USER_DB = 'postgres'
PASS_DB = '@aicungbiet89@'
HOST_DB = '127.0.0.1'

CONN_STR = '''dbname={} user={} password={} host={}'''.format(DB_NAME, USER_DB, PASS_DB, HOST_DB)

URL_FID = 'http://125.212.225.71:9333/dir/assign'
URL_UPLOAD = 'http://125.212.225.71:8089/'

def save_file(data):
    file_name = data.get('file_name')
    file_data = data.get('file_data').decode("utf-8") 
    origin_name = data.get('origin_name')
    return_id = ''
    try:
        conn = psycopg2.connect(CONN_STR)
        cur = conn.cursor()

        cur.execute("SELECT id FROM files WHERE file_name={}".format("'" + file_name + "'"))
        file = cur.fetchone()
        if not file or len(file) == 0:
            query = '''INSERT INTO files (orig_filename, file_name, file_data) VALUES ({}, {},{}) RETURNING id'''.format(
                "'" + origin_name + "'","'" + file_name + "'","'" + file_data + "'"
            )
            cur.execute(query)
            return_id = cur.fetchone()[0]
            conn.commit()
        cur.close()
        conn.close()

        print('done')

    except Exception as e:
        print(e)
    return return_id

def save_new_file(data):
    fid = ''
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'wb') as tmp:
            file_data = data.stream.read()
            tmp.write(file_data)
            response = requests.get(URL_FID)
            result = response.json()
            fid = result.get('fid')
            url1 = URL_UPLOAD + fid
            headers = {}
            payload={}
            files=[
                ('file',(str(data.filename),open(str(path),'rb'),data.content_type))
            ]
            response1 = requests.post(url1, headers=headers, data=payload, files=files)
            fid = fid.replace(',', '/')
    finally:
        os.remove(path)
    print(fid)    
    return fid

def save_new_file_init(path):
    fid = ''
    response = requests.get(URL_FID)
    result = response.json()
    fid = result.get('fid')
    url1 = URL_UPLOAD + fid
    headers = {}
    payload={}
    files=[
        ('file',('default',open(str(path),'rb'),'jpg'))
    ]
    response1 = requests.post(url1, headers=headers, data=payload, files=files)
    fid = fid.replace(',', '/')
    return fid

def get_file_name(name):
    return_id = ''
    conn = psycopg2.connect(CONN_STR)
    cur = conn.cursor()
    cur.execute("SELECT file_name FROM files WHERE file_name={}".format("'" + name + "'"))
    two = cur.fetchone()
    if two:
        return_id = two[0]
    cur.close()
    conn.close()
    return return_id


def get_file(file_name):
    orig_filename = ''
    file_data = ''
    file_id = ''
    try:
        conn = psycopg2.connect(CONN_STR)
        cur = conn.cursor()
        cur.execute("SELECT id, file_data, orig_filename, file_name FROM files WHERE file_name={}".format("'"+file_name+"'"))
        (file_id, file_data, orig_filename, file_name) = cur.fetchone()
        cur.close()
        conn.close()

    except Exception as e:
        print(e)

    return {
        'id': file_id,
        'file_name': file_name,
        'orig_filename': orig_filename,
        'file_data': file_data
    }
# save_new_file()
# path = 'http://files.nextify.vn/1,18b0345b1d'
# check = os.path.islink(path)
# print "-----"
# print check
# a = len('1,18b0345b1d')
# print a


