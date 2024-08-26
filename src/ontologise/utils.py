import re
from collections import defaultdict

header_flags = ["TITLE", "AT", "ATX", "DATE"]
header_length = len(max(header_flags, key=len))


class Document:
    """
    A Document object
    """

    def __init__(self, file=""):
        """
        Defining a document object
        """
        self.file = file

        # Information about the sources
        self.header = defaultdict(list)

    def read_document(self):
        """
        Reading a document
        """
        with open(self.file, "r") as d:
            for line in d:
                self.scan_for_header_lines(line)

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
        elif re.match(r"^##\w+:", line):
            m = re.search(r"^##(.*?):\s+(.*?)$", line)
            flag = m.group(1)
            content = m.group(2)
            self.header[flag].append(content)

    def print_header_information(self):
        """
        Printing the header information for a document object
        """
        for key, value in self.header.items():
            for i, j in enumerate(value):
                print(f"[{key:{header_length}} {i+1:02}]: {j}")

    def print_summary(self):
        """
        Printing a summary of a document
        """
        print(f"Document parsed = {self.file}")
        self.print_header_information()

    def get_header_information(self, flag):
        """
        Returning the value for a specific flag in a document header
        """
        return self.header[flag]
