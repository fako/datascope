clean:
	find . -type f -name "*.pyc" -delete;

docs:
	cd docs && make html
