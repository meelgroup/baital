# Generated from bool.g4 by ANTLR 4.13.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,8,55,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,2,7,7,7,1,0,1,0,1,1,1,1,1,2,1,2,1,2,1,2,1,3,1,3,1,3,1,3,3,
        3,30,8,3,1,4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,3,5,40,8,5,1,6,1,6,5,6,
        44,8,6,10,6,12,6,47,9,6,1,7,4,7,50,8,7,11,7,12,7,51,1,7,1,7,0,0,
        8,1,1,3,2,5,3,7,4,9,5,11,6,13,7,15,8,1,0,2,5,0,46,46,48,57,65,90,
        95,95,97,122,3,0,9,10,13,13,32,32,59,0,1,1,0,0,0,0,3,1,0,0,0,0,5,
        1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,0,13,1,0,0,0,0,15,1,
        0,0,0,1,17,1,0,0,0,3,19,1,0,0,0,5,21,1,0,0,0,7,29,1,0,0,0,9,31,1,
        0,0,0,11,39,1,0,0,0,13,41,1,0,0,0,15,49,1,0,0,0,17,18,5,40,0,0,18,
        2,1,0,0,0,19,20,5,41,0,0,20,4,1,0,0,0,21,22,5,110,0,0,22,23,5,111,
        0,0,23,24,5,116,0,0,24,6,1,0,0,0,25,26,5,124,0,0,26,30,5,124,0,0,
        27,28,5,38,0,0,28,30,5,38,0,0,29,25,1,0,0,0,29,27,1,0,0,0,30,8,1,
        0,0,0,31,32,5,61,0,0,32,33,5,62,0,0,33,10,1,0,0,0,34,40,2,60,62,
        0,35,36,5,60,0,0,36,40,5,61,0,0,37,38,5,62,0,0,38,40,5,61,0,0,39,
        34,1,0,0,0,39,35,1,0,0,0,39,37,1,0,0,0,40,12,1,0,0,0,41,45,7,0,0,
        0,42,44,7,0,0,0,43,42,1,0,0,0,44,47,1,0,0,0,45,43,1,0,0,0,45,46,
        1,0,0,0,46,14,1,0,0,0,47,45,1,0,0,0,48,50,7,1,0,0,49,48,1,0,0,0,
        50,51,1,0,0,0,51,49,1,0,0,0,51,52,1,0,0,0,52,53,1,0,0,0,53,54,6,
        7,0,0,54,16,1,0,0,0,5,0,29,39,45,51,1,6,0,0
    ]

class boolLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    LPAREN = 1
    RPAREN = 2
    NEGATION = 3
    TOPOP = 4
    MIDDLEOP = 5
    COMP = 6
    ID = 7
    WS = 8

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'('", "')'", "'not'" ]

    symbolicNames = [ "<INVALID>",
            "LPAREN", "RPAREN", "NEGATION", "TOPOP", "MIDDLEOP", "COMP", 
            "ID", "WS" ]

    ruleNames = [ "LPAREN", "RPAREN", "NEGATION", "TOPOP", "MIDDLEOP", "COMP", 
                  "ID", "WS" ]

    grammarFileName = "bool.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


