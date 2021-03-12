import json


def extract_json(file):
    with open(file) as json_file:
        try:
            json_list = json.load(json_file)
        except UnicodeDecodeError and UnboundLocalError:
            print('Error on line :\n', repr(json_file))
    return json_list


def extract_funcname(json_list):
    func_list = []
    if not "error" in json_list :
        for api_call in json_list:
            call = api_call['funcName']
            if call not in func_list:
                func_list.append(call)
        return func_list
    return ['error']
