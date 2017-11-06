#!/bin/bash
# NB: Use jstart -l release=trusty run_wiki_celery.sh to make this script run a celery worker on Tools
# NB: Use job -v run_wiki_celery to see status of the worker

source /data/project/algo-news/datascope/env/bin/activate
cd /data/project/algo-news/datascope/src/
export PYTHONIOENCODING=UTF-8
python manage.py celery worker -n datascope -l info -Q datascope
