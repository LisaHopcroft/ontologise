#!/usr/bin/python

## CONVERT SEMI-FORMATTED TRANSCRIPTION TEXT TO TSV DATA, USING BESPOKE CODE-BASED ALGORITHMS

import sys
import re
import itertools
from subprocess import call
import operator
import copy
import os

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.all as util
import ontologize.modules.data_transformation.all as prep
import ontologize.modules.data_transformation.autoparse.all as autoparse



is_override = False
run_dir = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/00.WWW/BLEAP, British Library Endangered Archive Program/EAP.688, St Vincent - Deeds/03a, 1788"

if len(sys.argv) > 1:
	run_dir = sys.argv[1]

def parse_microformats( run_dir, trx_root ):
	for root, dirs, files in os.walk( trx_root, topdown=True ):
		for fname in files:
			if fname.endswith(".txt") and not fname.startswith("^"):
				filepath = "%s/%s" % ( root, fname )

				PEOPLA_dat 		= []
				SAILING_dat 	= []
				PRICES_dat 		= []
				PASSAGE_dat 	= []
				src_type 		= ""
				context_date 	= ""
				context_at		= ""
				last_item_line_num		= None

				writepath = filepath.replace( "02_MKD", "03_^DAT" ).replace( "02_TXT", "03_^DAT" ).replace( "02_NOTES", "03_^DAT" )
				writepath = prep.insert_caret( writepath )

				with open(filepath, 'r') as r:
					for i, line in enumerate( r ):

						if line.lower().startswith( "##date:" ):
							context_date 	= line.lower().replace( "##date:", "" ).strip()
						if line.lower().startswith( "##at:" ):
							context_at 		= line[5:].strip()

						if line.startswith( "#[" ):
							src_type = line.replace( "#[", "" ).replace( "]", "" ).strip()
							last_item_line_num = i


						if line.startswith( "[-] " ) or line.startswith( "[+] " ):
							if src_type == "EXIT-PERMIT":
								PEOPLA_dat += autoparse.algorithms.munge_EXIT_PERMIT( line, context_date, context_at, filepath, i )

							if src_type in [ "VESSELS-ENTERED", "VESSELS-ARRIVED" ]:
								SAILING_dat += autoparse.algorithms.munge_SHIPPING( line, src_type, context_date, context_at, filepath, i )

							if src_type in [ "VESSELS-CLEARED", "VESSELS-DEPARTED" ]:
								SAILING_dat += autoparse.algorithms.munge_SHIPPING( line, src_type, context_date, context_at, filepath, i )

							#if src_type in [ "PASSENGERS-ARRIVED", "PASSENGERS-DEPARTED" ]:
							#	PASSAGE_dat += autoparse.algorithms.munge_PASSAGE( line, src_type, context_date, context_at, filepath, i )

							if src_type == "AVG-PRICES":
								PRICES_dat += autoparse.algorithms.munge_AVG_PRICES( line, context_date, context_at, filepath, i )

							if src_type in [ "PERS-LIST", "MEETING", "ADDRESS", "LETTERS-AWAITING", "DONATIONS-WI", "ORPHAN-CHAMBER", "PASSENGERS-ARRIVED" ]:
								PEOPLA_dat += autoparse.algorithms.munge_PERS_ONLY( line, context_date, context_at, filepath, i, src_type )


						if line.startswith( "========================" ) and last_item_line_num: # i.e. reached the end of the source block, so write if we have to...

							if PRICES_dat:
								writepath_edit = writepath + ".[%s].munge.AVG-PRICES.tsv" % last_item_line_num

								if prep.requires_refresh( filepath, writepath_edit, "AVGPRICES", is_override ):
									util.write_listdict_to_file( writepath_edit, PRICES_dat )

								PRICES_dat = []

							if SAILING_dat:
								writepath_edit = writepath + ".[%s].munge.SAILING.tsv" % last_item_line_num

								if prep.requires_refresh( filepath, writepath_edit, "SAILING", is_override ):
									util.write_listdict_to_file( writepath_edit, SAILING_dat )

								SAILING_dat = []

							if PEOPLA_dat:
								writepath_edit = writepath + ".[%s].munge.%s.tsv" % ( last_item_line_num, src_type )

								if prep.requires_refresh( filepath, writepath_edit, src_type, is_override ):
									util.write_listdict_to_file( writepath_edit, PEOPLA_dat )

								PEOPLA_dat = []



for root, dirs, files in os.walk( run_dir, topdown=True ):
	for folder in dirs:
		if "02_TXT" in folder or "02_MKD" in folder:
			collection_root = root
			trx_root 		= "%s/%s" % ( root, folder )
			parse_microformats( collection_root, trx_root )
