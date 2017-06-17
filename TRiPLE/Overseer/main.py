import converter
import jsonloader
import sys
import os
import mappingloader
from subprocess import call
import json
import json
from pprint import pprint
import csv
import argparse


# Getting arguments
parser = argparse.ArgumentParser(description='Overseer.')
# Source
parser.add_argument('-s','--source', help='The folder where the json input files are.',required=True)
parser.add_argument('-o','--output', help='The folder where the json files with mapping are gonna be.',required=True)
args = parser.parse_args()

# END Getting arguments

inputpathjson = args.source # "resources/cluster/input/json/" # Input path of json files
outputpathjsonwithmapping = args.output # Output folder



# with open('resources/bla/sparql.json') as data_file:
#     data = json.load(data_file)
#
# for key in data.keys():
#     value = data[key]
#     with open("resources/bla/out/sparql" + key + '.csv', 'w') as csvfile:
#         spamwriter = csv.writer(csvfile, delimiter=',',
#                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         for val in value:
#             print(val)
#             spamwriter.writerow([str(val)])
#
#
#
#
# sys.exit(0);

# inputpathcsv = "resources/bla/" # Input path
# outputpathjson = "resources/bla/" # Output path
# # convert all files in inputpath to json
# for file in converter.allfileswithfiletype(inputpathcsv, ".csv"):
#    converter.csvtojson(inputpathcsv + file, outputpathjson + os.path.splitext(file)[0])
# print('Finished converting json.')
# sys.exit(0)

# inputpath = "resources/bla/" # Input path
# outputpath = "resources/bla/"
# #convert all files in inputpath to csv
# for file in converter.allfileswithfiletype(inputpath, ".json"):
#    converter.jsontocsv(inputpath + file, outputpath + os.path.splitext(file)[0], None);
# print('Finished converting to csv.')
# sys.exit(0);



alljsonfiles = converter.allfileswithfiletype(inputpathjson, ".json") # read converted data

alljsonfiles.remove('content_pagecategoryrelationship.json')
alljsonfiles.remove('content_pagepagerelationship.json')


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
mappingloader.readp2pmapping('content_pagepagerelationship.json', contentfiles, idmapping, inputpathjson);

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
readcategoriesfileintomapping("content_category.json", contentfiles, categories)

# Loading category mappings
mappingloader.readp2cmapping('content_pagecategoryrelationship.json',  contentfiles, idmapping, inputpathjson, categories)

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