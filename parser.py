from Lexer import lexer
from Types import *
from AST import *
from TAC import *
GlobalScope = Scope()
class Parser():
    def __init__(self, lexer):
        self.lexer = lexer
        self.ct = lexer.token()
    def advance(self):
        self.ct = lexer.token()
    def error(self, msg):
        print(msg)
        print(self.ct)
    def match(self, t):
        return (self.ct.type == t)
    def parseProgram(self):
        x = []
        while self.ct != None:
            x.append(self.parseFunctionDeclaration())
        return x
    def expect(self,p):
        if not self.match(p):
            self.error("Expected %s"%p)
        self.advance()

    def parseFunctionDeclaration(self):
        t = self.parseType()
        if not self.match("ID"):
            self.error("Expected name")
        n = self.ct.value
        self.advance()
        argList = self.parseArgList()
        stmtList = self.parseStatementList()
        GlobalScope.addFunction(n,t,argList)
        return FunctionDecl(t,n,argList,stmtList)

    def parseArgList(self):
        self.match("LPAREN")
        args = []
        self.advance()
        while not self.match("RPAREN"):
            t = self.parseType()
            if not self.match("ID"):
                self.error("Expected name for argument")
            n = self.ct.value
            self.advance()

            args.append((n,t))
            if not self.match("COMMA"):
                break
            self.advance()
        self.match("RPAREN")
        self.advance()
        return ArgListAst(args)
    # Type = baseType [*]*
    # where baseType = int | short
    def parseType(self):
        print(self.ct.type)
        if self.ct.type == "INT":
            baseType = IntT
        elif self.ct.type == "VOID":
            baseType = VoidT
        elif self.ct.type == "SHORT":
            baseType = ShortT
        else:
            self.error("No suitable type given %s"%(self.ct.type))
            import sys
            sys.exit(1)
        self.advance()
        while self.match("MUL"):
            baseType = RefType(baseType)
            self.advance()
        return baseType
    def parseExpression(self):
        x = self.parseOrExpr()
        if self.match("ASSIGN"):
            self.advance()
            y = self.parseOrExpr()
            return AssignExpr(x,y)
        return x
    def genParseC(self,x,y,z):
        a = x()
        while any([self.match(t) for t in y]):
            op = self.ct.value
            self.advance()
            b = x()
            a = z(a,b,op)
        return a


    def parseOrExpr(self):
        return self.genParseC(self.parseAndExpr, ["BOR"], BinaryExpression)
    def parseAndExpr(self):
        return self.genParseC(self.parseEqualityExpression, ["BAND"], BinaryExpression)
    def parseEqualityExpression(self):
        return self.genParseC(self.parseRelationalExpression, ["EQEQ"], BinaryExpression)
    def parseRelationalExpression(self):
        return self.genParseC(self.parseAddExpr, ["LT","LTE","GTE","GT"], BinaryExpression)
    def parseAddExpr(self):
        return self.genParseC(self.parseMulExpr,["PLUS","MINUS"],BinaryExpression)
    def parseMulExpr(self):
        return self.genParseC(self.parseUnaryExpr, ["MUL", "DIV"], BinaryExpression)
    def parseUnaryExpr(self):
        if self.match("MINUS"):
            self.advance()
            y = self.parsePostFixExpr()
            return UnaryMinus(y)
        if self.match("ADRESSOF"):
            self.advance()
            y = self.parsePostFixExpr()
            return AdressOf(y)
        if self.match("MUL"):
            self.advance()
            y = self.parsePostFixExpr()
            return Indirect(y)
        return self.parsePostFixExpr()

    def parsePostFixExpr(self):
        x = self.parsePrimaryExpression()
        while self.match("LBRACK"):
            print("hi")
            self.advance()
            y = self.parseExpression()
            self.expect("RBRACK")
            x = ArrayAccess(x,y)
        return x


    def parsePrimaryExpression(self):
        if self.match("INTC"):
            y = self.ct.value
            self.advance()
            return ConstantAst(y)
        if self.match("ID"):
            n = self.ct.value
            self.advance()
            if self.match("LPAREN"):
                self.expect("LPAREN")
                l = []
                while not self.match("RPAREN"):
                    l.append(self.parseExpression())
                    if self.match("COMMA"):
                        self.advance()
                self.expect("RPAREN")
                return FuncCallAst(n,l)
            else:
                return VariableAst(n)
        if self.match("LPAREN"):
            self.advance()
            y = self.parseExpression()
            if not self.match("RPAREN"):
                self.error("Expected RPAREN")
            self.advance()
            return y

    def parseStatementList(self):
        self.expect("LBRACE")
        stmt = []
        while not self.match("RBRACE"):
            stmt.append(self.parseStatement())
            if self.match("SEMICOLON"):
                self.advance()
        self.expect("RBRACE")
        return StatementList(stmt)


    def parseStatement(self):
        if self.match("IF"):
            self.advance()
            self.expect("LPAREN")
            y = self.parseExpression()
            self.expect("RPAREN")
            z = self.parseStatement()
            elseB = None
            if self.match("ELSE"):
                self.advance()
                elseB = self.parseStatement()
            return IfStatement(y,z,elseB)
        elif self.match("FOR"):
            self.advance()
            self.expect("LPAREN")
            a = self.parseStatement()
            self.expect("SEMICOLON")
            b = self.parseStatement()
            self.expect("SEMICOLON")
            c = self.parseStatement()
            self.expect("RPAREN")
            t = self.parseStatement()
            return ForLoop(a,b,c,t)
        elif self.match("WHILE"):
            self.advance()
            self.expect("LPAREN")
            y = self.parseExpression()
            self.expect("RPAREN")
            z = self.parseStatement()
            return WhileLoop(y,z)
        elif self.match("RETURN"):
            self.advance()
            z = self.parseExpression()
            return ReturnStatement(z)
        elif self.match("INT") or self.match("SHORT"):
            type = self.parseType()
            if not self.match("ID"):
                self.error("Expected ID")
            n = self.ct.value
            self.advance()
            t = None
            if self.match("ASSIGN"):
                self.expect("ASSIGN")
                t = self.parseExpression()
            return VariableDecl(n,type, t)
        elif self.match("LBRACE"):
            return self.parseStatementList()
        else:
            # Expression
            if self.match("SEMICOLON"):
                return Nop()
            return self.parseExpression()



f = open("test.c","r")
lexer.input(f.read())
p = Parser(lexer)
y = p.parseProgram()
e = Emitter()

for x in y:
    x.pretty(0)
    x.typecheck(Scope(GlobalScope))
for x in y:
    print("***************")
    e = Emitter()
    x.emit(e)
    e.print()
    print("Codegen")
    e.generateMips()
f.close()