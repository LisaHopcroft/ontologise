#!/usr/bin/python

## CONVERT TRX MICROFORMATS TO TSV DATA

import sys
import re
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
from util.util import *
from subprocess import call



def get_filepaths( start_point ):
	filepaths = []

	for root, dirs, files in os.walk( start_point, topdown=True ):
		for fname in files:
			if fname.endswith(".txt") or fname.endswith(".mkd") and not fname.startswith("^"):
				filepath = root + "/" + fname
				with open(filepath, 'r') as r:
					for i, line in enumerate( r ):
						if "##ODS" in line:
							if not filepath in filepaths:
								filepaths.append( filepath )

	return sorted( filepaths )


def remove_pagetagtxt( text ):
	return text.strip("\n").strip("]").strip("![").strip("p").strip("x")


def remove_tagtxt( text ):
	return text.strip("#").strip("{").strip("}")


def MKD_to_ODS( filepaths ):
	written_files = []

	for filepath in filepaths:
		shipping_status = ""
		table_start_pos = 0
		last_blankline_pos = 0
		account_num = 1
		date_val = "ND"
		fname = filepath.rsplit("/", 1)[1]
		write_folder = filepath.rsplit('02_MKD', 1)[0] + "02_+ODS" # FRAGILE CODE - needs re-coding

		page = 0

		headings = []

		with open(filepath, 'r') as r:
			for i, line in enumerate( r ):
				if "#Date:".lower() in line.lower():
					date_val  = line.replace("#","").replace("Date:","").replace("DATE:","").strip()

				if "##ODS" in line:
					tags = [ "##{SUBSCRIBERS}", "##{ACCTS}", "##{CENSUS}" ]

					for tag in tags:
						if tag in line:
							tag_val = remove_tagtxt( tag )
							marker_pos = i
							#print marker_pos
							#print table_start_pos
					
							write_file = ( filepath + ".[#%s_%s].tsv" % ( tag_val, str(i).zfill(3) ) ).replace( "02_MKD", "02_+ODS" )
							write_folder = write_file.rsplit("/",1)[0]
							if not os.path.exists( write_folder ):
								os.makedirs( write_folder )

							modifier = "w"
							written_files.append( write_file )

							with open(write_file, modifier) as w:
								if modifier == "w":
									w.write( "\t".join( [ "###DATE", "##{}", "LINE" ] + headings ) + "\n" )

								with open(filepath, 'r') as readfile:
									lines = readfile.readlines()

									# Loop over the table
									for j in range( table_start_pos+1, marker_pos ):
										if lines[j].startswith( ( "| ###") ):
											continue

										if lines[j].startswith( ( "![p", "![x") ):
											page = remove_pagetagtxt( lines[j] )

										vals = lines[j].split("| ")[1:]
										for index, item in enumerate(vals):
											vals[index] = vals[index].strip().rstrip("|").strip()

										w.write( "\t".join( [ date_val, tag_val, str(j).zfill(3) ] + vals ) + "\n" )

				if line.startswith("| ###"):
					headings = line.split("| ###")[1:]
					for index, item in enumerate(headings):
						headings[index] = headings[index].strip().rstrip("|").strip()
					print headings

				if line.startswith("|:----"):
					table_start_pos = i


filepaths = get_filepaths( "/media/michael/Files/Dropbox/workspace/2.research" )
MKD_to_ODS( filepaths )
