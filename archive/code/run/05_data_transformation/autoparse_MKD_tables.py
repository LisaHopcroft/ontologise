#!/usr/bin/python

## CONVERT WELL-FORMATTED TRANSCRIPTION TEXT TO TSV DATA, USING LOCAL PATTERN RULES

import sys
import re
import itertools
from subprocess import call
import operator
import copy
import os
import re

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.all as util
import ontologize.modules.data_transformation.all as prep



run_dir = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/03.Publications/(B), Newspapers/(B), WIN/(GUI), Guianas/EDRG, Essequebo & Demerary Royal Gazette (1807-13)"

if len(sys.argv) > 1:
	run_dir = sys.argv[1]


def remove_square_brackets( input_text ):
	if "[" in input_text:
		return re.sub(r"\[.*\]","",input_text)

	return input_text


def parse_tables( collection_root, trx_root ):
	for root, dirs, files in os.walk( trx_root, topdown=True ):
		for fname in files:
			if fname.endswith(".txt") and not fname.startswith("^"):

				filepath = "%s/%s" % (root, fname)

				writepath = filepath.replace( "02_MKD", "03_^DAT" ).replace( "02_TXT", "03_^DAT" ).replace( "02_NOTES", "03_^DAT" )
				writepath = prep.insert_caret( writepath )

				with open( filepath, "r" ) as r:

					write_lines 	= []
					pattern_vals 	= []
					lines 			= r.readlines()
					src_date 		= ""
					src_type 		= ""

					line_num 		= 0

					for i, line in enumerate(lines):

						if line.startswith("#["):
							src_type = line.replace("#[","").replace("]","").strip()


						if line.startswith("##Date:"):
							src_date = line.replace("##Date:","").strip()


						if line.startswith("|"):
							vals = [ remove_square_brackets( val ).replace("-","").replace(":","").replace("*","").strip() for val in line[1:].split("|") ]

							for j, val in enumerate( vals ):
								val = val.strip()
								if val.startswith( "##" ):
									pattern_vals.append( val )
									line_num = i

							if all(val == "" for val in vals ):
								continue

							if pattern_vals:
								write_lines.append( "\t".join( vals ) + "\n" )


						if not line.startswith("|") and pattern_vals:
							pattern_vals = []

							writefile = writepath + ".[%s].munge.TABLEDATA.tsv" % line_num

							with open( writefile, "w" ) as w:
								for wl in write_lines:
									w.write( wl )
								# write to file

							write_lines = []


for root, dirs, files in os.walk( run_dir, topdown=True ):
	for folder in dirs:
		if "02_TXT" in folder or "02_MKD" in folder or "02_NOTES" in folder or "02A_TXT" in folder:
			collection_root = root
			trx_root = root + "/" + folder
			parse_tables( collection_root, trx_root )
