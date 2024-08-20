#!/usr/bin/python

## CONVERT WELL-FORMATTED TRANSCRIPTION TEXT TO TSV DATA, USING LOCAL PATTERN RULES
## 2024-08-09: Updated to a new (improved/refined) mark down syntax

import sys
import re
import itertools
from subprocess import call
import operator
import copy
import os
import pandas

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.all as util
import ontologize.modules.data_transformation.all as prep



run_dir = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/01.SCOTLAND"

if len(sys.argv) > 1:
	run_dir = sys.argv[1]


def split(txt, seps):
    default_sep = seps[0]

    # we skip seps[0] because that's the default seperator
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]


def is_pattern_line( line ):
	return line.startswith("###\\t") and not line.startswith("###\\tEND")# or line.startswith("###+\\t") or line.startswith("###-\\t")


def is_data_line( line ):
	if line.startswith( "#" ): return False
	if line.startswith( ">" ): return False
	if line.startswith( "[...]" ): return False
	if line.startswith( "![" ): return False
	if line.startswith( "[/]" ): return False
	return True


def parse_patterns( collection_root, trx_root ):
	for root, dirs, files in os.walk( trx_root, topdown=True ):
		for fname in files:
			if fname.endswith(".txt") and not fname.startswith("^"):
				filepath = "%s/%s" % (root, fname)
				with open( filepath, "r" ) as r:

					print( "----------------------" )
					print( filepath )

					patterns 			= []
					partial_lines		= []
					src_vals 			= {}
					scope_vals			= {}
					global_vals			= {}
					hard_vals			= {}

					src_ref 			= prep.get_ref_from_filepath( filepath.rstrip() )
					src_vals["SRC_REF"] = src_ref

					src_date 		= ""
					src_type 		= ""

					line_num = 0
					last_sep_linenum = 0

					lines = r.readlines()
					for line in lines:
						line_num += 1

						src_vals 				= prep.mkd.parse_src_vals( src_vals, line )
						scope_vals, global_vals = prep.mkd.parse_scope_vals( scope_vals, global_vals, line )

						if is_pattern_line( line ):
							last_sep_linenum = line_num
							pattern = list(filter(None, split( line.strip(), "\\t" )[2:]))
							#print( line )
							#print( pattern )


						if line.startswith("###\\tEND"):
							write_dicts		= []
							last_line_vals 	= None

							for l in range(last_sep_linenum, line_num): # loop back over the data area...

								if is_data_line( lines[l] ):
									lines[l] = lines[l].replace( "\t\t", "\t" ).replace( "\t\t", "\t" ).replace( "\t\t", "\t" ).replace( "\t\t", "\t" ).replace( "\t\t", "\t" )
									#lines[l] 		= lines[l].replace( "[\\t]", "\t" )
									#lines[l] 		= lines[l].replace( "\t\n", "\t.\n" )
									line_vals  		= re.split("\t",lines[l].strip())
									#print( line_vals )

									write_dict = {}
									write_dict = util.merge_two_dicts( scope_vals, global_vals )

									for pl in partial_lines:
										write_dict = util.merge_two_dicts( write_dict, pl )

									for k, pattern_val in enumerate( pattern ):
										try:
											val = line_vals[k]
										except IndexError:
											val = ""

										val=val.strip()

										if val == "Ditto" or val == "Do" or val == "do" or val == "ditto" or val == '\"':
											try:
												val = last_write_line[pattern_val] # get from last line...
											except KeyError:
												val = "."

										write_dict[pattern_val] = val

									write_dict['SRC_LINE'] = l
									write_dicts.append( copy.copy(write_dict) )
									last_write_line = write_dict


							# write to file after each data section...

							if write_dicts:

								dat_dir = (root.replace("02_TXT","03_^DAT"))

								if not os.path.isdir(dat_dir):
									os.mkdir(dat_dir)

								writepath = "%s/%s.[%s].tsv" % (dat_dir, fname, last_sep_linenum)

								l = []

								for dct in write_dicts:
									output = util.merge_two_dicts( dct, src_vals )
									l.append( pandas.DataFrame(output, index=[0]) )

								tmp = pandas.concat(l)

								tmp.to_csv( prep.insert_caret( writepath ), sep="\t" )

							patterns 			= {}
							partial_lines 		= []
							last_sep_linenum 	= line_num
							scope_vals = {} # 2024-08-09: ???


for root, dirs, files in os.walk( run_dir, topdown=True ):
	for folder in dirs:
		if "02_TXT" in folder or "02_MKD" in folder or "02_NOTES" in folder or "02A_TXT" in folder:
			collection_root = root
			trx_root = root + "/" + folder
			parse_patterns( collection_root, trx_root )
