import glob
import os
import sys
sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")


run_path = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/01.Archives/01.SCOTLAND/NLS, National Library of Scotland/Adv.MS.34.4.14, Chartulary of Paisley Abbey, 1163-1530"

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def convert_dir( dirpath ):
	for root, dirs, files in os.walk( dirpath ):
		for fname in files:

			if not fname.endswith( ".pdf" ): continue

			filepath = "%s/%s" % ( root, fname )

			writepath = filepath.replace( "00_PDF", "01_IMG" )
			writedir = writepath.rsplit("/",1)[0]

			if not os.path.exists(writedir):
				os.makedirs(writedir)

			if not os.path.exists( writedir + "/ALL-001.png" ):
				cmd = "pdftoppm \"%s\" \"%s/ALL\" -png -r 300" % ( filepath, writedir )
				#cmd = "mogrify -density 300 -format jpg -quality 90 \"%s\"" % ( filepath ) # stopped working...
				print( cmd )
				os.system( cmd )


for root, dirs, files in sorted( os.walk( run_path ) ):
	for dirname in sorted( dirs ):
		if dirname == "00_PDF":
			dirpath = "%s/%s" % ( root, dirname )
			convert_dir( dirpath )
