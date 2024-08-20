#!/usr/bin/python

import os
import shutil
import getopt
import sys
import re

# just targetting this at a single directory for now
# could be changed to operate universally...

# ------------------------------------------------------------- #
# Convert PNG to MKD template file
# ------------------------------------------------------------- #

root_dir = sys.argv[1]
img_sub = "01_IMG"
txt_sub = "02_TXT"
rel_sub = ".."

print root_dir


for root, dirs, files in os.walk(root_dir):
	for dirname in dirs:
		if dirname == "01_JPG":
			os.system("mv \"%s\" \"%s\"" % ( root+"/"+dirname, root+"/01_IMG" ))

for root, dirs, files in os.walk(root_dir):
	for dirname in dirs:
		if dirname == "01_IMG":
			if not os.path.exists( root+"/02_TXT" ):
				os.system( "mkdir \""+root+"/02_TXT\"" )

for root, dirs, files in os.walk(root_dir):
	for fname in files:
		if fname.lower().endswith(".jpg") or fname.lower().endswith(".png") or fname.lower().endswith(".JPG") and img_sub in root:
			imgpath = os.path.join(root, fname)
			txtpath = imgpath.replace(img_sub, txt_sub) + ".txt"

			rel_img_path = "../" + img_sub + "/" + fname

			if os.path.isfile( imgpath + ".txt" ):
				os.system( "rm \"%s\"" % imgpath + ".txt" )

			if not os.path.isfile(txtpath):
				with open( txtpath, "w" ) as output_file:
					output_file.write( "--------------------------------------------------------------------------------\n>\n--------------------------------------------------------------------------------\n\n\n![img](%s)" % ( rel_img_path.replace( " ", "%20" ) ) )
