# -*- coding: iso-8859-15 -*-
import os
import sys
from model.rml_mapping import RMLMapping
from model.rml_logicalSource import RMLlogicalSource
from model.filePTM import FilePTM
import jsonhelper
import inspect
from model.colors import color
import sys
class File:
    def __init__(self, mappingContent, inputfolder, globalmappings, variables, main):
        self.filename = mappingContent["filename"]
        self.variables = variables
        # build template
        self.handler = main
        if not mappingContent["templatePrefix"] in variables:
            print("Variable " + mappingContent["templatePrefix"] + " is not defined.")
            sys.exit(0)
        else:
            if not "template" in mappingContent:
                print("Template for " + self.filename + " is not defined.")
                sys.exit(0)
            else:
                self.template = "%s%s/{$.%s}" % (variables[mappingContent["templatePrefix"]],mappingContent["templatePath"], mappingContent["template"])
        # load rest
        self.templateStr =  mappingContent["template"]
        self.templatePath = mappingContent["templatePath"]
        self.templatePrefix = mappingContent["templatePrefix"]
        self.classdef = mappingContent["class"]
        self.source = RMLlogicalSource(inputfolder + mappingContent["filename"])
        self.ownMappings = {}
        self.allMappings = {}
        self.linksToOtherResources = []

        self.actualcontent = jsonhelper.loadjson(inputfolder + mappingContent["filename"])
        for m in mappingContent["mappings"]:
            if "parentTriplesMap" in m:
                self.ownMappings[m["parentTriplesMap"]] = RMLMapping(m, globalmappings)
                self.allMappings[m["parentTriplesMap"]] = self.ownMappings[m["parentTriplesMap"]]
            else:
                self.ownMappings[m["reference"]] = RMLMapping(m)
                self.allMappings[m["reference"]] = self.ownMappings[m["reference"]]

        self.globalmappings = globalmappings
        self.loadglobalMapping(globalmappings)


    def loadglobalMapping(self, globalmappings):
        for key in globalmappings.keys(): # loed alles rein, stuss
            if not key in self.ownMappings and not isinstance(globalmappings[key],FilePTM): # Priority for local mappings
                    self.allMappings[key] = globalmappings[key]

    def checkMappings(self, files = None, slugs = None):
        # get all types
        neededMappings = set([])
        for entry in self.actualcontent:
            for k in entry.keys():
                neededMappings.add(k)
        foundNoMapping = False
        for key in neededMappings:
            if not key in self.allMappings.keys():
                print("WARNING: " + color.BLUE + self.filename+ color.END + " No Mapping found for key:" + color.BLUE + color.BOLD + " " + key + " " + color.END + color.END)
                foundNoMapping = True #True
                keep = True #True
                while keep:
                    user_input = input("    Create mapping in Mapping file? g for global, l for local, i for ignore , gi for global ignore, el for empty local, eg for emtpy global, pj for parent triple map with join conditionn: ")
                    if user_input == "i":
                        data = {
                            "ignore" : True,
                            "reference" : key
                        }
                        self.ownMappings[key] = RMLMapping(data)
                        self.allMappings[key] = self.ownMappings[key]
                        self.handler.saveNewMapping()
                        keep = False
                    elif user_input == "gi":
                        data = {
                            "ignore": True,
                            "reference": key
                        }
                        self.globalmappings[key] = RMLMapping(data)
                        self.loadglobalMapping(self.globalmappings)
                        self.handler.saveNewMapping()
                        keep = False
                    elif user_input == "g":
                        print(color.BOLD + "    Please enter data (just press enter to ommit value)" + color.END)
                        new_predicate = input("    rr:predicate:")
                        new_datatype = input("    rr:datatype:")
                        new_language = input("    rr:language:")
                        data = {
                            "reference": key,
                            "predicate" : new_predicate,
                            "datatype" : new_datatype,
                            "language" : new_language
                        }

                        self.globalmappings[key] = RMLMapping(data)
                        self.loadglobalMapping(self.globalmappings)
                        self.handler.saveNewMapping()
                        keep = False
                    elif user_input == "l":
                        print(color.BOLD + "    Please enter data (just press enter to ommit value)" + color.END)
                        new_predicate = input("    rr:predicate:")
                        new_datatype = input("    rr:datatype:")
                        new_language = input("    rr:language:")
                        data = {
                            "reference": key,
                            "predicate": new_predicate,
                            "datatype": new_datatype,
                            "language": new_language
                        }
                        self.ownMappings[key] = RMLMapping(data)
                        self.allMappings[key] = self.ownMappings[key]
                        self.handler.saveNewMapping()
                        keep = False
                    elif user_input == "pj":
                        print(color.BOLD + "    Please enter data (just press enter to ommit value)" + color.END)
                        new_predicate = input("    rr:predicate:")
                        parent = input("    rr:parent:")
                        child = input("    rr:child:")
                        ptmName = input("   parentTriplesMap:")
                        data = {
                            "parentTriplesMap": ptmName,
                            "joinCondition" : {
                                "enabled" : True,
                                "predicate": new_predicate,
                                "child": child,
                                "parent": parent
                            }

                        }
                        self.ownMappings[key] = RMLMapping(data)
                        self.allMappings[key] = self.ownMappings[key]
                        self.handler.saveNewMapping()
                        keep = False
                    elif user_input == "eg":
                        data = {
                            "reference": key,
                            "predicate": "",
                            "datatype": "",
                            "language": ""
                        }

                        self.globalmappings[key] = RMLMapping(data)
                        self.loadglobalMapping(self.globalmappings)
                        self.handler.saveNewMapping()
                        keep = False
                    elif user_input == "el":
                        data = {
                            "reference": key,
                            "predicate": "",
                            "datatype": "",
                            "language": ""
                        }
                        self.ownMappings[key] = RMLMapping(data)
                        self.allMappings[key] = self.ownMappings[key]
                        self.handler.saveNewMapping()
                        keep = False
                    else:
                        print(color.RED + "    Invalid input" + color.END)
                        keep = True
                break
        if foundNoMapping:
            self.checkMappings() # start anew


    def toString(self, globalmappings = None, files = None):
        neededPTMTemplates = []
        neededNonInversePTMTemplates = []
        out = "<#%sMapping>" % os.path.splitext(self.filename)[0]
        # source
        out += self.source.toString()
        # subject map
        out += """
        rr:subjectMap [
            rr:template "%s";
            rr:class %s
        ];
        """ % (self.template, self.classdef)
        for index, key in enumerate(self.allMappings):
            if self.allMappings[key].type == "parentTriplesMap":
                if self.allMappings[key].joinCondition["enabled"] == True: # with join condition
                    out += self.allMappings[key].toString(os.path.splitext(self.filename)[0], self.allMappings[key].joinCondition["predicate"])
                    neededNonInversePTMTemplates.append(key)
                else: # normal ptm
                    neededPTMTemplates.append(key)
                    out += self.allMappings[key].toString(os.path.splitext(self.filename)[0], globalmappings[key].predicate)
            else:
                ref = self.allMappings[key].reference
                if ref != None and "|||" in ref: # special stuff
                    fromFile, toFile = self.allMappings[key].reference.split("|||")
                    counter = 0
                    for entry in self.actualcontent:
                        keys = entry.keys()
                        if ref in keys:
                            referenced = entry[ref]
                            if len(referenced) > counter: counter = len(referenced)
                    #print(ref + " is max %i" %counter)
                    for i in range(counter):
                        out += """
                        rr:predicateObjectMap [
                            """
                        if self.allMappings[key].predicate != None:
                            out += "rr:predicate %s;" % self.allMappings[key].predicate
                        else:
                            out += "rr:predicate dct:%s;" % toFile
                        out += """
                        rr:objectMap [
                        """
                        out+= 'rr:template "%s%s/{$.%s[%i]}";' % (self.variables[files[toFile + ".json"].templatePrefix],
                                                                  files[toFile + ".json"].templatePath,
                                                                ref,
                                                                i)
                        out+= """    ]
                        ];"""
                else:
                    out += self.allMappings[key].toString(os.path.splitext(self.filename)[0])
        out = self.rreplace(out, ";", ".", 1) # Make last one a .
        ###########
        # ptm
        out += """
        """
        for mName in neededPTMTemplates:
            out += globalmappings[mName].toString(self.filename)

        for ptm in neededNonInversePTMTemplates:
            out += ""

        return out

    def rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def toJson(self):
        m = []
        for mapng in self.ownMappings.values():
            m.append(mapng.toJson())
        return {
            "filename" : self.filename,
            "templatePrefix" : self.templatePrefix,
            "templatePath" : self.templatePath,
            "template" : self.templateStr,
            "class" : self.classdef,
            "mappings" : m
        }