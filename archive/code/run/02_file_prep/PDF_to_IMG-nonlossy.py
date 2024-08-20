import glob
import os
import sys
sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")


run_path = "/mnt/SSD3/Dropbox/workspace/2.research/01.Sources/01.Primary/01.Manuscripts/01.Archives/01.SCOTLAND/NLS, National Library of Scotland/Adv.MS.15.1.17, Rental of Paisley Abbey, 1460-1550"


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]



def escape_square_brackets( text ):
	text = text.replace("[","<[").replace("]","]>")
	text = text.replace("<[","[[]").replace("]>","[]]")
	return text


def convert_dir( dirpath ):
	for root, dirs, files in os.walk( dirpath ):
		for fname in files:
			if not fname.endswith( ".pdf" ): continue

			filepath = "%s/%s" % ( root, fname )

			writepath = filepath.replace( "00_PDF", "01_IMG" ) + ".jpg"
			writedir = writepath.rsplit("/",1)[0]

			if not os.path.exists(writedir):
				os.makedirs(writedir)

			if not os.path.exists( writepath.replace(".jpg","-0.jpg") ):
				cmd = "pdfimages -j \"%s\" \"%s\"" % ( filepath, filepath )				
				#cmd = "extractallimages \"%s\" \"%s\"" % ( filepath, filepath )
				#print( cmd )
				os.system( cmd )

				pattern = "%s/*.pbm" % ( filepath.rsplit("/",1)[0] )
				print( pattern )
				for fname in sorted( glob.glob( escape_square_brackets(pattern) ) ):
					#print( fname )
					cmd = "convert \"%s\" \"%s\"" % ( fname, fname.replace(".pbm",".jpg") )
					os.system( cmd )

				cmd = "rm \"%s\"" % ( pattern )
				#print( cmd )
				os.system( cmd )

				pattern = "%s/*.jpg" % ( filepath.rsplit("/",1)[0] )
				for fname in sorted( glob.glob( escape_square_brackets(pattern) ) ):
					#print( fname )
					cmd = "mv \"%s\" \"%s\"" % ( fname, fname.replace("00_PDF","01_IMG") )
					os.system( cmd )

				i = 0
				pattern = "%s/01_IMG/*.jpg" % ( filepath.rsplit("/",2)[0] )
				for fname in sorted( glob.glob( escape_square_brackets(pattern) ) ):
					print( fname )
					new_name = fname.rsplit("/",1)[0]
					new_name += "/" + str(i).zfill(4) + ".jpg"
					print( new_name )
					cmd = "mv \"%s\" \"%s\"" % ( fname, new_name )
					os.system( cmd )
					i+=1


for root, dirs, files in os.walk( run_path ):
	for dirname in dirs:
		if dirname == "00_PDF":
			dirpath = "%s/%s" % ( root, dirname )
			convert_dir( dirpath )
