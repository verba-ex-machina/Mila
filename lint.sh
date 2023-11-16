PATHS="main.py mila/*.py"

isort $PATHS
black -l 79 $PATHS
pydocstyle $PATHS
pycodestyle $PATHS
pylint $PATHS