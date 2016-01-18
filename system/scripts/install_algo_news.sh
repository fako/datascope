#!/bin/bash

# Prerequisites:
# 1)  Valid SSH key attached to github account to clone repository (truly needed with http protocol?)

# SETUP: repository
git clone git@github.com:fako/datascope.git src;

# SETUP: virtual environment
virtualenv env;
source env/bin/activate;
pip install -r src/system/requirements/production.txt

# SETUP: database
cp replica.my.cnf .my.cnf
mysql -e "CREATE DATABASE datascope CHARSET utf8;"
python src/manage.py migrate

# SETUP: server
wget https://raw.githubusercontent.com/fako/ds-server/master/deploy/uwsgi/algonews.ini
mv algonews.ini uwsgi.ini
webservice2 uwsgi-plain start
