#!/usr/bin/env python

import argparse
from lxml import etree as ET;
import sys
from EagleLibrary import *
import pipes
import StringIO
import subprocess

def ScanElement(e, pred, outparent):
    for i in e:
        if pred(i):
            new = ET.SubElement(outparent, i.tag, i.attrib)
            ScanElement(i, pred, new)

def isInteresting(e):
    return e.tag in ["eagle",
                     "drawing",
                     "settings",
                     "grid",
                     "layers",
                     "library",
                     "libraries",
                     "packages",
                     "package",
                     "symbols",
                     "symbol",
                     "devicesets",
                     "deviceset",
                     "gates",
                     "gate",
                     "devices",
                     "device",
                     "schematics",
                     "sheet",
                     "sheets",
                     "net",
                     "board",
                     "plain",
                     "elements",
                     "element",
                     "variantdefs",
                     "attributes",
                     "classes",
                     "designrules",
                     "autorouter",
                     "signals",
                     "signal"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize the content of an eagle file")
    parser.add_argument("-f", required=True,  type=str, nargs=1, dest='libname', help="Eagle file")
    args = parser.parse_args()

    f = ET.parse(args.libname[0])
    
    newTree = ET.ElementTree(ET.Element("eagle"))
    ScanElement(f.getroot(), isInteresting, newTree.getroot())

    t = pipes.Template()
    t.append("xmllint --format $IN", "f-")
    output = StringIO.StringIO()
    o = t.open("/tmp/foo", "w")
    newTree.write(o)
    subprocess.call(["cat", "/tmp/foo"])

    
