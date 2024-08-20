from .rdb import *
import pandas as pd


HLD_counties = [
	"ARL",
	"CAI",
	"INV",
	"NAI",
	#"OKI",
	"ROC",
	"SUT",
	#"SHI"
]

LLD_counties = [
	"ABD",
	#"ARL",
	"AYR",
	"BAN",
	"BEW",
	"BUT",
	#"CAI",
	"CLK",
	"DFS",
	"DNB",
	"MLN",
	"MOR",
	"FIF",
	"ANS",
	"ELN",
	#"INV",
	"KCD",
	"KRS",
	"KKD",
	"LKS",
	"WLN",
	#"NAI",
	#"OKI",
	"PEE",
	"PER",
	"RFW",
	#"ROC",
	"ROX",
	"SEL",
	"STI",
	#"SUT",
	"WIG",
	#"SHI"
]

NI_counties = [
	"OKI",
	"SHI"
]

SCO_counties = [
	"ABD",
	"ARL",
	"AYR",
	"BAN",
	"BEW",
	"BUT",
	"CAI",
	"CLK",
	"DFS",
	"DNB",
	"MLN",
	"MOR",
	"FIF",
	"ANS",
	"ELN",
	"INV",
	"KCD",
	"KRS",
	"KKD",
	"LKS",
	"WLN",
	"NAI",
	"OKI",
	"PEE",
	"PER",
	"RFW",
	"ROC",
	"ROX",
	"SEL",
	"STI",
	"SUT",
	"WIG",
	"SHI"
]

ENG_counties = [
	"BDF",
	"BRK",
	"BKM",
	"CAM",
	"CHS",
	"CON",
	"CUL",
	"DBY",
	"DEV",
	"DOR",
	"DUR",
	"ESS",
	"GLS",
	"HAM",
	"HEF",
	"HRT",
	"HUN",
	"KEN",
	"LAN",
	"LEI",
	"LIN",
	"LND",
	"NTH",
	"NFK",
	"NTT",
	"NBL",
	"OXF",
	"RUT",
	"SAL",
	"SOM",
	"STS",
	"SFK",
	"SRY",
	"SSX",
	"WAR",
	"WIL",
	"WES",
	"WOR",
	"YKS"
]

WAL_counties = [
	"AGY",
	"BRE",
	"CAE",
	"CGN",
	"CMN",
	"DEN",
	"FLN",
	"GLA",
	"MER",
	"MGY",
	"MON",
	"PEM",
	"RAD"
]

LLD_NE_counties = [ # Grampian
	"ABD",
	"BAN",
	"MOR",
	"KCD",
]

LLD_TS_counties = [ # Tayside
	"ANS",
	"PER",
	"KRS",
]

LLD_FE_counties = [ # Forth Estuary
	"CLK",
	"MLN",
	"FIF",
	"WLN",
	"ELN",
	"STI",
]

LLD_NI_counties = [ # Northern Isles
	"OKI",
	"SHI"
]

LLD_CE_counties = [ # Clyde Estuary
	"DNB",
	"RFW",
	"LKS",
]

LLD_SS_counties = [ # Southern Scotland (incl Ayrshire and Buteshire)
	"DFS",
	"KKD",
	"WIG",
	"AYR", #IW
	"BUT",
	"BEW",
	"PEE",
	"ROX",
	"SEL",
]

GBR_counties = SCO_counties + ENG_counties + WAL_counties

region_groups = {
"SCO, HLD_counties": [
	"CAI",
	"ARL",
	"INV",
	"ROC",
	"NAI",
	"SUT"
],

"SCO, HLD": [
	"HLD"
],

"SCO, HLD_rSCO": [
	"HLD",
	"rSCO"
],

#"SCO, HLD_rSCO_ENW": [
#	"HLD",
#	"rSCO",
#	"ENG_WAL"
#],

#"SCO, CIRNS_rSCOA_rGBRA": [
#	"CIRNS",
#	"rSCOA",
#	"rGBRA"
#],

"SCO_REGIONS_3": [
	"HLD",
	"LLD_GT",
	"LLD_MS",
],

"SCO_REGIONS_7": [
	"LLD_NI",
	"HLD",
	"LLD_NE",
	"LLD_TS",
	"LLD_CE",
	"LLD_FE",
	"LLD_SS",
],

"GBR_REGIONS": [
	"HLD",
	"LLD_GT",
	"LLD_MS",
	"ENG_NE",
	"ENG_NW",
	"ENG_YH",
	"ENG_EM",
	"ENG_WM",
	"ENG_EE",
	"ENG_SE",
	"ENG_SW",
	"WAL",
],

# nations...
#"GBR_NATIONS": [
#	"SCO",
#	"WAL",
#	"ENG",
#]
}

from collections import OrderedDict

regions = OrderedDict( [
( "CAI", ["CAI"] ),
( "ARL", ["ARL"] ),
( "INV", ["INV"] ),
( "ROC", ["ROC"] ),
( "NAI", ["NAI"] ),
( "SUT", ["SUT"] ),

( "HLD", HLD_counties ),

( "CIRNS", [
	"CAI",
	"INV",
	"ROC",
	"NAI",
	"SUT",
] ),

( "LLD", LLD_counties ),
( "SCO", SCO_counties ),
( "rSCO", LLD_counties + NI_counties ),
( "rSCOA", LLD_counties + NI_counties + ["ARL"] ),
( "rGBR", LLD_counties + NI_counties + ENG_counties + WAL_counties ),
( "rGBRA", LLD_counties + NI_counties + ENG_counties + WAL_counties + ["ARL"] ),

( "ENG_WAL", ENG_counties + WAL_counties ),
( "ENG", ENG_counties ),
( "WAL", WAL_counties ),
( "ENG_NE", [ "NBL", "DUR" ] ), #Northumberland, Durham
( "ENG_NW", [ "CUL", "WES", "LAN", "CHS" ] ), #Cumberland, Westmoreland, Lancashire, Cheshire ],
( "ENG_YH", [ "YKS" ] ), #Yorkshire],
( "ENG_EM", [ "NTH", "LEI", "DBY", "NTT", "LIN", "RUT" ] ), #Northants, Leicester, Derby, Notts, Lincoln, Rutland ],
( "ENG_WM", [ "HEF", "WOR", "WAR", "SAL", "STS" ] ), #Hereford, Worcester, Warick, Shropshire, Stafford ],
( "ENG_EE", [ "ESS", "HRT", "BDF", "HUN", "CAM", "NFK", "SFK" ] ), #Essex, Hertford, Bedrord, Hunts, Cambridge, Norfolk, Suffolk],
( "ENG_SE", [ "KEN", "SSX", "HAM", "BRK", "OXF", "BKM", "LND" ] ), #Kent, Sussex, Hampshire, Berks, Oxford, Bucks, Middx/London ],
( "ENG_SW", [ "CON", "DEV", "SOM", "DOR", "WIL", "GLS" ] ), #Cornwall, Devon, Somerset, Dorset, Wiltshire, Gloucester ],

( "LLD_GT", LLD_NE_counties + LLD_TS_counties ),
( "LLD_MS", LLD_SS_counties + LLD_FE_counties + LLD_CE_counties ),

( "LLD_NI", LLD_NI_counties ),
( "LLD_NE", LLD_NE_counties ),
( "LLD_TS", LLD_TS_counties ),
( "LLD_CE", LLD_CE_counties ),
( "LLD_FE", LLD_FE_counties ),
( "LLD_SS", LLD_SS_counties ),
])

ALL_counties = [
( "BDF", "Bedfordshire" ),
( "BRK", "Berkshire" ),
( "BKM", "Buckinghamshire" ),
( "CAM", "Cambridgeshire" ),
( "CHS", "Cheshire" ),
( "CON", "Cornwall" ),
( "CUL", "Cumberland" ),
( "DBY", "Derbyshire" ),
( "DEV", "Devon" ),
( "DOR", "Dorset" ),
( "DUR", "County Durham" ),
( "ESS", "Essex" ),
( "GLS", "Gloucestershire" ),
( "HAM", "Hampshire" ),
( "HEF", "Herefordshire" ),
( "HRT", "Hertfordshire" ),
( "HUN", "Huntingdonshire" ),
( "KEN", "Kent" ),
( "LAN", "Lancashire" ),
( "LEI", "Leicestershire" ),
( "LIN", "Lincolnshire" ),
( "LND", "London" ),
( "NTH", "Northamptonshire" ),
( "NFK", "Norfolk" ),
( "NTT", "Nottinghamshire" ),
( "NBL", "Northumberland" ),
( "OXF", "Oxfordshire" ),
( "RUT", "Rutland" ),
( "SAL", "Shropshire" ),
( "SOM", "Somerset" ),
( "STS", "Staffordshire" ),
( "SFK", "Suffolk" ),
( "SRY", "Surrey" ),
( "SSX", "Sussex" ),
( "WAR", "Warwickshire" ),
( "WIL", "Wiltshire" ),
( "WES", "Westmorland" ),
( "WOR", "Worcestershire" ),
( "YKS", "Yorkshire" ),
#
( "AGY", "Anglesey" ),
( "BRE", "Brecknockshire" ),
( "CAE", "Caernarfonshire" ),
( "CGN", "Cardiganshire" ),
( "CMN", "Carmarthenshire" ),
( "DEN", "Denbighshire" ),
( "FLN", "Flintshire" ),
( "GLA", "Glamorgan" ),
( "MER", "Merioneth" ),
( "MGY", "Montgomeryshire" ),
( "MON", "Monmouthshire" ),
( "PEM", "Pembrokeshire" ),
( "RAD", "Radnorshire" ),
#
( "ABD", "Aberdeenshire" ),
( "ARL", "Argyll" ),
( "AYR", "Ayrshire" ),
( "BAN", "Banffshire" ),
( "BEW", "Berwickshire" ),
( "BUT", "Buteshire" ),
( "CAI", "Caithness" ),
( "CLK", "Clackmannanshire" ),
( "DFS", "Dumfriesshire" ),
( "DNB", "Dunbartonshire" ),
( "MLN", "Edinburghshire (Midlothian)" ),
( "MOR", "Elginshire (Morayshire)" ),
( "FIF", "Fife" ),
( "ANS", "Forfarshire (Angus)" ),
( "ELN", "Haddingtonshire (East Lothian)" ),
( "INV", "Inverness-shire" ),
( "KCD", "Kincardineshire" ),
( "KRS", "Kinross-shire" ),
( "KKD", "Kirkcudbrightshire" ),
( "LKS", "Lanarkshire" ),
( "WLN", "Linlithgowshire (West Lothian)" ),
( "NAI", "Nairnshire" ),
( "OKI", "Orkney" ),
( "PEE", "Peeblesshire" ),
( "PER", "Perthshire" ),
( "RFW", "Renfrewshire" ),
( "ROC", "Ross-shire (Ross and Cromarty)" ),
( "ROX", "Roxburghshire" ),
( "SEL", "Selkirkshire" ),
( "STI", "Stirlingshire" ),
( "SUT", "Sutherland" ),
( "WIG", "Wigtownshire" ),
( "SHI", "Zetland (Shetland)" )
]



def is_dat_file(filename):
	return "02_ODS" in root and "[+]" in filename and ".tsv" in filename and filename.startswith( "^" ) and not "SURNAME" in filename


def strip_surname_from_pers_id(pers_id):

	surname = str(pers_id).replace("--","")
	if surname.startswith("+"):
		return ""
	if "," in surname:
		surname = surname.split( "," )[0]
	if "(" in surname:
		surname = surname.split( "(" )[0]
	return surname


def convert_county_list_to_sql( listobj ):
	sql = ""
	first = True
	for county in listobj:
		if not first:
			sql += "+"
		sql += "BSN.%s_total" % county
		first = False
	return sql


def get_surname_regionalism(surname):
	HLD_total_sql = convert_county_list_to_sql( HLD_counties )
	SCO_total_sql = convert_county_list_to_sql( SCO_counties )
	GBR_total_sql = convert_county_list_to_sql( GBR_counties )

	sql = """
	SELECT
		ROUND((( {HLD_total} )/CAST(BSN.GBR_total AS FLOAT))*100,1) AS VAL_HLD,
		ROUND((( {SCO_total} )/CAST(BSN.GBR_total AS FLOAT))*100,1) AS VAL_SCO,
		CASE WHEN BSN.surname IS NOT NULL THEN 1 else 0 END AS IS_GBR_SURNAME
	FROM
		surname_details AS BSN
	WHERE
		BSN.surname = "{surname}" AND
		BSN.src_filepath LIKE '%BSN, %'""".format(
			HLD_total=HLD_total_sql,
			SCO_total=SCO_total_sql,
			GBR_total=GBR_total_sql,
			surname=surname )

	results = rdb.get_DAT_from_SQL( sql )

	VAL_HLD 		= 0
	VAL_SCO 		= 0
	IS_GBR_SURNAME 	= 0

	if len( results ) > 0:
		result 			= results[0]
		VAL_HLD 		= result["VAL_HLD"]
		VAL_SCO 		= result["VAL_SCO"]
		IS_GBR_SURNAME 	= result["IS_GBR_SURNAME"]

	return( VAL_HLD, VAL_SCO, IS_GBR_SURNAME )


#panda functions

def add_surname_regionalism(surname):

	# sanitisation... ??
	if surname.startswith("MACK"):
		surname = surname.replace("MACK","M'",1)
	if surname.startswith("MAC"):
		surname = surname.replace("MAC","M'",1)
	if surname.startswith("MC"):
		surname = surname.replace("MC","M'",1)

	VAL_HLD, VAL_SCO, IS_GBR_SURNAME = get_surname_regionalism(surname.upper())
	return pd.Series([VAL_HLD, VAL_SCO, IS_GBR_SURNAME])
