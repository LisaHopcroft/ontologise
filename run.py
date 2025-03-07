from src.ontologise.utils import logger
from src.ontologise.kml_to_tsv import polygons_to_tsv, paths_to_tsv, frame_to_tsv
import logging
import argparse
import os.path
import sys


logging_level_mapping = {
	"critical": logging.CRITICAL,
	"error": logging.ERROR,
	"warn": logging.WARNING,
	"warning": logging.WARNING,
	"info": logging.INFO,
	"debug": logging.DEBUG,
}


### Checking that a file is valid
def is_valid_directory(parser, arg):
	if not os.path.isdir(arg):
		logger.critical("The directory '%s' does not exist!" % arg)
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

	### This argument sets the logging information
	parser.add_argument(
		"-l",
		dest="log",
		choices=logging_level_mapping.keys(),
		required=False,
		help="The logging level",
		metavar="LOGGING LEVEL",
	)

	return( parser )


if __name__ == "__main__":
	parser = kml_extraction()

	### Parse the arguments
	args = parser.parse_args()

	### Set the logging level first (default logging is 'info')
	logging_level = ""

	if args.log is None:
		logging_level = logging.INFO
	else:
		logging_level = logging_level_mapping[args.log.lower()]

	logger.setLevel(logging_level)
	logging_level_name = logging.getLevelName(logger.getEffectiveLevel())

	logger.info(f"Logging level is '{logging_level_name}'")

	logger.debug(args)

	### Stop processing if the file name is missing
	if args.dir is None:
		sys.exit(1)

	target_dir = args.dir

	for dirpath in [f.path for f in os.scandir(target_dir) if f.is_dir()]:

		if dirpath.endswith("/kml"):
			print("")
			logger.info(f"KML source directory: {dirpath}")
			logger.info(f"TSV target file	 : {dirpath + '/ALL.tsv'}")
			print("")

			with open(dirpath + "/ALL.tsv", "w") as w:
				w.write("\t".join(["type", "id", "class", "label", "lat", "lon"]) + "\n")
				frame_to_tsv(dirpath + "/frame", w)
				polygons_to_tsv(dirpath + "/polygons", w)
				paths_to_tsv(dirpath + "/paths", w)
				# points_to_tsv( dirpath + "/points", w )
