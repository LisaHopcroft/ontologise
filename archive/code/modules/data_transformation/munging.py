
# most common corruptions
synonyms = {
	# SCO cities
	"Edinburgh":	[ "Edinborough", "Edinboro", "Edinburo", "Edenborough", "Edenburgh", "Leith" ],
	"Glasgow":		[ "Glascow", "Glasgo" ],
	"Inverness":	[ "Invernis", "Inverniss", "Invernes", "Invemess", "Invernass", "Inverriess", ],
	"Aberdeen":		[ "Abirdeen", "Aiberdeen", "Aberdein", "Abendeen" ],
	"Kilmarnock":	[ "Kilmamock", "Kilmarnok" ],
	"Greenock":		[ "Greenok", "Grenock" ],
	"Paisley":		[ "Paisly" ],

	# ENG cities
	"Stoke-upon-Trent":	[ "Stoke" ],
	"Great Yarmouth":	[ "Yarmouth" ],

	# Nations
	"GBR, SCO":		[ "Scotland", "Caledonia", "Caledonian", "Alba", "Scotia", "Scotsman", "Scotch" ],
	"GBR, ENG":		[ "England", "Anglia" ],
	"GBR, WAL":		[ "Wales", "Cambria" ],
	"GBR, IRE":		[ "Ireland", "Hibernia", "Hybernia" ],
	"GBR, HLD":		[ "Highlands", "Highlander", ],

	"GBR, GBR":		[ "Briton", "Britannia", "Britain" ],

	# HLD other
	"Lemlair":		[ "Limlair" ],
	"Glencoe":		[ "Glenco" ],
	"Ft William":	[ "Fort William" ],
	"Ft Augustus":	[ "Fort Augustus" ],
	"Campbelltown":	[ "Campbeltown" ],
	"Argyll":		[ "Argyle" ],
	"Dunvegan":		[ "Dunvagan" ],
	"Roxburgh":		[ "Roxborough" ],
	"Runnymede":	[ "Runnemede" ],
	"Speyside":		[ "Spey Side" ],
	"Monymusk":		[ "Moneymusk" ],
	"Kendal":		[ "Kendall" ],
	"Bideford":		[ "Biddiford" ],
	"Grampian":		[ "Grampion" ],
	"Llanddewi":	[ "Llanddewey" ],
	"Cairncurran":	[ "Carncurran" ],
	"Chelsea":		[ "Chealsea" ],

	# surnames
	"M'intosh":		[ "M'entosh", ],
	"M'kenzie":		[ "M'kensie", "M'kinzie" ],
	"M'lauchlan":	[ "M'lanchlan", "M'lachlan" ],
	"M'pherson":	[ "M'phenson", ],
	"M'allister":	[ "M'alastair", "M'allastair", "M'alister" ],
	"M'neal":		[ "M'neil", "M'neill", "M'neall" ],
	"M'nicol":		[ "M'nichol" ],
	"M'millan":		[ "M'millen" ],
	"M'dermott":	[ "M'dermot" ],
	"M'culloch":	[ "M'cullock" ],
	"M'alpin":		[ "M'alpine" ]
}


synonyms_surnames = {
	"M'intosh":		[ "M'entosh", ],
	"M'kenzie":		[ "M'kensie", "M'kinzie" ],
	"M'lauchlan":	[ "M'lanchlan", "M'lachlan" ],
	"M'pherson":	[ "M'phenson", ],
	"M'allister":	[ "M'alastair", "M'allastair", "M'alister" ],
	"M'neal":		[ "M'neil", "M'neill", "M'neall" ],
	"M'nicol":		[ "M'nichol" ],
	"M'millan":		[ "M'millen" ],
	"M'dermott":	[ "M'dermot" ],
	"M'culloch":	[ "M'cullock" ],
	"M'alpin":		[ "M'alpine" ]
}

# converting in to an easier to process datatype
synonyms_list = []
synonyms_keys = []
for key, vals in synonyms.items():
for val in vals:
	synonyms_keys.append( prep_txt( key ) )
	synonyms_list.append( ( prep_txt( key ), prep_txt( val ) ) )
