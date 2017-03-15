import csv
import json
import os
import pandas as pd
from functools import reduce

def csvtojson(csvFileName, jsonFileName):
    print("Converting csv file " +  csvFileName +" to json file " + jsonFileName  + ".json")
    csvfile = open(csvFileName, 'r')
    list = []

    jsonfile = open(jsonFileName  + ".json", 'w+')
    reader = csv.DictReader( csvfile )
    for row in reader:
        list.append(row)

    jsonfile.write(json.dumps(list, indent=4))
    jsonfile.close()

def jsontocsv(jsonfilename, csvfilename, idlablename):
    print("Converting json file " + jsonfilename + " to csv file " + csvfilename + ".csv")
    df = pd.read_json(jsonfilename)
    df.to_csv(csvfilename + ".csv", index_label = idlablename)

def allfileswithfiletype(dir, type):
    list = []
    for file in os.listdir(dir):
        if file.endswith(type):
            list.append(file)
    return list

def flattenjson( b, delim ):
    val = {}
    for i in b.keys():
        if isinstance( b[i], dict ):
            get = flattenjson( b[i], delim )
            for j in get.keys():
                val[ i + delim + j ] = get[j]
        else:
            val[i] = b[i]

    return val