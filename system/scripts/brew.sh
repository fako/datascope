# This script will on a Mac:
# 1)   Brew: mysql, redis, python3, phantomjs and a few other dependencies
# 2)   Install datascope under ~/Datascope
# 3)   Create and setup the datascope database in MySQL
# 4)   Add "act-ds" alias to start development

#!/bin/bash

brew install redis
brew install phantomjs
brew install libjpeg
brew install mysql
brew install python3

pip3 install virtualenv

cd ~
mkdir Datascope
cd Datascope
git clone https://github.com/fako/datascope.git

cd ~
mkdir .envs
cd .envs
virualenv -p python3 ds-env
source ds-env/bin/activate
cd ../Datascope/datascope
pip install -r system/requirements/websockets.txt

export DJANGO_SETTINGS_MODULE=datascope.settings.development;
echo 'alias act-ds="source ~/Datascope/envs/ds-3/bin/activate && cd ~/Datascope/datascope/ && export DJANGO_SETTINGS_MODULE=datascope.settings.development"' >> ~/.bash_profile

mysql -uroot -e "CREATE DATABASE datascope CHARSET utf8;"
cd ~/Datascope/datascope/
./manage.py syncdb
