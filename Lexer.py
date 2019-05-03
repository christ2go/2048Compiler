from ply import *
tokens = (
    'INTC',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'PLUS',
    'MINUS',
    'MUL',
    'DIV',
    'LT',
    'LTE',
    'GTE',
    'GT',
    'BOR',
    'BAND',
    'ADRESSOF',
    'ASSIGN',
    'LBRACE',
    'RBRACE',
    'EQEQ',
    'WHILE',
    'IF',
    'ELSE',
    'FOR',
    'RETURN',
    'SHORT',
    'INT',
    'VOID',
    'COMMA',
    'SEMICOLON',
    'ID'
)
t_COMMA = r','
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'

t_LBRACK = r'\['
t_RBRACK = r'\]'
t_BOR   = r'\|\|'
t_BAND  = r'&&'

t_ADRESSOF = r'&'
t_PLUS   = r'\+'
t_ASSIGN = r'='
t_EQEQ = r'=='
t_MINUS  = r'-'
t_MUL    = r'\*'
t_DIV    = r'/'
t_LT     = r'<'
t_LTE    = r'<='
t_GT    = r'>'
t_GTE   = r'>='
def t_WHITESPACE(token):
  r'\s|\n'
  pass
t_VOID  = r'void'
t_WHILE = r'while'
t_IF    = r'if'
t_FOR   = r'for'
t_RETURN = r'return'
t_SHORT   = r'short'
t_INT  = r'int'
t_INTC = r'\d+'
keywords = ["short", "int", "for", "return", "void", "while", "if"]
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    if t.value in keywords:
        t.type = t.value.upper()
    return t

lexer = lex.lex(debug=0)
