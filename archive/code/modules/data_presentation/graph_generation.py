import os, sys, glob
sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
#import util.confdat as confdat
import fnmatch

academia_root = "/media/michael/SSD3/Dropbox/workspace/2.research"
comphist_root = academia_root + "/_bin/comphist"

# new
freq_path 	= "%s/%s" % ( comphist_root, "/run/draw-freq.R" )
maps_path 	= "%s/%s" % ( comphist_root, "/run/draw-maps.R" )
fill_path 	= "%s/%s" % ( comphist_root, "/run/draw-fill.R" )

# intermediate
enrichm_path 	= "%s/%s" % ( comphist_root, "/run/draw-graphs_enrichment.R" )
barplot_path 	= "%s/%s" % ( comphist_root, "/run/draw-graphs_barplot.R" )
stacked_path 	= "%s/%s" % ( comphist_root, "/run/draw-graphs_stacked.R" )
percent_path 	= "%s/%s" % ( comphist_root, "/run/draw-graphs_percentage.R" )
parish_path 	= "%s/%s" % ( comphist_root, "/run/draw-graphs_parish.R" )

# old
old_yearly_path	= "%s/%s" % ( comphist_root, "/run/draw-graphs_yearly.R" )
old_zones_path	= "%s/%s" % ( comphist_root, "/run/draw-graphs_zones.R" )


def escape_glob( text ):
	return text.replace( "[", "<" ).replace( "]", ">" ).replace( "<", "[[]" ).replace( ">", "[]]" ).replace( " ", "\ " )


def escape_fpath( text ):
	return text.replace( "^", "\^" ).replace( "{", "\{" ).replace( "}", "\}" ).replace( "[", "\[" ).replace( "]", "\]" )


def execute( script_type, filepath ):
	writedir = filepath.rsplit( "/", 1 )[0].replace( "/dat", "/fig" )

	freq_cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( freq_path, filepath, writedir )
	maps_cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( maps_path, filepath, writedir )
	fill_cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( fill_path, filepath, writedir )

	# new
	if script_type == "freq":
		cmd = freq_cmd

	elif script_type == "freq_yearly":
		cmd = freq_cmd + " --type '%s'" % ( "yearly" )

	elif script_type == "freq_at":
		cmd = freq_cmd + " --type '%s'" % ( "at" )

	elif script_type == "maps":
		cmd = maps_cmd

	elif script_type == "fill":
		cmd = fill_cmd

	# old
	elif script_type == "enrichment":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( enrichm_path, filepath, writedir )

	elif script_type == "stacked":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( stacked_path, filepath, writedir )

	elif script_type == "stacked_yearly":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s' --itemtype '%s' --binsize %s" % ( stacked_path, filepath, writedir, "yearly", 5 )

	elif script_type == "stacked_yearly_NOBIN":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s' --itemtype '%s'" % ( stacked_path, filepath, writedir, "yearly" )

	elif script_type == "percent":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( percent_path, filepath, writedir )

	elif script_type == "parish":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( parish_path, filepath, writedir )

	elif script_type == "barplot":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( barplot_path, filepath, writedir )

	# v old
	elif script_type == "old_yearly":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s' --scope %s --startyear %s --endyear %s" % ( old_yearly_path, filepath, writedir, "\"\"", 1750, 1850 )

	elif script_type == "old_zones_INT":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( old_zones_path, filepath, writedir )

	elif script_type == "old_zones_WIN":
		cmd = "Rscript --vanilla %s --file '%s' --out '%s'" % ( old_zones_path, filepath, writedir )

	else:
		print( "***NO SCRIPT SPECIFIED***" )
		return

	print( "-------------------------------------------------------------------------------------------------" )
	print( cmd )
	os.system( cmd )#+ " &>/dev/null" )


def recursive_find( basepath, pattern ): # run glob search in every sub directory...
	matches = []
	for root, dirs, files in os.walk( basepath ):
		for dirname in dirs:
			match_pattern = escape_glob( "%s/%s/%s" % ( root, dirname, pattern ) )
			matches += glob.glob( match_pattern )
	return matches


def draw_graphs( basepath, is_refresh=False ):

	dat_patterns = [

		# new
		{
			"pattern": 	"^*yearly.TOT.tsv",
			"analyses": [ "freq_yearly" ],
		},
		{
			"pattern": 	"^*mappings.tsv",
			"analyses": [ "maps" ],
		},
		{
			"pattern": 	"^*colony.TOT.tsv",
			"analyses": [ "freq_at" ]
		},
		{
			"pattern": 	"^*parish.TOT.tsv",
			"analyses": [ "freq_at", "parish" ]
		},
		{
			"pattern": 	"^*regional.colony.tsv",
			"analyses": [ "fill" ]
		},

		# intermediate
		{
			"pattern": 	"^POPULATIONS/^*].tsv",
			"analyses": [ "freq" ]
		},
		#{
		#	"pattern": 	"^*].tsv",
		#	"analyses": [ "freq" ],
		#},

		# old
		#{
		#	"pattern": 	"^*.yearly.tsv",
		#	"analyses": [ "old_yearly" ]
		#},
		#{
		#	"pattern": 	"^*.INT_zones.tsv",
		#	"analyses": [ "old_zones_INT" ]
		#},
		#{
		#	"pattern": 	"^*.WIN_zones.tsv",
		#	"analyses": [ "old_zones_WIN" ]
		#},'''

	]

	if is_refresh:
		print( "Refreshing..." )
		for filepath in recursive_find( basepath, "/fig/*/^*" ):
			os.system( "rm '%s'" % ( filepath ) )

	for dat in dat_patterns:
		print( "Generating graphs for %s..." % dat["pattern"] )
		for filepath in recursive_find( basepath, dat["pattern"] ):
			for val in dat["analyses"]:
				execute( val, filepath )


def get_fig_identifier( filepath ):
	element = filepath.split("/fig/",1)[1]
	if ".yearly." in element:
		element = element.split(".yearly.")[0]
	if ".at." in element:
		element = element.split(".at.")[0]
	return element.replace( "[$POPULATIONS]", "" ).replace( "[$SURNAMES]", "" ).replace( "[$PLACENAMES]", "" ).replace( ".[", ", " ).replace( "^POPULATIONS/^POPULATIONS, ", "POPULATIONS: " ).replace( "^SURNAMES/^SURNAMES, ", "SURNAMES: " ).replace( "^PLACENAMES/^PLACENAMES, ", "PLACENAMES: " ).replace( "]", "" ).replace("[",".")


def write_mkd_img( w, i, filepath ):
	w.write( "![i%s](%s)\n" % ( i, filepath ) )
	w.write( "Fig %s. %s\n\n" % ( i, get_fig_identifier( filepath ) ) )
	return i + 1


def write_mkd_reports( basepath, is_refresh=False ):
	writedir 	= basepath + "/^mkd"
	if not os.path.exists( writedir ):
		os.mkdir( writedir )

	if is_refresh:
		if glob.glob( escape_glob( writedir + "/^*" ) ):
			os.system( "rm %s" % escape_fpath( writedir + "/^*" ) )

	fig_patterns = [

		# basic
		{	"name":		"old.INT_YEARLY",
			"pattern":	"*INT_yearly_BARPLOT*",
			"files":	[]	},
		{	"name":		"old.WIN_YEARLY",
			"pattern":	"*WIN_yearly_BARPLOT*",
			"files":	[]	},
		{	"name":		"old.INT_ZONES",
			"pattern":	"*INT_zones_BARPLOT*",
			"files":	[]	},
		{	"name":		"old.WIN_ZONES",
			"pattern":	"*WIN_zones_BARPLOT*",
			"files":	[]	},
		{	"name":		"old.YEARLY",
			"pattern":	"*.yearly_BASIC.*",
			"files":	[]	},

		# src
		{	"name":		"src.VIOLIN",
			"pattern":	"*.yearly_VIOLIN.*",
			"files":	[]	},

		# parish
		{	"name":		"parish.TOT_BARPLOT_PCT_1",
			"pattern":	"*parish*TOT_BARPLOT_PCT_1*",
			"files":	[] 	},
		{	"name":		"parish.TOT_BARPLOT_PCT_2",
			"pattern":	"*parish*TOT_BARPLOT_PCT_2*",
			"files":	[] 	},
		{	"name":		"parish.TOT_BARPLOT_PCT_3",
			"pattern":	"*parish*TOT_BARPLOT_PCT_3*",
			"files":	[] 	},

		{	"name":		"parish.MAPS",
			"pattern":	"*JAM-MAP*FREQ_1-SRC_SIZE.*",
			"files":	[]	},

		# colony
		{	"name":		"colony.STACKEDBAR_ABS",
			"pattern":	"*colony*STACKEDBAR*abs*",
			"files":	[] },
		{	"name":		"colony.STACKEDBAR_PCT",
			"pattern":	"*colony*STACKEDBAR*SRC_SIZE*",
			"files":	[] },
		{	"name":		"colony.BARPLOT_PCT_1v2",
			"pattern":	"*colony*TOT_BARPLOT*FREQ_1-FREQ_2*",
			"files":	[] 	},

		# colony
		{	"name":		"colony.TOT_BARPLOT_FREQ_1",
			"pattern":	"*colony*TOT_BARPLOT_FREQ_1*",
			"files":	[] 	},
		{	"name":		"colony.TOT_BARPLOT_FREQ_2",
			"pattern":	"*colony*TOT_BARPLOT_FREQ_2*",
			"files":	[] 	},
		{	"name":		"colony.TOT_BARPLOT_FREQ_3",
			"pattern":	"*colony*TOT_BARPLOT_FREQ_3*",
			"files":	[] 	},

		{	"name":		"colony.TOT_BARPLOT_PCT_1",
			"pattern":	"*colony*TOT_BARPLOT_PCT_1*",
			"files":	[] 	},
		{	"name":		"colony.TOT_BARPLOT_PCT_2",
			"pattern":	"*colony*TOT_BARPLOT_PCT_2*",
			"files":	[] 	},
		{	"name":		"colony.TOT_BARPLOT_PCT_3",
			"pattern":	"*colony*TOT_BARPLOT_PCT_3*",
			"files":	[] 	},

		# yearly
		{	"name":		"yearly.STACKEDBAR_ABS",
			"pattern":	"*yearly*STACKEDBAR*abs*",
			"files":	[] },
		{	"name":		"yearly.STACKEDBAR_PCT",
			"pattern":	"*yearly*STACKEDBAR*SRC_SIZE*",
			"files":	[] },
		{	"name":		"yearly.BARPLOT_PCT",
			"pattern":	"*yearly*TOT_BARPLOT*SRC_SIZE*",
			"files":	[] },

		# crossanalysis
		{	"name":		"xanalysis.ENRICHMENT",
			"pattern":	"*ENRICHMENT*",
			"files":	[]	},
		{	"name":		"xanalysis.RT_PCT",
			"pattern":	"*]_STACKEDBAR_SRC_SIZE*",
			"files":	[]	},
		{	"name":		"xanalysis.RT_ABS",
			"pattern":	"*]_FREQ.*",
			"files":	[]	},
	]


	# retrieve files
	for fig in fig_patterns:
		fig["files"] = recursive_find( basepath, fig["pattern"] + "png" )


	# write files
	for fig in fig_patterns:
		if fig["files"]:
			with open( writedir + "/^%s.mkd" % fig["name"], "w" ) as w:
				i = 1
				prev_dirpath = ""

				for filepath in sorted( fig["files"] ):
					dirpath = filepath.rsplit("/fig/")[0].rsplit("/",1)[1]
					if dirpath != prev_dirpath:
						w.write( "\n\n# %s\n\n" % dirpath ) #.split("_",1)[1] )
					i = write_mkd_img( w, i, filepath )
					prev_dirpath = dirpath
