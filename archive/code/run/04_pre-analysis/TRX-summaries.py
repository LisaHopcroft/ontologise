#!/usr/bin/python

import sys
import os
#sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
#from util.util import *
from subprocess import call
from datetime import datetime


run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch/359031, Cairn of Lochwinyoch matters, 1827-37"


def intWithCommas(x):
    if type(x) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)


def get_word_count( readfile ):
	readfile.seek(0, 0)
	num_words = 0
	for line in readfile:
		if not line.startswith("#") and not line.startswith(">") and not line.startswith( "![" ) and not line.strip() == "[...]" and not line.strip() == "[END]" and not line.startswith( "----------" ):
			words = line.split()
			num_words += len(words)
	return num_words


def get_completion_status( readfile ):
	readfile.seek(0, 0)
	for line in readfile:
		if "[...]" in line:
			return "Partial"
	return "Complete"


def get_level_from_crmb( path ):
	level = ""
	if os.path.exists( path ):
		with open( path, 'r' ) as r:
			firstline = r.readline().rstrip()
			if firstline.startswith("#"):
				return firstline
	return level


def update_desc_from_crmb( path, desc ):
	if os.path.exists( path ):
		with open( path, 'r' ) as r:
			for line in r:
				if line.startswith( "#BIBDESC: " ):
					desc = line.rstrip()[10:]
	return desc


def get_trail_from_path( path, path_root ):
	subpath = path.replace(path_root,"")

	trail = []
	num_dirs = len( subpath.split("/") )

	lvl = 1
	if not subpath.startswith( "0" ):
		trail.append( ( 1, "Scotland", "zone" ) )
		lvl = lvl + 1

	# loop through dirs in the path
	for i in range( 0, num_dirs ):	
		split = subpath.split("/")	
		dir_name = split[i]
		dir_path = '/'.join(split[:i+1])

		if dir_name.startswith( "_" ) or "#" in dir_name:
			return None

		crmb_path = path_root + dir_path + "/crmb.txt"
		level = get_level_from_crmb( crmb_path )

		desc = dir_name

		if dir_name.startswith( "0" ) and len( dir_name.split(".") ) > 1:
			desc = dir_name.split(".")[1]

		if "skip" not in level and not any( x in dir_name for x in skip_dirs ):
			desc = update_desc_from_crmb( crmb_path, desc )
			trail.append( ( lvl, desc, level ) )
			lvl = lvl + 1

	return trail


def pad_tuple_list( target_len, tuple_list ):
	if len( tuple_list ) < target_len:
		tuple_list.append( ( None, None, None ) )
		return pad_tuple_list( target_len, tuple_list )
	return tuple_list


def is_letter( txtfile ):
	first_line = txtfile.readline()
	if "LETTER" in first_line:
		return True
	return False


def is_will( txtfile ):
	first_line = txtfile.readline()
	if "WILL" in first_line:
		return True
	return False


def get_tuple_path( path, folder, append="" ):
	tuple_path = get_trail_from_path( path, folder )
	if tuple_path:
		tuple_path = sorted( tuple_path, key=lambda tup: tup[0] )
	return tuple_path


def parse_trx_folder( folder ):
	tuple_paths = []

	for root, dirs, files in os.walk( folder, topdown=True ):
		for d in dirs:
			if "02_TXT" in d or "02_MKD" in d:
				path = root + "/" + d
				for trxroot, subdirs, txtfiles in os.walk( path ):
					file_details = []
					tuple_path = get_tuple_path( path, folder )

					for fname in sorted( txtfiles ):
						if fname.endswith(".txt") and not fname.startswith("^"):
							# open file to analyse
							with open(trxroot + "/" + fname, 'r') as r:
								num_words = get_word_count( r )
								file_details.append( { 	'num_words': num_words,
													   	'fname': fname,
														'completion_status': get_completion_status( r ) } )

					# write ^sum file for folder
					trx_dir = trxroot + "/../^trx/"
					if not os.path.exists( trx_dir ): os.mkdir( trx_dir )
					write_dir = trx_dir + datetime.today().strftime('%Y-%m-%d')
					if not os.path.exists( write_dir ): os.mkdir( write_dir )
					
					with open(write_dir + "/^txt.tsv", 'w+') as w:
						total_words = 0
						for item in file_details:				
							w.write( "\t".join( str(x) for x in [ item['fname'], item['num_words'], item['completion_status'] ] ) + "\n" )
							total_words = total_words + item['num_words']

					#if tuple-path update the last tuple
					if tuple_path:
						t = tuple_path[-1]
						lst = list(t)
						lst[1] = lst[1] + " **" + str(intWithCommas( total_words )) + " words**"
						tuple_path[-1] = tuple(lst)
						tuple_path = pad_tuple_list( max_depth, tuple_path )
						tuple_paths.append( tuple_path )

	return tuple_paths


def get_hashes( num_hashes ):
	hashes = ""
	for j in range( 0, num_hashes ):
		 hashes += "#"
	return hashes


def print_bib( outfile, bib_list ):
	with open( outfile, 'w+') as report:
		prev_tuple_path = []
		prev_tuple_path.append( ( None, None, None ) )
		for tuple_path in bib_list:
			for i in range( 0, len(tuple_path)-1 ):
				if len( prev_tuple_path ) > i:
					if tuple_path[i][1] != prev_tuple_path[i][1] and tuple_path[i][1] is not None:
						report.write( get_hashes( i+1 ) )
						report.write( str( tuple_path[i][1] ) + "\n" )
			prev_tuple_path = tuple_path


trx_all = []
trx_wills = []
trx_letters = []
jpg_all = []
trx_official_all = []
max_depth = 10
skip_dirs = [ "02_TXT", "02_MKD", "01_JPG", "01_PNG" ]

trx_all = parse_trx_folder( run_dir )

for root, dirs, files in os.walk( run_dir, topdown=True ):
	for d in dirs:
		if "01_IMG" in d:
			path = root + "/" + d
			for matchroot, subdirs, matchfiles in os.walk( path ):
				num_files = 0
				tuple_path = get_tuple_path( path, run_dir )
				for fname in sorted( matchfiles ):
					if not fname.startswith("^"):
						num_files = num_files + 1	

						if tuple_path:
							jpg_all.append( tuple_path )

				# write ^sum file for folder
				trx_dir = matchroot + "/../^trx/"
				if not os.path.exists( trx_dir ): os.mkdir( trx_dir )
				write_dir = trx_dir + datetime.today().strftime('%Y-%m-%d')
				if not os.path.exists( write_dir ): os.mkdir( write_dir )
				
				with open(write_dir + "/^img.tsv", 'w+') as w:
					w.write( str(num_files) + " files\n\n" )
					
				#if tuple-path update the last tuple
				if tuple_path:
					t = tuple_path[-1]
					lst = list(t)
					lst[1] = lst[1] + " **" + str(intWithCommas( num_files )) + " photos**"
					tuple_path[-1] = tuple(lst)
					tuple_path = pad_tuple_list( max_depth, tuple_path )
					jpg_all.append( tuple_path )


#sort
for i in range( max_depth-1, -1, -1 ):
	trx_all = sorted(trx_all, key=lambda elem: elem[i][1])
	jpg_all = sorted(jpg_all, key=lambda elem: elem[i][1])
	trx_official_all = sorted(trx_official_all, key=lambda elem: elem[i][1])
	
# TODO: summarise the word count per image... (have I dont that?)	
# TODO: count the number of datapoints... (have I done that in another script?)
# TODO: have this run periodically in the background, and have scripts to chart progression over time...

#print_bib( "/media/michael/Files/Dropbox/workspace/2.research/1.Material/1.Manuscripts/^trx_all.txt", trx_all )
#print_bib( "/media/michael/Files/Dropbox/workspace/2.research/1.Material/1.Manuscripts/^jpg_all.txt", jpg_all )
#print_bib( "/media/michael/Files/Dropbox/workspace/2.research/1.Material/2.Official/^trx_all.txt", trx_official_all )


