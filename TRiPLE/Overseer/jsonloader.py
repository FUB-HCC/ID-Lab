import json

def loadjson(file):
    with open(file) as data_file:
        return json.load(data_file)