# Makefile for Mila.
PYTHON = python3
PATHS = mila tests

.DEFAULT_GOAL = help

prep:
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r requirements.txt
	${PYTHON} -m pip install -r requirements-dev.txt

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  lint         to run the linter"
	@echo "  test         to run the tests"
	@echo "  clean        to clean the project"
	@echo "  all          to run lint, test and clean"
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
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -fr */*/*/__pycache__

# Set one command to run lint, test and clean.
all: lint test clean