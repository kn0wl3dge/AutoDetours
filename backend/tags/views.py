from os import listdir, remove
from os.path import isfile, join, exists

from rest_framework.response import Response
from rest_framework.views import APIView

from tags.rule import Rule, RULES_PATHS, valid_filename


DATA_RULES = "/data/db_rules/"


class RuleFormView(APIView):
    def post(self, request):
        rule = request.data["rule"]
        if not valid_filename(rule):
            return Response({"error": "Name format is incorrect"})
        functions = request.data["functions"]
        tag = request.data["tag"]
        with open(DATA_RULES + rule.lower() + ".yml", "w") as f:
            f.write("name: %s\n" % rule)
            f.write("features:\n")
            for func in functions:
                f.write("   - %s\n" % func)
            f.write("tag: %s" % tag)
        return Response({"success": "Rule has been uploaded"})

    def get(self, request):
        rules_list = []
        files = [
            join(d, f)
            for d in RULES_PATHS
            if exists(d)
            for f in listdir(d)
            if isfile(join(d, f))
        ]
        for filename in files:
            with open(filename, "r") as f:
                content = f.readlines()
                new_rule = Rule(name="", patterns=[], tag="")
                is_pattern = False
                for line in content:
                    if "tag: " in line:
                        is_pattern = False
                        new_rule.tag = line.split(": ")[1].rstrip()
                    if "name: " in line:
                        new_rule.name = line.split(": ")[1].rstrip()
                    elif "features:" in line:
                        is_pattern = True
                    elif is_pattern:
                        new_rule.patterns.append(line.split("- ")[1].rstrip())
                json_format = {
                    "rule": new_rule.name,
                    "functions": new_rule.patterns,
                    "tag": new_rule.tag,
                }
                rules_list.append(json_format)
        return Response(rules_list)

    def delete(self, request):
        name = request.query_params["rule"]
        if valid_filename(name):
            path = DATA_RULES + name + ".yml"
            if exists(path):
                remove(path)
            return Response({"success": "Rule as been deleted"})
        else:
            return Response({"error": "File is not valid"})
