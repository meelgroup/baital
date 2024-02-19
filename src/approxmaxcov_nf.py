## /***********[approxmaxcov_nf.py]
# Copyright (c) 2022 Eduard Baranov, Sourav Chakraborty, Axel Legay, Kuldeep S. Meel, Vinodchandran N. Variyam 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ***********/


import argparse
import os
import time
import math
import shutil
import random
import sys
import utils
import converter
from pathlib import Path
      
# Computing exact number of combinations 
def get_combinations_nf(z3file, size, outputfile, combs):
    tmpCNF = z3file[:-4] + '.tmp'
    z3outFile = 'z3res.txt'
    varsizes = {}
    orderedvars= [] 
    with open(z3file) as f:
        varline = f.readline()[3:].strip().split(' ')
        for el in varline:
            parts = el.strip().split('=')
            varsizes.update({parts[0]:int(parts[1])})
            orderedvars.append(parts[0])
    orderedvars = list(varsizes.keys())
    feasibleCombs = []
    allComb = []
    start = time.time()
    #generate all combinations to check
    if size == 1:
        allComb = [[(x,y)] for x in varsizes for y in range(varsizes[x])]
    else:
        for precomb in combs[-1]:
            first = orderedvars.index(precomb[-1][0]) +1
            for l in range(first, len(orderedvars)):
                for v in range(varsizes[orderedvars[l]]):
                    newComb = precomb[:] + [(orderedvars[l],v)]
                    allComb.append(newComb)
    
    total = len(allComb)
    print("Total combinations to check " + str(total))
    curPerc = 0.0
    with open(outputfile, "w+") as f:
        for i in range(len(allComb)):
            comb = allComb[i]
            shutil.copyfile(z3file, tmpCNF)
            # add constraint to include the current combination
            with open(tmpCNF, 'a+') as ftmpCNF:
                for lit in comb:
                    if varsizes[lit[0]] > 2:
                        nBits = math.ceil(math.log2(varsizes[lit[0]]))
                        ftmpCNF.write('(assert  (= ' + lit[0] + ' (_ bv' + str(lit[1]) + ' ' + str(nBits) +')))\n')
                    else:
                        if lit[1] ==0:
                            ftmpCNF.write('(assert (not ' + lit[0] +'))\n')
                        else:
                            ftmpCNF.write('(assert ' + lit[0] +')\n')
                ftmpCNF.write('(check-sat)\n')
            # check satisfiability
            cmd = 'z3 ' + tmpCNF + ' > ' + z3outFile 
            os.system(cmd)
            with open(z3outFile) as fres:
                lines = fres.readlines()
                s = 'UNSAT'
                if len(lines) > 0 and lines[0].strip() == 'sat':
                    s= 'SAT'
            if s != 'UNSAT':
                f.write(','.join(map(str, comb)) + '\n')
                feasibleCombs.append(comb)
            if i / total > curPerc + 0.05:
                curPerc += 0.05
                print(str(round(100 * curPerc)) + "% done")
            utils.rmfile(z3outFile)
    utils.rmfile(tmpCNF)
    print("Time to get satisfiable combinations " + str(time.time() - start))
    return feasibleCombs             

# Generate file with ApproxMaxCov constraints and convert to CNF
def generateGFFile(qfbvfile, twise, dimacsFile):
    tmpFile = 'tmp.smt'
    vars2bv = {}
    orderedvars= [] 
    with open(qfbvfile) as f:
        varline = f.readline()[3:].strip().split(' ')
        for el in varline:
            parts = el.strip().split('=')
            vars2bv.update({parts[0]:int(parts[1])})
            orderedvars.append(parts[0])
    
    
    nVars = len(orderedvars)
    maxVal = max(vars2bv.values())
    maxValBits = math.ceil(math.log2(maxVal))
    nVarBits = math.ceil(math.log2(nVars))
    
    shutil.copyfile(qfbvfile, tmpFile)
    with open(tmpFile, 'a+') as f:
        for i in range(twise):
            f.write('(declare-fun tmp_v_' + str(i) +' () (_ BitVec '+ str(nVarBits) +'))\n')
            f.write('(assert (bvule tmp_v_' + str(i)+ ' (_ bv' + str(nVars-1) + ' ' + str(nVarBits) +')))\n')
        
        for i in range(twise):
            for j in range(i+1, twise):
                f.write('(assert ( not (=  tmp_v_'+ str(i) + ' tmp_v_' + str(j) +  ')))\n')
        
        for i in range(twise):
            f.write('(declare-fun tmp_v_' + str(i+ twise) +' () (_ BitVec '+ str(maxValBits) +'))\n')
            
        for i in range(twise):
            for j in range(nVars):
                if vars2bv[orderedvars[j]] > 2:
                    extrabits = maxValBits - math.ceil(math.log2(vars2bv[orderedvars[j]]))
                    f.write('(assert (or (not (= tmp_v_'+ str(i) + ' (_ bv' + str(j) + ' '+ str(nVarBits) +'))) (= tmp_v_' + str(i+twise) + ' ((_ zero_extend '+ str(extrabits) +') ' + orderedvars[j] + '))))\n')
                else:
                    f.write('(assert (or (not (= tmp_v_'+ str(i) + ' (_ bv' + str(j) + ' '+ str(nVarBits) +'))) (or (and (= tmp_v_' + str(i+twise) +'(_ bv1 '+ str(maxValBits) +')) ' + orderedvars[j] +') (and (= tmp_v_' + str(i+twise) +'(_ bv0 '+ str(maxValBits) +')) (not ' + orderedvars[j] +')))))\n')

        for i in range(nVarBits):
            mask = '(_ bv' + str(int(math.pow(2,i))) +' '+ str(nVarBits) +')'
            for t in range(twise):
                f.write('(declare-fun maxcov_v_' + str(t)+'_'+str(i) +' () Bool)\n')
                f.write('(assert (= maxcov_v_' + str(t)+'_'+str(i) +' (= (bvand tmp_v_' + str(t)+' '+mask+'  ) '+mask+')))\n')
        for i in range(maxValBits):
            mask = '(_ bv' + str(int(math.pow(2,i))) +' '+ str(maxValBits) +')'
            for t in range(twise):
                f.write('(declare-fun maxcov_v_' + str(t+ twise)+'_'+str(i) +' () Bool)\n')
                f.write('(assert (= maxcov_v_' + str(t+ twise)+'_'+str(i) +' (= (bvand tmp_v_' + str(t+ twise)+' '+mask+'  ) '+mask+')))\n')
                
        f.write("(apply (then simplify (then bit-blast tseitin-cnf)))\n")

    converter.convert2CNF(tmpFile, dimacsFile, vars2bv, nMaxcovVars=twise*(nVarBits + maxValBits))

# Computes approximate number of combinations
def approxComb_nf(qfbvfile, twise, epsilon, delta, seed):
    benchmarkName = os.path.basename(qfbvfile).split('.')[0]
    dimacsFile = benchmarkName+'.cnf'
    approxOutput='out.pmc'

    generateGFFile(qfbvfile, twise, dimacsFile)
    utils.rmfile(approxOutput)
    
    seedstr = str(seed) if seed else str(random.randint(1,10000))
    cmd = 'approxmc --seed ' + seedstr + ' --epsilon ' + str(epsilon) + ' --delta ' + str(delta) + ' ' + dimacsFile + ' >' + approxOutput  
    os.system(cmd)

    result = -1
    divisor = math.factorial(twise)
    with open(approxOutput) as f:
        for line in f:
            if line.startswith('s mc'):
                number= int(line.strip().split(' ')[2].strip())
                result = number // divisor
                break
    if result != -1:
        print("Approximate number of combinations is " + str(result))
    else:
        print("Result is not found in " + approxOutput)
    utils.rmfile(approxOutput)
    utils.rmfile(dimacsFile)
    return result

#-----------------------------------------------------------------------------------------------------
# qfbvfile - input file with constraints
# size - size of combinations (twise)
# outputdir - directory to store combinations for exact counting
# approx - if True: use approximation else: use exact counting
# epsilon-delta - approximation parameters
# seed - random seed for approxmc
# returns number of combinations
# in case of exact, generates a set of files benchmarkName_i.comb for i \in [1..size] with valid combinations of size i
def run(qfbvfile, size, outputdir, approx, epsilon, delta, seed):
    if approx:
        start_full = time.time()
        res = approxComb_nf(qfbvfile, size, epsilon, delta, seed)
        print("Total time: " + str(time.time() - start_full))
    else:
        combs = []
        benchmarkName = os.path.basename(qfbvfile).split('.')[0]
        start_full = time.time()
        for i in range(size):
            print("Generating " + str(i+1) + "-wise combinations")
            combs.append(get_combinations_nf(qfbvfile, i+1, os.path.join(outputdir, benchmarkName + '_' + str(i+1) + '.comb'), combs))
        res = len(combs[-1])
        print("Number of combinations is " + str(res))
        print("Total time: " + str(time.time() - start_full))
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--outputdir", type=str, default="results/", help="output directory", dest='outputdir')
    parser.add_argument("--approximate", action='store_true', help="Computes combinations approximately", dest='approx')
    parser.add_argument("--twise", type=int, help="size of feature combinations. Note that with non-approximate method all combinations with smaller size would be generated", dest='twise')
    parser.add_argument("--delta", type=float, default=0.05, help="Delta for approximate counting", dest='delta')
    parser.add_argument("--epsilon", type=float, default=0.05, help="Epsilon for approximate counting", dest='epsilon')
    parser.add_argument("--seed", type=int, help="Random seed. Unused if approximate is not selected", dest='seed')
    parser.add_argument('qfbvfile', nargs='?', type=str, default="", help='input file with constraints')
    args = parser.parse_args()

    if args.qfbvfile == '':
        parser.print_usage()
        sys.exit(1)
    if not args.twise:
        parser.print_usage()
        sys.exit(1)

    Path(args.outputdir).mkdir(parents=True, exist_ok=True)
    run(args.qfbvfile, args.twise, args.outputdir, args.approx, args.epsilon, args.delta, args.seed)
