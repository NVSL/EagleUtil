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
        self._board = self.getET().find("./drawing/board")
        self.initFields(self._boardParts, self._board)

    def getBoard(self):
        return self._board
    
    def getLibraryContainer(self):
        return self.getLibraries()

    def instantiatePackages(self):
        for e in self.getElements():
            i = self.getLibraries().find("library[@name='" + e.get("library") + "']").find("packages/package[@name='" + e.get("package") + "']") 
            e.append(copy.deepcopy(i))

EagleFile.addAccessors(EagleBoard, EagleBoard._boardParts)
