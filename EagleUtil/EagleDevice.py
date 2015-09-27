from lxml import etree as ET;
import copy
from EagleError import *

def ensure(parent, child, args={}):
    if parent.find(child) is not None:
        return parent.find(child)
    else:
        return ET.SubElement(parent, child, args)

# this is actually a device set
class EagleDevice:
    _et = None;
    _root = None;

    def __init__(self, element):
        self._root = element

    def getRoot(self):
        return self._root

    def setName(self, name):
        name = name.upper()
        self._root.set("name", name)
        
    def setGate(self, symbol):
        symbol = symbol.upper()
        g = self._gate.set("symbol", symbol)
        return g

    def setPackage(self, package):
        package = package.upper()
        g = self._root.set("package", package)
        return g
        
    def Connect(self, pin, pad):
        self._connects = ensure(self._root, "connects")
        connect = ET.SubElement(self._connects, "connect", {
                "gate":"G$1",
                "pad":str(pad),
                "pin":str(pin)
                })
        return connect
    
    def getName(self):
        return self._root.get("name")
