from lxml import etree as ET
import copy
from EagleError import *
from EagleSchematicSheet import *
from EagleFile import *
import EagleBoard
import EagleLibrary
import unicodedata

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

    def getLibraryContainer (self):
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
        raise NotImplementedError("Make me!")
        return newName
        
    def addLibrariesFrom (self, other):
        assert( isinstance(other, EagleSchematic) )
        EagleSchematic.combineLibraries(self._root, other._root)
        
    @staticmethod
    def combineLibraries (dest, src):
    	srcLibs = src.findall("./drawing/schematic/libraries/library")
    	destLibs = dest.findall("./drawing/schematic/libraries/library")

    	destLibNames = []

    	for lib in destLibs:
    		destLibNames.append(lib.attrib["name"])

    	for lib in srcLibs:
    		if lib.attrib["name"] not in destLibNames:
    			dest.find('./drawing/schematic/libraries').append(lib)

    	#then match up all lib pairs with the same name and combine

    	for dLib in destLibs:
    		for sLib in srcLibs:
    			if dLib.attrib['name'] == sLib.attrib['name']:
	
    				#combine packages
    				dPackageNames = []
    				for package in dLib.findall('./packages/package'):
    					dPackageNames.append(package.attrib['name'])
		
    				for package in sLib.findall('./packages/package'):
    					if package.attrib['name'] not in dPackageNames:
    						dLib.find('packages').append(package)
			
	
    				#combine symbols
    				dSymbolNames = []
    				for symbol in dLib.findall('symbols/symbol'):
    					dSymbolNames.append(symbol.attrib['name'])
		
    				for symbol in sLib.findall('symbols/symbol'):
    					if symbol.attrib['name'] not in dSymbolNames:
    						dLib.find('symbols').append(symbol)
			
    				#combine devicesets
    				dDevicesetNames = []
    				for deviceset in dLib.findall('devicesets/deviceset'):
    					dDevicesetNames.append(deviceset.attrib['name'])
		
    				for deviceset in sLib.findall('devicesets/deviceset'):
    					if deviceset.attrib['name'] not in dDevicesetNames:
    						dLib.find('devicesets').append(deviceset)

    				#match up devicesets for combining devices
    				for dDeviceset in dLib.findall('devicesets/deviceset'):
    					for sDeviceset in sLib.findall('devicesets/deviceset'):
    						if dDeviceset.attrib['name'] == sDeviceset.attrib['name']:
				
    							#combine devices
    							dDeviceNames = []
    							for device in dDeviceset.findall('device'):
    								dDeviceNames.append(device.attrib['name'])
	
    							for device in sDeviceset.findall('device'):
    								if device.attrib['name'] not in dDeviceNames:
    									dDeviceset.append(device)
                
    def toBoard (self, libraries, template_filename):
        print
        print "Converting schematic to board."
        # initialize with template
        board = EagleBoard.EagleBoard(template_filename)
        
        # bring in libraries from external libraries, every thing we need is not in the sch file :(
        for library_file in libraries:
            lbr = EagleLibrary.EagleLibrary(library_file)
            lbr.getLibrary().set("name", library_file.split("/")[-1].replace(".lbr",""))
            board.getLibraries().append(copy.deepcopy(lbr.getLibrary()))
            
        # now we can add the components, known as elements, to the brd file
        elements = board.getElements()
        
        parts = self.getParts()
        parts = parts.findall("*")
        
        print "Parts in schematic:"
        for part in parts:
            attrib = {}
            attrib["name"] = part.get("name")
            attrib["library"] = part.get("library")
            
            print "Processing part:", attrib["name"]
            
            device = part.get("device")
            
            if (device is None) or (device == ""):
                print "No device for part. Ignoring."
                print
                continue
            else:
                print "Device:", device
            
            
            # find a package...
            board_libraries = board.getLibraries()
            
            
            
            print "Looking for library:", attrib["library"]
            
            library = board_libraries.find("./library/[@name='" + attrib["library"] + "']")
            
            print "Found:", library
            
            
            package = library.find("./packages/package").get("name")
            
            
            
            attrib["package"] = package
            
            
            
            #attrib["value"] = None
            attrib["x"] = "0"
            attrib["y"] = "0"
            attrib["smashed"] = "yes"
            attrib["rot"] = "R0"
            
            print "Got:", attrib
                
            
            
            
            new_element = ET.SubElement(elements, "element", attrib)
            print
        
        return board
        
        

EagleFile.addAccessors(EagleSchematic, EagleSchematic._schematicParts)





































