#!/bin/bash
# NB: Use jsub -l release=trusty run_wiki_feed_grow.sh to make this script run on Tools
# NB: Use job -v run_wiki_feed_grow to see status of the task

source /data/project/algo-news/datascope/env/bin/activate
cd /data/project/algo-news/src/
python manage.py grow_wiki_feed --delete
python manage.py publish_wiki_feed --delete
