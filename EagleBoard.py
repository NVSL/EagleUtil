from lxml import etree as ET
#from lxml import etree as ET;
import copy
from EagleError import *
from EagleFile import *

class EagleBoard(EagleFile):
    _board = None;
    _layers = None
    _boardParts =  ["plain", "libraries", "attributes", "variantdefs","classes", "designrules", "autorouter","elements", "signals"]

    def __init__(self, f):
        self._board = None
        EagleFile.__init__(self, f)
        self.file_name = f
        self._board = self.getET().find("./drawing/board")
        self.initFields(self._boardParts, self._board)

    def getBoard(self):
        return self._board

    #Return a single <element> given its name
    def getElement(self,name):
        return self.getElements().find("element[@name='" + name + "']")
    
    def getLibraryContainer(self):
        return self.getLibraries()

    #Return the package information belonging to an <element>
    def getPackage(self, e):
        return self.getLibraries().find("library[@name='" + e.get("library") + "']").find("packages/package[@name='" + e.get("package") + "']")

    def instantiatePackages(self):
        for e in self.getElements():
            i = self.getPackage(e)
            e.append(copy.deepcopy(i))
            
    def addLibrariesFromSch (self, sch):
        libs = self.getLibraries()
        libs.extend(copy.deepcopy(sch.getLibraries().findall("*")))

EagleFile.addAccessors(EagleBoard, EagleBoard._boardParts)
