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

        # logger.info( description_text["info"] )
        # logger.debug( description_text["debug"] )

    def print_description(self):
        s_info = (
            f"{'directed' if self.directed else 'undirected'}{self.type} ActionGroup,"
        )
        s_info = s_info + f"involving the following source Peoplas"

        s_debug = ""
        for n, peopla in enumerate([self.source_peopla]):
            s_debug = s_debug + f"{n}. {peopla}"

        s_info = s_info + f"involving {len(self.target_peoplas)} target Peoplas"

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

    # def add_attribute(self, attribute_text, inheritance, secondary_peopla=None):

    #     # self.attributes[attribute_text]["secondary_peopla"] = secondary_peopla

    #     logger.info(
    #         f"Adding attribute to PEOPLA object {self.name}: ({attribute_text})"
    #     )

    #     if secondary_peopla:
    #         logger.info(
    #             f"NB. attribute includes reference to secondary PEOPLA object {secondary_peopla.name}"
    #         )
    #         logger.debug(
    #             f"This information involves another Peopla: {secondary_peopla.name}"
    #         )
    #         logger.debug(f"Adding this to the inheritance object")
    #         inheritance["with"] = secondary_peopla
    #     else:
    #         logger.debug(f"No other Peopla is involved")

    #     logger.debug(f"This is what is to be inherited:{log_pretty(inheritance)}")

    #     self.attributes[attribute_text] = inheritance

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
        self.current_action = None
        self.current_source_peopla = None
        self.current_target_peoplas = []
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

                self.print_current_status(line_num, line)

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

        elif re.match(r"^###\t(\()?\t[^\*]+\*?$", line):
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

        elif re.match(r"^###\t(vs|w/).*$", line):
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

            self.current_target_peoplas = self.current_target_peoplas + [target_peopla]

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

    def scan_for_peopla_lines(self, line):
        """
        Function that exmaines the current input file from file.
        If it's format corresponds to PEOPLA line, a new object
        will be created and added to the list of PEOPLA that are
        attached to the Document.
        """
        if re.match(r"^###\t@?\[.*\](\(.*\))?(\{.*\})?$", line):
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

            self.current_source_peopla = source_peopla
            self.current_target_peoplas = []

            #########################################################

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

        # print("---------------------\n")
        # print(f"Primary Peoplas:")
        # for p in self.peoplas_primary:
        #     p.print_peopla()

        # print("---------------------\n")
        # print(f"Secondary Peoplas:")
        # for p in self.peoplas_secondary:
        #     p.print_peopla()

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

    m = re.search(r"^(\@)?(w\/)?\[(.*?)\](\(.*\))?(\{.*\})?(\*)?$", l1)

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


def extract_action_scope(l0):
    """
    Extract details of the scope of an action
    This 
    """

    m = re.search(r"^###\t(\S*)\t.*$", l0)

    scope_indicator = m.group(1)

    if scope_indicator == "":
        scope = "both"
    elif scope_indicator == "(":
        scope = "target"
    else:
        scope = None

    return scope


def extract_action_details(l0):
    """
    Parse details from a action line.
    Examples of action lines:
    - ###	(	OF
    - ###       PROPRIETOR*

    """

    l1 = remove_all_leading_action_markup(l0)

    m = re.search(r"^([^\*]+)(\*)?$", l1)
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
    if re.match(r"^###\tvs\[.*$", l0):
        return True
    elif re.match(r"^###\tw\/\[.*$", l0):
        return False
    else:
        return None
