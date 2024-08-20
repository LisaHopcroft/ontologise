#!/usr/bin/python

import sqlite3
import os, sys
import glob
import itertools
import pexpect
from collections import OrderedDict

sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
from ontologize.modules.data_transformation.mkd import *
import ontologize.modules.util.confdat as confdat
import ontologize.modules.util.performance as performance


DB_dir = confdat.academia_root + "_rdb"
DB_path = DB_dir + "/02_RDB/db.sqlite"
db = sqlite3.connect( DB_path )
db.text_factory = str



# ------------------------------------------------------------------------------------------ #
# Relational database...
# ------------------------------------------------------------------------------------------ #

letterwriter_sql = """
SELECT DISTINCT pers_id, colony FROM letterwriters;"""

BDM_sql = """
SELECT DISTINCT pers_id, SUBSTR(place_id,1,8) AS colony
FROM peopla
WHERE action='DIED'
AND src_type LIKE 'BDM-DEATH%'
AND place_id LIKE 'WIN%'
ORDER BY pers_id"""

Tttr_sql = """
SELECT DISTINCT pers_id, SUBSTR(place_id,1,8) AS colony
FROM peopla
WHERE action='WILL_SGD'
AND place_id LIKE 'WIN%'
ORDER BY pers_id"""

SAH_sql = """
SELECT DISTINCT pers_id, SUBSTR(place_id,1,8) AS colony
FROM peopla
WHERE src_filepath LIKE '%, S&H, %'
ORDER BY pers_id"""


def get_letterwriter_SAMPLE():
	cursor = db.cursor()
	sql = letterwriter_sql
	return get_RDB_rows_as_dict( sql )


def get_lettersource_SAMPLE():
	cursor = db.cursor()
	sql = """
SELECT DISTINCT SRC_letter.*
FROM peopla, SRC_letter
WHERE peopla.src_filepath = SRC_letter.src_filepath
AND src_type = 'LETTER'"""
	return get_RDB_rows_as_dict( sql )


def get_BDM_SAMPLE():
	cursor 	= db.cursor()
	sql 	= BDM_sql
	return get_RDB_rows_as_dict( sql )


def get_pers_SAMPLE( sql ):
	cursor 	= db.cursor()
	return get_RDB_rows_as_dict( sql )


def sql_male_corresp():
	return "NOT attr_fm LIKE '--%'"


def sql_WIN_src():
	return "src_at LIKE 'WIN%'"


def sql_GBR_src():
	return "( src_at LIKE 'SCO%' OR src_at LIKE 'ENG%' OR src_at LIKE 'GBR%' )"


def sql_family_corresp():
	is_family_corresp = "( "
	i = 0
	for x in FAM_terms:
		if not i==0:
			is_family_corresp += " OR "
		is_family_corresp += "attr_rel LIKE '{x}%'".format( x=x )
		is_family_corresp += " OR attr_rel LIKE '%{x}'".format( x=x )
		is_family_corresp += " OR attr_rel LIKE '%{x}%'".format( x=x )
		i+=1
	return is_family_corresp + " )"


def esc_sql( sql ):
	return str( sql ).replace("'","''")


def RDB_is_ex_HLD( pers_id, filepath="", linenum="" ):
	cursor = db.cursor()
	sql = """
SELECT COUNT(*)
FROM peopla
WHERE pers_id='{pers_id}'
AND action IN ({ex_actions})""".format( pers_id=esc_sql( pers_id ),
										ex_actions=", ".join( "'" + esc_sql( x ) + "'" for x in PEOPLA_ex_actions ) )
	sql += """ AND ( """
	sql += """OR """.join( "place_id LIKE '{pattern}%'".format( pattern=esc_sql( pattern ) ) for pattern in HLD_vals )
	sql += """)"""
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )

	cursor.execute(sql)
	result = cursor.fetchone()[0]
	if result > 0:
		return True
	return False


def RDB_get_ex_at( pers_id, filepath="", linenum="" ):
	cursor = db.cursor()
	sql = """
SELECT place_id
FROM peopla
WHERE pers_id='{pers_id}'
AND action IN ({ex_actions})""".format( pers_id=esc_sql( pers_id ),
										ex_actions=", ".join( "'" + esc_sql( x ) + "'" for x in PEOPLA_ex_actions ) )
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )
	cursor.execute(sql)
	rows = cursor.fetchall()
	if not rows:
		return False
	for row in rows:
		return row[0] # return first 'hing


def RDB_get_PEOPLA( pers_id, action, filepath="", linenum="" ):
	cursor = db.cursor()
	sql = """
SELECT *
FROM peopla
WHERE pers_id='{pers_id}'
AND action='{action}'""".format( pers_id=esc_sql( pers_id ), action=action )
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )

	return get_RDB_rows_as_dict( sql )


def RDB_get_re_at( pers_id, filepath="", linenum="" ):
	cursor = db.cursor()
	sql = """
SELECT place_id
FROM peopla
WHERE pers_id='{pers_id}'
AND action IN ({re_actions})""".format( pers_id=esc_sql( pers_id ),
										re_actions=", ".join( "'" + esc_sql( x ) + "'" for x in PEOPLA_re_actions ) )
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )
	cursor.execute(sql)
	rows = cursor.fetchall()
	if not rows:
		return False
	for row in rows:
		return row[0]


def RDB_get_birth_year( pers_id, filepath="", linenum="" ):
	cursor = db.cursor()

	sql = """
SELECT y1
FROM peopla
WHERE action='BORN'"""
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )
	cursor.execute(sql)
	result = cursor.fetchone()

	if result:
		return result[0]

	return None


def RDB_get_fatherocc( pers_id, filepath="", linenum="" ):
	cursor = db.cursor()

	# If FATHER-OCC is specified get the linenum...
	sql = """
SELECT src_linenum
FROM peopla
WHERE pers_id='{pers_id}'
AND action = 'FATHER_OCC'""".format( pers_id=esc_sql(pers_id) )
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )
	cursor.execute(sql)
	result = cursor.fetchone()

	# Get FATHER-OCC...
	if result:
		line_num = result[0]

		sql = """
SELECT occ
FROM mf_occ
WHERE src_filepath='{filepath}'
AND src_linenum='{linenum}'""".format( filepath=esc_sql(filepath), linenum=esc_sql(linenum) )
		cursor.execute(sql)
		result = cursor.fetchone()

		if result:
			return result[0]

	return False


def RDB_get_memorial( pers_id, filepath="", linenum="" ):
	cursor = db.cursor()

	# If FATHER-OCC is specified get the linenum...
	sql = """
SELECT src_filepath, src_linenum
FROM peopla
WHERE pers_id='{pers_id}'
AND action = 'MEMORIAL'""".format( pers_id=esc_sql(pers_id) )
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )
	cursor.execute(sql)
	result = cursor.fetchone()

	# Get FATHER-OCC...
	if result:
		filepath 	= result[0]
		linenum 	= result[1]

		sql = """
SELECT safhs_id
FROM MF_memorial
WHERE src_filepath='{filepath}'
AND src_linenum='{linenum}'""".format( filepath=esc_sql(filepath), linenum=esc_sql(linenum) )
		cursor.execute(sql)
		result = cursor.fetchone()

		if result:
			return result[0]

	return False


def RDB_get_fatherat( pers_id, filepath="", linenum="" ):
	cursor = db.cursor()

	sql = """
SELECT place_id
FROM peopla
WHERE action LIKE 'FATHER_%'
AND pers_id='{pers_id}'""".format( pers_id=esc_sql(pers_id) )
	if filepath:
		sql += """ AND src_filepath='{filepath}'""".format( filepath=esc_sql(filepath) )
	if linenum:
		sql += """ AND src_linenum='{linenum}'""".format( linenum=esc_sql(linenum) )
	cursor.execute(sql)
	result = cursor.fetchone()

	if result:
		return result[0]

	return False


def get_RDB_rows_as_list( sql ):
	listobj = []
	cursor = db.cursor()
	cursor.execute( sql )
	for row in cursor.fetchall():
		listobj.append( row[0] )
	return listobj


def get_RDB_rows_as_dict( sql ):
	cursor = db.cursor()
	rows = cursor.execute( sql )
	desc = cursor.description
	column_names = [col[0] for col in desc]
	data = [dict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	return data


def get_DAT_from_SQL( sql ):
	cursor = db.cursor()
	rows = cursor.execute( sql )
	desc = cursor.description
	column_names = [col[0] for col in desc]
	data = [OrderedDict(itertools.izip(column_names, row)) for row in cursor.fetchall()]
	return data


def get_RDB_table_cols( tablename ):
	cursor = db.cursor()
	sql = "SELECT * FROM %s LIMIT 1" % tablename
	rows = cursor.execute( sql )
	return [col[0] for col in cursor.description]


def xstr(s):
    if s is None:
        return ''
    return str(s)


def sql_safe( text_str ):
	return text_str.replace("'", "''")
