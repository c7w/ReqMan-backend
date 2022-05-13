#!/bin/sh
cp ./config/config.yml ./config.yml
# python3 manage.py makemigrations ums rms rdts
python3 manage.py migrate
python3 manage.py createcachetable
python3 manage.py schedule &
python3 manage.py webhook &
python3 manage.py create &
#python3 manage.py runserver 80

uwsgi --chdir=/opt/tmp/ --module=backend.wsgi:application  --env DJANGO_SETTINGS_MODULE=backend.settings --master  --socket=127.0.0.1:80   --processes=5   --uid=1000 --gid=2000   --harakiri=20   --max-requests=5000    --vacuum
