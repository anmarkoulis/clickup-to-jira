help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  install                            to install project."
	@echo "  install-reqs                       to install project dependencies."
	@echo "  install-docs                       to install docs dependencies"
	@echo "  install-rtd                        to install rtd dependencies"
	@echo "  install-tests                      to install test dependencies"
	@echo "  pre-commit                         to run the pre-commit checks."
	@echo "  test                               to run the tests"
	@echo "  test-with-coverage-report          to run the tests and create a coverage report"
	@echo "  build-sphinx                       to create the sphinx documentation"
	@echo "  build-package                      to build the package"


install:
	pip install .

install-reqs:
	pip install -r requirements.txt

install-docs:
	pip install -r requirements-docs.txt

install-rtd:
	pip install -r requirements-rts.txt

install-tests:
	pip install -r requirements-tests.txt

pre-commit: install-reqs install-tests
	pre-commit run ${args}

test: install-reqs install-tests
	coverage run --source=clickup_to_jira/ -m pytest

test-with-coverage-report: test
	coverage report

build-sphinx: install install-docs
	sphinx-build -b html docs/ docs/_build/html -a

build-package:
	pip install wheel && python setup.py sdist bdist_wheel
