from src.ontologise.utils import Document

# file_to_parse = "data/p2833, Felicity with new format sample.txt"
# d = Document(file_to_parse)

file_to_parse = "data/p2833, Felicity with new format multiple shortcuts stop_at_global_id.txt"
d = Document(file_to_parse, settings_file="settings2.yaml")

# file_to_parse = "data/p2833, Felicity.txt"
# d = Document(file_to_parse, settings_file="settings.yaml")


d.read_document()
d.print_summary()
