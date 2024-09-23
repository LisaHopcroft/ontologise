import re
import yaml
from collections import defaultdict
import logging
import pandas as pd
from copy import deepcopy


data_point_separator = "\\t"

# Obtained from: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# Colour codes from: https://gist.github.com/abritinthebay/d80eb99b2726c83feb0d97eab95206c4
# Bold text: https://stackoverflow.com/questions/50460222/bold-formatting-in-python-console
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    cyan = "\x1b[46m"
    magenta = "\x1b[45m"
    bold_red = "\x1b[41m"
    reset = "\x1b[0m"
    format = "\033[1m [%(name)s][%(levelname)-5s][%(funcName)s][%(filename)s] \033[0m %(message)s"

    FORMATS = {
        logging.DEBUG: cyan + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: magenta + format + reset,
        logging.ERROR: bold_red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("Ontologise".upper())
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

class DataTable:

    def __init__( self, fields, shortcuts ):
        self.column_names = fields
        self.column_num = len( fields )
        self.attributes = shortcuts

        logger.debug("==== Creating a table ====")
        logger.debug(f"{self.column_num} columns")
        logger.debug(f"Column names: {','.join(self.column_names)}")
        logger.debug(f"Attributes are: {self.attributes}")
        logger.debug("==========================")

        # column_dictionary = {}
        # for c in fields:
        #     o = c.split(":")
        #     if len(o) == 2 :
        #         column_dictionary.update({o[0]:{o[1],''}})
        #     else:
        #         column_dictionary.update({o:''})

        # self.column_dictionary = column_dictionary
        # logger.debug(-------" Column dictionary -------")
        # logger.debug( column_dictionary )

class DataPoint:

    def __init__( self, list, table ):

        logger.debug(f"data point list provided [{list}]")
        logger.debug(f"needs to fit into [{table.column_num}] slots")

        if len(list) < table.column_num:
            list += [''] * (table.column_num - len(list))
        elif len(list) > table.column_num:
            list = list[: table.column_num]

        logger.debug(f"list doctored to [{list}]")

        data = deepcopy(table.attributes)

        # print(f"Making a datapoint: shortcuts1: {table.attributes}")
        # print(f"Making a datapoint: final data1: {data}")

        for (key,val) in zip(table.column_names, list):
            if ':' in key:
                (key,subkey) = key.split(":") 
                data[key][subkey] = val                    
            else:
                data[key] = val

        print(f"Making a datapoint: shortcuts2: {table.attributes}")
        print(f"Making a datapoint: final data2: {data}")

        self.cells = data

    # def print_data_point( self ):

    #     info_to_print = ""
    #     for i, (k, v) in enumerate( self.cells.items() ):
    #         initial_text = f"{i:03} {k}"
    #         info_to_print = f"{initial_text}"
    #         if isinstance(v, dict):
    #             for (sk, sv) in v.items():
    #                 info_to_print = f"{info_to_print}\n{initial_text} {sk} {sv}\n"
    #         else:
    #             info_to_print = f"{info_to_print}\n{v}\n"
    #     print( info_to_print )

class Peopla:
    """
    A Peopla object
    """

    def __init__(self, input, place_flag=False):
        self.type = "place" if place_flag else "person"
        self.name = input
        self.attributes = {}
        logger.info(f"Creating PEOPLA object: {self.name} ({self.type})")

    def add_attribute(self, attribute_text, inheritance):
        self.attributes[attribute_text] = inheritance
        logger.debug("This is what is to be inherited:")
        print(inheritance)
        logger.info(
            f"Adding attribute to PEOPLA object {self.name}: ({attribute_text})"
        )

    def print_peopla(self):  # pragma: no cover
        logger.debug(f"I found this {self.type} PEOPLA called {self.name}")
        logger.debug("It has the following attributes:")
        print(self.attributes)


class Document:
    """
    A Document object
    """

    def __init__(self, file="", settings_file="settings.yaml"):
        """
        Defining a document object
        """
        logger.info(f"Reading input file: '{file}'")
        self.file = file

        # Read settings file
        logger.info(f"Reading settings file: '{settings_file}'")
        self.read_settings_file(settings_file)

        # Information about the sources
        self.header = defaultdict(list)

        # Saving information about shortcuts
        self.shortcut_live = False
        self.shortcuts = []

        # Saving the Peopla objects
        self.peopla_live = False
        self.peoplas = []

        # Saving the data tables
        self.data_table_live = False
        self.data_tables = []

        # Saving the data points
        self.data_points = []

    def read_settings_file(self, file):
        settings = ""

        with open(file) as stream:
            try:
                settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)

        self.header_tags = ["TITLE"] + settings["header_tags"]
        self.header_length = len(max(self.header_tags, key=len))

        if settings.get("shortcut_mappings") is not None:
            self.shortcut_mappings = dict(
                pair for d in settings["shortcut_mappings"] for pair in d.items()
            )

    def read_document(self):
        """
        Reading a document
        """
        line_num = 0
        with open(self.file, "r") as d:
            for line in d:
                line_num += 1
                logger.debug(f"Reading line #{line_num}: {line.rstrip()}")

                if self.shortcut_live:
                    if not self.scan_for_shortcut_lines(line):
                        self.scan_for_shortcut_definition(line)
                else:
                    self.scan_for_shortcut_lines(line)

                if self.peopla_live:
                    self.scan_for_peopla_attributes(line)
                elif self.data_table_live:
                    self.scan_for_data_points(line)
                else:
                    self.scan_for_data_table_header(line)

                self.scan_for_header_lines(line)
                self.scan_for_peopla_lines(line)

                # print( f"ASDFASDF: {self.shortcuts}")
                self.reset(line)

    def reset(self, line):
        logger.debug(f"Considering reset with: '{line}'")

        if re.match(r"^\s+$", line):
            if self.peopla_live:
                logger.debug("Resetting peopla")
            if self.data_table_live:
                logger.debug("Resetting data table")
            if self.shortcut_live:
                shortcut_dictionary = {}
                for s in self.shortcuts:
                    shortcut_dictionary.update(s)
                self.shortcuts = shortcut_dictionary
                logger.debug( "Resetting shortcut")

            self.peopla_live = False
            self.data_table_live = False
            self.shortcut_live = False

    def scan_for_shortcut_lines(self, line):
        """
        Function that exmaines the current input file from file.
        If it's format corresponds to a shortcut definition,
        a new shortcut object will be created and added to the
        list of shortcuts that are attached to the Document.
        """
        if re.match(rf"^###\t\^\d+:$", line):
            logger.debug(f"Identified shortcut line: '{line}'")

            m = re.search(r"^###\t\^(\d+):$", line)
            shortcut_id = m.group(1)
            logger.debug(f"with shortcut id: {shortcut_id}")

            self.shortcut_live = True
            self.shortcuts.append( { shortcut_id: {} } )
            return( True )
        else:
            return( False )

    def create_inheritance_hash(self, flag):
        h = {}
        if flag == "*":
            h = dict(self.header)
            h.pop("TITLE",None)
        return(h)

    def scan_for_shortcut_definition(self, line):
        if re.match(r"^###\t[^\*\[\]\{\}]+\*?$", line):
            logger.debug("FOUND a short cut definition")

            current_shortcut = self.shortcuts[-1]
            current_shortcut_key = list(current_shortcut.keys())[0]

            m = re.search(r"^###\s*(\!?)([^\*]+)(\*?)$", line)

            property_flag = m.group(1).rstrip()
            action_text = m.group(2).rstrip()
            inheritance_flag = m.group(3).rstrip()

            logger.debug(f"Identified shortcut content: '{property_flag}' / '{action_text}' / '{inheritance_flag}'")

            inheritance_hash = {}

            if property_flag == "!":
                logger.debug(f"a property: {action_text}")
                k = self.shortcut_mappings[action_text]
                inheritance_hash = { k: action_text }
            else:
                logger.debug(f"the header is: {dict(self.header)}" )
                logger.debug(f"self shortcuts: {current_shortcut_key}" )

                inheritance_hash = { action_text: self.create_inheritance_hash(inheritance_flag) }

            (self.shortcuts[-1])[current_shortcut_key].update( inheritance_hash )
            print("Setting self.shortcuts in scan_for_shortcut_definition to:")
            print( self.shortcuts )

            # (self.peoplas[-1]).add_attribute(attribute_text, inheritance_hash)
            # self.peopla_live = True

    def scan_for_data_table_header(self, line):
        """
        Function that exmaines the current input file from file.
        If it's format corresponds to the header of a data table,
        a new object will be created and added to the list of
        data tables that are attached to the Document.
        """

        if re.match(rf"^###{re.escape(data_point_separator)}.*$", line):
            # if re.match(r"^###\t[^\^]{1}.*$", line):
            m = re.search(
                rf"^###{re.escape(data_point_separator)}([^\^]*)(\^\d+)?$", line
            )
            header_content = m.group(1)
            header_shortcut = m.group(2).replace("^","")
            header_columns = header_content.split(data_point_separator)
            logger.debug(f"Identified table header: '{header_content}'")
            logger.debug(f"with {len(header_columns)} columns")
            logger.debug(f"with shortcut: {header_shortcut}")

            # m = re.search(rf"^###{re.escape(data_point_separator)}(.*)$", line)
            # header_content    = m.group(1)
            # header_columns = header_content.split(data_point_separator)
            # logger.debug(f"Identified table header: '{header_content}'")
            # logger.debug(f"with {len(header_columns)} columns")

            logger.debug( "Is this header shortcut correct?????")
            print(self.shortcuts[f"{header_shortcut}"])

            self.data_tables.append(
                DataTable(header_columns, self.shortcuts[f"{header_shortcut}"])
            )
            self.data_table_live = True

    def scan_for_data_points(self, line):
        logger.debug(f"Looking for data table content in {line}")

        current_table = (self.data_tables[-1])

        if re.match(rf"^###{re.escape(data_point_separator)}END$", line):
            logger.debug("End of table")
            self.data_table_live = False
        elif re.match(rf"^\[/\]$", line):
            logger.debug("Ignore (line break not relevant)")
        elif re.match(rf"^!.*$", line):
            logger.debug("Ignore (line starts with !)")
        elif re.match(r"^###\t\{.*\}$", line):
            # --- Functionality to be added ---
            # This is a globcal identifier to be added to the
            # immediately preceeding data point
            logger.debug( f"FOUND a global identifer")
        else:
            content_list = re.split("\t+",line.rstrip())
            logger.debug(f"FOUND {len(content_list)} data points for the table")
            logger.debug(f"This is the current table attributes: {current_table.attributes}")
            self.data_points.append( DataPoint(content_list, current_table ) )
            # (self.data_points[-1]).print_data_point()

    def scan_for_peopla_attributes(self, line):
        logger.debug(f"Looking for peopla attributes in {line}")

        if re.match(r"^###\t\t[^\*]+\*?$", line):
            logger.debug("FOUND a peopla attribute")

            m = re.search(r"^###\t\t([^\*]+)(\*?)$", line)
            attribute_text = m.group(1).rstrip()
            inheritance_flag = m.group(2).rstrip()
            logger.debug(f"Identified '{attribute_text}' / '{inheritance_flag}'")

            inheritance_hash = {}
            if inheritance_flag == "*":
                inheritance_hash = self.header
                inheritance_hash.pop("TITLE")

            (self.peoplas[-1]).add_attribute(attribute_text, inheritance_hash)
            self.peopla_live = True

    def scan_for_peopla_lines(self, line):
        """
        Function that exmaines the current input file from file.
        If it's format corresponds to PEOPLA line, a new object
        will be created and added to the list of PEOPLA that are
        attached to the Document.
        """
        if re.match(r"^###\t@?\[.*\]$", line):
            m = re.search(r"^###\t(\@?)\[(.*?)\]$", line)
            place_flag = m.group(1)
            content = m.group(2)
            logger.debug(f"Identified '{place_flag}' / '{content}'")
            self.peoplas.append(Peopla(content, place_flag == "@"))
            self.peopla_live = True

    def scan_for_header_lines(self, line):
        """
        Function that examines the current input file from file.
        If it's format corresponds to one of the header formats,
        appropriate slots in the corresponding Document objects
        `header` dictionary will be updated with appropriate text.
        """
        if line.startswith("#["):
            m = re.search(r"\[(.*?)\]", line)
            content = m.group(1)
            self.header["TITLE"].append(content)
            logger.info(f"Adding TITLE header attribute '{content}'")
        elif re.match(r"^##\w+:", line):
            m = re.search(r"^##(.*?):\s+(.*?)$", line)
            flag = m.group(1)
            content = m.group(2)
            self.header[flag].append(content)
            logger.info(f"Adding {flag} header attribute '{content}'")

    def print_header_information(self):
        """
        Printing the header information for a document object
        """
        for key, value in self.header.items():
            for i, j in enumerate(value):
                print(f"[{key:{self.header_length}} {i+1:02}]: {j}")

    def print_summary(self):  # pragma: no cover
        """
        Printing a summary of a document
        """
        print(f"Document parsed = {self.file}")
        self.print_header_information()

        for p in self.peoplas:
            p.print_peopla()

        print(self.shortcuts)

        print(f"Found {len(self.data_points)} data points")
        for d in self.data_points:

            df = pd.DataFrame.from_dict(d.cells)
            print( df.index )
            print( df )

    def get_header_information(self, flag):
        """
        Returning the value for a specific flag in a document header
        """
        return self.header[flag]
