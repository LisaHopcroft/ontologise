#!/usr/bin/python

import sys
import re
import os
import csv
from subprocess import call

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.all as util
import ontologize.modules.util.confdat as confdat
import ontologize.modules.data_transformation.all as prep
import ontologize.modules.data_analysis.all as osynth

try:
	# for Python2
	from Tkinter import *
except ImportError:
	# for Python3
	from tkinter import *


run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/SP, Scotlands Places"

if len(sys.argv) > 1:
	run_dir = sys.argv[1]

is_override = True


PEOPLA_patterns = [
	{ 	"match": 		"###AT",
		"action": 		"ACTION",
		"pers_id": 		"PERS_ID",
		"place_id": 	"AT",
		"date": 		"DATE",
		"pers_aged": 	"AGED",
		"pers_sex":		"SEX",
		"pers_race": 	"RACE",
		"latitude": 	"^LATITUDE",
		"longitude": 	"^LONGITUDE",
	},
]


def requires_refresh( filepath, writepath, tbl_name ):
	if is_override: return True

	writepath = "%s.%s.tsv" % ( writepath, tbl_name )
	if os.path.exists( writepath ):
		if os.path.getmtime( writepath ) > os.path.getmtime( filepath ):
			return False

	return True


def get_collection_path( filepath ):
	dirpath = os.path.dirname( filepath )
	dirname = dirpath.rsplit( "/", 1 )[1]
	if dirname.startswith( ( "01", "02", "03" ) ):
		return os.path.dirname( dirpath )
	return get_collection_path( dirpath )


def get_identifier_specific_value_if_exists( identifier, row, pattern ):
	if "###%s{%s}" % (pattern, identifier) in row:
		return row.get( "###%s{%s}" % (pattern, identifier), None )
	#else:
	#	return row.get( "###%s" % pattern, None )


def get_val_from_ranged_key( keyval, num_identifiers, first_row ):
	for key in first_row.keys():
		#if not key: return ""
		if key.startswith( keyval ) and "{" in key and ":" in key:
			val_range 	= key.split("{")[1].split("}")[0]
			start 		= val_range.split(":")[0]
			end 		= val_range.split(":")[1]
			for pos in range(int(start), int(end)+1):
				if pos == num_identifiers:
					return row.get( key, None )


for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if "@" in root: continue
		filepath = "%s/%s" % (root, fname)
		if prep.is_tagged_ODS( filepath ) or prep.is_tagged_TSV( filepath ):
			#print filepath

			DAT_dir = get_collection_path( filepath ) + "/03_^DAT"

			if not os.path.exists(DAT_dir):
				os.makedirs(DAT_dir)

			SURNAME_dat		= []
			PEOPLA_dat 		= []
			OCC_dat 		= []
			DONATION_dat 	= []
			MEMORIAL_dat 	= []
			MEMBER_dat 		= []
			POPULATION_dat 	= []

			# some surname specific stuff...
			codes = []
			for c in osynth.surnames.ALL_counties:
				codes.append( c[0] )

			cached_regions = {
				"HLD": osynth.surnames.HLD_counties,
				"SCO": osynth.surnames.SCO_counties
			}

			orig_filepath = filepath
			if prep.is_tagged_ODS( filepath ):

				# convert to TSV in a two-step process...
				prep.ods2csv(filepath)
				csv_path = '%s/^%s.csv' % (root, fname)
				tsv_path = '%s/^%s.tsv' % (root, fname)
				with open( csv_path, "r", encoding="utf8", errors='ignore' ) as r, open( tsv_path, "w", encoding="utf8" ) as w:
					for row in csv.reader(r):
						w.write( "\t".join(x.replace('\"','') for x in row) + "\n" )
				os.system( "rm '%s'" % csv_path ) # should escape the filepath...
				filepath = tsv_path

			dirname = util.get_branch_dir( filepath )
			src_ref = prep.get_ref_from_filepath( orig_filepath.rstrip() )


			#----------------------------------------------------------------------#
			# Gather data
			#----------------------------------------------------------------------#

			#print( "-------------------------------------------------------------------------------------" )
			#print( filepath )
			with open(filepath, "r") as infile:
				infile.seek(0)
				tsv = csv.DictReader( infile, delimiter="\t" )

				# Generic colon separated notation:

				write_tables = {}
				tables = {}
				first_row = next(tsv, None)
				if not first_row: continue

				# Loop over columns

				for key in first_row.keys():
					identifier = ""
					if not key: continue
					if ":" in key and key.startswith( "###" ):
						table_name = key.split(":",1)[0].replace("#","").lower()
						field_name = key.split(":",1)[1].lower()
						if "{" in field_name:
							identifier = field_name.rsplit("{")[1].rsplit("}")[0]
							field_name = field_name.rsplit("{")[0]

						if ( table_name, identifier ) in tables:
							tables[(table_name, identifier)].append( field_name )
						else:
							tables[(table_name, identifier)] = [ field_name ]
						write_tables[table_name] = []
					if ":" in key and not key.startswith( "###" ):
						print( "WARNING: Malformed key?" )

				src_type 				= ""
				src_pp 					= ""
				src_linenum_original	= ""
				src_subref				= ""
				z = 0

				# Get num identifiers

				num_identifiers = 1

				for key in first_row.keys():
					if not key: continue
					if key.startswith("###") and key.endswith("}"):
						val_range = key.split("{")[1].split("}")[0]
						if ":" in val_range: val_range = val_range.split(":")[1]
						if val_range.isdigit():
							val_range = int(val_range)
							if val_range > num_identifiers: num_identifiers = val_range

				for row in tsv:

					z += 1

					# Generic, but optionally present, values:

					if "#[]" in row:
						src_type = row["#[]"]
						#if src_type == "UK-CENSUS" or src_type == "SLAVE-REGISTER": continue ## TEMPORARY HACK to trim down database size when not needed !!! ##
					line_num = z # safer just using the ODS line num, rather than the source LINE value... (todo: add PP and LINE to the database?)
					if "PP" in row: src_pp = row["PP"]

					if "LINE" in row: src_linenum_original = row["LINE"]

					if "REF" in row: src_subref = row["REF"]


					# Generic colon separated notation:

					for (table_name, identifier), field_names in tables.items():
						db_dict = prep.get_RDB_table_as_dict( ( "MF_%s" ) % table_name.replace(" ","") )
						if not db_dict: continue
						for field_name in field_names:
							if identifier:
								access_name = field_name + "{%s}" % ( identifier )
							else:
								access_name = field_name
							val = row["###%s:%s" % (table_name.upper(), access_name.upper())]
							if val == ".": val = ""
							db_dict[field_name.replace(" ", "")]	= val
						db_dict["src_filepath"] = orig_filepath.rstrip()
						if identifier:
							db_dict["src_filepath"] = db_dict["src_filepath"] + "{%s}" % ( identifier ) # hack to get a unique foreign key...
						db_dict["src_linenum"] = line_num

						write_tables[table_name].append( db_dict )


					# PEOPLA patterns:

					for pattern in PEOPLA_patterns:
						if pattern["match"] in row:
							for i in range(num_identifiers):
								i += 1
								if i > 1:
									pers_id =  row.get( "###%s{%s}" % (pattern["pers_id"], i), None )
									if not pers_id: pers_id = row.get( "###^%s{%s}" % (pattern["pers_id"], i), None )
									if not pers_id: pers_id = get_val_from_ranged_key( "###PERS_ID", num_identifiers, first_row )

									place_id 	= get_identifier_specific_value_if_exists( i, row, pattern["place_id"] )
									if not place_id: place_id = row.get( "###^AT", None )

									date_txt 	= get_identifier_specific_value_if_exists( i, row, pattern["date"] )
									longitude 	= get_identifier_specific_value_if_exists( i, row, pattern["longitude"] )
									latitude 	= get_identifier_specific_value_if_exists( i, row, pattern["latitude"] )
									action 		= get_identifier_specific_value_if_exists( i, row, pattern["action"] )
									pers_sex 	= get_identifier_specific_value_if_exists( i, row, pattern["pers_sex"] )
									pers_aged 	= get_identifier_specific_value_if_exists( i, row, pattern["pers_aged"] )
									pers_race 	= get_identifier_specific_value_if_exists( i, row, pattern["pers_race"] )
									if not action: action == "AT"

									mod_filepath = orig_filepath.rstrip() + "{%s}" % ( i ) # HACK: needed to make the foreign key unique somehow...
								else:
									pers_id 	= row.get( "###%s" % (pattern["pers_id"]), None )
									if not pers_id: pers_id = autofill_val = row.get( "###^%s" % (pattern["pers_id"]), None )
									if not pers_id: pers_id = get_val_from_ranged_key( "###%s" % (pattern["pers_id"]), 1, first_row )

									place_id 	= row.get( "###%s" % (pattern["place_id" ]), None )
									if not place_id: place_id = row.get( "###^AT", None )

									date_txt	= row.get( "###%s" % (pattern["date" ]), None )
									longitude 	= row.get( "###%s" % (pattern["longitude"]), None )
									latitude 	= row.get( "###%s" % (pattern["latitude"]), None )
									action 		= row.get( "###%s" % (pattern["action"]), None )
									pers_sex 	= row.get( "###%s" % (pattern["pers_sex"]), None )
									pers_aged 	= row.get( "###%s" % (pattern["pers_aged"]), None )
									pers_race 	= row.get( "###%s" % (pattern["pers_race"]), None )

									mod_filepath = orig_filepath.rstrip()


								# hacked together quickly...
								additional_fields = {}
								if i == 1:
									for key in first_row.keys():
										if not key: continue
										if key.startswith( "###IS_" ) and "[" in key and "]" in key:
											if row.get( key, None ) != "" and row.get( key, None ) != "." and row.get( key, None ) != "...":
												col = key.replace("###IS_","").split("[")[0]
												val = key.split("[")[1].split("]")[0]
												additional_fields[ col ] = val

								pers_ids		= [ pers_id ]
								place_ids		= [ place_id ]
								#mapping_refs	= [ mapping_ref ]
								if pers_id:
									if ";" in pers_id:
										pers_ids = pers_id.split(";")
								if place_id:
									if ";" in place_id:
										place_ids = place_id.split(";")

								for i_pers_id in pers_ids:
									#if pers_id == "": continue # don't save blank peoplas...
									if i_pers_id: i_pers_id = i_pers_id.strip()
									for i_place_id in place_ids:
										if i_place_id:
											i_place_id = i_place_id.strip()
											if place_id or date_txt:
												date_dat 					= prep.mkd.convert_txtdate_to_DAT( date_txt )
												pers_id_core, pers_id_num 	= prep.mkd.get_pers_id_context( i_pers_id )

												PEOPLA_dict 					= prep.get_RDB_table_as_dict( "peopla" )
												PEOPLA_dict["src_ref"] 			= src_ref
												PEOPLA_dict["src_type"] 		= src_type
												PEOPLA_dict["src_linenum"] 		= line_num
												PEOPLA_dict["pers_id"] 			= pers_id_core
												PEOPLA_dict["pers_id_context"] 	= pers_id_num
												PEOPLA_dict["place_id"] 		= i_place_id
												PEOPLA_dict["action"] 			= action
												PEOPLA_dict["place_longitude"] 	= longitude
												PEOPLA_dict["place_latitude"] 	= latitude
												PEOPLA_dict["pers_sex"] 		= pers_sex
												PEOPLA_dict["pers_aged"] 		= pers_aged
												PEOPLA_dict["pers_race"] 		= pers_race
												PEOPLA_dict["date1_y"] 			= date_dat["date1_y"]
												PEOPLA_dict["date1_m"] 			= date_dat["date1_m"]
												PEOPLA_dict["date1_d"] 			= date_dat["date1_d"]
												PEOPLA_dict["date1_rel"] 		= date_dat["date1_rel"]
												PEOPLA_dict["date1_spec"] 		= date_dat["date1_spec"]
												PEOPLA_dict["date2_y"] 			= date_dat["date2_y"]
												PEOPLA_dict["date2_rel"] 		= date_dat["date2_rel"]
												PEOPLA_dict["date2_spec"] 		= date_dat["date2_spec"]
												PEOPLA_dict["src_pp"] 			= src_pp
												PEOPLA_dict["src_subref"]		= src_subref
												PEOPLA_dict["src_linenum_original"]		= src_linenum_original
												PEOPLA_dict["src_filepath"] = mod_filepath.rstrip().replace( confdat.academia_root, "" )
												for key, val in additional_fields.items():
													PEOPLA_dict[key.lower()] = val
												PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
												PEOPLA_dat.append( PEOPLA_dict )


					# ADDs, rather than MFs...


					# -------------------------------------------------------------------- #
					# ADD POPULATION
					# -------------------------------------------------------------------- #

					if "LINE" in row:

						for key, val in row.items():

							occ  = ""
							race = ""
							sex  = ""

							if key and val and row["LINE"]:

								if key.startswith( "###PPLN_" ) or key == "###POPULATION":

									key = key.replace( "###PPLN_", "" )
									race = "all"
									if key.startswith( "WHITES" ):
										race = "white"
									if key.startswith( "COLOURED" ):
										race = "coloured"
									if key.startswith( "SLAVES" ):
										race = "slaves"

									if "-M" in key:
										sex	= "males"
									if "-F" in key:
										sex = "females"
									if "-C" in key:
										sex = "children"
									if "-OCC_" in key:
										occ	= key.split("-OCC_")[1]

									if "###AT" in row and "DATE" in row:
										POPULATION_dict = prep.get_RDB_table_as_dict( "ADD_population" )
										POPULATION_dict[ "place_id" ]		= row[ "###AT" ]
										POPULATION_dict[ "popln" ]			= val.replace(",","")
										POPULATION_dict[ "surname" ]		= "[all]"
										POPULATION_dict[ "y1" ]				= row[ "DATE" ]
										POPULATION_dict[ "occ" ]			= occ
										POPULATION_dict[ "race" ]			= race
										POPULATION_dict[ "sex" ]			= sex
										POPULATION_dict[ "src_linenum" ] 	= line_num					# } FOREIGN KEY TO PEOPLA
										POPULATION_dict[ "src_filepath" ] 	= orig_filepath.rstrip()	# } FOREIGN KEY TO PEOPLA
										POPULATION_dat.append( POPULATION_dict )


					# -------------------------------------------------------------------- #
					# ADD MEMBER
					# -------------------------------------------------------------------- #

					'''
					if src_type == "MEMBER":
						MEMBER_dict = prep.get_RDB_table_as_dict( "ADD_member" )
						MEMBER_dict[ "pers_id" ] 		= pers_id_core
						MEMBER_dict[ "pers_id_context" ] = pers_id_num
						MEMBER_dict[ "org" ]			= row[ "###OF" ]
						MEMBER_dict[ "joined_y" ]		= row[ "###DATE" ]
						MEMBER_dict[ "src_linenum" ] 	= line_num					# } FOREIGN KEY TO PEOPLA
						MEMBER_dict[ "src_filepath" ] 	= orig_filepath.rstrip()	# } FOREIGN KEY TO PEOPLA
						MEMBER_dat.append( MEMBER_dict )
					'''

					# -------------------------------------------------------------------- #
					# ADD SURNAME_DETAILS
					# -------------------------------------------------------------------- #

					if "###SURNAME" in row and "SRC_SIZE" in row:

						# this code is a bit out of step -- copied in from a bespoke script...

						SURNAME_dict = prep.get_RDB_table_as_dict( "SURNAME_DETAILS" )
						SURNAME_dict["surname"] = row["###SURNAME"]
						SURNAME_dict["origin"] = row["ORIGIN"]
						SURNAME_dict["GBR_total"] = row["TOT_ALL"]
						SURNAME_dict["GBR_ratio"] = ( int(row["TOT_ALL"]) / float(row["SRC_SIZE"]) ) * 100

						for grp, vals in cached_regions.items():
							group_total = 0
							all_present = True
							for code in vals:
								if "TOT_" + code in row:
									group_total += int(row["TOT_" + code])
								else:
									all_present = False
							if all_present:
								SURNAME_dict["_" + grp + "_index"]	= ( group_total/float(row["TOT_ALL"]) ) * 100

						max_code = ""
						max_code_index = 0.0
						for code in codes:
							if "TOT_" + code in row:
								code_total = int(row["TOT_" + code])
								code_index = ( code_total / float(row["TOT_ALL"]) ) * 100
								SURNAME_dict[code + "_total"]	= code_total
								SURNAME_dict[code + "_index"]	= code_index
								if code_index > max_code_index:
									max_code_index = code_index
									max_code = code

						SURNAME_dict["src_filepath"] 		= orig_filepath
						SURNAME_dict["peak_county"] 		= max_code
						SURNAME_dict["peak_county_index"] = max_code_index

						SURNAME_dat.append( SURNAME_dict )


				'''
				#----------------------------------------------------------------------#
				# EXIT-PERMITS
				#----------------------------------------------------------------------#
				if "EXIT_TXT" in row:
					infile.seek(0)
					with open(''.join([DAT_dir,'/^EXIT-PERMITS.tsv']), "wb") as outfile:
						r = csv.reader( infile )
						w = csv.writer( outfile, delimiter='\t' )

						for row in r:
							w.writerow( row )
				else:
					print "- No exit permits..."


				#----------------------------------------------------------------------#
				# SHIPPING
				#----------------------------------------------------------------------#
				if "PORT" in row:
					infile.seek(0)
					with open(''.join([DAT_dir,'/^SHIPPING.tsv']), "wb") as outfile:
						r = csv.reader( infile )
						w = csv.writer( outfile, delimiter='\t' )

						for row in r:
							w.writerow( row )
				else:
					print "- No exit permits..."'''

			#----------------------------------------------------------------------#
			# Write data per file
			#----------------------------------------------------------------------#

			# will have to change this to delete files where no longer should exist... or just operate a forced refresh

			writepath = filepath.replace( "02_ODS", "03_^DAT" ).replace( "02_TSV", "03_^DAT" ).replace( "02_TXT", "03_^DAT" )
			writepath = prep.insert_caret( writepath )

			if PEOPLA_dat and requires_refresh( filepath, writepath, "PEOPLA" ):
				util.write_listdict_to_file( writepath + ".PEOPLA.tsv", PEOPLA_dat )

			if POPULATION_dat and requires_refresh( filepath, writepath, "POPULATION" ):
				util.write_listdict_to_file( writepath + ".POPULATION.tsv", POPULATION_dat )

			if SURNAME_dat and requires_refresh( filepath, writepath, "SURNAME" ):
				util.write_listdict_to_file( writepath + ".SURNAME_DETAILS.tsv", SURNAME_dat )

			for table_name, db_records in write_tables.items():
				if requires_refresh( filepath, writepath, table_name ):
					util.write_listdict_to_file( writepath + ".%s.tsv" % ( table_name.upper().replace(" ","") ), db_records )
