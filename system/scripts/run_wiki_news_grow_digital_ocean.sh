#!/bin/bash
# NB: Use jsub -l release=trusty run_wiki_news_grow.sh to make this script run on Tools
# NB: Use job -v run_wiki_news_grow to see status of the task

source /srv/datascope/ds-env/bin/activate
cd /srv/datascope/src/
export DJANGO_SETTINGS_MODULE=datascope.settings.digital-ocean
python manage.py grow_wiki_news --delete
