import yaml
from os import listdir, path
from os.path import isfile, join, exists
import yaml
import re


RULES_PATHS = ["tags/db_rules", "/data/db_rules"]


class Rule(object):
    """Represent a Rule used to find specific function call in
    JSON traces and return associated tags.
    """
    YAMLTag = "Rule"

    def __init__(self, name, patterns, tag):
        self.name = name
        self.patterns = patterns
        self.tag = tag


def get_rules(directories):
    """Load rules in memory from yaml files presents in a
    list of directories.

    Args:
        directories (List(String)): List of directories containings rules.

    Returns:
        List(Rule): List of Rule objects.
    """
    rules = []
    files = [
        path.join(d, f)
        for d in directories
        if exists(d)
        for f in listdir(d)
        if isfile(join(d, f))
    ]

    for f in files:
        with open(f, "r") as rule:
            try:
                yaml_rule = yaml.safe_load(rule)
                rules.append(
                    Rule(
                        name=yaml_rule["name"],
                        patterns=yaml_rule["features"],
                        tag=yaml_rule["tag"]
                    )
                )
            except yaml.YAMLError as exc:
                print(exc)
    return rules


def get_apicalls_from_traces(json_list):
    """Extract a Set of windows api calls from Detours traces.

    Args:
        json_list (List(Dict)): List of python dictionnaries.

    Returns:
        List(String): List of unique Windows API calls.
    """
    func_list = set()
    if not "error" in json_list:
        for api_call in json_list:
            func_list.add(api_call["funcName"])
        return func_list
    return ["error"]


def valid_filename(filename):
    """Function to validate user defined filename.

    Args:
        name (String): Filename from user.

    Returns:
        Bool: True if filename is valide, else False.
    """
    return bool(re.match("[0-9a-zA-Z-_]+", filename))
