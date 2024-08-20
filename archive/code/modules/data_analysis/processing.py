#!/usr/bin/python

from .rdb import *
from collections import OrderedDict



# util function...
def ordered_dict_prepend(dct, key, value, dict_setitem=dict.__setitem__):
    root = dct._OrderedDict__root
    first = root[1]

    if key in dct:
        link = dct._OrderedDict__map[key]
        link_prev, link_next, _ = link
        link_prev[1] = link_next
        link_next[0] = link_prev
        link[0] = root
        link[1] = first
        root[1] = first[0] = link
    else:
        root[1] = first[0] = dct._OrderedDict__map[key] = [root, first, key]
        dict_setitem(dct, key, value)


# ------------------------------------------------------------ #
# Generic functions...

def get_dat( sample, variable, scope="" ):
	if variable == "INT_zone":
		dat = OrderedDict()
		dat["WIN"] = 0
		dat["EIN"] = 0
		dat["CNA"] = 0
		dat["OTH"] = 0
	elif variable == "WIN_zone":
		dat = OrderedDict()
		for colony in postprocessing.colony_order:
			dat[colony] = 0
	else:
		dat = {}

	for row in sample:
		if variable == "place_id":
			x = get_addr( row[ "place_id" ], scope )
		elif variable == "INT_zone":
			x = get_INT_zone_from_addr( row[ "place_id" ] )
		elif variable == "WIN_zone":
			x = get_WIN_zone_from_addr( row[ "place_id" ] )
		elif variable == "GBR_zone":
			x = get_GBR_zone_from_addr( row[ "place_id" ] )
		else:
			x = row[variable]

		if not x: continue

		if not x in dat:
			if variable.endswith("_zone"): # don't add to pre-asigned column sets...
				print( "Skipping bad value: %s (%s)" % ( x, variable ) )
				continue
			else:
				dat[ x ] = 0

		dat[ x ] += 1

	return dat


def get_list( sample, vals ):
	dat = []
	for row in sample:
		dat_row = OrderedDict()
		for val in vals:
			dat_row[ val ] = row[ val ]
		dat.append( dat_row )
	return dat


def get_yearly( sample, date_key, var_key, focus="" ):
	dat = OrderedDict()
	for row in sample:
		yr 	= row[ date_key ]
		var = row[ var_key ]

		# set up a record for the year...
		if not yr in dat:
			dat[ yr ] = OrderedDict()
			dat[ yr ][ "TOT" ] = 0
			if focus == "WIN":
				for x in postprocessing.colony_order:
					dat[ yr ][ x ] = 0
			if focus == "INT":
				for x in INT_zones:
					dat[ yr ][ x ] = 0
			if focus == "GBR":
				for x in GBR_zones:
					dat[ yr ][ x ] = 0

		dat[ yr ][ "TOT" ] 	+= 1

		if focus == "WIN":
			var = get_WIN_zone_from_addr( var )
		if focus == "INT":
			var = get_INT_zone_from_addr( var )
		if focus == "GBR":
			var = get_GBR_zone_from_addr( var )
		if focus == "":
			var = "TOT"

		# skip bad values
		if not var in dat[ yr ] and focus:
			if var:
				print( "Skipping bad value: '%s' (%s)" % ( var, focus ) )
			continue

		dat[ yr ][ var ] 	+= 1

	# sort before returning...
	sorted_list = []
	for key in sorted(dat.iterkeys()):
		ordered_dict_prepend( dat[key], "YEAR", key )
		sorted_list.append( dat[key] )

	return sorted_list


def get_grouped( sample, groupby, var_key, focus="" ):
	dat = OrderedDict()
	for row in sample:
		yr 	= row[ groupby ]
		var = row[ var_key ]

		if not yr in dat:
			dat[ yr ] = OrderedDict()
			dat[ yr ][ "TOT" ] = 0
			if focus == "WIN":
				for x in WIN_zones:
					dat[ yr ][ x ] = 0
			if focus == "INT":
				for x in INT_zones:
					dat[ yr ][ x ] = 0
			if focus == "GBR":
				for x in GBR_zones:
					dat[ yr ][ x ] = 0

		dat[ yr ][ "TOT" ] 	+= 1

		if focus == "WIN":
			var = get_WIN_zone_from_addr( var )
		if focus == "INT":
			var = get_INT_zone_from_addr( var )
		if focus == "GBR":
			var = get_GBR_zone_from_addr( var )

		if not var in dat[ yr ]:
			if var and var != "":
				print( "VALUE NOT IN DICT... '%s'" % var )
			continue
			#dat[ yr ][ var ] = 0
		dat[ yr ][ var ] 	+= 1

	# sort before returning...
	sorted_list = []
	for key in sorted(dat.iterkeys()):
		ordered_dict_prepend( dat[key], groupby, key )
		sorted_list.append( dat[key] )

	return sorted_list


# ------------------------------------------------------------ #

def get_action_sample( sample, action ):
	dat = []
	for row in sample:
		if row["action"] == action:
			dat.append( row )

		# old version... #
		'''
		linenum = ""
		if row["src_filepath"].endswith( ".csv" ):
			linenum = row["src_linenum"]
		rows = RDB_get_PEOPLA( row["pers_id"], action, row["src_filepath"], linenum )
		for x in rows:
			dat.append( x )
		'''
	return dat

# ------------------------------------------------------------ #

def write_action_results( sample, action, filepath, focus ):
	new_sample = get_action_sample( sample, action )
	write_sample_results( new_sample, filepath, focus, False, action )
	return sample


def write_grouped_results( sample, groupby, filepath, focus ):
	if focus == "WIN":
		WIN_grouped 	= get_grouped( sample, groupby, "place_id", "WIN" )

		util.write_listdict_to_file( "%s.WIN_grouped.tsv" % ( filepath ), WIN_grouped )#, "PLACE" )


def write_sample_results( sample, filepath, focus, is_src_analysis=False, action="" ):
	if action: filepath = "%s.[%s]" % ( filepath, action )

	util.write_listdict_to_file( "%s.tsv" % filepath, sample )

	if is_src_analysis:
		date_key = "src_date"
	else:
		date_key = "y1"

	if focus == "WIN":
		WIN_yearly 	= get_yearly( sample, date_key, "place_id", "WIN" )
		WIN_places 	= get_dat( sample, "place_id", "WIN" )
		WIN_zones 	= get_dat( sample, "WIN_zone" )

		util.write_dict_to_file( "%s.WIN_places.tsv" % ( filepath ), WIN_places, "PLACE" )
		util.write_dict_to_file( "%s.WIN_zones.tsv" % ( filepath ), WIN_zones, "ZONE" )
		util.write_listdict_to_file( "%s.WIN_yearly.tsv" % ( filepath ), WIN_yearly )#, "YEAR" )

	if focus == "GBR":
		GBR_yearly 	= get_yearly( sample, date_key, "place_id", "GBR" )
		GBR_places 	= get_dat( sample, "place_id", "GBR" )
		GBR_zones	= get_dat( sample, "GBR_zone" )

		util.write_dict_to_file( "%s.GBR_places.tsv" % ( filepath ), GBR_places, "PLACE" )
		util.write_dict_to_file( "%s.GBR_zones.tsv" % ( filepath ), GBR_zones, "ZONE" )
		util.write_listdict_to_file( "%s.GBR_yearly.tsv" % ( filepath ), GBR_yearly )#, "YEAR" )

	if focus == "INT":
		INT_yearly 	= get_yearly( sample, date_key, "place_id", "INT" )
		INT_places	= get_dat( sample, "place_id", "INT" )
		INT_zones	= get_dat( sample, "INT_zone" )

		util.write_dict_to_file( "%s.INT_places.tsv" % ( filepath ), INT_places, "PLACE" )
		util.write_dict_to_file( "%s.INT_zones.tsv" % ( filepath ), INT_zones, "ZONE" )
		util.write_listdict_to_file( "%s.INT_yearly.tsv" % ( filepath ), INT_yearly )#, "YEAR" )

	if focus == "":
		yearly 	= get_yearly( sample, date_key, "place_id", "" )

		util.write_listdict_to_file( "%s.yearly.tsv" % ( filepath ), yearly )#, "YEAR" )

	if is_src_analysis and focus:
		grouped 	= get_grouped( sample, "src_place", "place_id", focus )
		util.write_listdict_to_file( "%s.%s_srcplace.tsv" % ( filepath, focus ), grouped )

	if not focus == "":
		# sample
		person_sample = {}
		for dat in sample:
			person_sample[ dat["pers_id"] ] = []
			person_sample[ dat["pers_id"] ].append( dat["src_filepath"] )
		util.write_dictlist_to_file( "%s.sample.tsv" % ( filepath ), person_sample, "PERS_ID" )


def filter_sample( sample, col, val ):
	dat = []
	for row in sample:
		if row[col] == val:
			dat.append( row )
	return dat


def write_MF_results( sample, filepath, MF_key, is_src_analysis=False ):
	filepath = "%s.%s" % ( filepath, MF_key )

	util.write_listdict_to_file( "%s.tsv" % filepath, sample )

	if MF_key == "PASSAGE":
		PORT 	= get_dat( sample, "port" )
		COST 		= get_list( sample, [ "y1", "cost_stg", "cost_cur", "src_filepath" ] )
		PORT_yr 	= get_yearly( sample, "y1", "port" )

		util.write_dict_to_file( "%s.PORT.tsv" % ( filepath ), PORT, "PORT" )
		util.write_listdict_to_file( "%s.COST.tsv" % ( filepath ), COST )
		util.write_dictdict_to_file( "%s.PORT_yr.tsv" % ( filepath ), PORT_yr, "YEAR" )

	#if MF_key == "MEMORIAL":
	#	sample["memorial"] 		= get_dat( sample["sample"] )
	#	util.write_listdict_to_file( "%s.tsv" % filepath, sample["sample"] )
	#	util.write_dict_to_file( "%s.memorial.tsv" % filepath, sample["memorial"], "SAFHS_ID" )

	if MF_key == "DEATH":
		CAUSES 	= get_dat( sample, "cause" )
		AGES 	= get_dat( sample, "aged" )

		util.write_dict_to_file( "%s.CAUSE.tsv" % ( filepath ), CAUSES, "CAUSE" )
		util.write_dict_to_file( "%s.AGE.tsv" % ( filepath ), AGES, "AGE" )

	'''
	if MF_key == "RETURN":
		CAUSES 	= get_dat( sample, "cause" )
		AGES 	= get_dat( sample, "aged" )

		util.write_dict_to_file( "%s.CAUSE.tsv" % ( filepath ), CAUSES, "CAUSE" )
		util.write_dict_to_file( "%s.AGE.tsv" % ( filepath ), AGES, "AGE" )
	'''

	if MF_key == "OCC":
		cols 	 = [ "y1", "pers_id", "salary_stg", "place_id", "src_filepath" ]
		src_cols = [ "sample_pers_id", "y1", "pers_id", "salary_stg", "place_id", "src_filepath" ]
		if is_src_analysis:
			cols = src_cols

		ROLE 	= get_dat( sample, "occ" )
		SALARY 	= get_list( sample, cols )
		for occ_role in [ "Bookkeeper", "Overseer", "Carpenter", "Manager" ]:
			subsample = filter_sample( sample, "occ", occ_role )# todo: filter the sample...
			x 	= get_list( subsample, cols )
			util.write_listdict_to_file( "%s.SALARY.[%s].tsv" % ( filepath, occ_role ), x )

		util.write_dict_to_file( "%s.ROLE.tsv" % ( filepath ), ROLE, "ROLE" )
		util.write_listdict_to_file( "%s.SALARY.tsv" % ( filepath ), SALARY )

	if MF_key == "FATHER-OCC":
		# ... do something ...
		return
