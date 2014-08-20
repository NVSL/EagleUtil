from lxml import etree as ET
import copy
from EagleError import *
from EagleSchematicSheet import *
from EagleFile import *

class EagleSchematic(EagleFile):
    _schematic = None;

    _schematicParts = ["libraries", "attributes", "variantdefs","classes", "parts", "sheets"]

    def __init__(self, f):
        self._schematic = None
        EagleFile.__init__(self, f)
        self._schematic = self.getDrawing().find("schematic")
        try:
            self.initFields(self._schematicParts, self._schematic)
        except EagleError as e:
            print "Trouble loading from " + f
            print str(e)
            raise e

    def getSchematic(self):
        return self._schematic

    def get1stSheet(self):
        return EagleSchematicSheet(self.getSheets().find("sheet"))

    def findPinsOnNets(self, headers):
        r = {}
        for n in self.get1stSheet().getNets().findall("net"):
            for segment in n:
                for pinref in segment.findall("pinref"):
                    if pinref.get("part") in headers:
                        r[pinref.get("part") + "." + pinref.get("pin")] = n.get("name")
        return r

    def getLibraryContainer(self):
        return self.getLibraries()

EagleFile.addAccessors(EagleSchematic, EagleSchematic._schematicParts)
