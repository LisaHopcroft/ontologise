import argparse
import os.path
import sys

def polygons_to_tsv( run_dir, w ):

	i = 0

	for fname in os.listdir( run_dir ):

		if not fname.endswith(".kml"): continue

		print( f"- Reading polygon file {fname}" )

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

        print(f"- Reading paths file {fname}")

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

        print(f"- Reading frames file {fname}")

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



### Checking that a file is valid
def is_valid_directory(parser, arg):
	if not os.path.isdir(arg):
		print("The directory '%s' does not exist!" % arg)
	else:
		return arg

def kml_extraction():

	### Parsing the command line argument
	parser = argparse.ArgumentParser(description="Extracting information from KML")

	### This argument provides the directory containing a 'kml' directory
	### This is REQUIRED
	parser.add_argument(
		"-d",
		dest="dir",
		required=True,
		help="The directory that contains the target kml directory",
		metavar="DIR",
		type=lambda x: is_valid_directory(parser, x),
	)

	return( parser )


if __name__ == "__main__":
	parser = kml_extraction()

	### Parse the arguments
	args = parser.parse_args()


	### Stop processing if the file name is missing
	if args.dir is None:
		sys.exit(1)

	target_dir = args.dir

	for dirpath in [f.path for f in os.scandir(target_dir) if f.is_dir()]:

		if dirpath.endswith("/kml"):
			print("")
			print(f"KML source directory: {dirpath}")
			print(f"TSV target file     : {dirpath + '/ALL.tsv'}")
			print("")

			with open(dirpath + "/ALL.tsv", "w") as w:
				w.write("\t".join(["type", "id", "class", "label", "lat", "lon"]) + "\n")
				frame_to_tsv(dirpath + "/frame", w)
				polygons_to_tsv(dirpath + "/polygons", w)
				paths_to_tsv(dirpath + "/paths", w)
				# points_to_tsv( dirpath + "/points", w )
