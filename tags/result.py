import json


def extract_json(file):
    with open(file) as json_file:
        try:
            json_list = json.load(json_file)
        except UnicodeDecodeError and UnboundLocalError:
            print('Error on line :\n', repr(json_file))
    return json_list


def extract_funcname(json_list):
    json_list = json_list['hooks_result']
    func_list = {}
    if not "error" in json_list :
        for api_call in json_list:
            func_list[(api_call['funcName'])] = api_call['funcParams']
        return func_list
    return {"error" : json_list['error']}


liste = extract_json("test.json")
print(extract_funcname(liste))
