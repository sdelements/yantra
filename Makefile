lint:
	flake8 . --extend-ignore=D,E501,W601 --extend-exclude=docs/ --statistics --count
