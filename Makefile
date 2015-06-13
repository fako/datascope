clean:
	find . -type f -name "*.pyc" -delete;

docs:
	cd system/docs && make html

deploy-transip: clean
	sudo service uwsgi restart
	sudo /etc/init.d/celeryd restart

deploy-wiki-labs: clean
	webservice2 uwsgi-python restart
