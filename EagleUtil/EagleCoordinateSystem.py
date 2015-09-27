from lxml import etree as ET;
import copy
import math
from EagleError import *

class Origin:
    eff_x_origin = 0;
    eff_y_origin = 0;
    eff_rotation = 0;
    eff_mirrored = False;

    def __init__(self, parent, x = 0, y = 0, r = 0, m = False):
        self.parent = parent;
        self.x_origin = x;
        self.y_origin = y;
        self.rotation = r;
        self.mirrored = m;
        if self.parent is not None:
            self.updateEffective()
        
    def transformPoint(self, x,y):
        r = [];
#        print "Transformed " + str(x) + ", " + str(y)

        r = [x * math.cos(-math.radians(self.eff_rotation))  + y * math.sin(-math.radians(self.eff_rotation)),
             -x * math.sin(-math.radians(self.eff_rotation))  + y * math.cos(-math.radians(self.eff_rotation))];

        if self.eff_mirrored:
            r[0] = (-r[0] + self.eff_x_origin)
        else:
            r[0] = (r[0] + self.eff_x_origin)

        r[1] = r[1] + self.eff_y_origin

 #       print "to " + str(r[0]) + ", " + str(r[1])
        return r;

    def updateEffective(self):
        if self.parent.eff_mirrored:
            [tx, ty] = self.transformPoint(-self.x_origin, self.y_origin)
        else:
            [tx, ty] = self.transformPoint(self.x_origin, self.y_origin)

        self.eff_x_origin = (self.parent.eff_x_origin + tx)
        # [tx, ty] = transformPoint(self.x_origin, self.y_origin)
        # if self.parent.eff_mirrored:
        #     self.eff_x_origin = (self.parent.eff_x_origin + tx)
        # else:
        #     self.eff_x_origin = (self.parent.eff_x_origin + tx)
        self.eff_y_origin = self.parent.eff_y_origin + ty
        self.eff_rotation = (self.parent.eff_rotation + self.rotation) % 360
        self.eff_mirrored = (self.parent.eff_mirrored and not self.mirrored) or ( not self.parent.eff_mirrored and self.mirrored)


    def renderCurrentOrientation(self, element):
        m = False;
        r = 0;
        if element.get("rot"):
            if element.get("rot")[0] == "M":
                m = True;
                r = int(element.get("rot")[2:])
            else:
                m = False;
                r = int(element.get("rot")[1:])
                
        r  =  str((self.eff_rotation + r) % 360);

        if self.eff_mirrored:
            if m:
                return "R" + r
            else: 
                return "MR" + r
        else:
            if m:
                return "MR" + r
            else: 
                return "R" + r

class EagleCoordinateSystem:
    _currentOrigin = Origin(None);

    def dump(self):
        print "eff_x = " + str(self._currentOrigin.eff_x_origin)
        print "eff_y = " + str(self._currentOrigin.eff_y_origin)
        print "eff_rot = " + str(self._currentOrigin.eff_rotation)
        print "eff_m = " + str(self._currentOrigin.eff_mirrored)

    def push(self, x, y, r, m):
#        print "WAS"
#        self.dump()
        self._currentOrigin = Origin(self._currentOrigin, x, y, r, m);
 #       print "PUSHED: " + str(x) + " " + str(y) + " " + str(r) + " " + str(m)
 #       print "IS"
 #       self.dump()

    def pushElement(self, e):
        if e.get("rot"):
            if e.get("rot")[0] == "M":
                m = True;
                r = int(e.get("rot")[2:])
            else:
                m = False;
                r = int(e.get("rot")[1:])
        else:
            m = False;
            r = 0;

        self.push(float(e.get("x")), float(e.get("y")), r, m);

    def pop(self):
 #       print "WAS"
 #       self.dump()
        self._currentOrigin = self._currentOrigin.parent
 #       print "POPPED:"
 #       print "IS"
 #       self.dump()

    def transformPoint(self, x,y):
#        self.dump()
        return self._currentOrigin.transformPoint(x,y)

    def transformElement(self, e):
  #     ET.dump(e)
        e = copy.deepcopy(e)
        for s in ["", "1", "2"]:
            if e.get("x"+ s):
                ny = float(e.get("y" + s))
                nx = float(e.get("x" + s))
                p = self.transformPoint(nx,ny)
                e.set("x" + s, str(p[0]))
                e.set("y" + s, str(p[1]))

        if self._currentOrigin.eff_mirrored:
            if e.tag == "wire" and e.get("curve"):
                e.set("curve", str(-float(e.get("curve"))))
            elif e.tag == "wire":
                None;
            elif e.tag == "hole":
                None;
            else:
                e.set("rot", self._currentOrigin.renderCurrentOrientation(e));

#        ET.dump(e)
        return e;

    def isElementOnTop(self, e):
        if e.get("rot"):
            if e.get("rot")[0] == "M":
                return self._currentOrigin.eff_mirrored
            else:
                return not self._currentOrigin.eff_mirrored
        else:
            return not self._currentOrigin.eff_mirrored

