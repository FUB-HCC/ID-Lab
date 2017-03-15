import sys

class RMLMapping:
    def __init__(self, content, globalvariables = None):
        self.content = content

        # types
        if "parentTriplesMap" in content and content["parentTriplesMap"] != "":
            ###### Is parent triples map
            self.parentTriplesMapName = content["parentTriplesMap"]
            self.ignore = False
            self.type = "parentTriplesMap"
            self.joinCondition = {"enabled": False}
            if "joinCondition" in content and content["joinCondition"]["enabled"]:
                self.joinCondition = {"enabled": True}
                if "parent" in content["joinCondition"] and not content["joinCondition"]["parent"] == "":
                    self.joinCondition["parent"] = content["joinCondition"]["parent"]
                if "child" in content["joinCondition"] and not content["joinCondition"]["child"] == "":
                    self.joinCondition["child"] = content["joinCondition"]["child"]
                if "predicate" in content["joinCondition"] and not content["joinCondition"]["predicate"] == "":
                    self.joinCondition["predicate"] = content["joinCondition"]["predicate"]
                else:
                    self.joinCondition["predicate"] = "schema:Thisismissing"
        else:
            self.type = "objectMap"
            self.parentTriplesMapName = "" # not ptm
            #### Is object map
            # predicate
            if "predicate" in content and content["predicate"] != "":
                self.predicate = content["predicate"]
            else:
                self.predicate = None
            # reference
            if "reference" in content and content["reference"] != "":
                self.reference = content["reference"]
            else: self.reference = None

            # datatype
            if "datatype" in content and content["datatype"] != "":
                self.datatype = content["datatype"]
            else: self.datatype = None
            # language
            if "language" in content and content["language"] != "":
                self.language = content["language"]
            else: self.language = None
            # ignore
            if "ignore" in content and content["ignore"] != "":
                self.ignore = content["ignore"]
            else:
                self.ignore = False



    def toString(self, filename, predicate = None):
        if self.type != "parentTriplesMap":
            return self.toStringObject()
        else:
            return self.toStringParentTriplesMap(filename,predicate)

    def toStringObject(self):
        if self.ignore: return ""
        #no parent
        out = ""
        if self.reference is not None:
            out += """
        rr:predicateObjectMap [
            rr:predicate %s;
            rr:objectMap [
                rml:reference "$.%s";
                """ % (self.predicate, self.reference)
            if self.datatype is not None:
                out += """rr:datatype %s;
                """ % self.datatype
            if self.language is not None:
                out += """rr:language "%s";
                """ % self.language
            out += """]
        ];
            """
        return out

    def toStringParentTriplesMap(self, filename, predicate):
        #return ""
        if self.ignore: return ""
        #no parent
        out = ""

        #ptm
        if not self.joinCondition["enabled"]:
            out += """
            rr:predicateObjectMap [
                rr:predicate %s;
                rr:objectMap [
                    rr:parentTriplesMap <#%s%s>;
                    """ % (predicate,filename, self.parentTriplesMapName)
        else:
            out += """
            rr:predicateObjectMap [
                rr:predicate %s;
                rr:objectMap [
                    rr:parentTriplesMap <#%sNonInverse>;
                    """ % (self.joinCondition["predicate"], self.parentTriplesMapName)
            out+="rr:joinCondition [\n"
            if "child" in self.joinCondition and not self.joinCondition["child"] == "":
                out += '                    rr:child "$.%s[*]";\n' % self.joinCondition["child"]
            if "parent" in self.joinCondition and not self.joinCondition["parent"] == "":
                out += '                    rr:parent "$.%s"\n' % self.joinCondition["child"]
            out += "                ]\n"

        #rest
        out += """           ]
        ];
            """

        return out

    def toJson(self):
        if self.parentTriplesMapName:
            out = {
                "parentTriplesMap" : self.parentTriplesMapName
            }
            if self.joinCondition["enabled"]:
                out["joinCondition"] = {"enabled" : True}
                if "child" in self.joinCondition and not self.joinCondition["child"] == "":
                    out["joinCondition"]["child"] = self.joinCondition["child"]
                if "parent" in self.joinCondition and not self.joinCondition["parent"] == "":
                    out["joinCondition"]["parent"] = self.joinCondition["parent"]
                if "predicate" in self.joinCondition and not self.joinCondition["predicate"] == "":
                    out["joinCondition"]["predicate"] = self.joinCondition["predicate"]
            else:
                out["joinCondition"] = {"enabled" : False}
            return out
        else:
            return {
                "reference" : self.reference,
                "predicate" : self.predicate,
                "ignore" : self.ignore,
                "language" : self.language,
                "datatype" : self.datatype
            }