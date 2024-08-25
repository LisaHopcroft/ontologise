import re
from collections import defaultdict

header_flags = ["TITLE", "AT", "ATX", "DATE"]
header_length = len( max(header_flags, key=len) )

class Document:
    def __init__(self, file=""):

        self.file = file

        ### Information about the sources
        self.header = defaultdict(list)

    def read_document(self):
        with open(self.file, "r") as d:
            for l in d:
                self.scan_for_header_lines(l)

    def scan_for_header_lines(self, l):
        if l.startswith("#["):
            m = re.search(r"\[(.*?)\]", l)
            content = m.group(1)
            self.header["TITLE"].append(content)
        elif re.match(r"^##\w+:", l):
            m = re.search(r"^##(.*?):\s+(.*?)$", l)
            flag = m.group(1)
            content = m.group(2)
            self.header[flag].append(content)

    def print_header_information(self):
        print(
            "------------------------------------------------------------------------"
        )
        for key, value in self.header.items():
            for i, j in enumerate(value):
                print(f"[{key:{header_length}} {i+1:02}]: {j}")
            print(
                "------------------------------------------------------------------------"
            )

    def get_source_list(self):
        return self.source_list

    def print_summary(self):
        print(f"Document parsed = {self.file}")

        self.print_header_information()
        # print( dict(self.header) )

    def get_header_information(self,flag):
        return self.header[flag]
    

