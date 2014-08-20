class EagleError(Exception):
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return repr(self.s)
