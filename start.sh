#!/bin/sh
# cp ./config/config.yml ./config.yml
# python3 manage.py makemigrations ums rms rdts
python3 manage.py migrate
python3 manage.py createcachetable
python3 manage.py schedule &
python3 manage.py webhook &
python3 manage.py create &
python3 manage.py runserver 80

#uwsgi --ini uwsgi.ini
