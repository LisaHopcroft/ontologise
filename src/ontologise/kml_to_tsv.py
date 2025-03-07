import os
import csv
# from src.ontologise.utils import logger


def polygons_to_tsv( run_dir, w ):

	i = 0

	for fname in os.listdir( run_dir ):

		if not fname.endswith(".kml"): continue

		logger.info( f"- Reading polygon file {fname}" )

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

    i = 0

    for fname in os.listdir( run_dir ):

        if not fname.endswith(".kml"): continue

        logger.info(f"- Reading paths file {fname}")

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
                        # print( coordinate )
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

    i = 0

    for fname in os.listdir( run_dir ):

        if not fname.endswith(".kml"): continue

        logger.info(f"- Reading frames file {fname}")

        name = None

        with open( "%s/%s" % ( run_dir, fname ), "r" ) as r:

            for line in r.readlines():
                i += 1

                if line.strip().startswith("<name>"):
                    name = line.strip().replace("<name>","").replace("</name>","")

                if line.strip().startswith("<coordinates>"): # i.e. a new start to coordintes...
                    if line.strip().endswith("</coordinates>"): # i.e. a new start to coordintes...

                        line = line.strip().replace("<coordinates>","").replace("</coordinates>","")
                        lon, lat, alt = line.split(",")
                        w.write( "\t".join( [ f"frame_{name}", "", "", "", lat, lon ] ) + "\n" )
                        name = ""
