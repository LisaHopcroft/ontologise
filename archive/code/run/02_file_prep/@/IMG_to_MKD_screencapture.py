#!/usr/bin/python

import os
import shutil
import getopt
import sys
import re

FORCE=False
VERBOSE=False

try:
	opts, args = getopt.getopt(sys.argv[1:],"fhv",["force","help","verbose"])

	for opt, arg in opts:

		if opt in ('-h',"--help"):
			print 'generate_markdown.py [-f/--force] [-v/--verbose]'
			print '-f : force Markdown generation (i.e., overwrite)'
			print '-v : be verbose'
			sys.exit()
		elif opt in ( "-v", "--verbose" ):
			VERBOSE=True
			print "Verbose option on"
		elif opt in ( "-f", "--force" ):
			print "\n"
			print "**WARNING** Force generation requested"
			print "**WARNING** All Markdown files will be overwritten"
			print "\nAre you sure (y/N)?\n> "
			check=raw_input()
			if ( check=="y" ):
				FORCE=True
				print "OK, all Markdown files will be replaced"
			else:
				print "Rerun the script without -f/--force"
				sys.exit()

except getopt.GetoptError:
	print 'generate_markdown.py [-f/--force] [-v/--verbose]'
	print '-f/--force   : force Markdown generation (i.e., overwrite)'
	print '-v/--verbose : be verbose'
	sys.exit(2)

template_file="./template.txt"

png_dir="../01_PNG-sel"
mkd_dir="../02_MKD"

png_ext=".png"
mkd_ext=".txt"


for root, dirs, files in os.walk(png_dir):
	for name in files:
		path = os.path.join(root, name)
		
		if VERBOSE:
			print "Considering file [%s]" % ( path )


		name_string=re.sub( r' .*', '', os.path.splitext(name)[0] )

		term=os.path.basename(root)

		elements=name_string.split( "-" )
		if ( len(elements)==1 ):
			elements=name_string.split( "_" )

		publ="NA"
		date="NA"
		page="NA"
		coln="NA"

		if VERBOSE:
			print "Number of elements in file name=%s" % ( len(elements) )

		if ( len(elements)==3 ):
			date=elements[0]
			page=elements[1]
			coln=elements[2]
		elif ( len(elements)==4 ):
			publ=elements[0]
			date=elements[1]
			page=elements[2]
			coln=elements[3]

		if VERBOSE:
			print "DATE: " + date
			print "PUBL: " + publ
			print "PAGE: " + page
			print "COLN: " + coln
			print "TERM: " + term

		this_mkd_name=name.replace(png_ext,mkd_ext)
		this_mkd_dir=root.replace(png_dir,mkd_dir)
		this_mkd_file="/".join( [ this_mkd_dir, this_mkd_name ] )

		if FORCE or not os.path.isfile( this_mkd_file ):
			if not os.path.exists( this_mkd_dir ):
				print "[+] Creating directory [%s]" % ( this_mkd_dir )
				os.mkdir( this_mkd_dir )
			else:
				print "[-] Directory already exists [%s]" % ( this_mkd_dir )
			mkd_filehandle=open( template_file )
			mkd_content=mkd_filehandle.read()
			
			mkd_content=mkd_content\
			.replace( "[DATE]"	, date )\
			.replace( "[PUBL]"	, publ )\
			.replace( "[PAGE]"	, page )\
			.replace( "[COLN]"	, coln )\
			.replace( "[TERM]"	, term )\
			.replace( "[FILENAME]", "../%s" % path )

			with open( this_mkd_file, "w" ) as output_file:
				output_file.write( mkd_content )
			
			print "[+] Markdown file generated [%s]" % ( this_mkd_file )
		else:
			print "[-] Markdown file already exists, will not update [%s]" % ( this_mkd_file )

		print "=================================================================="
		

