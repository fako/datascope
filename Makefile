now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;

docs:
	cd system/docs && make html

deploy: clean
	sudo service uwsgi restart
	sudo service celeryd restart

deploy-wiki-labs: clean
	webservice2 uwsgi-plain restart
	jstop celery
	jstart -l release=trusty -mem 1024m celery.sh

dump:
	./manage.py dumpdata --natural-foreign -e contenttypes -e auth.Permission -e admin -e sessions --indent=4 > db-dump.$(now).json

start-development:
	/usr/local/bin/mysql.server start
	redis-server

stop-development:
	/usr/local/bin/mysql.server stop

test:
	./manage.py test --settings=datascope.settings.test

grow-feed-wiki-labs:
	jsub -l release=trusty -mem 800m grow.sh
