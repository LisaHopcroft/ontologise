import os

# Matches any file ending "TO4x3.pdf"

for root, dirs, files in os.walk( "../.." ):
	for filename in files:
		filepath = root + "/" + filename
		if ".To4x3.pdf" in filename:
			writepath = filepath.replace(".To4x3.pdf",".4x3.pdf").strip()
			if not os.path.exists( writepath ):
				cmd =  "gs -sDEVICE=pdfwrite -dPDFFitPage -r72 -g594x792 -dFirstPage=1 -dPDFSETTINGS=/screen -o %s %s" % ( '"' + writepath + '"', '"' + filepath + '"' )
				print cmd
				os.system( cmd )
				os.remove( filepath )
			else:
				print "EXISTS: " + writepath
