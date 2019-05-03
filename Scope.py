class Scope():
    def __init__(self, parent = None):
        self.variables = {}
        self.functions = {}
        self.parent = parent
    def push(self):
        return Scope(self)
    def enter(self,name,type):
        self.variables[name] = type
        print("Entered name %s with type %s"%(name,str(type)))
    def typeOf(self, varname):
        return self.variables.get(varname, None)
    def addFunction(self, name, t, argl):
        self.functions[name] = (t, argl)
    def getFunction(self,x):
        if self.parent:
            return self.parent.getFunction(x)
        return self.functions[x]