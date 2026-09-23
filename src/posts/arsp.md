---
title: building a list programming language
date: sept. 23, 2026
---

## crafting a lexer

\[1\] the first step to programming a programming language is lexer creating a lexer, it's to synthesize a grammar or a test file that doesn't contradict itself. in this project, i named my programming language arsp for (*ar*ray *p*rogramming language). for the test file, i went with something a little beyond trivial like this:
```
(let fact)
(set fact ; bind existing to function
    (func (lst x) 
        (ifelse (lt x 1)
            x
            (mul x (fact x))
        )
    )
)

(fact 5)
"this is a completely unrelated string"
```
it does make use of an edge-case i think will appear later: if a function calls to itself, does it call the identifier that it's set to at the beginning? the answer i landed on is no, if an identifier shows up at the start of an application (list) inside a function definition, do not evaluate it.

\[2\] the next step is creating the lexer, we have to recognize some important lexemes that not only contain symbols and delimiters but i think macros are really important (except double-quotes because a string should be considered as one token inside the lexer rather than a chain of potential function names and identifiers enclosed by quote tokens to get parsed inside a parser)

```py
from enum import Enum, auto

class TokenType(Enum):
    # essence
    LPAREN = auto()
    RPAREN = auto()
    IDENT = auto()
    
    # types
    T_STRING = auto()
    T_NUMBER = auto()
    T_BOOL = auto()
    T_LST = auto()
    T_NIL = auto()
    
    # keywords
    KW_FUNC = auto()
    KW_IF = auto()
    KW_IFELSE = auto()
    KW_LET = auto()
    
    # operator
    OP_SET = auto()
    OP_INCR = auto()
    OP_DECR = auto()
    
    OP_PLUS = auto()
    OP_MINUS = auto()
    OP_MUL = auto()
    OP_DIV = auto()
    
    OP_LT = auto()
    OP_GT = auto()
    OP_LE = auto()
    OP_GE = auto()
    
    OP_OR = auto()
    OP_AND = auto()
    OP_NOT = auto()
    
    # not a token
    NAT = auto()

class Token():
    def __init__(self, ttype:TokenType, lexeme:str=""):
        self.ttype = ttype
        self.lexeme = lexeme
```

```py
from tokens import Token, TokenType
import re

KWOP = {
    "func": TokenType.KW_FUNC,
    "if": TokenType.KW_IF,
    "ifelse": TokenType.KW_IFELSE,
    "let": TokenType.KW_LET,
    
    "set": TokenType.OP_SET,
    "incr": TokenType.OP_INCR,
    "decr": TokenType.OP_DECR,
    
    "pls": TokenType.OP_PLUS,
    "mns": TokenType.OP_MINUS,
    "mul": TokenType.OP_MUL,
    "div": TokenType.OP_DIV,
    
    "lt": TokenType.OP_LT,
    "gt": TokenType.OP_GT,
    "le": TokenType.OP_LE,
    "ge": TokenType.OP_GE,
    
    "or": TokenType.OP_OR,
    "and": TokenType.OP_AND,
    "not": TokenType.OP_NOT,
    
    "true": TokenType.T_BOOL,
    "false": TokenType.T_BOOL, # literals
    "lst": TokenType.T_LST, # macro denoting atom
    "nil": TokenType.T_NIL # literal
}

class Lexer():
    def __init__(self, source:str):
        self.source = source
        self.tokens:list[Token] = []
        
    def _add_token(self, ttype, lexeme):
        self.tokens.append(Token(
            ttype, lexeme
        ))
        
    def _process_lexemes(self, lexemes):
        for lexeme in lexemes:
            if lexeme == "(": self._add_token(TokenType.LPAREN, lexeme)
            elif lexeme == ")": self._add_token(TokenType.RPAREN, lexeme)
            elif (KWOPtype := KWOP.get(lexeme, None)):
                self._add_token(KWOPtype, lexeme)
            elif lexeme[0] == ';': continue
            elif lexeme[0] == '"' and lexeme[-1] == '"':
                self._add_token(TokenType.T_STRING, lexeme)
            elif lexeme.isdigit():
                self._add_token(TokenType.T_NUMBER, lexeme)
            else:
                self._add_token(TokenType.IDENT, lexeme)
    
    def lex(self):
        pattern = re.compile(r'''
        (
            "(?:\\.|[^"\\])*"            # Strings
          | ;[^\n]*                      # Comments
          | [-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?  # Numbers
          | [()]                         # Parentheses
          | [^\s()"';]+                  # Symbols
        )
        ''', re.VERBOSE)
        lexemes = pattern.findall(self.source)
        self._process_lexemes(lexemes)
```

\[3\] the decisions i made here are important:
- parentheses delimiters are considered tokens because there are no tokens for function names and multiple tokens for macros. instead, functions should be recognized in the parser and function names are identifier tokens
- strings being delimited by quotes which are not tokens for reasons i already discussed
- lists that are shouldn't applications but actual lists are actually conveniently made by having it created as an application of "list constructor" with its operands as items. for example: `(lst 1 2 3 4 5)`

by the way shoutout to some random article for giving me the regex for splitting tokens in source for the lexer. this includes numeric atoms with sign (but `+` sign might be questionable), actual parentheses tokens with regarding quotes as part of string tokens (that i've talked before) and comments (i never knew lisp had comments prior to this by the way)

\[4\] with `simple.arsp` (the name of the demo program), the lexer should spit out this with `main.py`:
```py
from tokens import Token, TokenType
from lexer import Lexer
from parser import Parser

if __name__ == "__main__":
    with open("simple.arsp", "r", encoding="utf-8") as f:
        lexer = Lexer(f.read())
        lexer.lex()
        for token in lexer.tokens:
            print(token.ttype, token.lexeme)
```

```
PS C:\Users\█████████████████\Documents\projects-that-i-made\arsp> python main.py
TokenType.LPAREN (
TokenType.KW_LET let
TokenType.IDENT fact
TokenType.RPAREN )
TokenType.LPAREN (
TokenType.OP_SET set
TokenType.IDENT fact
TokenType.LPAREN (
TokenType.KW_FUNC func
TokenType.LPAREN (
TokenType.T_LST lst
TokenType.IDENT x
TokenType.RPAREN )
TokenType.LPAREN (
TokenType.KW_IFELSE ifelse
TokenType.LPAREN (
TokenType.OP_LT lt
TokenType.IDENT x
TokenType.T_NUMBER 1
TokenType.RPAREN )
TokenType.IDENT x
TokenType.LPAREN (
TokenType.OP_MUL mul
TokenType.IDENT x
TokenType.LPAREN (
TokenType.IDENT fact
TokenType.IDENT x
TokenType.RPAREN )
TokenType.RPAREN )
TokenType.RPAREN )
TokenType.RPAREN )
TokenType.RPAREN )
TokenType.LPAREN (
TokenType.IDENT fact
TokenType.T_NUMBER 5
TokenType.RPAREN )
TokenType.T_STRING "this is a completely unrelated string"
```