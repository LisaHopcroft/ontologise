#!/usr/bin/python

## CONVERT TEXTUAL ENCODINGS TO TSV DATA
import sys
import re
import os
import pandas as pd
import operator
from subprocess import call

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.all as util
import ontologize.modules.data_transformation.all as prep


run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch/359031, Cairn of Lochwinyoch matters, 1827-37"

if len(sys.argv) == 2:
	run_dir = sys.argv[1]

is_override  = True
is_debugging = False
is_flush     = False
debug_file = "..."#74, --- WILSON of Bowfield"


total_data_points = 0


def requires_refresh( filename, writepath, tbl_name ):
	if is_override:
		return True

	writepath = "%s.%s.tsv" % ( writepath, tbl_name )
	if os.path.exists( writepath ):
		if os.path.getmtime( writepath ) > os.path.getmtime( filename ):
			#print( "***NO NEED TO UPDATE***" )
			return False

	return True


def parse_TRX_directories( start_point ):

	if is_flush:
		for root, dirs, files in os.walk( start_point, topdown=True ):
			for fname in files:
				fpath = "%s/%s" % ( root, fname )
				if fname.endswith(".tsv") and fname.startswith("^") and "03_^DAT" in root:
					os.remove( fpath )

	for root, dirs, files in os.walk( start_point, topdown=True ):
		for folder in dirs:
			if "02_TXT" in folder or "02_MKD" in folder or "02_NOTES" in folder or "02A_TXT" in folder and not "/@/" in root:
				collection_root = root
				trx_root = root + "/" + folder
				parse_microformats( collection_root, trx_root )


def get_src_attribute( line ):
	return line.replace("#","").split(":",1)[1].strip()


mod_keys = {
	'AT':	"place_id",
}


def populate_dict_vals( empty_dict, vals_dict, line_num ):
	for key, val in vals_dict.items():
		if key in mod_keys.keys():
			mod_key = mod_keys[key]
		else:
			mod_key = key

		if mod_key in empty_dict:
			empty_dict[mod_key] = vals_dict[key]
		#else:
		#	print( "[%s]: %s key not in %s db table..." % ( line_num, mod_key, vals_dict["action"] ) )

	return empty_dict


def add_date_data( dictobj, attr_val ):
	date_dat = prep.mkd.convert_txtdate_to_DAT( attr_val )
	dictobj["date1_y"] = date_dat["date1_y"]
	dictobj["date1_m"] = date_dat["date1_m"]
	dictobj["date1_d"] = date_dat["date1_d"]
	dictobj["date1_rel"]  = date_dat["date1_rel"]
	dictobj["date1_spec"] = date_dat["date1_spec"]
	dictobj["date2_y"] = date_dat["date2_y"]
	dictobj["date2_m"] = date_dat["date2_m"]
	dictobj["date2_d"] = date_dat["date2_d"]
	dictobj["date2_rel"]  = date_dat["date2_rel"]
	dictobj["date2_spec"] = date_dat["date2_spec"]
	return dictobj


def populate_peopla_record( context_vals, line_num, filepath, tagged_vals ):
	PEOPLA_dict = prep.get_RDB_table_as_dict( "peopla" )
	PEOPLA_dict = populate_dict_vals( PEOPLA_dict, context_vals, line_num )
	PEOPLA_dict["src_ref"] 		= prep.get_short_filepath( filepath )
	PEOPLA_dict["src_linenum"] 	= line_num					# } FOREIGN KEY
	PEOPLA_dict["src_filepath"] = filepath.rstrip()			# } FOREIGN KEY
	for attr_key, attr_val in tagged_vals.items():
		if attr_key == ":" or attr_key == "date" or attr_key == "<" or attr_key == ">":
			PEOPLA_dict = add_date_data( PEOPLA_dict, attr_val.replace("~","") )
			if "~" in attr_val:
				PEOPLA_dict["date1_spec"] = "abt"
		if attr_key == "aged":
			PEOPLA_dict["pers_aged"] = attr_val

		if attr_key == ":":
			if PEOPLA_dict["date1_rel"] == "":
				PEOPLA_dict["date1_rel"] = "on"
		if attr_key == "<":
			PEOPLA_dict["date1_rel"] = "bef."
		if attr_key == ">":
			PEOPLA_dict["date1_rel"] = "aft."

	return PEOPLA_dict


def add_block( outputs, actor, action, places, vals, context_vals, line_num, filepath, actions ):

	if places:
		for i, place in enumerate( places ): # save a PEOPLA, for every place

			context_vals["pers_id"] 		= actor["pers_id"]
			context_vals["pers_id_context"] = actor["pers_id_context"]
			context_vals["pers_id_global"]  = actor["pers_id_global"]
			context_vals["action"] 			= action
			context_vals["place_id"] 		= place

			if not action == "AT" or len( actions )==1:

				PEOPLA_dict = populate_peopla_record( context_vals, line_num, filepath, vals )

				if "PEOPLA" in outputs:
					outputs[ "PEOPLA" ].append( PEOPLA_dict )
				else:
					outputs[ "PEOPLA" ] = [ PEOPLA_dict ]

			if i == 0: # save MF, only linking to first PEOPLA
				if not action == "AT":
					MF_dict = prep.get_RDB_table_as_dict( "MF_" + action )
					if MF_dict:
						MF_dict	= populate_dict_vals( MF_dict, util.merge_two_dicts( vals, context_vals ), line_num )
						MF_dict["src_linenum"] 	= line_num				# } FOREIGN KEY
						MF_dict["src_filepath"] = filepath.rstrip()		# } FOREIGN KEY
						if action in outputs:
							outputs[ action ].append( MF_dict )
						else:
							outputs[ action ] = [ MF_dict ]

	else:

		# shorthand transformations

		#if action == "DECD":
		#	action = "DEATH"
		#	is_bef = True

		context_vals["pers_id"] 			= actor["pers_id"]
		context_vals["pers_id_context"] 	= actor["pers_id_context"]
		context_vals["pers_id_global"] 	    = actor["pers_id_global"]
		context_vals["action"] 				= action

		PEOPLA_dict = populate_peopla_record( context_vals, line_num, filepath, vals )

		if "PEOPLA" in outputs:
			outputs[ "PEOPLA" ].append( PEOPLA_dict )
		else:
			outputs[ "PEOPLA" ] = [ PEOPLA_dict ]

		# shorthand modifications

		#if is_bef:  PEOPLA_dict["date1_rel"] = "bef."

		if not action == "AT":
			MF_dict = prep.get_RDB_table_as_dict( "MF_" + action )
			if MF_dict:
				MF_dict	= populate_dict_vals( MF_dict, util.merge_two_dicts( vals, context_vals ), line_num )
				MF_dict["src_linenum"] 	= line_num					# } FOREIGN KEY
				MF_dict["src_filepath"] = filepath.rstrip()			# } FOREIGN KEY
				if action in outputs:
					outputs[ action ].append( MF_dict )
				else:
					outputs[ action ] = [ MF_dict ]

	return outputs


def add_tagged_block( outputs, actors, actions, places, vals, context_vals, line_num, filepath, reactors ):
	# shorthand modifiers
	is_bef = False

	for actor in actors:
		for action in actions:
			outputs = add_block( outputs, actor, action, places, vals, context_vals, line_num, filepath, actions )

	for actor in reactors:
		for action in actions:
			outputs = add_block( outputs, actor, "RE-"+action, places, vals, context_vals, line_num, filepath, actions )

	return outputs


def is_mf_line( line ):
	return line.startswith("###\t") or line.startswith("### ")


def is_pers_id_line( line ):
	return line.startswith("###\t[") or line.startswith("### [") or line.startswith("###\t:[") or line.startswith("### :[") or line.startswith("###\t;[") or line.startswith("### ;[") or line.startswith("### w/[") or line.startswith("###\tw/[") or line.startswith("### vs[") or line.startswith("###\tvs[")


def is_pers_id_line_new( line ):
	return is_pers_id_line(line) and not "w/[" in line and not "vs[" in line


def is_relationship_line( line ):
	return is_mf_line( line ) and ( "\t*" in line and "*\n" in line )


def is_place_id_line( line ):
	return ( line.startswith("###\t\t") or line.startswith( "###\t(\t" ) or line.startswith( "###\t(>\t" ) ) and ( ( "@[" in line or "AT[" in line ) and "[" in line and "]" in line )


def is_action_line( line ):
	return ( line.startswith("###\t\t") or line.startswith("###\t>\t") or line.startswith("###\t(\t") or line.startswith("###\t(>\t") ) and not "[" in line and not "]" in line and not "^" in line and not "\t\t\t" in line


def save_tag_block( outputs, actors, actions, places, vals, context_vals, line_num, filepath, shortcut_id, shortcuts, is_aside, reactors ):
	if is_aside:
		if reactors:
			actors = reactors[-1:]
		else:
			actors = actors[-1:]

	if shortcut_id: # i.e. setting up a user-defined shortcut
		shortcuts[shortcut_id] = ( actions, places, vals )
	else:
		outputs = add_tagged_block( outputs, actors, actions, places, vals, context_vals, line_num, filepath, reactors )


def is_end_of_file( line ):
	return line == ""


def is_time_to_save( line, prev_tab_count, scope, current_scope ):
	return line.count("\t") < prev_tab_count or scope > current_scope or ( line.count("\t")==prev_tab_count and ( is_pers_id_line_new( line ) or is_relationship_line(line) ) or "\tw/[" in line ) # is_end_of_file( line ) # didn't seem to work, so added another line at the end instead of this


def is_shortcut_definition_line( line ):
	return( line.startswith( "###\t^" ) or line.startswith( "### ^" ) ) and line.strip().endswith( ":" )


current_scope = 0


def add_relationships( output_relationships, relationships, scope_actors, pers_id, pers_id_context, pers_id_global, filepath, line_num, src_pp, src_pp_original, scope, is_aside ):

	if is_aside:
		recip_actors = scope_actors[scope-1][-1:]
	else:
		recip_actors = scope_actors[scope-1]

	for rel_val in relationships:
		for pers2 in recip_actors:
			output_relationships.append( [
				prep.get_short_filepath( filepath ),
				src_pp,
				src_pp_original,
				str(line_num),
				"",
				pers_id,
				pers_id_context,
				pers_id_global,
				rel_val,
				pers2["pers_id"],
				pers2["pers_id_context"],
				pers2["pers_id_global"] ] )
	return output_relationships


def parse_microformats( collection_root, trx_root ):
	for root, dirs, files in os.walk( trx_root, topdown=True ):
		for fname in sorted( files ):
			if is_debugging and not debug_file in fname: continue # DEBUGGING FILTER
			if fname.endswith(".txt") and not fname.startswith("^") and not "02_TXT/@" in root:

				outputs 				= {}
				output_relationships 	= []
				shortcuts 				= {}
				filepath 				= root + "/" + fname
				shortcut_id 			= None

				if is_debugging: print( filepath )

				#with open(filepath, 'rU') as r: # python2.7
				with open(filepath, 'r') as r:

					src_vals 		= {}
					scope_vals		= {}
					global_vals		= {}

					scope_actors    = {}
					tagged_actors 	= []
					tagged_places  	= []
					tagged_actions  = []
					tagged_reactors = []
					tagged_vals		= {}

					prev_tab_count  = 0
					current_scope   = 0

					relationships   = []
					shortcut_id 	= None

					src_ref 			= prep.get_short_filepath( filepath.rstrip() )
					src_vals["src_ref"] = src_ref

					src_date 			= ""
					src_type 			= ""
					src_pp				= ""
					src_pp_original		= ""

					line_num 			= 0
					last_sep_linenum 	= 0
					is_aside 			= False

					lines = r.readlines()

					error_msgs			= []

					for line in lines:

						line_num += 1
						if line.endswith( " [<-]" ) or line.endswith( " [->]" ): line = line[:-5]

						if is_debugging: print( line_num )

						# --------------------------------------------------------------------------- #
						# Context vals
						# --------------------------------------------------------------------------- #

						src_vals 					= prep.mkd.parse_src_vals( src_vals, line )

						scope_vals, global_vals 	= prep.mkd.parse_scope_vals( scope_vals, global_vals, line )

						if line.startswith( "@" ):
							scope_vals["TIME"] 	= line.replace("@","").strip()


						if line.startswith("===============") or line.startswith("-----------------"):
							last_sep_linenum = line_num


						if line.startswith("==============="):
							scope_vals = {}


						if line.startswith( "##" ) and not line.startswith( "###" ) and ":\t" in line:
							key = line.split( ":\t" )[0].replace("#","")
							val = line.split( ":\t" )[1]
							if key == "Fm@": key = "SRC_at"
							global_vals[key] = val


						context_vals = util.merge_two_dicts( global_vals, scope_vals )


						# --------------------------------------------------------------------------- #
						# PEOPLA shortcut set-up tags
						# --------------------------------------------------------------------------- #

						if is_shortcut_definition_line( line ):
							key = line.strip().split( "###\t^", 1 )[1].replace(":","")
							shortcut_id = key

						if is_debugging and shortcut_id: print( "Setting up shortcut %s" % shortcut_id )


						# --------------------------------------------------------------------------- #
						# PEOPLA tags
						# --------------------------------------------------------------------------- #

						if not prep.mkd.is_mf_tag_line( line ):

							continue # ignore non-tag lines

						else:

							line = line.replace( "+\t", "" ) # just ignore these... purely aesthetic

							# ------------------------------------------------------------------------- #
							# save and reset values (if needed)
							# ------------------------------------------------------------------------- #

							scope = prep.mkd.get_scope_from_line( line ) # ">"
							if is_debugging: print( scope )

							if is_time_to_save( line, prev_tab_count, scope, current_scope ):
								if is_debugging: print( "- time to save" )

								# (1) save old tag data

								if is_debugging:
									print( tagged_actors )
									print( tagged_actions )
									print( tagged_places )
									print( tagged_reactors )
									print( scope_actors )

								if tagged_actions:
									save_tag_block( outputs, tagged_actors, tagged_actions, tagged_places, tagged_vals, context_vals, line_num, filepath, shortcut_id, shortcuts, is_aside, tagged_reactors )
								is_aside = False
								global total_data_points
								total_data_points += len( tagged_actions )

								# (2) blank current tag data

								if is_relationship_line( line ):
									tagged_actors   = []
									tagged_reactors = []

								if is_pers_id_line_new( line ):
									tagged_actors   = []
									tagged_reactors = []

								tagged_actions  = []
								tagged_places   = []
								tagged_vals 	= {}
								relationships   = []


							prev_tab_count = line.count("\t")
							current_scope = scope

							if not is_shortcut_definition_line: shortcut_id = None


							# ------------------------------------------------------------------------- #
							# read values
							# ------------------------------------------------------------------------- #

							original_line = line
							if "\t(\t" in line or "\t(>\t" in line: is_aside = True
							else: is_aside = False
							line = line.replace( "(>\t", "" )
							line = line.replace( ">\t", "" )

							if is_relationship_line( line ): # relationship line

								relationships.append( prep.mkd.get_val_from_relationship_line( line, context_vals ) )

							elif is_pers_id_line( line ): # person line

								shortcut_id = None

								val = prep.mkd.get_val_from_mf_line( line, context_vals )

								# shorthand
								if val.lower() == "auth":
									if "fm" in context_vals:
										val = context_vals.get("fm")
									if "tttr" in context_vals:
										val = context_vals.get("tttr")
								elif val.lower() == "recip":
									val = context_vals.get("to")

								if not "]" in line:
									error_msgs.append( "- WARNING: Malformed person line [line %s]" % line_num )
									continue

								context_val 	= prep.mkd.get_contextval_from_mf_line( line, context_vals, line_num )
								pers_id_global  = prep.mkd.get_globalval_from_mf_line( line, context_vals, line_num )
								if "\tw/[" in line or " w/[" in line:
									tagged_actors += [ { "pers_id": val, "pers_id_context": context_val, "pers_id_global": pers_id_global } ]
								elif "\tvs[" in line or " vs[" in line:
									tagged_reactors += [ { "pers_id": val, "pers_id_context": context_val, "pers_id_global": pers_id_global } ]
								else:
									tagged_actors = [ { "pers_id": val, "pers_id_context": context_val, "pers_id_global": pers_id_global } ]
								scope_actors[scope] = tagged_actors
								if is_debugging: print( tagged_actors )

								# -------------------- save relationships ------------------- #

								if relationships:

									pers_id 		= prep.mkd.get_val_from_mf_line( line, context_vals )
									pers_id_context = prep.mkd.get_contextval_from_mf_line( line, context_vals, line_num )
									pers_id_global  = prep.mkd.get_globalval_from_mf_line( line, context_vals, line_num )

									if not scope-1 in scope_actors:
										error_msgs.append( "- WARNING: Someone on the receiving end of relationship, without a sender [line %s]" % line_num )
										continue

									output_relationship = add_relationships( output_relationships, relationships, scope_actors, pers_id, pers_id_context, pers_id_global, filepath, line_num, src_pp, src_pp_original, scope, is_aside )

									relationships   = [] # TODO: maybe shouldn't do this, could be multiple people on receiving end of a relationship ??

								# ------------------------------------------------------------ #


							elif is_action_line( line ): # hit an action line
								val = prep.mkd.get_val_from_action_line( line )
								if is_debugging: print( "action line" )
								tagged_places = []
								tagged_actions.append( val )
								if scope_actors:
									tagged_actors = scope_actors[scope] # set the tagged_actors to the scope corresponding to this action

							elif is_place_id_line( line ): # hit a place line
								val = prep.mkd.get_val_from_mf_line( line, context_vals )
								tagged_places.append( val )

							else: # hit a normal key/value line
								# shorthand
								if "INF" in line:
									tagged_vals["is_inf"] = True

								if "YNG" in line:
									tagged_vals["is_yng"] = True

								if "UNM" in line:
									tagged_vals["is_unm"] = True

								if "[" in line and "]" in line:
									key = prep.mkd.get_key_from_mf_line( line )
									val = prep.mkd.get_val_from_mf_line( line, context_vals )
									if "~" in line:
										val+="~"
									tagged_vals[key] = val


							# shorthand

							if line.strip().endswith( "*" ) and not is_relationship_line( line ): # shortcut for "AT src_place AT src_date"...
								if "SRC_at" in context_vals: tagged_places = [ context_vals["SRC_at"] ]
								tagged_actions = [ "AT" ]

								outputs = add_tagged_block( outputs, tagged_actors, tagged_actions, tagged_places, tagged_vals, context_vals, line_num, filepath, tagged_reactors )

								tagged_places   = []
								tagged_actions  = []
								tagged_reactors = []
								tagged_vals 	= {}


							# shortcuts

							if line.strip().endswith( "^1" ): # change to match against any digit
								key = line.rsplit("^",1)[1].strip()
								if key in shortcuts:
									shortcut_actions, shortcut_places, shortcut_vals = shortcuts[str(key)]
									outputs = add_tagged_block( outputs, tagged_actors, shortcut_actions, shortcut_places, shortcut_vals, context_vals, line_num, filepath, tagged_reactors )
								else:
									error_msgs.append( "WARNING: Shorcut %s not defined [line %s]" % ( key, line_num ) )
									error_msgs.append( shortcuts )

					# end of file
					save_tag_block( outputs, tagged_actors, tagged_actions, tagged_places, tagged_vals, context_vals, line_num, filepath, shortcut_id, shortcuts, is_aside, tagged_reactors )

					if error_msgs and is_debugging:
						print( "-----------------------------------------------------" )
						print( filepath )
						for msg in error_msgs:
							print( msg )

				# --------------------------------------------------------------------------- #
				# WRITE PER FILE
				# --------------------------------------------------------------------------- #

				writepath = filepath.replace( "02_MKD", "03_^DAT" ).replace( "02_TXT", "03_^DAT" ).replace( "02_NOTES", "03_^DAT" )
				writepath = prep.insert_caret( writepath )

				if not os.path.exists( writepath.rsplit("/",1)[0] ):
					if not os.path.exists( writepath.rsplit("/",2)[0] ): # go back two directories ...
						os.mkdir( writepath.rsplit("/",2)[0] )
					os.mkdir( writepath.rsplit("/",1)[0] )

				for key, vals in outputs.items():
					if vals: # and requires_refresh( filepath, writepath, key ):
						df = pd.DataFrame( vals )
						df.to_csv( writepath + ".%s.tsv" % key, sep='\t', index=False )

					if key == "PEOPLA":
						pass
						# do something panda-y to add spouse relationships to PEO_REL for all marriages ... (Lisa? Pls. Thx.)
						# add births if deaths and age given
						# add death dates if births and age-of-death given...

				with open( writepath + ".PEO_REL.tsv", "w" ) as w:
					w.write( "\t".join( [
						"src_ref",
						"src_pp",
						"src_pp_original",
						"src_linenum",
						"src_linenum_original",
						"pers1_id",
						"pers1_id_context",
						"pers1_id_global",
						"rel",
						"pers2_id",
						"pers2_id_context",
						"pers2_id_global"] ) + "\n" )
					for out_rel in output_relationships:
						w.write( "\t".join( out_rel ) + "\n" ) # SHOULDN'T BE HARDWRITING LIKE THIS, SHOULD BE LOOKING UP TABLE AND POPULATING VALUES GIVEN KEYS


parse_TRX_directories( run_dir )


print( "Total data points: {:,}".format( total_data_points ) )
