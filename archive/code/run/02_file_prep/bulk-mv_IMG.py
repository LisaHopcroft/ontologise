#!/usr/bin/python
import os
import sys
sys.path.append("/media/michael/Files/Dropbox/workspace/2.research/_bin")


for root, dirs, files in os.walk("/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/02.ENGLAND & WALES/TNA, National Archives (UK)/CO, Colonial Office"):
	for dname in dirs:
		if dname == "mv":
			fpath = "%s/mv/IMG_rename.tsv" % ( root )
			if os.path.exists( fpath ):
				with open( fpath, "r" ) as r:
					for line in r.readlines():
						if "\t" in line:
							vals = line.split("\t")
							vals[1] = vals[1].strip()
							if vals[1]:

								# add file extension
								if not "." in vals[1]: vals[1] = vals[1] + "." + vals[0].rsplit(".",1)[1]

								fm_path = "%s/%s" % ( root, vals[0].strip() )
								to_path = "%s/%s" % ( root, vals[1].strip() )

								cmd = "mv \"%s\" \"%s\"" % ( fm_path, to_path )
								if not "." in to_path: to_path = to_path + "." + fm_path.rsplit(".",1)[1]
								if vals[1] and os.path.exists( fm_path ) and not os.path.exists( to_path ):
									os.system( cmd )
									print( cmd )
