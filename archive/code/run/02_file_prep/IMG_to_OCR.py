#!/usr/bin/python

import os
import shutil
import getopt
import sys
import re
import sys
sys.path.append("/mnt/SSD3/Dropbox/workspace/2.research/_bin")
from ontologize.modules.util.all import *

# just targetting this at a single directory for now
# could be changed to operate universally...

# ------------------------------------------------------------- #
# Convert PNG to MKD template file
# ------------------------------------------------------------- #

run_dir = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/02.Publications/(A), Books, Pamphlets &c/[BY-SUBJECT]/(SCO, REN, LWH)/(abt. Renfrewshire Poets)/RAMSAY, 1838 - The Works of Robert Tannahill"
rel_sub = "../../"
ocr_dir = "01_IMG"

ocr_dirs = []


for root, dirs, files in os.walk( run_dir ):
	for dirname in dirs:
		if dirname == ocr_dir:
			ocr_dirs.append( "%s/%s" % ( root, dirname ) )


def tidy_tesseract_ocr( content ):
	return content.replace( "\n| ","\n" ).replace(" |\n","\n").replace("\n\n\n","\n\n").replace("\n\n\n","\n\n").replace("\n\n\n","\n\n").replace("\n\n\n","\n\n")


for path in ocr_dirs:
	for root, dirs, files in os.walk( path ):
		for fname in sorted(files):
			if not fname.endswith(".jpg") and not fname.endswith(".png"): continue

			imgpath = os.path.join(root, fname)
			writedir = imgpath.rsplit("/",1)[0].replace( "01_IMG", "02_TXT/@ocr" )
			if not os.path.exists( writedir.rsplit("/",1)[0] ): continue
			if not os.path.exists( writedir ):
				cmd = "mkdir \"%s\"" % writedir
				os.system( cmd )
			txtpath = imgpath.replace( "01_IMG", "02_TXT/@ocr" ) + ".txt"
			if os.path.isfile(txtpath): continue

			print( imgpath )

			cmd		= "tesseract %s %s --psm 1 quiet" % ( escape_filepath( imgpath ), escape_filepath( txtpath )[:-4] )
			print( "- Running OCR..." )
			os.system( cmd )

			rel_img_path = imgpath.replace( path, rel_sub+ocr_dir )

			with open( txtpath, "r+" ) as f:
				content = f.read()
				f.seek(0, 0)
				f.write( "![img](%s)\n" % ( rel_img_path.replace( " ", "%20" ) ) )
				f.write( tidy_tesseract_ocr( content ) + "\n\n[END]")
