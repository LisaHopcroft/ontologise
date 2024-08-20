#!/usr/bin/python

import sys
sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
from ontologize.modules.util.all import *
import ontologize.modules.data_transformation.all as dt
from subprocess import call
import os
import csv

skip_dirs = [ "02_TXT", "02_MKD", "01_JPG", "01_PNG" ]

run_root = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch"


# USAGE: just create a ^tags directory wherever you want to see a tags overview


def get_txt_between_linenumbers( filepath, start_line, end_line ):
	txt = ""
	with open(filepath, 'r') as r:
		lines = r.readlines()
		for i in range( start_line, end_line ):
			txt = txt + lines[i]
	return txt


def write_references_etc( w, filepath, extra_ref, page_num ):
	w.write( "[Ref:] %s\n" % ( dt.get_ref_from_filepath( filepath, page_num ) ) )#, extra_ref ) )
	w.write( "[Path:] %s\n" % filepath.rstrip() ) #escape_filepath(  )
	w.write( "\n" )
	w.write( "----------------------------------" )
	w.write( "\n\n" )


def run_per_file( filepath, tags_list ):
	with open(filepath, 'r') as r:
		last_gap_line = 0
		line_num = 0
		page_num = 0
		for line in r.readlines():
			if line.startswith( "![" ):
				page_num = line.replace( "![", "" ).replace( "]", "" ).replace( "p", "" ).strip().lstrip("0")

			if line == "\n" or line == "\r" or line == ">\n" or line == ">\r" or line == "> \n" or line == ">\r\n" or line == "\r\n":
				last_gap_line = line_num

			if line.startswith( "##" ) and not line.startswith( "###" ) and not ":" in line and not "*" in line and not line.startswith( "01_" ) and not line.startswith( "02_" ) and not "##ODS" in line and not "[" in line and not "{" in line:
				tags = line.rstrip().split( " ##" )
				for tag in tags:
					tag = tag.replace( "#", "" ).replace( "/", "-" ).replace( ">", "" ).replace( "\\", "-" ).lstrip().upper()
					if not tag == "": # if not blank tag
						if not tag in tags_list:
							tags_list[ tag ] = [] # creates empty list
						tags_list[ tag ].append( [filepath, last_gap_line, line_num, get_txt_between_linenumbers( filepath, last_gap_line, line_num ), line, page_num] )

			line_num += 1
	return tags_list


def run_tag_search( dirpath ):

	tags_list = {}

	if os.path.isfile( "%s/^FILELIST.tsv" % (dirpath) ):
		with open( "%s/^FILELIST.tsv" % (dirpath), "r" ) as r:
			reader = csv.reader(r, delimiter='\t')
			for row in reader:
				tags_list = run_per_file( "%s/%s" % ( dirpath, row[1] ), tags_list )
	else:
		for root, dirs, files in os.walk( dirpath, topdown=True ):
			for d in dirs:
				if "TXT" in d or "MKD" in d:
					path = root + "/" + d
					for trxroot, subdirs, txtfiles in os.walk( path ):
						for fname in txtfiles:
							if fname.endswith(".txt") or fname.endswith(".mkd") and not fname.startswith("^"):
								# open file to analyse
								tags_list = run_per_file( "%s/%s" % ( trxroot, fname ), tags_list )

	overviewpath = "%s/^vis/^tags.html" % ( dirpath )

	with open(overviewpath, 'w') as w2:

		for tag, results in tags_list.iteritems():

			w2.write( "<a href='../^tags/^%s.txt'>%s</a> (%s)<br/>" % ( tag, tag, len(results) ) )

			tagfilepath = "%s/^tags/^%s.txt" % ( dirpath, tag )

			with open(tagfilepath, 'w') as w:
				i = 1
				last_filepath = None
				for result in sorted(results):
					filepath = result[0]
					last_gap_line	= result[1]
					tagline_num     = result[2]
					text     = result[3]
					tagline  = result[4]
					page_num = result[5]
					other_tags = tagline.replace( "##%s\n" % tag, "" ).replace( "##%s " % tag, "" ).strip()

					if last_gap_line >= tagline_num - 1:
						continue
					
					with open(filepath, 'r') as r:
						if last_filepath and ( filepath != last_filepath ):
							write_references_etc( w, last_filepath, last_extra_ref, page_num )

						if is_minutes( r ):
							date = get_key_detail( r, "#Date:" )
							if date:
								extra_ref = ", %s" % date

						if is_letter( r ):
							fm = get_key_detail( r, "#Fm:" )
							fm_at = get_key_detail( r, "#Fm@:" )
							to = get_key_detail( r, "#To:" )
							to_at = get_key_detail( r, "#To@:" )
							date = get_key_detail( r, "#Date:" )

							if not to_at and not fm_at:
								extra_ref = ", %s to %s, %s" % ( 	fm, 
																	to, 
																	date )
							elif not to_at:
								extra_ref = ", %s (%s) to %s, %s" % ( 	fm,
																		fm_at, 
																		to, 
																		date )
							elif not fm_at:
								extra_ref = ", %s to %s (%s), %s" % ( 	fm, 
																		to, 
																		to_at, 
																		date )

							else:
								extra_ref = ", %s (%s) to %s (%s), %s" % ( 	fm, 
																			fm_at, 
																			to, 
																			to_at,
																			date )
						else:
							extra_ref  = ""

						w.write( "[#%s]\n" % str(i) )
						w.write( "%s\n" % text.rstrip() )
						if other_tags:
							w.write( "%s\n" % ( other_tags ) )
						w.write( "\n" )
					
						if i == len(results)-1 or i == len(results):
							write_references_etc( w, filepath, extra_ref, page_num )

					last_filepath = filepath
					last_extra_ref = extra_ref
					i += 1
			w.close()

			if os.stat(tagfilepath).st_size == 0:
				os.remove(tagfilepath)



for root, dirs, files in os.walk( run_root, topdown=True ):
	for d in dirs:
		if d == "^tags":
			cmd = "rm \"%s/%s/^\"*" % ( root, d )
			print( cmd )
			os.system( cmd )
			run_tag_search( root )




# 0 - filepath
# 1 - last gap line
# 2 - line num
# 3 - txt between linenumbers
# 4 - tagline
# 5 - page num

