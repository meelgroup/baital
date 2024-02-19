# Generated from bool.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,8,72,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,
        1,0,1,0,1,0,1,0,1,0,1,0,1,0,3,0,22,8,0,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,3,1,32,8,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,2,41,8,2,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,3,3,51,8,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        4,3,4,61,8,4,1,5,1,5,1,5,1,5,1,5,3,5,68,8,5,1,6,1,6,1,6,0,0,7,0,
        2,4,6,8,10,12,0,0,70,0,21,1,0,0,0,2,31,1,0,0,0,4,40,1,0,0,0,6,50,
        1,0,0,0,8,60,1,0,0,0,10,67,1,0,0,0,12,69,1,0,0,0,14,15,5,7,0,0,15,
        22,6,0,-1,0,16,17,5,1,0,0,17,18,3,10,5,0,18,19,5,2,0,0,19,20,6,0,
        -1,0,20,22,1,0,0,0,21,14,1,0,0,0,21,16,1,0,0,0,22,1,1,0,0,0,23,24,
        3,0,0,0,24,25,6,1,-1,0,25,32,1,0,0,0,26,27,3,0,0,0,27,28,5,6,0,0,
        28,29,3,0,0,0,29,30,6,1,-1,0,30,32,1,0,0,0,31,23,1,0,0,0,31,26,1,
        0,0,0,32,3,1,0,0,0,33,34,3,2,1,0,34,35,6,2,-1,0,35,41,1,0,0,0,36,
        37,5,3,0,0,37,38,3,2,1,0,38,39,6,2,-1,0,39,41,1,0,0,0,40,33,1,0,
        0,0,40,36,1,0,0,0,41,5,1,0,0,0,42,43,3,4,2,0,43,44,6,3,-1,0,44,51,
        1,0,0,0,45,46,3,4,2,0,46,47,5,5,0,0,47,48,3,6,3,0,48,49,6,3,-1,0,
        49,51,1,0,0,0,50,42,1,0,0,0,50,45,1,0,0,0,51,7,1,0,0,0,52,53,3,6,
        3,0,53,54,6,4,-1,0,54,61,1,0,0,0,55,56,3,6,3,0,56,57,5,4,0,0,57,
        58,3,8,4,0,58,59,6,4,-1,0,59,61,1,0,0,0,60,52,1,0,0,0,60,55,1,0,
        0,0,61,9,1,0,0,0,62,68,3,8,4,0,63,64,5,1,0,0,64,65,3,10,5,0,65,66,
        5,2,0,0,66,68,1,0,0,0,67,62,1,0,0,0,67,63,1,0,0,0,68,11,1,0,0,0,
        69,70,3,10,5,0,70,13,1,0,0,0,6,21,31,40,50,60,67
    ]

class boolParser ( Parser ):

    grammarFileName = "bool.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'", "'not'" ]

    symbolicNames = [ "<INVALID>", "LPAREN", "RPAREN", "NEGATION", "TOPOP", 
                      "MIDDLEOP", "COMP", "ID", "WS" ]

    RULE_ident = 0
    RULE_term = 1
    RULE_expr_inner3 = 2
    RULE_expr_inner2 = 3
    RULE_expr_inner = 4
    RULE_expr = 5
    RULE_formula = 6

    ruleNames =  [ "ident", "term", "expr_inner3", "expr_inner2", "expr_inner", 
                   "expr", "formula" ]

    EOF = Token.EOF
    LPAREN=1
    RPAREN=2
    NEGATION=3
    TOPOP=4
    MIDDLEOP=5
    COMP=6
    ID=7
    WS=8

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class IdentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.var = None # Token
            self.ex = None # ExprContext

        def ID(self):
            return self.getToken(boolParser.ID, 0)

        def LPAREN(self):
            return self.getToken(boolParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(boolParser.RPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(boolParser.ExprContext,0)


        def getRuleIndex(self):
            return boolParser.RULE_ident

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdent" ):
                listener.enterIdent(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdent" ):
                listener.exitIdent(self)




    def ident(self):

        localctx = boolParser.IdentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_ident)
        try:
            self.state = 21
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [7]:
                self.enterOuterAlt(localctx, 1)
                self.state = 14
                localctx.var = self.match(boolParser.ID)

                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 16
                self.match(boolParser.LPAREN)
                self.state = 17
                localctx.ex = self.expr()
                self.state = 18
                self.match(boolParser.RPAREN)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TermContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.id_ = None # IdentContext
            self.id2 = None # IdentContext

        def ident(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(boolParser.IdentContext)
            else:
                return self.getTypedRuleContext(boolParser.IdentContext,i)


        def COMP(self):
            return self.getToken(boolParser.COMP, 0)

        def getRuleIndex(self):
            return boolParser.RULE_term

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTerm" ):
                listener.enterTerm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTerm" ):
                listener.exitTerm(self)




    def term(self):

        localctx = boolParser.TermContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_term)
        try:
            self.state = 31
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 23
                localctx.id_ = self.ident()

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 26
                localctx.id_ = self.ident()
                self.state = 27
                self.match(boolParser.COMP)
                self.state = 28
                localctx.id2 = self.ident()

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Expr_inner3Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.t = None # TermContext

        def term(self):
            return self.getTypedRuleContext(boolParser.TermContext,0)


        def NEGATION(self):
            return self.getToken(boolParser.NEGATION, 0)

        def getRuleIndex(self):
            return boolParser.RULE_expr_inner3

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr_inner3" ):
                listener.enterExpr_inner3(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr_inner3" ):
                listener.exitExpr_inner3(self)




    def expr_inner3(self):

        localctx = boolParser.Expr_inner3Context(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_expr_inner3)
        try:
            self.state = 40
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1, 7]:
                self.enterOuterAlt(localctx, 1)
                self.state = 33
                localctx.t = self.term()

                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 36
                self.match(boolParser.NEGATION)
                self.state = 37
                localctx.t = self.term()

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Expr_inner2Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.e = None # Expr_inner3Context
            self.e1 = None # Expr_inner3Context
            self.e2 = None # Expr_inner2Context

        def expr_inner3(self):
            return self.getTypedRuleContext(boolParser.Expr_inner3Context,0)


        def MIDDLEOP(self):
            return self.getToken(boolParser.MIDDLEOP, 0)

        def expr_inner2(self):
            return self.getTypedRuleContext(boolParser.Expr_inner2Context,0)


        def getRuleIndex(self):
            return boolParser.RULE_expr_inner2

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr_inner2" ):
                listener.enterExpr_inner2(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr_inner2" ):
                listener.exitExpr_inner2(self)




    def expr_inner2(self):

        localctx = boolParser.Expr_inner2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_expr_inner2)
        try:
            self.state = 50
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 42
                localctx.e = self.expr_inner3()

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 45
                localctx.e1 = self.expr_inner3()
                self.state = 46
                self.match(boolParser.MIDDLEOP)
                self.state = 47
                localctx.e2 = self.expr_inner2()

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Expr_innerContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.e = None # Expr_inner2Context
            self.e1 = None # Expr_inner2Context
            self.top = None # Token
            self.e2 = None # Expr_innerContext

        def expr_inner2(self):
            return self.getTypedRuleContext(boolParser.Expr_inner2Context,0)


        def TOPOP(self):
            return self.getToken(boolParser.TOPOP, 0)

        def expr_inner(self):
            return self.getTypedRuleContext(boolParser.Expr_innerContext,0)


        def getRuleIndex(self):
            return boolParser.RULE_expr_inner

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr_inner" ):
                listener.enterExpr_inner(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr_inner" ):
                listener.exitExpr_inner(self)




    def expr_inner(self):

        localctx = boolParser.Expr_innerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_expr_inner)
        try:
            self.state = 60
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 52
                localctx.e = self.expr_inner2()

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 55
                localctx.e1 = self.expr_inner2()
                self.state = 56
                localctx.top = self.match(boolParser.TOPOP)
                self.state = 57
                localctx.e2 = self.expr_inner()

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.ei = None # Expr_innerContext
            self.e = None # ExprContext

        def expr_inner(self):
            return self.getTypedRuleContext(boolParser.Expr_innerContext,0)


        def LPAREN(self):
            return self.getToken(boolParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(boolParser.RPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(boolParser.ExprContext,0)


        def getRuleIndex(self):
            return boolParser.RULE_expr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr" ):
                listener.enterExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr" ):
                listener.exitExpr(self)




    def expr(self):

        localctx = boolParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_expr)
        try:
            self.state = 67
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 62
                localctx.ei = self.expr_inner()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 63
                self.match(boolParser.LPAREN)
                self.state = 64
                localctx.e = self.expr()
                self.state = 65
                self.match(boolParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FormulaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self):
            return self.getTypedRuleContext(boolParser.ExprContext,0)


        def getRuleIndex(self):
            return boolParser.RULE_formula

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFormula" ):
                listener.enterFormula(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFormula" ):
                listener.exitFormula(self)




    def formula(self):

        localctx = boolParser.FormulaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_formula)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            self.expr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





