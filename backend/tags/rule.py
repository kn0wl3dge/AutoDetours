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


def check_type(dict_tags, reference):
    for k in dict_tags:
        for key in reference:
            if k == key and dict_tags[k] >= reference[key]:
                return True

    return False


def check_family(dict_tags):
    ransomware_tags = {"Write File/Directory": 15,
                       "Read File/Directory": 15, "Crypto": 10}
    keylogger_tags = {"Keyboard": 1}
    obfuscation_tags = {"GetProcess": 30, "Obfuscation": 1}
    spyware_tags = {"Camera": 1}
    c2_tags = {"C2": 1}
    if check_type(dict_tags, ransomware_tags) != False:
        return "Ransomware"
    elif check_type(dict_tags, keylogger_tags) != False:
        return "Keylogger"
    elif check_type(dict_tags, obfuscation_tags) != False:
        return "Obfuscation"
    elif check_type(dict_tags, spyware_tags) != False:
        return "Spyware"
    elif check_type(dict_tags, c2_tags) != False:
        return "RAT/Trojan"
    
    return "Unknown"
