now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;

docs:
	cd system/docs && make html

deploy: clean
	sudo service uwsgi restart
	sudo service celeryd restart

deploy-wiki-labs: clean
	webservice2 uwsgi-python restart

dump:
	./manage.py dumpdata --natural-foreign -e contenttypes -e auth.Permission -e admin -e sessions --indent=4 > db-dump.$(now).json

start-development:
	/usr/local/bin/mysql.server restart
	redis-server
