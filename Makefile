clean:
	find . -type f -name "*.pyc" -delete;
	find . -type d -name "__pycache__" -delete;

backup-data:
	# Syncing local data to a harddrive
	# -z means use compression
	# -r means recursive
	# -t means preserve creation and modification times
	# -h means human readable output
	# -v means verbose
	rsync -zrthv --progress data /Volumes/Leo65/data/datascope

start-celery:
	cd src && celery -A datascope worker --loglevel=info -B

start-postgres:
	psql -h localhost -U postgres -d postgres

test:
	cd src && ./manage.py test --settings=datascope.settings_test $(filter)
