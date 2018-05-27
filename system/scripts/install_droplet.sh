#!/bin/bash

# TODO: make this command take some passwords to setup correctly
# Get this command with wget https://raw.githubusercontent.com/fako/datascope/master/system/scripts/install_droplet.sh
# Prerequisites:
# 1)  Git installed with apt-get install git
# 2)  Manage security: https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server
# 3)  Install artillery: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-artillery-honeypot-on-an-ubuntu-vps
# 4)  Add bootstrap.py and secrets.py to /root
#
# TODO: include all steps necessary instead of having an after install manual process
# After execution:
# 1)  Take care of redis security: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis

# SETUP: install software
apt-get install vim
apt-get install nginx
apt-get install uwsgi
apt-get install uwsgi-plugin-python3
apt-get install python-pip
apt-get install mysql-server
apt-get install libmysqlclient-dev
apt-get install python3-dev
apt-get install python3-venv
apt-get install tcl8.5
apt-get install htop
# SciPy
apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
# Pillow
apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

# SETUP: install redis
# From: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis
cd /root
wget http://download.redis.io/releases/redis-stable.tar.gz
tar xzf redis-stable.tar.gz
cd redis-stable
make
make install
cd utils
./install_server.sh
update-rc.d redis_6379 defaults

# SETUP: basic repositories
cd /
mkdir /srv
cd /srv
git clone https://github.com/fako/ds-server.git
mkdir /srv/secrets
mv /root/secrets.py secrets/
mkdir -p /srv/logs/uwsgi
mkdir -p /srv/logs/nginx
mkdir -p /srv/logs/celery
mkdir /srv/www
mkdir /srv/uwsgi
# It's recommended to run provision-server from ds-server instead of 2 commands below
mkdir -p /srv/artefacts/datascope
mkdir /home/fako/datascope
# Finish setup by setting
chown www-data:www-data -R /srv

# SETUP: database
mysql -p -e "CREATE DATABASE datascope CHARSET utf8mb4;"
mysql -p -e "CREATE USER 'django'@'localhost' IDENTIFIED BY 'password';"
mysql -p -e "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES ON datascope.* TO 'django'@'localhost'; FLUSH PRIVILEGES;"
mysql -p -e "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES ON test_datascope.* TO 'django'@'localhost'; FLUSH PRIVILEGES;"

# SETUP: services
cd /srv/ds-server/server/
usermod -s /bin/bash www-data
# Celery
cp celery/celeryd.cnf.sh /etc/default/celeryd
cp celery/celeryd.cnf.sh /etc/default/S99celeryd
cp celery/celeryd.sh /etc/init.d/celeryd
chmod a+x /etc/init.d/celeryd
update-rc.d celeryd defaults 99
sudo service celeryd start
# Nginx
cp nginx/nginx.conf /etc/nginx/nginx.conf
cp nginx/data-scope.conf /etc/nginx/sites-available/data-scope.conf
ln -s /etc/nginx/sites-available/data-scope.conf /etc/nginx/sites-enabled/data-scope.conf
rm /etc/nginx/sites-enabled/default
nginx -s reload

# Setup firewall
ufw allow ssh/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw logging on
ufw enable

# TODO: deploy
