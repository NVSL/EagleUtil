from lxml import etree as ET
import copy
from EagleError import *
from EagleSchematicSheet import *
from EagleFile import *
import EagleBoard
import EagleLibrary
import unicodedata
import logging
log = logging.getLogger(__name__)

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
            log.error("Trouble loading from {}".format(f))
            raise e

    def getSchematic(self):
        return self._schematic
        
    def getPartRefs (self):
        parts = self.getParts()
        refs = []
        
        parts = parts.findall("part")
        log.debug("Parts:" + str( parts))
        
        for part in parts:
            refs.append(part.get("name"))
            
        log.debug(refs)
        return refs

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
            #log.debug("got instance:", instance.get("part")
            instance.set("part", instance.get("part") + postfix)
            #log.debug("now instance:", instance.get("part")
            
        for part in self.getRoot().findall(".//parts/part"):
            #log.debug("got part:", part.get("name")
            part.set("name", part.get("name") + postfix)
            #log.debug("now part:", part.get("name")
            
        for pinref in self.getRoot().findall(".//sheets/sheet/*/*/*/pinref"):
            #log.debug("got pinref:", pinref.get("part")
            pinref.set("part", pinref.get("part") + postfix)
            #log.debug("now pinref:", pinref.get("part")
            
    def appendToNetNames (self, postfix):
        for net in self.getRoot().findall(".//schematic/sheets/sheet/nets/net"):
            net.set("name", net.get("name") + postfix)    
    
    def getNetNames (self):
        #log.debug("EagleSchematic: getNetNames()"
        nets = self.getRoot().findall(".//schematic/sheets/sheet/nets/net")
        names = []
        
        #ET.dump(self.getRoot().find(".//schematic/sheets/sheet/nets"))
        #log.debug(nets
        
        for net in nets:
            names.append(net.get("name"))
                    
        return names
    
    def getPartNames (self):
        parts = self.getParts()
        names = []
        
        for part in parts:
            names.append(part.get("name"))
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
        
    def combine_duplicate_nets (self):
        #log.debug("Combining duplicate nets."
        sheets = self.getSheets()
        sheets = sheets.findall("sheet")
        
        for sheet in sheets:
            #log.debug("New sheet:"
            nets = sheet.findall("nets/net")
            net_map = {}
            for net in nets:
                name = net.get("name")
                #log.debug("Net:", name
                #log.debug("Map:    ", net_map.keys()
                
                if name not in net_map:
                    net_map[name] = net
                    #log.debug("New map:", net_map.keys()
                else:
                    #log.debug("Found dupe:", name
                    #ET.dump(sheet.find("nets"))
                    segments = net.findall("segment")
                    if segments is not None:
                        if len(segments) > 0:
                            net_map[name].extend(segments)
                    sheet.find("nets").remove(net)
        
    @staticmethod
    def combineLibraries (dest, src):

        log.debug("Combining libraries...")
        
    	srcLibs = src.findall("./drawing/schematic/libraries/library")
    	destLibs = dest.findall("./drawing/schematic/libraries/library")
        
        log.debug("src: {}".format([lib.get("name") for lib in srcLibs]))
        log.debug("dest: {}".format([lib.get("name") for lib in destLibs]))
        

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
                                        
    def gatePinToPad (self, part, gate, pin):
        debug = False
        
        log.debug("Mapping pin to pad.")
        part = self.getParts().find("part/[@name='"+part+"']")
        ET.dump(part)
        
        
        lib_name = part.get("library")
        deviceset_name = part.get("deviceset")

        if (deviceset_name is None): return None
        
        device_name = part.get("device")

        if (device_name is None): return None
        
        # check for dummy part, like ground symbol
        
        
        
        log.debug("Libraries available:")

        log.debug("libs:")
        #ET.dump(self.getLibraries())

        for l in self.getLibraries().findall("*"):
            log.debug(l.get("name"))
            
        log.debug("Looking for library:" +  lib_name)
        log.debug("xpath:" + "library/[@name='"+lib_name+"']")
        lib = self.getLibraries().find("library/[@name='"+lib_name+"']")
        log.debug("Got:" +  lib)
        
        log.debug("Looking for deviceset:" +  deviceset_name)
        deviceset = lib.find("devicesets/deviceset/[@name='"+deviceset_name+"']")
        log.debug("Got:" + deviceset)
        
        log.debug("Want:"+ device_name)
        device = deviceset.find("devices/device/[@name='"+device_name+"']")
        log.debug("Got:" + device)
        
        ET.dump(device)
        if device is None:
            device = deviceset.find("devices/device/[@name='"+device_name.upper()+"']")
            
        assert device is not None, "Could not find device: "+device_name+" in library: "+lib_name+" in deviceset:"+deviceset_name
        
        connect = device.find("connects/connect/[@gate='"+gate+"'][@pin='"+pin+"']")
        if connect is None: return None
        ET.dump(connect)
        
        pad = connect.get("pad")
        
        log.debug("Pad:" +  pad)
        
        return pad
        
    def getPackageFromPartName (self, part_name):
        part = self.getPart(part_name)
        device = part.get("device")
        deviceset = part.get("deviceset")
        library = part.get("library")
        
        return self.getPackage(library, deviceset, device)
        
    def getPackage (self, library, deviceset, device):
        log.debug("Getting package.")
        
        libraries = self.getLibraries()
        library = libraries.find("./library/[@name='"+library+"']")
        log.debug("Library:" + str(library))
        if library is None: return None
        
        
        deviceset = library.find("./devicesets/deviceset/[@name='"+deviceset+"']")
        log.debug("Deviceset:" + str(deviceset))
        if deviceset is None: return None
        
        device = deviceset.find("./devices/device/[@name='"+device+"']")
        log.debug("Device:" + str(device))
        if device is None: return None
        
        package_name = device.get("package")
        log.debug("Package name:"+ str(package_name))
        if package_name is None: return None
        
        package = library.find("./packages/package/[@name='"+package_name+"']")
        log.debug("Package:"+ str(package))
        return package
		
    def getPart (self, part_name):
        parts = self.getParts()
        parts = parts.findall("./*")
        parts = [part for part in parts if part.get("name") == part_name]
        assert len(parts) == 1, "More than one part with the same name."
        return parts[0]
		
                
    def toBoard (self, libraries, template_filename):
        assert len(libraries) > 0, "No libraries to use in conversion!"
        assert len(self.getLibraries().findall("library")) > 0, "There are no libraries in this schematic. Something is wrong!"
        log.debug("Converting schematic to board.")
        # initialize with template
        board = EagleBoard.EagleBoard(template_filename)
        
        
            
        # now we can add the components, known as elements, to the brd file
        elements = board.getElements()
        
        parts = self.getParts()
        parts = parts.findall("*")
        
        
        assert len(self.getLibraries().findall("library")) > 0, "There are no libraries in this schematic. Something is wrong!"
        
        board.remove_all_libraries()
        
        assert len(self.getLibraries().findall("library")) > 0, "There are no libraries in this schematic. Something is wrong!"
        
        for library in libraries:
            board.add_library(copy.deepcopy(library))
            
        assert len(self.getLibraries().findall("library")) > 0, "There are no libraries in this schematic. Something is wrong!"    
            
        log.debug("Libraries to add:" +str( libraries))
        log.debug("Board libraries:" + str([library.get("name") for library in board.getLibraries().findall("library")]))
        
        
        pin_mapping = {}
        
        log.debug("Parts in schematic:")
        for part in parts:
            attrib = {}
            name = part.get("name")
            attrib["name"] = name
            
            pin_mapping[name] = {}
            
            attrib["library"] = part.get("library")
            
            log.debug("Processing part:" + attrib["name"])
            
            # Find libraries
            #log.debug("Looking for library:", attrib["library"]
            
            # get lib from board
            board_libraries = board.getLibraries()
            library = board_libraries.find("./library/[@name='" + attrib["library"] + "']")
            assert library is not None, "Could not find library with name: "+attrib["library"]+" available libraries are: "+str([library.get("name") for library in board.getLibraries().findall("library")])
            
            # get lib from sch
            sch_libraries = self.getLibraries()
            sch_library = sch_libraries.find("./library/[@name='" + attrib["library"] + "']")
            #log.debug("Found:", library
            
            
            # Find device definition
            device_name = part.get("device")
            package = self.getPackage(library=part.get("library"), deviceset=part.get("deviceset"), device=device_name)
            
            if (package is None) and (device_name is not None):
                device_name = device_name.upper()
                package = self.getPackage(library=part.get("library"), deviceset=part.get("deviceset"), device=device_name)
            
            # check if device is defined. If it isn't then it is just a dummy symbol like a ground symbol.
            if (device_name is None) or (package is None):
                log.debug("No device for part. Ignoring.")

                continue
            else:
                log.debug("Device:" +  device_name)
            
            
            deviceset_name = part.get("deviceset")
            log.debug("Device set:" +  deviceset_name)
            
            deviceset = library.find("devicesets/deviceset/[@name='"+deviceset_name+"']")
            devices = library.find("devicesets/deviceset/[@name='"+deviceset_name+"']").find("devices")
            device_def = devices.find("device/[@name='"+ device_name + "']")
            
            tech_attributes = device_def.findall("./technologies/technology/attribute")
            part_attributes = part.findall("attribute")
            
            # find a package...
            package = device_def.get("package")
            attrib["package"] = package
            
            # find pinrefs
            #pinrefs = self.getSheets().findall("./sheet/nets/net/segment/pinref/[@part='" + name + "']")
            #log.debug("Got pinrefs:", pinrefs
            
            # find gate pins
            #for pinref in pinrefs:
            #    pin_name = pinref.get("pin")
            
            #attrib["value"] = None
            attrib["x"] = "0"
            attrib["y"] = "0"
            attrib["rot"] = "R0"
            
            # this is default for the value field
            value = part.get("value")
            if value is None:
                value = deviceset_name+device_name
            
            # this is a flag to see if the user can specify a value
            uservalue = deviceset.get("uservalue")
            
            log.debug("User value:" +  uservalue)
            if uservalue == "yes":
                value = part.get("value")
                if value is not None:
                    attrib["value"] = value
            else:
                attrib["value"] = value
            
            log.debug("Got:" +  attrib)
                
            
            new_element = ET.SubElement(elements, "element", attrib)
            
            for attribute in tech_attributes + part_attributes:
                new_attrib = copy.deepcopy(attribute)
                new_attrib.set("x", new_element.get("x"))
                new_attrib.set("y", new_element.get("y"))
                new_attrib.set("display", "off")
                new_attrib.set("layer", "27")
                new_attrib.set("size", "1.778")
                try:
                    new_attrib.attrib.pop("constant")
                except:
                    pass
                    
                new_element.append(new_attrib)
            

        log.debug("Now on to connections.")
        raw_nets = self.getSheets().findall("./sheet/nets/net")
        
        class Net (object):
            def __init__ (self, name=None):
                self.name = name
                self.pinrefs = []
                self.contactrefs = []
            
            def valid (self):
                return True # This is just for sch consistancy
                #return len(self.contactrefs) > 1
                
        nets = {}
        
        for net in raw_nets:
            name = net.get("name")
            log.debug("Got schematic net:" +  name)
            
            if nets.get(name, None) is None:
                nets[name] = Net(name)
                
            #log.debug("\tWith", len(net.findall("segment/pinref"))
                
            nets[name].pinrefs += net.findall("segment/pinref")
            
            for pinref in nets[name].pinrefs:
                log.debug("for:", pinref.get("part"))
            
            #log.debug("\tTotal for processed net:", len(nets[name].pinrefs)

        for net in nets.values():
            name = net.name
            log.debug("Processing:" +  name)
            
            # get contact refs from pin refs
            for pinref in net.pinrefs:
                part_name = pinref.get("part")
                gate = pinref.get("gate")
                pin = pinref.get("pin")
                pad = self.gatePinToPad(part=part_name, gate=gate, pin=pin)
                
                log.debug("\tpinref:" +  part_name + gate  + pin + pad)
                
                if pad is None:
                    continue
                
                net.contactrefs.append(ET.Element("contactref", element=part_name, pad=pad))
                
            #log.debug("For signal:", net.name, "got:", net.contactrefs
            
            if net.valid():
                signal = ET.Element("signal", name=net.name)
                signal.extend(net.contactrefs)
                board.getSignals().append(signal)
        
        log.debug("Finished board conversion.")

        return board
        
        

EagleFile.addAccessors(EagleSchematic, EagleSchematic._schematicParts)





































