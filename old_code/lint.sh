PATHS="milabot.py mila/*.py mila/tools/*.py"

isort $PATHS
black -l 79 $PATHS
pydocstyle $PATHS
pycodestyle $PATHS
pylint $PATHS