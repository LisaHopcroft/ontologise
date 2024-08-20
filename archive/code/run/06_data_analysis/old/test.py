import argparse

parser = argparse.ArgumentParser(description="Generating tree visualisations from PEO/REL and PEO/PLA data sources.")

parser.add_argument("dir",
	nargs='?',
	help="The directory in which to search for PEO/REL and PEO/PLA data sources",
	default=".")

parser.add_argument("-v", action='store_true')

args = parser.parse_args()

if args.v:
	print( "Be verbose" )
else:
	print( "Be quiet")

print( "Directory: " + args.dir)


