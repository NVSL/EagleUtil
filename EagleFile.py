from lxml import etree as ET;
#from lxml import etree as ET;
import sys
import XMLUtil

from EagleError import *

class EagleFile:

    _parts = ["layers", "settings", "grid"]
    _drawing = None

    def initFields(self, parts, element):
        for i in parts:
            setattr(self, "_" + i, element.find(i))
#            print "_" + i + " is " + str(getattr(self, "_" + i)) 
            if getattr(self, "_" + i) is None:
                raise EagleError("Couldn't find section " + i)

    @staticmethod
    def addAccessors(c, p):
        def _access(i):  
            return lambda x: getattr(x, "_" + i)

        for i in p:
            a = _access(i)
            t = i[0].upper() + i[1:]
            a.__name__ = "get" + t
            setattr(c, "get" + t, a)

    def __init__(self, f):
        self._et = None;
        self._root = None;
        self._et = ET.parse(f)
        self._root = self._et.getroot()                
        self._drawing = self._root.find("drawing")
        self.initFields(self._parts, self._drawing)
        self.initialize()

    def getET(self):
        return self._et

    def getDrawing(self):
        return self._drawing

    def initialize(self):
        for i in self._parts:
            setattr(self, "_" + i, self._drawing.find(i))
    
    def getRoot(self):
        return self._root

    def write(self, f):
        XMLUtil.formatAndWrite(self._et, f)
        
    def addLibrariesFrom (self, other):
        assert( isinstance(other, EagleFile) )
        EagleFile.combineLibraries(self._root, other._root)
        
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

EagleFile.addAccessors(EagleFile, EagleFile._parts)
