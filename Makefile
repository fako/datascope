clean:
	find . -type f -name "*.pyc" -delete;

docs:
	cd development/docs && make html

deploy-transip: clean
    sudo service uwsgi restart
    sudo /etc/init.d/celeryd restart