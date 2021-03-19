import yaml
from os import listdir, path
from os.path import isfile, join
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
    return Rule(name = node['name'],
    patterns = node['features'],
    tag = node['tag'])


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


def check_ransomware(dict_tags):
    ransomware_tags = {"Write File/Directory": 15, "Read File/Directory": 15, "Crypto": 10}
    for k in dict_tags:
        for key in ransomware_tags:
            if k == key and dict_tags[k] >= ransomware_tags[key]:
                return "Ransomware"
    
    return None

def check_keylogger(dict_tags):
    keylogger_tags = {"Keyboard": 1}
    for k in dict_tags:
        for key in keylogger_tags:
            if k == key and dict_tags[k] >= keylogger_tags[key]:
                return "Keylogger"

    return None

def check_obfuscation(dict_tags):
    obfuscation_tags = {"GetProcess": 30, "Obfuscation": 1}
    for k in dict_tags:
        for key in obfuscation_tags:
            if k == key and dict_tags[k] >= obfuscation_tags[key]:
                return "Obfuscation"

    return None

def check_family(dict_tags):
    if check_ransomware(dict_tags) != None:
        return "Ransomware"
    elif check_keylogger(dict_tags) != None:
        return "Keylogger"
    elif check_obfuscation(dict_tags) != None:
        return "Obfuscation"
    return None
