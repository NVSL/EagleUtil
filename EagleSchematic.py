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
        
    def getSheet (self, index):
        return EagleSchematicSheet(self.getSheets().findall("sheet")[index])
        
    def addPart(self, sheet, name, library, deviceset, device, value, gate, x, y):
        parts = self.getParts()
        ET.SubElement(self.getParts(), "part", name=name, library=library, deviceset=device, device=variant, value=value)
        ET.SubElement(sheet.getInstances(), "instance", part=part, gate=gate, x=x, y=y)
        
    def addSheets (self, other):
        """Adds all the sheets from another schematic."""
        self.addLibrariesFrom(other)
        
        otherSheetList = other.getSheets().findall("sheet")
        selfSheets = self.getSheets()
        for sheet in otherSheetList:
            self.getSheets().append(sheet)
            
    def addSchematic (self, other):
        """Merges another schematic into this schematic."""
        self.addLibrariesFrom(other)
        
        for sheet in other.getSheets():
            self.getParts().extend( other.getParts() )
            
        self.addSheets(other)
        
    def appendToPartNames (self, postfix):        
        for instance in self.getRoot().findall(".//sheets/sheet/instances/instance"):
            #print "got instance:", instance.get("part")
            instance.set("part", instance.get("part") + postfix)
            #print "now instance:", instance.get("part")
            
        for part in self.getRoot().findall(".//parts/part"):
            #print "got part:", part.get("name")
            part.set("name", part.get("name") + postfix)
            #print "now part:", part.get("name")
            
        for pinref in self.getRoot().findall(".//sheets/sheet/*/*/*/pinref"):
            #print "got pinref:", pinref.get("part")
            pinref.set("part", pinref.get("part") + postfix)
            #print "now pinref:", pinref.get("part")
            
    def appendToNetNames (self, postfix):
        for net in self.getRoot().findall(".//schematic/sheets/sheet/nets/net"):
            net.set("name", net.get("name") + postfix)    
    
    def getNetNames (self):
        nets = self.getRoot().findall(".//schematic/sheets/sheet/nets/net")
        names = []
        
        for net in nets:
            names.append(net.get("name"))
            
        return names
        
    def renameNet (self, oldName, newName):
        nets = self.getRoot().findall(".//schematic/sheets/sheet/nets/net")
        for net in nets:
            if net.get("name") == oldName:
                net.set("name", newName)
                
    def renameNets (self, renameList):
        nets = self.getRoot().findall(".//schematic/sheets/sheet/nets/net")
 
        for net in nets:
            for rename in renameList:
                oldName, newName = rename
                if net.get("name") == oldName:
                    net.set("name", newName)
                    
    def connectTwoNets (self, net1, net2, newName=None):
        if newName is None:
            newName = net1
            
        self.renameNet(net2, newName)
        self.renameNet(net1, newName)
        return newName
        
    def connectNets (self, nets, newName=None):
        if newName is None:
            newName = nets[0]
            
        myNets = self.getRoot().findall(".//schematic/sheets/sheet/nets/net")
        for net in myNets:
            net.set("name", newName)
        
        return newName
                
                

EagleFile.addAccessors(EagleSchematic, EagleSchematic._schematicParts)
