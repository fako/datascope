now = $(shell date +"%Y-%m-%d")

clean:
	find . -type f -name "*.pyc" -delete;
	find . -type d -name "__pycache__" -delete;

deploy: clean
	sudo service uwsgi restart
	sudo service celeryd restart

backup-db:
	mysqldump -uroot -p --databases datascope > data/datascope.mysql.sql
	pg_dump -h localhost -U postgres datascope > data/datascope.postgres.sql

backup-data:
	rsync -zrthv --progress data /Volumes/Leo65/data/datascope

start-celery:
	celery -A datascope worker --loglevel=info -B

start-mysql:
	mysql --protocol=tcp -uroot -p

start-postgres:
	psql -h localhost -U postgres -d postgres

test:
	./manage.py test --settings=datascope.settings_test $(filter)
