#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import os, csv, re
import operator
import sys
sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.confdat as confdat
import ontologize.modules.util.util as util

# these are generic patterns...
# also each write_tex file appends their own specific patterns, as per local requirements...

patterns = [
{
	"file_pattern": "^REGIONGROUPS",
	"orientation": 	"portrait",
	"fields": OrderedDict([
		( "ITEM", 			{ "header": "Region", 					"justification": "l",	"format": "str" } ),
		( "N",				{ "header": "Number of \\\\ localised \\\\ surnames", "justification": "r",	"format": "longint" } ),
		#( "BASE_TOT", 		{ "header": "British \\\\ surname popl. \\\\ (1881)", 		"justification": "r",	"format": "longint" } ),
		( "BASE_PCT", 		{ "header": "UK 1881 \\\\ occurrence \\\\ per million", 			"justification": "r",	"format": "pct_per_million" } ),
		#( "FREQ", 			{ "header": "", 		"justification": "r",	"format": "longint" } ),
		( "PCT", 			{ "header": "Observed \\\\ occurrence \\\\ per million", 			"justification": "r",	"format": "pct_per_million" } ),
		( "OBS_VS_BASE", 	{ "header": "+/-", 						"justification": "r",	"format": "diff" } )
	])
},
{
	"suffix":		"prob",
	"file_pattern": "*parish.TOT.tsv",
	"orientation": 	"portrait",
	"fields": OrderedDict([
		( "ITEM",			{ "header": "Parish",	"justification": "l",	"format": "str" } ),
		( "SRC_SIZE", 		{ "header": "N", 		"justification": "r",	"format": "longint" } ),
		( "FREQ_1", 		{ "header": "Number of \\\\ matches", 		"justification": "r",	"format": "longint", 			"multicolheader": "Threshhold" } ),
		( "PCT_1", 			{ "header": "Incidence \\\\ per million", 	"justification": "r",	"format": "pct_per_million", 	"multicolheader": "Threshhold" } ),
		( "VAL_1", 			{ "header": "Representative \\\\ value (r.v.)", 	"justification": "r",	"format": "pct" } )
	])
},
{
	"suffix":		"appendix",
	"file_pattern": "*parish.TOT.tsv",
	"orientation": 	"landscape",
	"fields": OrderedDict([
		( "ITEM",			{ "header": "Parish",	 	"justification": "l",	"format": "str" } ),
		( "SRC_SIZE", 		{ "header": "N", 			"justification": "r",	"format": "longint" } ),
		( "FREQ_1", 		{ "header": "Number of \\\\ matches", 	"justification": "r",	"format": "longint" } ),
		( "matches_1", 		{ "header": "Breakdown of results", 		"justification": "p{17cm}",	"format": "str" } )
	])
},
{
	"suffix":		"thold",
	"file_pattern": "*colony.TOT.tsv",
	"orientation": 	"portrait",
	"fields": OrderedDict([
		( "ITEM",			{ "header": "Colony",	"justification": "l",	"format": "str" } ),
		( "SRC_SIZE", 		{ "header": "N", 		"justification": "r",	"format": "longint" } ),
		( "FREQ_1", 		{ "header": "Number of \\\\ matches", 		"justification": "r",	"format": "longint" } ),
		( "PCT_1", 			{ "header": "Incidence \\\\ per million", 	"justification": "r",	"format": "pct_per_million" } )
	])
},
{
	"suffix":		"prob",
	"file_pattern": "*colony.TOT.tsv",
	"orientation": 	"portrait",
	"fields": OrderedDict([
		( "ITEM",			{ "header": "Colony",	"justification": "l",	"format": "str" } ),
		( "SRC_SIZE", 		{ "header": "N", 		"justification": "r",	"format": "longint" } ),
		( "FREQ_1", 		{ "header": "Number of \\\\ matches", 		"justification": "r",	"format": "longint", 			"multicolheader": "Threshhold" } ),
		( "PCT_1", 			{ "header": "Incidence \\\\ per million", 	"justification": "r",	"format": "pct_per_million", 	"multicolheader": "Threshhold" } ),
		( "VAL_1", 			{ "header": "Representative \\\\ value (r.v.)", 	"justification": "r",	"format": "pct" } )
	])
},
{
	"suffix":		"appendix",
	"file_pattern": "*colony.TOT.tsv",
	"orientation": 	"landscape",
	"fields": OrderedDict([
		( "ITEM",			{ "header": "Colony",	 	"justification": "l",	"format": "str" } ),
		( "SRC_SIZE", 		{ "header": "N", 			"justification": "r",	"format": "longint" } ),
		( "FREQ_1", 		{ "header": "Number of \\\\ matches", 	"justification": "r",	"format": "longint" } ),
		( "matches_1", 		{ "header": "Breakdown of results", 	"justification": "p{17cm}",	"format": "str" } )
	])
},
{
	"file_pattern": "^SURNAMES*].tsv",
	"orientation": "portrait",
	"fields": OrderedDict([
		( "ITEM",				{ "header": "Surname",	 	"justification": "l",	"format": "str" } ),
		#( "BASE_GRP_VS_BASE", 	{ "header": "\% Localism", 	"justification": "r",	"format": "pct" } ),
		#( "GRP_TOT", 			{ "header": "UK 1881 \\\\ population", 	"justification": "r",	"format": "longint" } ),
		( "BASE_PCT", 			{ "header": "UK 1881 \\\\ incidence \\\\ per million", 		"justification": "r",	"format": "pct_per_million" } ),
		( "PCT", 				{ "header": "Observed \\\\ incidence \\\\ per million", 	"justification": "r",	"format": "pct_per_million" } ),
		( "OBS_VS_BASE", 		{ "header": "Diff. \\\\ mult.", 			"justification": "r",			"format": "diff_mult" } )
	])
},
{
	"file_pattern": ".parish.TOT.tsv",
	"orientation": "portrait",
	"fields": OrderedDict([
		( "ITEM", 			{ "header": "Parish", 				"justification": "l",	"format": "str" } ),
		( "SRC_SIZE", 		{ "header": "Total", 				"justification": "r",	"format": "longint" } ),
		( "2:_SRC_SIZE", 	{ "header": "British", 				"justification": "r",	"format": "longint" } ),
		( "KARRAS_PCT_2", 		{ "header": "\% Scottish \\\\ (Karras, 1991)", 	"justification": "r",	"format": "pct", "optional": True } ), #,
		#( "_2:_SRC_SIZE", 	{ "header": "British \\\\ threshhold", 		"justification": "r",	"format": "longint" } ),
		#( "FREQ_2", 		{ "header": "Scottish \\\\ (threshhold)", 		"justification": "r",	"format": "longint" } ),
		#( "FREQ_1", 		{ "header": "Highland \\\\ threshhold", 		"justification": "r",	"format": "longint" } ),
		( "2:_PCT_2", 			{ "header": "\% Scottish \\\\ (thresh.)", 		"justification": "r",	"format": "pct" } ), #"pre_hline"=True
		#( "PCT_1", 			{ "header": "\% Highland \\\\ threshhold", 		"justification": "r",	"format": "pct" } ),
		( "2:_VAL_2", 		{ "header": "\% Scottish \\\\ (prob.)", 	"justification": "r",	"format": "pct", "pre_hline": False } ), #, 	"pre_hline"=True
		( "2:_VAL_1", 		{ "header": "\% Highland \\\\ (prob.)", 	"justification": "r",	"format": "pct" } ),
		( "VAL_1_vs_VAL_2", 	{ "header": "\% Highland \\\\ vs Scottish \\\\ (prob.)", 	"justification": "r",	"format": "pct" } ),
	])
} ]

latex_pairs = [
	( "HLD", "Highlands" ),
	( "LLD_NI", "Northern \\\\ Isles" ),
	( "LLD_NE", "Grampian" ),
	( "LLD_TS", "Tayside" ),
	( "LLD_CE", "Clyde \\\\ Estuary" ),
	( "LLD_FE", "Forth \\\\ Estuary" ),
	( "LLD_SS", "Southern \\\\ Scotl." ),

	( "CIRNS", "Northern \\\\ Highlands" ),

	( "LLD_GT", "N.E. \\\\ Scotl." ),
	( "LLD_MS", "C.\&S. \\\\ Scotl." ),
	( "ENG_NE", "N.E. \\\\ Engl." ),
	( "ENG_NW", "N.W. \\\\ Engl." ),
	( "ENG_YH", "York." ),
	( "ENG_EM", "E.Mid \\\\ Engl." ),
	( "ENG_WM", "W.Mid \\\\ Engl." ),
	( "ENG_EE", "East \\\\ Engl." ),
	( "ENG_SE", "S.E. \\\\ Engl." ),
	( "ENG_SW", "S.W. \\\\ Engl." ),
	( "WAL", 	"Wales" ),

	( "rGBRA", "Rest of  \\\\ Britain"  ),
	( "rGBR", "Rest of \\\\ Britain" ),
	( "rSCOA", "Rest of \\\\ Scotland" ),
	( "rSCO", "Rest of \\\\ Scotland" ),

	( "SCO", "Scotland" ),
	( "ENG", "England" ),

	( "ARL", "Argyll" ),
	( "CAI", "Caithness" ),
	( "INV", "Inverness" ),
	( "NAI", "Nairn" ),
	( "ROC", "Ross \& C." ),
	( "SUT", "Sutherland" )
]

def replace_latex( textobj ):
	for pair in latex_pairs:
		textobj = textobj.replace( pair[0], pair[1] )
	return textobj


diff_fields 				= []
prob_fields					= []
thold_fields 				= []
baseline_fields 			= []
baseline_prob_diff_fields 	= []
baseline_full_prob_diff_fields 	= []

for region, counties in confdat.regions.items():

	baseline_field = ( "%s_baseline" % region, 	{ "header": "%s" % replace_latex( region ), 		"justification": "r",	"format": "pct" } )
	baseline_fields.append( baseline_field )
	baseline_field = ( "%s_baseline" % region, 	{ "header": "Base.", "justification": "r",	"format": "pct", "multicolheader": "%s" % replace_latex( region ) } )
	baseline_prob_diff_fields.append( baseline_field )
	baseline_full_prob_diff_fields.append( baseline_field )

	full_prob_field = ( "%s_prob_B" % region, 	{ "header": "Prob.", "justification": "r",	"format": "pct", "multicolheader": "%s" % replace_latex( region ) } )
	baseline_full_prob_diff_fields.append( full_prob_field )

	diff_field = ( "%s_diffpct_B" % region, 	{ "header": "\% Diff.", "justification": "r",	"format": "diff", "multicolheader": "%s" % replace_latex( region ) } )
	baseline_full_prob_diff_fields.append( diff_field )

	prob_field = ( "%s_prob" % region, 		{ "header": "%s" % replace_latex( region ), 		"justification": "r",	"format": "pct" } )
	prob_fields.append( prob_field )
	prob_field = ( "%s_prob" % region, 		{ "header": "Prob.", "justification": "r",	"format": "pct", "multicolheader": "%s" % replace_latex( region ) } )
	baseline_prob_diff_fields.append( prob_field )
	baseline_full_prob_diff_fields.append( prob_field )

	diff_field = ( "%s_diffpct" % region, 	{ "header": "%s" % replace_latex( region ), 		"justification": "r",	"format": "diff" } )
	diff_fields.append( diff_field )
	diff_field = ( "%s_diffpct" % region, 	{ "header": "\% Diff.", "justification": "r",	"format": "diff", "multicolheader": "%s" % replace_latex( region ) } )
	baseline_prob_diff_fields.append( diff_field )
	baseline_full_prob_diff_fields.append( diff_field )

	thold_field = ( "%s_thold" % region, 	{ "header": "%s" % replace_latex( region ), 		"justification": "r",	"format": "pct" } )
	thold_fields.append( thold_field )

print( diff_fields )


def intWithCommas(x):
    if type(x) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)


replace_patterns = [
	#( "\\", "\\textbackslash{}" ),
	( "£", "\\textsterling" ),
	( "#", "\\#" ),
	( "$", "\\$" ),
	( "%", "\\%" ),
	( "^", "\\^{}" ),
	#( "&", "\\&" ), # handled seperately, depending on in table or not...
	( "_", "\\_" ),
	#( "{", "\\{" ),
	#( "}", "\\}" ),
	( "~", "\\~{}" )
]

def escape_latex( text_str ):
	for pair in replace_patterns:
		text_str = text_str.replace( pair[0], pair[1] )
	return text_str

def escape_latex_filepath( text_str ):
	return text_str
	#for pair in replace_patterns_filepath:
	#	text_str = text_str.replace( pair[0], pair[1] )
	#return text_str

latex_open_wrapper = """
\\documentclass[8pt]{article}
\\usepackage{makecell}
\\usepackage{rotating}
\\usepackage{lscape}
\\usepackage{xcolor}
\\usepackage{longtable}
\\usepackage{geometry}
\\geometry{a4paper, %s, margin=1in}
\\usepackage{graphicx}
\\usepackage[hang,small,singlelinecheck=false]{caption}
\\usepackage{booktabs}
\\usepackage{threeparttable}
\\usepackage{threeparttablex}
\\newcommand{\\plus}{\\raisebox{.4\\height}{\\scalebox{.6}{+}}}

\\begin{document}
\\pagenumbering{gobble}
\\pagecolor{yellow!30}"""

latex_open = """
\\begin{table}
	\\centering
	\\begin{threeparttable}
		\\caption{[title]}
		\\begin{tabular}{ %s }
			\\toprule
			%s%s \\\\
			\\midrule
"""

latex_close = """
			\\bottomrule
		\\end{tabular}
		\\caption*{[caption]}
		\\label{...}
	\\end{threeparttable}
\\end{table}
"""

latex_open_longtable = """
%s
\\begin{ThreePartTable}
	\\setlength\\LTleft{0pt}
	\\setlength\\LTright{0pt}
	\\begin{longtable}{@{\\extracolsep{\\fill}}%s@{}}
	\\caption{[title]} \\\\ %% This linebreak needed in a longtable... !
	\\toprule
	%s%s \\\\
	\\midrule
"""

latex_close_longtable = """
	\\bottomrule
	\\caption*{[caption]}
	\\end{longtable}
\\end{ThreePartTable}
%s"""

latex_close_wrapper = """
\\end{document}
"""

list_open_wrapper = """
\\documentclass[8pt]{article}
\\usepackage{multicol}
\\usepackage{xcolor}

\\begin{document}
\\pagecolor{yellow!30}"""

list_open = """
\\begin{multicols}{%s}
	\\scriptsize
	\\begin{itemize}
"""

list_close = """
	\\end{itemize}
\\end{multicols}"""

list_close_wrapper = """
\\end{document}
"""


def is_float( variable ):
	return variable.replace(".","").replace(",","").isdigit()


def add_col( writeline, row, field_key, field_pattern ):
	insert_val = row[field_key]

	if field_pattern["format"] == "str":
		if insert_val:
			if "parish" in field_pattern["header"].lower():
				for pair in confdat.replace_parishes:
					insert_val = re.sub(r'\b%s\b' % pair[0], pair[1], insert_val)
			elif "ref" in field_pattern["header"].lower():
				if ".[" in insert_val:
					insert_val = insert_val.split(".[",1)[0]
				if insert_val.startswith( "Publ." ):
					insert_val = "\\textit{%s}" % ( insert_val.replace("Publ.","") )
				insert_val = insert_val.replace("Maps.","")
				insert_val = insert_val.replace("Manu.","")
			elif "colony" in field_pattern["header"].lower():
				for pair in confdat.replace_colonies:
					insert_val = re.sub(r'\b%s\b' % pair[0], pair[1], insert_val)
			else:
				for pair in confdat.replace_GBR:
					insert_val = re.sub(r'\b%s\b' % pair[0], pair[1], insert_val)

			insert_val = escape_latex( insert_val ).replace("&","\&")

	if field_pattern["format"] == "stg":
		if insert_val:
			if is_float( insert_val ):
				insert_val = format(float(insert_val), '.2f')
			else:
				insert_val = "--"
		else:
			insert_val = "--"

	if field_pattern["format"] == "longint":
		if insert_val:
			if is_float( insert_val ):
				if float(insert_val) < 1 and float(insert_val) > 0:
					insert_val = "\\textless 1"
				else:
					insert_val = intWithCommas( int(float(insert_val)) )
			if insert_val == "0":
				insert_val = "--"
		else:
			insert_val = "--"

	if field_pattern["format"] == "pct":
		if insert_val:
			if is_float( insert_val ):
				if float(insert_val) == 0.0:
					insert_val = "--"
				elif float(insert_val) < 0.1:
					insert_val = "\\textless 0.1"
				else:
					insert_val = str(round(float(insert_val), 1))
			else:
				insert_val = "--"
		else:
			insert_val = "--"

	if field_pattern["format"] == "pct_per_million":
		if is_float( insert_val ):
			insert_val = str(intWithCommas(int(float(insert_val) * 10000)))
			if insert_val == "0":
				insert_val = "--"
		else:
			insert_val = "--"

	if field_pattern["format"] == "diff":
		if insert_val:
			insert_val = round(float(insert_val),1)
			if insert_val == 0:
				insert_val = "--"
			elif insert_val == -100:
				insert_val = "--"
			elif insert_val > 0:
				insert_val = "\\textbf{\plus%s}" % str(insert_val)
			else:
				insert_val = str(insert_val)
		else:
			insert_val = "--"

	if field_pattern["format"] == "diff_mult":
		if insert_val:
			insert_val = round(float(insert_val)/100,1)
			if insert_val == 0:
				insert_val = "--"
			elif insert_val == -1.0:
				insert_val = "--"
			elif insert_val > 0:
				insert_val = "\\textbf{\plus%s}" % str(insert_val)
			else:
				insert_val = str(insert_val)
		else:
			insert_val = "--"

	writeline[field_key] = insert_val

	return writeline


import copy

def write_tex_tables( def_filepath ):
	esc_filepath = util.escape_filepath( def_filepath )

	os.system( "rm %s/^tex/^*.tex" % esc_filepath)
	os.system( "rm %s/^tex/^*.png" % esc_filepath)
	os.system( "rm %s/^tex/^SUMMARY/^*.tex" % esc_filepath)
	os.system( "rm %s/^tex/^SUMMARY/^*.png" % esc_filepath)
	os.system( "rm %s/^tex/^REGIONGROUPS/^*.tex" % esc_filepath)
	os.system( "rm %s/^tex/^REGIONGROUPS/^*.png" % esc_filepath)

	for root, dirs, files in os.walk( "%s/dat" % def_filepath ):
		for fname in files:
			if fname.endswith( ".tsv" ):

				filepath = "%s/%s" % ( root, fname )

				with open( filepath, "r" ) as r:
					tsv = csv.DictReader( r, delimiter="\t" )
					fieldnames = tsv.fieldnames
					if not tsv.fieldnames:
						continue # i.e. it's an empty file...

					# Replace with the correct labels... so can be sorted properly...
					new_tsv = []
					for row in tsv:
						if "ITEM" in row:
							if "parish" in filepath and not "regional" in filepath:
								for pair in confdat.replace_parishes:
									row["ITEM"] = re.sub(r'\b%s\b' % pair[0], pair[1], row["ITEM"])
							elif "colony" in filepath and not "regional" in filepath:
								for pair in confdat.replace_colonies:
									row["ITEM"] = re.sub(r'\b%s\b' % pair[0], pair[1], row["ITEM"])
							elif "projects" in filepath:
								if "," in row["ITEM"]:
									row["ITEM"] = row["ITEM"].split(",")[0]
								for pair in confdat.replace_projects:
									row["ITEM"] = str(row["ITEM"]).replace( pair[0], pair[1] )
							else:
								for pair in confdat.replace_GBR:
									row["ITEM"] = re.sub(r'\b%s\b' % pair[0], pair[1], row["ITEM"])
						new_tsv.append(row)

					tsv = new_tsv

					if ( "parish" in filepath or "colony" in filepath or "yearly" in filepath ) and "ITEM" in fieldnames:
						# Sort, except the first and last rows...
						#r.seek(0)
						tsv = sorted(tsv, key=operator.itemgetter("ITEM"))
						i = 0
						top_row = None
						tot_row = None
						for row in tsv:
							if row["ITEM"] == "TOTAL":
								tot_row = row
								tsv.pop(i)
							if row["ITEM"] == "ITEM":
								top_row = row
								tsv.pop(i)
							i += 1
						if tot_row:
							tsv = tsv + [tot_row]
						if top_row:
							tsv = [top_row] + tsv

					matched_patterns = []


					# find the patterns that match this file

					for row_pattern in patterns:

						key = row_pattern["file_pattern"]
						if "*" in key:
							els = key.split("*")
						else:
							els = [ key ]
						if all( x in filepath for x in els ):
							pattern_fields = row_pattern["fields"].keys()
							for field in pattern_fields:
								if field.startswith( "__" ): pattern_fields.remove( field )
							if all( x in fieldnames for x in pattern_fields ):
								matched_patterns.append( row_pattern )


					# for each matched pattern...

					for model_pattern in matched_patterns:

						print( "-----------------------------------------------------------------" )

						# grab the data from the file

						tmp_pattern = copy.deepcopy( model_pattern )
						tmp_pattern[ "writelines" ] = []

						for row in tsv:
							if "ITEM" in row:
								if row["ITEM"] == "TOTAL":
									tmp_pattern[ "writelines" ].append( "\\midrule\n" )

							writeline = OrderedDict()
							for key in model_pattern["fields"].keys():
								if key.startswith( "__" ):
									if key == "__INSERT_VAL_FIELDS__":
										substitute_fields = diff_fields
									elif key == "__THOLD_FIELDS__":
										substitute_fields = thold_fields
									elif key == "__DIFF_FIELDS__":
										substitute_fields = diff_fields
									elif key == "__PROB_FIELDS__":
										substitute_fields = prob_fields
									elif key == "__BASELINE_FIELDS__":
										substitute_fields = baseline_fields
									elif key == "__BASELINE+PROB+DIFF_FIELDS__":
										substitute_fields = baseline_prob_diff_fields
									elif key == "__BASELINE+ALLPROB+DIFF_FIELDS__":
										substitute_fields = baseline_full_prob_diff_fields

									if key in tmp_pattern["fields"]:
										del tmp_pattern["fields"][key] # may have already update this...
									for val_key, val_pattern in substitute_fields:
										if val_key in row.keys():
											writeline = add_col( writeline, row, val_key, val_pattern )
											tmp_pattern["fields"][ val_key ] = val_pattern
								else:
									writeline = add_col( writeline, row, key, model_pattern["fields"][key] )

							tmp_pattern[ "writelines" ].append( writeline )


						# write the data

						orientation = model_pattern["orientation"]
						if "suffix" in model_pattern:
							suffix = "." + model_pattern["suffix"]
						else:
							suffix = ""
						writepath = filepath.replace( "/dat", "/^tex" ) + "%s.tex" % suffix

						model_type = ""
						if "type" in model_pattern:
							model_type = model_pattern["type"]

						if model_type == "multicol":
							tex_body	= ""
							num_cols 	= model_pattern["num_cols"]

							tex_body 	+= list_open % ( num_cols )
							for line in tmp_pattern["writelines"]:
								tex_body += "\\item %s \n" % "".join( line.values() )
							tex_body 	+= list_close

							with open( writepath, "w" ) as w:
								w.write( tex_body )

							with open( writepath+".tmp", "w" ) as w:
								w.write( list_open_wrapper )
								w.write( tex_body + "\n"  )
								w.write( list_close_wrapper )
						else:
							justifications 	= []
							headers 		= []
							pre_headers 	= []

							is_multi	= False
							multi_i 	= 1
							prev_header = ""
							i 			= 0
							last_loop 	= len( tmp_pattern["fields"] )-1
							for k, vals in tmp_pattern["fields"].items():
								#print( vals )
								if "multicolheader" in vals:
									if vals["multicolheader"] == prev_header:
										multi_i += 1
									if ( vals["multicolheader"] != prev_header and prev_header != "" ) or i == last_loop:
										if i == last_loop: prev_header = vals["multicolheader"]
										pre_headers.append( "\\multicolumn{%s}{c}{%s}" % ( multi_i, prev_header.replace("\\\\","").replace("  "," ") ) )
										multi_i = 1 # reset
									prev_header = vals["multicolheader"]
									is_multi = True
								else:
									pre_headers.append( " " )
								i+=1
							if not is_multi:
								pre_headers = []

							tex_body	= ""
							table_type  = "tabular"
							if "suffix" in model_pattern:
								if "appendix" in model_pattern["suffix"]:
									table_type = "longtable"

							for k, vals in tmp_pattern["fields"].items():
								just_txt = ""
								if "pre_hline" in vals:
									if vals["pre_hline"] == True:
										just_txt = " | "
								just_txt += vals["justification"]
								justifications.append( just_txt )
								#headers.append( vals["header"] )
								if table_type == "longtable":
									justification = vals["justification"]
									if justification.startswith("p"):
										justification = "l"
									headers.append( "\\thead[%s]{%s}" % ( justification, vals["header"] ) )
									#headers.append( "\\multicolumn{1}{%s}{\\parbox{%s}}" % ( vals["justification"], vals["header"] ) )
								else:
									headers.append( "\\thead[%s]{%s}" % ( vals["justification"], vals["header"] ) )
							justification_txt	= " ".join( map(str, justifications ) )
							pre_headers_txt 	= " & ".join( map(str, pre_headers ) )
							headers_txt 		= " & ".join( map(str, headers ) )
							if pre_headers_txt:
								pre_headers_txt += " \\\\ \n"

							if orientation == "landscape":
								#begin_orientation 	= "\\begin{landscape} \\tiny"
								#end_orientation 	= "\\end{landscape}"
								begin_orientation 	= "" #"""\\tiny \\renewcommand\\theadfont{\\tiny}"""
								end_orientation 	= ""
							else:
								begin_orientation = end_orientation = ""

							if table_type == "longtable":
								tex_body 	+= latex_open_longtable % ( begin_orientation, justification_txt, pre_headers_txt, headers_txt )
							else:
								tex_body 	+= latex_open % ( justification_txt, pre_headers_txt, headers_txt )

							for line in tmp_pattern["writelines"]:
								if isinstance(line, basestring):
									tex_body += line
								else:
									tex_body += " & ".join( map(str, line.values()) ) + " \\\\\n"

							if table_type == "longtable":
								tex_body 	+= latex_close_longtable % ( end_orientation )
							else:
								tex_body 	+= latex_close

							with open( writepath, "w" ) as w:
								w.write( tex_body )

							with open( writepath+".tmp", "w" ) as w:
								w.write( latex_open_wrapper % ( orientation ) )
								w.write( tex_body + "\n"  )
								w.write( latex_close_wrapper )

	for root, dirs, files in os.walk( "%s/^tex" % def_filepath ):
		for fname in files:
			if fname.endswith(".tex"):
				filepath = "%s/%s" % ( root, fname )
				esc_filepath = util.escape_filepath( filepath )
				esc_dirpath = util.escape_filepath( os.path.dirname( filepath ) )
				print( filepath )

				cmd = "pdflatex -output-directory %s %s" % ( esc_dirpath, esc_filepath+".tmp" )
				print( cmd )
				os.system( cmd )

				cmd = "convert -density 300 %s.pdf -quality 90 -trim %s.png" % ( esc_filepath, esc_filepath )
				os.system( cmd )

				os.system( "rm %s" % ( esc_filepath+".tmp" ) )
				os.system( "rm %s" % ( esc_filepath+".log" ) )
				os.system( "rm %s" % ( esc_filepath+".aux" ) )
				os.system( "rm %s" % ( esc_filepath+".pdf" ) )
