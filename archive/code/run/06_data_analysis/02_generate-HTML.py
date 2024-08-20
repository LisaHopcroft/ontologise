#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import json
import os.path
import argparse
from re import search
import configparser
import pickle


def convert_to_url( fpath ):
	fpath = fpath.replace( " ", "%20" )
	fpath = fpath.replace( "^", "%5E" )
	fpath = fpath.replace( server_dir, "http://localhost:8000" )
	return fpath

if __name__ == "__main__":

	### READ COMMAND LINE ARGUMENTS

	parser = argparse.ArgumentParser(description="Generating tree visualisations from PEO/REL and PEO/PLA data sources.")

	parser.add_argument("run_dir",
						nargs='?',
						help="The directory in which to search for PEO/REL and PEO/PLA data sources",
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

	#root_dir = "/media/michael/SSD3/Dropbox/workspace/2.research" # set this globally...
	config = configparser.ConfigParser()
	config.read( '../../config.ini' )
	server_dir = config['LOCAL']['server_dir']

	# STEP 2: create a webpages linking all the family tree files
	json_paths = []
	for root, dirs, files in os.walk( run_dir + "/03_^DAT/^trees/" ):
		for fname in files:
			if fname.endswith( ".json" ) and "^trees" in root:
				print( "ADDING: " + root + "/" + fname )
				json_paths.append( "%s/%s" % ( root, fname ) )

	# vis_dir = "%s/^vis" % run_dir
	vis_dir = "%s/^vis" % run_dir
	if not os.path.exists( vis_dir ): os.mkdir( vis_dir )
	prev_dirname = ""
	with open( "%s/^trees.html" % vis_dir, "w" ) as w, open( server_dir + "/_bin/ontologize/templates/html/trees.html", "r" ) as r:
		lines = r.readlines()
		nav = ""
		for fname in sorted( json_paths ):

			# print ( "FNAME : " + fname + "\n" )
			# print ( "RUN_DIR : " + run_dir + "\n" )
			# print ( "1 : " + fname.replace(run_dir+"/","") + "\n" )
			# print ( "2 : " + fname.replace(run_dir+"/","").replace( "/03_^DAT/^trees/", " : " ) + "\n" )

			tmp = fname.replace(run_dir+"/","").replace( "/03_^DAT/^trees/", " : " )
			dirname = tmp.split( " : ", 1 )[0]
			stub = tmp.split( " : ", 1 )[1]
			if dirname != prev_dirname:
				if prev_dirname != "": nav += "</div>\n"
				nav += "<h2>%s</h2>\n<div>\n" % ( dirname )
			nav += '<a href="%s">%s</a><br/>\n' % ( convert_to_url( fname ), stub.replace(".json","") )
			prev_dirname = dirname
		for line in lines:
			w.write( line.replace( "{nav}", nav + "</div>\n" ) )
