now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;

deploy: clean
	sudo service uwsgi restart
	sudo service celeryd restart

backup-db:
	mysqldump -uroot -p --databases datascope > data/datascope.sql

backup-data:
	rsync -zrthv --progress data /Volumes/Leo65/data/datascope

start-celery:
	celery -A datascope worker --loglevel=info -B

start-mysql:
	mysql --protocol=tcp -uroot -p

start-postgres:
	psql -h localhost -U root -d postgres

test:
	./manage.py test --settings=datascope.settings_test $(filter)
