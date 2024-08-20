import re, codecs
from collections import OrderedDict
from unidecode import unidecode
import collections
import operator

import csv, os, sys
sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.confdat as confdat


dataset_dir = "/media/michael/SSD3/Dropbox/workspace/2.research/3.Research/1.Subsets"


regex = re.compile('[^a-zA-Z ;&]') # remove all non-letter characters...


# wee hack to wrap text in spaces, to make sure search matches distinct words, not in-word patterns
def prep_txt( txt ):
	txt = regex.sub( '', txt ) #remove special characters...
	return " %s " % txt.rstrip().lstrip().lower()


ambiguous_terms = [ # to implement... use tertiary colour on the graph for these terms...
	"Newton", 	#surnames
	"Carrol",

	"Petty", 	#features
	"Tongue",

	"Bellfield", #other places
	"Fairburn",
	"Thornhill",
	"Heathfield",
]


ambiguous_terms_proc = []
for a in ambiguous_terms:
	a = " %s " % a.lower()
	ambiguous_terms_proc .append( a )


T71_primary_sample = [
	"1",		# JAM, CAT
	"13",		# JAM, DOR
	"19",		# JAM, JOH
	"25",		# JAM, TIV
	"33",		# JAM, MAR
	"43",		# JAM, ANN
	"51", 		# JAM, VER
	"57",		# JAM, CLA
	"65",		# JAM, MAN
	"74-80",	# JAM, KIN
	"119",		# JAM, ROY
	"125",		# JAM, AND
	"139",		# JAM, DAV
	"145",		# JAM, TIE
	"151",		# JAM, POR
	"158",		# JAM, GEO
	"164-6",	# JAM, ELI
	"178",		# JAM, WES
	"190",		# JAM, HAN
	"201-4",	# JAM, JAM
	"224-9",	# JAM, TRE
	"244",		# ANT
	"253",		# KIT
	"267",		# GRE
	"337-47",	# DOM
	"364",		# NEV
	"370",		# VIR
	"376-9",	# LUC
	"437",		# BER
	"461-2",	# TOB
	"493", 		# VIN
	"501-5", 	# TRI
	"520-3"		# BAR
]

T71_secondary_sample = [
	"316-7",	#GRE
	"362",		#DOM
	"487-8",	#TOB
	"499",		#VIN
	"516-7"		#TRI
]

colony_order = [
	"WIN, JAM",
	"WIN, DGO",
	"WIN, VIR", # "CRO", # "THO",
	"WIN, ANG",
	"WIN, K&N",
	"WIN, ANT",
	"WIN, MON",
	"WIN, GUA",
	"WIN, DOM",
	"WIN, MAR",
	"WIN, LUC",
	"WIN, BAR",
	"WIN, VIN",
	"WIN, GRE", #"CAR", - part of Grenada
	"WIN, TOB",
	"WIN, TRI",
	"WIN, GUI", # "ESS", # "DEM", # "BER",
	"WIN, SUR", ]

parish_order = [
	"WIN, HAN",
	 "WIN, WES",
	 "WIN, JAM",
	 "WIN, ELI",
	 "WIN, TRE",
	 "WIN, MAN",
	 "WIN, ANN",
	 "WIN, CLA",
	 "WIN, VER",
	 "WIN, JOH",
	 "WIN, DOR",
	 "WIN, MAR",
	 "WIN, TIV",
	 "WIN, CAT",
	 "WIN, AND",
	 "WIN, KIN",
	 "WIN, GEO",
	 "WIN, ROY",
	 "WIN, DAV",
	 "WIN, POR",
	 "WIN, TIE" ]

qualifiers = [ "young", "old", "little", "big", "l", "o" ]


def wildcard_search( search_txt, val_txt ):
	if "*" in search_txt:
		if all( el in val_txt for el in search_txt.split( "*" ) ):
			return True
	return False

def simple_add_total_row( listdict, data_type="", sort_by="" ):
	if not listdict: return

	num_rows = len( listdict )
	if num_rows == 0: return listdict

	# update label text
	for row in listdict:
		if "ITEM" in row:
			if data_type == "parish":
				for pair in confdat.replace_parishes:
					row["ITEM"] = str(row["ITEM"]).replace( pair[0], pair[1] )
			elif data_type == "colony":
				for pair in confdat.replace_colonies:
					row["ITEM"] = str(row["ITEM"]).replace( pair[0], pair[1] )
			else:
				for pair in confdat.replace_GBR:
					row["ITEM"] = str(row["ITEM"]).replace( pair[0], pair[1] )
			# should I do this at the latex presentation stage??

	# then sort
	if sort_by:
		listdict = sorted(listdict, key=lambda k: k[sort_by])
	else:
		listdict = sorted(listdict, key=lambda k: k['ITEM'])

	headers = listdict[0].keys()

	tot_row = OrderedDict()
	for key in headers:
		tot_row[ key ] = 0

	tot_row["ITEM"] = "TOTAL"

	sum_cols = [
		"FREQ",
		"FREQ_1",
		"FREQ_2",
		"FREQ_3",
		"SRC_SIZE",
		"FULL_SRC_SIZE",
		"*_thold",
		"N"
	]
	avg_cols = [
		"VAL",
		"VAL_TOT",
		"VAL_1",
		"VAL_2",
		"VAL_3",
		"FREQ_PCT_1",
		"FREQ_PCT_2",
		"FREQ_PCT_3",
		"VAL_PCT_1",
		"VAL_PCT_2",
		"VAL_PCT_3",
		"PCT_1",
		"PCT_2",
		"PCT_3",
		"PCT_2v3",
		"VAL_PCT_*"
		"*_diffpct",
		"*_prob",
		"*_AVG",
	]
	repeat_cols = [
		"*_baseline"
	]

	# go through the dataset and populate the total row...
	for row in listdict:
		headers = row.keys()
		for col in row:
			for val_col in sum_cols + avg_cols:
				if val_col == col or wildcard_search( val_col, col ):
					if row[ col ]:
						tot_row[ col ] += float(row[ col ])

			for val_col in repeat_cols:
				if val_col == col or wildcard_search( val_col, col ) and col in tot_row:
					tot_row[ col ] = row[ col ]

	# do some normalisation of the data...
	for col in tot_row:
		for val_col in avg_cols:
			if val_col == col or wildcard_search( val_col, col ):
				tot_row[ col ] = round( tot_row[ col ] / float(num_rows), 1 )

	listdict.append( tot_row )

	return listdict


def is_term_ambiguous( term ):
	is_ambiguous = False
	for a in ambiguous_terms_proc:
		if term == a:
			return True


def is_a_match( searchtxt, term, searchtype ):
	if searchtype == "placenames":
		return term in searchtxt
	else:
		return searchtxt.startswith( term )


def handle_multiple_places( txt ):
	if ";" in txt:
		returntxt = ""
		els = txt.split(";")
		for el in els:
			if ", " in el:
				el = el.rsplit(", ",1)[1]
			returntxt += " " + el
		return returntxt
	else:
		return txt


def search_txt( terms, txt, analysis_type, searchtype ):
	if analysis_type.startswith( "SURNAMES" ):
		return find_surnames( terms, txt, searchtype )
	else:
		return find_placenames( terms, txt, searchtype )


def find_placenames( termslist, txt, searchtype="" ):
	if searchtype == "placenames":
		txt = get_plnname_fm_place_id( txt )
	if not txt:
		return [] # no plantation name in this row, so skip analysing...

	txt = prep_txt( txt )
	resultlist = []
	for term in termslist:
		if term == "":
			continue

		term = prep_txt( term )

		for q in qualifiers:
			txt = txt.replace( " %s " % q, " " )

		if is_term_ambiguous( term ):
			continue

		if is_a_match( txt, term, searchtype ):
			resultlist.append( term )
		else: # search the synonyms...
			for synonym in synonyms_list:
				if synonym[0] == term:
					if is_a_match( txt, synonym[1], searchtype ):
						resultlist.append( synonym[1] )
						break # don't add multiple matching synonyms...
	return resultlist


surname_derivs = [
	"M'",
	"Mc",
	"Mac",
	"Mack",
	"Macc",
	"Mc ",
	"Mc k",
	"Mc c",
	"Mac ",
	"Mac k",
	"Mac c",
]


def get_surname_deriv( key ):
	options = []
	options.append( key )
	if key.startswith( "M'" ):
		for deriv in surname_derivs:
			options.append( key.replace( "M'", deriv, 1 ) )

	if key.startswith( "MAC" ):
		for deriv in surname_derivs:
			options.append( key.replace( "MAC", deriv, 1 ) )
	return options


def find_surnames( keylist, searchtxt, searchtype="" ):
	searchtxt = prep_txt( searchtxt )
	resultlist = []
	for key in keylist:
		for deriv in get_surname_deriv( key ):
			deriv = prep_txt( deriv )
			if searchtxt.startswith( deriv ):
				resultlist.append( deriv )
	return resultlist


def postprocess_lt( results, src, dataset_filepath, analysis_type, searchtype="" ):
	terms	= []

	rows = util.get_dict_fm_TSV( dataset_filepath )
	for row in rows:
		if analysis_type.startswith( "SURNAMES" ):
			terms.append( row["###SURNAME"] )
		else:
			terms.append( row["###AT"] )

	# FOR each row in the src file

	i = 0
	for row in src["data"]:
		matches 	= []
		num_results = 0

		t 	= unidecode(row['txt'])
		t.encode("ascii")
		txt	= t


		# run a search using every item in the dataset ...

		matches = search_txt( terms, txt, analysis_type, searchtype )

		results[i][ 'MATCHES_TXT'] 	= ";".join( matches )

		i += 1

	return results


def get_grp_totals( item, freq, grp_txt ):
	freq_1 = 0
	freq_2 = 0
	freq_3 = 0
	matches_1 = []
	matches_2 = []
	matches_3 = []
	if "HLD" in grp_txt:
		freq_1 = freq
		for i in range( 0, freq_1 ):
			matches_1.append( item ) # append a match from each freq, so totals are correct
	elif "LLD" in grp_txt or "SCO" in grp_txt:
		freq_2 = freq
		matches_2.append( item )
		for i in range( 0, freq_2 ):
			matches_2.append( item ) # append a match from each freq, so totals are correct
	else:
		freq_3 = freq
		matches_3.append( item )
		for i in range( 0, freq_3 ):
			matches_3.append( item ) # append a match from each freq, so totals are correct

	return( freq_1, freq_2, freq_3, matches_1, matches_2, matches_3 )


def cross_analysis_lt( src_data, analysis_type, writedir, subsets=[], suffix="LT", is_full=True, searchtype="" ):

	if suffix:
		suffix = ".%s" % suffix

	# FOR each src file...

	for src in src_data:

		sample_size = get_sample_size( src["data"] )
		if sample_size == 0:
			"Empty src data"
			continue

		# FOR each analysis file: add columns to the results object...

		for dataset_filepath in get_all_dataset_filepaths( analysis_type, subsets ):

			# set up the results object... to be appended to...
			results = []
			for row in src[ "data" ]:
				result = OrderedDict()
				txt = row[ 'txt' ]
				if "{" in txt:
					txt = txt.split( "{" )[0]
				result[ '###DATE' ] 	= row[ 'date1_y' ]
				result[ 'ITEM' ] 		= txt
				result[ 'ITEM_NUM' ] 	= row[ 'freq' ]
				result[ 'SRC_SIZE' ]    = sample_size
				results.append( result )

			results 	= postprocess_lt( results, src, dataset_filepath, analysis_type, searchtype )


			# add tail values to results object...

			i = 0
			for row in src[ "data" ]:
				results[i][ 'src_ref' ] 		= src[ 'src_ref' ]
				results[i][ 'src_filepath' ] 	= row[ 'src_filepath' ]
				i += 1


			# delete empty rows

			if not is_full:
				results[:] = [x for x in results if x["FREQ"] > 0]


			# write to file...

			dataset_identifier	= get_dataset_identifier( dataset_filepath )
			if is_full or tot_freq > 0:
				writepath 	= "%s/../dat/^%s/^%s.[%s].[%s]%s.tsv" % ( writedir, analysis_type, analysis_type, src[ "src_ref" ], dataset_identifier, suffix )
				util.write_listdict_to_file( writepath, results )


def cast_int( text ):
	return int(str(text).replace(",",""))


def add_total_row( results, sample_size, src={}, dat_type="", override_base_pct="" ):
	if sample_size == 0:
		return None, None

	tot_freq 	= 0
	tot_size 	= 0
	tot_freq_1 	= 0
	tot_freq_2 	= 0
	tot_freq_3 	= 0
	tot_base_pct = 0
	tot_base_tot = 0
	tot_grp_tot = 0

	headers 	= []

	# (1) calculate totals
	for row in results:
		headers = row.keys()
		tot_freq += int(row["FREQ"])
		if "ITEM_SIZE" in row:
			tot_size 	+= cast_int( row["ITEM_SIZE"] )
		tot_freq_1 		+= cast_int( row["FREQ_1"] )
		tot_freq_2 		+= cast_int( row["FREQ_2"] )
		tot_freq_3 		+= cast_int( row["FREQ_3"] )
		if "BASE_PCT" in row:
			if row["BASE_PCT"]:
				tot_base_pct += float( row["BASE_PCT"] )
		if "BASE_TOT" in row:
			tot_base_tot += int(row["BASE_TOT"])
		if "BASE_GRP_TOT" in row:
			if not row["BASE_GRP_TOT"]:
				row["BASE_GRP_TOT"] = 0
			tot_grp_tot += int(row["BASE_GRP_TOT"])
		row["N"] = ""

	# (2) create and append the tot row
	tot_row = OrderedDict()
	for header in headers:
		tot_row[ header ] 	= " "

	tot_row[ "ITEM" ] 		= "TOTAL"

	if "ITEM_SIZE" in headers and tot_size:
		tot_row[ "ITEM_SIZE" ] 	= tot_size

	tot_row[ "N" ]		= len(results)
	tot_row[ "FREQ" ]	= tot_freq
	tot_row[ "FREQ_1" ]	= tot_freq_1
	tot_row[ "FREQ_2" ]	= tot_freq_2
	tot_row[ "FREQ_3" ]	= tot_freq_3
	if tot_base_pct:
		tot_row[ "BASE_PCT" ] 		= tot_base_pct
	if tot_base_tot:
		tot_row[ "BASE_TOT" ] 		= tot_base_tot
	if tot_grp_tot:
		tot_row[ "BASE_GRP_TOT" ] 	= tot_grp_tot

	tot_row[ "SRC_SIZE" ] 	= sample_size

	if "DATE" in headers and "src_date" in src:
		tot_row[ "DATE" ] 		= src["src_date"]

	if "ITEM" in headers and "src_at" in src:
		tot_row[ "ITEM" ] 		= src["src_at"]

	results.append( tot_row )

	# (3) go back and update values
	for row in results:
		if row["SRC_SIZE"]:
			row["PCT"]		= ( row["FREQ"]		/ float(row["SRC_SIZE"]) ) * 100
			row["PCT_1"]	= ( row["FREQ_1"] 	/ float(row["SRC_SIZE"]) ) * 100
			row["PCT_2"]	= ( row["FREQ_2"] 	/ float(row["SRC_SIZE"]) ) * 100
			row["PCT_3"]	= ( row["FREQ_3"] 	/ float(row["SRC_SIZE"]) ) * 100

			if override_base_pct != "":
				row["BASE_PCT"] = override_base_pct

			# either set in the above override, or already present...
			if "BASE_PCT" in row:
				base_pct 	= row["BASE_PCT"]
				pct 		= row["PCT"]
				if not str(base_pct).replace(".","").replace("e-","").isdigit():
					base_pct = 0

				if float(base_pct):# or int(base_pct):
					row["OBS_VS_BASE"]	= round( ( float(pct) / float(base_pct) )*100, 2 )-100
				else:
					row["OBS_VS_BASE"]	= 0

		if "matches_1" in row and "matches_2" in row and "matches_3" in row:
			row["matches_1"] = write_matches_list_as_txt( row["matches_1"] )
			row["matches_2"] = write_matches_list_as_txt( row["matches_2"] )
			row["matches_3"] = write_matches_list_as_txt( row["matches_3"] )

	return ( results, tot_freq )


def is_dataset_file( fname, analysis_type, subsets ):
	return "[$%s]" % ( analysis_type ) in fname and fname.endswith( ".tsv" ) and ( any( "@"+subset in fname for subset in subsets ) or not subsets	)


def get_all_dataset_filepaths( analysis_type, subsets ):
	filepaths = []
	for root, dirs, files in os.walk( dataset_dir ):
		for fname in files:
			filepath = "%s/%s" % ( root, fname )
			if is_dataset_file( fname, analysis_type, subsets ) and "HLD" in filepath:
				filepaths.append( "%s/%s" % ( root, fname ) )
	return filepaths


def get_dataset_identifier( filepath ):
	if "@" in filepath:
		return "@" + filepath.rsplit("@",1)[1].split("]",1)[0]
	else:
		dirref 	= filepath.rsplit("/",3)[1].replace("/","")
		fileref = filepath.rsplit("/",1)[1].replace( "ALL.html.", "" )
		return ( dirref + fileref ).replace( ".tsv", "" ).replace( "ALL", "" ).replace( ".[$PLACENAMES]", "" ).replace( ".[$POPULATIONS]", "" ).replace( ".[$SURNAMES]", "" ).replace( ".[$COORDINATES]", "" )


def is_yearly( suffix ):
	return "yearly" in suffix


def is_parish( suffix ):
	return "parish" in suffix


def is_colony( suffix ):
	return "colony" in suffix


def add_empty_tot_row( key, tots ):
	if not key in tots:
		tots[ key ] = OrderedDict()
		tots[ key ][ "FREQ" ] = 0
		tots[ key ][ "FREQ_1" ] = 0
		tots[ key ][ "FREQ_2" ] = 0
		tots[ key ][ "FREQ_3" ] = 0
		tots[ key ][ "PCT" ] = 0
		tots[ key ][ "PCT_1" ] = 0
		tots[ key ][ "PCT_2" ] = 0
		tots[ key ][ "PCT_3" ] = 0
		tots[ key ][ "SRC_SIZE" ] = 0
		tots[ key ][ "matches_1" ] = []
		tots[ key ][ "matches_2" ] = []
		tots[ key ][ "matches_3" ] = []
	return tots


def get_yearly_limits( data ):
	return( 1750, 1851 ) # hack to override... will kinda be context specific...

	years = []
	for row in data:
		try:
			val = int( row["y1"] )
		except ValueError:
			continue
		years.append( val )
	return ( min(years), max(years) )


def get_plnname_fm_place_id( place_id ):
	if "," in place_id:
		last_el = place_id.rsplit( ",", 1 )[1]

		if last_el.isupper():
			return "" # no plantation name given... just colony name...
		else:
			return last_el

	return place_id


def get_colony_fm_place_id( place_id ):
	if not place_id.startswith( "WIN, " ):
		return ""
	tmp_id = place_id.replace( "WIN, ", "" )

	if not tmp_id[:3].isupper():
		return ""
	else:
		return place_id[:8]


def get_parish_fm_place_id( place_id ):
	if not place_id.startswith( "WIN, JAM, " ):
		return ""
	tmp_id = place_id.replace( "WIN, JAM, ", "" )

	if not tmp_id[:3].isupper():
		return ""
	else:
		return place_id[:13]


def postprocess_tot( dataset_filepath, src, analysis_type, suffix="", searchtype="" ):

	tots = OrderedDict()

	if is_colony( suffix ):
		# set up the dict in order
		for val in colony_order:
			tots = add_empty_tot_row( val, tots )

	if is_parish( suffix ):
		# set up the dict in order
		for val in parish_order:
			tots = add_empty_tot_row( val, tots )

	if is_yearly( suffix ):
		print( "IS YEARLY" )
		# set up for all years in the range...
		lowest_year, highest_year = get_yearly_limits( src["data"] )
		for val in range( lowest_year, highest_year ):
			tots = add_empty_tot_row( val, tots )

	dataset_rows = util.get_dict_fm_TSV( dataset_filepath )


	# go through each src line...

	totals_base_pct = 0

	for src_row in src["data"]:

		searchtxt = src_row["txt"]

		if is_yearly( suffix ):
			key_val = src_row["date1_y"]

		if is_colony( suffix ):
			key_val = get_colony_fm_place_id( src_row["place_id"] )

		if is_parish( suffix ):
			key_val = get_parish_fm_place_id( src_row["place_id"] )

		if not key_val in tots:
			#if is_colony( suffix ) or is_parish( suffix ):
			#	if key_val:
			#		print( "Skipping malformed data: %s" % key_val )
			#	continue
			tots = add_empty_tot_row( key_val, tots )

		tots[ key_val ][ "SRC_SIZE" ] += src_row["freq"]



		# go through each line in the dataset...

		for row in dataset_rows:

			if "###AT" in row:
				dataset_item = row["###AT"]
			elif "###SURNAME" in row:
				dataset_item = row["###SURNAME"]
			else:
				print( "NO ITEM SPECIFIED: %s" % dataset_filepath )
				continue

			matches = search_txt( [dataset_item], searchtxt, analysis_type, searchtype )

			if len( matches ) > 0:
				tots[ key_val ][ "FREQ" ] += src_row["freq"]
				if "###GRP" in row:
					freq_1, freq_2, freq_3, matches_1, matches_2, matches_3 = get_grp_totals( dataset_item, src_row["freq"], row["###GRP"] )
					tots[ key_val ][ 'FREQ_1' ] += freq_1
					tots[ key_val ][ 'FREQ_2' ] += freq_2
					tots[ key_val ][ 'FREQ_3' ] += freq_3
					tots[ key_val ][ 'matches_1' ] += matches_1
					tots[ key_val ][ 'matches_2' ] += matches_2
					tots[ key_val ][ 'matches_3' ] += matches_3

			if "BASE_PCT" in row:
				if row["BASE_PCT"]:
					totals_base_pct += float(row["BASE_PCT"])

	# ADD totals row

	tots, freq = add_total_row( dictdict_to_listdict( tots ), get_sample_size( src["data"] ), dat_type="total", override_base_pct=totals_base_pct )

	return tots


def dictdict_to_listdict( dictdict ):
	listdict = []
	for k, v in dictdict.items():
		new = OrderedDict()
		new["ITEM"] = k
		for k2, v2 in v.items():
			new[k2] = v2
		listdict.append( new )

	return listdict


def write_matches_list_as_txt( listobj ):
	results = {}

	for el in listobj:
		if el in results:
			results[el] += 1
		else:
			results[el] = 1

	txt = ""
	for k, v in sorted(results.items(), key=operator.itemgetter(1), reverse=True):
		if txt:
			txt += ", "
		if v > 1:
			txt += "%s (%s)" % ( k.strip(), v )
		else:
			txt += "%s" % ( k.strip() )
	return txt


def postprocess( dataset_filepath, src, analysis_type, suffix="", searchtype="", additional="" ):

	sample_size = get_sample_size( src["data"] )

	# FIRST: set up the results object to mirror the dataset file...

	rows = util.get_dict_fm_TSV( dataset_filepath )
	tsv_rows 	= []
	for row in rows:
		item_size = 0
		if "###AT" in row:
			item = row["###AT"]
		if "###SURNAME" in row:
			item = row["###SURNAME"]
		if "###POPULATION" in row:
			item_size = row["###POPULATION"]

		tsv_row = OrderedDict()
		for col in row:
			tsv_row[ col ] = row[ col ]

		tsv_row[ "ITEM" ]		= item
		if item_size:
			tsv_row[ "ITEM_SIZE" ]	= item_size
		tsv_row[ "FREQ" ] 		= 0
		tsv_row[ "FREQ_1" ] 	= 0
		tsv_row[ "FREQ_2" ] 	= 0
		tsv_row[ "FREQ_3" ] 	= 0
		tsv_row[ "PCT" ] 		= 0
		tsv_row[ "PCT_1" ] 		= 0
		tsv_row[ "PCT_2" ] 		= 0
		tsv_row[ "PCT_3" ] 		= 0
		tsv_row[ "SRC_SIZE" ] 	= sample_size
		tsv_row[ "SRC_DATE" ] 	= src["src_date"]
		tsv_row[ "SRC_AT" ] 	= src["src_at"]
		tsv_row[ "matches_1" ] 	= []
		tsv_row[ "matches_2" ] 	= []
		tsv_row[ "matches_3" ] 	= []
		tsv_rows.append( tsv_row )


	# For each line in the dataset...

	i = 0
	for row in tsv_rows:

		# Search the entire source data, to augment an analysis...

		for src_row in src["data"]:

			matches = search_txt( [row["ITEM"]], src_row["txt"], analysis_type, searchtype )

			if len( matches ) > 0:
				row["FREQ"] += src_row["freq"]
				if "###GRP" in row:
					freq_1, freq_2, freq_3, matches_1, matches_2, matches_3 = get_grp_totals( row["ITEM"], src_row["freq"], row["###GRP"] )
					row[ "FREQ_1" ] += freq_1
					row[ "FREQ_2" ] += freq_2
					row[ "FREQ_3" ] += freq_3
					row[ 'matches_1' ] += matches_1
					row[ 'matches_2' ] += matches_2
					row[ 'matches_3' ] += matches_3

	# add a totals row

	return add_total_row( tsv_rows, sample_size )


def get_sample_size( src_vals ):
	tot = 0
	for src_row in src_vals:
		tot += src_row["freq"]
	return tot


def cross_analysis( src_data, analysis_type, writedir, subsets=[], suffix="", is_full=True, searchtype="", additional="" ):

	if suffix:
		suffix = ".%s" % suffix

	# FOR each dataset file...

	for dataset_filepath in get_all_dataset_filepaths( analysis_type, subsets ):

		print( dataset_filepath )
		# FOR each src file

		for src in src_data:

			if ".yearly" in suffix:

				# yearly

				xsuffix = suffix + ".TOT"
				tsv_rows 	= postprocess_tot( dataset_filepath, src, analysis_type, xsuffix, searchtype=searchtype )

				if tsv_rows:
					writepath 	= "%s/../dat/^%s/^%s.[%s].[%s]%s.tsv" % ( writedir, analysis_type, analysis_type, get_dataset_identifier( dataset_filepath ), src["src_ref"], xsuffix )

					util.write_listdict_to_file( writepath, tsv_rows )

			elif ".at" in suffix:

				# colonies

				xsuffix = suffix + ".colony.TOT"
				tsv_rows 	= postprocess_tot( dataset_filepath, src, analysis_type, xsuffix, searchtype=searchtype )

				if tsv_rows:
					writepath 	= "%s/../dat/^%s/^%s.[%s].[%s]%s.tsv" % ( writedir, analysis_type, analysis_type, get_dataset_identifier( dataset_filepath ), src["src_ref"], xsuffix )
					util.write_listdict_to_file( writepath, tsv_rows )

				# parishes

				xsuffix = suffix + ".parish.TOT"
				tsv_rows 	= postprocess_tot( dataset_filepath, src, analysis_type, xsuffix, searchtype=searchtype )

				if tsv_rows:
					writepath 	= "%s/../dat/^%s/^%s.[%s].[%s]%s.tsv" % ( writedir, analysis_type, analysis_type, get_dataset_identifier( dataset_filepath ), src["src_ref"], xsuffix )
					util.write_listdict_to_file( writepath, tsv_rows )

				# create a RT mapping file... (EXPERIMENTAL)
				# if lat and lon in the dataset filepath...

				if analysis_type == "PLACENAMES":
					tsv_rows, tot_freq 	= postprocess( dataset_filepath, src, analysis_type, searchtype=searchtype )

					if tsv_rows:
						if is_full or tot_freq > 0:
							writepath 	= "%s/../dat/^%s/^%s.[%s].[%s]%s.mappings.tsv" % ( writedir, analysis_type, analysis_type, get_dataset_identifier( dataset_filepath ), src["src_ref"], suffix )
							util.write_listdict_to_file( writepath, tsv_rows )

			else:

				# general

				tsv_rows, tot_freq 	= postprocess( dataset_filepath, src, analysis_type, searchtype=searchtype, additional=additional )

				if tsv_rows:
					if not is_full:
						tsv_rows[:] = [x for x in tsv_rows if x["FREQ"] > 0] # delete the empty rows

					if is_full or tot_freq > 0:
						writepath 	= "%s/../dat/^%s/^%s.[%s].[%s]%s.tsv" % ( writedir, analysis_type, analysis_type, get_dataset_identifier( dataset_filepath ), src["src_ref"], suffix )
						util.write_listdict_to_file( writepath, tsv_rows )
