#!/usr/bin/env python

import argparse
from lxml import etree as ET;
import sys
from EagleLibrary import *
import pipes
import StringIO
import subprocess
import csv
import XMLVisitor

class gcomVisitor(XMLVisitor.XMLVisitor):
    def __init__(self):
        self._lineage = []
        self._withinVariant = 0
        self._variants = []
        self._hadChild = [True]
        self.pushVariant(ET.Element("device"))

    def currentVariant(self):
        return self._lineage[-1]

    def pushVariant(self, v):
        return self._lineage.append(v)

    def popVariant(self):
        self._lineage.pop()
        
    def decendFilter(self, e):
        return (e.tag == "variant")

    def getVariants(self):
        return self._variants

    def keyname_pre(self, e):
        if e.text is not None:
            self.currentVariant().set("keyname",e.text)
        else:
            self.currentVariant().set("keyname","")
    
    def default_pre(self, e):
        if self._withinVariant != 0:
            #ET.dump(e)
            self.currentVariant().append(copy.deepcopy(e))

    def variant_pre(self, v):
        self._withinVariant = self._withinVariant + 1
        self._hadChild[-1] = True
        self._hadChild.append(False)

        c = copy.deepcopy(self.currentVariant())
        if self.currentVariant().get("keyname") is not None:
            if v.get("suffix") is not None:
                c.set("keyname", self.currentVariant().get("keyname") + "-" + v.get("suffix"))
            else:
                c.set("keyname", self.currentVariant().get("keyname"))
        c.attrib.update(v.attrib)
#        print "start"
#        ET.dump(c)
        self.pushVariant(c)
        
    def variant_post(self, v, state):
        self._withinVariant = self._withinVariant - 1
        if not self._hadChild[-1]:
            self._variants.append(self.currentVariant())
        self._hadChild.pop()
        self.popVariant()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a family of Eagle Devices")
    parser.add_argument("--db", required=True,  type=str, nargs=1, dest='db', help="Spec for device list to build")
    parser.add_argument("--lbrin", required=True,  type=str, nargs=1, dest='lbrin', help="Library containing the symbol and the package.")
    parser.add_argument("--lbrout", required=True,  type=str, nargs=1, dest='lbrout', help="Output Library.")
    args = parser.parse_args()

    db = ET.parse(args.db[0])
    v = gcomVisitor()
    v.visit(db.getroot())

    lbrIn = EagleLibrary(args.lbrin[0])
#    ET.dump(db.getroot())
       
    for j in v.getVariants():
        #ET.dump(j)
        devset = lbrIn.findDeviceSet(j.find("devset").text.upper())
#        ET.dump(devset)
#        sys.exit(0)
        assert(devset is not None)
        for a in j.findall("attr"):
            j.set(a.get("key"), a.get("value"))
       
        device = ET.SubElement(devset.find("devices"), 
                               "device",
                               name=(j.find("format").text % j.attrib).upper(),
                               package=j.find("package").text.upper())
        connects = ET.SubElement(device,
                                 "connects");
        connections = eval(j.find("pinmapping").text)
        for c in connections:
            ET.SubElement(connects,
                          "connect",
                          gate="G$1",
                          pin=c,
                          pad=connections[c])

        t = ET.SubElement(device,"technologies")
        tech =ET.SubElement(t,"technology",name="")
        
        for a in j.attrib:
            ET.SubElement(tech,
                          "attribute",
                          name=a.upper(),
                          value=j.attrib[a])

lbrIn.write(args.lbrout[0])                               
        
        
