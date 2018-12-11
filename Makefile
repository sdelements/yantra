lint:
	find . -name '*.py' | egrep -v './doc' | xargs flake8 --ignore=E501,W601
