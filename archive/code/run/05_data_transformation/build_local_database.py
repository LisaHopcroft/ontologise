#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.data_transformation.all as dp
import ontologize.modules.util.confdat as confdat
import ontologize.modules.util.performance as performance
from ontologize.modules.util.all import *
import pexpect


run_dir = ""
if len(sys.argv) > 1:
	run_dir = sys.argv[1]


sources = []
with open( "sources.txt", "r" ) as r:
	for line in r.readlines():
		if line.startswith("#"): continue
		sources.append( line.strip() )


def gather_DAT( DATname ):
	# NOTE: (1) Changed to pandas due to performance problem... still slow though...
	# NOTE: (2) Changed to piping on the command line... FASTER!!!

	DAT_path = run_dir + "/01_TSV/^%s.tsv" % DATname

	if os.path.isfile( DAT_path ):
		os.system( "rm %s" % DAT_path )

	#print( "Gathering %s..." % DATname )
	# gather DAT files...
	ALL_dat = None
	is_a_dat = False

	for src in sources:
		for root, dirs, files in os.walk( src, topdown=True ):
			for fname in files:
				if fname.endswith( ".%s.tsv" % ( DATname.replace("MF_","").replace("ADD_","") ) ) and "03_^DAT" in root and not "/@/" in root:
					filepath = root + "/" + fname
					cmd = "cat \"%s\"|tail -n +2 >> \"%s\"" % ( filepath.replace("$","\$"), DAT_path )
					os.system( cmd )


def regather_DAT():

	performance.timer("Collating DAT files")
	print( "Collating DAT files..." )

	gather_DAT( "PEOPLA" )
	gather_DAT( "PEO_REL" )
	gather_DAT( "MF_OCC" )
	# new
	gather_DAT( "MF_PLN" )
	gather_DAT( "MF_SLAVES" )


def repopulate_DB( is_regather=True, override=False ):

	if is_regather:
		regather_DAT( )

	DB_path = run_dir + "/02_RDB/db.sqlite"

	print( "Populating database..." )
	for filename in glob.glob( run_dir + "/01_TSV/*" ):

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


repopulate_DB( is_regather=True )
