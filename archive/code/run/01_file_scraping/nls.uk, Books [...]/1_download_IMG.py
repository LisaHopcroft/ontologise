import os

nls_home = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/02.Publications"

for root, dirs, files in os.walk( nls_home ):
	for fname in files:
		if fname == "@nls-multi.txt":
			with open( "%s/%s" % (root,fname), "r" ) as r:
				for line in r.readlines():
					if line.startswith("#"): continue

					url = line.strip()

