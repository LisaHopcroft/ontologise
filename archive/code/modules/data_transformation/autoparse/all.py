#!/usr/bin/python
import ontologize.modules.data_transformation.all as prep

import sys
sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.confdat as confdat
import ontologize.modules.data_transformation.autoparse.algorithms as algorithms


surname_vals = [
	"Van",
	"van",
	"de",
	"De",
	"den",
	"Le",
]

prefixes = [
	"Mr. ",
	"Hon. ",
	"Honb. ",
	"His Honor ",
	"Honorable ",
	"Honourable ",
	"Doctor ",
	"Dr. ",
	"Rev. ",
	"Revd. ",
	"The ",
	"the ",
]

female_prefixes = [
	"Widow ",
	"widow ",
	"Mrs. ",
	"Miss. ",
	"Mrs ",
	"Miss ",
]

strip_vals = [
	" free ",
	" Free ",
	" mulatto ",
	" negro ",
	" Negro ",
	" boy ",
	" coloured ",
	" Coloured ",
	" Man ",
	" q.q.",
	" Jr."
]

strip_vals_female = [
	" Woman ",
	" woman ",
	" Girl ",
	" girl ",
]


def get_is_child_from_txt( pers_txt ):
	return any( x in pers_txt.lower() for x in [ " children ", " child ", " servant ", " son ", " daughter " ] )


def get_race_from_txt( pers_txt ):
	race		= "."

	if( "coloured" in pers_txt.lower() ):
		race 	= "Coloured"
	elif( "mulatto" in pers_txt.lower() ):
		race 	= "Mulatto"
	elif( any( x in pers_txt.lower() for x in [ " negro", " black man", " black boy", " black girl", " black woman", " the property", " slave", " slaves" ] ) ):
		race 	= "Black"

	return race


def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)


def get_pers_id_from_txt( pers_txt ):
	surname 	= "."
	forenames	= "."
	is_female	= False


	if pers_txt.strip().endswith(","):
		pers_txt = rreplace( pers_txt, ",", "", 1 )


	if " of " in pers_txt:
		pers_txt		= pers_txt.split( " of ", 1 )[0]


	# run it a few times, because there might be a few prefixes...

	for i in range(0,3):
		for val in prefixes:
			if pers_txt.startswith( val ):
				pers_txt 	= pers_txt[ len(val): ]
		for val in female_prefixes:
			if pers_txt.startswith( val ):
				pers_txt 	= pers_txt[ len(val): ]
				is_female = True

	pers_txt = " " + pers_txt

	for val in strip_vals:
		pers_txt = pers_txt.replace( val, " " )
	for val in strip_vals_female:
		if val in pers_txt:
			pers_txt = pers_txt.replace( val, " " )
			is_female = True

	pers_txt = pers_txt.strip()


	if "(" in pers_txt:
		pers 	= pers_txt.split( "(", 1 )[0].strip()
	if "[" in pers_txt:
		pers_txt 	= pers_txt.split( "[", 1 )[0].strip()



	if "^" in pers_txt:
		surname 	= pers_txt.split("^")[0].strip()
		forenames 	= pers_txt.split("^")[1].strip()
	elif pers_txt.count( "," ) == 1:
		surname 	= pers_txt.split(",")[0].strip()
		forenames 	= pers_txt.split(",")[1].strip()
	elif pers_txt.count( " " ) == 0:
		surname		= pers_txt.upper().strip()
	elif pers_txt.count( " " ) == 1:
		surname 	= pers_txt.split( " ", 1 )[1].strip()
		forenames 	= pers_txt.split( " ", 1 )[0].strip()
	elif pers_txt.count( " " ) > 1:
		surname 		= pers_txt.rsplit( " ", 1 )[1].strip()
		forenames		= ""
		els				= pers_txt.split( " " )[:-1]
		for el in els:
			if( any( x in el for x in surname_vals ) ):
				surname 	= el + " " + surname
			elif el.endswith("."):
				forenames 	+= el + " "
			else:
				#print "?: " + el
				forenames 	+= el + " "


	if is_female:
		surname = "--%s" % surname


	if surname.lower().startswith("mc"):
		surname = "M'" + surname[2:]
	if surname.lower().startswith("mac") and len(surname) != 4:
		surname = "M'" + surname[3:]


	return "%s, %s" % ( surname.upper(), forenames )


def search_keyvals( keylist, searchtxt ):
	resultlist = []
	for key, val in keylist.items():
		for v in val:
			if v in searchtxt:
				return key.lstrip()
	return "."


def strip_keyvals( keylist, searchtxt ):
	resultlist = []
	for key, val in keylist.items():
		for v in val:
			if v in searchtxt:
				return searchtxt.replace( v, " " )
	return searchtxt
