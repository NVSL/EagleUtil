from lxml import etree as ET;
import copy
from EagleError import *

class EaglePackage:
    _et = None;
    _root = None;
    def __init__(self, element):
        self._root = element

    def getRoot(self):
        return self._root

    # def AddArt(self, k, *xy):
    #     layer=94
    #     width=.254
    #     art = ET.SubElement(self._root, k, width=str(width), layer=str(layer));
    #     if len(xy) % 2 is not 0:
    #         raise EagleError("Odd number of coordinates")
        
    #     for i in range(0,len(xy)/2,1):
    #         art.set("x"+str(i+1), str(self.scale(xy[i*2])))
    #         art.set("y"+str(i+1), str(self.scale(xy[i*2 + 1])))
    #     return art
        

    # def AddPin(self, name, x,y):
    #     pin = ET.SubElement(self._root, "pin", {
    #             "name":name.upper(),
    #             "length":"middle",
    #             "x":str(self.scale(x)),
    #             "y":str(self.scale(y)),
    #             })
    #     return pin
        
    def getName(self):
        return self._root.get("name")
