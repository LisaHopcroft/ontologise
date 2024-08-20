#!/usr/bin/python
import sys
import re
import os
from subprocess import call
import operator
import glob

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.data_transformation.all as prep
import ontologize.modules.util.all as util
import ontologize.modules.util.confdat as confdat


run_dir = confdat.academia_root

if len(sys.argv) == 2:
	run_dir = sys.argv[1]

is_override = False


def requires_refresh( filename, writepath, tbl_name ):
	if is_override:
		return True

	writepath = "%s.%s.tsv" % ( writepath, tbl_name )
	if os.path.exists( writepath ):
		if os.path.getmtime( writepath ) > os.path.getmtime( filename ):
			print( "***NO NEED TO UPDATE***" )
			return False

	return True

def find_between_r( s, first, last ):
	try:
		start 	= s.index( first ) + len( first )
		end 	= s.rindex( last, start )
		return s[start:end]
	except ValueError:
		return ""

for root, dirs, files in os.walk( run_dir ):
	for dirname in dirs:
		if dirname == "02_TREE":
			for filepath in glob.glob( "%s/%s/*" % ( root, dirname ) ):
				PEOPLA_dat = []

				with open( filepath, "r" ) as r:
					open_line 	= False
					close_line	= False
					name		= ""
					ancestor_names	= {}
					i = 0
					for line in r.readlines():
						i += 1
						if line.startswith( "~~~~~~~~~~~~~~~" ):
							if not open_line:
								open_line = True
							else:
								close_line = True
						else:
							if open_line and not close_line:
								parent_name = ""

								num_tabs = len( line ) - len( line.lstrip('\t') )
								line = line.strip().replace("\t","")
								if num_tabs-1 in ancestor_names.keys():
									parent_name = ancestor_names[num_tabs-1]

								if line.lstrip('0123456789.[]+ ').startswith( "b." ):
									born_at = line #todo...
								elif line.lstrip('0123456789.[]+ ').startswith( "d." ):
									died_at = find_between_r( line, "*", "*" )
									if died_at:
										if num_tabs in ancestor_names.keys():
											pers_name = ancestor_names[num_tabs]

											if died_at:
												PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
												PEOPLA_dict["src_ref"] 		= src_ref
												PEOPLA_dict["pers_id"] 		= pers_name
												PEOPLA_dict["place_id"] 	= line
												PEOPLA_dict["action"] 		= "DIED"
												PEOPLA_dict["src_filepath"] = filepath.rstrip()
												PEOPLA_dict["src_type"] 	= "TREE"
												PEOPLA_dict["src_linenum"] 	= i
												PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
												PEOPLA_dat.append( PEOPLA_dict )
								elif line.lstrip('0123456789.[]+ ').startswith( "m" ):
									spouse 	= line #todo...
									date 	= find_between_r( line, "(", ")" )
								else:
									born_in		= ""
									died_in		= ""
									father 		= ""
									name 		= line.strip().lstrip('0123456789.[]+ ').split( " '" )[0].split( " [" )[0].split( " (" )[0].split( " *" )[0]
									place 		= find_between_r( line, "'", "'" )
									at			= find_between_r( line, "*", "*" ).strip("*")
									lifedates 	= find_between_r( line, "[", "]" ).strip("c.a")
									src_ref		= prep.get_ref_from_filepath( filepath.rstrip() )
									if "-" in lifedates:
										born_in = lifedates.split( "-" )[0]
										died_in = lifedates.split( "-" )[1]
										if len( died_in ) == 2:
											died_in = born_in[:2] + died_in

									if not "," in name:
										modifier = ""
										if name.startswith( "--" ):
											modifier = "--"
										name = "%s%s, %s" % ( modifier, parent_name.split(",")[0], name.replace("--","") )

									'''if "*" in line:
										print "----------------------------------"
										print "Line: %s" % line
										print "Name: %s" % name
										print "Parent: %s" % parent_name
										print "Place: %s" % place
										print "Born in: %s" % born_in
										print "Died in: %s" % died_in
										print "At: %s" % at
										print "Father: %s" % father
										print "Srcref: %s" % src_ref
										print "Filepath: %s" % filepath'''

									if born_in:
										PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
										PEOPLA_dict["src_ref"] 		= src_ref
										PEOPLA_dict["pers_id"] 		= name
										PEOPLA_dict["pers_id_context"] = i
										PEOPLA_dict["action"] 		= "BORN"
										PEOPLA_dict["y1"] 			= born_in
										PEOPLA_dict["src_filepath"] = filepath.rstrip()
										PEOPLA_dict["src_type"] 	= "TREE"
										PEOPLA_dict["src_linenum"] 	= i
										PEOPLA_dat.append( PEOPLA_dict )

									if died_in:
										PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
										PEOPLA_dict["src_ref"] 		= src_ref
										PEOPLA_dict["pers_id"] 		= name
										PEOPLA_dict["pers_id_context"] = i
										PEOPLA_dict["action"] 		= "DIED"
										PEOPLA_dict["y1"] 			= died_in
										PEOPLA_dict["src_filepath"] = filepath.rstrip()
										PEOPLA_dict["src_type"] 	= "TREE"
										PEOPLA_dict["src_linenum"] 	= i
										PEOPLA_dat.append( PEOPLA_dict )

									if at:
										PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
										PEOPLA_dict["src_ref"] 		= src_ref
										PEOPLA_dict["pers_id"] 		= name
										PEOPLA_dict["pers_id_context"] = i
										PEOPLA_dict["place_id"] 	= at
										PEOPLA_dict["action"] 		= "AT"
										PEOPLA_dict["y1"] 			= died_in
										PEOPLA_dict["src_filepath"] = filepath.rstrip()
										PEOPLA_dict["src_type"] 	= "TREE"
										PEOPLA_dict["src_linenum"] 	= i
										PEOPLA_dict = prep.mkd.update_place_vals( PEOPLA_dict )
										PEOPLA_dat.append( PEOPLA_dict )

								# todo: model father...

								ancestor_names[num_tabs] = "%s {%s}" % ( name, i )


				writepath = filepath.replace( "02_TREE/", "03_^DAT/^" )
				if PEOPLA_dat and requires_refresh( filepath, writepath, "PEOPLA" ):
					util.write_listdict_to_file( writepath + ".PEOPLA.tsv", PEOPLA_dat )
