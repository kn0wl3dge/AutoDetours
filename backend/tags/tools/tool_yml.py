import sys
from argparse import ArgumentParser


def extract_functions_from_file(filename):
    function_list = []

    try:
        with open(filename, "r") as f:
            for line in f.readlines():
                if ("function" not in line) or ("callback" in line):
                    continue

                function_list.append(line.split()[0])
    except IOError:
        print("File does not exist", file=sys.stderr)

    return function_list


def write_rule(name, tag, functions):
    with open("../db_rules/" + name.lower() + ".yml", "w") as f:
        f.write("name: %s\n" % name)
        f.write("features:\n")
        for func in functions:
            f.write("    - %s\n" % func)
        f.write("tag: %s" % tag)
