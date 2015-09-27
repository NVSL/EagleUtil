from lxml import etree as ET;
import copy
from EagleError import *
from EagleDevice import * 

def ensure(parent, child, args={}):
    if parent.find(child) is not None:
        return parent.find(child)
    else:
        return ET.SubElement(parent, child, args)

# this is actually a device set
class EagleDeviceSet:
    _et = None;
    _root = None;

    def __init__(self, element):
        self._root = element
        self._gates = ensure(self._root, "gates")
        self._devices = ensure(self._root, "devices")
        self._gate = ensure(self._gates, "gate", {
                "name":"G$1",
                "x":str(0),
                "y":str(0)
                })

    def getRoot(self):
        return self._root

    def setName(self, name):
        name = name.upper()
        self._root.set("name", name)
        
    def setGate(self, symbol):
        symbol = symbol.upper()
        g = self._gate.set("symbol", symbol)
        return g

    def getName(self):
        return self._root.get("name")

    def newDevice(self, name):
        name = name.upper()
        if self.findDevice(name) is None:
            d = ET.SubElement(self._devices, "device", {"name":name})
            device = EagleDevice(d)
            device.setName(name)
            return d
        else:
            raise EagleError("Device '" + name + "' already exists")
        
    def findDevice(self, name):
        name = name.upper()
        return self._devices.find("device[@name='"+name+"']");

    def setDescription(self, text):
        d = ensure(self._root, "description")
        d.text = text
        return d

    def deleteDevice(self, name):
        name = name.upper()
        p = self.findDevice(name)
        if p is not None:
            self._devices.remove(p)
