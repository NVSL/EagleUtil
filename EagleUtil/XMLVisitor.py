from lxml import etree as ET

class XMLVisitor:
    def visitFilter(self, e):
        return True

    def decendFilter(self, e):
        return True

    def default_pre(self,element):
        pass

    def default_post(self,element, state):
        pass

    def always_pre(self, element):
        pass
    def always_post(self, element, state):
        pass

    def visit(self, root):
        alwaysState = self.always_pre(root)
        if self.visitFilter(root):
            try:
                t = root.tag.split("}")[-1]
                pre = getattr(self, t + "_pre")
            except AttributeError as e:
                pre = self.default_pre
            state = pre(root)

        if self.decendFilter(root):
            for e in root:        
                self.visit(e)
                
        if self.visitFilter(root):
            try:
                t = root.tag.split("}")[-1]
                post = getattr(self, t + "_post")
            except AttributeError:
                post = self.default_post
            post(root, state)
        self.always_post(root,alwaysState)

# def _pre():
#     return lambda self, element : self.default_pre(element)

# def _post():
#     return lambda self, element : self.default_post(element)

# for t in eagleTags:
#     temp = t
#     pre = _pre()
#     pre.__name__ = temp + "_pre"
#     setattr(EagleVisitor, temp + "_pre", pre)
    
#     post = _post()
#     post.__name__ = temp + "_post"
#     setattr(EagleVisitor, temp + "_post", post)
