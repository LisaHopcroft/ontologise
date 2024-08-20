#!/usr/bin/python
from __future__ import unicode_literals, division
import ezodf

import sys
import re
import os
import csv
from subprocess import call

sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.all as util
import ontologize.modules.data_transformation.all as prep
import ontologize.modules.data_analysis.all as osynth

try:
	# for Python2
	from Tkinter import *
except ImportError:
	# for Python3
	from tkinter import *


run_dir = util.confdat.academia_root
run_dir = "/media/michael/SSD3/Dropbox/workspace/2.research"


#----------------------------------------------------------------------#
# Trawl directories...
#----------------------------------------------------------------------#

for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		filepath = "%s/%s" % (root, fname)
		if prep.is_tagged_ODS( filepath ):

			ods = ezodf.opendoc( filepath )
			sheet = ods.sheets[0]

			is_mapping 		= False
			is_longitude 	= False
			is_latitude 	= False

			for col in range(sheet.ncols()):
				if sheet[0, col].value == "###MAPPING_REF": is_mapping = True
				if sheet[0, col].value == "###^LONGITUDE": 	is_longitude = True
				if sheet[0, col].value == "###^LATITUDE": 	is_latitude = True

			if is_mapping and not is_longitude and not is_latitude:
				print( filepath )
