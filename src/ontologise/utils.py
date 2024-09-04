import re
import yaml
from collections import defaultdict
import logging


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

        # Saving the Peopla objects
        self.peopla_live = False
        self.peoplas = []

    def read_settings_file(self, file):
        settings = ""

        with open(file) as stream:
            try:
                settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.error(exc)

        self.header_tags = ["TITLE"] + settings["header_tags"]
        self.header_length = len(max(self.header_tags, key=len))

    def read_document(self):
        """
        Reading a document
        """
        line_num = 0
        with open(self.file, "r") as d:
            for line in d:
                line_num += 1
                logger.debug(f"Reading line #{line_num}: {line.rstrip()}")
                self.scan_for_header_lines(line)
                self.scan_for_peopla_lines(line)
                if self.peopla_live:
                    self.scan_for_peopla_attributes(line)

                self.reset(line)

    def reset(self, line):
        logger.debug(f"Considering reset with: '{line}'")

        if re.match(r"^\s+$", line):
            if self.peopla_live:
                logger.debug("Resetting peopla")

            self.peopla_live = False

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

    def get_header_information(self, flag):
        """
        Returning the value for a specific flag in a document header
        """
        return self.header[flag]
