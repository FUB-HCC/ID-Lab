# -*- coding: utf-8 -*-

import subprocess
import time
import sys
import requests
import argparse
import psycopg2
import errno
import shutil
import csv
import json
import os
import pandas as pd


########################
## Settings
#

# Housekeeper Parameters
# Refer to README.md in Housekeeper folder for all possible options
housekeeperParams = {
    #'slugify': 'slug_de',
    'outputType': 'json' # this needs to be json
}

# Python command
pythonCommand = "python3"
# Files to delete if they exist in input folder (after beeing created from db or in manual folder)
uselessFiles = ["auth_user.csv","django_content_type.csv","home_homepage.csv","taggit_taggeditem.csv","wagtailcore_page.csv","wagtailcore_site.csv","wagtailimages_filter.csv"]

# RDF format
rdfFormat = "rdfxml" # Could also be turtle, ntriples, nquads, rdfxml, rdfjson, jsonld

#
## END Settings
##########################

# Variables
workingDir = os.getcwd()
tmpFolderName = "/tmp"
tmpFolder =  workingDir + tmpFolderName
tmpFolderDbOut = tmpFolder + "/dbOut"
housekeeperInputFolder = ""
housekeeperFolderName = "/housekeeperOutput"
housekeeperTmpFolder = tmpFolder + housekeeperFolderName
overseerTmpFolderName = "/overseerOutput"
overseerTmpFolder = tmpFolder + overseerTmpFolderName
rmlMakerTmpFolderName = "/rmlMakerOutput"
rmlMakerTmpFolder = tmpFolder + rmlMakerTmpFolderName
# END Variables

# -s sql -ip localhost -u immanuelpelzer -db cluster

# Getting arguments
parser = argparse.ArgumentParser(description='This is the TRiPLE pipeline.')
# Source
parser.add_argument('-s','--source', help='Can be "sql" or "folder"',required=True)
# Folder settings
parser.add_argument('-if','--inputFolder', help='Folder to import',required=False)
# SQL settings
parser.add_argument('-ip','--ip', help='Connect to PostgreSQL database at ip',required=False)
parser.add_argument('-u','--user',help='PostgreSQL user', required=False)
parser.add_argument('-p','--password',help='PostgreSQL password', required=False)
parser.add_argument('-db','--dbName',help='PostgreSQL database name', required=False)

parser.add_argument('--keepFolders')

args = parser.parse_args()
# END Getting arguments

# Creating folders to work in
if not args.keepFolders and os.path.isdir(tmpFolder): # Delete all old content
    shutil.rmtree(tmpFolder)
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
make_sure_path_exists(tmpFolder)
make_sure_path_exists(tmpFolderDbOut)
make_sure_path_exists(housekeeperTmpFolder)
make_sure_path_exists(overseerTmpFolder)
make_sure_path_exists(rmlMakerTmpFolder)
# END folder

# Helper functions
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
    df.to_csv(csvfilename + ".csv")

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
# END Helper functions

###############
## Getting the data
#
print("Running complete TRiPLE pipeline.")
# Importing data from database
if args.source == "sql":
    if args.ip and args.user and args.dbName is not None:
        print("Connecting to database, escaping and converting to csv.")
        ip = args.ip
        user = args.user
        db = args.dbName
        pw = args.password or ""
        try:
            conn = psycopg2.connect(host=ip, database=db, user=user, password=pw)
            cur = conn.cursor()

            cur.execute("""do $$
  declare
    arow record;
  begin
    for arow in
    select
        'UPDATE '||c.table_name||' SET '||c.COLUMN_NAME||' = regexp_replace('||c.COLUMN_NAME||', E''[\\n\\r\\u2028]+'', '' '', ''g'' );
           '
         as my_update_query
     from
        (SELECT
            table_name,COLUMN_NAME, data_type
         FROM INFORMATION_SCHEMA.COLUMNS
         WHERE table_name LIKE 'content_%' and (data_type LIKE 'text%' OR data_type LIKE 'character%')
         ) c
    loop
     execute arow.my_update_query;
    end loop;
  end;
$$;


CREATE OR REPLACE FUNCTION db_to_csv(path TEXT) RETURNS void AS $$
declare
  tables RECORD;
  statement TEXT;
begin
  FOR tables IN
    SELECT (table_schema || '.' || table_name) AS schema_table
    FROM information_schema.tables t INNER JOIN information_schema.schemata s
    ON s.schema_name = t.table_schema
    WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'configuration')
    ORDER BY schema_table
  LOOP
    statement := 'COPY ' || tables.schema_table || ' TO ''' || path || '/' || tables.schema_table || '.csv' ||''' DELIMITER '','' CSV HEADER ENCODING ''UTF8'' QUOTE ''"'' ESCAPE ''\\'' ';
    EXECUTE statement;
  END LOOP;
  return;
end;
$$ LANGUAGE plpgsql;

SELECT db_to_csv('""" + tmpFolderDbOut + """');""")
            db_version = cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.close()
            sys.exit(0)
        finally:
            if conn is not None:
                conn.close()
                print('✓ Success. Database connection closed.')
                housekeeperInputFolder = tmpFolderDbOut
    else:
        print("When using PostgreSQL, you have to pass --ip, --user and --dbName. Please refer to the README.")
        sys.exit(0)
elif args.source == "folder":
    # Check if folder exists
    inputFolder = args.inputFolder or "error"
    f = workingDir + "/"+ inputFolder
    if os.path.isdir(f):
        housekeeperInputFolder = f
    else:
        print("Folder " + f + " does not exists. Please pass --inputFolder.")
        sys.exit(0)
else:
    print("You need to pass a --source. It has to be 'inputFolder' or 'sql'");
# END data input
#########

###############
## Delete useless files
#
def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred
for f in uselessFiles:
    silentremove(housekeeperInputFolder + "/"+ f )
    silentremove(housekeeperInputFolder + "/public." + f )
#
# END Delete useless files
################

###############
## Check if files in folder
#
allFiles = allfileswithfiletype(housekeeperInputFolder, "csv")
if len(allFiles) > 0:
    print("✓ Using " + housekeeperInputFolder + " as input folder. There are " + str(len(allFiles)) + " files in this folder.")
else:
    print("No files in "+ housekeeperInputFolder)
    sys.exit(0)
#
# END Check if files in folder
################

######################################################################################################################
############### Here the usage of the other tools begins
#####################################################




################
## Housekeeper
#
print("Cleaning all data inside " +  housekeeperInputFolder + " using Housekeeper.")
print("Starting housekeeper.")
housekeeperProcess = subprocess.Popen("php -S 0.0.0.0:8080 -t ./Housekeeper/public", shell = True)
url = 'http://localhost:8080/clean'
headers = {'content-type': 'text/csv'}

time.sleep(5.0) # Wait for php server to start

try:
    for file in allFiles:
        print("Cleaning " + housekeeperInputFolder + "/" + file)
        filepath = housekeeperInputFolder + "/" + file
        with open(filepath) as fh:
            mydata = fh.read()
            mydata = mydata.encode('utf-8') # needed
            r = requests.post(url, data=mydata, params = housekeeperParams, headers=headers)
            fp = os.path.splitext(housekeeperTmpFolder + "/" + file)[0]+'.json'
            fp = fp.replace("public.","")
            with open(fp, "w") as text_file: # save returned data as json
                print(r.text, file=text_file)
                print("✓ " + file + " cleaned.")
except (Exception) as error:
    print(error)
    housekeeperProcess.kill()
    sys.exit(0)
housekeeperProcess.kill()
print("✓ Finished cleaning using housekeeper. Killing Housekeeper.")
#
## END Housekeeper
################



#################
## Overseer
#
print("Starting Overseer to insert mappings into the json files.")
#print(pythonCommand + " ./Overseer/main.py --source " + workingDir + tmpFolderName + housekeeperFolderName + "/ --output " +  workingDir + tmpFolderName + overseerTmpFolderName + "/")
overseerProcess = subprocess.Popen(pythonCommand + " ./Overseer/main.py --source " + workingDir + tmpFolderName + housekeeperFolderName + "/ --output " +  workingDir + tmpFolderName + overseerTmpFolderName + "/", shell=True, stdout=subprocess.PIPE)
overseerProcess.wait()
if overseerProcess.returncode == 0:
    print("✓ Finished adding mappings using Overseer.")
else:
    print("Error running Overseer. Please run the following command to see error messages:")
    print(pythonCommand + " ./Overseer/main.py --source " + workingDir + tmpFolderName + housekeeperFolderName + "/ --output " +  workingDir + tmpFolderName + overseerTmpFolderName + "/")
    sys.exit(0)
#
## END Overseer
#################

#################
## RMLMaker
#
print("Starting RMLMaker. This run does not prompt you to add new predicates. Use RMLMaker for that. See ./RMLMaker/README.md for usage information.")
rmlmakerProcess = subprocess.Popen(pythonCommand + " ./RMLMaker/main.py -s " + workingDir + tmpFolderName + overseerTmpFolderName + "/ -o " +  workingDir + tmpFolderName + rmlMakerTmpFolderName + "/mappings.rml.ttl -m " +  workingDir + "/RMLMaker/mapping.json --checkMappings 0 --checkFiles 0", shell=True, stdout=subprocess.PIPE)
# python3 ./RMLMaker/main.py -s /Users/immanuelpelzer/Development/ID-Lab/TRiPLE/tmp/overseerOutput/ -m /Users/immanuelpelzer/Development/ID-Lab/TRiPLE/RMLMaker/mapping.json -o /Users/immanuelpelzer/Development/ID-Lab/TRiPLE/tmp/rml/results.rml.ttl
rmlmakerProcess.wait()
if rmlmakerProcess.returncode == 0:
    print("✓ Finished generating RML.")
else:
    print("Error running RMLMaker. Please run the following command to see error messages:")
    print(pythonCommand + " ./RMLMaker/main.py -s " + workingDir + tmpFolderName + overseerTmpFolderName + "/ -o " +  workingDir + tmpFolderName + rmlMakerTmpFolderName + "/mappings.rml.ttl -m " +  workingDir + "/RMLMaker/mapping.json --checkMappings 0 --checkFiles 0")
    sys.exit(0)
#
## END RMLMaker
#################

#################
## RML-Mapper
#
print("!!!!!!! Now please run this command inside ./TRiPLE:")
command = "java -jar ./RML-Mapper/RML-Processor/target/RML-Processor-0.3.jar -m " + workingDir + tmpFolderName + rmlMakerTmpFolderName + "/mappings.rml.ttl -o results.rdf -f "+ rdfFormat
print(command)

#
## END RML-Mapper
#################


print("After that you will be finished. Your rdf results are in the file ./results.rdf. So Long, and Thanks for All the Fish.")
sys.exit(0)