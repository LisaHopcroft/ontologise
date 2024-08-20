#!/usr/bin/python
import os
import sys
import glob
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")
from ontologize.module.util.all import *


# rename 's/\ \(copy\).jpg/-R.jpg/' ./*


run_path = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/01.SCOTLAND/NRS, National Records of Scotland/GD, Gifts and Deposits/31, FEA of Clestrain/419, Letters of Factory, 1788"

for root, dirs, files in os.walk( run_path ):
	for dname in dirs:
		if dname == "01_IMG":
			pattern = "%s/%s/DSC*.JPG" % ( root.replace("[","$1[$2").replace("]","$1]$2").replace("$1","[").replace("$2","]"), dname )

			unnamed_images = glob.glob( pattern )

			for img in sorted( unnamed_images ):
				if " copy.JPG" in img:
					cmd = 'mv "%s" "%s"' % ( img, img.replace( " copy.JPG", "-R.JPG" ) )
					os.system( cmd )

					non_copy_img = img.replace( " copy.JPG", ".JPG" )
					if os.path.exists( non_copy_img ):
						cmd = 'mv "%s" "%s"' % ( non_copy_img, non_copy_img.replace( ".JPG", "-L.JPG" ) )
						os.system( cmd )

				if " (copy).JPG" in img:
					cmd = 'mv "%s" "%s"' % ( img, img.replace( " (copy).JPG", "-R.JPG" ) )
					os.system( cmd )

					non_copy_img = img.replace( " (copy).JPG", ".JPG" )
					if os.path.exists( non_copy_img ):
						cmd = 'mv "%s" "%s"' % ( non_copy_img, non_copy_img.replace( ".JPG", "-L.JPG" ) )
						os.system( cmd )

			unnamed_images = glob.glob( pattern )
