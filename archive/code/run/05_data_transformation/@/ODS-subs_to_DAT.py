#!/usr/bin/python

import sys
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")

try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *
import sqlite3
from util.ods2csv import *
import os, time
from util.util import *


override = False
if len(sys.argv) > 1:
	arg = sys.argv[1]
	if arg == "override":
		override = True


def write_totals( dirname, suffix, reports, path ):
	writepath = path.replace("02_ODS", "03_^DAT") + "." + suffix + "-totals.tsv" ## todo: insert ^ before the filename 

	folder = writepath.rsplit("/",1)[0]
	if not os.path.exists( folder ):
		os.mkdir( folder )

	with open(writepath, "wb") as outfile:
		w = csv.writer( outfile, delimiter='\t' )
		row = []
		row.append( "Beneficiary" )
		row.append( "Series" )
		row.append( "Location" )
		row.append( "Num_entries" )
		row.append( "Tot_amt" )
		row.append( "Avg_amt" )
		w.writerow( row )

		for beneficiary, serieses in reports.iteritems():
			for series, reports in serieses.iteritems():
				if beneficiary and beneficiary != "":
					for report, totals in reports.iteritems():
						row = []
						row.append( beneficiary )
						row.append( series )
						row.append( report )
						row.append( totals['entries'] )
						row.append( totals['amt'] )
						row.append( totals['amt'] / totals['entries'] )
						w.writerow( row )


def write_yearly_totals( dirname, suffix, reports, path ):
	writepath = path.replace("02_ODS", "03_^DAT") + "." + suffix + ".tsv" ## todo: insert ^ before the filename 

	folder = writepath.rsplit("/",1)[0]
	if not os.path.exists( folder ):
		os.mkdir( folder )

	with open(writepath, "wb") as outfile:
		w = csv.writer( outfile, delimiter='\t' )
		row = []
		row.append( "Beneficiary" )
		row.append( "Series" )
		row.append( "Location" )
		row.append( "Year" )
		row.append( "Amt" )
		w.writerow( row )

		for beneficiary, serieses in reports.iteritems():
			for series, reports in serieses.iteritems():
				if beneficiary and beneficiary != "":
					for report, totals in reports.iteritems():
						for total, years in totals.iteritems():
							row = []
							row.append( beneficiary )
							row.append( series )
							row.append( report )
							row.append( total )
							row.append( years )
							w.writerow( row )


for root, dirs, files in os.walk("/media/michael/Files/Dropbox/workspace/2.research/1.Material/"):
	for fname in files:
		if( "@SUBSCRIBERS" in fname or "@DONATIONS" in fname or "@SUBS" in fname ) and fname.endswith(".ods"):

			#if directory has @ then move up a dir - some weird error ????
			if "@" in root.split("/")[-1]:
				root = root.rsplit('/',1)[0]

			path = os.path.join(root, fname)

			ods2csv(path)
			csv_root, csv_ext = os.path.splitext(path)
			csv_path, csv_filename = csv_root.rsplit( "/", 1 )
			csv_filepath = "%s/^%s.csv" % ( csv_path, csv_filename )

			dirname = os.path.dirname(os.path.dirname(root))

			with open(csv_filepath,"rb") as infile:
				reader = csv.reader(infile, delimiter=',', quotechar='"')
				firstrow = next(reader) #read first line
				#print firstrow

				if not "###AT" in firstrow:
					print path
					print "****MISSING ###AT****"
					continue
				if not "###AMT_STG" in firstrow:
					print path
					print "****MISSING ###AMT_STG****"
					continue
				if not "###BENEFICIARY" in firstrow:
					print path
					print "****MISSING ###BENEFICIARY****"
					continue
				if not "###SERIES" in firstrow:
					print path
					print "****MISSING ###SERIES****"
					continue
				if not "###PERS_ID" in firstrow:
					print path
					print "****MISSING ###SERIES****"
					continue

				reports_yearly = {}
				reports_colony = {}
				reports_region = {}
				reports_place = {}
				reports_transactions = {}

				if not "###DATE" in firstrow:
					print path
					print "*****MISSING ###DATE*****"
					break

				infile.seek(0)
				r = csv.DictReader( infile )

				for row in r:
					loc_now 	= row[ "###AT" ]
					beneficiary = row[ "###BENEFICIARY" ]
					series 		= row[ "###SERIES" ]
					amt_stg 	= row[ "###AMT_STG" ]
					date    	= row[ "###DATE" ]
					pers_id    	= row[ "###PERS_ID" ]

					if pers_id:
						if pers_id.startswith("+") and pers_id != "+Multiple": # exclude non individual subscriptions
							continue

					if ( not amt_stg or amt_stg == "0" ) and "###NUM_COPIES" in row:
						amt_stg = row[ "###NUM_COPIES" ]

					if not loc_now:
						loc_now = "..."

					if not beneficiary in reports_yearly:
						reports_yearly[ beneficiary ] = {}
					if not beneficiary in reports_colony:
						reports_colony[ beneficiary ] = {}
					if not beneficiary in reports_region:
						reports_region[ beneficiary ] = {}
					if not beneficiary in reports_place:
						reports_place[ beneficiary ] = {}

					if not series in reports_yearly[ beneficiary ]:
						reports_yearly[ beneficiary ][ series ] = {}
					if not series in reports_colony[ beneficiary ]:
						reports_colony[ beneficiary ][ series ] = {}
					if not series in reports_region[ beneficiary ]:
						reports_region[ beneficiary ][ series ] = {}
					if not series in reports_place[ beneficiary ]:
						reports_place[ beneficiary ][ series ] = {}

					if "Q.Trans" in row and "Q.Indiv/Group" in row:
						if not beneficiary in reports_transactions:
							reports_transactions[ beneficiary ] = {}

						if not series in reports_transactions[ beneficiary ]:
							reports_transactions[ beneficiary ][ series ] = {}

						trans_type = row["Q.Trans"]
						indiv_group = row["Q.Indiv/Group"]

						if trans_type != '' and indiv_group != '':
							if not indiv_group in reports_transactions[ beneficiary ][ series ]:
								reports_transactions[ beneficiary ][ series ][ indiv_group ] = {}
							if not trans_type in reports_transactions[ beneficiary ][ series ][ indiv_group ]:
								reports_transactions[ beneficiary ][ series ][ indiv_group ][ trans_type ] = float(amt_stg)
							else:
								reports_transactions[ beneficiary ][ series ][ indiv_group ][ trans_type ] += float(amt_stg)

					## add to yearly totals
					if amt_stg and not amt_stg == ".":
						if date and not date == ".":
							year = date[:4]
						else:
							year = "NA"
						
						# set up blank records
						if not "WIN" in reports_yearly[ beneficiary ][ series ]:
							reports_yearly[ beneficiary ][ series ][ "WIN" ] = {}
						if not "TOT" in reports_yearly[ beneficiary ][ series ]:
							reports_yearly[ beneficiary ][ series ][ "TOT" ] = {}
						if not year in reports_yearly[ beneficiary ][ series ][ "WIN" ]:
							reports_yearly[ beneficiary ][ series ][ "WIN" ][ year ] = 0
						if not year in reports_yearly[ beneficiary ][ series ][ "TOT" ]:
							reports_yearly[ beneficiary ][ series ][ "TOT" ][ year ] = 0

						if loc_now.startswith( "WIN, " ):
							reports_yearly[ beneficiary ][ series ][ "WIN" ][ year ] += float(amt_stg)
						
						reports_yearly[ beneficiary ][ series ][ "TOT" ][ year ] += float(amt_stg)
				
					## add to colony totals
					if loc_now and amt_stg:
						if loc_now.startswith( "WIN, " ):
							colony = loc_now[5:8]  # cut off the ZONE section ... "WIN, " "SCO, " etc...

							if amt_stg != "" and amt_stg != " " and amt_stg != "0" and amt_stg != "[...]" and amt_stg != ".":

								# set up blank records
								if not "NUL" in reports_colony[ beneficiary ][ series ]:
									reports_colony[ beneficiary ][ series ]['NUL'] = {}
									reports_colony[ beneficiary ][ series ]['NUL']["entries"] = 1 # avoid division by zero
									reports_colony[ beneficiary ][ series ]['NUL']["amt"] = 0 

								if colony in reports_colony[ beneficiary ][ series ]:
									reports_colony[ beneficiary ][ series ][colony]['entries'] += + 1
									reports_colony[ beneficiary ][ series ][colony]['amt']     += float(amt_stg)
								else:
									reports_colony[ beneficiary ][ series ][colony] = {'entries':1, 'amt': float(amt_stg)}

					## add to region totals
					if amt_stg and amt_stg != "" and amt_stg != " " and amt_stg != "0" and amt_stg != "[...]" and amt_stg != ".":
						if len(loc_now) < 3:
							region = "OTH"
						else:
							region = loc_now[:3]

						# set up blank records ... 20160928: why?
						#if not "NUL" in reports_region[ beneficiary ][ series ]:
						#	reports_region[ beneficiary ][ series ]['NUL'] = {}
						#	reports_region[ beneficiary ][ series ]['NUL']["entries"] = 1 # avoid division by zero
						#	reports_region[ beneficiary ][ series ]['NUL']["amt"] = 0 

						if region in reports_region[ beneficiary ][ series ]:
							reports_region[ beneficiary ][ series ][ region ]['entries'] += 1
							reports_region[ beneficiary ][ series ][ region ]['amt']     += float(amt_stg)
						else:
							reports_region[ beneficiary ][ series ][ region ] = {'entries': 1, 'amt': float(amt_stg)}

					## add to place totals
					if amt_stg and amt_stg != "" and amt_stg != " " and amt_stg != "0" and amt_stg != "[...]" and amt_stg != ".":

						# set up blank records
						if not "NUL" in reports_place[ beneficiary ][ series ]:
							reports_place[ beneficiary ][ series ]['NUL'] = {}
							reports_place[ beneficiary ][ series ]['NUL']["entries"] = 1 # avoid division by zero 
							reports_place[ beneficiary ][ series ]['NUL']["amt"] = 0

						if loc_now in reports_place[ beneficiary ][ series ] and loc_now != '':
							reports_place[ beneficiary ][ series ][loc_now]['entries'] += 1
							reports_place[ beneficiary ][ series ][loc_now]['amt']     += float(amt_stg)
						else:
							reports_place[ beneficiary ][ series ][loc_now] = {'entries':1, 'amt': float(amt_stg)}

				write_totals( dirname, "colony", reports_colony, csv_filepath )
				write_totals( dirname, "region", reports_region, csv_filepath )
				write_totals( dirname, "place",  reports_place,  csv_filepath )
				write_yearly_totals( dirname, "yearly-totals", reports_yearly, csv_filepath )	
				writepath = csv_filepath.replace("02_ODS", "03_^DAT") + ".transtype-totals.tsv"

				if reports_transactions:
					print reports_transactions
					with open( writepath, "w" ) as w:
						w.write( "Beneficiary\tSeries\tIndiv/Group\tTransType\tAmt\n" )
						for bname, benefs in reports_transactions.iteritems():
							for sname, series in benefs.iteritems():
								for grpname, grps in series.iteritems():
									for transtype, val in grps.iteritems():
										w.write( "%s\t%s\t%s\t%s\t%s\n" % (bname, sname, grpname, transtype, val) )

