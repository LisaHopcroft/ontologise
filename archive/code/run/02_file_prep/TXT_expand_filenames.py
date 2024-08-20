import os
import csv
import glob


run_dir = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/00.WWW/NL-HaNA, Nationaal Archief/1.05.21, Dutch Series Guyana/(4), Berbice/(4.2), Court of Civil Justice/(5), Transports, 1770-1814/(8), AZ.3.212, 1812-4"

for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname == "expand_filenames.tsv":
			fpath = "%s/%s" % ( root, fname )
			with open( fpath, "r" ) as r:
				tsv = csv.reader(r, delimiter='\t')
				for row in tsv:
					if len(row)<2: continue
					if row[1] and not ", " in row[0]:
						orig = row[0]
						dest = orig.replace(".jpg.txt", ", "+row[1]+".jpg.txt")
						cmd = "mv \"%s/02_TXT/%s\" \"%s/02_TXT/%s\"" % ( root, orig, root, dest )
						print( cmd )
						os.system( cmd )


# set up the tsvs

for root, dirs, files in os.walk( run_dir ):
	for fname in files:
		if fname == "expand_filenames.tsv":
			fpath = "%s/%s" % ( root, fname )
			print( fpath )
			print( os.path.getsize(fpath) )
			if os.path.getsize(fpath) > 0:
				print( "not zero" )
				continue

			with open( fpath, "w" ) as w:
				for fpath in sorted( glob.glob( root + "/02_TXT/*.txt" ) ):
					w.write( fpath.rsplit("/",1)[1] + "\n" )
