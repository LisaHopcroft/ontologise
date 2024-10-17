#!/bin/bash

# Run black
black src
black tests

# Run flake8
flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 tests --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
flake8 tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Run ruff
ruff check src --output-format=github
ruff check tests --output-format=github

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
rm docs/source/utils.rst
rm docs/source/modules.rst
# Remove any obsolete .rst/.html files, e.g.:
# rm docs/source/test_parser.rst
# rm docs/html/test_parser.html

sphinx-apidoc -a -o docs/source src/ontologise tests
sphinx-build -a -b html docs/source docs/html -j auto
# cd docs
# make clean; make html
