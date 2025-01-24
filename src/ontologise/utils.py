import re
import yaml
from collections import defaultdict
import logging
import pandas as pd
from copy import deepcopy
import pprint


PROJECT_NAME = "Ontologise"
DEFAULT_SETTINGS = "settings.yaml"

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
    # format = "\033[1m [%(name)s][%(levelname)-5s][%(funcName)s][%(filename)s] \033[0m \n%(message)s"
    debug_format = (
        "\033[1m🪲 [%(filename)s::%(funcName)s::%(lineno)d]\033[0m\n%(message)s"
    )
    info_format = "\033[1m%(message)s"
    format = "\033[1m%(message)s"

    FORMATS = {
        logging.DEBUG: cyan + debug_format + reset,
        logging.INFO: grey + info_format + reset,
        logging.WARNING: magenta + format + reset,
        logging.ERROR: bold_red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(PROJECT_NAME.upper())
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

# set up pretty printer
# https://stackoverflow.com/questions/77991049/is-there-a-way-to-print-a-formatted-dictionary-to-a-python-log-file
pp = pprint.PrettyPrinter(indent=2, sort_dicts=False)


def log_pretty(obj):
    pretty_out = f"{pp.pformat(obj)}"
    return f"{pretty_out}\n"


def read_settings_file(file):
    settings = ""

    with open(file) as stream:
        try:
            settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    return settings


def flatten_dict(nested_dict):
    res = {}
    if isinstance(nested_dict, dict):
        for k in nested_dict:
            flattened_dict = flatten_dict(nested_dict[k])
            for key, val in flattened_dict.items():
                key = list(key)
                key.insert(0, k)
                res[tuple(key)] = val
    else:
        res[()] = nested_dict
    return res


class DataTable:
    def __init__(self, fields, shortcuts):
        self.column_names = fields
        self.column_num = len(fields)
        self.attributes = shortcuts

        logger.info("Creating a table")
        logger.debug(f" - {self.column_num} columns")
        logger.debug(f" - Column names: {','.join(self.column_names)}")
        logger.debug(f" - Attributes are: {self.attributes}")


class DataPoint:
    def __init__(self, list, table):

        logger.info("Creating a datapoint")
        logger.debug(f" - data point list provided [{list}]")
        logger.debug(f" - needs to fit into [{table.column_num}] slots")

        if len(list) < table.column_num:
            list += [""] * (table.column_num - len(list))
        elif len(list) > table.column_num:
            list = list[: table.column_num]

        logger.debug(f" - list doctored to [{list}]")

        data = deepcopy(table.attributes)

        for (key, val) in zip(table.column_names, list):
            if ":" in key:
                (key, subkey) = key.split(":")
                data[key][subkey] = val
            else:
                data[key] = val

        self.cells = data
        self.global_id = None

    def add_global_id(self, id):
        self.global_id = id


class Peopla:
    """
    A Peopla object
    """

    def __init__(self, input, place_flag=False, local_id=None, global_id=None):
        self.type = "place" if place_flag else "person"
        self.name = input
        self.attributes = {}
        self.relationships = {}
        self.global_id = global_id
        self.local_id = local_id

        logger.info(
            f"Creating a PEOPLA object: {self.name} ({self.type}) ({self.local_id}) ({self.global_id})"
        )

    def add_relationship(self, relationship_text, relationship_target):

        logger.info(
            f"Adding relationship to PEOPLA object {self.name}: ({relationship_text})"
        )
        
        # ...

        self.attributes[relationship_text] = relationship_target

    def add_attribute(self, attribute_text, inheritance, secondary_peopla=None):

        # self.attributes[attribute_text]["secondary_peopla"] = secondary_peopla

        logger.info(
            f"Adding attribute to PEOPLA object {self.name}: ({attribute_text})"
        )

        if secondary_peopla:
            logger.info(
                f"NB. attribute includes reference to secondary PEOPLA object {secondary_peopla.name}"
            )
            logger.debug(
                f"This information involves another Peopla: {secondary_peopla.name}"
            )
            logger.debug(f"Adding this to the inheritance object")
            inheritance["secondary"] = secondary_peopla
        else:
            logger.debug(f"No other Peopla is involved")

        logger.debug(f"This is what is to be inherited:{log_pretty(inheritance)}")

        self.attributes[attribute_text] = inheritance

    def update_attribute(self, attribute_text, d):

        # self.attributes[attribute_text]["secondary_peopla"] = secondary_peopla

        logger.info(
            f"Adding attribute to PEOPLA object {self.name}: ({attribute_text})"
        )

        existing_attributes = self.attributes[attribute_text]
        updated_attributes = { **existing_attributes, **d }

        logger.debug(
            f"This is what exists at the moment:{log_pretty(existing_attributes)}"
            f"This is what needs to be added: {log_pretty(d)}"
            f"This is what it is going to look like: {log_pretty(updated_attributes)}"
        )

        self.attributes[attribute_text] = updated_attributes

    def print_peopla(self):  # pragma: no cover
        logger.info(f"I found this {self.type} PEOPLA called {self.name}")
        logger.info(f"It has the following attributes:\n{log_pretty(self.attributes)}")
        if self.global_id:
            logger.info(f"It has the following global ID: {self.global_id}")


class Document:
    """
    A Document object
    """

    def __init__(self, file="", settings_file="settings.yaml"):
        """
        Defining a document object
        """

        logger.info(f"Creating a document object from:\n - {file}\n - {settings_file})")

        self.file = file

        # Read settings file
        logger.info(f"Reading settings file: '{settings_file}'")
        self.add_settings_to_document(settings_file)

        # Information about the sources
        self.header = defaultdict(list)

        # Saving information about shortcuts
        self.shortcut_live = False
        self.shortcuts = []

        # Saving the Peopla objects
        self.peopla_live = False
        self.peoplas_primary = []

        # Saving the Peopla objects that are derived from action_groups
        self.peopla_action_group_live = False
        self.peoplas_secondary = []

        # Saving the data tables
        self.data_table_live = False
        self.data_tables = []

        # Saving the data points
        self.data_points = []

    def add_settings_to_document(self, file):

        logger.info(f"Reading settings file [{file}]")

        settings = read_settings_file(file)

        logger.info(f"{log_pretty(settings)}")

        self.settings_file = file
        self.header_tags = ["TITLE"] + settings["header_tags"]
        self.header_length = len(max(self.header_tags, key=len))

        if settings.get("shortcut_mappings") is not None:
            self.shortcut_mappings = dict(
                pair for d in settings["shortcut_mappings"] for pair in d.items()
            )

            logger.info(f"Shortcut mappings provided:")
            logger.info(f"{log_pretty(self.shortcut_mappings)}")

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

                ### It is possible for there to be blank lines inside a peopla
                if not self.peopla_live:
                    self.reset(line)

        ### flatten the datapoints into a table here
        self.data_points_df = self.generate_table_from_datapoints()

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
                logger.debug("Resetting shortcut")
                logger.debug(
                    f"Shortcut dictionary has been created: {shortcut_dictionary}"
                )

            self.peopla_live = False
            self.data_table_live = False
            self.shortcut_live = False

    def scan_for_shortcut_lines(self, line):
        """
        Function that examines the current input file from file.
        If it's format corresponds to a shortcut definition,
        a new shortcut object will be created and added to the
        list of shortcuts that are attached to the Document.
        """
        if re.match(r"^###\t\^\d+:$", line):
            logger.debug(f"Identified shortcut line: '{line}'")

            m = re.search(r"^###\t\^(\d+):$", line)
            shortcut_id = m.group(1)
            logger.debug(f"with shortcut id: {shortcut_id}")

            self.shortcut_live = True
            self.shortcuts.append({shortcut_id: {}})
            return True
        else:
            return False

    def create_inheritance_hash(self, flag):
        h = {}
        if flag == "*":
            h = dict(self.header)
            h.pop("TITLE", None)
        return h

    def scan_for_shortcut_definition(self, line):
        if re.match(r"^###\t[^\*\[\]\{\}]+\*?$", line):
            logger.debug("Found a short cut definition")

            current_shortcut = self.shortcuts[-1]
            current_shortcut_key = list(current_shortcut.keys())[0]

            m = re.search(r"^###\s*(\!?)([^\*]+)(\*?)$", line)

            property_flag = m.group(1).rstrip()
            action_text = m.group(2).rstrip()
            inheritance_flag = m.group(3).rstrip()

            logger.debug(
                f"Identified shortcut content: '{property_flag}' / '{action_text}' / '{inheritance_flag}'"
            )

            inheritance_hash = {}

            if property_flag == "!":
                logger.debug(f"a property: {action_text}")
                k = self.shortcut_mappings[action_text]
                inheritance_hash = {k: action_text}
            elif inheritance_flag == "*":
                logger.debug(f"the header is: {dict(self.header)}")
                logger.debug(f"self shortcuts: {current_shortcut_key}")

                inheritance_hash = {
                    action_text: self.create_inheritance_hash(inheritance_flag)
                }
            else:
                logger.warning(f"shortcut format not recognised: {line}")

            (self.shortcuts[-1])[current_shortcut_key].update(inheritance_hash)
            logger.debug("Setting self.shortcuts in scan_for_shortcut_definition to:")
            logger.debug(self.shortcuts)

    def scan_for_data_table_header(self, line):
        """
        Function that exmaines the current input file from file.
        If it's format corresponds to the header of a data table,
        a new object will be created and added to the list of
        data tables that are attached to the Document.
        """

        if re.match(rf"^###{re.escape(data_point_separator)}.*$", line):
            ### Previous approach where only one caret was present:
            # m = re.search(
            #     rf"^###{re.escape(data_point_separator)}([^\^]*)(\^\d+)?$", line
            # )
            # header_content = m.group(1)
            # header_shortcut = m.group(2).replace("^","")
            # header_columns = header_content.split(data_point_separator)
            # logger.debug(f"Identified table header: '{header_content}'")
            # logger.debug(f"with {len(header_columns)} columns")
            # logger.debug(f"with shortcut: {header_shortcut}")

            ### Now we can have more than one shortcut
            m = re.search(
                rf"^###{re.escape(data_point_separator)}([^\^]*)([\^\d]+)$", line
            )

            header_content = m.group(1)
            header_shortcuts = list(filter(None, m.group(2).split("^")))
            header_columns = header_content.split(data_point_separator)
            logger.debug(f"Identified table header: '{header_content}'")
            logger.debug(f"with {len(header_columns)} columns")
            logger.debug(f"with shortcut: {header_shortcuts}")

            logger.debug(f"Shortcuts are: {log_pretty(self.shortcuts)}\n")
            # m = re.search(rf"^###{re.escape(data_point_separator)}(.*)$", line)
            # header_content    = m.group(1)
            # header_columns = header_content.split(data_point_separator)
            # logger.debug(f"Identified table header: '{header_content}'")
            # logger.debug(f"with {len(header_columns)} columns")

            logger.debug(
                f"Is/are the header shortcut(s) ({header_shortcuts}) correct?????"
            )

            ### check: are all the shortcuts present in the table header
            ###        actually defined in the document header?

            check = all(e in list(self.shortcuts.keys()) for e in header_shortcuts)

            if check:
                logger.debug(
                    f"--> All shortcut keys ({','.join(header_shortcuts)}) have been defined in the header"
                )
            else:
                missing_definitions = [
                    e for e in header_shortcuts if e not in list(self.shortcuts.keys())
                ]
                logger.debug(
                    f"--> Some shortcut keys ({','.join(missing_definitions)}) have been NOT been defined in the header"
                )
                logger.debug(self.shortcuts)

            ### Extract only the shortcut information required for this table
            relevant_header_shortcuts = {k: self.shortcuts[k] for k in header_shortcuts}
            logger.debug(
                "Extracting only the shortcut information required for this table\n"
            )
            logger.debug(relevant_header_shortcuts)

            ### Combine the shortcut information into one dictionary (this is necessary where
            ### more than one shortcut marker has been applied to the table)
            relevant_header_shortcuts_combined = {}
            for d in relevant_header_shortcuts.values():
                relevant_header_shortcuts_combined.update(d)

            logger.debug("Combine the header shortcut information\n")
            logger.debug(relevant_header_shortcuts_combined)

            ### Add the definition of this table to the document
            self.data_tables.append(
                DataTable(header_columns, relevant_header_shortcuts_combined)
            )

            self.data_table_live = True

    def scan_for_data_points(self, line):
        logger.debug(f"Looking for data table content in {line}")

        current_table = self.data_tables[-1]

        if re.match(rf"^###{re.escape(data_point_separator)}END$", line):
            logger.debug("End of table")
            self.data_table_live = False
        elif re.match(r"^\[/\]$", line):
            logger.debug("Ignore (line break not relevant)")
        elif re.match(r"^!.*$", line):
            logger.debug("Ignore (line starts with !)")
        elif re.match(r"^###\t\{.*\}$", line):
            m = re.search(r"^###\t\{(.*)\}$$", line)
            global_id = m.group(1).rstrip()
            logger.debug(f"Found a global identifer: {global_id}")
            self.data_points[-1].add_global_id(global_id)
        else:
            content_list = re.split("\t+", line.rstrip())
            logger.debug(f"Found {len(content_list)} data points for the table")
            logger.debug(
                f"This is the current table attributes: {current_table.attributes}"
            )
            self.data_points.append(DataPoint(content_list, current_table))
            # (self.data_points[-1]).print_data_point()

    def generate_table_from_datapoints(self):
        datapoint_table = pd.DataFrame()

        for d in self.data_points:
            d_dict_tuples = flatten_dict(d.cells)
            d_dict_flat = {}
            for k, v in d_dict_tuples.items():
                new_key = "_".join(k)
                d_dict_flat[new_key] = v
            d_df = pd.DataFrame.from_dict(d_dict_flat)

            d_df["global_id"] = d.global_id

            datapoint_table = pd.concat([datapoint_table, d_df])

        return datapoint_table.reset_index().drop(columns=["index"])

    def scan_for_peopla_attributes(self, line):

        logger.debug(f"Looking for peopla attributes in {line}")

        # if re.match(r"^###\t(\(>)?\t\*([^\*]*)\*$", line):
        #     logger.debug("Found a relationship that belongs to the current secondary Peopla")
        # elif re.match(r"^###\t(>)?\t\*([^\*]*)\*$", line):
        #     logger.debug("Found a relationship that belongs to BOTH the primary and secondary Peopla")
        # if re.match(r"^###\t(\()?\>\t(.*)$", line):
        #     m = re.search(r"^###\t(\()?\>\t(.*)$", line)
        #     scope_flag = "both" if m.group(1) is None else "secondary"
        #     text_to_parse = m.group(2)
        #     logger.debug( f"This is the scope flag: '{scope_flag}'" )
        #     logger.debug(f"This is the text to parse: '{text_to_parse}'")

        if re.match(r"^###\t(\()?\t\t[^\*]+\*?$", line):
            logger.debug("Found an attribute of an attribute")
            logger.debug(f"This will be in relation to {self.current_attribute}")

            m = re.search(r"^###\t(\()?\t([^\*]+)(\*?)$", line)
            secondary_flag = False if m.group(1) is None else True
            if secondary_flag:
                logger.debug(f"This information is relevant to the secondary Peopla")
            else:
                logger.debug(f"This information is relevant to the primary Peopla")

            ### Work out which Peopla we should update with the information -
            ### the primary or the secondary Peopla
            peopla_to_update = (
                (self.peoplas_secondary[-1])
                if secondary_flag
                else (self.peoplas_primary[-1])
            )

            line_content = re.sub(r"^###[\s\(]+", "", line )

            info = extract_attribute_information( line_content )

            logger.debug(
                f"Identified '{self.current_attribute}' / '{info}' / '{peopla_to_update.name}'"
            )

            ### Add this information to the attribute dictionary
            peopla_to_update.update_attribute( self.current_attribute, info )

        elif re.match(r"^###\t(\()?\t[^\*]+\*?$", line):
            logger.debug("Found a peopla attribute")

            m = re.search(r"^###\t(\()?\t([^\*]+)(\*?)$", line)
            secondary_flag = False if m.group(1) is None else True
            attribute_text = m.group(2).rstrip()
            inheritance_flag = m.group(3).rstrip()
            if secondary_flag:
                logger.debug(f"This information is relevant to the secondary Peopla")
            else:
                logger.debug(f"This information is relevant to the primary Peopla")
            logger.debug(
                f"Identified '{attribute_text}' / '{inheritance_flag}' / '{secondary_flag}'"
            )

            self.current_attribute = attribute_text

            inheritance_hash = {}
            if inheritance_flag == "*":
                inheritance_hash = self.header
                inheritance_hash.pop("TITLE")

            ### If this information is relevant for the primary Peopla
            ### AND we have a action_group currently live (i.e., a secondary
            ### Peopla that is part of this action_group) then that secondary
            ### Peopla should be recorded as part of the action_group
            secondary_peopla_object = None
            if not secondary_flag and self.peopla_action_group_live:
                logger.debug(
                    f"This is information that defines a action_group between two Peoplas"
                )
                logger.debug(f"1. primary  : {self.peoplas_primary[-1].name}")
                logger.debug(f"2. secondary: {self.peoplas_secondary[-1].name}")
                secondary_peopla_object = self.peoplas_secondary[-1]

            ### Work out which Peopla we should update with the information -
            ### the primary or the secondary Peopla
            peopla_to_update = (
                (self.peoplas_secondary[-1])
                if secondary_flag
                else (self.peoplas_primary[-1])
            )

            peopla_to_update.add_attribute(
                attribute_text, inheritance_hash, secondary_peopla_object
            )

            self.peopla_live = True

        elif re.match(r"^###\tw/.*$", line):
            logger.debug("Found a peopla action_group")

            peopla_content = re.sub(r"^###\s+", "", line)

            logger.debug(f"Parsed out this content: {peopla_content}")

            peopla_content_parsed = extract_peopla_details(peopla_content)

            self.peoplas_secondary.append(
                Peopla(
                    peopla_content_parsed["content"],
                    peopla_content_parsed["place_flag"],
                    peopla_content_parsed["local_id"],
                    peopla_content_parsed["global_id"],
                )
            )

            self.peopla_action_group_live = True

    def scan_for_peopla_lines(self, line):
        """
        Function that exmaines the current input file from file.
        If it's format corresponds to PEOPLA line, a new object
        will be created and added to the list of PEOPLA that are
        attached to the Document.
        """
        if re.match(r"^###\t@?\[.*\](\(.*\))?(\{.*\})?$", line):
            m = re.search(r"^###\t(\@?)\[(.*?)\](\(.*\))?(\{.*\})?$", line)
            place_flag = m.group(1)
            content = m.group(2)
            local_id = None
            if m.group(3):
                local_id = re.sub("[\(\)]", "", m.group(3))
            global_id = None
            if m.group(4):
                global_id = re.sub("[\{\}]", "", m.group(4))
            logger.debug(
                f"Identified '{place_flag}' / '{content}' / '{local_id}'/ '{global_id}'"
            )
            self.peoplas_primary.append(Peopla(content, place_flag == "@", local_id, global_id))
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

        print("---------------------\n")
        print(f"Primary Peoplas:")
        for p in self.peoplas_primary:
            p.print_peopla()

        print("---------------------\n")
        print(f"Secondary Peoplas:")
        for p in self.peoplas_secondary:
            p.print_peopla()

        print("---------------------\n")
        print("Shortcuts:")
        print(self.shortcuts)

        print("---------------------\n")
        print(f"Found {len(self.data_points)} data points")
        print(self.data_points_df)

    def get_header_information(self, flag):
        """
        Returning the value for a specific flag in a document header
        """
        return self.header[flag]

def extract_attribute_information(l):
    """
    Parse details from an attribute line.
    Examples of attribute lines:
    - @[SCO, REN, LWH, Johnshill] (belongs to, e.g., OF)
    - :[1762-06] (belongs to, e.g., BORN)
    - :[1810-11->1818] (belongs to, e.g., EDUCATED)
    - :[1819-12->] (belongs to, e.g., HEALTH)
    - :[1820->]~ (belongs to, e.g., RESIDED)
    - CONDITION[Typhus fever] (belongs to, e.g., HEALTH)
    - ROLE[Clerk] (belongs to, e.g., OCC)
    - DUR[1 yr] (belongs to, e.g., OCC)
    """

    m = re.search(r"^(.*)\[(.*)\](~)?$", l)
    key = translate_attribute(m.group(1))
    approx_flag = False if m.group(3) is None else True
    value = f"approx. {m.group(2)}" if approx_flag else m.group(2)

    return({key: value})

### This is what we could do with Python 3.10
# def translate(x):
#     match x:
#         case ':':
#             return "DATE"
#         case '@':
#             return "AT"
#         case _:
#             return x
def translate_attribute(x):
    return {
        ':': "DATE",
        '@': "AT",
    }.get(x, x)


def extract_peopla_details(l):
    """
    Parse details from a peopla line.
    Examples of peopla lines:
    - [ADAM, Jean](5){80071ca9-d47a-4cb6-b283-f96ce7ad1618}
    - w/[CRAWFURD, Andrew](x){5cf88045-6337-428c-ab5b-8ea9b1a50103}
    - [M'TURK, Michael]
    - [M'TURK, Michael]*
    - @[SCO, REN, LWH, Johnshill]
    """

    m = re.search(r"^(\@)?(w\/)?\[(.*?)\](\(.*\))?(\{.*\})?(\*)?$", l)

    place_flag = False if m.group(1) is None else True
    with_flag = False if m.group(2) is None else True
    content = m.group(3)
    local_id = None if m.group(4) is None else re.sub("[\(\)]", "", m.group(4))
    global_id = None if m.group(5) is None else re.sub("[\{\}]", "", m.group(5))
    inheritance_flag = False if m.group(6) is None else True

    logger.debug(
        f"New method for extracting peopla details:\n"
        + f" - is place flag present? '{place_flag}'\n"
        + f" - is a with flag present? '{with_flag}'\n"
        + f" - content is? '{content}'\n"
        + f" - local_id provided? '{local_id}'\n"
        + f" - global_id provided? '{global_id}'\n"
        + f" - inheritance flag provided? '{inheritance_flag}'"
    )

    peopla_info_dictionary = {
        "place_flag": place_flag,
        "with_flag": with_flag,
        "content": content,
        "local_id": local_id,
        "global_id": global_id,
        "inheritance_flag": inheritance_flag,
    }

    return peopla_info_dictionary
