#!/bin/bash

echo "Start update"

PROJECT_DIR=/srv/django1.6/datascope/

find $PROJECT_DIR -name "*.pyc" | xargs rm;
sudo service uwsgi restart;
sudo /etc/init.d/celeryd restart;

echo "End update"