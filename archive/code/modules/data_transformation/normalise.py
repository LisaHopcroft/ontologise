# -*- coding: utf-8 -*-
from collections import OrderedDict

# previously 'preprocessing.py'


colony_mapping = {
	"Jamaica": 		"WIN, JAM",
	"Barbadoes": 	"WIN, BAR",
	"Barbados": 	"WIN, BAR",
	"Grenada": 		"WIN, GRE",
	"Dominica": 	"WIN, DOM",
	"Nevis": 		"WIN, K&N, NEV",
	"Virgin Islands": "WIN, VIR",
	"St Lucia": 	"WIN, LUC",
	"Berbice": 		"WIN, GUI, BER",
	"Tobago": 		"WIN, TOB",
	"St Vincent": 	"WIN, VIN",
	"Trinidad": 	"WIN, TRI",
	"St Christopher":	"WIN, K&N, KIT",
	"Antigua":		"WIN, ANT",

	"British Guiana":	"WIN, GUI",
	"St Kitts":		"WIN, K&N, KIT",
	"Montserrat":	"WIN, MON",
	"Anguilla":		"WIN, ANG",
}

parish_mapping = OrderedDict([
	("Roseau", 			"ROS"),
	("Westmoreland", 	"WES"),
	("Hanover", 		"HAN"),
	("Trelawney", 		"TRE"),
	("St James",		"JAM"),
	("St David", 		"DAV"),
	("St Elizabeth", 	"ELI"),
	("Elizabeth", 		"ELI"),
	("St George", 		"GEO"),
	("Portland", 		"POR"),
	("St Thomas in the East", "TIE"),
	("St Thomas-in-the-East", "TIE"),
	("St Thomas in the Vale", "TIV"),
	("St Thomas-in-the-Vale", "TIV"),
	("St Andrew", 		"AND"),
	("Port Royal", 		"ROY"),
	("Kingston",		"KIN"),
	("Manchester",		"MAN"),
	("Clarendon", 		"CLA"),
	("Vere", 			"VER"),
	("St Ann", 			"ANN"),
	("St Mary", 		"MAR"),
	("St John", 		"JOH"),
	("St Dorothy", 		"DOR"),
	("St Catherine",	"CAT"),

	# VIR
	("Tortola",			"TOR"),

	# Lucia
	("Soufriere",		"SOU"),
	("Vieux Fort",		"VIE"),

	# Grenada
	("Carriacou",		"CAR"),
	("St Mark",			"MRK"),
	("St Patrick",		"PAT"),

	# Guiana
	("Demerara",		"DEM"),
	("Berbice",			"BER"),
	("Essequebo",		"ESS"),

	# Barbados
	("St Philip",		"PHI"),
	("St Peter",		"PET"),
	("St Thomas",		"THO"),
	("St Michael",		"MIC"),
	("Christ Church",	"CHR"),
	("St Joseph",		"JSP"),
	("St Lucy",			"LUC"),

	# Trinidad
	("South Naparima",	"SNA"),
	("Maracas",			"MAR"),
	("Carenage",		"CAR"),

	# VIN
	("Mustique",		"MUS"),
])


find_replace = [
	( "M'KENSEY", "M'KENZIE" ),
	( "CAMBEL", "CAMPBELL" ),
	( "M'LENAN", "M'LENNAN" ),
	( "M'LELAN", "M'LELLAN" ),
	( "M'NEAL", "M'NEILL" ),
	( "M'NIEL", "M'NEILL" ),
	( "ARCHIBAULD", "ARCHIBALD" ),
	( "ARCHIBOULD", "ARCHIBALD" ),
	( "M'KDONALD", "M'DONALD" ),
	( "M'KQUEEN", "M'QUEEN" ),
	( "M'FARLIN", "M'FARLANE" ),
	( "M'FARLEN", "M'FARLANE" ),
	( "M'FAREAN", "M'FARLANE" ),
	( "M'KENLAY", "M'KINLAY" ),
	( "M'KENLEY", "M'KINLAY" ),
	( "M'KEWAN", "M'EWAN" ),
	( "M'LACHLANE", "M'LACHLAN" ),
	( "M'MILLEN", "M'MILLAN" ),
	( "M'NEAL", "M'NEILL" ),
	( "M'PHUSON", "M'PHERSON" ),
	( "URQUBART", "URQUHART" ),
	( "WINTERBOLLOM", "WINTERBOTTOM" ),
	( "CAMERSON", "CAMERON" ),
	( "CHISHOLME", "CHISHOLM" ),
	( "CHRISHOLM", "CHISHOLM" ),
	( "CLARKE", "CLARK" ),
	( "CLEALAND", "CLELAND" ),
	( "COLHOUN", "COLQUHOUN" ),
	( "CURICKSHANK", "CRUICKSHANK" ),
	( "M'CULLOCK", "M'CULLOCH" ),
	( "M'CULLOH", "M'CULLOCH" ),
	( "M'CRAE", "M'RAE" ),
	( "M'CLELLAN", "M'LELLAN" ),
	( "M'CLARTY", "M'LARTY" ),
	( "M'DERMOT", "M'DERMOTT" ),
	( "M'DERMEIT", "M'DERMOTT" ),
	( "M'DERMRIT", "M'DERMOTT" ),
	( "M'FARGUHAR", "M'FARQUHAR" ),
	( "M'FARGUHAN", "M'FARQUHAR" ),
	( "M'GILLEWRAY", "M'GILLEVRAY" ),
	( "M'KINZIE", "M'KENZIE" ),
	( "M'KGLASHAN", "M'GLASHAN" ),
	( "M'MILLIEN", "M'MILLAN" ),
	( "M'NAMARRA", "M'NAMARA" ),
	( "M'NICOL", "M'NICOLL" ),
	( "M'REA", "M'RAE" ),
	( "M'NEMARA", "M'NAMARA" ),
	( "M'CLANAGAN", "M'LANAGAN" ),
	( "M'DOWAL", "M'DOWALL" ),
	( "M'LARIN", "M'LAREN" ),
	( "LEVERMORE", "LIVERMORE" ),
	( "FARGUHARSON", "FARQUHARSON" ),
	( "CROOKSHANKS", "CRUICKSHANKS" ),
	( "M'LAUGHLIN", "M'LACHLAN" ),
	( "M'LAUCHLIN", "M'LACHLAN" ),
	( "M'LAUGHLAN", "M'LACHLAN" ),
	( "M'LAUGHLEN", "M'LACHLAN" ),
	( "M'LAUGLIN", "M'LACHLAN" ),
	( "M'LAUD", "M'LEOD" ),
	( "M'LEAD", "M'LEOD" )
]


def normalise_surnames( surname ):
	surname 	= surname.upper().replace("[']S","").replace("['S]","").replace("'S","")

	#if surname.startswith( "MACK" ):
	#	surname = "M'" + surname[4:]
	if surname.startswith( "MAC" ) and surname != "MACER" and surname != "MACK":
		surname = "M'" + surname[3:]
	if surname.startswith( "MC" ):
		surname = "M'" + surname[2:]

	surname		= surname.replace( "[", "" ).replace( "]", "" ).strip()

	for f, r in find_replace:
		if surname == f: surname = r

	return surname


def place_txt_to_place_id( txt ):
	place_id = ""

	for k, v in colony_mapping.items():
		if k in txt:
			place_id = v
			break

	for k, v in parish_mapping.items():
		if k in txt:
			place_id = place_id + ", " + v
			break

	if "(" in txt:
		estate_txt = txt.split("(")[1].split(")")[0]
		place_id += ", %s" % estate_txt
	else:
		place_id += ", ."

	return place_id


def pers_txt_to_pers_id( txt ):

	if txt == "[no name]":
		return "."

	txt = txt.strip()
	if " of " in txt:
		txt = txt.split( " of " )[0]
	if " or " in txt:
		txt = txt.split( " or " )[0]
	if " (née " in txt:
		txt = txt.split( " (née " )[0]
	if " formerly " in txt:
		txt = txt.split( " formerly " )[0]

	suffixes = [
		" esquire",
		" esqr",
		" esqr.",
		" esq",
		" esq.",
		" junior",
		" jun",
		" jun.",
		" jnr",
		" jnr.",
		" junr",
		" junr.",
		" widow",
		" (sic)",
		" spinster",
		" baronet",
	]

	for suffix in suffixes:
		if txt.upper().endswith( suffix.upper() ): txt = txt[:-len(suffix)]
	for suffix in suffixes: # run again... just in case there are two suffixes...
		if txt.upper().endswith( suffix.upper() ): txt = txt[:-len(suffix)]

	if " " in txt.strip():
		surname = txt.rsplit( " ", 1 )[1]
		forename = txt.rsplit( " ", 1 )[0]
	else:
		surname = txt
		forename = "."

	surname = normalise_surnames( surname )

	txt = surname.upper().strip() + ", " + forename.strip()

	return txt
