import os
import sys
import traceback
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
from util.ods2csv import *
from util.util import *

for root, dirs, files in os.walk("/media/michael/Files/Dropbox/workspace/2.research/1.Material/"):
	for filename in files:
		if "[#COMP]" in filename and filename.endswith(".ods"):
			filepath = root + "/" + filename

			ods2csv(filepath)
			csv_path, csv_filename = filepath.rsplit( "/", 1 )
			csv_filepath = "%s/^%s.csv" % ( csv_path, csv_filename )
				
			dirname = os.path.dirname(os.path.dirname(root))

			with open(csv_filepath,"rb") as infile:
				reader = csv.reader(infile, delimiter=',', quotechar='"')
				firstrow = next(reader) #read first line

				compensation_report = {}

				infile.seek(0)
				r = csv.DictReader( infile )

				for row in r:
					try:
						pers_uclid	= row["###PERS_UCLID"]
						pers_id     = row["^PERS_ID"]
						sex		= row["^SEX"]
						ex		= row["^EX"]
						wi		= row["^WI"]
						re		= row["^RE"]
						mer		= row["^MERCHANT"]
						inh		= row["^INHERITOR"]
						at			= row["###AT"]
						born_in		= row["^BORN_IN"]
						died_in		= row["^DIED_IN"]
					except KeyError:
						print "KeyError"
						traceback.print_exc()
						break
	
					if not pers_uclid in compensation_report and pers_id != "." and pers_id != "...":
						compensation_report[ pers_uclid ] = {}
						compensation_report[ pers_uclid ][ "pers_id" ] = pers_id
						compensation_report[ pers_uclid ][ "sex" ] = sex
						compensation_report[ pers_uclid ][ "ex" ] = ex
						compensation_report[ pers_uclid ][ "wi" ] = wi
						compensation_report[ pers_uclid ][ "re" ] = re
						compensation_report[ pers_uclid ][ "mer" ] = mer
						compensation_report[ pers_uclid ][ "inh" ] = inh
						compensation_report[ pers_uclid ][ "at" ] = at
						compensation_report[ pers_uclid ][ "born_in" ] = born_in
						compensation_report[ pers_uclid ][ "died_in" ] = died_in

				writepath = filepath.replace("02_ODS/", "03_^DAT/^") + ".tsv"
				with open( writepath, "w" ) as w:
					keys = [ "###PERS_UCLID", "###PERS_ID", "###SEX", "###EX", "###WI", "###RE", "###MERCHANT", "###AT", "###BORN_IN", "###DIED_IN"]
					w.write( "\t".join( str(v) for v in keys ) + "\n" )

					for key, val in compensation_report.iteritems():
						val_list = [ key, val["pers_id"], val[ "sex" ], val[ "ex" ], val[ "wi" ], val[ "re" ], val[ "mer" ], val[ "at" ], val[ "born_in" ], val[ "died_in" ] ]
						w.write( "\t".join( str(v) for v in val_list ) + "\n" )
