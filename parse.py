from src.ontologise.utils import Document

# file_to_parse = "data/p2833, Felicity with new format sample.txt"
# d = Document(file_to_parse)

file_to_parse = "data/p2833, Felicity with new format multiple shortcuts.txt"
d = Document(file_to_parse, settings_file="settings2.yaml")

d.read_document()
d.print_summary()
