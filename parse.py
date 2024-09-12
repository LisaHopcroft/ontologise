from src.ontologise.utils import Document

file_to_parse = "data/p2833, Felicity with new format.txt"

d = Document(file_to_parse)

d.read_document()
d.print_summary()
