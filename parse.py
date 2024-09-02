from src.ontologise.utils import Document
import sys
import logging

file_to_parse = "data/p2833, Felicity doubled.txt"


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

logger.info(f"Reading input file: '{file_to_parse}'")

d = Document(file_to_parse)

d.read_document()
d.print_summary()
