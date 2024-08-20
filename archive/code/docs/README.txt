
2018-10-10
==========

Ontologize has been completely refactored.  Code separated into discreet modules for each stage of analysis.

1. File acquisition: (file-scraping)

2. File preparation: (file-preparation)

3. Data generation:

4. Data analysis:

5. Data presentation:


Code before was an ugly mish-mash of all of the above.

Runable scripts go in the top-level directory of each module.  Reusable code goes in util directory.

Quick Reference
===============

* To load jupyter notebook
  <$> jupyter notebook jupyter notebook generate-trees.ipynb 

* To extract python script from Jupyter Notebook
  <$> jupyter nbconvert --to script generate-trees.ipynb 

* To run python server (do this at the root node).
  This must be done before you can view the results of generate-trees.py
  python2.7 runserver.py
  ...or...
  python -m http.server

* Config.ini file should be in ontologize directory.
  It should be of the format:

  [LOCAL]
  server_dir = /path/of/root/directory

  ...where /path/of/root/directory is where we want the localhost:8000 server to run.