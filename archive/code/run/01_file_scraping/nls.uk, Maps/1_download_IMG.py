import os

nls_home = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Primary/03.Maps etc/00.WWW/NLS, National Library of Scotland/OS 6-inch, 1st Edition, 1843-1882 [+]/Ayrshire"

for root, dirs, files in os.walk( nls_home ):
	for fname in files:
		if fname == "@NLS-GET.txt":
			with open( "%s/%s" % (root,fname), "r" ) as r:
				for line in r.readlines():
					if line.startswith("#"): continue
					if not "/" in line: continue

					url = line.strip()
					dlfile = url.rsplit("/",1)[1]
					dest = "%s/01_IMG/%s.jpg" % ( root, dlfile )

					if not os.path.exists( "%s/01_IMG" % (root) ): os.mkdir( "%s/01_IMG" % (root) )

					if os.path.isfile( dest ): continue
					if os.path.isfile( dest.replace(".png",".jpg") ): continue

					cmd = "./phantomjs ./rasterize.js '%s' '%s'" % ( url, dest )
					print( cmd )
					os.system( cmd )

					print( "- Shaving and trimming" )
					cmd = "convert '%s' -shave 300x300 '%s'" % (dest,dest)
					os.system( cmd )
					cmd = "convert '%s' -fuzz 10%% -trim +repage '%s'" % (dest,dest)
					os.system( cmd )
