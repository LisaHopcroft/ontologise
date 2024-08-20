import ontologize.modules.data_transformation.autoparse.all as autoparse
import ontologize.modules.data_transformation.all as prep

# 2024-08-09: this should be defined in TSVs and imported into script ... !

port_keywords = {
	"WIN, JAM": 		[ "Jamaica", ],
	"WIN, VIN": 		[ "St Vincent", "St. Vincent", ],
	"WIN, BAR": 		[ "Barbados", " Barabados", "Brabodoes", "Barbados", "Bardabos" ],
	"WIN, GRE": 		[ "Grenada", ],
	"WIN, SUR": 		[ "Surinam", "Nicare", "Surimam" ],
	"WIN, ANT": 		[ "Antigua", ],
	"WIN, GUI":			[ "George Town" ],
	"WIN, GUI, BER": 	[ "Berbice", "Beribce" ],
	"WIN, MAR": 		[ "Martinique", ],
	"WIN, VIR": 		[ "St. Bartholomews", "St. Barthomews", "St. Bartholomew", "St. Thomas", "St. Thos", "St. John", "St. Croix", "St Thomas", "Tortola" ],
	"WIN, TRI": 		[ "Trinidad", ],
	"WIN, LUC": 		[ "St Lucia", "St. Lucia", "St. Lucie.", "St. Luicia" ],
	"WIN, KIT": 		[ "St. Kitts"," St. Christopher", "St. Kit.", "Saint Kitt's" ],
	"WIN, NEV": 		[ "Nivis", ],
	"WIN, TOB": 		[ "Tobago", ],
	"WIN, TUR": 		[ "Turks Island", ],
	"WIN, MON":			[ "Montserat" ],
	"WIN, GUA":			[ "Guadeloupe", "Guadaloupe" ],
	"WIN, DOM":			[ "Dominica", "Dominique" ],
	"WIN, TUR":			[ "Turks' Island", "Turks Island" ],
	"WIN, BTH":			[ "St. Bartholomews", "St. Bartholemew's", "St. Bartholemews" ],
	"WIN, CUR":			[ "Curacao", "Curacoa" ],
	"WIN":				[ "Islands" ],

	"ATL, BDA": 		[ "Bermuda", ],

	"SCO, Glasgow":		[ "Glasgow", "Greenock", "Clyde", " Grenock", "Grennock" ],

	"ENG, Sunderland":	[ "Sunderland", ],
	"ENG, Bristol":		[ "Bristol", ],
	"ENG, Liverpool":	[ "Liverpool", ],
	"ENG, Lancaster":	[ "Lancaster", ],
	"ENG, Portsmouth":	[ "Portsmouth", "Porstmouth" ],
	"ENG, London":		[ "London", ],
	"ENG, Gloucester":	[ "Gloucester", ],
	"ENG, Falmouth":	[ "Falmoth", "Falmouth", "Flushing" ],
	"ENG, Plymouth":	[ "Plymouth", ],
	"ENG, Whitehaven":	[ "White Haven", "Whitehaven" ],
	"ENG, York":		[ "York", ],
	"ENG, Guernsey":	[ "Guernsey" ],
	"ENG, Colchester":	[ "Colchester" ],
	"ENG, Dover":		[ "Dover" ],
	"IRE, Dublin":		[ "Dublin", ],
	"IRE, Belfast":		[ "Belfast", ],
	"IRE, Mayo":		[ "Island Mayo", ],
	"IRE, Cork":		[ "Cork", ],

	"EUR, Amsterdam":	[ "Amsterdam", ],
	"EUR, Tenerife":	[ "Teneriffe", "Tenerif" ],
	"EUR, Gothenburg":	[ "Gothenburg", ],
	"EUR, Lisbon":		[ "Lisbon", ],
	"EUR, Gibraltar":	[ "Gibraltar" ],
	"EUR, Rotterdam":	[ "Rotterdam" ],
	"EUR, Malta":		[ "Malta" ],

	"ATL, Madeira":		[ "Madeira", ],
	"ATL, Fayal":		[ "Fayal", ],

	"AFR, Cape of Good Hope":	[ "Cape Good Hope" ],
	"AFR, Ascension":			[ "Island of Ascension" ],
	"AFR":						[ "Africa"],

	"CNA, Carolinas":	[ "Charleston", "Newburn" ],
	"CNA, Canada":		[ "Newfoundland", "Nova Scotia", "New Brunswick", "New Foundland", "Halifax", "St. Andrews", "St Andrews", "St Andrew's", "St. Andrew's", "Quebec", "Cape Breton" ],
	"CNA, Conneticut":	[ "New Haven", "New London", "Newhaven", "Hartford", "Milford", "Saybrook" ],
	"CNA, Delaware":		[ "Wilmington", "Newcastle" ],
	"CNA, Georgia":		[ "Savannah", ],
	"CNA, Louisiana":	[ "New Orleans", ],
	"CNA, Maryland":	[ "Baltimore", "Washington", ],
	"CNA, Maine":		[ "Saco", "Wiscasset", "Penobscot", "Bath N.A", "Biddeford", "Beddeford", "Kennebunk", "Kennebeck", "Kennebuck", "Bath", "Beddefort", "Kennebunck", "Kennebank", "Kennybeck", "Portland", "Yarmouth", "Waldeborough", "Peneobscot", "Kennebek", "Waldobrough" ],
	"CNA, Massachusetts":	[ "Boston", "Rhode Island", "Salem", "Newbury Port", "Newburyport", "Cape Ann", "Charlestown", "Massachusetts", "Charlstown", "Newberry Port", "Newbury P" ],
	"CNA, New Jersey":	[ "New York", "New-York", "Philadelphia", "Newyork" ],
	"CNA, New Hampshire":	[ "New Hampshire"],
	"CNA, North Carolina":	[ "North Carolina" ],
	"CNA, Virginia":	[ "Norfolk", ],
	"CNA":				[ "N. A.", "N.A.", "U.S", "America" ],
	"CSA":				[ "Oronoque",  "Monte Video", "Mounte Video", "Pernambuco", "Maranham", "Santos" ]
}

vessel_type_keywords = {
	"schooner": 		[ "Schnr. ", "Schr. ", "Schooner ", "Schooner, ", "Shoon ", "Sch. ", "Shooner [sic] " ],
	"sloop":			[ "Sloop ", ],
	"ship":				[ "Ship ", "Ship, ", ],
	"brig":				[ "Brig ", ],
	"snow":				[ "Snow ", "snow " ],
	"barque": 			[ "Bark ", "Barque " ]
}


def munge_EXIT_PERMIT( line, context_date, context_at, src_filepath, line_num ):
	PEOPLA_dat = []

	line = line.replace( "[-] ", "" )

	pers_txt	= line
	pers_list	= []

	# source specific parsing...
	if "," in pers_txt:
		pers_txt	= pers_txt.split( ", ", 1 )[0]
	if " in " in pers_txt:
		pers_txt		= pers_txt.split( " in ", 1 )[0]
	if " with " in pers_txt:
		pers_txt		= pers_txt.split( " with ", 1 )[0]
	if " will transport " in pers_txt:
		pers_txt		= pers_txt.split( " will transport ", 1 )[0]
	if " will Transport " in pers_txt:
		pers_txt		= pers_txt.split( " will Transport ", 1 )[0]
	if " will send " in pers_txt:
		pers_txt		= pers_txt.split( " will send ", 1 )[0]
	if " will transfer " in pers_txt:
		pers_txt		= pers_txt.split( " will transfer ", 1 )[0]

	if " and " in pers_txt:
		pers_list = pers_txt.split( " and " )
	elif " & " in pers_txt:
		pers_list = pers_txt.split( " & " )
	else:
		pers_list = [ pers_txt ]

	for pers_txt in pers_list:
		race		= autoparse.get_race_from_txt( pers_txt )
		is_child	= autoparse.get_is_child_from_txt( pers_txt )
		pers_id		= autoparse.get_pers_id_from_txt( pers_txt )

		date_dat 	= prep.mkd.convert_txtdate_to_DAT( context_date )
		PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
		PEOPLA_dict["src_ref"] 		= prep.get_ref_from_filepath( src_filepath.strip() )
		PEOPLA_dict["pers_id"] 		= pers_id
		PEOPLA_dict["person_txt"] 	= pers_txt
		PEOPLA_dict["place_id"] 	= context_at
		PEOPLA_dict["action"] 		= "EXIT"
		PEOPLA_dict["date1_y"] 		= date_dat["date1_y"]
		PEOPLA_dict["date1_m"] 		= date_dat["date1_m"]
		PEOPLA_dict["date1_d"] 		= date_dat["date1_d"]
		PEOPLA_dict["src_type"] 	= "EXIT-PERMIT"
		PEOPLA_dict["src_filepath"] = src_filepath.strip()
		PEOPLA_dict["src_linenum"] 	= line_num
		PEOPLA_dict["race"] 		= race
		PEOPLA_dict["is_child"] 	= is_child
		#PEOPLA_dict["txt"] 		= line  # this will add too much to the database ... ?

		PEOPLA_dat.append( PEOPLA_dict )

	return PEOPLA_dat


def munge_SHIPPING( line, src_type, context_date, context_at, src_filepath, line_num ):
	line = line.replace( "[-] ", " " )
	line = line.replace( "[+] ", " " )
	if ", for " in line:
		line = line.replace( ", for ", ", " )
	if " for " in line:
		line = line.replace( " for ", ", " )
	if ", from " in line:
		line = line.replace( ", from ", ", " )
	if " from " in line:
		line = line.replace( " from ", ", " )
	line = line.replace( ",", ", " ).replace( ";", ", " ).replace( "\.", "." )

	vessel_txt		= ""
	vessel_id		= ""
	vessel_type		= ""
	capt_text		= ""
	capt_id			= ""
	fm_port_txt		= ""
	fm_port_id		= ""
	to_port_txt		= ""
	to_port_id		= ""
	via_port_ids	= ""

	port_txt		= ""
	if line.count(",") == 1:
		vessel_txt 	= line.split(",")[0]
		misc_txt 	= line.split(",")[1]
		if autoparse.search_keyvals( port_keywords, misc_txt ):
			port_txt = misc_txt
		else:
			capt_txt = misc_txt
	elif line.count(",") == 2:
		vessel_txt 	= line.split(",")[0]
		capt_txt	= line.split(",")[1]
		port_txt 	= line.split(",")[2]
	elif line.count(",") > 2:
		vessel_txt 	= line.split(",")[0]
		capt_txt	= line.split(",")[1]
		port_txt 	= line.split(",")[2]
	else:
		print( line )
		print( src_filepath )
		return []

	# should do as regex...
	date_seperators = []
	nums = [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ]
	for num in nums:
		date_seperators.append( num + "." )
		date_seperators.append( num + " " )
		date_seperators.append( num + "d." )
		date_seperators.append( num + "th." )
		date_seperators.append( num + "st." )
		date_seperators.append( num + "d " )
		date_seperators.append( num + "th " )
		date_seperators.append( num + "st " )

	for sep in date_seperators:
		if sep in vessel_txt:
			vessel_txt = " " + vessel_txt.split(sep,1)[1] + " "

	months = [
		" Jan.",
		" Feb.",
		" Mar.",
		" Apr.",
		" May.",
		" Jun.",
		" Jul.",
		" Aug.",
		" Sep.",
		" Sept.",
		" Octr.",
		" Oct.",
		" Nov.",
		" Decb.",
	]

	for month_txt in months:
		vessel_txt = vessel_txt.replace( month_txt, " " )

	if any(substr in src_type for substr in ["ARRIVED","ENTERED"]):
		fm_port_txt = port_txt
		to_port_id 	= context_at
	if any(substr in src_type for substr in ["CLEARED","DEPARTED"]):
		to_port_txt = port_txt
		fm_port_id 	= context_at

	vessel_type = autoparse.search_keyvals( vessel_type_keywords, vessel_txt )
	vessel_id	= autoparse.strip_keyvals( vessel_type_keywords, vessel_txt )

	# todo: captain parsing...

	if not fm_port_id:
		fm_port_id 	= autoparse.search_keyvals( port_keywords, fm_port_txt )
	if not to_port_id:
		to_port_id 	= autoparse.search_keyvals( port_keywords, to_port_txt )

	date_dat = prep.mkd.convert_txtdate_to_DAT( context_date )
	SAILING_dict = prep.get_RDB_table_as_dict( "ADD_sailing" )
	SAILING_dict["vessel_txt"] 		= vessel_txt.strip()
	SAILING_dict["vessel_id"] 		= vessel_id.strip()
	SAILING_dict["vessel_type"] 	= vessel_type.strip()
	SAILING_dict["capt_text"] 		= capt_text.strip()
	SAILING_dict["capt_id"] 		= capt_id.strip()
	SAILING_dict["fm_port_txt"] 	= fm_port_txt.strip()
	SAILING_dict["fm_port_id"] 		= fm_port_id.strip()
	SAILING_dict["to_port_txt"] 	= to_port_txt.strip()
	SAILING_dict["to_port_id"] 		= to_port_id.strip()
	SAILING_dict["via_port_ids"] 	= via_port_ids.strip()
	SAILING_dict["date1_y"]			= date_dat["date1_y"]
	SAILING_dict["date1_m"] 			= date_dat["date1_m"]
	SAILING_dict["date1_d"] 			= date_dat["date1_d"]
	SAILING_dict["src_filepath"] 	= src_filepath.strip()
	SAILING_dict["src_type"] 		= src_type

	return [ SAILING_dict ]


def munge_JAIL_SLAVES( line, context_date, context_at, src_filepath, line_num ):
	return []


def munge_TRANSPORTS( line, context_date, context_at, src_filepath, line_num ):
	return []


def munge_PERS_ONLY( line, context_date, context_at, src_filepath, line_num, src_type ):
	PEOPLA_dict = []

	if "[:]" in line:
		line = line.split("[:]")[0]

	if line.count("*") == 2:
		pers_txt = line.split("*",1)[1].split("*",1)[0]
	else:
		pers_txt = line

	pers_txt = pers_txt.replace("*","")

	race		= autoparse.get_race_from_txt( pers_txt )
	is_child	= autoparse.get_is_child_from_txt( pers_txt )
	pers_id		= autoparse.get_pers_id_from_txt( pers_txt.replace( "[-] ","" ) )

	date_dat 	= prep.mkd.convert_txtdate_to_DAT( context_date )
	PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
	PEOPLA_dict["src_ref"] 		= prep.get_ref_from_filepath( src_filepath.strip() )
	PEOPLA_dict["pers_id"] 		= pers_id
	PEOPLA_dict["person_txt"] 	= pers_txt.replace( "[-] ","" ).strip()
	PEOPLA_dict["place_id"] 	= context_at
	PEOPLA_dict["action"] 		= ""
	PEOPLA_dict["date1_y"] 		= date_dat["date1_y"]
	PEOPLA_dict["date1_m"] 		= date_dat["date1_m"]
	PEOPLA_dict["date1_d"] 		= date_dat["date1_d"]
	PEOPLA_dict["src_type"] 	= src_type
	PEOPLA_dict["src_filepath"] = src_filepath.strip()
	PEOPLA_dict["src_linenum"] 	= line_num
	PEOPLA_dict["race"] 		= race
	PEOPLA_dict["is_child"] 	= is_child

	return [ PEOPLA_dict ]


def munge_AVG_PRICES( line, context_date, context_at, src_filepath, line_num ):
	PRICES_dat = []

	line = line.replace("[-] ","")

	produce = ""
	if line.startswith( "Cotton" ):
		produce = "cotton"
	if line.startswith( "Sugar" ):
		produce = "sugar"
	if line.startswith( "Coffee" ):
		produce = "coffee"
	if line.startswith( "Rum" ):
		produce = "rum"

	num			= 0
	numbers 	= [int(s) for s in line.split() if s.isdigit()]
	if numbers:
		num 	= numbers[0]

	date_dat 	= prep.mkd.convert_txtdate_to_DAT( context_date )
	PRICES_dat 	= prep.get_RDB_table_as_dict( "ADD_prices" )
	PRICES_dat["produce"] 	= produce
	PRICES_dat["num"] 		= num
	PRICES_dat["curr"] 		= "Stivers"
	PRICES_dat["place_id"] 	= context_at
	PRICES_dat["y1"]		= date_dat["y1"]
	PRICES_dat["m1"] 		= date_dat["m1"]
	PRICES_dat["d1"] 		= date_dat["d1"]

	return [ PRICES_dat ]
