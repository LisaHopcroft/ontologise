#!/usr/bin/python

academia_root = "/mnt/SSD3/Dropbox/workspace/2.research/"
DB_dir = "/mnt/SSD3/Dropbox/workspace/2.research/_rdb/"

NRS_path = academia_root + "01.Primary/01.Manuscripts/01.SCOTLAND/NRS, National Records of Scotland"

sample_root = academia_root + "3.Research/4.Samples/01_TSV/"

replace_GBR = [
	( "ENG_NE", "North East" ),
	( "ENG_NW", "North West" ),
	( "ENG_YH", "Yorkshire" ),
	( "ENG_EM", "East Midlands" ),
	( "ENG_WM", "West Midlands" ),
	( "ENG_EE", "East England" ),
	( "ENG_SE", "South East" ),
	( "ENG_SW", "South West" ),
	( "WAL", "Wales" ),
	( "CAIRNSBOS", "Highlands and Islands" ),
	( "CAIRNSB", "Highlands" ),
	( "LLD", "Lowlands" ),
	( "SCO", "Scotland" ),
	( "ENG", "England" ),
	( "NORTH_counties", "Northern Scotland" ),
	( "SOUTH_counties", "Southern Scotland" ),
	( "LLD_GT", "Grampian and Tayside" ),
	( "LLD_MS", "Central and Southern" ),
	( "LLD_NE", "Grampian" ),
	( "LLD_MD", "Mid Scotland" ),
	( "LLD_CS", "Central and Southern" ),
	( "LLD_SW", "South West" ),
	( "LLD_FS", "South East" ),
	( "LLD_TS", "Tayside" ),
	( "LLD_CE", "Clyde Estuary" ),
	( "LLD_FE", "Forth Estuary" ),
	( "LLD_SS", "Southern" ),
	( "LLD_NI", "Northern Isles" ),

	( "ARL_single", "Argyll" ),
	( "CAI_single", "Caithness" ),
	( "INV_single", "Inverness" ),
	( "NAI_single", "Nairn" ),
	( "SUT_single", "Sutherland" ),
	( "ROC_single", "Ross & Cromarty" ),

	( "HLD", 		"Highlands" ),
	( "rSCO", 		"Rest of Scotland" ),
	( "rGBR", 		"Rest of Britain" )
]

replace_colonies = [
	( "WIN, JAM", "Jamaica" ),
	( "WIN, DGO", "St Domingo" ),
	( "WIN, VIR", "Virgin Islands" ),
	( "WIN, ANG", "Anguilla" ),
	( "WIN, K&N", "St Kitts & Nevis" ),
	( "WIN, ANT", "Antigua" ),
	( "WIN, MON", "Montserrat" ),
	( "WIN, GUA", "Guadaloupe" ),
	( "WIN, DOM", "Dominica" ),
	( "WIN, MAR", "Martinique" ),
	( "WIN, LUC", "St Lucia" ),
	( "WIN, BAR", "Barbados" ),
	( "WIN, VIN", "St Vincent" ),
	( "WIN, GRE", "Grenada" ),
	( "WIN, TOB", "Tobago" ),
	( "WIN, TRI", "Trinidad" ),
	( "WIN, GUI", "Guiana" ),
	( "WIN, SUR", "Surinam" ),
]

replace_projects = [
	( "+IRA+RNI", 			"Inverness, Other" ),

	( "+FA", 				"Fortrose Academy" ),
	( "+TRA", 				"Tain Academy" ),
	( "+IRA", 				"Inverness Academy" ),
	( "+RNI", 				"Northern Infirmary" ),

	( "+Inv.D", 			"Inverness Dispensary" ),
	( "+Inv.IIISM", 		"Inverness Inst. Sacred Music" ),
	( "+Inv.ISSB", 			"Inverness Soc. Suppression of Begging" ),
	( "+Inv.NMR", 			"Inverness Meeting Rooms" ),
	( "+Inv.NC", 			"Inverness New Church" ),
	( "+Inv.Ness_Islands", 	"Ness Islands Improvements" ),
	( "+Nai.A", 			"Nairn Academy" ),
	( "+Suth.Coal", 		"Sutherland Coal Exploration" ),

	( "+Dumf.Schools", 		"Dumfries Schools" ),
	( "+Perth.Schools", 	"Perth Schools" ),
	( "+Banff.Infirmary", 	"Banff Infirmary" ),
	( "+Spey.Bridge", 		"Fochabers, Spey Bridge" ),

	( "+SSGS", 		"Scottish Society (\\textit{SSGS})" ),
	( "+GGSS", 		"Glasgow Auxilliary Society (\\textit{GASGS})" ), # should probably
	( "+SEPH", 		"Inverness Society (\\textit{ISEPH})" ), # merge with Gaelic Schools ? merge

	( "+Publ.HSOS.1828", 		"\\textit{H.S.O.S., 1828}" ),
	( "+Publ.ARMSTRONG.1825",	"\\textit{Armstrong, 1825}"  ),
	( "+Publ.TURNER.1813",		"\\textit{Turner, 1813}"  ),
	( "+Publ.M'KAY.1821",		"\\textit{Mackay, 1821}"  ),
	( "+Publ.M'COLL.1836",		"\\textit{McColl, 1836}"  ),
	( "+Publ.M'INTYRE.1790",	"\\textit{McIntyre, 1790}"  ),
	( "+Publ.M'KENZIE.1792",	"\\textit{McKenzie, 1792}"  ),
	( "+Publ.SHAW.1778",		"\\textit{Shaw, 1778}"  ),
	( "+Publ.SHAW.1780",		"\\textit{Shaw, 1780}"  ),
	( "+Publ.M'CALLUM&M'CALLUM.1816", "\\textit{McCallum and McCallum, 1816}"  ),
]

replace_parishes = [
	( "WIN, JAM, HAN", "Hanover" ),
	( "WIN, JAM, WES", "Westmoreland" ),
	( "WIN, JAM, JAM", "St James" ),
	( "WIN, JAM, ELI", "St Elizabeth" ),
	( "WIN, JAM, TRE", "Trelawney" ),
	( "WIN, JAM, MAN", "Manchester" ),
	( "WIN, JAM, ANN", "St Ann" ),
	( "WIN, JAM, CLA", "Clarendon" ),
	( "WIN, JAM, VER", "Vere" ),
	( "WIN, JAM, JOH", "St John" ),
	( "WIN, JAM, DOR", "St Dorothy" ),
	( "WIN, JAM, MAR", "St Mary" ),
	( "WIN, JAM, TIV", "St Thomas-in-the-Vale" ),
	( "WIN, JAM, CAT", "St Catherine" ),
	( "WIN, JAM, AND", "St Andrew" ),
	( "WIN, JAM, KIN", "Kingston" ),
	( "WIN, JAM, GEO", "St George" ),
	( "WIN, JAM, ROY", "Pt Royal" ),
	( "WIN, JAM, DAV", "St David" ),
	( "WIN, JAM, POR", "Portland" ),
	( "WIN, JAM, TIE", "St Thomas-in-the-East" ),

	( "WIN, BAR, LUC", "St Lucy" ),
	( "WIN, BAR, PET", "St Peter" ),
	( "WIN, BAR, JAM", "St James" ),
	( "WIN, BAR, MIC", "St Michael" ),
	( "WIN, BAR, CHR", "Christ Church" ),
	( "WIN, BAR, PHI", "St Philip" ),
	( "WIN, BAR, GEO", "St George" ),
	( "WIN, BAR, JOH", "St John" ),
	( "WIN, BAR, THO", "St Thomas" ),
	( "WIN, BAR, AND", "St Andrew" ),
	( "WIN, BAR, JOS", "St Joseph" ),
	( "WIN, BAR, JOH", "St John" ),

	( "WIN, ANT, JOH", "St John" ),
	( "WIN, ANT, GEO", "St George" ),
	( "WIN, ANT, PET", "St Peter" ),
	( "WIN, ANT, PHI", "St Philip" ),
	( "WIN, ANT, PAU", "St Paul" ),
	( "WIN, ANT, MAR", "St Mary" ),

	( "WIN, GUI, ESS", "Essequebo"),
	( "WIN, GUI, DEM", "Demerara"),
	( "WIN, GUI, BER", "Berbice"),

	( "WIN, GUI, TRI", "The Trinity"),
	( "WIN, GUI, JOH", "St John"),
	( "WIN, GUI, JAM", "St James"),
	( "WIN, GUI, PET", "St Peter"),
	( "WIN, GUI, LUK", "St Luke"),
	( "WIN, GUI, MRK", "St Mark"),
	( "WIN, GUI, MAT", "St Mathew"),
	( "WIN, GUI, PAU", "St Paul"),
	( "WIN, GUI, MAR", "St Mary"),
	( "WIN, GUI, MIC", "St Michael"),
	( "WIN, GUI, CAT", "St Catherine"),
	( "WIN, GUI, CLE", "St Clement"),
	( "WIN, GUI, PAT", "St Patrick"),
	( "WIN, GUI, SAV", "St Saviour"),

	( "WIN, K&N, NEV", "Nevis"),
	( "WIN, K&N, KIT", "St Kitts"),

	( "WIN, DOM, AND", "St Andrew"),
	( "WIN, DOM, DAV", "St David"),
	( "WIN, DOM, GEO", "St George"),
	( "WIN, DOM, JOH", "St John"),
	( "WIN, DOM, JOS", "St Joseph"),
	( "WIN, DOM, LUK", "St Luke"),
	( "WIN, DOM, PAT", "St Patrick"),
	( "WIN, DOM, PAU", "St Paul"),
	( "WIN, DOM, PET", "St Peter"),
	( "WIN, DOM, MAR", "St Mark"),

	( "WIN, TOB, AND", "St Andrew"),
	( "WIN, TOB, PAT", "St Patrick"),
	( "WIN, TOB, DAV", "St David"),
	( "WIN, TOB, GEO", "St George"),
	( "WIN, TOB, MAR", "St Mary"),
	( "WIN, TOB, PAU", "St Paul"),
	( "WIN, TOB, JOH", "St John"),

	( "WIN, LUC, VIE", "Vieux Fort"),

	( "WIN, GRE, DAV", "St David"),
	( "WIN, GRE, GEO", "St George"),
	( "WIN, GRE, AND", "St Andrew"),
	( "WIN, GRE, JOH", "St John"),
	( "WIN, GRE, MAR", "St Mark"),
	( "WIN, GRE, PAT", "St Patrick"),
	( "WIN, GRE, CAR", "Carriacou"),

	( "WIN, VIN, CHA", "Charlotte"),
	( "WIN, VIN, GEO", "St George"),
	( "WIN, VIN, AND", "St Andrew"),
	( "WIN, VIN, PAT", "St Patrick"),
	( "WIN, VIN, DAV", "St David"),

	( "WIN, TRI, CAR", "Caroni"),
	( "WIN, TRI, MAY", "Mayaro"),
	( "WIN, TRI, AND", "St Andrew"),
	( "WIN, TRI, PAT", "St Patrick"),
	( "WIN, TRI, DAV", "St David"),
]

outports = [ "Bristol", "Greenock", "Glasgow", "Falmouth", "London", "Ryde", "Spithead", "Liverpool" ]

WIN_vals = [ 	"Jamaica",
				"St Croix",
				"St Kitts",
				"St Nevis",
				"Antigua",
				"Guadeloupe",
				"Dominica",
				"Martinique",
				"St Lucia",
				"Barbados",
				"St Vincent",
				"Grenada",
				"Tobago",
				"Trinidad",
				"Essequebo",
				"Demerara",
				"Berbice",
				"Surinam" ]

WIN_keys = [ 	"JAM",
			 	"VIR",
				"K&N",
				"ANT",
				"GUA",
				"DOM",
				"MAR",
				"LUC",
				"BAR",
				"VIN",
				"GRE",
				"TOB",
				"TRI",
				"GUI",
				"SUR" ]

WIN_zones 	= [ "JAM", "GUI", "TOB", "GRE", "VIN", "DOM", "TRI", "THO", "TOR", "BAH", "LUC", "KIT", "NEV", "MAR", "BAR", "CRO", "ANT", "SUR" ]
GBR_zones 	= [ "HLD", "LLD", "ENG", "SCO", "IRE" ]
INT_zones 	= [ "WIN", "EIN", "CNA", "OTH", "NON" ]

PEOPLA_at_actions = [ "AT", "OCC", "LETTER_SENT", "LETTER_RECD" ]
PEOPLA_ex_actions = [ "EX", "BORN", "FATHER_AT", "FATHER_OCC", "EX-OCC" ]
PEOPLA_re_actions = [ "RE", "DIED", "MEMORIAL" ]

HLD_vals = [ "SCO, RSS", "SCO, ROS", "SCO, INV", "SCO, CAI", "SCO, SUT", "SCO, ARG", "SCO, NAI", "SCO, HLD" ]
LLD_vals = [ "SCO, BUT", "SCO, LAN", "SCO, LTN", "SCO, Glasgow", "SCO, Edinburgh", "SCO, ANG", "SCO, LOT", "SCO, REN", "SCO, LLD", "SCO, DMF", "SCO, DUM", "SCO, DMB", "SCO, ELG", "SCO, Edin", "SCO, ABE", "SCO, FIF" ]
GBR_vals = [ "SCO", "ENG", "GBR" ]
WIN_vals = [ "WIN" ]
SCO_vals = [ "SCO" ]
ENG_vals = [ "ENG" ]

FAM_terms	= [
	"Parent",
	"Brother",
	"Sister",
	"Father",
	"Mother",
	"Cousin",
	"Nephew",
	"Aunt",
	"Grandfather",
	"Friend",
	"Niece",
	"Son",
	"Benefactor" ]
