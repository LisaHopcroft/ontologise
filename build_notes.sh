#!/bin/bash

# Run black
black src

# Run flake8
flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Run ruff
ruff check src --output-format=github

# Run tests
pytest --rootdir=tests

# Check coverage
pytest --rootdir=tests --cov=src --cov-report term-missing

# Generate requirements files
pipreqs --savepath=requirements.in src/
pip-compile -r --strip-extras requirements.in -o requirements.txt

# pipreqs --savepath=requirements_tests.in tests/
# pip-compile -r --strip-extras requirements_tests.in -o requirements_tests.txt

# Test build
python3 -m build

# Push to PyPI
twine upload dist/ontologise-[...]

# Generate documentation
sphinx-apidoc -a -o docs/source src/ontologise tests
cd docs
make clean; make html
