import re

class Document:
    def __init__(self, file=""):

        self.file = file

        ### Information about the sources
        self.source_list = []

    def read_document(self):
        with open(self.file, "r") as d:
            for l in d:
                self.scan_for_source_header(l)

    def scan_for_source_header(self, l):
        if l.startswith("#["):
            m = re.search(r"\[(.*?)\]", l)
            self.source_list.append( m.group(1) )

    def print_summary(self):
        print(f"Document parsed = {self.file}")
        print(f"Contained {len(self.source_list)} sources")

        for order, source_name in enumerate(self.source_list):
            print(f"[{order+1:02}]: {source_name}")

    def get_source_list(self):
        return self.source_list
