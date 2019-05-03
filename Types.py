class Type():
  def __init__(self, str, size):
      self.strr = str
      self.size = size
  def isRefType(self):
      return False
  def __str__(self):
      return self.strr
  def getSize(self):
      return self.size

ShortT = Type("short",2)
IntT   = Type("int",4)
VoidT = Type("void",0)
class RefType(Type):
    def __init__(self, parent):
        self.parent = parent
        self.size = 4
    def isRefType(self):
        return True
    def __eq__(self, other):
        if other == None:
            return False
        if not other.isRefType():
            return False
        return other.getParent() == self.getParent()
    def __str__(self):
        return "pointer to "+str(self.parent)
    def getParent(self):
        return self.parent
class FunctionT(Type):
    pass

class Scope():
    def __init__(self):
        self.parent = None
        self.currentFunc = None # For return, etc computations