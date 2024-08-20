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

root_dir = "/media/michael/Files/Dropbox/workspace/2.research/1.Material/05.Periodicals/A, Newspapers/a, SCOTLAND/InvJ, Inverness Journal (est.1807)/ALL, IMG+TRX"
img_sub = "/01_JPG/20160928, IRL"
txt_sub = "/02_TXT"
rel_sub = ".."

for root, dirs, files in os.walk(root_dir + img_sub):
	for fname in files:
		if fname.lower().endswith(".jpg") or fname.lower().endswith(".png"):
			imgpath = os.path.join(root, fname)
			txtpath = imgpath.replace(img_sub, txt_sub) + ".txt"

			rel_img_path = ".." + img_sub + "/" + fname

			if not os.path.isfile(txtpath):
				print txtpath
				with open( txtpath, "w" ) as output_file:
					output_file.write( "#NEWSPAPER\n\n![image]\n\n\n--------------------------------\n[image]: %s" % ( rel_img_path.replace( " ", "%20" ) ) )
