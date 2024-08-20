#!/usr/bin/python

import os
import glob
import sys
import re
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
from subprocess import call


match_files = []
pdf_files = []
txt_files = []


run_dir = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/03.Publications/(B), Newspapers/(A), GBR/InvC, Inverness Courier (est.1817)"


for root, dirs, files in os.walk( run_dir, topdown=True ):
	for fname in files:
		fpath = "%s/%s" % ( root, fname )
		if fname.endswith(".anno"):
			#print fpath
			with open( fpath, 'r' ) as r:
				for i, line in enumerate( r ):
					if "content:" in line:
						tag = line.replace("content:","").strip().replace("##","")
						writefile = fname.replace( "^", "" ).replace( ".anno", "" ).replace( ".pdf", ".pdf.jpg" ) + ".[" + tag + "].txt"
						date_txt  = writefile.split( "_" )[2]
						page_txt  = writefile.split( "_" )[4]
						writefile = "%s_%s" % ( date_txt, page_txt )
						writedir  = root.replace("00_PDF","02_TXT")
						writepath = "%s/%s" % ( writedir, writefile )
						imgpath   = writepath.split(".[")[0].replace("02_TXT","01_IMG").replace(run_dir,"../..")
						page_txt  = page_txt.split( ".", 1 )[0]

						file_exists = False
						matching_files = glob.glob( fpath )
						for globfiles in matching_files:
							if tag in globfiles:
								file_exists = True

						if not os.path.exists(writepath) and not file_exists:
							print writepath
							with open(writepath, 'w') as w:
								template = """#[NEWSPAPER]
##DATE:\t{0}
##PAGE:\t{1}
--------------------------------


![img]({2})\n\n[END]""".format( date_txt, page_txt, imgpath )
							
								w.write( template )

