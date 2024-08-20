#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
import argparse


# Summary:
# - Find married couples in the PEOPLA data and add relevant entries to PEO_REL data


# run_dir = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch/359031, Cairn of Lochwinyoch matters, 1827-37"
# change this to also take a command line argument...



def get_spouse_rels( fpath ):
    d = pd.read_csv(fpath, "\t", header=0)

    # dplyr		pandas equivalent
    # head		head
    # mutate	assign
    # select	filter
    # rename	rename
    # filter	query
    # arrange	sort_values
    # group_by	groupby
    # summarize	agg

    ### FILTER THE DATA FRAME TO ONLY FIND THOSE MARRIED RECORDS
    # https://stmorse.github.io/journal/tidyverse-style-pandas.html
    d_married = ( d.query( 'action=="MARRIED"' ) )

    ### GROUP THE MARRIAGES THAT ARE ON THE SAME LINE
    married_grouping = ( d_married.groupby( ['src_linenum'] ) )

    ### ADD A COLUMN TO IDENTIFY THE 1st/2nd (3rd?) PERSON IN EACH MARRIAGE
    d_married['person_number'] = married_grouping['src_linenum'].rank(method="first", na_option="top")

    ### PIVOT (equivalent of pivot_wider() in R)
    d_married_wide = d_married.pivot(index='src_linenum', columns='person_number', values='pers_id')

    return d_married_wide

    #TODO: return the new found spouse rels as a list
    #
    # 	PEO_REL example:
    #
    #	src_ref										src_linenum		pers1_id			pers1_id_context	rel		pers2_id			pers2_id_context
    #	01.01.01.00.FS.359031.1419516.02_TXT.0306	291				WILSON, Margaret	291					SPOUSE	WILSON, William		(4)


# In[ ]:


def get_spouse_rels2( fpath ):
    if is_debugging: print ( "+ Identifying spouses from %s" % ( fpath ) )

    d = pd.read_csv(fpath, "\t", header=0)

    spouse_results = None

    ### FILTER THE DATA FRAME TO ONLY FIND THOSE MARRIED RECORDS
    # https://stmorse.github.io/journal/tidyverse-style-pandas.html
    d_married = ( d.query( 'action=="MARRIED"' ) )

    if d_married.shape[0]>0:
	    ### GROUP THE MARRIAGES THAT ARE ON THE SAME LINE
	    married_grouping = ( d_married.groupby( ['src_linenum'] ) )

	    ### ADD A COLUMN TO IDENTIFY THE 1st/2nd (3rd?) PERSON IN EACH MARRIAGE
	    d_married['person_number'] = married_grouping['src_linenum'].rank(method="first", na_option="top")

	    # https://stackoverflow.com/questions/52069315/valueerror-when-trying-to-have-multi-index-in-dataframe-pivot
	    # WARNING is caused: fix here? https://www.dataquest.io/blog/settingwithcopywarning/

	    ### PIVOT WIDER - to find the names
	    ### (1) Add the variable to pivot on
	    d_married['person_number_text'] = np.where(d_married['person_number']==1, "pers1_id", "pers2_id")
	    ### (2) Do the pivot
	    wide_names = (d_married.set_index(["src_ref", "src_linenum"])
	                      .pivot(columns="person_number_text")['pers_id']
	                      .reset_index()
	                      .rename_axis(None, axis=1) )

	    ### PIVOT WIDER - to find the name contexts
	    ### (1) Add the variable to pivot on
	    d_married['person_number_text'] = np.where(d_married['person_number']==1, "pers1_id_context", "pers2_id_context")
	    ### (2) Do the pivot
	    wide_context = (d_married.set_index(["src_ref", "src_linenum"])
	                      .pivot(columns="person_number_text")['pers_id_context']
	                      .reset_index()
	                      .rename_axis(None, axis=1) )

	    ### MERGE THE TWO PIVOTS
	    wide_results = pd.merge(wide_names, wide_context,
	                           left_on=["src_ref", "src_linenum"],
	                           right_on=["src_ref", "src_linenum"])
	    wide_results["rel"] = "SPOUSE"

	    if is_debugging: print ( "> %d spouse pairs identified" % ( wide_results.shape[0] ) )
	    
	    spouse_results = wide_results[["src_ref","src_linenum",
	                        "pers1_id","pers1_id_context",
	                        "rel",
	                        "pers2_id","pers2_id_context"]]
    
    return ( spouse_results )


# In[ ]:


if __name__ == "__main__":

    ### READ COMMAND LINE ARGUMENTS
    
    parser = argparse.ArgumentParser(description="Identify spouses in a PEO/PLA resource")

    parser.add_argument("run_dir",
                        nargs='?',
                        help="The directory in which to search for PEO/PLA data sources",
                        default=".")
    parser.add_argument("-v",
                        help="Print additional messages at run time",
                        action='store_true')

    args = parser.parse_args()

    is_debugging = False
    if args.v: is_debugging = True

    run_dir = args.run_dir

    error_msgs = []

    for root, dirs, files in os.walk( run_dir ):
        for fname in files:
            if fname.endswith(".PEOPLA.tsv"):
                spouse_rels = get_spouse_rels2( "%s/%s" % ( root, fname ) )
                print( spouse_rels )
                
                #TODO: append these spouse rels to the relevant PEO_REL file

