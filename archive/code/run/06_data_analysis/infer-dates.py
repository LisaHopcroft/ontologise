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
import networkx as nx
import matplotlib.pyplot as plt

config = configparser.ConfigParser()
config.read( '../../config.ini' )
server_dir = config['LOCAL']['server_dir']

sys.path.append(server_dir + "/_bin")
import ontologize.modules.inference.gender as gender
import ontologize.modules.data_transformation.family_trees as family_trees

# import sys
# print(sys.path)


def extract_places( peopla_file ):
	# peopla_file = "../../../../dat/03_^DAT/^0123, --- RANKINE of Largs [+].jpg.txt.PEOPLA.tsv"

	##########################################################
	### STEP 1: read in and process data from PEO/REL file ###
	##########################################################

	if is_debugging: print( "+ Reading PEO/PLA file\n> " + peopla_file )
	PEOPLA_0 = pd.read_csv( peopla_file, "\t", header=0 )
	PEOPLA_in = PEOPLA_0[ PEOPLA_0.place_id.notnull() ]
	PEOPLA_in[ "pers_id_context" ] = PEOPLA_in[ "pers_id_context" ].astype(str)
	PEOPLA_in[ "place_id" ] = PEOPLA_in[ "place_id" ].astype(str)
	if is_debugging: print ( "> Rows = %d, Columns = %d\n" % PEOPLA_in.shape )

	PEOPLA_annotated = ( PEOPLA_in[["place_id",
									"pers_id",
									"pers_id_context",
									"action"]] )

	#PEOPLA_annotated.head()
	#PEOPLA_annotated.columns



def read_json_file(filename):
    with open(filename) as f:
        js_graph = json.load(f)
    return json_graph.node_link_graph(js_graph)




if __name__ == "__main__":

	### READ COMMAND LINE ARGUMENTS

	# parser = argparse.ArgumentParser(description="Generating place info.")
	#
	# parser.add_argument("run_dir",
	# 					nargs='?',
	# 					help="The directory in which to search for PEO/PLA data sources",
	# 					default=".")
	# parser.add_argument("-v",
	# 					help="Print additional messages at run time",
	# 					action='store_true')
	#
	# args = parser.parse_args()
	#
	# is_debugging = False
	# if args.v: is_debugging = True
	#
	# run_dir = args.run_dir
	#
	# error_msgs = []

	### READ THE CONFIG FILE

	config = configparser.ConfigParser()
	config.read( '../../config.ini' )
	server_dir = config['LOCAL']['server_dir']

	# DAG_file = "/Users/lisahopcroft_tmp/Projects/History/dat/03_^DAT/^pickles/^0123, --- RANKINE of Largs [+].jpg.txt.pickle"
	# DAT_file = "/Users/lisahopcroft_tmp/Projects/History/dat/03_^DAT/^0123, --- RANKINE of Largs [+].jpg.txt.PEOPLA.tsv"
	# JSON_file = "/Users/lisahopcroft_tmp/Projects/History/dat/03_^DAT/^trees/^0123, --- RANKINE of Largs [+].jpg.txt.json"
	DAT_file = "/Users/lisahopcroft_tmp/Projects/History/dat/test/test.PEOPLA.txt"
	DAG_file = "/Users/lisahopcroft_tmp/Projects/History/dat/test/test.PEO_REL.tsv.pickle"
	peorel_file = "/Users/lisahopcroft_tmp/Projects/History/dat/test/test.PEO_REL.tsv"

	### This is a dictionary object
 	DAG_object = pickle.load( open( DAG_file, "rb" ) )
	DAG_object_specific = ( DAG_object
	.assign( pers1_id_full = lambda x: x.pers1_id + " (" + x.pers1_id_context + ")" )
	.assign( pers2_id_full = lambda x: x.pers2_id + " (" + x.pers2_id_context + ")" ) )

	# g = nx.DiGraph()
	# g.add_nodes_from(DAG_object_specific.pers1_id_full)
	# g.add_nodes_from(DAG_object_specific.pers2_id_full)
	# g.add_edges_from()

	g = nx.from_pandas_edgelist(DAG_object_specific,
	"pers1_id_full", "pers2_id_full",
	["rel"], create_using=nx.DiGraph())

	pos = nx.spring_layout(g)
	nx.draw(g, pos, with_labels=True)
	edge_labels = nx.get_edge_attributes(g,'rel')
	nx.draw_networkx_edge_labels(g, pos, edge_labels)
	plt.show()

	target = 'RANKINE, Mary (246)'
	target_parents  = family_trees.get_parents ( g, target )
	target_siblings = family_trees.get_siblings( g, target )

	### ------------------------------------------------------------ ###
	### STEP 1: EXPANDING BY SELF ---------------------------------- ###
	### ------------------------------------------------------------ ###

	RULES = pd.read_csv( "ref/RULES-dates.txt",sep="\t" )

	PEOPLA_in = pd.read_csv( DAT_file, "\t", header=0 )
	PEOPLA_0  = PEOPLA_in[["pers_id","pers_id_context","action","place_id","place_txt","date1_y"]]
	PEOPLA_0  = PEOPLA_0[ PEOPLA_0.date1_y.notnull() ]

	PEOPLA_0_project_forward = ( PEOPLA_0
						.merge( RULES,
								how="left",
								left_on=["action"],
								right_on=["ACTION1"])
						.assign( prediction_text = lambda x: "Derived from " + x.action )
						.assign( prediction_min  = lambda x: x.date1_y + x.MIN_ADDITION )
						.assign( prediction_max  = lambda x: x.date1_y + x.MAX_ADDITION )
						.drop( columns=["ACTION1"] )
						.rename( columns = {'ACTION2':'predicted_action'} ) )

	PEOPLA_0_project_backward = ( PEOPLA_0
					.merge( RULES,
							how="left",
							left_on=["action"],
							right_on=["ACTION2"])
					.assign( prediction_text = lambda x: "Derived from " + x.action  )
					.assign( prediction_min  = lambda x: x.date1_y - x.MIN_ADDITION )
					.assign( prediction_max  = lambda x: x.date1_y - x.MAX_ADDITION )
					.drop( columns=["ACTION2"] )
					.rename( columns = {'ACTION1':'predicted_action'} ) )

	PEOPLA_0_projected = ( PEOPLA_0[["pers_id","pers_id_context","action", "date1_y"]]
							.assign( MIN_ADDITION = np.nan )
							.assign( MAX_ADDITION = np.nan )
							.assign( predicted_action = np.nan )
							.assign( prediction_text = np.nan )
							.assign( prediction_min = np.nan )
							.assign( prediction_max = np.nan )
							.append( PEOPLA_0_project_backward, sort=True )
							.append( PEOPLA_0_project_forward, sort=True ) )

	### ------------------------------------------------------------ ###
	### STEP 2: EXPANDING BY PARENTS ------------------------------- ###
	### ------------------------------------------------------------ ###


	### ------------------------------------------------------------ ###
	### STEP 3: EXPANDING BY SIBLINGS ------------------------------ ###
	### ------------------------------------------------------------ ###
