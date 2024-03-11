flake8 .
if [[ $? -ne 0 ]]; then
    exit 1
fi
pylint sources
if [[ $? -ne 0 ]]; then
    exit 1
fi
pylint tests
if [[ $? -ne 0 ]]; then
    exit 1
fi