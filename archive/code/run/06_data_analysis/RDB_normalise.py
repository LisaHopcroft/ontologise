#!/usr/bin/python
import sys
import lib.rdb as rdb 
import sqlite3
import os
import glob
import itertools
import pexpect
from collections import OrderedDict


DB_path = academia_root + "_rdb/02_RDB/db.sqlite"
db = sqlite3.connect( DB_path )
cursor = db.cursor()


# ---------------------------------------------------------------------- #

# Create cached values of surnames...
sql = """
UPDATE
	surname_details
SET
	_HLD_index = ROUND((( ARL_total+CAI_total+INV_total+NAI_total+ROC_total+SUT_total )/CAST(GBR_total AS FLOAT))*100),
	_SCO_index = ROUND((( ABD_total+ARL_total+AYR_total+BAN_total+BEW_total+BUT_total+CAI_total+CLK_total+DFS_total+DNB_total+MLN_total+MOR_total+FIF_total+ANS_total+ELN_total+INV_total+KCD_total+KRS_total+KKD_total+LKS_total+WLN_total+NAI_total+OKI_total+PEE_total+PER_total+RFW_total+ROC_total+ROX_total+SEL_total+STI_total+SUT_total+WIG_total+SHI_total )/CAST(GBR_total AS FLOAT))*100)"""
cursor.execute( sql )
db.commit()

# ---------------------------------------------------------------------- #


# populate a cached zone field for ease of use in sql queries...

'''
sql = "SELECT * from peopla WHERE place_zone = ''"

ids = []
for row in cursor.execute( sql ):
	id_val 		= row[24]
	place_id 	= row[6]
	zone_txt 	= get_place_zone_text(place_id)
	if zone_txt:
		print zone_txt
		cursor2 = db.cursor()
		update_sql = """
		UPDATE
			peopla
		SET
			place_zone = "{zone_txt}"
		WHERE id = {id_val}""".format(id_val=id_val, zone_txt=zone_txt)
		ids.append( str(id_val) )

		cursor2.execute( update_sql )
		db.commit()

db.close()
'''


# THIS ATTEMPTED EFFICIENCY IMPROVEMENT WAS ACTUALLY MUCH SLOWER

'''
update_sql = """
UPDATE
	peopla
SET
	place_zone = CASE id"""

sql = "SELECT * from peopla WHERE place_zone = ''"

ids = []
for row in cursor.execute( sql ):
	id_val = row[24]
	place_id = row[6]
	zone_txt = get_place_zone_text(place_id)
	if zone_txt:
		cursor2 = db.cursor()
		update_sql += """
		WHEN {id_val} THEN "{zone_txt}" """.format(id_val=id_val, zone_txt=zone_txt)
		ids.append( str(id_val) )

update_sql += "END WHERE id IN ({ids})".format( ids=", ".join( ids ))

print update_sql
cursor.execute( update_sql )
db.commit()
'''



# ------------------------------------------------------------------ #

'''
sql = """
DELETE FROM ADD_population WHERE 1;"""
cursor.execute( sql )
db.commit()

# All surnames...
sql = """
INSERT INTO
	ADD_population( place_id, y1, surname, popln, src_type, src_ref )
SELECT
	place_id,
	y1,
	"[all]" AS surname,
	count(*) AS popln,
	src_type,
	src_ref
FROM
	peopla
WHERE
	src_type = "UK-CENSUS"
GROUP BY
	place_id, y1, src_type, src_ref;"""
cursor.execute( sql )
db.commit()

# Per surname...
sql = """
INSERT INTO
	ADD_population( place_id, y1, surname, popln, src_type, src_ref )
SELECT
	place_id,
	y1,
	replace( SUBSTR(pers_id,0,INSTR(pers_id,",")), "--", "" ) AS surname,
	count(*) AS popln,
	src_type,
	src_ref
FROM
	peopla
WHERE
	src_type = "UK-CENSUS"
GROUP BY
	surname, y1, place_id, src_type;"""
cursor.execute( sql )
db.commit()

# ------------------------------------------------------------------ #

places = {}
unique_zones = {}

sql = """
SELECT
	*
FROM
	ADD_population"""

# get all the places

for row in cursor.execute( sql ):
	places[row[0]] = 0


# consolidate in to zones

def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False

for place in places.keys():
	els = place.rsplit( ", " )
	zone = ""
	for el, has_more in lookahead( els ):
		if has_more:
			zone += el
			unique_zones[ zone ] = 0
			zone += ", "


# create population record for each zone

for zone in unique_zones.keys():
	print zone

	# All surnames
	sql = """
INSERT INTO
	ADD_population( place_id, y1, surname, popln, src_type, src_ref )
SELECT
	"{zone}" AS place_id,
	y1,
	"[all]" AS surname,
	SUM(popln) AS popln,
	src_type,
	src_ref
FROM (
	SELECT
		"{zone}" AS place_id,
		y1,
		surname AS surname_appearance,
		"[all]" AS surname,
		SUM(popln) AS popln,
		src_type,
		src_ref
	FROM
		ADD_population
	WHERE
		place_id LIKE "{zone}, %" AND surname_appearance != "[all]"
	GROUP BY
		y1, src_type, src_ref );""".format( zone=zone )
	cursor.execute( sql )
	db.commit()
	# Adding extra layer to this query to be able to check the surname value, but not return it...

	# Per surname
	sql = """
INSERT INTO
	ADD_population( place_id, y1, surname, popln, src_type, src_ref )
SELECT
	"{zone}" AS place_id,
	y1,
	surname,
	SUM(popln) AS popln,
	src_type,
	src_ref
FROM
	ADD_population
WHERE
	place_id LIKE "{zone}, %" AND surname != "[all]"
GROUP BY
	surname, y1, src_type, src_ref;""".format( zone=zone )
	cursor.execute( sql )
	db.commit()
'''
