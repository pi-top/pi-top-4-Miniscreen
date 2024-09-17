#!/bin/bash

if [ ! -d "/src" ]; then
    echo "Error: /src directory not found, make sure to mount the project root directory to /src"
    exit 1
fi

cd /src

# Install new dependencies
pip3 install -r tests/requirements.txt --extra-index-url=https://packagecloud.io/pi-top/pypi/pypi/simple

# Run the tests
pytest --verbose --cov-report term-missing --cov=pt_miniscreen || exit 1

# Generate the coverage report
coverage xml
