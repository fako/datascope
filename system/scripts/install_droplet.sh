#!/bin/bash

# TODO: make this command take some passwords to setup correctly
# Get this command with wget https://raw.githubusercontent.com/fako/datascope/master/system/scripts/install_droplet.sh
# Prerequisites:
# 1)  Git installed with apt-get install git
# 2)  Manage security: https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server
# 3)  Install artillery: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-artillery-honeypot-on-an-ubuntu-vps
# 4)  Add bootstrap.py and secrets.py to /root

# SETUP: install software
apt-get install nginx
apt-get install uwsgi
apt-get install python-pip
apt-get install python-virtualenv
apt-get install mysql-server
apt-get install libmysqlclient-dev
apt-get install python3-dev

# SETUP: basic repositories
cd /
mkdir /srv
cd /srv
git clone https://github.com/fako/datascope.git datascope/src
git clone https://github.com/fako/ds-server.git
mkdir /srv/datascope/logs
chown www-data:www-data -R /srv

# SETUP: virtual environment
cd /srv/datascope
virtualenv -p python3 ds-env
source ds-env/bin/activate
pip install -r src/system/requirements/production.txt

# SETUP: database
mysql -p -e "CREATE DATABASE datascope CHARSET utf8;"
mysql -p -e "CREATE USER 'django'@'localhost' IDENTIFIED BY 'password';"
mysql -p -e "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX ON datascope.* TO 'django'@'localhost'; FLUSH PRIVILEGES;"

# SETUP: Django
export DJANGO_SETTINGS_MODULE="datascope.settings.digital-ocean"
cd /srv/datascope/src
python manage.py syncdb
python manage.py collectstatic
