import os
import csv


def polygons_to_tsv( run_dir, w ):

	print( "Reading polygons\n" )

	i = 0

	for fname in os.listdir( run_dir ):

		if not fname.endswith(".kml"): continue

		print( f"Reading polygon file {fname}\n" )

		class_name = "Undefined"

		if "-" in fname:
			class_name = fname.split("-",1)[0]
		elif "." in fname:
			class_name = fname.split(".",1)[0]

		with open("%s/%s" % (run_dir, fname), "r") as r:
			for line in r.readlines():
				i += 1
				if (
					line.strip().startswith("-") or line.strip()[0].isdigit()
				):  # i.e. a new start to coordintes...
					line = line.strip()
					for coordinate in line.split(" "):
						if "," in coordinate:
							lon, lat, alt = coordinate.split(",")
							w.write(
								"\t".join(
									["poly", "poly" + str(i), class_name, "", lat, lon]
								)
								+ "\n"
							)


def paths_to_tsv( run_dir, w ):

	print( "Reading paths\n" )

	i = 0

	for fname in os.listdir( run_dir ):

		if not fname.endswith(".kml"): continue

		print( f"Reading paths file {fname}\n" )

		class_name = "Undefined"

		if "-" in fname:
			class_name = fname.split("-",1)[0]
		elif "." in fname:
			class_name = fname.split(".",1)[0]

		with open( "%s/%s" % ( run_dir, fname ), "r" ) as r:
			for line in r.readlines():
				i += 1
				if line.strip().startswith("-") or line.strip()[0].isdigit(): # i.e. a new start to coordintes...
					line = line.strip()
					for coordinate in line.split(" "):
						#print( coordinate )
						if "," in coordinate:
							lon, lat, alt = coordinate.split(",")
							w.write( "\t".join( [ "path", "path"+str(i), class_name, "", lat, lon ] ) + "\n" )


def points_to_tsv( run_dir, w ):
	for root, dirs, files in os.walk( run_dir ):
		i = 0
		for fname in files:
			if not fname.endswith(".kml"): continue

			class_name = "Undefined"

			if "-" in fname:
				class_name = fname.split("-",1)[0]
			elif "." in fname:
				class_name = fname.split(".",1)[0]

			name = ""
			with open( "%s/%s" % ( root, fname ), "r" ) as r:
				for line in r.readlines():
					i += 1

					if line.strip().startswith("<name>"):
						name = line.strip().replace("<name>","").replace("</name>","")

					if line.strip().startswith("<coordinates>"): # i.e. a new start to coordintes...
						line = line.strip().replace("<coordinates>","").replace("</coordinates>","")
						lon, lat, alt = line.split(",")
						w.write( "\t".join( [ "point", "point"+str(i), class_name, name, lat, lon ] ) + "\n" )
						name = ""


def frame_to_tsv( run_dir, w ):
	for root, dirs, files in os.walk( run_dir ):
		i = 0
		for fname in files:
			if not fname.endswith(".kml"): continue

			if "TL" in fname:
				with open( "%s/%s" % ( root, fname ), "r" ) as r:
					for line in r.readlines():
						i += 1

						if line.strip().startswith("<coordinates>"): # i.e. a new start to coordintes...
							line = line.strip().replace("<coordinates>","").replace("</coordinates>","")
							lon, lat, alt = line.split(",")
							w.write( "\t".join( [ "frame_TL", "", "", "", lat, lon ] ) + "\n" )
							name = ""

			if "BR" in fname:
				with open( "%s/%s" % ( root, fname ), "r" ) as r:
					for line in r.readlines():
						i += 1

						if line.strip().startswith("<coordinates>"): # i.e. a new start to coordintes...
							line = line.strip().replace("<coordinates>","").replace("</coordinates>","")
							lon, lat, alt = line.split(",")
							w.write( "\t".join( [ "frame_BR", "", "", "", lat, lon ] ) + "\n" )
							name = ""


for dirpath in [f.path for f in os.scandir("./data") if f.is_dir()]:
	print ( f"Reading this directory {dirpath}" )

	with open( dirpath + "/ALL.tsv", "w" ) as w:
		w.write( "\t".join( [ "type", "id", "class", "label", "lat", "lon" ] ) + "\n" )
		# frame_to_tsv( dirpath + "/frame", w )
		polygons_to_tsv( dirpath + "/polygons", w )
		# paths_to_tsv( dirpath + "/paths", w )
		# points_to_tsv( dirpath + "/points", w )


# append some src specific background stuff

# with open( "kml/LWH/ALL.tsv", "a" ) as a:
# 	with open( "kml/LWH/src_points.tsv", "r" ) as tsv:
# 		reader = csv.DictReader( tsv, delimiter='\t' )
# 		for row in reader:
# 			a.write( "\t".join( row.values() ) + "\n" )


# with open( "kml/WIN/ALL.tsv", "a" ) as a:
# 	with open( "kml/WIN/src_points.tsv", "r" ) as tsv:
# 		reader = csv.DictReader( tsv, delimiter='\t' )
# 		for row in reader:
# 			a.write( "\t".join( row.values() ) + "\n" )
