from lxml import etree as ET;
import sys
from EagleError import *
from EagleDevice import *

class EagleLayers:

    _libraryParts = ["layers", "packages", "symbols", "devicesets"]

    def addAccessor(self, x):
        a = lambda : getattr(self, "_" + x)
        t = x[0].upper() + x[1:]
        a.__name__ = "get" + t
        setattr(self, "get" + t, a)

    def __init__(self, initfrom):
        self._et = None;
        self._root = initfrom;
        self._byNum = {}
        self._byName = {}
    
        for l in self._root:
            self._byNum[l.get("number")] = l
            self._byName[l.get("name")] = l
#        print repr(self._byNum)
        #print repr(self._byName)

    def flipByName(self, name):
        origName = name
        if name[0] == "t":
            name = "b" + name[1:]
        elif name[0] == "b":
            name = "t" + name[1:]
        elif name == "Top":
            name = "Bottom"
        elif name == "Bottom":
            name = "Top"
        if name not in self._byName:
#            print "failed to flipp " + origName + " to " + name
            raise EagleError("Tried to flip layer '" + origName + "', but '" + name + "' doesn't exist")

#        print "flipped " + origName + " to " + name
#        raise EagleError("")
        return name

    def flipByNumber(self, number):
        try:
            name = self._byNum[number].get("name");
            new = self.flipByName(name)
 #           print "flipped " + number + " to " + self._byName[new].get("number")
            return self._byName[new].get("number")
        except KeyError:
            raise EagleError("Can't find layer number " + number)
        except EagleError:
            return number

    def numberToName(self, num, flip=False):
        if num not in self._byNum:
            raise EagleError("No layer number " + num)
        r = self._byNum[num].get("name")
        if flip:
            r = self.flipByName(r)
        return r

    def nameToNumber(self, name, flip=False):
        if name not in self._byName:
            raise EagleError("No layer named " + name)
        if flip:
            name = self.flipByName(name)
        return self._byName[name].get("number")
    
    def ensureLayer(self, name, number, color=4, fill=1):
        if (name not in self._byName and num in self._byNum) or (name in self._byName and num not in self._byNum):
            raise EagleError("Tried to create layer " + name + "@" + str(num) + ", but a layer of that name or number already exists.")
        
        if name not in self._byName and num not in self._byNum:
            ET.SubElement(self._root, "layer", {active:"yes",
                                                color:str(color),
                                                fill:str(fill),
                                                name:name,
                                                number:number,
                                                visible:"yes"})
    def checkForMissingLayers(self, root):
        for e in root.iter():
            if e.get("layer") is not None:
                if e.get("layer") not in self._byNum:
                    path = ""
                    t = e
                    while t is not None:
                        path = t.tag + "/" + path
                        t = t.getparent()
                    raise EagleError("Element in layer " + e.get("layer") + ", but there is no such layer.  path=" + path)
