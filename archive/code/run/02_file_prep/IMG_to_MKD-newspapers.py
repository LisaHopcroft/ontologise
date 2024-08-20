#!/usr/bin/python

import os
import shutil
import getopt
import sys
import re
import glob

# just targetting this at a single directory for now
# could be changed to operate universally...

# ------------------------------------------------------------- #
# Convert PNG to MKD template file
# ------------------------------------------------------------- #

#root_dir = sys.argv[1]
root_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/02.Publications/(B), Newspapers/[BY-REPOSITORY]/00.WWW/BNA, British Newspaper Archive/[BY-SUBJECT]/(LWH)/[BY-COLUMN]/(P&RG - Lochwinnoch, 1905-7)"

img_sub = "/01_IMG"
txt_sub = "/02_TXT"
rel_sub = ".."
is_grouped = False

print( root_dir )


def is_file_exists( txtdir, txtpath ):
	for i in os.listdir(txtdir):
		txtname = txtpath.rsplit("/",1)[1].replace(".jpg.txt","").replace(".png.txt","")
		if i.startswith( txtname + "." ) or i.startswith( txtname + "," ):
			return True
	return False


for root, dirs, files in os.walk(root_dir):
	for fname in files:
		if not "01_IMG" in root or "@" in root: continue
		if fname.lower().endswith(".jpg") or fname.lower().endswith(".png"):
			imgpath = os.path.join(root, fname)
			txtdir  = root.replace(img_sub, txt_sub)

			abbrvimgpath = os.path.join(root, fname)#.rsplit("_",1)[1])
			txtpath = abbrvimgpath.replace(img_sub, txt_sub) + ".txt"

			rel_img_path = imgpath.replace( root.rsplit("/",1)[0], ".." )

			if os.path.isfile(txtpath): continue
			if not os.path.exists(txtdir): os.mkdir(txtdir)
			if not os.path.exists(txtpath.rsplit("/",1)[0]): os.mkdir(txtpath.rsplit("/",1)[0])
			if is_file_exists(txtdir, txtpath): continue 
			
			date_txt = fname
			if "." in fname:
				date_txt = fname.rsplit(".",1)[0]
			if "_" in fname:
				date_txt = fname.rsplit("_",1)[0]

			print( txtpath )
			with open( txtpath, "w" ) as w:
				w.write( "#[NEWSPAPER]\n##PUBL: P&RG\n##DATE: %s\n--------------------------------------------------------------------------------\n\n\n" % date_txt )
				w.write( "![img]({rel_img_path})".format( rel_img_path=rel_img_path.replace( " ", "%20" ) ) )
