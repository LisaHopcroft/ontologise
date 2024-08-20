#!/usr/bin/env python
# -*- coding: utf-8 -*-

# THIS NEEDS TO BE COMPLETELY REFACTORED: CODE NEEDS TO BE MOVED TO THE RELEVANT MODULES, AND UNIT TESTED... #


try:
	# for Python2
	from Tkinter import *
except ImportError:
	# for Python3
	from tkinter import *
import sqlite3
import os, time
import datetime
import calendar
import glob
import csv
from collections import OrderedDict

from .confdat import *
from .performance import *
#from rdb import *
#from mkdmf import *
#from processing import *
#import postprocessing 	# changed from import *
#import confdat			# changed from import *
#import performance
#from ods2csv import *



def file_safe( text_str ):
	return text_str.replace("\"", "").replace("*", "")


# ------------------------------------------------------------------------------------------ #
# Generic
# ------------------------------------------------------------------------------------------ #

alphabet = { 	'1': 'a',
				'2': 'b',
				'3': 'c',
				'4': 'd',
				'5': 'e',
				'6': 'f',
				'7': 'g',
				'8': 'h',
				'9': 'i',
				'10': 'j',
				'11': 'k',
				'12': 'l',
				'13': 'm',
				'14': 'n',
				'15': 'o',
				'16': 'p',
				'17': 'q',
				'18': 'r',
				'19': 's',
				'20': 't',
				'21': 'u',
				'22': 'v',
				'23': 'w',
				'24': 'x',
				'25': 'y',
				'26': 'z', }


def merge_two_dicts(x, y):
	z = x.copy()   	# start with x's keys and values
	z.update(y)		# modifies z with y's keys and values & returns None
	return z


def is_blank( val ):
	if val == ".":
		return True
	if val == "":
		return True
	if val == " ":
		return True
	if not val:
		return True

def convert_list_to_sql( listobj ):
	sql = ""
	first = True
	for county in listobj:
		if not first:
			sql += "+"
		sql += "%s_total" % county
		first = False
	return sql

def get_zone( addr ):
	if addr.count(",") >= 2:
		return addr.split(",", 2)[0]
	if addr.count(",") == 1:
		return addr.split(",", 1)[0]
	return addr


def num_instances_before_match( text, find, terminal ):
	text = text.split( terminal, 1 )[0]
	return text.count( find )

def assure_path_exists(path):
	dir = os.path.dirname(path)
	if not os.path.exists(dir): os.makedirs(dir)

def add_to_dict( dictobj, index, value ):
	if not index in dictobj:
		dictobj[ index ] = OrderedDict()
		dictobj[ index ][ "NUM" ] = 0
		dictobj[ index ][ "TOT" ] = 0
		dictobj[ index ][ "AVG" ] = 0
		dictobj[ index ][ "VALS" ] = []
	dictobj[ index ][ "NUM" ] += 1
	dictobj[ index ][ "TOT" ] += value
	dictobj[ index ][ "AVG" ] = round( dictobj[ index ][ "TOT" ] / dictobj[ index ][ "NUM" ], 1 )
	dictobj[ index ][ "VALS" ].append( value )
	return dictobj

def convert_to_float( text ):
	is_number = True
	nondecimal = re.compile(r'[^\d.]+')
	text = nondecimal.sub('', text )
	try:
		return float( text )
	except ValueError:
		return False

def turn_dict_of_dicts_into_list_of_lists( d ):
	l = []
	for key, subdict in d.items():
		subl = []
		subl.append( key )
		for subkey, subval in subdict.items():
			subl.append( subval )
		l.append( subl )
	return l


# ------------------------------------------------------------------------------------------ #


def write_dictdict_to_file( writepath, dictobj, key_txt="", sort=True ):
	if not dictobj: return
	assure_path_exists( writepath )

	with open( writepath, "w" ) as outfile:
		print( writepath )
		if len( dictobj ) == 0: return
		w = csv.writer( outfile, delimiter='\t', lineterminator="\n" )

		key, vals = dictobj.items().next()
		w.writerow( [key_txt] + vals.keys() )

		if sort:
			for key, vals in sorted(dictobj.items()):
				w.writerow( [key] + vals.values() )
		else:
			for key, vals in dictobj.items():
				w.writerow( [key] + vals.values() )


def write_dict_to_file( writepath, dictobj, key_txt="" ):
	if not dictobj: return
	assure_path_exists( writepath )

	with open( writepath, "w" ) as outfile:
		if len( dictobj ) == 0: return
		w = csv.writer( outfile, delimiter='\t', lineterminator="\n" )

		w.writerow( [key_txt] + ["TOT"] )

		for key, vals in dictobj.items():
			w.writerow( [ key, vals ] )

def write_dictlist_to_file( writepath, dictobj, key_txt="" ):
	if not dictobj: return
	assure_path_exists( writepath )

	with open( writepath, "w" ) as outfile:
		if len( dictobj ) == 0: return
		w = csv.writer( outfile, delimiter='\t', lineterminator="\n" )

		w.writerow( [key_txt] + ["..."] )

		for key, vals in sorted(dictobj.items(), key=lambda kv: (kv[1],kv[0])):
			w.writerow( [ key ] + vals )


def write_list_to_file( writepath, listobj ):
	if not listobj: return
	assure_path_exists( writepath )

	with open( writepath, "w" ) as w:
		if len( listobj ) == 0: return
		for el in listobj:
			w.write( el )


def write_listlist_to_file( writepath, listobj ):
	if not listobj: return
	assure_path_exists( writepath )

	with open( writepath, "w" ) as w:
		if len( listobj ) == 0: return
		for el in listobj:
			w.write( "\t".join( map( str, el ) ) + "\n" )


def convert_to_ascii( listobj ):
	new_list = []
	for val in listobj:
		if isinstance(val, basestring):
			val = val.encode('ascii', 'ignore')
			new_list.append( val )
	return new_list


def write_listdict_to_file( writepath, listobj ):
	if not listobj: return
	assure_path_exists( writepath )

	with open( writepath, "w" ) as outfile:
		if len( listobj ) == 0: return
		w = csv.writer( outfile, delimiter='\t', lineterminator="\n" )

		w.writerow( listobj[0].keys() )

		for obj in listobj:
			vals = obj.values()
			w.writerow( vals )


def write_panda_to_file( writepath, obj, db_headers ):
	obj.to_csv( writepath, sep="\t", index=False, columns=db_headers, header=False )


def get_dict_fm_TSV( filepath ):
	DAT = []
	with open(filepath, 'r') as r:
		tsv = csv.DictReader( r, delimiter='\t' )
		for row in tsv:
			DAT.append( OrderedDict(sorted(row.items(),
						  key=lambda item: tsv.fieldnames.index(item[0]))) )
		r.close() # being explicit to see if improves performance...
	return DAT

	## OLD: non-performant code
	'''
	DAT = []
	with open(filepath, 'r') as r:
		tsv = csv.DictReader( r, delimiter='\t' )
		for row in tsv:
			obj = OrderedDict()
			for f in tsv.fieldnames:
				obj[f] = row[f]
			DAT.append( obj )
	return DAT
	'''


def get_panda_fm_TSV( filepath ):
	return pd.read_table( filepath, header=0 )


def write_ordlistdict_to_file( writepath, listobj ):
	assure_path_exists( writepath )

	with open( writepath, "w" ) as outfile:
		if len( listobj ) == 0: return
		w = csv.writer( outfile, delimiter='\t', lineterminator="\n" )

		w.writerow( listobj[0].keys() )

		for obj in listobj:
			vals = obj.values()
			w.writerow( [str(s[0]) for s in vals] ) #vals


# ------------------------------------------------------------------------------------------ #


def analyse_file( filepath, prepend ):
	yearly_data = OrderedDict()
	colony_data = OrderedDict()
	sample_data = OrderedDict()

	with open( filepath, 'r' ) as tsv:
		tsv = csv.DictReader(tsv, delimiter='\t')
		for row in tsv:
			date = row["ATTR_date"]
			year = date[:4]

			corresp_addr = ""
			colony = ""
			fm_at = row["ATTR_fm@"].replace(" ?","").replace("?","")
			to_at = row["ATTR_to@"].replace(" ?","").replace("?","")
			if "WIN, " in fm_at:
				groups = fm_at.split(",")
				colony = get_colony_from_addr( fm_at )
				corresp_addr = to_at
			elif "WIN, " in to_at:
				groups = to_at.split(",")
				colony = get_colony_from_addr( to_at )
				corresp_addr = fm_at

			# set up blank dictionaries...
			if not year in yearly_data:
				yearly_data[year] = OrderedDict()
				yearly_data[year]["num_total"]	=  0
				yearly_data[year]["num_complete"] =  0
				yearly_data[year]["num_REM"]   =  0
				yearly_data[year]["num_RET"]   =  0
				yearly_data[year]["num_DWI"]   =  0

			if not colony in colony_data:
				colony_data[colony] = OrderedDict()
				colony_data[colony]["num_total"]	=  0
				colony_data[colony]["num_complete"] =  0
				colony_data[colony]["num_REM"]   =  0
				colony_data[colony]["num_RET"]   =  0
				colony_data[colony]["num_DWI"]   =  0

			if not corresp_addr in sample_data:
				sample_data[corresp_addr] = OrderedDict()
				sample_data[corresp_addr]["num_total"]	=  0
				sample_data[corresp_addr]["num_complete"] =  0
				sample_data[corresp_addr]["num_REM"]   =  0
				sample_data[corresp_addr]["num_RET"]   =  0
				sample_data[corresp_addr]["num_DWI"]   =  0

			# append to the dictionaries...
			yearly_data[year]["num_total"] += 1
			colony_data[colony]["num_total"] += 1
			sample_data[corresp_addr]["num_total"] += 1

			if row["IS_COMPLETE"] == "True":
				yearly_data[year]["num_complete"]   += 1
				colony_data[colony]["num_complete"] += 1
				sample_data[corresp_addr]["num_complete"] += 1

			if row["NUM_REM"] != "0":
				yearly_data[year]["num_REM"]	 += 1
				colony_data[colony]["num_REM"]   += 1
				sample_data[corresp_addr]["num_REM"] += 1
			if row["NUM_RET"] != "0":
				yearly_data[year]["num_RET"]	 += 1
				colony_data[colony]["num_RET"]   += 1
				sample_data[corresp_addr]["num_RET"] += 1
			if row["NUM_DWI_NW"] != "0":
				yearly_data[year]["num_DWI"]	 += 1
				colony_data[colony]["num_DWI"]   += 1
				sample_data[corresp_addr]["num_DWI"] += 1

	print( "" )
	print( "Yearly data..." )
	write_dict_to_file( "../dat/^%s.yearly.tsv" % prepend, yearly_data, "Year" )

	print( "" )
	print( "Colony data..." )
	write_dict_to_file( "../dat/^%s.colony.tsv" % prepend, colony_data, "Colony" )

	print( "" )
	print( "Recipient data..." )
	write_dict_to_file( "../dat/^%s.sample.tsv" % prepend, sample_data, "PERS_ID" )

# ------------------------------------------------------------------------------------------ #


def build_surnames_row( colony, year, nation, total ):
	tmp_row = []
	tmp_row.append( colony )
	tmp_row.append( year )
	tmp_row.append( nation )
	tmp_row.append( total )
	return tmp_row


def get_branch_dir( path ):
	dirname = path.rsplit("/",1)[1]

	if dirname.startswith( "0" ):
		return os.path.dirname( path ) #go up one dir
	else:
		return get_branch_dir(  os.path.dirname( path ) )


def get_path_from_ref( base_path, ref, path="", orig_base_path="", final_dir="",  ):
	os.chdir( base_path )

	if not orig_base_path:
		orig_base_path = base_path

	ref_groups = ref.split( ".", 1 )
	if len( ref_groups ) < 2:
		next = ref
		ref_stub = None
	else:
		next =		ref_groups[0]
		ref_stub = 	ref_groups[1]

	next_dir = None
	for element in os.listdir( "." ):
		# special hack... because WILL references aren't unique we need to check name, date etc also at the last dir stage
		if not ref_stub: #i.e. at the last dir
			if final_dir:
				if final_dir in element and next in element:
					next_dir = element
		else:
			if element.startswith( next + "," ) or ( element == next ):
				next_dir = element

	full_path = orig_base_path + path

	if next_dir:
		if ref_stub: #i.e. there is more to go...
			return get_path_from_ref( next_dir, ref_stub, path + "/" + next_dir, orig_base_path, final_dir )
		else:
			return { 'is_full': True, 'is_onedir': False, 'val': full_path + "/" + next_dir }
	else:
		if not ref_stub: #i.e. at the end
			return { 'is_full': False, 'is_onedir': True, 'val': full_path }
		else:
			return { 'is_full': False, 'is_onedir': False, 'val': full_path }


def get_will_dirname( ref, persid, date ):
	print( ref )
	print( persid )
	print( date )
	if "." in ref:
		return "%s, %s, %s" % ( ref.rsplit(".",1)[1], persid.split(",")[1][1:2] + "." + persid.replace(":: ","").replace("- ","").split(",")[0], date[:4] )
	return False


def get_numwords_from_ref( base_path, ref, path="" ):
	dirpath = get_path_from_ref( base_path, ref )
	path = dirpath['val'] + "/02_TXT"
	if not os.path.exists( path ):
		return "."
	else:
		return str(len(glob.glob(path + "/*")))


def get_numtags_from_ref( base_path, ref, path="" ):
	dirpath = get_path_from_ref( base_path, ref )
	path = dirpath['val'] + "/03_^DAT"
	if not os.path.exists( path ):
		return "."
	else:
		return str(len(glob.glob(path + "/*")))


def write_stubfile( base_path, content="", samplename="" ):
	os.chdir( base_path )
	newdir = "02_TXT"
	stubfile = "^%s.txt" % samplename
	stubpath = newdir + "/" + stubfile
	if not os.path.exists( newdir ):
		os.makedirs( newdir )
	#if not os.path.exists( stubpath ):
	with open( stubpath, "w" ) as w:
		w.write( content )


def get_about_file( rootdir ):
	for root, dirs, files in os.walk( rootdir ):
		for file in files:
			if file.startswith( "#about.txt" ): return root + "/" + file
	return False


def get_source_details_from_file( about_file ):
	src_vals = {}

	with open(about_file) as f:
		content = f.readlines()
		src_vals["year"] = None
		src_vals["month"] = None
		src_vals["day"] = None
		src_vals["ref"] = None
		src_vals["archive"] = None
		src_vals["shorttitle"] = None
		src_vals["longtitle"] = None
		src_vals["url"] = None
		src_vals["frame"] = None
		src_vals["id"] = None

		for row in content:
			if row.startswith("Year: "):
				src_vals["year"] = row.split(": ")[1].rstrip()
			if row.startswith("Month: "):
				src_vals["month"] = row.split(": ")[1].rstrip()
			if row.startswith("Day: "):
				src_vals["day"] = row.split(": ")[1].rstrip()
			if row.startswith("Reference: "):
				src_vals["ref"] = row.split(": ")[1].rstrip()
			if row.startswith("Archive: "):
				src_vals["archive"] = row.split(": ")[1].rstrip()
			if row.startswith("Short Title: "):
				src_vals["shorttitle"] = row.split(": ")[1].rstrip()
			if row.startswith("Long Title: "):
				src_vals["longtitle"] = row.split(": ")[1].rstrip()
			if row.startswith("Url: "):
				src_vals["url"] = row.split(": ")[1].rstrip()
			if row.startswith("Frame: "):
				src_vals["frame"] = row.split(": ")[1].rstrip()
			if row.startswith("Id: "):
				src_vals["id"] = row.split(": ")[1].rstrip()

	return src_vals


def create_sitelinked_row( prefix ):
	return False


def create_rooting_row( prefix, person, place, rel_type, src_vals, row ):
	# TODO: also pass the number of person and place in the ; seperated list and use that to get values relating to that position

	vals = {}

	if person == "" or person == ".": return False
	if place == "" or place == ".": return False

	# if deviation from standard rel_type
	if prefix+"ROLE_MOD" in row and row[prefix+"ROLE_MOD"] != "." and row[prefix+"ROLE_MOD"] != "": rel_type = row[prefix+"ROLE_MOD"]

	vals["person"] = person
	vals["place"] = place
	vals["rel_type"] = rel_type
	vals["year1"] = src_vals["year"]
	vals["source"] = src_vals["id"]
	vals["date_added"] = datetime.datetime.now()

	vals["mapping_ref"] = row["MAPPING_REF"] if "MAPPING_REF" in row else False
	vals["person_txt"] = row["PROPRIETOR_TXT"] if "PROPRIETOR_TXT" in row else False
	vals["place_txt"] = row["PLACE_TXT"] if "PLACE_TXT" in row else False
	vals["record_num"] = row["SEQ"] if "SEQ" in row else False

	vals["date2_spec"] = vals["date2_rel"] = vals["date1_spec"] = vals["date1_rel"] = vals["day2"] = vals["month2"] = vals["year2"] = vals["month1"] = vals["day1"] = ""

	tmp_row = []
	tmp_row.append( vals["source"] )
	tmp_row.append( vals["mapping_ref"] )
	tmp_row.append( vals["date2_spec"] )
	tmp_row.append( vals["date2_rel"] )
	tmp_row.append( vals["date1_spec"] )
	tmp_row.append( vals["date1_rel"] )
	tmp_row.append( vals["day2"] )
	tmp_row.append( vals["month2"] )
	tmp_row.append( vals["year2"] )
	tmp_row.append( vals["person"] )
	tmp_row.append( vals["place"] )
	tmp_row.append( vals["rel_type"] )
	tmp_row.append( vals["year1"] )
	tmp_row.append( vals["month1"] )
	tmp_row.append( vals["day1"] )
	tmp_row.append( vals["date_added"] )
	tmp_row.append( vals["person_txt"] )
	tmp_row.append( vals["place_txt"] )

	return tmp_row


def lookahead(iterable):
	it = iter(iterable)
	last = it.next() # next(it) in Python 3
	for val in it:
		yield last, False
		last = val
	yield last, True


def file_safe( text_str ):
	return text_str.replace(u'\xa0', u' ')


def filepath_safe( text_str ):
	return text_str.replace(' ', '\ ').replace(',', '\,').replace('[', '\[').replace(']', '\]').replace("'", "\\'").replace( "(","\(" ).replace( ")","\)" ).replace( "&", "\&" )


def is_letter( f ):
	f.seek(0)
	first_line = f.readline()
	if "#LETTER" in first_line:
		return True
	return False

def is_minutes( f ):
	f.seek(0)
	first_line = f.readline()
	if "#MINUTES" in first_line:
		return True
	return False

def is_letter_file( filepath ):
	with open( filepath, "r" ) as r:
		first_line = r.readline()
		if "#LETTER" in first_line:
			return True
	return False

def is_will_file( filepath ):
	with open( filepath, "r" ) as r:
		first_line = r.readline()
		if "#WILL" in first_line:
			return True
	return False

def make_name_readable( val ):
	if val == ".":
		return "Unknown"

	val = re.sub(r'\[(.*?)\]', '', val)

	if "," in val:
		forenames = val.split(",")[1].strip()
		surname = val.split(",")[0].title().strip()
		if surname == "." and forenames == ".":
			return "Unknown"
		if surname == ".":
			return "%s" % ( forenames )
		if forenames == ".":
			return "Mr %s" % ( surname )
		else:
			return "%s %s" % ( forenames, surname )
	return val


def make_date_readable( val ):
	if val == ".":
		return "Undated"

	if val == "...":
		return "< DATE: recheck with original >"

	if "-" in val:
		val = val.replace( "-", "" )

	val = val.replace( "XX", "00" )

	#datetime.strptime doesn't work on dates before 1900
	if val.isdigit() and len( val ) == 8:
		year_val = val[0:4]
		month_val = val[5:6]
		day_val = val[7:8]
		if month_val == "00":
			return "%s" % (	year_val.lstrip("0") )
		elif day_val == "00":
			return "%s &s" % (	calendar.month_name[int(month_val)],
								year_val.lstrip("0") )
		else:
			return "%s %s %s" % (	day_val,
									calendar.month_name[int(month_val)],
									year_val.lstrip("0") )
	return val


colony_abbrv = [[ "CRO", "St Croix" ],
				[ "KIT", "St Kitts" ],
				[ "ANT", "Antigua" ],
				[ "GUA", "Guadeloupe" ],
				[ "DOM", "Dominica" ],
				[ "MAR", "Martinique" ],
				[ "LUC", "St Lucia" ],
				[ "VIN", "St Vincent" ],
				[ "GRE", "Grenada" ],
				[ "BAR", "Barbados" ],
				[ "TRI", "Trinidad" ],
				[ "GUI", "Guiana" ],
				[ "DEM", "Demerara" ],
				[ "BER", "Berbice" ],
				[ "ESS", "Essequebo" ],
				[ "WIN", "West Indies" ]]

def make_place_readable( val ):
	for abbrv in colony_abbrv:
		if abbrv[0] in val:
			return abbrv[1]


def get_key_detail( f, search ):
	f.seek(0)
	for line in f.readlines():
		if search.lower() in line.lower():
			val = line.replace( search, "" ).replace( "#", "" ).strip()
			if "Fm:" in line or "To:" in line:
				return make_name_readable( val )
			if "Date:" in line:
				return make_date_readable( val )
			if "@:" in line:
				return make_place_readable( val )
			return val
	return search


def create_crops_row( crops, place, src_vals ):
	vals = {}

	if place == "" or place == ".": return False

	tmp_row = []

	vals["source"] = src_vals["id"]
	vals["place"] = place
	vals["is_sugar"] = 0
	vals["is_cotton"] = 0
	vals["is_coffee"] = 0
	vals["is_plantains"] = 0
	vals["is_cattle"] = 0
	vals["is_tobacco"] = 0
	vals["is_cocoa"] = 0
	vals["is_timber"] = 0
	vals["is_abandoned"] = 0

	for crop in crops:
		if crop=="SUG":
			vals["is_sugar"] = 1
		if crop=="CTN":
			vals["is_cotton"] = 1
		if crop=="COF":
			vals["is_coffee"] = 1
		if crop=="PLA":
			vals["is_plantains"] = 1
		if crop=="CAT":
			vals["is_cattle"] = 1
		if crop=="TOB":
			vals["is_tobacco"] = 1
		if crop=="CCA":
			vals["is_cocoa"] = 1
		if crop=="TIM":
			vals["is_timber"] = 1
		if crop=="XXX":
			vals["is_abandoned"] = 1

	tmp_row.append( vals["source"] )
	tmp_row.append( vals["place"] )
	tmp_row.append( vals["is_sugar"] )
	tmp_row.append( vals["is_cotton"] )
	tmp_row.append( vals["is_coffee"] )
	tmp_row.append( vals["is_plantains"] )
	tmp_row.append( vals["is_cattle"] )
	tmp_row.append( vals["is_tobacco"] )
	tmp_row.append( vals["is_cocoa"] )
	tmp_row.append( vals["is_timber"] )
	tmp_row.append( vals["is_abandoned"] )

	return tmp_row


def get_hashes( num_hashes ):
	hashes = ""
	for j in range( 0, num_hashes ):
		 hashes += "#"
	return hashes


def escape_filepath( filepath ):
	return filepath.replace( " ", "\ " ).replace( "(", "\(" ).replace( ")", "\)" ).replace( ",", "\," ).replace( "^", "\^" ).replace( "&", "\&" ).replace( "[", "\[" ).replace( "]", "\]" ).replace( "'", "\\'" ).replace( "{", "\{" ).replace( "}", "\}" ).replace( "$", "\$" )


def intWithCommas(x):
	if type(x) not in [type(0), type(0)]:
		raise TypeError("Parameter must be an integer.")
	if x < 0:
		return '-' + intWithCommas(-x)
	result = ''
	while x >= 1000:
		x, r = divmod(x, 1000)
		result = ",%03d%s" % (r, result)
	return "%d%s" % (x, result)


def get_TRX_wordcount( readfile ):
	readfile.seek( 0 )
	num_words = 0
	for line in readfile:
		if not line.startswith("#") and not line.startswith(">"):
			words = line.split()
			num_words += len(words)
	return num_words


def get_TRX_tagcount( readfile ):
	readfile.seek( 0 )
	num_tags = 0
	for line in readfile:
		if line.startswith("#"):
			num_tags += 1
	return num_tags


def get_DIR_imgcount( dirpath ):
	if os.path.exists( dirpath + "/01_JPG" ):
		return str(len(glob.glob(dirpath + "/01_JPG/*")))
	if os.path.exists( dirpath + "/01_PDF" ):
		return "PDF"


def is_TRX_complete( readfile ):
	readfile.seek( 0 )
	for line in readfile:
		if "[...]" in line:
			return False
	return True


# method description ...
def get_level_from_crmb( path ):
	level = ""
	if os.path.exists( path ):
		with open( path, 'r' ) as r:
			firstline = r.readline().rstrip()
			if firstline.startswith("#"):
				return firstline
	return level

# method description ...
def update_desc_from_crmb( path, desc ):
	if os.path.exists( path ):
		with open( path, 'r' ) as r:
			for line in r:
				if line.startswith( "#BIBDESC: " ):
					desc = line.rstrip()[10:]
	return desc

# method description ...
def get_trail_from_path( path, path_root ):
	subpath = path.replace(path_root,"")

	trail = []
	num_dirs = len( subpath.split("/") )

	lvl = 1
	if not subpath.startswith( "0" ):
		trail.append( ( 1, "Scotland", "zone" ) )
		lvl = lvl + 1

	# loop through dirs in the path
	for i in range( 0, num_dirs ):
		split = subpath.split("/")
		dir_name = split[i]
		dir_path = '/'.join(split[:i+1])

		if dir_name.startswith( "_" ) or "#" in dir_name:
			return None

		crmb_path = path_root + dir_path + "/crmb.txt"
		level = get_level_from_crmb( crmb_path )

		desc = dir_name

		if dir_name.startswith( "0" ) and len( dir_name.split(".") ) > 1:
			desc = dir_name.split(".")[1]

		if "skip" not in level and not any( x in dir_name for x in skip_dirs ):
			desc = update_desc_from_crmb( crmb_path, desc )
			trail.append( ( lvl, desc, level ) )
			lvl = lvl + 1

	return trail


def get_collection_dirpath( filepath ):
	if "/01_" in filepath:
		col_dir = filepath.split( "/01_" )[0]
		sub_dir = filepath.split( "/01_" )[1]
		if sub_dir.count( "/" ) == 0:
			return False, False # must have matched on trailing filename... not what we want...
		if sub_dir.count( "/" ) == 1:
			return col_dir, "" # no sub dir
		if sub_dir.count( "/" ) == 2:
			return col_dir, sub_dir.split("/")[1] # return middle dir
		if sub_dir.count( "/" ) > 2:
			return False, False # must have matched earlier directory... not what we want
	return False, False


def create_mapping_row( place, src_vals, row ):
	# TODO: also pass the number of person and place in the ; seperated list and use that to get values relating to that position

	vals = {}

	if place == "" or place == ".": return False

	vals["place"] = place
	vals["source"] = src_vals["id"]
	vals["mapping_ref"] = row["MAPPING_REF"] if "MAPPING_REF" in row else False
	vals["date_added"] = datetime.datetime.now()

	vals["day"] = vals["month"] = ""

	tmp_row = []
	tmp_row.append( vals["source"] )
	tmp_row.append( vals["place"] )
	tmp_row.append( vals["mapping_ref"] )
	tmp_row.append( vals["date_added"] )

	return tmp_row
