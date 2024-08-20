#!/usr/bin/python

import os


override = False

# -------------------------------------------------------------- #
# Extract the TXT from a text-based PDF
# -------------------------------------------------------------- #


run_dir = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/02.Publications/(C), Periodicals/(B), WIN/(SUR), Suriname/Surinaamsche Almanak"


is_override = True
is_ocr 		= False


for root, dirs, files in os.walk( run_dir ):
	for filename in files:
		if filename.endswith(".pdf") and "00_PDF" in root and "@" in root:
			filepath = "%s/%s" % ( root, filename )
			print( filepath )
			new_dirname = "02_TXT"
			if is_ocr: new_dirname = "02_TXT/@pdf-ocr"
			writepath = filepath.replace("00_PDF",new_dirname) + ".txt"
			writedir = writepath.rsplit("/",1)[0]

			if not os.path.exists( writedir ): os.makedirs( writedir )

			if not os.path.exists( writepath ) or is_override:
				cmd = "pdftotext -layout \"%s\" \"%s\"" % ( filepath, writepath )
				os.system( cmd )

				page_num = 0
				lines = []
				with open( writepath, "r" ) as r:
					lines = r.readlines()

				is_first_line = True
				with open( writepath, "w" ) as w:
					for line in lines:
						if line == "\f": 
							line = "\n\n[END]"
						elif "\f" in line or is_first_line:
							line = "\n![img](%s)\n\n%s" % ( writepath.replace( run_dir, "../.." ).replace(".pdf","").replace(".txt","-%s.jpg" % (page_num)).replace("02_TXT","01_IMG"), line.replace("\f","") )
							page_num += 1
						is_first_line = False
						w.write( line )
	
			# if too small - delete it
			if os.path.getsize( writepath ) < 50:
				os.remove( writepath )
