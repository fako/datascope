#!/bin/bash
# NB: Use jstart -l release=trusty run_wiki_celery.sh to make this script run a celery worker on Tools
# NB: Use job -v run_wiki_celery to see status of the worker

source /data/project/algo-news/env/bin/activate
cd /data/project/algo-news/src/
export DJANGO_SETTINGS_MODULE=datascope.settings.wikipedia
export PYTHONIOENCODING=UTF-8
python manage.py celery worker -n datascope -l info -Q datascope
