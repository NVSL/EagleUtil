from lxml import etree as ET;
import sys
from EagleError import *
from EagleDevice import *
from EagleFile import *

class EagleLibrary(EagleFile):

    _libraryParts =[ "packages", "symbols", "devicesets"]

    def __init__(self, f):
        self._library = None
        EagleFile.__init__(self, f)
        self._library = self.getDrawing().find("library")
        self.initFields(self._libraryParts, self._library)
#        if isinstance(initfrom, ET.Element):
#            self._library = initfrom
#            self.initialize()
#        elif initfrom is not None:
#            self.open(initfrom)
                
    def newPackage(self, name):
        name = name.upper()
        if self.findPackage(name) is None:
            return ET.SubElement(self._packages, "package", {"name":name})
        else:
            raise EagleError("Package '" + name + "' already exists")

    def findPackage(self, name):
        name = name.upper()
        return self.getPackages().find("package[@name='"+name+"']");
    
    def deletePackage(self, name):
        name = name.upper()
        p = self.findPackage(name)
        if p is not None:
            self.getPackages().remove(p)

    def getSection(self, section):
        return self.find(section)

    def ensureSectionExists(self, section):
        if self.getSection(section) is None:
            return ET.SubElement(self, section)

    def newSymbol(self, name):
        name = name.upper()
        if self.findSymbol(name) is None:
            return ET.SubElement(self._symbols, "symbol", {"name":name})
        else:
            raise EagleError("Symbol '" + name + "' already exists")

    def findSymbol(self, name):
        name = name.upper()
        return self.getSymbols().find("symbol[@name='"+name+"']");

    def deleteSymbol(self, name):
        name = name.upper()
        p = self.findSymbol(name)
        if p is not None:
            self.getSymbols().remove(p)


    def newDeviceSet(self, name):
        name = name.upper()
        if self.findDeviceSet(name) is None:
            d = ET.SubElement(self._devicesets, "deviceset", {"name":name})
            device = EagleDevice(d)
            device.setName(name)
            return d
        else:
            raise EagleError("DeviceSet '" + name + "' already exists")

    def findDeviceSet(self, name):
        name = name.upper()
        return self.getDevicesets().find("deviceset[@name='"+name+"']");

    def deleteDeviceSet(self, name):
        name = name.upper()
        p = self.findDeviceSet(name)
        if p is not None:
            self.getDevicesets().remove(p)
    
    def write(self, f):
        if self._et is None:
            raise EagleError("Trying to write out element-based library")
        self._et.write(f)

    def getLibraryContainer(self):
        return self._root.find("drawing")

    def addItem(self, element):
        if element.tag == "package":
            container = self._library.find("packages")
        elif element.tag == "symbol":
            container = self._library.find("symbols")
        elif element.tag == "deviceset":
            container = self._library.find("devicesets")

        incumbant = container.find(element.tag + "[@name='"+ element.get("name") + "']")
        if incumbant is not None:
            container.remove(incumbant)
        container.append(copy.deepcopy(element))

EagleFile.addAccessors(EagleLibrary, EagleLibrary._libraryParts)
