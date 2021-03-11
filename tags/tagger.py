from os import listdir, path
from os.path import isfile, join
import yaml #install ruamel.yaml.cmd

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

rules = []

def get_db_rules(directory):
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    for f in files:
        with open(path.join(directory,f), 'r') as rule:
            try:
                yaml_rule = yaml.safe_load(rule)
                rules.append(from_yaml(yaml_rule))
                
            except yaml.YAMLError as exc:
                print(exc)
        


def set_tags():
    tags = []
    
    # parcours des rules 

    return ['None']

get_db_rules('db_rules')
print(rules)