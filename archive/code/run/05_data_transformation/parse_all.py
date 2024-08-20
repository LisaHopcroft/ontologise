#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.performance as performance
import ontologize.modules.util.confdat as confdat


bin_root = "/mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/05_data_transformation"
run_dir = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/02.ENGLAND & WALES/TNA, National Archives (UK)/T71, Registry of Colonial Slaves and Compensation/(001-671), Slave Registers, 1817-32/(461-492), Tobago"

if len(sys.argv) == 2:
	run_dir = sys.argv[1]


def empty_DAT( run_root ):
	os.system( "find \"%s\" -path */03_^DAT/*.tsv -delete" % run_root )


override = True

performance.timer("Regenerating DAT files")

if override:
	print( "Clearing DAT files..." )
	empty_DAT( run_dir )
	override_txt = " \"override\""
else:
	override_txt = ""

print( "Generating new DAT files..." )

print( "------------------------------------------------------------------------" )

print( " - KML to DAT" )
cmd = "python3 \"%s/parse_KML.py\" \"%s\"" % ( bin_root, run_dir )
os.system( cmd )

print( "------------------------------------------------------------------------" )

print( " - MKD to DAT" )
cmd = "python3 \"%s/parse_MKD.py\" \"%s\"" % ( bin_root, run_dir )
os.system( cmd )

print( "------------------------------------------------------------------------" )

print( " - ODS to DAT" )
cmd = "python3 \"%s/parse_ODS.py\" \"%s\"" % ( bin_root, run_dir )
os.system( cmd )

print( "------------------------------------------------------------------------" )

print( " - TREE to DAT" )
cmd = "python3 \"%s/parse_TREE.py\" \"%s\"" % ( bin_root, run_dir )
os.system( cmd )

print( "------------------------------------------------------------------------" )

print( " - Autoparse MKD tables" )
cmd = "python3 \"%s/autoparse_MKD_tables.py\" \"%s\"" % ( bin_root, run_dir )
os.system( cmd )

print( "------------------------------------------------------------------------" )

print( " - Autoparse MKD patterns" )
cmd = "python3 \"%s/autoparse_MKD_patterns.py\" \"%s\"" % ( bin_root, run_dir )
os.system( cmd )

print( "------------------------------------------------------------------------" )

print( " - Autoparse MKD custom" )
cmd = "python3 \"%s/autoparse_MKD_custom.py\" \"%s\"" % ( bin_root, run_dir )
os.system( cmd )
