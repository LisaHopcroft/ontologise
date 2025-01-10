from src.ontologise.utils import Document
import argparse
from argparse import ArgumentParser
import os.path

### Defining the default settings file
default_settings_file = "settings.yaml"

### Checking that a file is valid
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, "r")  # return an open file handle

### Parsing the command line argument
parser = argparse.ArgumentParser(description="Parsing Ontologise markup documents")

### This argument provides the marked up Ontologise document
### This is REQUIRED
parser.add_argument(
    "-i",
    dest="file",
    required=True,
    help="A file using the Ontologise markup format",
    metavar="FILE",
    type=lambda x: is_valid_file(parser, x),
)

### This argument provides the settings file
### If this argument is not provided, the default settings file (settings.yaml) is used
parser.add_argument(
    "-s",
    dest="settings_yaml",
    required=False,
    help="The settings for the parsing",
    metavar="SETTINGS YAML",
    type=lambda x: is_valid_file(parser, x),
)

args = parser.parse_args()

file_to_read = args.file.name
settings_to_use = None

if args.settings_yaml is None:
    print( "No value provided for the settings file, using the default settings file" )
    settings_to_use = default_settings_file
else:
    settings_to_use = args.settings_yaml.name

print( f"File to read: {file_to_read}" )
print( f"Settings to use: {settings_to_use}" )

d = Document(file_to_read, settings_file=settings_to_use)

d.read_document()
d.print_summary()
