import os

nls_home = "/media/michael/Files/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/04.OTHER/USA, United States of America/UOM-JFBL, University of Minnesota - James Ford Bell Library"

for root, dirs, files in os.walk( nls_home ):
	for fname in files:
		if fname == "@umedia.txt":
			with open( "%s/%s" % (root,fname), "r" ) as r:
				for line in r.readlines():
					if line.startswith("#"): continue

					url = line.strip()
					dlfile = url.rsplit("/",1)[1]
					dest = "%s/01_IMG/%s.png" % ( root, dlfile )

					if not os.path.exists( "%s/01_IMG" % (root) ): os.mkdir( "%s/01_IMG" % (root) )

					if os.path.isfile( dest ): continue

					cmd = "./phantomjs ./rasterize.js '%s' '%s'" % ( url, dest )
					print( cmd )
					os.system( cmd )

					cmd = "convert '%s' -shave 300x300 '%s'" % (dest,dest)
					os.system( cmd )
					cmd = "convert '%s' -fuzz 10%% -trim +repage '%s'" % (dest,dest)
					os.system( cmd )
