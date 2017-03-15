import os
import sys

class RMLlogicalSource:
    def __init__(self, sourceFile):
        self.sourceFile = sourceFile
        self.filename, file_extension = os.path.splitext(sourceFile)
        if file_extension == ".json":
            self.filetype = "JSONPath"
        else:
            print("Unsupported file extention %s in %s" % (file_extension, sourceFile))
            sys.exit(0)

    def toString(self):
        return """
        rml:logicalSource [
            rml:source "%s";
            rml:referenceFormulation ql:%s;
            rml:iterator "$"
        ];
        """ % (self.sourceFile, self.filetype)