#!/usr/bin/env python

import argparse
from lxml import etree as ET;
import sys
from EagleLibrary import *
from EagleBoard import *
from EagleCoordinateSystem import *
from EagleSymbol import *
from EagleDevice import *
from EagleDeviceSet import *
from EaglePackage import *
from EagleSchematic import *
import re
import pipes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool for moving symbols, packages, and devices betweens brd, sch, and lbr files.  For instance, to build a library from a brd and sch, do something like './extractLibraries.py --src foo.sch bar.brd --dst Empty.lbr'")

    parser.add_argument("--src", required=True,  type=str, nargs='+', dest='srcFile', help="source .brd, .sch, or .lbr file")
    parser.add_argument("--dst", required=True,  type=str, nargs=1, dest='dstFile', help="destination .brd, .sch, or .lbr file")
#    parser.add_argument("--targets", required=False,  type=str, nargs='*', dest='targets', help="Items to copy")

    args = parser.parse_args()

    if re.match(".*\.sch", args.dstFile[0]):
        dstF = EagleSchematic(args.dstFile[0])
    elif re.match(".*\.brd", args.dstFile[0]):
        dstF = EagleBoard(args.dstFile[0])
    elif re.match(".*\.lbr", args.dstFile[0]):
        dstF = EagleLibrary(args.dstFile[0])
    else:
        raise EagleError("Unknown type: " +  args.dstFile[0])    
    
    dst = dstF.getLibraryContainer().find("library")
    dstLib = EagleLibrary(dst)

    for f in args.srcFile:
        if re.match(".*\.sch", f):
            src = EagleSchematic(f).getLibraryContainer()
        elif re.match(".*\.brd", f):
            src = EagleBoard(f).getLibraryContainer()
        elif re.match(".*\.lbr", f):
            src = EagleLibrary(f).getLibraryContainer()
        else:
            raise EagleError("Unknown type: " +  f)

        for library in src.findall("library"):
            srcLib = EagleLibrary(library)

            if srcLib.getPackages() is not None:
                for i in srcLib.getPackages():
                    dstLib.addItem(i)
            if srcLib.getSymbols() is not None:
                for i in srcLib.getSymbols():
                    dstLib.addItem(i)
            if srcLib.getDevicesets() is not None:
                for i in srcLib.getDevicesets():
                    dstLib.addItem(i)

    f = args.dstFile[0]
    # write it out.  Eagle has trouble reading xml with no newlines.  Run it through xmllint to make it pretty.
    t = pipes.Template()
    t.append("xmllint --format $IN", "f-")
    dstF.write(t.open(f, 'w'))
