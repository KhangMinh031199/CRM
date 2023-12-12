#!/bin/bash

#ln -s /usr/bin/python /usr/local/bin/python
#/root/.local/bin/pybabel compile -d translations .
#/root/.local/bin/pybabel update -i translations.pot -d translations

/root/.local/bin/uwsgi --protocol=http --socket 0.0.0.0:8096 --enable-threads --module new_cms:app --ini uwsgi.ini
#/root/.local/bin/uwsgi --protocol=http --enable-threads --workers 4 --gevent 100 --socket  0.0.0.0:8096 --module new_cms:app
