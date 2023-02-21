# /***********[utils.py]
# Copyright (c) 2022 Eduard Baranov, Axel Legay, Kuldeep Meel
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

import itertools
import random

# Simple and incomplete DIMACS2 parser
def parse_cnf(cnffile):
    clauses = []
    with open(cnffile) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("c"):
                continue
            elif line.startswith("p"):
                nVars = int(line.strip().split(' ')[2])
            else:
                literals = list(map(int, line.strip().split(' ')))
                if len(literals) > 1:
                    clauses.append(literals[:-1])
    return nVars, clauses

# Compute n choose k
def cnk(n, k):
    res =1
    for i in range(k):
        res *= n-i
    for i in range(k):
        res /= (i+1)
    return res

# The function update trieNode and count variables. PerLiteral controls whether the total or per-literal counting shall be performed. Comb argument is aggregator for recursion, shall be [] in the call.
def getTuples_rec(lst, sizeLeft, trieNode, count, comb, perLiteral):
    if sizeLeft == 1:
        for x in lst:
            if x not in trieNode: 
                trieNode[x] = True
                if perLiteral:
                    for v in [x] + comb:
                        count[v] +=1
                else:
                    count[0] +=1
    else:
        for i in range(len(lst) - sizeLeft + 1):
            if lst[i] not in trieNode:
                trieNode[lst[i]] = {}
            trieNodeNew = trieNode[lst[i]]
            combNew = comb[:] + [lst[i]]
            getTuples_rec(lst[i+1 :], sizeLeft -1, trieNodeNew, count, combNew, perLiteral)

#def genRandomBoxesOld(nvars, size, number, allowGenerateMoreThanExists = False):
#    res = {}
#    maxval = cnk(nvars, size) *(2**size)
#    if  maxval < number and not allowGenerateMoreThanExists:
#        print('There are only ' + str(maxval) + ' combinations')
#        coeff = list(itertools.product(range(2), repeat=size))
#        for comb in itertools.combinations(range(1,nvars+1), size):
#            res.update({(0,tuple(sorted(map(lambda x : x[0] if x[1]==1 else -x[0], zip(comb,k))))):0 for k in coeff})
#        return res
#    for i in range(number):
#        res.update({(i,tuple(sorted(map(lambda x: x if random.randint(0,1) == 1 else -x, random.sample(range(1,nvars+1), size))))):0})
#    return res

# Generates boxes for approximate counting. If allowGenerateMoreThanExists - always generates <number> of boxes, else can generate fewer if total number of distinct combinations is smaller that <number>            
def genRandomBoxes(nvars, size, number, allowGenerateMoreThanExists = False):
    res = []
    maxval = cnk(nvars, size) *(2**size)
    if  maxval < number and not allowGenerateMoreThanExists:
        print('There are only ' + str(maxval) + ' combinations')
        coeff = list(itertools.product(range(2), repeat=size))
        for comb in itertools.combinations(range(1,nvars+1), size):
            res.extend([tuple(sorted(map(lambda x : x[0] if x[1]==1 else -x[0], zip(comb,k)))) for k in coeff])
        return res
    for i in range(number):
        res.append(tuple(sorted(map(lambda x: x if random.randint(0,1) == 1 else -x, random.sample(range(1,nvars+1), size)))))
    return res

def updateBoxesCoverage(uncovBoxes, size, sample):
    newUncovBoxes = [] 
    for comb in uncovBoxes:
        if not all(sample[abs(comb[i])-1] == comb[i] for i in range(size)):
            newUncovBoxes.append(comb)
    return newUncovBoxes

def updateBoxesCoverageSet(uncovBoxes, size, samples):
    newUncovBoxes = [] 
    for comb in uncovBoxes:
        if all((not all(sample[abs(comb[i])-1] == comb[i] for i in range(size))) for sample in samples):
            newUncovBoxes.append(comb)
    return newUncovBoxes

def computeBoxesCoverageImprove(newUncovBoxes, size, samples):
    samplecov = []
    boxcov = [[] for i in range(len(newUncovBoxes))]
    for i in range(len(samples)):
        scov = []
        for j in range(len(newUncovBoxes)):
             if all(samples[i][abs(newUncovBoxes[j][k])-1] == newUncovBoxes[j][k] for k in range(size)):
                scov.append(j)
                boxcov[j].append(i)
        samplecov.append((len(scov),i,set(scov)))
    return (samplecov,boxcov)

#def updateBoxesCoverageOld(boxes, size, sample):
#    for comb in boxes.keys():
#        if boxes[comb] == 0 and all(sample[abs(comb[1][i])-1] == comb[1][i] for i in range(size)):
#            boxes[comb] = 1


def get_combinations_from_file(combfile):
    with open(combfile, "r") as f:
        if combfile[-5:] == 'acomb':
            total = int(f.readline().split(' ')[1].strip())
        else:
            total = len(f.readlines()) -1
    return total


def getCoverageFromCombFile(combinationsFile):
    if combinationsFile[-5:] == '.comb':
        with open(combinationsFile) as f:
            lines = f.readlines()
            return len(lines)
