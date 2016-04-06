clean:
	find . -type f -name "*.pyc" -delete;

docs:
	cd system/docs && make html

deploy: clean
	sudo service uwsgi restart
	sudo service celeryd restart

deploy-wiki-labs: clean
	webservice2 uwsgi-python restart
