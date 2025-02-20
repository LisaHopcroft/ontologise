import re
import os
import yaml
from collections import defaultdict
import logging
import pandas as pd
from copy import deepcopy
import pprint


PROJECT_NAME = "Ontologise"
DEFAULT_SETTINGS = "settings.yaml"

data_point_separator = "\\t"

### Regexes to identify specific lines
empty_line_regex = r"^\s+$"
ignore_line_regex = r"^!.*$"
header_line_regex = r"^##\w+:"
shortcut_line_regex = r"^###\t\^\d+:$"
shortcut_definition_regex = r"^###\t[^\*\[\]\{\}]+\*?$"
# peopla_line_regex = r"^###\t@?\[.*\](\(.*\))?(\{.*\})?$"
peopla_line_regex = r"^###\t(>\t)*@?\[.*\](\(.*\))?(\{.*\})?$"
peopla_regex = r"^(\@)?(w\/)?\[(.*?)\](\(.*\))?(\{.*\})?(\*)?$"
peopla_attribute_regex = r"^###\t(\()?\t[^\*]+\*?$"
peopla_relation_line_regex = r"^###\t(\()?(>\t)+\*(.*)\*$"
peopla_relation_depth_regex = r">\t"
peopla_relation_string_regex = r"\*(.*)\*"
peopla_relation_target_regex = r"^###\t(\()?(>\t)+@?\[.*\](\(.*\))?(\{.*\})?$"
peopla_relation_scope_regex = r"^###\t(\(?>).*$"

action_regex = r"^([^\*]+)(\*)?$"
action_attribute_regex = r"^###\t(\()?\t\t[^\*]+\*?$"
# action_group_regex = r"^###\t(vs|w/).*$"
# action_group_vs_regex = r"^###\tvs\[.*$"
# action_group_w_regex = r"^###\tw\/\[.*$"
action_group_regex = r"^###\t(>\t)*(vs|w/).*$"
action_group_vs_regex = r"^###\t(>\t)*vs\[.*$"
action_group_w_regex = r"^###\t(>\t)*w\/\[.*$"

action_scope_regex = r"^###\t(\S*)\t.*$"
data_table_header_regex = rf"^###{re.escape(data_point_separator)}.*$"
data_table_linebreak_regex = r"^\[/\]$"
data_table_id_regex = r"^###\t\{.*\}$"
data_table_end_regex = rf"^###{re.escape(data_point_separator)}END$"


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


class ActionGroup:
    """
    A ActionGroup involves two or more Peoplas
    """

    def __init__(
        self, type, directed=False, source_peopla=[], target_peoplas=[], attributes={}
    ):

        self.type = type
        self.directed = directed
        self.source_peopla = source_peopla
        self.target_peoplas = target_peoplas

        ### Aggributes of the Relationship itself
        self.attributes = attributes

        # description_text = self.print_description()

        ### Evidence reference (line number from original file)
        self.evidence_reference = []

        # logger.info( description_text["info"] )
        # logger.debug( description_text["debug"] )

    def __str__(self):
        out_s = (
            f"{'directed' if self.directed else 'undirected'} {self.type} ActionGroup\n"
        )
        out_s = out_s + f"...involving the following source Peoplas:\n"

        for n, peopla in enumerate([self.source_peopla]):
            out_s = out_s + f"   {n+1}. {peopla.name}\n"

        out_s = out_s + f"...involving {len(self.target_peoplas)} target Peoplas:\n"

        for n, peopla in enumerate(self.target_peoplas):
            out_s = out_s + f"   {n+1}. {peopla.name}\n"

        out_s = out_s + f"...{len(self.evidence_reference)} evidence lines are:\n"

        for n, line_number in enumerate(self.evidence_reference):
            out_s = out_s + f"   {n+1}. {line_number}"

        return out_s

    def print_description(self):
        s_info = f"{'directed' if self.directed else 'undirected'} {self.type} ActionGroup,\n"
        s_info = s_info + f" involving the following source Peoplas\n"

        s_debug = ""
        for n, peopla in enumerate([self.source_peopla]):
            s_debug = s_debug + f"{n}. {peopla}"

        s_info = s_info + f" involving {len(self.target_peoplas)} target Peoplas\n"

        for n, peopla in enumerate(self.target_peoplas):
            s_debug = s_debug + f"{n}. {peopla}"

        return {"info": s_info, "debug": s_debug}

    def update_attribute(self, attribute_text, d):

        logger.info(
            f"Adding attribute to ACTION GROUP object {self.type}: ({attribute_text})"
        )

        existing_attributes = {}
        if attribute_text in self.attributes:
            existing_attributes = self.attributes[attribute_text]
        updated_attributes = {**existing_attributes, **d}

        logger.debug(
            f"This is what exists at the moment:{log_pretty(existing_attributes)}"
            f"This is what needs to be added: {log_pretty(d)}"
            f"This is what it is going to look like: {log_pretty(updated_attributes)}"
        )

        self.attributes[attribute_text] = updated_attributes


class Peorel:
    """
    A Peorel object - relationship between two people
    """

    def __init__(
        self, peopla_is, peopla_to, relation_text, relation_depth, details_hash=None
    ):

        self.relation_text = relation_text
        self.relation_depth = relation_depth
        self.peopla_is = peopla_is
        self.peopla_to = peopla_to

        ### Attributes of the Peorel itself
        self.attributes = details_hash

        ### Evidence reference (line number from original file)
        self.evidence_reference = []

        logger.info(
            f"Creating a PEOREL object: {self.peopla_is.name} is a {self.relation_text} to {self.peopla_to.name} (depth={self.relation_depth})"
        )

    ### What needs to match for two PEOREL objects to be considered the same?
    def __eq__(self, other):
        return_result = False

        if (
            self.relation_text == other.relation_text
            and self.relation_depth == other.relation_depth
            and self.peopla_is.name == other.peopla_is.name
            and self.peopla_to.name == other.peopla_to.name
            and self.peopla_is.global_id == other.peopla_is.global_id
            and self.peopla_is.local_id == other.peopla_is.local_id
        ):
            return_result = True

        return return_result
        # return self.__dict__ == other.__dict__

    def __str__(self):  # pragma: no cover
        evidence_string = ",".join(str(x) for x in self.evidence_reference)

        s_out = (
            f"{self.peopla_is.name} is a {self.relation_text} to {self.peopla_to.name} "
        )
        s_out = s_out + "[Evidence: " + evidence_string + "]"

        return s_out


class Peopla:
    """
    A Peopla object
    """

    def __init__(self, input, place_flag=False, local_id=None, global_id=None):
        self.type = "place" if place_flag else "person"
        self.name = input

        ### Aggributes of the Peopla itself
        self.attributes = {}
        ### Any ActionGroups that are relevant to this Peopla
        self.action_groups = []

        ### IDs for the Peoplas
        self.global_id = global_id
        self.local_id = local_id

        ### Evidence reference (line number from original file)
        self.evidence_reference = []

        logger.info(
            f"Creating a PEOPLA object: {self.name} ({self.type}) ({self.local_id}) ({self.global_id})"
        )

    # def add_relationship(self, peorel):

    #     self.peorels = self.peorels + peorel

    #     logger.info(
    #         f"Adding a {peorel} {peorel.type} relationship to PEOPLA object {self.name}"
    #     )

    #     logger.debug(
    #         f"- {peorel.type} actor relationship to PEOPLA object {self.name}"
    #     )

    def new_add_action(self, action_text, inheritance):

        # self.attributes[attribute_text]["secondary_peopla"] = secondary_peopla

        logger.info(
            f"NEW Adding attribute to PEOPLA object {self.name}: ({action_text})"
        )
        logger.debug(f"This is what is to be inherited:{log_pretty(inheritance)}")

        self.attributes[action_text] = inheritance

    def update_attribute(self, attribute_text, d):

        logger.info(
            f"Adding attribute to PEOPLA object {self.name}: ({attribute_text})"
        )

        existing_attributes = {}
        if attribute_text in self.attributes:
            existing_attributes = self.attributes[attribute_text]
        updated_attributes = {**existing_attributes, **d}

        logger.debug(
            f"This is what exists at the moment:{log_pretty(existing_attributes)}"
            f"This is what needs to be added: {log_pretty(d)}"
            f"This is what it is going to look like: {log_pretty(updated_attributes)}"
        )

        self.attributes[attribute_text] = updated_attributes

    def __str__(self):  # pragma: no cover
        s_out = f"{self.type} PEOPLA called {self.name}\n"

        evidence_string = ",".join(str(x) for x in self.evidence_reference)

        s_out = s_out + "Evidence: lines " + evidence_string + "\n"

        if self.global_id:
            s_out = s_out + f"...with the global ID: {self.global_id}\n"
        if self.local_id:
            s_out = s_out + f"...with the local ID: {self.local_id}\n"

        if len(self.attributes) == 0:
            s_out = s_out + f"...with no attributes\n"
        else:
            s_out = (
                s_out
                + f"...and the following attributes:\n{log_pretty(self.attributes)}"
            )

            if "GENDER" in self.attributes:

                print(self.attributes["GENDER"]["evidence"])

                s_out = (
                    s_out
                    + f"...further information for gender evidence (if we have it):\n"
                )

                for this_peorel_evidence in self.attributes["GENDER"]["evidence"]:
                    s_out = s_out + format(this_peorel_evidence) + "\n"

        return s_out


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
        self.current_line = 0

        # Read settings file
        logger.info(f"Reading settings file: '{settings_file}'")
        self.add_settings_to_document(settings_file)

        # Information about the sources
        self.header = defaultdict(list)

        # Saving information about shortcuts
        self.shortcut_live = False
        self.shortcuts = []

        #############################################################
        ### OLD VERSION (being used for w/ relationships) ###########
        #############################################################
        # # Saving the Peopla objects
        # self.peopla_live = False
        # self.peoplas_primary = []
        # # Saving the Peopla objects that are derived from action_groups
        # self.peopla_action_group_live = False
        # self.peoplas_secondary = []
        #############################################################

        #############################################################
        ### NEW VERSION (being used for the vs action groups) #######
        #############################################################
        self.peopla_live = False
        self.all_peoplas = []
        self.all_action_groups = []
        self.all_peorels = []
        self.current_action = None
        self.current_source_peopla = None
        self.current_target_peoplas = []

        self.current_source_peopla_breadcrumbs = []
        self.current_target_peopla_breadcrumbs = []

        self.relation_live = False
        self.relation_text = None
        self.relation_depth = 0

        self.peopla_action_group_live = False
        self.peopla_action_group_directed = False
        #############################################################

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

    def read_document(self, pause_threshold=1):
        """
        Reading a document
        """

        with open(self.file, "r") as d:
            for line in d:
                self.current_line += 1
                self.current_breadcrumb_depth = get_depth(line)

                logger.debug(f"Reading line #{self.current_line}: {line.rstrip()}")

                if self.shortcut_live:
                    if not self.scan_for_shortcut_lines(line):
                        self.scan_for_shortcut_definition(line)
                else:
                    self.scan_for_shortcut_lines(line)

                if self.data_table_live:
                    self.scan_for_data_points(line)
                else:
                    if self.peopla_live:
                        self.scan_for_peopla_attributes(line)

                    self.scan_for_data_table_header(line)

                self.scan_for_header_lines(line)
                self.scan_for_peopla_lines(line)

                ### It is possible for there to be blank lines inside a peopla
                if not self.peopla_live:
                    self.reset(line)

                self.print_current_status(self.current_line, line)

                if not "PYTEST_CURRENT_TEST" in os.environ:
                    if self.current_line >= pause_threshold:
                        input()

        ### flatten the datapoints into a table here
        self.data_points_df = self.generate_table_from_datapoints()

    def print_current_status(self, n, l):

        status_update = (
            "=================================================================\n"
        )

        ### Headers -------------------------------------------------

        if len(self.header) > 0:
            status_update = (
                status_update + f"There are currently {len(self.header)} header items\n"
            )

            for i, p in enumerate(self.header):
                status_update = status_update + f"Header item ({i}) {p}\n"

        status_update = status_update + f"Just read line number [{n}]\n"
        status_update = status_update + f"The content was [{l}]\n"

        status_update = status_update + "------------------------------------\n"

        status_update = (
            status_update
            + f"There are {len(self.all_peoplas)} Peoplas recorded overall\n"
        )

        for ii, pp in enumerate(self.all_peoplas):
            status_update = status_update + f"---> Peopla #({ii}) {pp.name}\n"

        status_update = status_update + "------------------------------------\n"

        if self.current_source_peopla != None:
            status_update = (
                status_update
                + f"The current source Peopla is {self.current_source_peopla.name}\n"
            )

            for k, v in self.current_source_peopla.attributes.items():
                status_update = (
                    status_update + f"--> Current source peopla attribute ({k}) {v}\n"
                )

        else:
            status_update = status_update + f"There is no current source Peopla\n"

        status_update = status_update + "------------------------------------\n"

        if len(self.current_target_peoplas) > 0:
            status_update = (
                status_update
                + f"There are currently {len(self.current_target_peoplas)} target Peoplas\n"
            )

            for i, p in enumerate(self.current_target_peoplas):
                status_update = status_update + f"({i}) {p.name}\n"

                for j, q in enumerate(p.attributes):
                    status_update = (
                        status_update
                        + f"--> Current target peopla attribute ({i}) {q}\n"
                    )

                    for k, v in (p.attributes)[q].items():
                        status_update = status_update + f"------> ({k}) {v}\n"

        else:
            status_update = status_update + f"There is no current target Peopla\n"

        status_update = status_update + "------------------------------------\n"

        ### Breadcrumbs ---------------------------------------------

        status_update = status_update + f"The current source peopla breadcrumbs:\n"

        num_source_breadcrumbs = len(self.current_source_peopla_breadcrumbs)

        status_update = (
            status_update
            + f"---> There are {num_source_breadcrumbs} SOURCE peopla breadcrumbs populated:\n"
        )

        for i, b in enumerate(self.current_source_peopla_breadcrumbs):
            status_update = status_update + f"SOURCE [{i}] {format(b)}\n"

        status_update = status_update + "------------------------------------\n"

        status_update = status_update + f"The current target peopla breadcrumbs:\n"

        num_target_breadcrumbs = len(self.current_target_peopla_breadcrumbs)

        status_update = (
            status_update
            + f"---> There are {num_target_breadcrumbs} TARGET peopla breadcrumbs populated:\n"
        )

        for i, b in enumerate(self.current_target_peopla_breadcrumbs):
            if b:
                for j, bj in enumerate(b):
                    status_update = status_update + f"TARGET [{i}.{j}] {format(bj)}\n"
            else:
                status_update = status_update + f"TARGET [{i}] is absent\n"

        ### Peorels -------------------------------------------------

        status_update = (
            status_update
            + f"There are {len(self.all_peorels)} Peorels recorded overall\n"
        )

        for ii, pp in enumerate(self.all_peorels):
            evidence_string = ",".join(str(x) for x in pp.evidence_reference)
            status_update = (
                status_update
                + f"---> Peorel #({ii}) {pp.peopla_is.name} is a {pp.relation_text} to {pp.peopla_to.name} [refs: {evidence_string}]\n"
            )

        status_update = status_update + "------------------------------------\n"

        ### Action groups -------------------------------------------

        if len(self.all_action_groups) > 0:
            status_update = (
                status_update
                + f"There are currently {len(self.all_action_groups)} Action Groups\n"
            )

            for i, p in enumerate(self.all_action_groups):
                status_update = status_update + f"({i}) {p.type}\n"
                status_update = status_update + f"    directed? {p.directed}\n"
                status_update = (
                    status_update + f"    source peopla? {p.source_peopla.name}\n"
                )
                status_update = (
                    status_update + f"    target peoplas? {len(p.target_peoplas)}\n"
                )

                for j, q in enumerate(p.target_peoplas):
                    status_update = (
                        status_update
                        + f"------> target peopla in action group ({i}) {q.name}\n"
                    )

                status_update = (
                    status_update + f"    attributes? length = {len(p.attributes)}\n"
                )

                for k, v in (p.attributes).items():
                    status_update = status_update + f"------> ({k}) {v}\n"

        ### Indicators ----------------------------------------------

        status_update = status_update + "------------------------------------\n"

        relevant_live_indicators = [
            "shortcut_live",
            "peopla_live",
            "peopla_action_group_live",
            "relation_live",
            "data_table_live",
        ]

        for r in relevant_live_indicators:
            status_update = status_update + f"The [{r}] flag is {getattr(self,r)}\n"

        status_update = (
            status_update
            + "================================================================="
        )

        logger.debug(status_update)

        # input()

    def reset(self, line):  # pragma: no cover
        logger.debug(f"Considering reset with: '{line}'")

        if re.match(empty_line_regex, line):
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
            self.relation_live = False

            self.current_relation_text = None
            self.current_relation_depth = 0
            self.current_breadcrumb_depth = 0

    def scan_for_shortcut_lines(self, line):
        """
        Function that examines the current input file from file.
        If its format corresponds to a shortcut definition,
        a new shortcut object will be created and added to the
        list of shortcuts that are attached to the Document.
        """
        if re.match(shortcut_line_regex, line):
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
        if re.match(shortcut_definition_regex, line):
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

        if re.match(data_table_header_regex, line):
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

            self.peopla_live = False
            self.data_table_live = True

    def scan_for_data_points(self, line):
        logger.debug(f"Looking for data table content in {line}")

        current_table = self.data_tables[-1]

        if re.match(data_table_end_regex, line):
            logger.debug("End of table")
            self.data_table_live = False
        elif re.match(data_table_linebreak_regex, line):
            logger.debug("Ignore (line break not relevant)")
        elif re.match(ignore_line_regex, line):
            logger.debug("Ignore (line starts with !)")
        elif re.match(data_table_id_regex, line):
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

        if re.match(peopla_relation_line_regex, line):
            logger.debug("Found a peopla relationship")

            relation_details = extract_relation_details(line)

            logger.debug(
                f"Identified that a '{relation_details['relation_text']}' relationship is now live"
            )
            logger.debug(
                f"Context will dictate which Peopla are involved in that Peorel"
            )

            self.current_relation_text = relation_details["relation_text"]
            self.current_relation_depth = relation_details["relation_depth"]
            self.relation_live = True

        elif re.match(peopla_relation_target_regex, line) and self.relation_live:
            ### If we're in here, we've got a relation open
            ### AND we have found what the target is of that relation

            peopla_content_parsed = extract_peopla_details(line)

            ### Who is the target of the relation?
            relation_peopla_is_tmp = Peopla(
                peopla_content_parsed["content"],
                peopla_content_parsed["place_flag"],
                peopla_content_parsed["local_id"],
                peopla_content_parsed["global_id"],
            )

            relation_peopla_is = self.record_peopla(relation_peopla_is_tmp)
            record_evidence(relation_peopla_is, self.current_line)

            logger.debug(
                f"Found the target of a relation action: '{relation_peopla_is.name}'"
            )
            logger.debug(
                f"This will be in relation to the {self.current_relation_text} relation (depth={self.current_relation_depth})"
            )
            logger.debug(f"But need to work out who the 'to' Peopla is")

            ### Creating this here so that we can catch it and record it as evidence
            ### in the case of gendered relations
            new_peorel = []

            ### This is where we have a relation attached directly to a single Peopla
            if not self.peopla_action_group_live:

                logger.debug(
                    f"The context tells us that the 'to' peopla for this peorel is the current source peopla: {self.current_source_peopla}"
                )

                relevant_source_peopla = self.current_source_peopla_breadcrumbs[
                    self.current_breadcrumb_depth - 1
                ]

                print(
                    f"*** The 'is' peopla is {relation_peopla_is.name}\n",
                    f"*** The 'to' peopla will be the the source peopla (there is no target for this relation)\n",
                    f"*** The current_source_peopla is {self.current_source_peopla.name}\n",
                    f"*** The current_source_peopla (as breadcrumbs) is\n",
                    self.print_source_breadcrumbs(),
                    f"*** The current breadcrumb depth is {self.current_breadcrumb_depth}\n",
                    f"*** The relevant source peopla is {relevant_source_peopla.name}\n",
                )

                peorel_tmp = Peorel(
                    relation_peopla_is,
                    relevant_source_peopla,
                    self.current_relation_text,
                    self.current_relation_depth,
                )

                this_new_peorel = self.record_peorel(peorel_tmp)
                record_evidence(this_new_peorel, self.current_line)
                new_peorel.append(this_new_peorel)

            ### This is where we have a relation attached to an open ActionGroup
            ### It will be indicated with a ( as to whether the relation refers to
            ### to the target Peopla(s) only or to the source AND target peoplas
            else:

                relation_scope = extract_relation_scope(line)

                logger.debug(
                    f"The context tells us that the 'to' peopla for this peorel is something to do with the target peopla"
                )

                logger.debug(f"The scope for this is: {relation_scope}")

                # -----------------------------

                # print( f"The current target peopla breadcrumbs (to be used where relation depth is {self.current_relation_depth}):\n")

                # num_target_breadcrumbs = len(self.current_target_peopla_breadcrumbs)

                # print( f"---> There are {num_target_breadcrumbs} TARGET peopla breadcrumbs populated:\n")

                # for i,b in enumerate(self.current_target_peopla_breadcrumbs):
                #     for j,bj in enumerate( b ):
                #         print( f"TARGET [{i}.{j}] {format(bj)}\n" )

                # relevant_to_peopla_list = deepcopy(self.current_target_peoplas)

                # print( f"The relevant depth is {self.current_relation_depth}:\n")

                relevant_to_peopla_list = deepcopy(
                    self.current_target_peopla_breadcrumbs[
                        (self.current_breadcrumb_depth - 1)
                    ]
                )
                tt = ""
                for n, x in enumerate(self.current_target_peoplas):
                    tt = f"{tt}[{n}] {x.name}\n"

                print(
                    f"*** The 'is' peopla is {relation_peopla_is.name}\n",
                    f"*** The 'to' peopla will be source AND target peopla\n",
                    f"*** There are {len(self.current_target_peoplas)} current_target_peoplas\n",
                    tt,
                    f"*** The current_target_peopla (as breadcrumbs) is\n",
                    self.print_target_breadcrumbs(),
                    f"*** The current breadcrumb depth is {self.current_breadcrumb_depth}\n",
                    f"*** There are {len(relevant_to_peopla_list)} relevant target_peopla\n",
                )

                # input()

                # _relevant_to_peopla_list = self.current_target_peopla_breadcrumbs[0]
                # relevant_to_peopla_list = _relevant_to_peopla_list[(self.current_relation_depth-1)]

                logger.debug("Current to_peopla_list (step 1) - the target peoplas")
                logger.debug(relevant_to_peopla_list)

                if relation_scope == "target":
                    logger.debug(
                        f"This information is only relevant for the target peopla"
                    )
                    logger.debug(f"No need to do anything more")
                else:
                    logger.debug(
                        f"This information is relevant for the source and target peopla"
                    )
                    logger.debug(
                        f"Need to add the current source peopla to the 'to' list"
                    )

                    # # -----------------------------

                    # print( f"The current source peopla breadcrumbs (to be used where relation depth is {self.current_relation_depth}):\n")

                    # num_source_breadcrumbs = len(self.current_source_peopla_breadcrumbs)

                    # print( f"---> There are {num_source_breadcrumbs} SOURCE peopla breadcrumbs populated:\n")

                    # for i,b in enumerate(self.current_source_peopla_breadcrumbs):
                    #     print( f"SOURCE [{i}] {format(b)}\n" )

                    # # -----------------------------

                    relevant_source_peopla = self.current_source_peopla_breadcrumbs[
                        (self.current_breadcrumb_depth) - 1
                    ]

                    relevant_to_peopla_list.append(relevant_source_peopla)
                    logger.debug(
                        "Current to_peopla_list (step 2) - adding the source peoplas"
                    )
                    logger.debug(relevant_to_peopla_list)

                    print(
                        f"*** The context indicated that the source people needed to be added as well\n",
                        f"*** The current_source_peopla is {self.current_source_peopla.name}\n",
                        f"*** The current_source_peopla (as breadcrumbs) is\n",
                        self.print_source_breadcrumbs(),
                        f"*** The current breadcrumb depth is {self.current_breadcrumb_depth}\n",
                        f"*** There are now {len(relevant_to_peopla_list)} relevant 'to' peopla\n",
                    )

                for this_to_peopla in set(relevant_to_peopla_list):
                    peorel_tmp = Peorel(
                        relation_peopla_is,
                        this_to_peopla,
                        self.current_relation_text,
                        self.current_relation_depth,
                    )

                    this_new_peorel = self.record_peorel(peorel_tmp)
                    record_evidence(this_new_peorel, self.current_line)
                    new_peorel.append(this_new_peorel)

            ### If we have a gendered relation, we can augment the Peopla with this
            ### Gender information. The evidence for this (i.e., the relevant Peorel
            ### objects should be recorded alongside this inference).

            relation_peopla_is.update_attribute(
                "GENDER",
                {
                    "value": gender_inference_from_relation(self.current_relation_text),
                    "evidence": new_peorel,
                },
            )

            self.relation_live = False
            self.current_relation_text = None
            self.current_relation_depth = 0

        elif re.match(action_attribute_regex, line):
            logger.debug("Found an attribute of an action")
            logger.debug(
                f"This will be in relation to the {self.current_action} action"
            )

            action_scope = extract_action_scope(line)

            line_content = re.sub(r"^###[\s\(]+", "", line)
            info = extract_attribute_information(line_content)
            logger.debug(
                f"Identified '{self.current_action}' / '{info}' "  # / '{peopla_to_update.name}'"
            )

            if self.peopla_action_group_live:

                if action_scope == "both":
                    ### This is an attribute for an action that occurs between
                    ### members of an action group. We need to update the action
                    ### group to have this attribute. So:
                    ### 1. Find the action group
                    ### 2. Add the attributes

                    ###logger.critical("This has not been implemented yet")

                    self.all_action_groups[-1].update_attribute(
                        self.current_action, info
                    )

                elif action_scope == "target":
                    ### This is only relevant for the LAST target peoplas
                    ### We need to add an attribute to a peopla

                    self.current_target_peoplas[-1].update_attribute(
                        self.current_action, info
                    )

                    logger.debug(
                        f"Adding [{self.current_action}] attribute to {self.current_target_peoplas[-1].name}"
                    )

            else:
                ### This is an attribute for an action that belongs to a Peopla
                ### that is not part of an action group. So:
                ### 1. Find the Peopla
                ### 2. Add the attributes

                self.current_source_peopla.update_attribute(self.current_action, info)

        elif re.match(peopla_attribute_regex, line):
            logger.debug("Found a peopla attribute")

            # m = re.search(r"^###\t(\()?\t([^\*]+)(\*?)$", line)
            # secondary_flag = False if m.group(1) is None else True
            # attribute_text = m.group(2).rstrip()
            # inheritance_flag = m.group(3).rstrip()
            action_scope = extract_action_scope(line)
            action_details = extract_action_details(line)

            self.current_action = action_details["action_text"]

            logger.debug(f"The action scope is {action_scope}")
            logger.debug(
                f"Identified '{action_details['action_text']}' / '{action_details['inheritance_flag']}'"
            )

            inheritance_hash = {}
            if action_details["inheritance_flag"]:
                inheritance_hash = self.header
                inheritance_hash.pop("TITLE")

            ### What we have found here is an action of an action group
            if self.peopla_action_group_live:
                if action_scope == "both":
                    ### This is a description of an action between an action group
                    ### We need to make a action_group

                    ag = ActionGroup(
                        action_details["action_text"],
                        directed=self.peopla_action_group_directed,
                        source_peopla=self.current_source_peopla,
                        target_peoplas=self.current_target_peoplas,
                        attributes=inheritance_hash,
                    )
                    record_evidence(ag, self.current_line)

                    o = ag.print_description()
                    logger.info(o["info"])
                    logger.debug(o["debug"])

                    self.all_action_groups = self.all_action_groups + [ag]

                elif action_scope == "target":
                    ### This is only relevant for the LAST target peoplas
                    ### We need to add an attribute to a peopla

                    self.current_action = action_details["action_text"]

                    ### If this information is relevant for the primary Peopla
                    ### AND we have a action_group currently live (i.e., a secondary
                    ### Peopla that is part of this action_group) then that secondary
                    ### Peopla should be recorded as part of the action_group
                    # secondary_peopla_object = None
                    # if not secondary_flag and self.peopla_action_group_live:
                    #     logger.debug(
                    #         f"This is information that defines a action_group between two Peoplas"
                    #     )
                    #     logger.debug(f"1. primary  : {self.peoplas_primary[-1].name}")
                    #     logger.debug(f"2. secondary: {self.peoplas_secondary[-1].name}")
                    #     secondary_peopla_object = self.peoplas_secondary[-1]

                    ### Work out which Peopla we should update with the information -
                    ### the primary or the secondary Peopla
                    # peopla_to_update = (
                    #     (self.peoplas_secondary[-1])
                    #     if secondary_flag
                    #     else (self.peoplas_primary[-1])
                    # )
                    # logger.critical("This has not been implemented yet")

                    for tp in self.current_target_peoplas:
                        logger.debug(
                            f"Adding [{action_details['action_text']}] attribute to {tp.name}"
                        )

                        tp.update_attribute(self.current_action, inheritance_hash)

            ### What we have found here is an action of a Peopla
            ### (the current Source peopla)
            else:
                self.current_action = action_details["action_text"]
                self.current_source_peopla.new_add_action(
                    action_details["action_text"], inheritance_hash
                )

            # Maybe this shouldn't be removed????
            # self.peopla_live = True

        # elif re.match(r"^###\tw/.*$", line):
        #     logger.debug("Found a peopla action_group")

        #     peopla_content = re.sub(r"^###\s+", "", line)

        #     logger.debug(f"Parsed out this content: {peopla_content}")

        #     peopla_content_parsed = extract_peopla_details(peopla_content)

        #     self.peoplas_secondary.append(
        #         Peopla(
        #             peopla_content_parsed["content"],
        #             peopla_content_parsed["place_flag"],
        #             peopla_content_parsed["local_id"],
        #             peopla_content_parsed["global_id"],
        #         )
        #     )

        #     ### Open an action group
        #     self.peopla_action_group_live = True
        #     self.peopla_action_group_directed = False

        elif re.match(action_group_regex, line):
            logger.debug("Found an ActionGroup")

            # peopla_content = remove_all_leading_markup(line)
            # logger.debug(f"Parsed out this content: {peopla_content}")

            peopla_content_parsed = extract_peopla_details(line)
            direction_flag = is_action_group_directed(line)

            target_peopla_tmp = Peopla(
                peopla_content_parsed["content"],
                peopla_content_parsed["place_flag"],
                peopla_content_parsed["local_id"],
                peopla_content_parsed["global_id"],
            )

            target_peopla = self.record_peopla(target_peopla_tmp)
            record_evidence(target_peopla, self.current_line)

            self.current_target_peoplas = self.current_target_peoplas + [target_peopla]
            # self.current_target_peoplas.append(target_peopla)

            # new_target_peoplas = []

            # if self.current_breadcrumb_depth <= (len(self.current_target_peopla_breadcrumbs)-1):
            #     new_target_peoplas = deepcopy(self.current_target_peopla_breadcrumbs[self.current_breadcrumb_depth])

            new_target_peoplas = [target_peopla]

            print(
                f"^^^^^^^^^^^^^^^^^^^^^ num target peoplas { len(new_target_peoplas) }"
            )
            for n, t in enumerate(new_target_peoplas):
                print(f"^^^^^^^^^^^^^^^^^^^^^ ({n}) {t}")

            ### (3) reset the source/target breadcrumbs
            # self.current_target_peopla_breadcrumbs[self.relation_depth] = self.current_target_peoplas

            print(f"IN HERE __________{line}\n")
            print(f"IN HERE __________{get_depth(line)}")

            self.current_target_peopla_breadcrumbs = update_breadcrumbs(
                deepcopy(self.current_target_peopla_breadcrumbs),
                self.current_breadcrumb_depth,
                # deepcopy(self.current_target_peoplas),
                new_target_peoplas,
                "TARGET",
            )

            ### Open an action group
            self.peopla_action_group_live = True
            self.peopla_action_group_directed = direction_flag

    def record_peopla(self, p):

        peopla_ref = p
        already_recorded = False

        for this_p in self.all_peoplas:
            if this_p.name == p.name and (
                this_p.local_id == p.local_id or this_p.global_id == p.global_id
            ):
                already_recorded = True
                peopla_ref = this_p
                break

        if not already_recorded:
            logger.debug(f"This is a new Peopla that should be recorded ({p.name})")
            self.all_peoplas = self.all_peoplas + [peopla_ref]
        else:
            logger.debug(f"We have already seen this peopla ({p.name})")

        return peopla_ref

    def print_source_breadcrumbs(self):
        n = len(self.current_target_peopla_breadcrumbs)

        o = f"BREADCRUMBS | SOURCE | {n} populated breadcrumbs\n"

        for i, b in enumerate(self.current_source_peopla_breadcrumbs):
            o = o + f"BREADCRUMBS | SOURCE | [{i}] {format(b)}\n"

        return o

    def print_target_breadcrumbs(self):
        n = len(self.current_target_peopla_breadcrumbs)

        o = f"BREADCRUMBS | TARGET | {n} populated breadcrumbs\n"

        for i, b in enumerate(self.current_target_peopla_breadcrumbs):
            if b:
                for j, bj in enumerate(b):
                    o = o + f"BREADCRUMBS | TARGET | [{i}.{j}] {format(bj)}\n"
            else:
                o = o + f"BREADCRUMBS | TARGET | [{i}] is absent\n"

        return o

    def record_peorel(self, pr):

        peorel_ref = pr
        already_recorded = False

        for this_peorel in self.all_peorels:
            if this_peorel == pr:
                already_recorded = True
                peorel_ref = this_peorel
                break

        if not already_recorded:
            logger.debug(
                f"This is a new Peorel that should be recorded ({pr.peopla_is.name} is {pr.relation_text} to {pr.peopla_to.name})"
            )
            self.all_peorels = self.all_peorels + [peorel_ref]
        else:
            logger.debug(
                f"We have already seen this peorel ({pr.peopla_is.name} is {pr.relation_text} to {pr.peopla_to.name})"
            )

        return peorel_ref

    def scan_for_peopla_lines(self, line):
        """
        Function that exmaines the current input file from file.
        If it's format corresponds to PEOPLA line, a new object
        will be created and added to the list of PEOPLA that are
        attached to the Document.
        """
        if re.match(peopla_line_regex, line):
            # m = re.search(r"^###\t(\@?)\[(.*?)\](\(.*\))?(\{.*\})?$", line)
            # place_flag = m.group(1)
            # content = m.group(2)
            # local_id = None
            # if m.group(3):
            #     local_id = re.sub("[\(\)]", "", m.group(3))
            # global_id = None
            # if m.group(4):
            #     global_id = re.sub("[\{\}]", "", m.group(4))
            # logger.debug(
            #     f"Identified '{place_flag}' / '{content}' / '{local_id}'/ '{global_id}'"
            # )
            # self.peoplas_primary.append(Peopla(content, place_flag == "@", local_id, global_id))

            ### New version #########################################
            # peopla_content = remove_all_leading_markup(line)
            # logger.debug(f"Parsed out this content: {peopla_content}")
            peopla_content_parsed = extract_peopla_details(line)

            source_peopla_tmp = Peopla(
                peopla_content_parsed["content"],
                peopla_content_parsed["place_flag"],
                peopla_content_parsed["local_id"],
                peopla_content_parsed["global_id"],
            )

            source_peopla = self.record_peopla(source_peopla_tmp)
            record_evidence(source_peopla, self.current_line)

            #########################################################

            ### If we're making a new Peopla object and we're at the top level,
            ### then everything needs to be reset.
            ### We don't want to reset everything otherwise, as we might be in
            ### a string of relations and we don't want to loose the existing source
            ### and target Peoplas (see the test test_gender_evidence_is_correct()
            ### for example of a string of relations).

            this_depth = len(re.findall(peopla_relation_depth_regex, line))

            if this_depth == 0:
                ### (1) reset what our source and target peoplas are
                self.current_source_peopla = source_peopla
                self.current_target_peoplas = []

                ### (2) reset relevant live flags
                self.peopla_live = True
                self.peopla_action_group_live = False
                self.relation_live = False
                self.relation_depth = 0

                ### (3) reset the source/target breadcrumbs
                self.current_source_peopla_breadcrumbs = []
                self.current_source_peopla_breadcrumbs.append(source_peopla)
                self.current_target_peopla_breadcrumbs = []
            else:
                self.current_source_peopla_breadcrumbs = update_breadcrumbs(
                    deepcopy(self.current_source_peopla_breadcrumbs),
                    this_depth,
                    deepcopy(source_peopla),
                    "SOURCE",
                )

                new_target_list = deepcopy(self.current_target_peopla_breadcrumbs)[
                    :this_depth
                ]

                self.current_target_peopla_breadcrumbs = new_target_list

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
        elif re.match(header_line_regex, line):
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

    def __str__(self):  # pragma: no cover
        """
        Compiling a toString for a document
        """
        s_out = f"Document parsed = {self.file}\n"
        for key, value in self.header.items():
            for i, j in enumerate(value):
                s_out = s_out + f"[{key:{self.header_length}} {i+1:02}]: {j}\n"

        s_out = s_out + "\n"
        s_out = s_out + "---------------------\n"
        s_out = s_out + "Shortcuts:\n"
        for i, v in enumerate(self.shortcuts):
            s_out = s_out + f"[{i}: {v}]\n"

        s_out = s_out + "\n"
        s_out = s_out + "---------------------\n"
        s_out = s_out + "All Peoplas:\n"
        for i, p in enumerate(self.all_peoplas):
            s_out = s_out + f"[{i}] " + str(p) + "\n"

        s_out = s_out + "\n"
        s_out = s_out + "---------------------\n"
        s_out = s_out + "All Peorels:\n"
        for i, p in enumerate(self.all_peorels):
            s_out = s_out + f"[{i}] " + str(p) + "\n"

        s_out = s_out + "\n"
        s_out = s_out + "---------------------\n"
        s_out = s_out + "All ActionGroups:\n"
        for i, p in enumerate(self.all_action_groups):
            s_out = s_out + f"[{i}] " + str(p) + "\n"

        s_out = s_out + "\n"
        s_out = s_out + "---------------------\n"
        s_out = s_out + f"Found {len(self.data_points)} data points\n"

        s_out = s_out + str(self.data_points_df)

        return s_out

    def print_summary(self):  # pragma: no cover
        """
        Printing a summary of a document
        """
        print(f"Document parsed = {self.file}")
        self.print_header_information()

        print("---------------------\n")
        print("Shortcuts:")
        print(self.shortcuts)

        print("---------------------\n")
        print(f"All Peoplas:")
        for i, p in enumerate(self.all_peoplas):
            logger.info(f"[{i}] " + str(p))

        print("---------------------\n")
        print(f"All Peorels:")
        for i, p in enumerate(self.all_peorels):
            logger.info(f"[{i}] " + str(p))

        print("---------------------\n")
        print(f"All ActionGroups:")
        for i, p in enumerate(self.all_action_groups):
            logger.info(f"[{i}] " + str(p))

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

    return {key: value}


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
    return {":": "DATE", "@": "AT",}.get(x, x)


def remove_all_leading_peopla_markup(l):
    """
    Removes markup, but retains the @ for place peoplas
    """
    return re.sub(r"^###[^@]*(\@?)(\[)", r"\1\2", l)


def remove_all_leading_action_markup(l):
    """
    Removes markup, but retains the @ for place peoplas
    """
    return re.sub(r"^###\t(\S*)\t", "", l)


def remove_all_leading_relation_markup(l):
    """
    Removes markup
    """
    return re.sub(r"^###\t", "", l)


def extract_peopla_details(l0):
    """
    Parse details from a peopla line.
    Examples of peopla lines:
    - ###   [ADAM, Jean](5){80071ca9-d47a-4cb6-b283-f96ce7ad1618}
    - ###   [CRAWFURD, Andrew](x){5cf88045-6337-428c-ab5b-8ea9b1a50103}
    - ###   [M'TURK, Michael]
    - ###   [M'TURK, Michael]*
    - ###   @[SCO, REN, LWH, Johnshill]
    """

    l1 = remove_all_leading_peopla_markup(l0)

    m = re.search(peopla_regex, l1)

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


def extract_relation_scope(l0):
    """
    Extract details of the scope of an action
    This
    """

    m = re.search(peopla_relation_scope_regex, l0)

    scope = None

    if m is not None:
        scope_indicator = m.group(1)

        if scope_indicator == ">":
            scope = "both"
        elif scope_indicator == "(>":
            scope = "target"

    return scope


def extract_action_scope(l0):
    """
    Extract details of the scope of an action
    This 
    """

    m = re.search(action_scope_regex, l0)

    scope_indicator = m.group(1)

    if scope_indicator == "":
        scope = "both"
    elif scope_indicator == "(":
        scope = "target"
    else:
        scope = None

    return scope


def extract_relation_details(l0):
    """
    Parse details from a relation line.
    Examples of action lines:
    - ###	>	*SON*
    - ###	>	>	*DAUG*
    - ###	>	*FATHER*
    Where the closed vocabulary is:
    * SON
    * DAUG
    * FATHER
    * MOTHER
    """

    l1 = remove_all_leading_relation_markup(l0)

    relation_depth = len(re.findall(peopla_relation_depth_regex, l1))

    m = re.search(peopla_relation_string_regex, l1)
    relation_text = m.group(1)

    logger.debug(
        f"Extracting relationship information:\n"
        + f" - relationship depth ? '{relation_depth}'\n"
        + f" - relationship text ? '{relation_text}'"
    )

    relationship_info_dictionary = {
        "relation_text": relation_text,
        "relation_depth": relation_depth,
    }

    return relationship_info_dictionary


def extract_action_details(l0):
    """
    Parse details from a action line.
    Examples of action lines:
    - ###	(	OF
    - ###       PROPRIETOR*

    """

    l1 = remove_all_leading_action_markup(l0)

    m = re.search(action_regex, l1)
    action_text = m.group(1).rstrip()
    inheritance_flag = False if m.group(2) is None else True

    logger.debug(
        f"New method for extracting action details:\n"
        + f" - attribute_text is ? '{action_text}'\n"
        + f" - inheritance flag provided? '{inheritance_flag}'"
    )

    action_info_dictionary = {
        "action_text": action_text,
        "inheritance_flag": inheritance_flag,
    }

    return action_info_dictionary


def is_action_group_directed(l0):
    if re.match(action_group_vs_regex, l0):
        return True
    elif re.match(action_group_w_regex, l0):
        return False
    else:
        return None


relation_gender_mapping = {
    "DAUG": "FEMALE",
    "MOTHER": "FEMALE",
    "SON": "MALE",
    "FATHER": "MALE",
}


def gender_inference_from_relation(t):
    inferred_gender = "UNKNOWN"
    if t in relation_gender_mapping:
        inferred_gender = relation_gender_mapping[t]
    return inferred_gender


def record_evidence(object, line_number):
    existing_list = object.evidence_reference
    existing_list.append(line_number)
    object.evidence_reference = sorted(set(existing_list))


def update_breadcrumbs(existing_list, update_depth, update_object, label=""):
    logger.debug(
        f"!!!!!!!!!!!!! [UPDATE {label} BCs] The update depth is {update_depth}"
    )
    logger.debug(
        f"!!!!!!!!!!!!! [UPDATE {label} BCs] Updating breadcrumbs from this ({len(existing_list)} items):\n"
    )
    # for i,x in enumerate( existing_list ):
    #     f"!!!!!!!!!!!!! [UPDATE {label} BCs] [{i}] {x.name}\n"

    # Remove everything including the level that is to be updated
    new_list = existing_list[:(update_depth)]

    # If you are updating something at a deeper level and you don't have an
    # entry for a higher level, need to add a None to show that that was missing
    # (this can happen where there isn't a Target peopla at a higher level (see
    # nested_pedictree_A3.txt).
    if update_depth > (len(new_list)):
        new_list = pad_with_none(new_list, update_depth)

    # Append the new object (this will be at the correct depth)
    new_list.append(update_object)

    logger.debug(
        f"!!!!!!!!!!!!! [UPDATE {label} BCs] to this: ({len(new_list)} items)\n"
    )
    # for i,x in enumerate( new_list ):
    #     f"!!!!!!!!!!!!! [UPDATE {label} BCs] [{i}] {x.name}\n"

    # input()

    return new_list


def pad_with_none(l, n, pad=None):
    if len(l) >= n:
        return l[:n]
    return l + ([pad] * (n - len(l)))


def get_depth(l):
    return len(re.findall(peopla_relation_depth_regex, l))
