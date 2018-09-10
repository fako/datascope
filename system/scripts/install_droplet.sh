#!/bin/bash

# TODO: make this command take some passwords to setup correctly
# Get this command with wget https://raw.githubusercontent.com/fako/datascope/master/system/scripts/install_droplet.sh
# Prerequisites:
# 1)  Git installed with apt-get install git
# 2)  Manage security: https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server
# 3)  Install artillery: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-artillery-honeypot-on-an-ubuntu-vps
# 4)  Add secrets.py to /root
#
# TODO: include all steps necessary instead of having an after install manual process
# After execution:
# 1)  Take care of redis security: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis

# SETUP: install software
apt-get install -y vim nginx uwsgi uwsgi-plugin-python3 python-pip mysql-server libmysqlclient-dev python3-dev python3-venv tcl8.5 htop
# SciPy
apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran
# Pillow
apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

# SETUP: install redis
# From: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis
# TODO: use conda instead
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
git clone git@github.com:fako/ds-server.git
mkdir /srv/secrets
mv /root/secrets.py secrets/
mkdir -p /srv/logs/uwsgi
mkdir -p /srv/logs/nginx
mkdir -p /srv/logs/celery
mkdir /srv/www
mkdir /srv/uwsgi
# Now run from local: fly --flightplan=provision.js provision-server:aws

# SETUP: database
mysql -p -e "CREATE DATABASE datascope CHARSET utf8mb4;"
mysql -p -e "CREATE USER 'django'@'localhost' IDENTIFIED BY 'password';"
mysql -p -e "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES ON datascope.* TO 'django'@'localhost'; FLUSH PRIVILEGES;"
mysql -p -e "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES ON test_datascope.* TO 'django'@'localhost'; FLUSH PRIVILEGES;"

# SETUP: services
cd /srv/ds-server/server/
usermod -s /bin/bash www-data
# Celery
adduser celery --system --group
cp celery/celeryd.cnf.sh /etc/default/celeryd
cp celery/celeryd.cnf.sh /etc/default/S99celeryd
cp celery/celeryd.sh /etc/init.d/celeryd
chmod a+x /etc/init.d/celeryd
update-rc.d celeryd defaults 99
sudo service celeryd start
# Server content
cp statics/* /srv/www/
# Nginx
cp nginx/nginx.conf /etc/nginx/nginx.conf
cp nginx/data-scope.conf /etc/nginx/sites-available/data-scope.conf
cp nginx/server-www.conf /etc/nginx/
ln -s /etc/nginx/sites-available/data-scope.conf /etc/nginx/sites-enabled/data-scope.conf
rm /etc/nginx/sites-enabled/default
nginx -s reload

# Setup firewall
ufw allow ssh/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw logging on
ufw enable

# Finish setup by setting
chown www-data:www-data -R /srv
chown ubuntu:ubuntu -R /srv/artefacts
chown ubuntu:ubuntu -R /srv/ds-server
chown ubuntu:ubuntu -R /srv/secrets

# Deploy locally with
# fly --flightplan=deploy.js upload-artefacts:<remote> --releases=datascope
# fly --flightplan=deploy.js install-artefacts:<remote> --releases=datascope
# fly --flightplan=deploy.js deploy-artefacts:<remote> --releases=datascope

# After deploy we can link up with
ln -s /srv/www/static /srv/uwsgi/datascope/static
ln -s /etc/uwsgi/apps-enabled/datascope.ini /srv/uwsgi/datascope/<environment>.ini
