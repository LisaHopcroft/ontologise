#!/usr/bin/python

import os
import sys

num_pages = 369

#convert
'''for i in range(0,num_pages):
	cmd = "convert -density 300 ../01_PDF/Franklin_1992_Enterprise_and_advantage.pdf[%s] -alpha off -depth 8 ../tmp/p%s.tif" % ( i, str(i).zfill(3) )
	print cmd
	os.system( cmd )'''

#OCR
'''for i in range(0,num_pages):
	cmd = "tesseract ../tmp/p%s.tif ../tmp/PDF.%s.OCR" % ( str(i).zfill(3), str(i).zfill(3) )
	os.system( cmd )'''

#concatenate
with open( "../01_OCR/PDF.OCR.txt", "w" ) as w:
	for i in range(0,num_pages):
		filename = "../tmp/PDF.%s.OCR.txt" % ( str(i).zfill(3) )
		with open( filename, "r" ) as r:
			content = r.read()
			w.write( "------------------------------\n\n![%s]\n" % ( str(i).zfill(3) ) )
			w.write( content )
