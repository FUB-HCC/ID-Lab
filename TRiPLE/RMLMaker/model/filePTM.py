import os
import sys
from model.rml_mapping import RMLMapping
from model.rml_logicalSource import RMLlogicalSource
import jsonhelper

class FilePTM:
    def __init__(self, mappingContent, inputfolder, globalmappings, variables):
        self.inputfolder = inputfolder
        # build template
        if not mappingContent["templatePrefix"] in variables:
            print("Variable " + mappingContent["templatePrefix"] + " is not defined.")
            sys.exit(0)
        else:
            if not "template" in mappingContent:
                print("Template for " + mappingContent["parentTriplesMap"] + " is not defined.")
                sys.exit(0)
            else:
                self.template = "%s%s/{$.%s}" % (variables[mappingContent["templatePrefix"]],mappingContent["templatePath"], mappingContent["template"])
        # load rest
        self.templateStr = mappingContent["template"]
        self.templatePath = mappingContent["templatePath"]
        self.templatePrefix = mappingContent["templatePrefix"]
        self.ptmName = mappingContent["parentTriplesMap"]
        self.classdef = mappingContent["class"]
        self.predicate = mappingContent["predicate"]

        #self.source = RMLlogicalSource(inputfolder + mappingContent["filename"])
        self.ownMappings = {}
        self.allMappings = {}
        #self.actualcontent = jsonhelper.loadjson(inputfolder + mappingContent["filename"])
        for m in mappingContent["mappings"]:
            self.ownMappings[m["reference"]] = RMLMapping(m)
            self.allMappings[m["reference"]] = self.ownMappings[m["reference"]]
        #self.checkMappings()

    def checkMappings(self):
        # get all types
        neededMappings = set([])
        for entry in self.actualcontent:
            for k in entry.keys():
                neededMappings.add(k);
        for key in neededMappings:
            if not key in self.allMappings.keys():
                print("ERROR: %s No Mapping found for key %s" % ( self.filename, key))

    def toString(self, filename, files = None):
        self.actualcontent = jsonhelper.loadjson(self.inputfolder + filename)
        out="""
        """
        out += "<#%s%s>" % (os.path.splitext(filename)[0], self.ptmName)
        # source
        out += RMLlogicalSource(self.inputfolder + filename).toString()
        # subject map
        out += """
        rr:subjectMap [
            rr:template "%s";
            rr:class %s
        ];
        """ % (self.template, self.classdef)
        for index, key in enumerate(self.allMappings):
                out += self.allMappings[key].toString(os.path.splitext(filename)[0])

        out = self.rreplace(out, ";", ".", 1)
        return out

    def rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def toJson(self):
        ms = []
        for mapng in self.ownMappings.values():
            ms.append(mapng.toJson())
        return {
            "parentTriplesMap" : self.ptmName,
            "predicate" : self.predicate,
            "class" : self.classdef,
            "templatePrefix" : self.templatePrefix,
            "templatePath" : self.templatePath,
            "template" : self.templateStr,
            "mappings" : ms
        }