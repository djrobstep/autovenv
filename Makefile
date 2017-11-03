.PHONY: docs

# test commands and arguments
tcommand = PYTHONPATH=. py.test -x
tmessy = -svv
targs = --cov-report term-missing --cov autovenv

all: clean fmt lint tox docs

pip:
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

pipeditable:
	pip install -e .

tox:
	tox tests

test:
	$(tcommand) $(targs) tests

stest:
	$(tcommand) $(tmessy) $(targs) tests

clean:
	git clean -fXd
	find . -name \*.pyc -delete

lint:
	flake8 autovenv
	flake8 tests

docs:
	cd docs && make clean && make html

opendocs:
	python -c 'import os;import webbrowser;webbrowser.open_new_tab("file://" + os.getcwd() + "/docs/_build/html/index.html")'

testpublish:
	python setup.py register -r https://testpypi.python.org/pypi
	python setup.py sdist bdist_wheel --universal upload -r https://testpypi.python.org/pypi

publish:
	python setup.py sdist bdist_wheel --universal
	twine upload dist/*

updatepythonbuild:
	rm -fr autovenv/python-build
	rm -fr pyenv
	git clone https://github.com/yyuu/pyenv.git
	mkdir -p autovenv/python-build
	cp pyenv/plugins/python-build/LICENSE autovenv/python-build/
	cp -r pyenv/plugins/python-build/share autovenv/python-build/
	cp pyenv/plugins/python-build/bin/python-build autovenv/python-build/autovenv-python-build
	rm -fr pyenv
