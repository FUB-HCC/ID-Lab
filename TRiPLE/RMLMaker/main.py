# -*- coding: iso-8859-15 -*-
import argparse

import jsonhelper
from model.filePTM import FilePTM
import model.file as File
import sys
from model.rml_mapping import RMLMapping
import datetime
from subprocess import call
import os
class Main:
    def __init__(self, mappingfile = "mapping.json", outputfile = "output.rml.ttl", settings = { "mappingChecks" : True, "fileChecks" : True }):
        self.mappingfile = mappingfile
        # Load mapping file
        self.mapping =jsonhelper.loadjson(self.mappingfile);
        self.outputfile = outputfile
        # Data
        self.files = {}
        self.workplace = {}
        self.globalmappings = {}
        self.inputfolder = settings["source"]
        self.prefixes = set([])
        # Load variables
        self.variables = {}
        for var in self.mapping["variables"]:
            self.variables[var["key"]] = var["value"]
        # load slugs
        self.slugs = {}
        for s in self.mapping["slugs"]:
            self.slugs[s] = self.mapping["slugs"][s]
        # Load global mappings
        for gm in self.mapping["globalmappings"]:
            if "parentTriplesMap" in gm and gm["parentTriplesMap"] != "":
                if "joinCondition" in gm:
                    self.globalmappings[gm["parentTriplesMap"]] = RMLMapping(gm)
                else:
                    self.globalmappings[gm["parentTriplesMap"]] = FilePTM(gm, self.inputfolder, self.globalmappings, self.variables)
            else:
                self.globalmappings[gm["reference"]] = RMLMapping(gm)

        # Load prefixes
        for p in self.mapping["prefixes"]:
            self.prefixes.add(p)


        # Generate File Mappings
        if settings["fileChecks"] == 1 or settings["fileChecks"] == True:
            allFiles = self.allfileswithfiletype(self.inputfolder, ".json");
            addedFile = False
            for f in allFiles:
                found = False
                for fls in self.mapping["files"]:
                    if fls["filename"] == f:
                        found = True
                if not found:
                    addedFile = True
                    print("No mapping found for " + f)
                    i = input("Create json? y or n:")
                    if (i == "y"):
                        data = {
                            "filename": f,
                            "templatePrefix": "VAR_BASEURL",
                            "templatePath": input("Template Path (example.com/THIS/template):"),
                            "class": input("Class:")
                        }
                        if f in self.slugs:
                            data["template"] = self.slugs[f]
                            print("Slug autoset to %s" % data["template"])
                        else:
                            data["template"] = input("Template (example.com/project/IDENTIFIER (eg. slug_de):"),

                        if (input("With Image/Foerderer Mappings?:") == "y"):
                            data["mappings"] = [
                                {
                                    "parentTriplesMap": "ImageMapping"
                                },
                                {
                                    "parentTriplesMap": "FoerdererMapping"
                                }
                            ]
                        else:
                            data["mappings"] = []
                        self.mapping["files"].append(data)


        # Load Files
        for file in self.mapping["files"]:
            self.files[file["filename"]] = File.File(file, self.inputfolder, self.globalmappings, self.variables, self)

    # Check all mappings
        if settings["mappingChecks"] == 1 or settings["mappingChecks"] == True:
            for file in self.files.values():
                file.checkMappings(self.files,self.slugs)

    def allfileswithfiletype(self,dir, type):
        list = []
        for file in os.listdir(dir):
            if file.endswith(type):
                list.append(file)
        return list

    def writeAll(self):
        ## overwrite file
        out = "#"+datetime.date.today().strftime("%I:%M%p on %B %d, %Y") + "\n"
        self.deleteContent(open(self.outputfile, "w+"))
        for prefix in self.prefixes:
            out += prefix + "\n"
        out += "\n"
        ## get all files
        for file in self.files:
            out += self.files[file].toString(self.globalmappings, self.files)
        ## write to out
        with open(self.outputfile, "w+") as text_file:
            text_file.write(out)
        print("Wrote %s." % self.outputfile)

    def deleteContent(self,pfile):
        pfile.seek(0)
        pfile.truncate()

    def saveNewMapping(self):
        fls = []
        for f in self.files.values():
            fls.append(f.toJson())
        glmpngs = []
        for m in self.globalmappings.values():
            glmpngs.append(m.toJson())
        vrs = []
        for v in self.variables.keys():
            vrs.append({
                "key" :  v,
                "value" : self.variables[v]
            })
        #prepare
        output = {
            "slugs" : self.slugs,
            "folder" : self.inputfolder,
            "prefixes" : self.prefixes,
            "variables" : vrs,
            "files" : fls,
            "globalmappings" : glmpngs
        }
        #save
        jsonhelper.savejson(self.mappingfile, output)


# Getting arguments
parser = argparse.ArgumentParser(description='This is the RMLMaker.')
# Source
parser.add_argument('-s','--source', help='Source folder',required=True)
parser.add_argument('-m','--mappingFile', help='Mapping file',required=True)
parser.add_argument('-o','--outputFolder', help='Resulting RML file folder',required=True)
parser.add_argument('-cm','--checkMappings', help='Should check mappings? 1/0',required=False)
parser.add_argument('-cf','--checkFiles', help='Should check for new files? 1/0',required=False)

args = parser.parse_args()
print("""Running RMLMaker""")
settings = {
    "mappingChecks" : args.checkMappings or True,
    "fileChecks" : args.checkFiles or True,
    "source" : args.source or "input/"
}
main = Main(args.mappingFile,outputfile=args.outputFolder, settings=settings)
main.writeAll()
print("Finished.")

    # Run RML
#main = Main()

