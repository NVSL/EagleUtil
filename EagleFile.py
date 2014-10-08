from lxml import etree as ET;
#from lxml import etree as ET;
import sys
import os
import XMLUtil
import copy

from EagleError import *

class EagleFile(object):

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
        self._et = None
        self._root = None
        if not os.path.isfile(f):
            raise EagleError("Eagle file '{0}' does not exist".format(f))
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
        
    def remove_all_libraries (self):
        for lib in self.getLibraries().findall("library"):
            self.getLibraries().remove(lib)
            
    def add_library (self, library):
        import EagleLibrary
        print library
        assert type(library) == EagleLibrary.EagleLibrary, "Can only add libraries to a schematic if they are EagleLibrary type. Got: "+type(library).__name__
        assert library.name is not None, "EagleLibrary must have a name attribute if you are adding it to a schematic."
        assert library.name not in [lib.get("name") for lib in self.getLibraries().findall("library")], "Cannot add library with duplicat name: " + library.name
        
        new_lib = library.getLibrary()
        new_lib.set("name", library.name)
        
        new_lib_layers = library.getLayers().findall("layer")
        new_lib_layer_numbers = {layer.get("number"): layer for layer in new_lib_layers}
        old_layer_numbers = {layer.get("number"): layer for layer in self.getLayers().findall("layer")}
        
        #print "Old Layers:", old_layer_numbers
        #print "New Layers:", new_lib_layer_numbers
        
        for number in new_lib_layer_numbers.keys():
            if number not in old_layer_numbers:
                self.getLayers().append(copy.deepcopy(new_lib_layer_numbers[number]))
                print number, new_lib_layer_numbers[number].get("name")
                assert self.getLayers().find("./layer[@number='"+number+"']") is not None
                if number == "99":
                    print self.getLayers().find("./layer[@number='"+number+"']")
                    #exit(-1)
                    
        
        self.getLibraries().append(new_lib)

    def write(self, f):
        XMLUtil.formatAndWrite(self._et, f)
        


EagleFile.addAccessors(EagleFile, EagleFile._parts)
