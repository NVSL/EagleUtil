from lxml import etree as ET;
import copy
from EagleError import *

class EagleSchematicSheet:
    _root = None;
    _sheet = None;

    _sheetParts = ["plain", "instances", "busses", "nets"]

    def addAccessor(self, x):
        a = lambda : getattr(self, "_" + x)
        t = x[0].upper() + x[1:]
        a.__name__ = "get" + t
        setattr(self, "get" + t, a)

    def __init__(self, element):
        self._sheet = element

        for i in self._sheetParts:
            setattr(self, "_" + i, None)
            self.addAccessor(i);
        for i in self._sheetParts:
            #            print i, " ", self._board.find(i)
            setattr(self, "_" + i, self._sheet.find(i))
            
    def getRoot(self):
        return self._root

