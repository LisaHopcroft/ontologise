#!/usr/bin/env python
# coding: utf-8

# In[374]:


import os
import pandas as pd
import numpy as np
import json
import os.path
import argparse
from re import search
import configparser


# In[387]:

if __name__ == "__main__":

	### READ COMMAND LINE ARGUMENTS
	
	parser = argparse.ArgumentParser(description="Generating place info.")

	parser.add_argument("run_dir",
						nargs='?',
						help="The directory in which to search for PEO/PLA data sources",
						default=".")
	parser.add_argument("-v",
						help="Print additional messages at run time",
						action='store_true')

	args = parser.parse_args()

	is_debugging = False
	if args.v: is_debugging = True

	run_dir = args.run_dir

	error_msgs = []

	### READ THE CONFIG FILE

	config = configparser.ConfigParser()
	config.read( '../../config.ini' )
	server_dir = config['LOCAL']['server_dir']

	# STEP 1: go through the directory and create reports for each place
	# - list all the peopla data points in date order
