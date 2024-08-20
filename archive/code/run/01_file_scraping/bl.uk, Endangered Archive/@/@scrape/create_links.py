#!/usr/bin/python

import sys, os, time
sys.path.append("/mnt/cloud/Dropbox/workspace/2.academia/_bin")
from util import *


url_start = "http://eap.bl.uk/EAPDigitalItems/EAP688/EAP688"

for root, dirs, files in os.walk("/mnt/cloud/Dropbox/workspace/2.academia/1.Material/2.Official/00.DIGITAL-COLLECTIONS/"):
	print "woof"
	for name in files:
		print name
		if name.startswith("dload.txt"):
			print "woof"
			text_file = open(root + "/links.html", "w")

			path = root + "/" + name
			f = open(path, 'r')

			print path
			url_end = f.readline().rstrip()
			start = int( f.readline().rstrip() )
			end = int( f.readline().rstrip() )
			modifier = f.readline().rstrip()

			for x in range(start, start+end):
				x_str = ""
				if x < 10:
					x_str = "00" + str(x);
				elif x < 100:
					x_str = "0" + str(x);
				else:
					x_str = str( x )
				text_file.write( "<a href='" + url_start + "_" + url_end + "_" + x_str + modifier + "_L.jpg'>" + str(x) + "</a><br/>\n" )

			text_file.close()
