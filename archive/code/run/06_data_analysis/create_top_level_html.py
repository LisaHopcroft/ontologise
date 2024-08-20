#!/usr/bin/env python
# coding: utf-8

import os

root_dir = "/media/michael/SSD3/Dropbox/workspace/2.research" # set this globally...

def convert_to_url( fpath ):
	fpath = fpath.replace( " ", "%20" )
	fpath = fpath.replace( "^", "%5E" )
	fpath = fpath.replace( root_dir, "http://localhost:8000" )
	return fpath


trees_paths = []
for root, dirs, files in os.walk( "%s/01.Sources" % root_dir ):
	for fname in files:
		if fname.endswith( "^trees.html" ) and "^vis" in root:
			trees_paths.append( "%s/%s" % ( root, fname ) )

with open( "%s/^vis/^trees.html" % root_dir, "w" ) as w:
	for fpath in trees_paths:
		w.write( '<a href="%s">%s</a>' % ( convert_to_url( fpath ), fpath.replace( root_dir, "" ) ) )
