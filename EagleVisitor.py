from lxml import etree as ET

eagleTags = ["approved",
             "attribute",
             "attributes",
             "autorouter",
             "board",
             "circle",
             "class",
             "classes",
             "clearance",
             "compatibility",
             "connect",
             "connects",
             "contactref",
             "description",
             "designrules",
             "device",
             "devices",
             "deviceset",
             "devicesets",
             "dimension",
             "drawing",
             "eagle",
             "element",
             "elements",
             "errors",
             "frame",
             "gate",
             "gates",
             "grid",
             "hole",
             "layer",
             "layers",
             "libraries",
             "library",
             "note",
             "package",
             "packages",
             "pad",
             "param",
             "pass",
             "pin",
             "plain",
             "polygon",
             "rectangle",
             "setting",
             "settings",
             "signal",
             "signals",
             "smd",
             "symbol",
             "symbols",
             "technologies",
             "technology",
             "text",
             "variantdefs",
             "vertex",
             "via",
             "wire"]

class EagleVisitor:
    _preFuncs = {}
    _postFuncs = {}

    def visitFilter(self, e):
        return True

    def decendFilter(self, e):
        return True

    def default_pre(self,element):
        pass
    def default_post(self,element):
        pass

    def visit(self, root):
        if self.visitFilter(root):
            pre = getattr(self, root.tag + "_pre")
            if pre is None:
                raise EagleError("Unknown tag: " + e.tag)
            pre(root)

        if self.decendFilter(root):
            for e in root:        
                self.visit(e)
                
        if self.visitFilter(root):
            post = getattr(self, root.tag + "_post" )
            if post is None:
                raise EagleError("Unknown tag: " + e.tag)
            post(root)
        

def _pre():
    return lambda self, element : self.default_pre(element)

def _post():
    return lambda self, element : self.default_post(element)

for t in eagleTags:
    temp = t
    pre = _pre()
    pre.__name__ = temp + "_pre"
    setattr(EagleVisitor, temp + "_pre", pre)
    
    post = _post()
    post.__name__ = temp + "_post"
    setattr(EagleVisitor, temp + "_post", post)
