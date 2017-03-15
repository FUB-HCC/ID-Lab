import json

def loadjson(file):
    with open(file) as data_file:
        return json.load(data_file)

def savejson(file, content):
    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return json.JSONEncoder.default(self, obj)
    jsonfile = open(file, 'w+')
    jsonfile.write(json.dumps(content, indent=4, cls=SetEncoder))
    jsonfile.close()

