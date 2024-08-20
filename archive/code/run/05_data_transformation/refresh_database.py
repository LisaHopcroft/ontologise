#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.data_transformation.all as dp
import ontologize.modules.util.confdat as confdat
from ontologize.modules.util.all import *
import pexpect


run_dir = confdat.academia_root


def gather_DAT( DATname, single_univ="" ):
	# NOTE: (1) Changed to pandas due to performance problem... still slow though...
	# NOTE: (2) Changed to piping on the command line... FASTER!!!

	DAT_path = confdat.DB_dir + "/01_TSV/^%s.tsv" % DATname
	os.system( "rm %s" % DAT_path )

	print( "Gathering %s..." % DATname )
	# gather DAT files...
	ALL_dat = None
	is_a_dat = False
	for root, dirs, files in os.walk( run_dir, topdown=True ):
		for fname in files:
			if " [AIC]" in root and "[SLAVES]" in fname:
				print( "- Skipping %s/%s due to performance problems" % ( root, fname ) )
				continue # tmp hack to avoid adding all the slave registers...
			if single_univ:
				if not single_univ in fname:
					continue
			if fname.endswith( ".%s.tsv" % ( DATname.replace("MF_","").replace("ADD_","") ) ) and "03_^DAT" in root and not "/@/" in root:
				filepath = root + "/" + fname
				cmd = "cat \"%s\"|tail -n +2 >> \"%s\"" % ( filepath.replace("$","\$"), DAT_path )
				os.system( cmd )


def regather_DAT( single_table="", single_univ="" ):

	performance.timer("Collating DAT files")
	print( "Collating DAT files..." )

	if single_table:
		gather_DAT( single_table )
	else:
		gather_DAT( "PEOPLA", 			single_univ )
		gather_DAT( "PEO_REL", 			single_univ )
		gather_DAT( "MF_OCC", 			single_univ )
		#gather_DAT( "MF_DONATION",		single_univ )
		#gather_DAT( "MF_MEMORIAL",		single_univ )
		#gather_DAT( "MF_DEATH", 		single_univ )
		#gather_DAT( "MF_STATUS", 		single_univ )

		# new
		gather_DAT( "MF_PLN", 			single_univ )
		gather_DAT( "MF_SLAVES", 		single_univ )
		#gather_DAT( "MF_PRODUCE", 		single_univ )
		#gather_DAT( "MF_WHITES", 		single_univ )

		#gather_DAT( "SRC", 			single_univ )
		#gather_DAT( "SRC_LETTER", 		single_univ )
		#gather_DAT( "SRC_WILL", 		single_univ )
		#gather_DAT( "MAPPING", 		single_univ )

		#gather_DAT( "SURNAME_DETAILS",	single_univ ) # should be a different database ?

		#gather_DAT( "MF_PASSAGE", single_univ ) # deprecated
		#gather_DAT( "TXT", single_univ )

		#gather_DAT( "ADD_MEMBER", single_univ )
		#gather_DAT( "ADD_POPULATION", single_univ )
		#gather_DAT( "ADD_SAILING", single_univ )


def repopulate_DB( is_regather=True, override=False, single_table="", single_univ="" ):

	if is_regather:
		regather_DAT( single_table, single_univ )

	if single_univ:
		DB_path = confdat.DB_dir + "/02_RDB/%s.sqlite" % ( single_univ )
		print( DB_path )
	else:
		DB_path = confdat.DB_dir + "/02_RDB/db.sqlite"

	print( "Populating database..." )
	for filename in glob.glob( confdat.DB_dir + "/01_TSV/*" ):

		if single_table:
			if not single_table in filename:
				continue

		print( "Importing %s..." % filename )

		db_tbl_name = filename.rsplit( "/", 1 )[1].replace( ".tsv", "" ).replace( "^", "" ).lower().replace( "mf_", "MF_" ).replace( "src_", "SRC_" ).replace( "add_", "ADD_" )

		# -------------------------------------------------------- #
		# CHANGED to an import statement for better performance... #
		# -------------------------------------------------------- #
		cmd = "sqlite3 %s" % DB_path
		child = pexpect.spawn( cmd )

		child.expect( "sqlite>" )
		child.sendline( ".mode tabs" )

		child.expect( "sqlite>", timeout=2000 )

		if " " in db_tbl_name: continue

		cmd = "delete from %s where 1;" % db_tbl_name
		print( cmd )
		child.sendline( cmd )

		child.expect( "sqlite>", timeout=2000 )
		cmd = ".import %s %s" % ( filename, db_tbl_name )
		print( cmd )
		child.sendline( cmd )

		# alternatively from the command line: sqlite3 Bethel_Chapel.sqlite -separator $'\t' '.import ../01_TSV/^PEOPLA.tsv peopla'

		child.expect( "sqlite>", timeout=2000 )
		child.close()


#rdb.repopulate_DB(is_refresh=False, is_regather=True, single_table="ADD_SAILING")
repopulate_DB( is_regather=True )
