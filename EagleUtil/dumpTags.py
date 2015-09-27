#!/usr/bin/env python
import argparse
from lxml import etree as ET
#from lxml import etree as ET;
import sys
from EagleLibrary import *
from EagleBoard import *
import pipes
import svgwrite
from EagleLayers import *

def main():
    parser = argparse.ArgumentParser(description="Tool for auto-generating packages for breakout boards")
    parser.add_argument("--brd", required=True,  type=str, nargs=1, dest='brdfile', help="brd file")
    args = parser.parse_args()

    et = None;
    root = None;
    et = ET.parse(args.brdfile[0])
    root = et.getroot()                

    print "\n".join([ x.tag for x in root.iter()])
