#!/bin/bash

# Prerequisites:
# 1)  Valid SSH key attached to github account to clone repository (truly needed with http protocol?)

# SETUP: repository
git clone git@github.com:fako/datascope.git src;

# SETUP: virtual environment
virtualenv -p python3 env;
source env/bin/activate;
pip install -r src/system/requirements/production.txt

# SETUP: database
cp replica.my.cnf .my.cnf
mysql -e "CREATE DATABASE s52573__datascope CHARSET utf8md4;"
python src/manage.py syncdb

# SETUP: statics
mkdir www
mkdir www/static
ln -s src/system/files/static/ www/static/static
ln -s src/system/files/media/ www/static/media
python src/manage.py collectstatic

# SETUP: server
wget https://raw.githubusercontent.com/fako/ds-server/master/deploy/uwsgi/algonews.ini
wget https://raw.githubusercontent.com/fako/ds-server/master/deploy/misc/wikipedia/.bigbrotherrc
mv algonews.ini uwsgi.ini
webservice2 uwsgi-plain start
