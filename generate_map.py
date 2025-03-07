from src.ontologise.utils import Document, DEFAULT_SETTINGS, logger
import logging
import argparse
import os.path
import sys
import math


logging_level_mapping = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


### Checking that a file is valid
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        logger.critical("The file '%s' does not exist!" % arg)
    else:
        return open(arg, "r")  # return an open file handle

def kml_mapping():

    ### Parsing the command line argument
    parser = argparse.ArgumentParser(description="Drawing maps from KML")

    ### This argument provides the marked up Ontologise document
    ### This is REQUIRED
    parser.add_argument(
        "-i",
        dest="file",
        required=True,
        help="A KML file containing the information to be mapped",
        metavar="FILE",
        type=lambda x: is_valid_file(parser, x),
    )

    ### This argument provides the style file (tsv)
    ### This needs to be provided
    parser.add_argument(
        "-s",
        dest="style_file",
        required=True,
        help="The styles to be used for the mapping",
        metavar="STYLE TSV",
        type=lambda x: is_valid_file(parser, x),
    )

    ### This argument requests a pause after reading each line
    parser.add_argument(
        "-p",
        nargs='?',
        const=1,
        default=math.inf,
        dest="pause",
        required=False,
        help="Request a pause after a specific line (default = 1)",
        metavar="INTEGER",
        type=int
    )

    ### This argument sets the logging information
    parser.add_argument(
        "-q",
        dest="quiet",
        required=False,
        help="Suppress any logging messages",
        action="store_true",
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
    parser = kml_mapping()

    ### Parse the arguments
    args = parser.parse_args()

    ### Set the logging level first (default logging is 'info')
    logging_level = ""

    if args.log is None:
        logging_level = logging.INFO
    else:
        logging_level = logging_level_mapping[args.log.lower()]

    if args.quiet:
        logger.disabled = True
    else:
        logger.setLevel(logging_level)
        logging_level_name = logging.getLevelName(logger.getEffectiveLevel())

        logger.info(f"Logging level is '{logging_level_name}'")

        logger.debug(args)

    ### Stop processing if the file name is missing
    if args.file is None:
        sys.exit(1)

    ### Stop processing if the file name is missing
    if args.style_file is None:
        sys.exit(1)

    ### If the file name is present, use it
    file_to_read = args.file.name

    ### If the pause flag is present, set pause_threshold to true
    pause_threshold = args.pause

    ### If the settings file is missing, use the default one
    styles_to_use = None

    if args.style_file is None:
        logger.info(
            "No value provided for the settings file, using the default settings file"
        )
        styles_to_use = DEFAULT_SETTINGS
    else:
        styles_to_use = args.style_file.name

    logger.debug(f"File to read: {file_to_read}")
    logger.debug(f"Styles to use: {styles_to_use}")

    ### Do the work
    # d = Document(file_to_read, settings_file=styles_to_use)
    # d.read_document(pause_threshold)

    ### Print a summary of the results
    # print(d)
