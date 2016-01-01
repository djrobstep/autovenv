.PHONY: docs

# test commands and arguments
tcommand = PYTHONPATH=. py.test -x
tmessy = -svv
targs = --cov-report term-missing --cov autovenv

all: clean fmt lint tox docs

pip:
	pip install -r requirements-dev.txt

pipupgrade:
	pip install --upgrade -r requirements-dev.txt
	pip install --upgrade pip

pipreqs:
	pip install -r requirements.txt

pipeditable:
	pip install -e .

init: pip

freshenv%:
	autovenv recreate

tox:
	tox tests

test:
	$(tcommand) $(targs) tests

stest:
	$(tcommand) $(tmessy) $(targs) tests


clean:
	git clean -fXd
	find . -name \*.pyc -delete

fmt:
	yapf --recursive --in-place autovenv
	yapf --recursive --in-place tests

lint:
	flake8 autovenv
	flake8 tests

checkinstall: freshenv1 pipreqs pipeditable freshenv2 pip

docs:
	cd docs && make html
