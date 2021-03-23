from os import listdir, path
from os.path import isfile, join
import yaml
import re
# install pyyaml


class Rule(object):
    YAMLTag = 'Rule'
    
    def __init__(self, name, patterns, tag):
        self.name = name
        self.patterns = patterns
        self.tag = tag

    def __repr__(self):
        ret = "{\n" + "  name : " + self.name + ",\n"
        ret += "  patterns : " + str(self.patterns) + ",\n"
        ret += "  tag : " + self.tag + "\n}"
        return ret

    def __str__(self):
        ret = "{\n" + "  name : " + self.name + ",\n"
        ret += "  patterns : " + str(self.patterns) + ",\n"
        ret += "  tag : " + self.tag + "\n}"
        return ret


def from_yaml(node):
    return Rule(name=node['name'], patterns=node['features'], tag=node['tag'])


def get_db_rules(directory):
    rules = []
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    for f in files:
        with open(path.join(directory,f), 'r') as rule:
            try:
                yaml_rule = yaml.safe_load(rule)
                rules.append(from_yaml(yaml_rule))
                
            except yaml.YAMLError as exc:
                print(exc)
    return rules


def valid_filename(name):
    return bool(re.match("[0-9a-zA-Z-_]+", name))
