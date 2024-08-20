#!/usr/bin/env python

import sys
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
from util.util import *
from subprocess import call
import os
import glob


def filecount(dir_name):
	return len([f for f in os.listdir(dir_name) if os.path.isfile(f)])

filecount = filecount(os.getcwd())

forloop = 1
if filecount == 2:
	for filepath in sorted(glob.glob( "*" )):
		new_filename = ""
		if forloop == 1:
			new_filename += "recto"
		if forloop == 2:
			new_filename += "verso"
		os.system( "cp %s %s" % ( filepath, new_filename + "_L.jpg" ) )
		os.system( "cp %s %s" % ( filepath, new_filename + "_R.jpg" ) )
		os.system( "rm %s" % ( filepath ) )
		forloop += 1
else:
	print "Only works on two files..."
