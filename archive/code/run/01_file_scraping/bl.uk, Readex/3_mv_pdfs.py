import os


with open( "./mv.tsv" ) as r:
	for line in r.readlines():
		vals = line.split("\t")
		cmd = ( "mv /home/michael/Downloads/%s* \"%s\"" % ( vals[0].strip(), vals[1].strip() ) )
		os.system( cmd )
