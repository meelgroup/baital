from antlr4 import *
from .boolLexer import boolLexer
from .boolParser import boolParser
import math
import re

#antlr boolean parsing
def visitIdent(ctx:boolParser.IdentContext, vars2bv, valuedvars2int):
    if ctx.getChildCount() == 3:
        return visitExpr(ctx.getChild(1), vars2bv, valuedvars2int)
    else:
        var = ctx.getText()
        if (var.isnumeric()):
            return int(var)
        else:
            return var

def visitTerm(ctx:boolParser.TermContext, vars2bv, valuedvars2int):
    if ctx.getChildCount() == 3:
        op = ctx.getChild(1).getText()
        v1 = visitIdent(ctx.getChild(0), vars2bv, valuedvars2int)
        v2 = visitIdent(ctx.getChild(2), vars2bv, valuedvars2int)
        if not v1 in vars2bv:
            print("unknown variable " + str(v1))
            exit(1)
        size = vars2bv[v1][0]
        if not isinstance(v2, int):
            print("expected integer but given " + str(v2))
            exit(1)
        val = valuedvars2int[v1][v2] if v1 in valuedvars2int else v2 # if int values have been converted to [0..n] - use dict to get value of v2
        match op:
            case '=' : qfbvOp = '='
            case '>' : qfbvOp ='bvugt'
            case '>=' : qfbvOp ='bvuge'
            case '<' : qfbvOp ='bvult'
            case '<=' : qfbvOp ='bvule'
            case '_' : 
                print("unknown operator " + str(op))
                exit(1)
        return "(" + qfbvOp +" " + v1 + " (_ bv" + str(val)+ " " + str(size) +"))"
    else:
        return visitIdent(ctx.getChild(0), vars2bv, valuedvars2int)

def visitInner3(ctx:boolParser.Expr_inner3Context, vars2bv, valuedvars2int):
    if ctx.getChildCount() == 2:
        v1= visitTerm(ctx.getChild(1), vars2bv, valuedvars2int)
        return "(not " + v1 + ")"
    else:
        return visitTerm(ctx.getChild(0), vars2bv, valuedvars2int)

def visitInner2(ctx:boolParser.Expr_inner2Context, vars2bv, valuedvars2int):
    if ctx.getChildCount() == 3:
        v1= visitInner3(ctx.getChild(0), vars2bv, valuedvars2int)
        v2 = visitInner2(ctx.getChild(2), vars2bv, valuedvars2int)
        return "(or (not " + v1 + ") " + v2 + ")" 
    else:
        return visitInner3(ctx.getChild(0), vars2bv, valuedvars2int)

def visitInner(ctx:boolParser.Expr_innerContext, vars2bv, valuedvars2int):
    if ctx.getChildCount() == 3:
        v1= visitInner2(ctx.getChild(0), vars2bv, valuedvars2int)
        v2 = visitInner(ctx.getChild(2), vars2bv, valuedvars2int)
        op = "or" if (ctx.getChild(1).getText() == "||")  else "and" 
        return "(" + op + " " + v1 + " " + v2 + ")" 
    else:
        return visitInner2(ctx.getChild(0), vars2bv, valuedvars2int)

def visitExpr(ctx:boolParser.ExprContext, vars2bv, valuedvars2int):
    if ctx.getChildCount() == 3:
        return visitExpr(ctx.getChild(1), vars2bv, valuedvars2int)
    else:
        return visitInner(ctx.getChild(0), vars2bv, valuedvars2int)

def visitFormula(ctx:boolParser.FormulaContext, vars2bv, valuedvars2int):
    return visitExpr(ctx.getChild(0), vars2bv, valuedvars2int)
    
def antlrParse(line, vars2bv, valuedvars2int):
    inputStream = InputStream(line);
    lexer = boolLexer(inputStream)
    stream = CommonTokenStream(lexer)
    parser = boolParser(stream)
    tree = parser.formula()
    return visitFormula(tree, vars2bv, valuedvars2int)

def unsupported(line, extra_message=''):
    print("Parsing unimplemented for line " + line)
    if extra_message:
        print(extra_message)
    exit(1)

#Parsing of the first part of the file (until Cp : line)
def parseVars(lines):
    clauses = []
    curline = 1
    beforeCp = True
    vars2bv = {lines[0].strip().split(' ')[-1] :[1,0,2]} # variable:[nBits,minvalue,maxvalue]
    intvars = {}                                         # variable:[minvalue,maxvalue] for int variables, where boundaries are defined in the following constraints
    valuedvars2int = {} # varaible: {value:int} : int from 0 to n-1
    valuedvarsfromint = {} # varaible: {int:value} - for 'or' constraints [varname = 128 || varname = 256 || varname = 512] values are converted to 0,1,2...; this disctionary stores original values  
    clausesparts = {}
    clauses4antlr =[]
    try:
        while (curline < len(lines)) and beforeCp:
            line = lines[curline].strip()
            if line == '' or line.startswith("//"): # empty or comment line
                curline +=1
            elif line.startswith("Cp :"): # constraints line
                beforeCp = False
                curline +=1
            elif not line.startswith('['):
                els = line.split(' ')
                if (len(els) == 1) and (not line.startswith('[')):    # simple variable - bool
                    vars2bv.update({line :[1,0,2]})
                    curline +=1
                elif (len(els) == 2) and (els[0] == 'xor'):           # xored children
                    vars2bv.update({els[1] :[1,0,2]})
                    tablevel = len(lines[curline]) - len(lines[curline].lstrip())
                    curline +=1
                    insidexor = True
                    xoredVars = []
                    while (curline < len(lines)) and insidexor:
                        tablevelnew = len(lines[curline]) - len(lines[curline].lstrip())
                        if tablevelnew <= tablevel:
                            insidexor = False
                        else:
                            varname = lines[curline].strip() 
                            vars2bv.update({varname :[1,0,2]})
                            xoredVars.append(varname)
                            curline +=1
                    makeorstr = lambda x :  str(x[0]) if len(x) ==1 else '(or ' + str(x[0]) + ' ' + makeorstr(x[1:]) + ')'
                    clauses.append('(= ' + els[1] + ' ' + makeorstr(xoredVars) +')')
                    for i in range(len(xoredVars)):
                        for j in range(i+1, len(xoredVars)):
                            clauses.append('(or (not ' + str(xoredVars[i]) + ') (not ' + xoredVars[j] +'))')
                elif (len(els) ==3) and els[1] == '->' and els[2] == 'integer':
                    intvars.update({els[0]:[-1,-1]})               # curmin and curmax to be found in further constraints
                    curline +=1
                else:
                    unsupported(lines[curline])
            else:
                els = line.strip("[]").split(' ')
                if len(els) ==1:                #case    varname -> integer \n [varname] - skip
                    curline +=1
                elif len(els)==5:           #case  [var1 + var2 >0]
                    match els[3]:
                        case '>': op1 = 'bvugt'
                        case '>=': op1 = 'bvuge'
                        case '<': op1 = 'bvult'
                        case '<=': op1 = 'bvule'
                        case '=': op1 = '='
                        case '_': unsupported(lines[curline])
                    if els[0] not in intvars: 
                        unsupported(lines[curline], extra_message="Undefined variable " + els[0])
                    if els[2] not in intvars:
                        unsupported(lines[curline], extra_message="Undefined variable " + els[2])
                    match els[1]:
                        case '+': 
                            if els[0] not in clausesparts:
                                clausesparts[els[0]] = []
                            clausesparts[els[0]].append('('+op1 +' (bvadd ' + els[0] + ' ' + els[2] + ') (_ bv' + els[4] + ' ') # TODO check/add condition for same length for els[0] and els[2] 
                        case _: unsupported(lines[curline])
                    curline +=1
                elif len(els)==3:           # case [varname < 100]
                    if els[0] not in intvars:
                        unsupported(lines[curline], extra_message="Undefined variable " + els[0])
                    match els[1]:
                        case '>=' : intvars[els[0]][0] = int(els[2])
                        case '>' : intvars[els[0]][0] = int(els[2]) + 1
                        case '<' : intvars[els[0]][1] = int(els[2])
                        case '<=' : intvars[els[0]][1] = int(els[2]) + 1
                    curline +=1
                elif '||' in els:           # case [varname = 128 || varname = 256 || varname = 512]
                    if '>=' in els or '>' in els or '<=' in els or '<' in els:
                        clauses4antlr.append(line.strip("[]")) # case of complex constraints - add for antlr
                    else:
                        vals =[]
                        curp = 0
                        curvar = els[0]
                        valuedvars2int.update({curvar:{}})
                        valuedvarsfromint.update({curvar:{}})
                        curintval=0
                        while curp < len(els):
                            if (els[curp] != curvar) or (els[curp+1] != "=") or ((curp+3 < len(els)) and (els[curp+3] != '||')):
                                unsupported(lines[curline])
                            valuedvarsfromint[curvar].update({curintval:int(els[curp+2])})
                            valuedvars2int[curvar].update({int(els[curp+2]):curintval})
                            curp += 4
                            curintval += 1
                    curline +=1
                else:
                    unsupported(lines[curline], extra_message="Undefined variable " + els[2])
                
        for varname in intvars:   # collect boundaries for integer variables
            if varname in valuedvarsfromint:
                vmax = max(valuedvarsfromint[varname].keys()) +1
                vars2bv.update({varname:[math.ceil(math.log2(vmax)), 0, vmax]})
            elif intvars[varname][0] != -1 or intvars[varname][1] != -1:
                vmax = intvars[varname][1]
                vmin = max(0,intvars[varname][0])
                vars2bv.update({varname:[math.ceil(math.log2(vmax-vmin)), vmin, vmax]})
            else:
                unsupported(lines[curline], extra_message="No constraints for "+ varname )
        for varname in clausesparts:
            for parts in clausesparts[varname]:
                print(vars2bv[varname])
                clauses.append(parts + str(vars2bv[varname][0]) + ' ))')
        for clause in clauses4antlr:
            clauses.append(antlrParse(clause, vars2bv, valuedvars2int))
    except Exception as ex:
        print(ex)
        unsupported(lines[curline])
    return curline,clauses, vars2bv, valuedvars2int,valuedvarsfromint

# Write variables and clauses to qf_bv file for MaxCov algo (currently assumes all variables have names v_<integer>)
def writeQFBVFileForMaxCov(outfile, vars2bv, orderedVars, clauses):
    with open(outfile, 'w+') as fo:
        fo.write(';; ' + ' '.join([var + '='+str(vars2bv[var][2]-vars2bv[var][1]) for var in orderedVars]) + '\n')
        fo.write('(set-logic QF_BV)\n')
        maxcov_names = {v : 'v_'+str(k) for (k,v) in enumerate(orderedVars)}
        replace_keys = (re.escape(k) for k in maxcov_names.keys())
        pattern = re.compile(r'\b(' + '|'.join(replace_keys) + r')\b')
        for var in orderedVars:
            if (vars2bv[var][0] == 1) :
                fo.write('(declare-fun ' + maxcov_names[var] +' () Bool)\n')
            else: 
                fo.write('(declare-fun ' + maxcov_names[var] +' () (_ BitVec '+ str(vars2bv[var][0]) +'))\n')
                if (vars2bv[var][2] - vars2bv[var][1]) != 2**vars2bv[var][0]:
                    fo.write('(assert (and (bvuge ' + maxcov_names[var] + ' (_ bv' + str(vars2bv[var][1]) + " " +  str(vars2bv[var][0]) +')) (bvult ' + maxcov_names[var]+ ' (_ bv' + str(vars2bv[var][2]) + " " +  str(vars2bv[var][0]) +'))))\n')
        for cl in clauses:
            fo.write('(assert '+ pattern.sub(lambda x: maxcov_names[x.group()], cl) +')\n')

# Write variables and clauses to qf_bv file
def writeQFBVFile(outfile, vars2bv, orderedVars, valuedvarsfromint, clauses):
    with open(outfile, 'w+') as fo:
        fo.write(';; ' + ' '.join([var + '=' + str(vars2bv[var][2]-vars2bv[var][1]) for var in orderedVars]) + '\n')
        fo.write(';; ' + ' '.join([var + '=' + str(vars2bv[var][1]) for var in orderedVars if vars2bv[var][0]>1 and vars2bv[var][1] != 0 and (not (var in valuedvarsfromint))])+ '\n')
        fo.write(';; ' + ' '.join([var + '=[' + ','.join([str(i)+':'+str(valuedvarsfromint[var][i]) for i in valuedvarsfromint[var]]) + ']' for var in valuedvarsfromint])+ '\n')
        fo.write('(set-logic QF_BV)\n')
        extravars = [] #additional variables for each bit of integer variable - for name recovery
        for var in orderedVars:
            if (vars2bv[var][0] == 1) :
                fo.write('(declare-fun ' + var +' () Bool)\n')
            else: 
                fo.write('(declare-fun ' + var +' () (_ BitVec '+ str(vars2bv[var][0]) +'))\n')
                if (vars2bv[var][2] - vars2bv[var][1]) != 2**vars2bv[var][0]:
                    fo.write('(assert (and (bvuge ' + var+ ' (_ bv' + str(vars2bv[var][1]) + " " +  str(vars2bv[var][0]) +')) (bvult ' + var+ ' (_ bv' + str(vars2bv[var][2]) + " " +  str(vars2bv[var][0]) +'))))\n')
                for j in range(vars2bv[var][0]):
                    fo.write('(declare-fun ' + var + '_' + str(j) +' () (_ Bool))\n')
                extravars.append(var)
        for cl in clauses:
            fo.write('(assert '+ cl +')\n')
        for var in extravars:
            for j in range(vars2bv[var][0]):
                mask = '(_ bv' + str(int(math.pow(2,j))) +' '+ str(vars2bv[var][0]) +')'
                fo.write('(assert (= ' + var + '_' + str(j) +' (= (bvand ' + var + ' ' + mask + '  ) ' + mask + ')))\n')
        
#Convert file to qf_bv
def convert(inputfile, outfile):
    with open(inputfile) as f:
        lines = f.readlines()    
    curline,clauses, vars2bv, valuedvars2int,valuedvarsfromint = parseVars(lines)
    while(curline < len(lines)):
        line = lines[curline].strip()
        if line == '' or line.startswith("//"):
            curline +=1
        else:
            line = line[1:len(line)-1]
            convertedClause = antlrParse(line, vars2bv, valuedvars2int)
            if not (len(convertedClause.split(' '))==1 and convertedClause in vars2bv and vars2bv[convertedClause][0]!=1):
                # current assumption that integer variables are always present  - i.e. ignore clauses [int_var]
                clauses.append(convertedClause)
            curline +=1
    orderedVars = list(vars2bv.keys())
    writeQFBVFile(outfile, vars2bv, orderedVars, valuedvarsfromint, clauses)
    return vars2bv,orderedVars,valuedvarsfromint
