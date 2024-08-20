import os
import csv
import glob


run_dir = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Material/01.Primary/01.Manuscripts/00.WWW/FS, FamilySearch/359031, Cairn of Lochwinyoch matters, 1827-37/1419535, Vol 45, Descriptions [...]"

writelines = []
writepath = ""

for root, dirs, files in os.walk( run_dir ):
	for fname in sorted( files ):
		if fname.endswith(".txt") and root.endswith( "/02_TXT" ):
			if ", " in fname:
				# write the previous file
				if writelines != "" and writepath != "":
					with open( writepath, "w" ) as w:
						for line in writelines:
							w.write( line )

				writepath = "%s/%s" % ( root, fname )
				with open( writepath, "r" ) as r:
					writelines = r.readlines()
			else:
				is_content = False
				with open( "%s/%s" % ( root, fname ), "r" ) as r:
					for line in r.readlines():
						if is_content:
							writelines += line
						if line.startswith( "---------" ):
							is_content = True
				os.system( "rm \"%s/%s\"" % ( root, fname ) )



			# write the previous file
			if writelines != "" and writepath != "":
				with open( writepath, "w" ) as w:
					for line in writelines:
						w.write( line )
