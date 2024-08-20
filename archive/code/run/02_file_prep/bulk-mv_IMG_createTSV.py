#!/usr/bin/python
import os
import sys
import glob
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")


run_path = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/03.CARIBBEAN"

for root, dirs, files in os.walk( run_path ):
	for dname in dirs:
		if dname == "01_IMG":
			pattern = "%s/%s/DSC*.jpg" % ( root.replace("[","$1[$2").replace("]","$1]$2").replace("$1","[").replace("$2","]"), dname )
			print( pattern )
			unnamed_images = glob.glob( pattern )

			pattern = "%s/%s/DSC*.JPG" % ( root.replace("[","$1[$2").replace("]","$1]$2").replace("$1","[").replace("$2","]"), dname )
			print( pattern )
			unnamed_images += glob.glob( pattern )

			pattern = "%s/%s/IMG*.jpg" % ( root.replace("[","$1[$2").replace("]","$1]$2").replace("$1","[").replace("$2","]"), dname )
			print( pattern )
			unnamed_images += glob.glob( pattern )

			pattern = "%s/%s/2019-*.jpg" % ( root.replace("[","$1[$2").replace("]","$1]$2").replace("$1","[").replace("$2","]"), dname )
			print( pattern )
			unnamed_images += glob.glob( pattern )

			if unnamed_images:

				tsv_dir = "%s/%s/mv" % ( root, dname )

				if not os.path.exists( tsv_dir ):
					print( "Dir doesn't exist %s." % tsv_dir )

				else:
					tsv_path = "%s/%s" % ( tsv_dir, "IMG_rename.tsv" )

					if not os.path.exists( tsv_path ):
						with open( tsv_path, "w" ) as w:
							for img in sorted( unnamed_images ):
								imgname = img.replace( root, "" ).replace( dname, "" ).replace( "/", "" )
								w.write( imgname + "\n" )
								print( imgname )

					else:
						print( "Rewrite file already exists." )

			else:
				print( "No unnamed images." )
