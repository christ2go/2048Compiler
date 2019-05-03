import random


class Register():
    def __init__(self, name, saveOnJump):
        self.name = name
        self.saveOnJump = saveOnJump
        self.reinit()
    def reinit(self):
        self.current = None  # Stores current variable
        self.var = None
        self.dirty = False
    def mipsName(self):
        return "$"+self.name
class Location():
    def __init__(self, name, seg, os, size=4):
        self.offset = os
        self.segment = seg
        self.name = name
        self.size = size
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.offset, self.segment, self.size) == (other.offset, other.segment, other.size)
        else:
            return False

class Mips():
    def __init__(self):
        self.registers = [
            Register("t0", True),
            Register("t1", True),
            Register("t2", True),
            Register("t3", True),
            Register("t4", True),
            Register("t5", True),
            Register("t6", True),
            Register("t7", True),


        ]
        self.argRegister = [
            Register("a0", True),
            Register("a1", True),
            Register("a2", True),
            Register("a3", True)
        ]
        self.special = [
            Register("ra", True),
            Register("fp", True)
        ]

    def loadIntoRegister(self):
        pass
    def spillRegister(self):
        for x in self.registers:
            if x.current != None and x.dirty:
                x.reinit()
                # Save onto Stack
    def findRegisterWithContents(self, var):
        for r in self.registers:
            if r.var != None:
                if r.var == var:
                    return r
        return None

    def getRegister(self, var, grund = "w", avoid1 = None, avoid2 = None):
        if self.findRegisterWithContents(var):
            r = self.findRegisterWithContents(var)
            if grund == "w":
                r.dirty = True
            return r
        elif self.findRegisterWithContents(None):
            r = self.findRegisterWithContents(None)
        else:
            r = self.SelectRegisterToSpill(avoid1, avoid2)
        if grund == "w":
            r.dirty = True
        r.var = var
        # Emit Load
        if grund == "r":
            command = "lw"
            if var.size == 2:
                command = "lh"
            print("%s %s, %d(%s)" % (command, r.mipsName(), var.offset, var.segment))
        return r
    def SelectRegisterToSpill(self, avoid1, avoid2):
        for r in self.registers:
            if r == avoid1 or r == avoid2:
                continue
            if not r.dirty:
                return r
        # Else pick randon
        random.shuffle(self.registers)
        for r in self.registers:
            if r == avoid1 or r == avoid2:
                continue
            return r
    def spillRegister(self, r):
        loc = r.var
        if loc != None and r.dirty:
            self.generateStore(loc, r)
            # Emit store
        r.var = None
    def spillAllDirty(self):
        for x in self.registers:
            self.spillRegister(x)

    def generateStore(self, storel, fromWhere):
        command = "sw"
        if storel.size == 2:
            command = "sh"
        print("%s %s, %d(%s)"%(command, fromWhere.mipsName(),storel.offset, storel.segment))

    def emitLoadConstant(self, reg, constant):
        print("li %s %d"%(reg.mipsName(), int(constant)))





