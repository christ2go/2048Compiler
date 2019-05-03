from mipsgenerate import Location, Mips, Register


class Code:
    def __init__(self, op="", arg1="", arg2="", arg3="", arg4=""):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.arg4 = arg4
    def __str__(self):
        return str(self.op)+" "+str(self.arg1)+" "+str(self.arg2)+" "+str(self.arg3)+" "+str(self.arg4)

class Emitter:
    def __init__(self):
        self.code = []
        self.lc = 0
        self.vc = 0
        self.variables = {} # Dictionary of variables + size
        self.unused = set()
        self.callStored = []
    def registerLabel(self, name="label_"):
        self.lc += 1
        return name+str(self.lc)
    def emitLoadParam(self, varname, i):
        self.code.append(Code("LoadParam", varname, i))
    def registerTemp(self, size=4,name=""):
        if name == "" and len(self.unused) != 0 and False:
            iteras = 10
            i = 0
            while  i < iteras:
                y = self.unused.pop()
                if y[1] == size:
                    return y[0]
                self.unused.add(y)
                i = i+1

        self.vc += 1
        if name == "":
            name = "t_" + str(self.vc)
        self.variables[name] = {"size": size}
        return name

    def emit(self, code):
        self.code.append(code)

    def emitBinary(self, ziel, x1, op, x2):
        self.code.append(Code("binary",ziel,x1,op,x2))
    def emitEqZGoto(self, var, label):
        self.code.append(Code("ifEqZGoto", var, label))
    def emitAssign(self, x, y):
        self.code.append(Code("assign", x, y))
    def emitRAssign(self, x, y, w):
        self.code.append(Code("assign*", x, y, w))
    def free(self, var):
        self.unused.add((var, self.variables[var]["size"]))
    def loadConstant(self,t,x):
        self.code.append(Code("assignC",t,x))
    def emitReturn(self, x1):
        self.code.append(Code("return", x1))
    def emitJump(self, x1):
        self.code.append(Code("goto", x1))
    def emitLabel(self, labelname):
        self.code.append(Code("label", labelname,":"))

    def emitBeginF(self, labelname):
        self.code.append(Code("beginfunction", labelname, ":"))


    def emitFParam(self, varname, i):
        self.code.append(Code("fparam", varname,i))
    def emitCallBegin(self):
        self.code.append(Code("begincall"))
    def emitCallEnd(self):
        self.code.append(Code("endcall"))
    def emitCall(self, fn, temp):
        self.code.append(Code("call", fn, temp))
    def emitPointerAccess(self, var, offset):
        pass
    def emitConstant(self, var, const):
        self.code.append(Code("assignC", var, const))
    def emitDeference(self, var, arg, size):
        self.code.append(Code("assignVof", var, arg, size))

    def print(self):
        for x in self.code:
            print(x)
    def reset(self):
        self.lc = 0
        self.vc = 0
        self.unused = set()
        self.variables = {}
        self.callStored = []

    def generateMips(self):
        M = Mips()
        locations = {}
        os = 0
        for x in self.variables:
            locations[x] = Location(x,"$fp", os, self.variables[x]["size"])
            os += 4
        for x in self.code:
            print("# %s"%(str(x)))
            if x.op == "beginfunction":
                print("%s:"%(x.arg1))
                print("subu $sp, $sp, 8\t# decrement sp to make space to save ra, fp");
                print("sw $fp, 8($sp)\t# save fp");
                print("sw $ra, 4($sp)\t# save ra");
                print("addiu $fp, $sp, 8\t# set up new fp");
                print("subu $sp, $sp, %d\t# decrement sp to make space for locals/temps"%(
                     os));
            elif x.op == "label":
                M.spillAllDirty()
                print("%s:" % (x.arg1))
            elif x.op == "LoadParam":
                v = locations[x.arg1]
                reg = M.argRegister[x.arg2]
                M.generateStore(v, reg)
            elif x.op == "assignC":
                v = locations[x.arg1]
                r = M.getRegister(v)
                M.emitLoadConstant(r, x.arg2)
            elif x.op == "assign*":
                v = locations[x.arg1]
                t = locations[x.arg2]
                r = M.getRegister(v, "w")
                z = M.getRegister(t, "r", v, r)
                if x.arg3 == 2:
                    print("sh %s 0(%s)"%(z.mipsName(), r.mipsName()))
                else:
                    print("sw %s 0(%s)" % (z.mipsName(), r.mipsName()))
            elif x.op == "assign":
                v = locations[x.arg1]
                t = locations[x.arg2]
                r = M.getRegister(v)
                z = M.getRegister(t, "r", r)
                print("move %s %s" % (r.mipsName(), z.mipsName()))
            elif x.op == "binary":
                lo1 = locations[x.arg2]
                lo2 = locations[x.arg4]
                r1 = M.getRegister(lo1, "r")
                r2 = M.getRegister(lo2, "r", r1)
                v = locations[x.arg1]
                r3 = M.getRegister(v,"w",r1,r2)
                binops = {
                    "+": "add",
                    "-": "sub",
                    "*": "mul",
                    "==": "seq",
                    "<=": "sle",
                    "<" : "slt",
                    ">":  "sgt",
                    ">=": "sge",
                    "&&": "mul",
                    "/": "div"
                }
                print("%s %s %s %s"%(binops[x.arg3],r3.mipsName(),r1.mipsName(), r2.mipsName()))


            elif x.op == "goto":
                M.spillAllDirty()
                print("b %s"%(x.arg1))
            elif x.op == "return":
                v = locations[x.arg1]
                r = M.getRegister(v, "r")
                print("move $v0 %s"%(r.mipsName()))
                M.spillAllDirty()
                print("jr $ra")
            elif x.op == "ifEqZGoto":
                M.spillAllDirty()
                z = locations[x.arg1]
                r = M.getRegister(z, "r")
                print("beq %s $0 %s "%(r.mipsName(), x.arg2))
            elif x.op == "begincall":
                # Save registers
                c = 0
                toStore = []
                for x in M.registers:
                    if x.saveOnJump and x.dirty:
                        c += 1
                        toStore.append(x.mipsName())
                for x in M.argRegister:
                    if x.saveOnJump:
                        c += 1
                        toStore.append(x.mipsName())
                for x in M.special:
                    if x.saveOnJump:
                        c += 1
                        toStore.append(x.mipsName())
                print("subu $sp, $sp, %d"%(c*4)) # Allocate space
                for i,x in enumerate(toStore):
                    print("sw %s %d($sp)"%(x,i*4))
                self.callStored.append((c*4, toStore))
            elif x.op == "fparam":
                y = locations[x.arg1]
                z = M.getRegister(y, 'r')
                print("mov $a%d  %s "%( x.arg2,z.mipsName()))
            elif x.op == "endcall":
                r = self.callStored.pop()
                for i,x in enumerate(r[1]):
                    print("lw %s %d($sp)" % (x, i * 4))
                print("addi $sp, $sp, %d" % (c * 4))  # Allocate space
            elif x.op == "call":
                print("jal %s"%x.arg1)
                y = locations[x.arg2]
                z = M.getRegister(y, 'w')
                M.generateStore(y, Register("v0", False))
            elif x.op == "assignVof":
                v = locations[x.arg1]
                t = locations[x.arg2]
                r = M.getRegister(v)
                z = M.getRegister(t, "r", v, r)
                if x.arg3 == 2:
                    print("lh %s 0(%s)" % (r.mipsName(), z.mipsName()))
                else:
                    print("lw %s 0(%s)" % (r.mipsName(), z.mipsName()))
            else:
                print("Not implemented")
                print(x)
                import sys
                sys.exit(-1)




