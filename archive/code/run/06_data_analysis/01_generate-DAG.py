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


is_debugging_forced = False
debug_fname  = "0182, --- FULTON of Auchinbothie"


# In[376]:

def build_tree2( parent, structure, annotations, annotation_column ):

	if is_debugging: print ( "+ Tree building for %s %s" % ( parent[0], parent[1] ) )

	### --- Identifying the annotation for the current 'parent' node
	parent_annotations = ( annotations
						  .drop_duplicates(subset=['pers_id', 'pers_id_context', annotation_column ] )
						  .query( 'pers_id=="%s" & pers_id_context=="%s"' % ( parent[0], parent[1] ) )
						  .query( '%s=="Yes"' % annotation_column)
						 )

	this_class = "male"
	if parent_annotations.shape[0] > 0:
		this_class = annotation_column

	if is_debugging: print ( "> Node identified as class '%s'" % this_class )

	node = {}

	if "(" in parent[1]:
		pers_id_context_safe = "c" + parent[1].replace("(","").replace(")","")
	else:
		pers_id_context_safe = parent[1]

	node["name"] = parent[0].lower().replace(", ","_").replace(" ","_") + pers_id_context_safe
	node["class"] = this_class

	surname = ""
	forenames = ""
	if ", " in parent[0]:
		surname = parent[0].split(", ")[0]
		forenames = parent[0].split(", ")[1]
	else:
		surname = parent[0]


	node["extra"] = {}
	node["extra"]["surname"]   = surname
	node["extra"]["forenames"] = forenames
	node["extra"]["context"]   = parent[1]

	if this_class == "in_WIN":
		node["extra"]["win_val"]    = "1"
	else:
		node["extra"]["win_val"]    = "0"

	structure_children = structure.query( 'pers2_id=="%s" & pers2_id_context=="%s"' % ( parent[0], parent[1] ) )
	children_ids = structure_children[["pers1_id","pers1_id_context"]].to_records(index=False)
	# TODO: make sure this is just unique children...

	if is_debugging: print ( "> Node has %d children" % len( children_ids ) )

	if len(children_ids)>0:
		m = {}
		m["spouse"] = {}
		m["spouse"]["name"] = "."
		m["spouse"]["class"] = "unknown"
		m["children"] = []
		for child in children_ids:
			m["children"].append( build_tree2( child, structure, annotations, annotation_column ) )
			# TODO: implement a way of detecting recursion and stopping the script gracefully - enforce the rule: "someone can't be a child of themselves!"
		node["marriages"] = [ m ]

	return node


# In[377]:


def convert_DAT_to_tree2( root, peorel_file, peopla_file ):

	##########################################################
	### STEP 1: read in and process data from PEO/REL file ###
	##########################################################

	if is_debugging: print( "+ Reading PEO/REL file\n> " + peorel_file )
	print( peorel_file )
	PEOREL_in = pd.read_csv(peorel_file, "\t", header=0)
	if is_debugging: print ( "> Rows = %d, Columns = %d\n" % PEOREL_in.shape )

	### Filter dataframe for son/daughter/child relationships
	### https://stackoverflow.com/questions/12065885/filter-dataframe-rows-if-value-in-column-is-in-a-set-list-of-values/46460307#46460307
	rel_list = ["SON","DAUG","CHILD"]
	PEOREL_d = ( PEOREL_in
				.query( "rel in @rel_list" )
				.drop_duplicates(subset=['src_ref', 'src_linenum', 'pers1_id', 'pers2_id']))
	PEOREL_d[ "pers1_id_context" ] = PEOREL_d[ "pers1_id_context" ].astype(str)
	PEOREL_d[ "pers2_id_context" ] = PEOREL_d[ "pers2_id_context" ].astype(str)

	if is_debugging: print( "+ Filtering PEO/REL data for " + "/".join( rel_list ) )
	if is_debugging: print( "+ Removing duplicationes [of src_ref/src_linenum]" )
	if is_debugging: print ( "> Rows = %d, Columns = %d\n" % PEOREL_d.shape )

	### Pickling the relationships so that we can pick this back
	### up again at a later date.
	PICKLE_file = "%s.pickle" % ( peorel_file.replace("03_^DAT", "03_^DAT/^pickles") )
	PICKLE_dir  = os.path.dirname(PICKLE_file)

	if is_debugging: print( "+ Writing to PICKLE dir: %s" % PICKLE_dir )
	if not os.path.exists( PICKLE_dir ): os.mkdir( PICKLE_dir )

	pickle_out = open( PICKLE_file, "wb" )
	pickle.dump( PEOREL_d, pickle_out )
	pickle_out.close()

	##########################################################
	### STEP 2: read in and process data from PEO/PLA file ###
	###		 (if present)							   ###
	##########################################################
	locations_of_interest = ["LWH","WIN"]
	PEOPLA_annotated = ()

	if os.path.exists(peopla_file):
		if is_debugging: print( "+ Reading PEO/PLA file\n> " + peopla_file )
		PEOPLA_in = pd.read_csv( peopla_file, "\t", header=0 )
		PEOPLA_in[ "pers_id_context" ] = PEOPLA_in[ "pers_id_context" ].astype(str)
		PEOPLA_in[ "place_id" ] = PEOPLA_in[ "place_id" ].astype(str)
		if is_debugging: print ( "> Rows = %d, Columns = %d\n" % PEOPLA_in.shape )

		PEOPLA_annotated = PEOPLA_in

		### --- Adding flags for locations of interest
		for location in locations_of_interest:
			new_col = "in_" + location
			if is_debugging: print ( "+ Adding annotation '%s' for place_ids containing '%s'" % (new_col, location))
			PEOPLA_annotated[new_col] = ( PEOPLA_annotated['place_id']
										 .apply( lambda x : detect_country(x,location) ) )
	else:
		### --- If no PEOPLA file exists, generate an empty one,
		### --- adding default values of "No" for the location annotations
		### --- that we're interested in
		group1_people = ( PEOREL_d[["src_ref",
									   "src_pp",
									   "src_pp_original",
									   "src_linenum",
									   "src_linenum_original",
									   "pers1_id",
									   "pers1_id_context"]]
						 .rename(columns={'pers1_id': 'pers_id', 'pers1_id_context': 'pers_id_context'}) )
		group2_people = ( PEOREL_d[["src_ref",
									   "src_pp",
									   "src_pp_original",
									   "src_linenum",
									   "src_linenum_original",
									   "pers2_id",
									   "pers2_id_context"]]
						 .rename(columns={'pers2_id': 'pers_id', 'pers2_id_context': 'pers_id_context'}) )

		PEOPLA_annotated = ( group1_people
							.append( group2_people )
							.drop_duplicates(subset=['src_ref','src_linenum','pers_id', 'pers_id_context'] ) )

		for location in locations_of_interest:
			new_col = "in_" + location
			if is_debugging: print ( "+ No PEOPLA data, using default values in '%s'" % (new_col))
			PEOPLA_annotated[new_col] = "No"

	##########################################################
	### STEP 4: Check for multiple root nodes ################
	##########################################################
	### Identifying how many root nodes there are, so that an error
	### message can be generated and the file name recorded.
	###
	### This step is done by merging the database with itself - any
	### person who does not have a "parent" in the tree structure
	### will have NA in pers1_id_r column.  By filtering the merged
	### dataset for NAs in this column, we will find the root nodes.
	### Note that I've used a hacky way of identifying NAs here
	### (NaN does not equal itself).
	##########################################################

	root_nodes_d = ( PEOREL_d
					.merge( PEOREL_d[["pers1_id","pers1_id_context"]],
						   how="left",
						   left_on=["pers2_id","pers2_id_context"],
						   right_on=["pers1_id","pers1_id_context"],
						   suffixes=('', '_r') )
					.query( "pers1_id_r != pers1_id_r" ) # Hacky way to find NaNs
					.drop_duplicates(subset=['pers2_id', 'pers2_id_context'] ) )

	### to_records() converts a DataFrame to a NumPy record array.
	root_nodes = root_nodes_d[["pers2_id", "pers2_id_context", "src_linenum"]].to_records(index=False)

	if is_debugging: print ( "> There are %d root nodes" % len( root_nodes ) )

	if len( root_nodes ) > 1:
		if is_debugging: print ( "<!> WARNING: Multiple trees (n=%d)" % len( root_nodes ) )
		for pid in root_nodes:
			print( "  - %s: %s %s" % ( pid[2], pid[0], pid[1] ) )
		error_msgs.append( peorel_file )

	i = 1

	print( root_nodes )
	for this_root in root_nodes:
		if len( root_nodes ) > 1 and i>1: identifier = "_%s" % i
		else: identifier = ""

		tree = build_tree2( this_root, PEOREL_d, PEOPLA_annotated, "in_WIN" )

		stub = peorel_file.split("03_^DAT",1)[1]
		dirpath = peorel_file.split("03_^DAT",1)[0]
		vis_dir = "%s/%s" % ( dirpath, "04_^VIS" )
		trees_dir = "%s/%s" % ( vis_dir, "^trees" )
		#DAG_dir = "%s/%s/%s" % ( dirpath, "03_^DAT", "^trees" )
		#PICKLE_dir = "%s/%s/%s" % ( dirpath, "03_^DAT", "^pickles" )

		if is_debugging:
			print( "+ Writing to DAG dir: %s" % DAG_dir )
			print( "+ Writing to PICKLE dir: %s" % PICKLE_dir )
			# print( "+ Writing to visualisation dir: %s" % vis_dir )
			# print( "+ Writing to trees dir: %s" % trees_dir )

		#if not os.path.exists( DAG_dir ): os.mkdir( DAG_dir )
		#if not os.path.exists( PICKLE_dir ): os.mkdir( PICKLE_dir )
		if not os.path.exists( vis_dir ): os.mkdir( vis_dir )
		if not os.path.exists( trees_dir ): os.mkdir( trees_dir )

		### Pickling the JSON object so that we can pick this back
		### up again at a later date.
		#PICKLE_filepath = "%s/%s" % ( PICKLE_dir, stub.replace(".PEO_REL.tsv", "%s.pickle" % identifier) )
		#pickle_out = open( PICKLE_filepath , "wb" )
		#pickle.dump( tree, pickle_out )
		#pickle_out.close()

		### Currently the same output is written out to the DAG_filepath
		### and the json_filepath. However, the longer term intention is that
		### the RAW json representating the STRUCTURE of the relationship should
		### be written to the DAG_filepath, and an ANNOTATED json file (with additional
		### information relevant to visualisation) should be written to the json_filepath.
		#DAG_filepath = "%s/%s" % ( DAG_dir, stub.replace(".PEO_REL.tsv", "%s.json" % identifier) )
		#with open( DAG_filepath, "w" ) as w:
		#	w.write( json.dumps( [ tree ] ) )

		json_filepath = "%s/%s" % ( trees_dir, stub.replace(".PEO_REL.tsv", "%s.json" % identifier) )
		print( json_filepath )
		with open( json_filepath, "w" ) as w:
		 	w.write( json.dumps( [ tree ] ) )

		i += 1


# In[378]:


def detect_country(x, country):
	if x == "nan":
		return( "No")
	elif x.find(country) != -1:
		return( "Yes" )
	else:
		return( "No" )



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

	script_dir = os.path.dirname(__file__)
	config = configparser.ConfigParser()
	config.read( script_dir + '/../../config.ini' )
	server_dir = config['LOCAL']['server_dir']

	# STEP 1: create the family tree json files

	for root, dirs, files in sorted( os.walk( run_dir ) ):
		for fname in files:

			if is_debugging_forced:
				if not debug_fname in fname: continue

			if fname.endswith( ".PEO_REL.tsv" ) and "03_^DAT" in root:
				#if not single_file in fname: continue
				peorel_file = "%s/%s" % ( root, fname )
				peopla_file = peorel_file.replace("PEO_REL", "PEOPLA", 1)
				convert_DAT_to_tree2( root, peorel_file, peopla_file )
				if is_debugging: print( "--------------------------------------------------------" )

	print( "%s files with more than one tree root." % len(error_msgs) )


	'''


	# STEP 2: create a webpages linking all the family tree files
	# MH: ...this should be a different script...

	json_paths = []
	for root, dirs, files in os.walk( run_dir + "/04_^VIS/^trees/" ):
	 	for fname in files:
	 		if fname.endswith( ".json" ) and "^trees" in root:
	 			json_paths.append( "%s/%s" % ( root, fname ) )

	vis_dir = "%s/^vis" % run_dir
	if not os.path.exists( vis_dir ): os.mkdir( vis_dir )
	prev_dirname = ""
	with open( "%s/^trees.html" % vis_dir, "w" ) as w, open( server_dir + "/_bin/ontologize/templates/html/trees.html", "r" ) as r:
	 	lines = r.readlines()
	 	nav = ""
	 	for fname in sorted( json_paths ):
	 		print ( "FNAME : " + fname + "\n" )
	 		print ( "RUN_DIR : " + run_dir + "\n" )
	 		print ( "1 : " + fname.replace(run_dir+"/","") + "\n" )
	 		print ( "2 : " + fname.replace(run_dir+"/","").replace( "/04_^VIS/^trees/", " : " ) + "\n" )

	 		tmp = fname.replace(run_dir+"/","").replace( "/04_^VIS/^trees/", " : " )
	 		dirname = tmp.split( " : ", 1 )[0]
	 		stub = tmp.split( " : ", 1 )[1]
	 		if dirname != prev_dirname:
	 			if prev_dirname != "": nav += "</div>\n"
	 			nav += "<h2>%s</h2>\n<div>\n" % ( dirname )
	 		nav += '<a href="%s">%s</a><br/>\n' % ( convert_to_url( fname ), stub.replace(".json","") )
	 		prev_dirname = dirname
	 	for line in lines:
	 		w.write( line.replace( "{nav}", nav + "</div>\n" ) )


def convert_to_url( fpath ):
	fpath = fpath.replace( " ", "%20" )
	fpath = fpath.replace( "^", "%5E" )
	fpath = fpath.replace( server_dir, "http://localhost:8000" )
	return fpath

	'''
