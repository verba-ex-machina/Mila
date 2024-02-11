# Makefile for Mila.
PYTHON = python3
PATHS = mila tests

.PHONY: help test clean

.DEFAULT_GOAL = help

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  lint         to run the linter"
	@echo "  test         to run the tests"
	@echo "  clean        to clean the project"
	@echo "  help         to display this help message"

lint:
	isort ${PATHS}
	black -l 79 ${PATHS}
	pydocstyle ${PATHS}
	pycodestyle ${PATHS}
	pylint ${PATHS}

test:
	${PYTHON} -m pytest

clean:
	rm -rf .pytest_cache
	rm -rf mila/__pycache__
	rm -rf tests/__pycache__