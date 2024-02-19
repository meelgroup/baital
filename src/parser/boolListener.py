# Generated from bool.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .boolParser import boolParser
else:
    from boolParser import boolParser

# This class defines a complete listener for a parse tree produced by boolParser.
class boolListener(ParseTreeListener):

    # Enter a parse tree produced by boolParser#ident.
    def enterIdent(self, ctx:boolParser.IdentContext):
        pass

    # Exit a parse tree produced by boolParser#ident.
    def exitIdent(self, ctx:boolParser.IdentContext):
        pass


    # Enter a parse tree produced by boolParser#term.
    def enterTerm(self, ctx:boolParser.TermContext):
        pass

    # Exit a parse tree produced by boolParser#term.
    def exitTerm(self, ctx:boolParser.TermContext):
        pass


    # Enter a parse tree produced by boolParser#expr_inner3.
    def enterExpr_inner3(self, ctx:boolParser.Expr_inner3Context):
        pass

    # Exit a parse tree produced by boolParser#expr_inner3.
    def exitExpr_inner3(self, ctx:boolParser.Expr_inner3Context):
        pass


    # Enter a parse tree produced by boolParser#expr_inner2.
    def enterExpr_inner2(self, ctx:boolParser.Expr_inner2Context):
        pass

    # Exit a parse tree produced by boolParser#expr_inner2.
    def exitExpr_inner2(self, ctx:boolParser.Expr_inner2Context):
        pass


    # Enter a parse tree produced by boolParser#expr_inner.
    def enterExpr_inner(self, ctx:boolParser.Expr_innerContext):
        pass

    # Exit a parse tree produced by boolParser#expr_inner.
    def exitExpr_inner(self, ctx:boolParser.Expr_innerContext):
        pass


    # Enter a parse tree produced by boolParser#expr.
    def enterExpr(self, ctx:boolParser.ExprContext):
        pass

    # Exit a parse tree produced by boolParser#expr.
    def exitExpr(self, ctx:boolParser.ExprContext):
        pass


    # Enter a parse tree produced by boolParser#formula.
    def enterFormula(self, ctx:boolParser.FormulaContext):
        pass

    # Exit a parse tree produced by boolParser#formula.
    def exitFormula(self, ctx:boolParser.FormulaContext):
        pass



del boolParser