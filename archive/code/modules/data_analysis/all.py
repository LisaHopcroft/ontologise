import os
import fnmatch
import pandas as pd
import sys

#from .postprocessing import *
#from .processing import *
#from .rdb import *
#from .surnames import *

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.data_analysis.postprocessing as postprocessing
import ontologize.modules.data_analysis.processing as processing
import ontologize.modules.data_analysis.rdb as rdb
import ontologize.modules.data_analysis.surnames as surnames


empty_vals = ["","nan",".",0.0]


def separate_surnames(pers_id):
	return surnames.strip_surname_from_pers_id(pers_id)


def df_concat_files(pattern):
	output = pd.DataFrame()
	matches = []
	for root, dirnames, filenames in os.walk('../..'):
		for filename in fnmatch.filter(filenames, pattern):
			tsv_path = (os.path.join(root, filename))
			df = pd.read_csv(tsv_path, sep='\t', lineterminator='\n')
			output = pd.concat( [output, df] )
	return output


def df_add_surname_data( filepattern, name, action="" ):
	df = df_concat_files( filepattern )
	if action:
		df = df[df['action']==action]
	df["###SURNAME"] = df["pers_id"].apply(separate_surnames)
	df = df[~df['###SURNAME'].isin(empty_vals)]
	df = df.groupby(["###SURNAME"]).size().reset_index(name='NUM')
	df[[ "VAL_HLD", "VAL_SCO", "IS_GBR_SURNAME" ]] = df["###SURNAME"].apply(surnames.add_surname_regionalism)
	df = df.sort_values(by="VAL_HLD", ascending=False)
	df.to_csv("../02_dat/%s.SURNAMES.tsv" % name, index=False, sep='\t')
	df_analysis_surname_simple( df )

	return df


def df_analysis_surname_simple( df ):

	num_TOT = int(len(df.index))
	num_GBR = int(df["IS_GBR_SURNAME"].sum())
	print
	print( "ALL" )
	print( "%s %% HLD" % round( df["VAL_HLD"].mean(), 2 ) )
	print( "%s %% SCO" % round( df["VAL_SCO"].mean(), 2 ) )
	print( "%s / %s (%s %%) GBR" % ( num_GBR, num_TOT, round( (num_GBR / float(num_TOT)) * 100, 2 ) ) )

	# remove the non GBR names...
	#gbr_only = df.dropna(subset=["IS_GBR_SURNAME"])
	gbr_only = df[~df['IS_GBR_SURNAME'].isin(empty_vals)]
	print( "" )
	print( "ALL (GBR only)" )
	print( "%s %% HLD" % round( gbr_only["VAL_HLD"].mean(), 2 ) )
	print( "%s %% SCO" % round( gbr_only["VAL_SCO"].mean(), 2 ) )
	print( len(gbr_only.index) )

	print( "" )
