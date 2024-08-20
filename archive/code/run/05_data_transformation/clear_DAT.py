import os


run_path = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/02.Publications/(C), Periodicals/(B), WIN/(SUR), Suriname"

for root, dirs, files in os.walk( run_path ):
	for fname in files:
		if "03_^DAT" in root and fname.startswith( "^" ):
			delfile = "%s/%s" % ( root, fname )
			print( delfile )
			os.system( "rm \"%s\"" % delfile )
