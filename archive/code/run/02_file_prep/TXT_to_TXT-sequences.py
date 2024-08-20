#!/usr/bin/python

import os
import glob
import re

override = False

# -------------------------------------------------------------- #
# Extract the TXT from a text-based PDF
# -------------------------------------------------------------- #


run_dir = "/media/michael/Files/Dropbox/workspace/2.research/02.Secondary/03.Articles/NORTHERN SCOTLAND/ALSTON, 2018 - Suriname Planters"


def write_a_file( path, section_page, section_title, page_line, writelines ):
	writepath		= "%s/%s, %s.txt" % ( path, section_page.replace("-",".pdf-"), section_title )
	if os.path.isfile( writepath ): return
	with open( writepath, "w" ) as w:
		w.write( page_line + "\n" )
		w.writelines( writelines )
		w.write( "\n[END]" )


for root, dirs, files in os.walk( run_dir ):
	for dirname in dirs:
		if dirname == "02_TXT":
			path = "%s/%s" % ( root, dirname )
			pattern = path + "/*.txt"
			print( pattern )
			for fname in sorted( glob.glob( pattern ) ):
				writelines = []
				section_title 	= ""
				section_page 	= ""
				page_line 		= ""
				with open( fname, "r" ) as r:
					for line in r.readlines():
						if line.startswith( "![img](" ):
							page_line = line
						if line.startswith( "![x]:" ):
							write_a_file( path, section_page, section_title, page_line, writelines )

							section_page 	= page_line.split( "01_IMG/", 1 )[1].split( ".jpg", 1 )[0]
							section_title 	= line.replace("![x]:","").strip()
							section_title	= re.sub("[^a-zA-Z0-9]+", " ", section_title) # remove special characters
							writelines 		= []
							line = line.replace("![x]:","")
						if line.startswith( "[END]" ):
							if section_title != "":
								write_a_file( path, section_page, section_title, page_line, writelines )
						writelines.append( line )
