import os


for root, dirs, files in os.walk( "." ):
	for fname in files:
		if fname.endswith( ".jpg" ) and "01_IMG" in root:
			fpath = "%s/%s" % ( root, fname )
			writepath = fpath.replace( "01_IMG", "02_TXT" ) + ".txt"

			at 		= ""
			date 	= writepath.rsplit( "/", 1 )[1].split("-",1)[0]

			if len( date ) == 8:

				page 	= writepath.rsplit( "-", 1 )[1].split(".",1)[0]
				colony 	= writepath.split( ")", 1 )[0].split("(",1)[1]

				if len( colony ) == 3:
					at = "WIN, " + colony

				if not os.path.exists( writepath ) and len( page ) < 3 and colony:
					print writepath
					print fpath
					print at
					print date
					print page
					relpath = "01_IMG" + fpath.split("01_IMG",1)[1]
					count_dir = relpath.count( "/" )
					prepath = ""
					for i in range( 1, count_dir+1 ):
						prepath += "../"
					relpath = prepath + relpath
					print count_dir
					print relpath

					if not os.path.exists(writepath.rsplit("/",1)[0]):
						os.makedirs(writepath.rsplit("/",1)[0])

					with open( writepath, "w" ) as w:
						w.write( """#NEWSPAPER
##DATE:	{date}
##AT:	{at}
##PAGE:	{page}
----------------------------------------------


![img]

[...]
[...]
[...]


----------------------------------------------
[img]: {relpath}
""".format( page=page, date=date, at=at, relpath=relpath ) )
			
