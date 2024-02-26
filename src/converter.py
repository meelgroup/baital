import parser.convert2SMT
import os
import utils
import shutil

#vars2bv - dictionary: varname -> (number of bits, minimal value, maximal value +1)
#varsmap and varsretmap: varname <-> index in cnf. For non-binary varname is original varname + _  + bit index
#valuedvarsfromint: for integer variables defined with [v=5 || v=10 || v=20] stores varname -> {0:5, 1:10, 2:20}
# orderedVars: list with fixed order for vars2bv keys

#Generates QF_BV file for sampling from input file
def generateZ3file(inputfile, z3file):
    utils.rmfile(z3file)
    vars2bv,orderedVars,valuedvarsfromint = parser.convert2SMT.convert(inputfile,z3file)
    return vars2bv,orderedVars,valuedvarsfromint
    
#Runs z3 on z3file and converts output to DIMACS format
def convert2CNF(z3file, outputfile, vars2bv, nMaxcovVars=0):
    z3outfile = z3file + '.out'
    utils.rmfile(z3outfile)
    cmd =  'z3 ' + z3file + '> ' + z3outfile
    os.system(cmd)
    with open(z3outfile) as fo:
        lines = fo.readlines()
        lines = lines[2:-2]  
    i =0
    maxvar = 0
    cnffilelines = []
    varsmap = {}
    varsretmap = {}
    curvar = 1 + nMaxcovVars
    curMaxCovVar = 1
    nLines = len(lines)
    while i < nLines:
        line = lines[i].strip()
        lbracket = line.count('(')
        rbracket = line.count(')')
        while lbracket !=rbracket :
            line = line + lines[i+1]
            lbracket = line.count('(')
            rbracket = line.count(')')
            i+=1
        line = line.replace('(or', '')
        line = line.replace(',', '')
        line = line.replace(')', '')
        line = line.replace('(not ', '-')
        els = list(filter(None, line.split(' ')))
        elsConv = []
        for var in els:
            isneg = var.startswith('-')
            vr = var[1:].strip() if isneg else var.strip()
            if not vr in varsmap:
                if vr.startswith('maxcov_v_'):
                    varsmap.update({vr:curMaxCovVar})
                    varsretmap.update({str(curMaxCovVar):vr})
                    curMaxCovVar +=1
                else:
                    varsmap.update({vr:curvar})
                    varsretmap.update({str(curvar):vr})
                    curvar +=1
            elsConv.append(-varsmap[vr] if isneg else varsmap[vr])
        cnffilelines.append(' '.join([str(x) for x in elsConv])+' 0\n')
        i+=1
    for var in vars2bv:
        if var not in varsmap:
            varsmap.update({var:curvar})
            varsretmap.update({str(curvar):var})
            curvar +=1
    with open(outputfile, 'w+') as fi:  
        if nMaxcovVars>0:
            fi.write('c ind ' + ' '.join(map(str, range(1, nMaxcovVars+1))) + ' 0\n')
        fi.write('p cnf ' + str(curvar-1) + ' ' + str(len(cnffilelines)) + '\n')
        for line in cnffilelines:
            fi.write(line)
    utils.rmfile(z3outfile)
    return varsmap, varsretmap

def convert4Baital(z3file, outputfile, vars2bv):
    tmpfile = 'tmp.smt'
    shutil.copyfile(z3file, tmpfile)
    with open(tmpfile, 'a+') as f:
        f.write("(apply (then simplify (then bit-blast tseitin-cnf)))\n")
    varsmap, varsretmap = convert2CNF(tmpfile, outputfile, vars2bv)
    utils.rmfile(tmpfile)
    return varsmap, varsretmap

# Converts baital samples into samples with numerical features. 
def changeVarsBack(samplesfile, nsamples, rsamples, vars2bv, orderedVars, varsretmap, valuedvarsfromint):
    with open(samplesfile) as fo:
        lines = fo.readlines()
    newSamples = []
    newSamplesReadable = [] 
    for i in range(len(lines)):
        sample = [x.strip() for x in lines[i].strip().split(",")[1].split(' ')]
        parsed = {}
        newsample = []
        readable = []
        for var in sample:
            isneg = var.startswith('-')
            vr = var[1:].strip() if isneg else var.strip()
            origvar = varsretmap[vr]
            parsed.update({origvar:0 if isneg else 1})
        for var in orderedVars:
            if vars2bv[var][0] == 1:
                newsample.append(str(parsed[var]))
                readable.append(var+ '=' + str(parsed[var]))
            else:
                sm = 0
                for j in range(vars2bv[var][0]):
                    sm += parsed[var + '_' + str(j)] * (2**j)
                newsample.append(str(sm))
                if var in valuedvarsfromint:
                    readable.append(var+ '=' + str(valuedvarsfromint[var][sm]))
                else:
                    readable.append(var+ '=' + str(sm + vars2bv[var][1]))
        newSamples.append(newsample)
        newSamplesReadable.append(readable)
    with open(nsamples, "w+") as fi:
        fi.write(' '.join([str(vars2bv[var][2]-vars2bv[var][1]) for var in orderedVars]) + '\n')
        for i in range(len(newSamples)):
            fi.write(str(i) + ', ' + ' '.join(newSamples[i]) + '\n')
    with open(rsamples, "w+") as fi:
        for i in range(len(newSamples)):
            fi.write(str(i) + ', ' + ' '.join(newSamplesReadable[i]) + '\n')
