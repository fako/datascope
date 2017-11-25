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
brew install python3 --framework

cd ~
mkdir Datascope
cd Datascope
git clone https://github.com/fako/datascope.git

mkdir envs
cd envs
python3 -m venv ds-env
source ds-env/bin/activate
cd datascope
pip install -r system/requirements/websockets.txt
python -m spacy download en
python -m spacy download nl


echo 'alias act-ds="source ~/Datascope/envs/ds-3/bin/activate && cd ~/Datascope/datascope/' >> ~/.bash_profile

mysql -uroot -e "CREATE DATABASE datascope CHARSET utf8mb4;"
cd ~/Datascope/datascope/
./manage.py syncdb
