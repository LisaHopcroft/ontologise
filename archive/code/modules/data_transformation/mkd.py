#!/usr/bin/python
import csv
import sys
import os
import glob
from collections import OrderedDict
import pandas as pd
import ontologize.modules.util.performance as performance
import ontologize.modules.util.confdat as confdat


def update_place_vals( PEOPLA_dict ):
	place_id = PEOPLA_dict["place_id"]
	if place_id:
		i=1
		for el in place_id.split(", "):
			if len(el) == 3 and el.upper() == el:
				PEOPLA_dict["place_%s" % i] = el
				i+=1
	return PEOPLA_dict


def get_pers_id_context( pers_id ):
	if not pers_id: return ( "", "" )

	if "{" in pers_id:
		return ( pers_id.split("{")[0].strip(), pers_id.split("{")[1].replace( "}","" ).strip() )
	return ( pers_id, "" )


# ------------------------------------------------------------------------------------------ #
# File handling stuff
# ------------------------------------------------------------------------------------------ #

def convert_single_date( txtdate ):
	y1 = m1 = d1 = ""
	if ( len( txtdate ) == 4 ):
		y1	= txtdate[:4]
		m1	= ""
		d1	= ""

	if ( len( txtdate ) == 7 and txtdate.count("-") == 1 ):
		y1	= txtdate[:4]
		m1	= txtdate[6:7]
		d1	= ""

	if ( len( txtdate ) == 10 and txtdate.count("-") == 2 ):
		y1	= txtdate[:4]
		m1	= txtdate[5:7]
		d1	= txtdate[8:10]

	if ( len( txtdate ) == 8 and txtdate.count("-") == 0 ):
		y1	= txtdate[:4]
		m1	= txtdate[4:6]
		d1	= txtdate[6:8]

	return { 	"date1_y": y1,
				"date1_m": m1,
				"date1_d": d1,
				"date1_rel": "",
				"date1_spec": "",
				"date2_y": "",
				"date2_m": "",
				"date2_d": "",
				"date2_rel": "",
				"date2_spec": "" }


def convert_txtdate_to_DAT( txtdate ):
	blank_date = { 	"date1_y": "",
					"date1_m": "",
					"date1_d": "",
					"date1_rel": "",
					"date1_spec": "",
					"date2_y": "",
					"date2_m": "",
					"date2_d": "",
					"date2_rel": "",
					"date2_spec": "" }

	if not txtdate:
		return blank_date

	if "," in txtdate:
		txtdate = txtdate.split(",")[0]

	if any( x in txtdate for x in [ "(", ")", "?", "/", ".", "th", "*" ] ): # TODO: should handle all of this stuff, rather than just rejecting the data...
		print( "WARNING: Malformed date" )
		return blank_date

	if not "->" in txtdate and not "<>" in txtdate:
		return convert_single_date( txtdate )
	elif "->" in txtdate:
		dates = txtdate.split("->")

		if len( dates ) > 2:
			print( "WARNING: Malformed date" )
			return blank_date

		if len( dates ) < 1:
			print( "WARNING: Malformed date" )
			return blank_date

		if len( dates ) == 1:
			if txtdate.startswith("->"):
				date_obj = convert_single_date( dates[0] )
				date_obj["data_rel"] = "ends"
				return date_obj
			if txtdate.endswith("->"):
				date_obj = convert_single_date( dates[0] )
				date_obj["data_rel"] = "starts"
				return date_obj

		if len( dates ) == 2:
			first_date_obj = convert_single_date( dates[0] )
			second_date_obj = convert_single_date( dates[1] )

			return { 	"date1_y":    first_date_obj["date1_y"],
						"date1_m":    first_date_obj["date1_m"],
						"date1_d":    first_date_obj["date1_d"],
						"date1_rel":  "starts",
						"date1_spec": first_date_obj["date1_spec"],
						"date2_y":    second_date_obj["date1_y"],
						"date2_m":    second_date_obj["date1_m"],
						"date2_d":    second_date_obj["date1_d"],
						"date2_rel":  "ends",
						"date2_spec": second_date_obj["date1_spec"] }

	elif "<>" in txtdate:
		dates = txtdate.split("<>")

		if len( dates ) > 2:
			print( "WARNING: Malformed date" )
			return blank_date

		if len( dates ) < 2:
			print( "WARNING: Malformed date" )
			return blank_date

		if len( dates ) == 2:
			first_date_obj = convert_single_date( dates[0] )
			second_date_obj = convert_single_date( dates[1] )

			return { 	"date1_y":    first_date_obj["date1_y"],
						"date1_m":    first_date_obj["date1_m"],
						"date1_d":    first_date_obj["date1_d"],
						"date1_rel":  "earliest",
						"date1_spec": first_date_obj["date1_spec"],
						"date2_y":    second_date_obj["date1_y"],
						"date2_m":    second_date_obj["date1_m"],
						"date2_d":    second_date_obj["date1_d"],
						"date2_rel":  "latest",
						"date2_spec": second_date_obj["date1_spec"] }


def get_ATTR_vals( filepath ):
	ATTR_vals = {}
	with open(filepath.replace( "\\", "" ), "r") as r:
		for line in r.readlines():
			if line.startswith("----"):
				break
			if line.startswith("#") and ":" in line:
				ATTR_vals[ line.split(":",1)[0].lower().replace("#","") ] = line.split(":",1)[1].strip()
	return ATTR_vals


def get_ATTR_val( key, filepath ):
	with open(filepath.replace( "\\", "" ), "r") as r:
		for line in r.readlines():
			if line.startswith("-------"):
				break
			if line.startswith("#") and ":" in line:
				if line.split(":",1)[0].lower().replace("#","") == key.lower():
 					return line.split(":",1)[1].strip()
	return ""


def get_src_type( filepath ):
	with open(filepath.replace( "\\", "" ), "r") as r:
		for line in r.readlines():
			if line.startswith( "#[" ):
				return line.strip()[2:-1]
	return ""


def get_numimg_from_ref( base_path, ref, path="" ):
	dirpath = get_path_from_ref( base_path, ref )
	path = dirpath['val'] + "/01_JPG"
	if os.path.exists( path ):
		return str(len(glob.glob(path + "/*")))

	path = dirpath['val'] + "/01_PDF"
	if os.path.exists( path ):
		return str(len(glob.glob(path + "/*")))

	return "."


def get_DAT_vals_from_dir( base_path, pers_id ):
	ex = "."
	wi = "."
	re = "."
	colonies = {}

	PEOPLA_path = DB_dir + "/01_TSV/^PEOPLA.tsv"
	if os.path.exists( PEOPLA_path ):
		with open( PEOPLA_path, "r" ) as r:
			reader = csv.DictReader( r, delimiter="\t" )

			for row in reader:
				#if row["PERS_ID"] == pers_id: #sort this out...
				if row["ACTION"] == "AT":
					if "WIN" in row["AT"]:
						wi = "ADV"
				if row["ACTION"] == "EX":
					if any( substr in row["AT"] for substr in HLD_vals ):
						ex = "HLD"
					elif any( substr in row["AT"] for substr in LLD_vals ):
						ex = "LLD"
					elif "SCO" in row["AT"]:
						ex = "SCO"
					elif "ENG" in row["AT"]:
						ex = "ENG"
					elif "..." in row["AT"]:
						ex = "..."
					else:
						ex = "."
				if ( row["ACTION"] == "RE" or row["ACTION"] == "RET" or row["ACTION"] == "DIED" ):
					if any( substr in row["AT"] for substr in HLD_vals ):
						re = "HLD"
					elif any( substr in row["AT"] for substr in LLD_vals ):
						re = "LLD"
					elif "SCO" in row["AT"]:
						re = "SCO"
					elif "ENG" in row["AT"]:
						re = "ENG"
					elif "..." in row["AT"]:
						re = "..."
					else:
						re = "."
				if "WIN, " in row["AT"]:
					colony_txt = row["AT"].replace( "WIN, ","" )
					if "," in colony_txt:
						colony_txt = colony_txt.split(",",1)[0]
					colonies[ colony_txt ] = 1

	colonies_txt = ""
	for key, val in colonies.items():
		colonies_txt += key + ", "
	return { 'ex': ex, 'wi': wi, 're': re, 'colonies': colonies_txt }


# ------------------------------------------------------------------------------------------ #
# Microformat parsing stuff
# ------------------------------------------------------------------------------------------ #

def get_val( line, pattern):
	if pattern == "ID": # special case for IDs...
		match = re.search(r"\[(.+?)\]", line) # how to do start of line ... ?
	else:
		match = re.search(r"%s\[(.+?)\]" % pattern, line)

	if match:
		return match.group(1)

def split_lines( mf_txt ):
	if "]" in mf_txt:
		mf_txt = mf_txt.split( "]",1 )[1] # cut after the id declaration...
	return mf_txt.split( "###" )

def get_pers_id( mf_txt ):
	pers_id = get_val( mf_txt, "ID" )
	if pers_id: return pers_id

def get_is_military( mf_txt ):
	for line in split_lines( mf_txt ):
		if "+[military]" in line.lower():
			return True

def get_died_at( mf_txt ):
	for line in split_lines( mf_txt ):
		if line.startswith( "DIED-" ):
			at = get_val( line, "AT" )
			if at: return at

def get_died_in( mf_txt ):
	for line in split_lines( mf_txt ):
		if line.startswith( "DIED-" ):
			at = get_val( line, "IN" )
			if at: return at

def get_died_age( mf_txt ):
	for line in split_lines( mf_txt ):
		if line.startswith( "DIED-" ):
			aged = get_val( line, "AGED" )
			if aged: return aged

def get_ex_at( mf_txt ):
	for line in split_lines( mf_txt ):
		if line.startswith( "EX-" ):
			at = get_val( line, "AT" )
			if at: return at

def get_father_at( mf_txt ):
	is_father = False
	for line in split_lines( mf_txt ):
		if line.startswith( ">FATHER" ) or ( line.startswith( ">" ) and is_father and not line.startswith( ">MOTHER" ) ): #etc
			is_father = True
			at = get_val( line, "AT" )
			if at: return at

def get_father_occ( mf_txt ):
	is_father = False
	for line in split_lines( mf_txt ):
		if line.startswith( ">FATHER" ) or ( line.startswith( ">" ) and is_father and not line.startswith( ">MOTHER" ) ): #etc
			is_father = True
			occ = get_val( line, "OCC" )
			if occ: return occ

def get_colony_from_addr( addr_txt ):
	if not addr_txt:
		return ""
	if addr_txt.startswith( "WIN, " ) and len( addr_txt ) >= 8:
		return addr_txt[5:8]

def get_zone_from_addr( addr_txt ):
	return addr_txt[:3]

def get_subzone_from_addr( addr_txt ):
	return addr_txt[:8]

def get_quarter_from_addr( addr_txt ):
	return addr_txt[:3]

# ------------------------------------------------------------------------------------------ #

def parse_src_vals( src_vals, line ):
	if line.startswith( "#[" ):
		src_vals["SRC_TYPE"] = line.strip()[2:-1]
	return src_vals


def parse_scope_vals( scope_vals, global_vals, line ):
	if line.startswith( "##" ) and ":" in line and not line.startswith("###"):
		key = line.split(":")[0].replace("##","")
		val = line.split(":")[1].strip()
		if key.upper() == key: # if caps, then it's a global val
			global_vals["SRC_"+key.lower()] = val
		else:
			scope_vals[key.lower()] = val

	return scope_vals, global_vals


def is_mf_add_line( line ):
	line = line.replace( "\t", "" ).strip()
	return line == "###+++"


def is_mf_tag_line( line ):
	if "\\t" in line or line.startswith("###+") or line.startswith("###-"):
		return False
	line = line.replace( "\t", "" )
	return line.startswith( "###" ) and not "---" in line and not is_mf_add_line( line )


def get_scope_from_line( line ):
	return line.count(">\t")


def get_val_from_relationship_line( line, scope_vals ):
	val = line.split("*",1)[1].split("*",1)[0].replace("\n","")
	return val


def get_val_from_action_line( line ):
	val = line.replace( "###", "" ).replace( "\t", "" ).replace( ">", "" ).replace( "(", "" ).strip()
	return val


def get_val_from_mf_line( line, scope_vals ):
	val = line.split("[",1)[1].split("]",1)[0].replace("\n","")
	if val.startswith("^"):
		if ", " in val:
			lookup 		= val.split(", ",1)[0].replace("^","")
			remainder 	= val.split(", ",1)[1]
			if lookup in scope_vals:
				val 		= scope_vals[ lookup ].strip() + remainder
		else:
			lookup 		= val.replace("^","")
			if lookup in scope_vals:
				val 		= scope_vals[ lookup ]
	return val


def get_contextval_from_mf_line( line, scope_vals, line_num ):
	remainder = line.rsplit("]",1)[1]
	if "(" in remainder:
		remainder = remainder.split("(",1)[1]
		if ")" in remainder:
			return "(%s)" % remainder.split(")",1)[0]

	return str(line_num)


def get_globalval_from_mf_line( line, scope_vals, line_num ):
	remainder = line.rsplit("]",1)[1]
	if "{" in remainder:
		remainder = remainder.split("{",1)[1]
		if "}" in remainder:
			return "%s" % remainder.split("}",1)[0]

	return str("")


def get_key_from_mf_line( line ):
	return line.split("[",1)[0].replace("\t","").replace("#","").lower().replace("-","_")

# ------------------------------------------------------------------------------------------ #

def is_addr_HLD( address ):
	if address: return any( address.startswith( substr ) for substr in HLD_vals )
	return False

def is_addr_LLD( address ):
	if address: return any( address.startswith( substr ) for substr in LLD_vals )
	return False

def is_addr_WIN( address ):
	if address: return any( address.startswith( substr ) for substr in WIN_vals )
	return False

def is_addr_GBR( address ):
	if address: return any( address.startswith( substr ) for substr in GBR_vals )
	return False

def is_addr_SCO( address ):
	if address: return any( address.startswith( substr ) for substr in SCO_vals )
	return False

def is_addr_ENG( address ):
	if address: return any( address.startswith( substr ) for substr in ENG_vals )
	return False

# ------------------------------------------------------------------------------------------ #

def get_GBR_zone_from_addr( addr_txt ):
	if not addr_txt: return ""

	if is_addr_HLD( addr_txt ):
		return "HLD"
	if is_addr_LLD( addr_txt ):
		return "LLD"
	if is_addr_ENG( addr_txt ):
		return "ENG"

def get_WIN_zone_from_addr( addr_txt ): # colony
	if not addr_txt: return ""

	if addr_txt == "WIN":
		return "UNK"

	if addr_txt.startswith( "WIN, " ) and len( addr_txt ) >= 8:
		return addr_txt[5:8]

def get_INT_zone_from_addr( addr_txt ):
	if not addr_txt: return "NON"

	if addr_txt.startswith( ( "ATL", "ASI", "AUS", "CSA" ) ):
		return "OTH"
	elif addr_txt.startswith( ( "WIN" ) ):
		return "WIN"
	elif addr_txt.startswith( ( "EIN" ) ):
		return "EIN"
	elif addr_txt.startswith( ( "CNA" ) ):
		return "CNA"
	else:
		return "NON"

def get_addr( addr_txt, scope ):
	if not addr_txt:
		return ""

	if scope == "WIN":
		if addr_txt.startswith( "WIN" ):
			return addr_txt
		else:
			return ""

	if scope == "INT":
		if not addr_txt.startswith( ("GBR", "ENG", "SCO") ):
			return addr_txt
		else:
			return ""

	if scope == "GBR":
		if addr_txt.startswith( ("GBR", "ENG", "SCO") ):
			return addr_txt
		else:
			return ""

	return addr_txt


# ------------------------------------------------------------------------------------------ #
# Microformat gathering stuff...
# ------------------------------------------------------------------------------------------ #

def get_DAT_fm_filelist( pattern, filelist ):
	DAT = []
	for filepath in filelist:
		filepath = filepath.replace( "\\", "" )
		filepath = filepath.replace( "02_TXT", "03_^DAT" )
		filepath += "." + pattern
		if os.path.exists( filepath ):
			with open( filepath, "r" ) as r:
				DAT += get_dict_fm_TSV( filepath )
	return DAT


# ------------------------------------------------------------------------------------------ #
# Reporting
# ------------------------------------------------------------------------------------------ #

# DEPRECATED: ... use relational database instead ...
def digest_PEOPLA( PEOPLA_dat ):
	# first make a digested file which groups the PEOPLA records for same individual together...
	DIGEST_dat = []

	DIGEST = OrderedDict()
	ref 	= ""
	pers_id = ""
	line_num = 0
	born_in = ""
	died_in = ""
	born_at = ""
	died_at = ""
	at 		= ""
	father_at = ""
	filepath = ""

	for row in PEOPLA_dat:
		if ( row["PERS_ID"] != pers_id ) or ( row["FILEPATH"] != filepath ) or ( "ods" in row["FILEPATH"].lower() and row["LINE_NUM"] != line_num ):
			# save...
			DIGEST["REF"] 		= ref
			DIGEST["PERS_ID"] 	= pers_id
			DIGEST["LINE_NUM"] 	= line_num
			DIGEST["BORN_IN"] 	= born_in
			DIGEST["BORN_AT"] 	= born_at
			DIGEST["DIED_IN"] 	= died_in
			DIGEST["DIED_AT"] 	= died_at
			DIGEST["AT"] 		= at
			DIGEST["FATHER_AT"] = father_at
			DIGEST["FILEPATH"] 	= filepath
			DIGEST_dat.append( DIGEST )
			# start again...
			DIGEST = OrderedDict()

		# gather values...
		ref 		= row["REF"]
		pers_id 	= row["PERS_ID"]
		line_num 	= row["LINE_NUM"]
		filepath 	= row["FILEPATH"]
		if row["ACTION"] == "DIED":
			died_in = row["DATE"]
			died_at = row["AT"]
		if row["ACTION"] == "BORN":
			born_in = row["DATE"]
			born_at = row["AT"]
		if row["ACTION"] == "AT":
			at = row["AT"]
		if row["ACTION"] == "FATHER_AT":
			father_at = row["AT"]

	return DIGEST_dat
