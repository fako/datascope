now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;

docs:
	cd system/docs && make html

deploy: clean
	sudo service uwsgi restart
	sudo service celeryd restart

deploy-wiki-labs: clean
	jstop celery
	webservice2 uwsgi-plain restart
	jstart -N celery -l release=trusty -mem 2048m commands/celery.sh

health-wiki-labs:
	qstat

dump:
	./manage.py dumpdata --natural-foreign -e contenttypes -e auth.Permission -e admin -e sessions --indent=4 > db-dump.$(now).json

start-development:
	/usr/local/bin/mysql.server start
	redis-server

start-celery:
	celery -A datascope worker --loglevel=info

stop-development:
	/usr/local/bin/mysql.server stop

test:
	./manage.py test --settings=datascope.settings_test $(filter)

grow-feed-wiki-labs:
	jsub -l release=trusty -mem 3072m commands/grow.sh
