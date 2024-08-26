#!/bin/bash

### Run tests
pytest --rootdir=tests

### Check coverage
pytest --rootdir=tests --cov=src

### Generate requirements files
pipreqs --savepath=requirements.in src/ && pip-compile --strip-extras

### Test build
python3 -m build

### Push to PyPI
twine upload dist/ontologise-[...]

### Generate documentation
sphinx-apidoc -a -o docs/source src/ontologise tests
cd docs
make clean; make html
