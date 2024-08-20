#!/usr/bin/python

## CONVERT TEXTUAL ENCODINGS TO TSV DATA
import sys
import re
import os
from subprocess import call
import operator
from collections import OrderedDict

sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.all as util
import ontologize.modules.data_transformation.all as prep




run_dir = "/media/michael/Files/Dropbox/workspace/2.research"
#run_dir = "/media/michael/Files/Dropbox/workspace/2.research/03.Tertiary/(B), Indexes/DOBSON, 2009 - Scots in the West Indies Vol 2, 1707-1857"


is_override = False
if len(sys.argv) > 1:
	arg = sys.argv[1]
	if arg == "override":
		is_override = True
		print "**********OVERRIDE**************"

	arg = sys.argv[2]
	if arg != "":
		parse_dir = arg


def requires_refresh( filename, writepath, tbl_name ):
	if is_override:
		return True

	writepath = "%s.%s.tsv" % ( writepath, tbl_name )
	if os.path.exists( writepath ):
		if os.path.getmtime( writepath ) > os.path.getmtime( filename ):
			#print "***NO NEED TO UPDATE***"
			return False

	return True


def parse_TRX_directories( start_point ):
	for root, dirs, files in os.walk( start_point, topdown=True ):
		for folder in dirs:
			if "02_TXT" in folder or "02_MKD" in folder or "02_NOTES" in folder or "02A_TXT" in folder:
				collection_root = root
				trx_root = root + "/" + folder
				parse_microformats( collection_root, trx_root )


def write_output( write_file, output, headers="" ):
	with open( write_file, "w" ) as w:
		if headers:
			w.write( "\t".join( headers ) + "\n" )
		w.write( output )
		w.close()


def write_line( write_file, output ):
	with open( write_file, "a" ) as a:
		a.write( output + "\n" )


def get_variants( x ):
	return [ 	"]%s-"  % x,
				"]%s["  % x,
				"#%s["  % x,
				"#%s-"  % x,
				"-%s["  % x,
				"\t%s[" % x,
				"%s*"   % x ]


def is_src_line( line ):
	line = line.replace( "\t", "" )
	return line.startswith( "#[" ) or line.startswith( "#LETTER" ) or line.startswith( "#MINUTE" ) or line.startswith( "#WILL" )


def is_netw_tag_line( line ):
	line = line.replace( "\t", "" )
	return line.startswith( "##>" ) or line.startswith( "###>" )


def is_mf_add_line( line ):
	line = line.replace( "\t", "" ).strip()
	return line == "###+++"


def is_mf_tag_line( line ):
	line = line.replace( "\t", "" )
	return line.startswith( "###" ) and not "---" in line and not is_mf_add_line( line )


def get_src_attribute( line ):
	return line.replace("#","").split(":",1)[1].strip()


def get_simple_val( line ):
	if "[" in line or "]" in line:
		return line[line.find("[")+1:line.find("]")]
	else:
		return ""


def parse_microformats( collection_root, trx_root ):
	for root, dirs, files in os.walk( trx_root, topdown=True ):
		for fname in files:
			if fname.endswith(".txt") and not fname.startswith("^"):

				PASSAGE_dat 	= []
				OCC_dat 		= []
				PEOPLA_dat 		= []
				REMIT_dat 		= []
				BEQUEST_dat 	= []
				WILLREF_dat 	= []
				DEATH_dat 		= []
				MEMBER_dat 		= []
				STATUS_dat 		= []
				TXT_dat			= []

				SRC_letter_dat 	= []
				SRC_will_dat 	= []
				SRC_dat 		= []

				filename = root + "/" + fname
				univ			= "." # this is file specific

				with open(filename, 'rU') as r:

					#print "----------------------"
					#print fname

					wills_output_file = ""

					line_num = 0

					is_will 	= util.is_will_file( filename )
					is_letter 	= util.is_letter_file( filename )
					is_first_dash = False

					src_type  		= "."
					src_date   		= "."
					attr_rel   		= "."
					auth_id    		= "."
					recip_id   		= "."
					recip_at 		= "."
					sgd_in 			= "."
					sgd_at 			= "."
					cnf_in 			= "."
					cnf_at 			= "."
					src_auth		= "."

					scope_pers 	 	= ""
					scope_rel 	 	= ""

					context_pers 	= "."
					context_for  	= "."
					context_at   	= "."
					context_date 	= "."
					context_exch 	= "."
					context_role 	= "."
					context_org 	= "."
					context_time 	= "."

					duration_txt 	= "."

					scope_actors	= []
					scope_actions	= []
					scope_reactors 	= []
					scope_places 	= []
					scope_date		= "."
					scope_time		= "."

					is_context_vars = False
					is_opening_vars = True

					ontolog_vers	= "1.0"

					is_first_dash_line = True

					src_ref = prep.get_ref_from_filepath( filename.rstrip() )

					for line in r:

						if line.strip() == "":
							is_opening_vars = False
						if line.startswith("#["):
							is_opening_vars = True

						line_num += 1

						# --------------------------------------------------------------------------- #
						# SOURCE VALUES
						# --------------------------------------------------------------------------- #

						if is_src_line( line ):
							src_type = line.replace( "[", "" ).replace( "]", "" ).replace( "#", "" ).strip()

						if is_netw_tag_line( line ):
							src_type += "-NETWORKNEWS"
							src_type = src_type.replace( "-NETWORKNEWS-NETWORKNEWS", "-NETWORKNEWS" )

						# LETTER SPECIFIC ATTR
						if "#fm:" in line.lower():
							src_auth 		= get_src_attribute( line )
							context_pers   	= src_auth
						if "#fm@:" in line.lower():
							context_at   	= get_src_attribute( line )
						if "#to:" in line.lower():
							recip_id  		= get_src_attribute( line )
						if "#to@:" in line.lower():
							recip_at  		= get_src_attribute( line )
						if "#date:" in line.lower():
							context_date  	= get_src_attribute( line )
						if "#rel:" in line.lower():
							attr_rel  		= get_src_attribute( line )

						# WILL SPECIFIC ATTR
						if "#tttr:" in line.lower():
							src_auth 		= get_src_attribute( line )
							context_pers  	= src_auth
						if "#sgd:" in line.lower():
							sgd_in			= get_src_attribute( line )
							context_date	= sgd_in
						if "#sgd@:" in line.lower():
							sgd_at  		= get_src_attribute( line )
						if "#cnf:" in line.lower():
							cnf_in			= get_src_attribute( line )
						if "#cnf@:" in line.lower():
							cnf_at  		= get_src_attribute( line )

						# GENERAL / OTHER
						if "#for:" in line.lower():
							context_for		= get_src_attribute( line )
						if "#at:" in line.lower():
							context_at		= get_src_attribute( line )
						if "#auth:" in line.lower():
							context_pers	= get_src_attribute( line )
							src_auth 		= context_pers
						if "#exch:" in line.lower():
							context_exch	= get_src_attribute( line )
						if "#org:" in line.lower():
							context_org		= get_src_attribute( line )
						if "#role:" in line.lower():
							context_role	= get_src_attribute( line )

						context_pers = context_pers.replace( "(", "[" ).replace( ")", "]" )

						# --------------------------------------------------------------------- #
						# SRC data (+ peopla related src info)
						# --------------------------------------------------------------------- #

						if line.startswith( "---------------------------------" ) and src_type:
							list_srcs = ( "NEWSPAPER", "LETTER" )
							if src_type.startswith( list_srcs ) :
								date_dat = prep.mkd.convert_txtdate_to_DAT( context_date )

								# add the SRC record...
								SRC_dict = prep.get_RDB_table_as_dict( "src" )
								SRC_dict["place_id"]		= context_at
								SRC_dict["y"]				= date_dat["y1"]
								SRC_dict["m"]				= date_dat["m1"]
								SRC_dict["d"]				= date_dat["d1"]
								SRC_dict["src_ref"]			= src_ref
								SRC_dict["src_type"]		= src_type
								SRC_dict["src_filepath"]	= filename.rstrip()
								SRC_dict["src_linenum"] 	= line_num
								SRC_dat.append( SRC_dict )

							if src_type.startswith( "MINUTE" ):
								date_dat = prep.mkd.convert_txtdate_to_DAT( context_date )

								# add the SRC record...
								SRC_dict = prep.get_RDB_table_as_dict( "src" )
								SRC_dict["place_id"]		= context_at
								SRC_dict["y"]				= date_dat["y1"]
								SRC_dict["src_type"]		= src_type
								SRC_dict["src_filepath"]	= filename.rstrip()
								SRC_dict["src_linenum"] 	= line_num
								SRC_dat.append( SRC_dict )

							if src_type.startswith( "LETTER" ):
								date_dat = prep.mkd.convert_txtdate_to_DAT( context_date )

								# add PEOPLA records... for sent and received...
								PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
								PEOPLA_dict["src_ref"] 		= src_ref
								PEOPLA_dict["pers_id"] 		= prep.mkd.get_pers_id_context( context_pers )[0]
								PEOPLA_dict["place_id"] 	= context_at
								PEOPLA_dict["action"] 		= "LETTER_SENT"
								PEOPLA_dict["y1"] 			= date_dat["y1"]
								PEOPLA_dict["m1"] 			= date_dat["m1"]
								PEOPLA_dict["d1"] 			= date_dat["d1"]
								PEOPLA_dict["src_type"] 	= src_type
								PEOPLA_dict["src_filepath"]	= filename.rstrip()
								PEOPLA_dict["src_linenum"] 	= line_num
								PEOPLA_dict["pers_id_context"] 	= prep.mkd.get_pers_id_context( context_pers )[1]
								PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
								PEOPLA_dat.append( PEOPLA_dict )

								PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
								PEOPLA_dict["src_ref"] 		= src_ref
								PEOPLA_dict["pers_id"] 		= prep.mkd.get_pers_id_context( recip_id )[0]
								PEOPLA_dict["place_id"]	 	= recip_at
								PEOPLA_dict["action"] 		= "LETTER_RECD"
								PEOPLA_dict["y1"] 			= date_dat["y1"]
								PEOPLA_dict["m1"] 			= date_dat["m1"]
								PEOPLA_dict["d1"] 			= date_dat["d1"]
								PEOPLA_dict["src_type"] 		= src_type
								PEOPLA_dict["src_filepath"] 	= filename.rstrip()
								PEOPLA_dict["src_linenum"] 		= line_num
								PEOPLA_dict["pers_id_context"] 	= prep.mkd.get_pers_id_context( recip_id )[1]
								PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
								PEOPLA_dat.append( PEOPLA_dict )

								# add the SRC record...
								SRC_letter_dict = prep.get_RDB_table_as_dict( "SRC_letter" )
								SRC_letter_dict["attr_fm"]		= context_pers
								SRC_letter_dict["attr_fm_at"]	= context_at
								SRC_letter_dict["attr_to"]		= recip_id
								SRC_letter_dict["attr_to_at"]	= recip_at
								SRC_letter_dict["attr_rel"]		= attr_rel
								SRC_letter_dict["attr_date"]	= date_dat["y1"]
								SRC_letter_dict["src_filepath"]	= filename.rstrip()
								SRC_letter_dict["src_linenum"] 	= line_num
								SRC_letter_dat.append( SRC_letter_dict )

							if src_type.startswith( "WILL" ):
								sgd_dt = prep.mkd.convert_txtdate_to_DAT( context_date )
								cnf_dt = prep.mkd.convert_txtdate_to_DAT( cnf_in )

								# add PEOPLA records... for signed will...
								PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
								PEOPLA_dict["src_ref"] 		= src_ref
								PEOPLA_dict["pers_id"] 		= prep.mkd.get_pers_id_context( context_pers )[0]
								PEOPLA_dict["place_id"] 	= sgd_at
								PEOPLA_dict["action"] 		= "WILL_SGD"
								PEOPLA_dict["y1"] 			= sgd_dt["y1"]
								PEOPLA_dict["m1"] 			= sgd_dt["m1"]
								PEOPLA_dict["d1"] 			= sgd_dt["d1"]
								PEOPLA_dict["src_type"] 		= src_type
								PEOPLA_dict["src_filepath"] 	= filename.rstrip()
								PEOPLA_dict["src_linenum"] 		= line_num
								PEOPLA_dict["pers_id_context"] 	= prep.mkd.get_pers_id_context( context_pers )[1]
								PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
								PEOPLA_dat.append( PEOPLA_dict )

								# add the SRC record...
								SRC_will_dict = prep.get_RDB_table_as_dict( "SRC_will" )
								SRC_will_dict["attr_ttor"]		= context_pers
								SRC_will_dict["attr_sgd_in"]	= sgd_dt["y1"]
								SRC_will_dict["attr_sgd_at"]	= sgd_at
								SRC_will_dict["attr_cnf_in"]	= cnf_dt["y1"]
								SRC_will_dict["attr_cnf_at"]	= cnf_at
								SRC_will_dict["src_filepath"]	= filename.rstrip()
								SRC_will_dict["src_linenum"] 	= line_num
								SRC_will_dat.append( SRC_will_dict )

							src_type = ""


						if line.startswith( "#[" ):
							list_srcs = ( "BDM-DEATH", "ENTERED", "CLEARED" )
							if src_type.startswith( list_srcs ) :
								date_dat = prep.mkd.convert_txtdate_to_DAT( context_date )

								# add the SRC record...
								SRC_dict = prep.get_RDB_table_as_dict( "src" )
								SRC_dict["place_id"]		= context_at
								SRC_dict["y"]				= date_dat["y1"]
								SRC_dict["m"]				= date_dat["m1"]
								SRC_dict["d"]				= date_dat["d1"]
								SRC_dict["src_ref"]			= src_ref
								SRC_dict["src_type"]		= src_type
								SRC_dict["src_filepath"]	= filename.rstrip()
								SRC_dict["src_linenum"] 	= line_num
								SRC_dat.append( SRC_dict )


						if line.startswith( "@" ):
							context_time = line.replace("@","").strip()

						if line.startswith( "!{2.0}" ):
							ontolog_vers	= "2.0"
							if "[" in line:
								univ 		= line.strip().split("[",1)[1][:-1]

						if line.startswith( "############" ):
							is_context_vars = True

						# --------------------------------------------------------------------------- #
						# PEOPLA tags
						# --------------------------------------------------------------------------- #

						if not is_mf_tag_line( line ) and ontolog_vers == "2.0":

							if scope_time == ".":
								scope_time = context_time

							if scope_date == ".":
								scope_date = context_date

							if scope_actions == []:
								scope_actions.append("AT")

							for actor in scope_actors:
								for action in scope_actions:
									for place in scope_places:
										if place == "": continue
										date_dat 	= prep.mkd.convert_txtdate_to_DAT( scope_date )

										PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
										PEOPLA_dict["src_ref"] 		= src_ref
										PEOPLA_dict["pers_id"] 		= actor
										PEOPLA_dict["place_id"] 	= place
										PEOPLA_dict["action"] 		= action
										PEOPLA_dict["y1"] 			= date_dat["y1"]
										PEOPLA_dict["m1"] 			= date_dat["m1"]
										PEOPLA_dict["d1"] 			= date_dat["d1"]
										PEOPLA_dict["date1_rel"] 	= date_dat["date1_rel"]
										PEOPLA_dict["time"]			= scope_time
										PEOPLA_dict["src_filepath"] = filename.rstrip()
										PEOPLA_dict["src_type"] 	= src_type
										PEOPLA_dict["src_linenum"] 	= line_num
										PEOPLA_dict["aged"] 		= line_aged
										PEOPLA_dict["univ"] 		= univ
										PEOPLA_dict["duration_txt"] = duration_txt
										PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
										PEOPLA_dat.append( PEOPLA_dict )

							for actor in scope_reactors:
								for action in scope_actions:
									for place in scope_places:
										if place == "": continue
										action 		= action + "-PASSIVE"
										date_dat 	= prep.mkd.convert_txtdate_to_DAT( scope_date )

										PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
										PEOPLA_dict["src_ref"] 		= src_ref
										PEOPLA_dict["pers_id"] 		= actor
										PEOPLA_dict["place_id"] 	= place
										PEOPLA_dict["action"] 		= action
										PEOPLA_dict["y1"] 			= date_dat["y1"]
										PEOPLA_dict["m1"] 			= date_dat["m1"]
										PEOPLA_dict["d1"] 			= date_dat["d1"]
										PEOPLA_dict["date1_rel"] 	= date_dat["date1_rel"]
										PEOPLA_dict["time"]			= scope_time
										PEOPLA_dict["src_filepath"] = filename.rstrip()
										PEOPLA_dict["src_type"] 	= src_type
										PEOPLA_dict["src_linenum"] 	= line_num
										PEOPLA_dict["aged"] 		= line_aged
										PEOPLA_dict["univ"] 		= univ
										PEOPLA_dict["duration_txt"] = duration_txt
										PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
										PEOPLA_dat.append( PEOPLA_dict )

							if is_context_vars or is_opening_vars:
								if scope_places:
									context_at = scope_places[0]
								context_date = scope_date
								context_time = scope_time

							if not is_mf_add_line( line ):
								scope_actors	= []
							scope_actions	= []
							scope_reactors 	= []
							scope_places 	= []
							scope_date		= "."
							scope_time		= "."
							is_context_vars = False
						else:
							line_at     = "."
							line_date   = "."
							line_to     = "."
							line_action = "."
							line_pers   = "."
							line_aged   = "."
							line_rel 	= ""

							if ontolog_vers == "2.0":
								line 	= line.replace( "\t", "" ).strip()
								val		= get_simple_val(line)
								#print line

								if line.startswith("###[") and len( scope_actions ) == 0:
									if val.lower() == "auth":
										val = src_auth
									if val.lower() == "recip":
										val = recip_id
									scope_actors.append( val )

								if not "[" in line and not "]" in line and not "^" in line:
									scope_actions.append( line.replace("###","") )

								if line.startswith("###[") and len( scope_actions ) > 0:
									if val.lower() == "auth":
										val = src_auth
									if val.lower() == "recip":
										val = recip_id
									scope_reactors.append( val )

								if line.startswith("###AT"):
									if line.startswith("###AT^"):
										if context_at:
											val = context_at + ", " + val
									scope_places.append( val )

								if line.startswith("###DUR"):
									duration_txt = val

								if line.startswith("###DATE"):
									if line.startswith("###DATE^"):
										if context_date:
											val = context_date.replace("-","")
									scope_date = val.replace("-","")

								if line.startswith("###TIME"):
									scope_time = val

							else:

								# ---------------------------------------------------------- #
								# TODO: sort out proper scope functionality at some point...
								# at the moment using relationships and allowing tabbed lines after this...
								# ---------------------------------------------------------- #

								if not line.startswith( "###\t" ) and not line.startswith( "###>\t" ):
									match = re.findall(r"###(>+?[^\[-]*){0,1}\[(.+?)\]", line) # pers
									if match:
										rel_match 	= match[0][0]
										if not "\t" in rel_match:
											line_rel = rel_match
										line_pers 	= match[0][1]
										trail 		= line.split("]",1)[1]
										submatch 	= re.search(r"\((.+?)\)", trail)
										if submatch and submatch != "...":
											line_pers = "%s [%s]" % ( line_pers, submatch.group(1) )

										if line_pers.lower() == "auth":
											line_pers = src_auth
										if line_pers.lower() == "recip":
											line_pers = recip_id

										if line_rel:
											if not "," in line_pers: # not specified a surname, so use context surname
												line_pers = "%s, %s" % ( context_pers.split(",")[0], line_pers )
											scope_pers = line_pers
											scope_rel  = line_rel.replace( ">", "").strip()
										else: # i.e. if not a >REL line use context rather than scope...
											context_pers = line_pers

								# ---------------------------------------------------------- #

								# Get PEOPLA data

								match  = re.search(r"AT\[(.+?)\]", line)      # at
								if match:
									line_at   = match.group(1)

								if any( substring in line for substring in get_variants( "AT" ) ):
									line_action    = "AT"

								if any( substring in line for substring in get_variants( "RE" ) ):
									line_action    = "RE"

								if any( substring in line for substring in get_variants( "EX" ) ):
									line_action    = "EX"

								if any( substring in line for substring in get_variants( "DIED" ) ):
									line_action    = "DIED"

								if any( substring in line for substring in get_variants( "OCC" ) ):
									line_action    = "OCC"

								if any( substring in line for substring in get_variants( "EX-OCC" ) ):
									line_action    = "EX-OCC"

								if any( substring in line for substring in get_variants( "RE-OCC" ) ):
									line_action    = "RE-OCC"

								if any( substring in line for substring in get_variants( "BORN" ) ):
									line_action    = "BORN"

								if any( substring in line for substring in get_variants( "MEMORIAL" ) ):
									line_action    = "MEMORIAL"

								if any( substring in line for substring in get_variants( "MARRIED" ) ):
									line_action    = "MARRIED"

								if any( substring in line for substring in get_variants( "REMITS" ) ):
									line_action    = "REMITS"

								if any( substring in line for substring in get_variants( "BEQUEST" ) ):
									line_action    = "BEQUEST"

								if any( substring in line for substring in get_variants( "MEMBER" ) ):
									line_action    = "MEMBER"

								if any( substring in line for substring in get_variants( "RETURN" ) ):
									line_action    = "RETURN"

								if any( substring in line for substring in get_variants( "OUT" ) ):
									line_action    = "OUT"

								if any( substring in line for substring in get_variants( "PASSAGE" ) ):
									line_action    = "PASSAGE"

								if any( substring in line for substring in get_variants( "STATUS" ) ):
									line_action    = "STATUS"

								if any( substring in line for substring in get_variants( "HEALTH" ) ):
									line_action    = "HEALTH"

								if any( substring in line for substring in get_variants( "HAPPINESS" ) ):
									line_action    = "HAPPINESS"

								if any( substring in line for substring in get_variants( "FORTUNES" ) ): # personal
									line_action    = "FORTUNES"

								if any( substring in line for substring in get_variants( "PROSPECTS" ) ): # general
									line_action    = "PROSPECTS"

								# get age
								match  = re.search(r"AGED\[(.+?)\]", line)
								if match:
									line_aged = match.group(1)

								# get date
								match  = re.search(r"IN\[(.+?)\]", line)
								if match:
									line_date = match.group(1)
									if line_date == "yr":
										line_date = context_date
									if line_date == "date":
										line_date = context_date
									if line_date == "dt":
										line_date = context_date
								else:
									if src_type.lower() == "bdm-death" and line_action == "DIED":
										line_date = context_date
									if src_type.lower() == "bdm-birth" and line_action == "BIRTH":
										line_date = context_date
									if src_type.lower() == "bdm-married" and line_action == "MARRIED":
										line_date = context_date

								# get date and place from context indictators ( * @ ~ < ^ ) ...
								if line.strip().endswith( "**" ):
									if line_at == ".":
										line_at = context_at
									if line_date == ".":
										line_date = context_date
								elif line.strip().endswith( "*" ):
									line_at = prep.mkd.get_subzone_from_addr( context_at )
									if line_date == ".":
										line_date = context_date

								if line.strip().endswith( "@" ):
									line_at = prep.mkd.get_subzone_from_addr( recip_at )
									if line_date == ".":
										line_date = context_date

								date_dat = prep.mkd.convert_txtdate_to_DAT( line_date )

								if line.startswith("###>"):
									pers_id = scope_pers.rstrip()
									if not line_rel:
										line_rel = scope_rel
								else:
									pers_id = context_pers.rstrip()
									scope_rel = ""

								# ---------------------------------------------------------- #

								pers_id_core, pers_id_num = prep.mkd.get_pers_id_context( pers_id )

								if line_at != "." and not any( x in line_action for x in [ "PASSAGE", "RETURN", "OUT" ] ):
									PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
									PEOPLA_dict["src_ref"] 		= src_ref
									PEOPLA_dict["pers_id"] 		= pers_id_core
									PEOPLA_dict["place_id"] 	= line_at.rstrip()
									PEOPLA_dict["action"] 		= line_action.rstrip()
									PEOPLA_dict["y1"] 			= date_dat["y1"]
									PEOPLA_dict["m1"] 			= date_dat["m1"]
									PEOPLA_dict["d1"] 			= date_dat["d1"]
									PEOPLA_dict["date1_rel"] 	= date_dat["date1_rel"]
									PEOPLA_dict["date1_spec"] 	= date_dat["date1_spec"]
									PEOPLA_dict["y2"] 			= date_dat["y2"]
									PEOPLA_dict["m2"] 			= date_dat["m2"]
									PEOPLA_dict["d2"] 			= date_dat["d2"]
									PEOPLA_dict["date2_rel"] 	= date_dat["date2_rel"]
									PEOPLA_dict["date2_spec"] 	= date_dat["date2_spec"]
									PEOPLA_dict["src_filepath"] = filename.rstrip()
									PEOPLA_dict["src_type"] 	= src_type
									PEOPLA_dict["src_linenum"] 	= line_num
									PEOPLA_dict["pers_id_context"] 	= pers_id_num
									PEOPLA_dict["aged"] 		= line_aged
									PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
									PEOPLA_dat.append( PEOPLA_dict )

									# hacking in some more PEOPLAs... as not done relationships yet...
									if line_rel == "FATHER":
										pers_id_core, pers_id_num = prep.mkd.get_pers_id_context( context_pers )

										PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
										PEOPLA_dict["src_ref"] 		= src_ref
										PEOPLA_dict["pers_id"] 		= pers_id_core
										PEOPLA_dict["place_id"] 	= line_at.rstrip()
										PEOPLA_dict["action"] 		= "FATHER_" + line_action.rstrip()
										PEOPLA_dict["y1"] 			= date_dat["y1"]
										PEOPLA_dict["m1"] 			= date_dat["m1"]
										PEOPLA_dict["d1"] 			= date_dat["d1"]
										PEOPLA_dict["date1_rel"] 	= date_dat["date1_rel"]
										PEOPLA_dict["date1_spec"] 	= date_dat["date1_spec"]
										PEOPLA_dict["y2"] 			= date_dat["y2"]
										PEOPLA_dict["m2"] 			= date_dat["m2"]
										PEOPLA_dict["d2"] 			= date_dat["d2"]
										PEOPLA_dict["date2_rel"] 	= date_dat["date2_rel"]
										PEOPLA_dict["date2_spec"] 	= date_dat["date2_spec"]
										PEOPLA_dict["src_filepath"] = filename.rstrip()
										PEOPLA_dict["src_type"] 	= src_type
										PEOPLA_dict["src_linenum"] 	= line_num
										PEOPLA_dict["pers_id_context"] 	= pers_id_num
										PEOPLA_dict["aged"] 		= line_aged
										PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
										PEOPLA_dat.append( PEOPLA_dict )

								# ---------------------------------------------------------- #

								# Get WILLS ref data
								line_reg  = "."
								line_ref  = "."

								match  = re.search(r"WILL\[([\w\\.]+)\]", line)
								if match:
									line_ref   = match.group(1).strip()

								match = re.search(r"REG\[(\w+)\]", line)
								if match:
									line_reg  = match.group(1).strip()

								match  = re.search(r"AT\[([\w\\.]+)\]", line)
								if match:
									line_at   = match.group(1).strip()

								if line_ref != ".":
									WILLREF_dict = OrderedDict()
									WILLREF_dict["REF"] 		= src_ref
									WILLREF_dict["LINE_NUM"] 	= line_num
									WILLREF_dict["PERS_ID"] 	= context_pers
									WILLREF_dict["REF"] 		= line_ref
									WILLREF_dict["REG"] 		= line_reg
									WILLREF_dict["AT"] 			= line_at
									WILLREF_dict["FILEPATH"] 	= filename.strip()
									WILLREF_dat.append( WILLREF_dict )

								# ---------------------------------------------------------- #

								# Get BEQUEST data
								if line_action == "BEQUEST":
									line_rel = "."
									line_at = "."
									line_item = "."
									line_share = "."
									line_mult = "."
									line_pref = "."

									match = re.search(r"BEQUEST\[(.+?)\]", line)
									if match:
										line_item  = match.group(1).strip()

									match = re.search(r"REL\[(.+?)\]", line)
									if match:
										line_rel  = match.group(1).strip()

									match = re.search(r"AT\[(.+?)\]", line)
									if match:
										line_at  = match.group(1).strip()

									match = re.search(r"SHARE\[(.+?)\]", line)
									if match:
										line_share  = match.group(1).strip()

									match = re.search(r"[Xx]\[(.+?)\]", line)
									if match:
										line_mult  = match.group(1).strip()

									match = re.search(r"PREF\[(.+?)\]", line)
									if match:
										line_pref  = match.group(1).strip()

									# todo - get the EX, WI, RE values...
									ex_at = "."
									wi_at = "."
									re_at = "."

									# To do - parse the bequests...
									BEQUEST_dict = OrderedDict()
									BEQUEST_dict["REF"] 		= src_ref
									BEQUEST_dict["LINE_NUM"] 	= line_num
									BEQUEST_dict["PERS_ID"] 	= auth_id
									BEQUEST_dict["EX"] 			= ex_at
									BEQUEST_dict["WI"] 			= wi_at
									BEQUEST_dict["RE"] 			= re_at
									BEQUEST_dict["SGD_IN"] 		= sgd_in
									BEQUEST_dict["SGD_AT"] 		= sgd_at
									BEQUEST_dict["ITEM"] 		= line_item
									BEQUEST_dict["SHARE"] 		= line_share
									BEQUEST_dict["REL"] 		= line_rel
									BEQUEST_dict["RECIP_ID"] 	= context_pers.strip()
									BEQUEST_dict["AT"] 			= line_at
									BEQUEST_dict["MULT"] 		= line_mult
									BEQUEST_dict["PREF"] 		= line_pref
									BEQUEST_dict["FILEPATH"] 	= filename.strip()
									BEQUEST_dat.append( BEQUEST_dict )

								# ---------------------------------------------------------- #

								# Get DIED data
								if line_action == "DIED":
									line_cause  = "."

									match = re.search(r"CAUSE\[(.+?)\]", line)
									if match:
										line_cause = match.group(1)

									DEATH_dict = prep.get_RDB_table_as_dict( "MF_death" )
									DEATH_dict["cause"] 		= line_cause.rstrip()
									DEATH_dict["src_filepath"] 	= filename.rstrip()
									DEATH_dict["src_linenum"] 	= line_num
									DEATH_dat.append( DEATH_dict )

								# ---------------------------------------------------------- #

								# Get REMITTANCE data
								if line_action == "REMITS":
									line_remits = "."
									line_rel = "."
									line_to = "."

									match = re.search(r"REMITS\[(.+?)\]", line)
									if match:
										line_remits = match.group(1)

									match = re.search(r"TO\[(.+?)\]", line)
									if match:
										line_to = match.group(1)

									match = re.search(r"REL\[(.+?)\]", line)
									if match:
										line_to = match.group(1)

									REMIT_dict = OrderedDict()
									REMIT_dict["REF"] 		= src_ref
									REMIT_dict["LINE_NUM"] 	= line_num
									REMIT_dict["PERS_ID"] 	= context_pers.rstrip()
									REMIT_dict["REMITS"] 	= line_remits.rstrip()
									REMIT_dict["DATE"] 		= line_date.rstrip()
									REMIT_dict["AT"] 		= line_at.rstrip()
									REMIT_dict["TO"] 		= line_to.rstrip()
									REMIT_dict["REL"] 		= line_rel.rstrip()
									REMIT_dat.append( REMIT_dict )


								# ---------------------------------------------------------- #

								# Get MEMBER data
								if line_action == "MEMBER":
									line_org = "."

									match = re.search(r"OF\[(.+?)\]", line)
									if match:
										line_org = match.group(1)

									if line_org == ".":
										line_org = context_org

									if line_date == ".":
										line_date = context_date

									date_dat = prep.mkd.convert_txtdate_to_DAT( line_date )
									MEMBER_dict 					= prep.get_RDB_table_as_dict( "ADD_member" )
									MEMBER_dict[ "pers_id" ] 		= pers_id_core
									MEMBER_dict[ "pers_id_context" ] = pers_id_num
									MEMBER_dict[ "org" ]			= line_org
									MEMBER_dict[ "joined_y" ]		= line_date #date_dat["y"]
									MEMBER_dict[ "src_filepath" ]	= filename.rstrip()	# FK
									MEMBER_dict[ "src_linenum" ] 	= line_num			# FK
									MEMBER_dat.append( MEMBER_dict )


								# ---------------------------------------------------------- #


								# Get PASSAGE data
								if line_action == "RETURN" or line_action == "OUT" or line_action == "PASSAGE":
									# RETURN and OUT are shorthands...

									line_desire 	= ""
									line_plans 		= ""
									is_actual		= False

									match = re.search(r"PLANS\[(.+?)\]", line)
									if match:
										line_plans = match.group(1)

									match = re.search(r"DESIRE\[(.+?)\]", line)
									if match:
										line_desire = match.group(1)

									if not line_desire and not line_plans:
										is_actual = True

									if line_action == "RETURN":
										is_return = True
									if line_action == "OUT":
										is_out = True


									# --------------------------------------------------- #
									# create PEOPLAs at /source/ and /destination/
									# --------------------------------------------------- #

									line_fm 	= ""
									line_to 	= ""
									line_dep 	= ""
									line_arr 	= ""
									is_return	= False
									is_out		= False

									match = re.search(r"FM\[(.+?)\]", line)
									if match:
										line_fm = match.group(1)

									match = re.search(r"DEP\[(.+?)\]", line)
									if match:
										line_dep = match.group(1)

									if line.strip().endswith( "*" ):
										if line_fm == "":
											line_fm = context_at
										if line_dep == "":
											line_dep = context_date

									date_dat = prep.mkd.convert_txtdate_to_DAT( line_dep )
									PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
									PEOPLA_dict["src_ref"] 		= src_ref
									PEOPLA_dict["pers_id"] 		= pers_id_core
									PEOPLA_dict["place_id"] 	= line_fm
									PEOPLA_dict["action"] 		= "DEPARTS"
									PEOPLA_dict["y1"] 			= date_dat["y1"]
									PEOPLA_dict["m1"] 			= date_dat["m1"]
									PEOPLA_dict["d1"] 			= date_dat["d1"]
									PEOPLA_dict["date1_rel"] 	= date_dat["date1_rel"]
									PEOPLA_dict["date1_spec"] 	= date_dat["date1_spec"]
									PEOPLA_dict["y2"] 			= date_dat["y2"]
									PEOPLA_dict["m2"] 			= date_dat["m2"]
									PEOPLA_dict["d2"] 			= date_dat["d2"]
									PEOPLA_dict["date2_rel"] 	= date_dat["date2_rel"]
									PEOPLA_dict["date2_spec"] 	= date_dat["date2_spec"]
									PEOPLA_dict["src_filepath"] = filename.rstrip()
									PEOPLA_dict["src_type"] 	= src_type
									PEOPLA_dict["src_linenum"] 	= line_num
									PEOPLA_dict["pers_id_context"] 	= pers_id_num
									PEOPLA_dict["aged"] 		= line_aged
									PEOPLA_dict["is_actual"] 	= is_actual
									PEOPLA_dat.append( PEOPLA_dict )

									# --------------------------------------------------- #

									match = re.search(r"TO\[(.+?)\]", line)
									if match:
										line_to = match.group(1)

									match = re.search(r"ARR\[(.+?)\]", line)
									if match:
										line_arr = match.group(1)

									if line_to == "" and line_action == "RETURN":
										line_to = "GBR"

									date_dat = prep.mkd.convert_txtdate_to_DAT( line_arr )
									PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
									PEOPLA_dict["pers_id"] 		= pers_id_core
									PEOPLA_dict["place_id"] 	= line_to
									PEOPLA_dict["action"] 		= "ARRIVES"
									PEOPLA_dict["y1"] 			= date_dat["y1"]
									PEOPLA_dict["m1"] 			= date_dat["m1"]
									PEOPLA_dict["d1"] 			= date_dat["d1"]
									PEOPLA_dict["date1_rel"] 	= date_dat["date1_rel"]
									PEOPLA_dict["date1_spec"] 	= date_dat["date1_spec"]
									PEOPLA_dict["y2"] 			= date_dat["y2"]
									PEOPLA_dict["m2"] 			= date_dat["m2"]
									PEOPLA_dict["d2"] 			= date_dat["d2"]
									PEOPLA_dict["date2_rel"] 	= date_dat["date2_rel"]
									PEOPLA_dict["date2_spec"] 	= date_dat["date2_spec"]
									PEOPLA_dict["src_filepath"] = filename.rstrip()
									PEOPLA_dict["src_type"] 	= src_type
									PEOPLA_dict["src_linenum"] 	= line_num
									PEOPLA_dict["pers_id_context"] 	= pers_id_num
									PEOPLA_dict["aged"] 		= line_aged
									PEOPLA_dict["is_actual"] 	= is_actual
									PEOPLA_dat.append( PEOPLA_dict )

									# --------------------------------------------------- #
									# add the microformat
									# --------------------------------------------------- #

									line_purpose 	= "."
									line_port 		= "."
									line_dur_m 		= "."

									match = re.search(r"PORT\[(.+?)\]", line)
									if match:
										line_port = match.group(1)

									match = re.search(r"DUR_M\[(.+?)\]", line)
									if match:
										line_dur = match.group(1)

									match = re.search(r"PURPOSE\[(.+?)\]", line)
									if match:
										line_purpose = match.group(1)

									PASSAGE_dict = prep.get_RDB_table_as_dict( "MF_passage" )
									PASSAGE_dict[ "desire" ] 		= line_desire
									PASSAGE_dict[ "plans" ] 		= line_plans
									PASSAGE_dict[ "purpose" ] 		= line_purpose
									PASSAGE_dict[ "port" ] 			= line_port
									PASSAGE_dict[ "is_actual" ] 	= is_actual
									PASSAGE_dict[ "dur_m" ] 		= line_dur_m
									PASSAGE_dict[ "src_filepath" ]	= filename.rstrip()	# FK
									PASSAGE_dict[ "src_linenum" ] 	= line_num			# FK
									PASSAGE_dat.append( PASSAGE_dict )

								# ---------------------------------------------------------- #

								# Get STATUS (HEALTH/FORTUNE/HAPPINESS/PROSPECTS) data
								if any( x in line_action for x in [ "HEALTH", "FORTUNES", "HAPPINESS", "PROSPECTS" ] ):
									line_current 	= "."
									line_outlook 	= "."
									line_reflection = "."
									line_dur 		= "."

									if line_action == "HEALTH":
										match = re.search(r"HEALTH\[(.+?)\]", line)
										if match:
											line_current = match.group(1)

									if line_action == "FORTUNES":
										match = re.search(r"FORTUNES\[(.+?)\]", line)
										if match:
											line_current = match.group(1)

									if line_action == "HAPPINESS":
										match = re.search(r"HAPPINESS\[(.+?)\]", line)
										if match:
											line_current = match.group(1)

									if line_action == "PROSPECTS":
										match = re.search(r"PROSPECTS\[(.+?)\]", line)
										if match:
											line_current = match.group(1)

									match = re.search(r"OUTLOOK\[(.+?)\]", line)
									if match:
										line_outlook = match.group(1)

									match = re.search(r"REFLECTION\[(.+?)\]", line)
									if match:
										line_reflection = match.group(1)

									match = re.search(r"DUR\[(.+?)\]", line)
									if match:
										line_dur = match.group(1)

									STATUS_dict = prep.get_RDB_table_as_dict( "MF_status" )
									STATUS_dict[ "current" ] 	= line_current
									STATUS_dict[ "outlook" ] 	= line_outlook
									STATUS_dict[ "reflection" ] = line_reflection
									STATUS_dict[ "dur" ] 		= line_dur
									STATUS_dict[ "type" ] 		= line_action
									STATUS_dict[ "src_filepath" ]	= filename.rstrip()	# FK
									STATUS_dict[ "src_linenum" ] 	= line_num			# FK
									STATUS_dat.append( STATUS_dict )


								# ---------------------------------------------------------- #


								# GET OCCUPATION data
								if line_action == "OCC":
									line_occ 		= "."
									line_salary_cur = "."
									line_salary_stg = "."
									line_income_cur = "."
									line_income_stg = "."
									line_paid_cur 	= "."
									line_paid_stg 	= "."
									line_for 		= "."

									match = re.search(r"OCC\[(.+?)\]", line) #occ
									if match:
										line_occ  = match.group(1)

									match = re.search(r"AT\[(.+?)\]", line) #at
									if match:
										line_at  = match.group(1)

									match = re.search(r"IN\[(.+?)\]", line) #in
									if match:
										line_date  = match.group(1)

									match  = re.search(r"SALARY-CUR\[(.+?)\]", line) #salary
									if match:
										line_salary_cur = match.group(1)

									match  = re.search(r"SALARY-STG\[(.+?)\]", line) #salary
									if match:
										line_salary_stg = match.group(1)

									match  = re.search(r"INCOME-CUR\[(.+?)\]", line) #income
									if match:
										line_income_cur   = match.group(1)

									match  = re.search(r"INCOME-STG\[(.+?)\]", line) #income
									if match:
										line_income_stg   = match.group(1)

									match  = re.search(r"PAID-CUR\[(.+?)\]", line) #income
									if match:
										line_paid_cur   = match.group(1)

									match  = re.search(r"PAID-STG\[(.+?)\]", line) #income
									if match:
										line_paid_stg   = match.group(1)

									match  = re.search(r"FOR\[(.+?)\]", line) #for
									if match:
										line_for   	= match.group(1)

									if line_for == ".":
										line_for = context_for

									if line_occ == ".":
										line_occ = context_role

									if line_salary_stg == "." and not line_salary_cur == "." and not context_exch == ".":
										if ":" in context_exch:
											div = int( context_exch.split(":")[0] )
											mul = int( context_exch.split(":")[1] )
										cur = int( line_salary_cur.strip().replace( ",", "" ) )
										line_salary_stg = str( cur / ( div * mul ) ) # change to take context_exch

									OCC_dict = prep.get_RDB_table_as_dict( "MF_occ" )
									OCC_dict["occ"] 		= line_occ.rstrip()
									OCC_dict["salary_cur"] 	= line_salary_cur.rstrip()
									OCC_dict["salary_stg"] 	= line_salary_stg
									OCC_dict["income_cur"] 	= line_income_cur.rstrip()
									OCC_dict["income_stg"] 	= line_income_stg.rstrip()
									OCC_dict["paid_cur"] 	= line_paid_cur.rstrip()
									OCC_dict["paid_stg"] 	= line_paid_stg.rstrip()
									OCC_dict["employer"] 	= line_for.rstrip()
									OCC_dict["src_pagenum"] = "" 					# todo
									OCC_dict["src_linenum"] = line_num				# } FOREIGN KEY
									OCC_dict["src_filepath"] = filename.rstrip()	# } FOREIGN KEY
									OCC_dat.append( OCC_dict )

				# WRITE PER FILE
				writepath = filename.replace( "02_MKD", "03_^DAT" ).replace( "02_TXT", "03_^DAT" ).replace( "02_NOTES", "03_^DAT" )
				writepath = prep.insert_caret( writepath )
				if univ != ".":
					#print univ
					writepath = "%s.[%s]" % ( writepath, univ )

				if PASSAGE_dat and requires_refresh( filename, writepath, "PASSAGE" ):
					util.write_listdict_to_file( writepath + ".PASSAGE.tsv", PASSAGE_dat )

				if OCC_dat and requires_refresh( filename, writepath, "OCC" ):
					util.write_listdict_to_file( writepath + ".OCC.tsv", OCC_dat )

				if TXT_dat and requires_refresh( filename, writepath, "TXT" ):
					util.write_listdict_to_file( writepath + ".TXT.tsv", TXT_dat )

				if PEOPLA_dat and requires_refresh( filename, writepath, "PEOPLA" ):
					util.write_listdict_to_file( writepath + ".PEOPLA.tsv", PEOPLA_dat )

				if REMIT_dat and requires_refresh( filename, writepath, "REMIT" ):
					util.write_listdict_to_file( writepath + ".REMIT.tsv", REMIT_dat )

				if BEQUEST_dat and requires_refresh( filename, writepath, "BEQUEST" ):
					util.write_listdict_to_file( writepath + ".BEQUEST.tsv", BEQUEST_dat )

				if WILLREF_dat and requires_refresh( filename, writepath, "BEQUEST" ):
					util.write_listdict_to_file( writepath + ".BEQUEST.tsv", WILLREF_dat )

				if DEATH_dat and requires_refresh( filename, writepath, "DEATH" ):
					util.write_listdict_to_file( writepath + ".DEATH.tsv", DEATH_dat )

				if STATUS_dat and requires_refresh( filename, writepath, "STATUS" ):
					util.write_listdict_to_file( writepath + ".STATUS.tsv", STATUS_dat )

				# ---------------------------------------------------------------------- #

				if MEMBER_dat and requires_refresh( filename, writepath, "MEMBER" ):
					util.write_listdict_to_file( writepath + ".MEMBER.tsv", MEMBER_dat )

				# ---------------------------------------------------------------------- #

				if SRC_letter_dat and requires_refresh( filename, writepath, "SRC_LETTER" ):
					util.write_listdict_to_file( writepath + ".SRC_LETTER.tsv", SRC_letter_dat )

				if SRC_will_dat and requires_refresh( filename, writepath, "SRC_WILL" ):
					util.write_listdict_to_file( writepath + ".SRC_WILL.tsv", SRC_will_dat )

				if SRC_dat and requires_refresh( filename, writepath, "SRC" ):
					util.write_listdict_to_file( writepath + ".SRC.tsv", SRC_dat )


parse_TRX_directories( run_dir )
