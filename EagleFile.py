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
        


EagleFile.addAccessors(EagleFile, EagleFile._parts)
