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
    for api_call in json_list:
        if api_call['funcName'] not in func_list:
            func_list.append(api_call['funcName'])
    return func_list


liste = extract_json("test.json")
print("Type: ", type(liste))
# print("1st: ", liste[0]['funcName'])
print("2nd: ", liste['hooks_result'][0]['funcName'])
# print(extract_funcname(liste))
