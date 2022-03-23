#!/bin/sh
cp ./config/config.yml ./config.yml
python3 manage.py makemigrations ums rms rdts
python3 manage.py migrate --fake
python3 manage.py createcachetable
python3 manage.py runserver 0.0.0.0:80
