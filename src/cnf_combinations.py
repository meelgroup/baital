## /***********[cnf_combinations.py]
# Copyright (c) 2024 Eduard Baranov, Sourav Chakraborty, Axel Legay, Kuldeep S. Meel, Vinodchandran N. Variyam 
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
import bisect
import pycosat
import sys
import random
from pathlib import Path
import utils

TMPCNFSUFFIX = '_tmp.cnf'
     
###combs is a list of precomputed combinations of smaller sizes: combs[x] contains combinatios of size x+1             
def get_combinations(nVars, clauses, size, outputfile, combs):
    feasibleCombs = []
    allComb = [] ### list of combinations to check for SAT
    start = time.time()
    if size == 1:
        allComb = [[x] for x in range(-nVars, 0)] + [[x] for x in range(1, nVars+1)]
    else:
        literals = list(map(lambda x : x[0], combs[0])) # remove literals that are known to be unsat
        for precomb in combs[-1]:  # expected to be sorted, add only literals with greater value. Combination of size can be sat only if its subset of size-1 is sat
            first = bisect.bisect_right(literals, precomb[-1]) # we add only literals that are greater than any literal in precomb
            for l in range(first, len(literals)):
                if -(literals[l]) not in precomb: # to avoid i and -i in combination
                    newComb = precomb[:] + [literals[l]]
                    allComb.append(newComb)
    f = open(outputfile, "w")
    total = len(allComb)
    print("Total combinations to check " + str(total))
    curPerc = 0.0
    for i in range(len(allComb)):
        comb = allComb[i]
        cnf = clauses[:] + list(map(lambda x : [x], comb)) # add a clause x for each literal in combination
        s = pycosat.solve(cnf)
        if s != 'UNSAT':
            f.write(','.join(map(str, comb)) + '\n')
            feasibleCombs.append(comb)
        if i / total > curPerc + 0.05:
            curPerc += 0.05
            print(str(round(100 * curPerc)) + "% done")
    f.close()
    print("Time to get satisfiable combinations " + str(time.time() - start))
    return feasibleCombs

#-----------------------------------------------------------------------------------------------------

# Generete clauses corresponding to i < n, where i consists of variables startPos..startPos+bvsize-1
def lessClause(startPos, n, bvsize):
    bitN = [ (n >> i) % 2 for i in range(bvsize)]
    for i, j in enumerate(bitN): #reverse & cutdown end zeroes
        if j:
            bitN = list(reversed(bitN[i:]))
            break
    result = []
    agg = []
    for i in range(len(bitN)):
        if bitN[i]:
            agg.append(-(startPos +i))
        else:
            result.append(agg[:] + [-(startPos +i)])
    result.append(agg)
    return result

# Generete clauses corresponding to i= j => v_i = x_j
def relClause(startPos, n, bvsize, vPos):
    bitN = list(reversed([ ((n-1) >> i) % 2 for i in range(bvsize)]))
    neq = [(startPos + i) * (bitN[i]*2-1) * (-1) for i in range(len(bitN))]
    return [neq[:] + [-n, vPos], neq[:] + [n, -vPos]]

       
# Generete clauses corresponding to i_1 < i_2
def ltClause(startPosFirst, startPosSecond, bvsize):
    if (bvsize==1):
        return [[-startPosFirst],[startPosSecond]]
    else:
        recres = ltClause(startPosFirst+1, startPosSecond+1, bvsize-1)
        return [[-startPosFirst] + cl[:] for cl in recres] + [[startPosSecond] + cl[:] for cl in recres] + [[-startPosFirst, startPosSecond]]

#Generate clause i != x, where i consists of variables startPos..startPos+bvsize-1  
def neqClause(startPos, x, bvsize):
    bitX = list(reversed([ ((abs(x)-1) >> i) % 2 for i in range(bvsize)]))
    result = []
    for i in range(bvsize):
        result.append(startPos + i if bitX[i] == 0 else -(startPos + i))
    return [result]

def generateNewClauses(nVars, fsize, bvsize):
    newClauses = []
    valueVarsBaseIndex = nVars + fsize*bvsize
    for i in range(fsize):
        newClauses.extend(lessClause(nVars + i*bvsize + 1, nVars, bvsize))
    for i in range(fsize-1):
        newClauses.extend(ltClause(nVars + i*bvsize + 1, nVars + (i+1)*bvsize + 1, bvsize))
    for i in range(fsize):
        for j in range(1, nVars+1):
            newClauses.extend(relClause(nVars + i*bvsize + 1, j, bvsize, valueVarsBaseIndex + i + 1))
    return newClauses

def writeClauses(outputFile, clauses, nVars, fsize, bvsize):
    with open(outputFile, 'w+') as f:
        varList = [i for i in range(nVars + 1, nVars + fsize*bvsize + fsize +1)]
        f.write('c ind ' + ' '.join(list(map(str, varList))) + ' 0\n')
        f.write('p cnf ' + str(nVars + fsize*bvsize + fsize) + ' ' +  str(len(clauses)) + '\n')
        for cl in clauses:
            f.write(' '.join(list(map(str, cl + [0]))) + '\n')
    
    
#vars indexes: [1, nVars] - original, [nVars+1, nVars + fsize*bvsize] - index variables, [nVars + fsize*bvsize + 1, nVars + fsize*bvsize + fsize]
# index i correspond to var=(i+1), indexes starting from 0 rather than from 1
def generateGFCNF(nVars, clauses, fsize, outputFile):
    bvsize = math.ceil(math.log2(nVars+1))
    newClauses = generateNewClauses(nVars, fsize, bvsize)
    writeClauses(outputFile, clauses + newClauses, nVars, fsize, bvsize)        


# Generate formula to compute the number of feature combinations involving a literal in a parameter. Size of feature combination is twise = fzise + 1 (the given literal)
def generateGFCNFLiteral(nVars, clauses, fsize, literal, outputFile):
    if fsize== 0:
        return
    bvsize = math.ceil(math.log2(nVars+1))
    valueVarsBaseIndex = nVars + fsize*bvsize
    newClauses = [[literal]] + generateNewClauses(nVars, fsize, bvsize)
    for i in range(fsize):
        newClauses.extend(neqClause(nVars + i*bvsize + 1, literal, bvsize))
    writeClauses(outputFile, clauses + newClauses, nVars, fsize, bvsize)       

def runApproxmc(tmpCNF, epsilon, delta):
    approxOutput='out.pmc'
    try:
        cmd = 'approxmc --seed ' + str(random.randint(1,10000)) + ' --epsilon ' + str(epsilon) + ' --delta ' + str(delta) + ' ' + tmpCNF + ' >' + approxOutput  
        os.system(cmd)
        result = -1
        with open(approxOutput) as f:
            for line in f:
                if line.startswith('s mc'): #Note the version of ApproxMC
                    number= int(line.strip().split(' ')[2].strip())
                    result = number
                    break
        utils.rmfile(approxOutput)
        return result
    except:
        print("Approxmc call failed.")
        sys.exit(1)

# Computes the approximate number of combinations
def approxComb(nVars, clauses, twise, tmpCNF, epsilon, delta):
    generateGFCNF(nVars, clauses, twise, tmpCNF)
    result = runApproxmc(tmpCNF, epsilon, delta)
    utils.rmfile(tmpCNF)
    return result
    
# Computes the approximate number of combinations for each literal
def approxCombLiteral(nVars, clauses, twise, outputfile, tmpCNF, epsilon, delta):
    res = {}
    curPerc = 0.0
    for i in range(1, nVars+1):
        clausesTmp = clauses[:]
        generateGFCNFLiteral(nVars, clausesTmp, twise-1, i, tmpCNF)
        res[i] = runApproxmc(tmpCNF, epsilon, delta)
        clausesTmp = clauses[:]
        generateGFCNFLiteral(nVars, clausesTmp, twise-1, -i, tmpCNF)
        res[-i] = runApproxmc(tmpCNF, epsilon, delta)
        if i / nVars > curPerc + 0.05:
            curPerc += 0.05
            print(str(round(100 * curPerc)) + "% done")
    with open(outputfile, "w") as f:
        f.write(str(twise)+ '\n')
        for key in res.keys():
            f.write(str(key) + ' ' + str(res[key]) + '\n')
    utils.rmfile(tmpCNF)
    return res
    
#-----------------------------------------------------------------------------------------------------
###Modes: 1 - compute exact number of combinations;  2 - compute approximate number of combinations; 3 - compute approximate number of combinations per literal
def run(dimacscnf, twise, mode, outputdir, epsilon, delta):
    nVars, clauses = utils.parse_cnf(dimacscnf)
    benchmarkName = os.path.basename(dimacscnf).split('.')[0]
    if mode == 2:
        start_full = time.time()
        res = approxComb(nVars, clauses, twise, benchmarkName + TMPCNFSUFFIX, epsilon, delta)
        print("Approximate number of combinations is " + str(res))
        print("Total time: " + str(time.time() - start_full))
    elif mode == 3:
        start_full = time.time()
        res = approxCombLiteral(nVars, clauses, twise, os.path.join(outputdir,  benchmarkName + '_' + str(twise) + '.acomb'), benchmarkName + TMPCNFSUFFIX, epsilon, delta)
        print("Total time: " + str(time.time() - start_full))
    elif mode == 1:
        combs = []   
        start_full = time.time()
        for i in range(twise):
            print("Generating " + str(i+1) + "-wise combinations")
            combs.append(get_combinations(nVars, clauses, i+1, os.path.join(outputdir, benchmarkName + '_' + str(i+1) + '.comb'), combs))
        res = len(combs[-1])
        print("Number of combinations is " + str(len(combs[-1])))
        print("Total time: " + str(time.time() - start_full))
    else:
        print("Unsupproted mode")
        return -1
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--outputdir", type=str, default="results/", help="output directory", dest='outputdir')
    parser.add_argument("--twise", type=int, help="size of feature combinations. Note that with non-approximate method all combinations with smaller size would be generated", dest='size')
    parser.add_argument('DIMACSCNF', nargs='?', type=str, default="", help='input cnf file in dimacs format')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--combinations', action='store_true', help="counts number of combinations, this is the default mode", dest='m1')
    mode.add_argument('--approximate', action='store_true', help="counts approximate number of combinations", dest='m2')
    mode.add_argument('--approximate-literal', action='store_true', help="counts approximate number of combinations for each literal", dest='m3')
    parser.add_argument("--delta", type=float, default=0.05, help="Delta for approximate counting", dest='delta')
    parser.add_argument("--epsilon", type=float, default=0.05, help="Epsilon for approximate counting", dest='epsilon')
    parser.add_argument("--seed", type=int, help="Random seed. Unused if approximate is not selected", dest='seed')
    args = parser.parse_args()
    
    if args.DIMACSCNF == '':
        parser.print_usage()
        sys.exit(1)
        
    if args.seed:
        random.seed(args.seed)
    mode = 1
    if args.m2: 
        mode = 2
    elif args.m3:
        mode =3 
    
    Path(args.outputdir).mkdir(parents=True, exist_ok=True)
    run(args.DIMACSCNF, args.size, mode, args.outputdir, args.epsilon, args.delta)


