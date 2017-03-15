import converter
import jsonloader
import sys
import os
import mappingloader
from subprocess import call
import json

inputpathjson = "resources/cluster/input/json/" # Input path of json files
outputpathjsonwithmapping = "resources/output/jsonandmapping/" # Output folder


# inputpathcsv = "resources/cluster/input/csv/" # Input path
# outputpathjson = "resources/output/json/" # Output path
# convert all files in inputpath to json
# for file in converter.allfileswithfiletype(inputpathcsv, ".csv"):
#    converter.csvtojson(inputpathcsv + file, outputpathjson + os.path.splitext(file)[0])
# print('Finished converting json.')
# sys.exit(0)

# outputpathcsv = "resources/output/csv/"
# convert all files in inputpath to csv
#for file in converter.allfileswithfiletype(inputpath, ".json"):
#    converter.jsontocsv(inputpath + file, outputpath + os.path.splitext(file)[0], "page_ptr_id");
#print('Finished converting to csv.')

alljsonfiles = converter.allfileswithfiletype(inputpathjson, ".json") # read converted data

alljsonfiles.remove('public_content_pagecategoryrelationship.json')
alljsonfiles.remove('public_content_pagepagerelationship.json')


def readjsonfileintomapping(filename, files, idmapping):
    #print("Loading " + filename)
    files[filename] = jsonloader.loadjson(inputpathjson + filename)
    for a in files[filename]:
        if "page_ptr_id" in a:
            if a["page_ptr_id"] in idmapping and a["page_ptr_id"] != "":
                print(a["page_ptr_id"] + " in " + filename + " already exists. NOT overwriting.")
            else:
                a["filename"] = filename
                idmapping[a["page_ptr_id"]] = a

# Load all data
idmapping = {}
contentfiles = {}
for f in alljsonfiles:
    readjsonfileintomapping(f, contentfiles, idmapping)
print("Loading content finished.")

# load mapping
print("Loading mapping")
mappingloader.readp2pmapping('public_content_pagepagerelationship.json', contentfiles, idmapping, inputpathjson);

# Loading categories
categories = {}
def readcategoriesfileintomapping(filename, files, idmapping):
    #print("Loading " + filename)
    files[filename] = jsonloader.loadjson(inputpathjson + filename)
    for a in files[filename]:
        if "id" in a:
                a["filename"] = filename
                idmapping[a["id"]] = a
print("Loading categories")
readcategoriesfileintomapping("public_content_category.json", contentfiles, categories)

# Loading category mappings
mappingloader.readp2cmapping('public_content_pagecategoryrelationship.json',  contentfiles, idmapping, inputpathjson, categories)

# Write connected files
for f in contentfiles:
    jsonfile = open(outputpathjsonwithmapping +  f, 'w+')
    # you shall null pass
    for entry in contentfiles[f]:
        for k in entry.keys():
            if entry[k] is None:
                entry[k] = ""

    jsonfile.write(json.dumps(contentfiles[f] , indent=4))
    jsonfile.close()