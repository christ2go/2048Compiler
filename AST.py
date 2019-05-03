class AST():
    pass
from Types import *
from Scope import *



class PrettyUtils():
    def pWi(ident, str):
        print("    "*ident,end="")
        print(str)
class FunctionDecl(AST):
    def __init__(self,retType, Name, ArgList, Statement):
        self.retType = retType
        self.Name = Name
        self.ArgList = ArgList
        self.Statement = Statement
    # Add this function to scope
    def typecheck(self, scope):
        for (a,b) in self.ArgList.list:
            scope.enter(a,b)
        self.Statement.typecheck(scope)

    def emit(self, emitter):
        print("Emitting function %s"%(self.Name))
        emitter.emitBeginF(self.Name)
        i = 0
        for (a, b) in self.ArgList.list:
            emitter.registerTemp(b.getSize(), a)
            emitter.emitLoadParam(a, i)
            i = i+1
        self.Statement.emit(emitter)

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "Funktionsdeklaration")
        PrettyUtils.pWi(ident+1, "Name: %s"%(self.Name))
        PrettyUtils.pWi(ident+1, "Argumentsliste")
        self.ArgList.pretty(ident+1)
        self.Statement.pretty(ident+1)




class ArgListAst(AST):
    def __init__(self, list):
        self.list = list
    # Introduce them into the scope
    def type(self, scope):
        pass
    def pretty(self,ident):
        for x in self.list:
            PrettyUtils.pWi(ident+1, x[0])
class UnaryMinus(AST):
    def __init__(self,t):
        self.t = t

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "UnaryMinus")
        self.t.pretty(ident + 1)
    def typecheck(self, scope):
        self.type = self.t.typecheck()
        if self.type != IntT and self.type != ShortT:
            pass
        pass
class AdressOf(AST):
    def __init__(self,t):
        self.t = t

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "AdressOf")
        self.t.pretty(ident+1)
    def typecheck(self, scope):
        self.t.typecheck(scope)
        self.type = RefType(self.t.type)
class Indirect(AST):
    def __init__(self,t):
        self.t = t

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "Indirect")
        self.t.pretty(ident + 1)
    def typecheck(self, scope):
        self.t.typecheck(scope)
        t = self.t.type
        if t == None or not t.isRefType():
            print("RefTypeError")
            print(scope.variables)
            self.t.pretty(0)
        self.type = t.getParent()
    def emit(self, emitter):
        v = emitter.registerTemp(self.t.type.getParent().getSize())
        t = self.t.emit(emitter)
        emitter.free(t)
        emitter.emitDeference(v,t,self.t.type.getParent().getSize())
        return v
    def emitPlace(self, emitter):
        t = self.t.emit(emitter)
        return t

class ArrayAccess(AST):
    def __init__(self,t,ind):
        self.t = t
        self.ind = ind

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "ArrayAccess")
        PrettyUtils.pWi(ident, "- Array")
        self.t.pretty(ident+1)
        PrettyUtils.pWi(ident, "- Index")
        self.ind.pretty(ident + 1)

    def typecheck(self, scope):
        self.t.typecheck(scope)
        self.t.pretty(0)
        self.ind.typecheck(scope)
        t = self.t.type
        if not t.isRefType():
            print("TypeError")
            print(t)
        self.type = t.getParent()
        print("AC")
        print(self.type)

    def emit(self, emitter):
        z = self.t.emitPlace(emitter)
        y = self.ind.emit(emitter)
        t3 = emitter.registerTemp()
        tc = emitter.registerTemp()
        adr = emitter.registerTemp()
        erg = emitter.registerTemp()
        emitter.emitConstant(tc, self.type.getSize())
        emitter.emitBinary(t3, y , "*", tc)
        emitter.emitBinary(adr, t3, "+", z)

        emitter.emitDeference(erg, adr, self.type.getSize())
        emitter.free(y)
        emitter.free(t3)
        emitter.free(tc)
        return erg
    def emitPlace(self, emitter):
        z = self.t.emitPlace(emitter)
        y = self.ind.emit(emitter)
        t3 = emitter.registerTemp()
        tc = emitter.registerTemp()
        adr = emitter.registerTemp()
        erg = emitter.registerTemp()
        emitter.emitConstant(tc, self.type.getSize())
        emitter.emitBinary(t3, y, "*", tc)
        emitter.emitBinary(adr, t3, "+", z)
        emitter.free(z)
        emitter.free(y)
        emitter.free(t3)
        emitter.free(tc)
        return adr



class StatementList():
    def __init__(self,list):
        self.list = list
    def pretty(self, ident):
        PrettyUtils.pWi(ident, "StatementList")
        for x in self.list:
            x.pretty(ident+1)
    def typecheck(self, scope):
        for x in self.list:
            x.typecheck(scope)
        # Get Function from table

    def emit(self, emitter):
        for x in self.list:
            x.emit(emitter)

class Statement(AST):
    pass
class Nop(Statement):
    def pretty(self, ident):
        pass
class ReturnStatement(AST):
    def __init__(self, rval):
        self.retval = rval

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "Return")
        self.retval.pretty(ident + 1)

    def typecheck(self, scope):
        self.type = self.retval.typecheck(scope)
        # TODO Test if compatible
        return self.type
    def emit(self, emitter):
        tx = self.retval.emit(emitter)
        emitter.emitReturn(tx)

class IfStatement(Statement):
    def __init__(self, cond, impl, implf):
        self.cond = cond
        self.impl = impl
        self.implf = implf
    def pretty(self, ident):
        PrettyUtils.pWi(ident, "IfStatement")
        PrettyUtils.pWi(ident, "- Bedingung")
        self.cond.pretty(ident + 1)
        PrettyUtils.pWi(ident, "- Konsequenz")
        self.impl.pretty(ident + 1)
        if self.implf != None:
            PrettyUtils.pWi(ident, "- Else")
            self.implf.pretty(ident + 1)
    def typecheck(self, scope):
        self.cond.typecheck(scope)
        self.impl.typecheck(scope)
        if self.implf != None:
            self.implf.typecheck(scope)

    def emit(self, emitter):
        l1 = emitter.registerLabel("L_if_begin")
        l2 = emitter.registerLabel("L_if_else")
        l3 = emitter.registerLabel("L_if_end")
        emitter.emitLabel(l1)
        r1 = self.cond.emit(emitter)
        emitter.emitEqZGoto(r1, l2)
        self.impl.emit(emitter)
        emitter.emitJump(l3)
        emitter.emitLabel(l2)
        if self.implf != None:
            self.implf.emit(emitter)
        emitter.emitLabel(l3)
class WhileLoop(Statement):
    def __init__(self, cond, conclusion):
        self.cond = cond
        self.conclusion = conclusion

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "WhileLoop")
        PrettyUtils.pWi(ident, "- Bedingung")
        self.cond.pretty(ident + 1)
        PrettyUtils.pWi(ident, "- Konsequenz")
        self.conclusion.pretty(ident + 1)
    def typecheck(self, scope):
        self.cond.typecheck(scope)
        self.conclusion.typecheck(scope)
    def emit(self, emitter):
        l1 = emitter.registerLabel("while_loop")
        l2 = emitter.registerLabel("while_end")
        c = self.cond.emit(emitter)
        emitter.emitEqZGoto(c, l2)
        emitter.emitJump(l1)
        emitter.emitLabel(l2)
class ForLoop(Statement):
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "ForLoop")
        PrettyUtils.pWi(ident, "- First ")
        self.a.pretty(ident + 1)
        PrettyUtils.pWi(ident, "- Second ")
        self.b.pretty(ident + 1)
        PrettyUtils.pWi(ident, "- Third ")
        self.c.pretty(ident + 1)
        PrettyUtils.pWi(ident, "- Loop")
        self.d.pretty(ident+1)
    def typecheck(self, scope):
        self.a.typecheck(scope)
        self.b.typecheck(scope)
        self.c.typecheck(scope)
        self.d.typecheck(scope)
    def emit(self, emitter):
        # Generate labels
        l1 = emitter.registerLabel("for_begin")
        l2 = emitter.registerLabel("for_end")
        self.a.emit(emitter)
        emitter.emitLabel(l1)
        b = self.b.emit(emitter)
        emitter.emitEqZGoto(b,l2)
        self.c.emit(emitter)
        self.d.emit(emitter)
        emitter.emitJump(l1)
        emitter.emitLabel(l2)


        # TODO Ensure b not void
class Expression(AST):
    pass
class BinaryExpression(AST):
    def __init__(self, l, r, op):
        self.l = l
        self.r = r
        self.op = op

    def pretty(self, ident):
        PrettyUtils.pWi(ident, "Binary")
        PrettyUtils.pWi(ident, self.op)
        self.l.pretty(ident + 1)
        self.r.pretty(ident + 1)
    def __str__(self):
        return "BinaryAst: %s %s %s"%(str(self.l),self.op,str(self.r))
    def typecheck(self, scope):
        self.l.typecheck(scope)
        self.r.typecheck(scope)
        x = self.l.type
        y = self.r.type
        if set([x,y]) != set([ShortT, IntT]):
            if x != y:
                print("TypeError")
                print(x)
                self.l.pretty(0)
                print(scope.variables)
            self.type = x
        else:
            self.type = IntT
    def emit(self, emitter):
        t1 = self.l.emit(emitter)
        t2 = self.r.emit(emitter)
        t3 = emitter.registerTemp(self.type.getSize())
        emitter.emitBinary(t3, t1, self.op, t2)
        emitter.free(t1)
        emitter.free(t2)
        return t3
class AssignExpr(AST):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def pretty(self, depth=0):
        PrettyUtils.pWi(depth, "= (VarAssign)")
        self.lhs.pretty(depth + 1)
        self.rhs.pretty(depth + 1)

    def typecheck(self, scope):
        t1 = self.lhs.typecheck(scope)
        t1 = self.lhs.type
        t2 = self.rhs.typecheck(scope)
        t2 = self.rhs.type
        if t1 == t2:
            self.type = t1
        else:
            if set([t1,t2]) == set([ShortT, IntT]):
                self.type = t1
                return
            print("Error")
            print(t1)
            self.lhs.pretty
            print(t2)
            import sys
            sys.exit(-1)

    def emit(self, emitter):
        y = self.rhs.emit(emitter)
        z = self.lhs.emitPlace(emitter)
        if isinstance(self.lhs, VariableAst):
            emitter.emitAssign(z,y)
        else:
            emitter.emitRAssign(z,y, self.type.size)
        emitter.free(y)


class VariableDecl(AST):
    def __init__(self, name, type, init):
        self.name = name
        self.init = init
        self.Vtype = type

    def pretty(self, depth=0):
        PrettyUtils.pWi(depth, "VariableDecl")
        PrettyUtils.pWi(depth, "Name %s"%(self.name))
        if self.init:
            self.init.pretty(depth+1)
    def typecheck(self, scope):
        if self.init:
            x = self.init.typecheck(scope)
            print(self.init.type)
            print(self.Vtype)
            if not(self.init.type == ShortT and self.Vtype == IntT):
                assert self.init.type == self.Vtype
        scope.enter(self.name, self.Vtype)
        self.type = self.Vtype
    def emit(self, emitter):
        n = emitter.registerTemp(self.type.getSize(), self.name)
        if self.init:
            tx = self.init.emit(emitter)
            emitter.emitAssign(n, tx)
        return n
class ConstantAst(AST):
    def __init__(self, constant):
        self.const = constant
        if int(self.const) < 2**4:
            self.type = ShortT
        else:
            self.type = IntT
    def pretty(self, depth=0):
        PrettyUtils.pWi(depth, "Constant %s"%(str(self.const)))
    def typecheck(self, scope):
        return self.type
    def emit(self, emitter):
        t = emitter.registerTemp()
        emitter.loadConstant(t, self.const)
        return t
class VariableAst(AST):
    def __init__(self, vn):
        self.varname = vn
    def pretty(self, ident):
        PrettyUtils.pWi(ident, "VariableAccess")
        PrettyUtils.pWi(ident, "Name %s" % (self.varname))
    def typecheck(self, scope):
        self.type = scope.typeOf(self.varname)
        print("Variable %s has type %s"%(self.varname,str(self.type)))
        if self.type == None:
            import sys
            print("Exiting")
            sys.exit(-1)
    def emit(self, emitter):
        print(self.varname)
        print(self.type)
        tname = emitter.registerTemp(self.type.getSize())
        emitter.emitAssign(tname, self.varname)
        return tname
    def emitPlace(self, emitter):
        return self.varname


class FuncCallAst(AST):
    def __init__(self, funcname, args):
        self.funcname = funcname
        self.args = args
    def pretty(self,ident):
        PrettyUtils.pWi(ident, "FuncCall")
        PrettyUtils.pWi(ident, "Name %s" % (self.funcname))
        PrettyUtils.pWi(ident, "Argumente")
        for x in self.args:
            x.pretty(ident+1)
    def typecheck(self, scope):
        for x in self.args:
            x.typecheck(scope)
        fn = scope.getFunction(self.funcname)
        self.type = fn[0]
    def emit(self, emitter):
        l = [x.emit(emitter) for x in self.args]
        t = emitter.registerTemp()
        emitter.emitCallBegin()
        for i,x in enumerate(l):
            emitter.emitFParam(x,i)
        emitter.emitCall(self.funcname, t)
        emitter.emitCallEnd()
        return t
