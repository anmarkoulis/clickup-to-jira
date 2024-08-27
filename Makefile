.PHONY: help dep install install-no-venv install-as-library pre-commit test test-with-coverage-report build-sphinx build-package

help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  dep                                to install Poetry and other project dependencies."
	@echo "  install                            to install project dependencies using Poetry."
	@echo "  install-no-venv                    to install project dependencies without creating a virtual environment."
	@echo "  install-as-library                 to install project dependencies (assumes Poetry is configured)."
	@echo "  pre-commit                         to run the pre-commit checks."
	@echo "  test                               to run the tests."
	@echo "  test-with-coverage-report          to run the tests and create a coverage report."
	@echo "  build-sphinx                       to create the Sphinx documentation."
	@echo "  build-package                      to build the package."

dep:
	pip install -r requirements-poetry.txt

install: dep
	poetry install --no-interaction --no-root

install-no-venv: dep
	poetry config virtualenvs.create false
	make install-as-library

install-as-library: dep
	poetry install --no-interaction

pre-commit: install-as-library
	poetry run pre-commit run ${args}

test: install-as-library
	poetry run pytest --cov=src/clickup_to_jira

test-with-coverage-report: test
	poetry run coverage report

build-sphinx: install-as-library
	poetry run sphinx-build -b html docs/ docs/_build/html -a

build-package: install-as-library
	poetry build

migrate_to_jira: install-as-library
	poetry run migrate_to_jira
