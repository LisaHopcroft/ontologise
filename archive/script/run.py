import os

bin_dir = "/mnt/SSD3/Dropbox/workspace/2.research/_bin/ontologize/run/05_data_transformation"
run_dir = "/mnt/SSD3/Dropbox/workspace/3.productions/websites/demerara1823.michaelhopcroft.com/script"


def escape_filepath( txt ):
	txt = txt.replace( "[", "!$" ).replace( "]", "$!" )
	return txt.replace( "(", "\(" ).replace( ")", "\)" ).replace( "!$", "[[" ).replace( "$!", "]]" )


sources = []
with open( "sources.txt", "r" ) as r:
	for line in r.readlines():
		if line.startswith("#"): continue
		sources.append( line.strip() )
		
		
# parse sources
		
for src in sources:

	print()
	print( "========================================================================" )
	print( "========================================================================" )
	print()

	cmd = "python3 %s/parse_all.py \"%s\"" % ( bin_dir, src )
	print( cmd )
	os.system( cmd )

print()
print()


# build database from sources
		
cmd = "python3 %s/build_local_database.py %s" % ( bin_dir, run_dir )
os.system( cmd )

print()
print()
