from os import listdir, path
from os.path import isfile, join
import os
os.system("python extract.py")
import yaml
import json
import extract
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

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

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

#rules = get_db_rules('db_rules')
#print(rules)
#json_extract = extract.extract_json("../../loul.json")
#api_calls = extract.extract_funcname_list(json_extract)
#print(api_calls)
#print(set_tags(api_calls, rules))

