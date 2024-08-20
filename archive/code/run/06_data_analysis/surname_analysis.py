#!/usr/bin/python

# Perform the regionality analysis on every list containing ###PERS_ID...

import csv, os, sys
import pd
bin_path = "/media/michael/Files/Dropbox/workspace/2.research/_bin"
sys.path.append( bin_path )
from util.util import *

import sqlite3
conn = sqlite3.connect('/media/michael/Files/Dropbox/workspace/2.research/_rdb/02_RDB/db.sqlite')
c = conn.cursor()


if len( sys.argv ) > 1:
	groupby = sys.argv[1]
	print groupby

rootpath = os.getcwd()


for root, dirs, files in os.walk( rootpath ):
	for filename in files:
		if is_dat_file(filename):

			filepath = "%s/%s" % ( root, filename )
			writepath = filepath.replace( "02_ODS", "03_^DAT" ) + ".SURNAME.tsv"

			df = pd.read_table( filepath )

			if "###PERS_ID" in df:
				for index, row in df.iterrows():
					pers_id = str(row["###PERS_ID"])
					surname = strip_surname_from_pers_id(pers_id)

					VAL_HLD, VAL_SCO, IS_GBR_SURNAME = get_surname_regionalism(surname)

					df.at[index,"VAL_HLD"] 			= VAL_HLD
					df.at[index,"VAL_SCO"] 			= VAL_SCO
					df.at[index,"IS_GBR_SURNAME"] 	= IS_GBR_SURNAME

					df.to_csv(writepath, sep='\t')

					# then do some summary analysis... allow fieldnames to be passed to this script for groupby
					# and draw plots of results in 04_^FIG
