import json


def extract_funcname_list(json_list):
    func_list = []
    if not "error" in json_list:
        for api_call in json_list:
            call = api_call["funcName"]
            func_list.append(call)
        return func_list
    return ["error"]
