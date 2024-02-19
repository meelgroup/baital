# /***********[utils.py]
# Copyright (c) 2024 Eduard Baranov, Axel Legay, Kuldeep Meel
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
import os

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
    if k > n/2:
        k = n-k
    res =1
    for i in range(k):
        res *= n-i
    for i in range(k):
        res //= (i+1)
    return res


# The function update trieNode and count variables. PerLiteral controls whether the total or per-literal counting shall be performed. Comb argument is aggregator for recursion, shall be [] in the call.
def getTuples_rec(lst, sizeLeft, trieNode, count, comb, perLiteral = False):
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
            combNew = comb[:] + [lst[i]] if perLiteral else comb
            getTuples_rec(lst[i+1 :], sizeLeft -1, trieNodeNew, count, combNew, perLiteral)

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

# Used in genRandomBoxes_nf
def random_walk(proba):
    return random.random() < proba

# Generates boxes for approximate counting for multivalued case.
def genRandomBoxes_nf(nvars, size, varsizes, number, matrix):
    res = []
    total_comb = matrix[nvars-1][size-1]
    if total_comb <= number:
        print('There are only ' + str(total_comb) + ' combinations')
        for comb in itertools.combinations(range(0,nvars), size):
            combsizes = [list(range(varsizes[x])) for x in comb]
            res.extend([tuple(sorted(zip(comb,k))) for k in itertools.product(*combsizes)])
    else:
        for ind in range(number):
            box = []
            i = nvars-1
            j = size-1
            while len(box) < size:
                if i == 0:
                    box.append(i)
                elif random_walk(matrix[i-1][j]/matrix[i][j]):
                    i -=1
                else:
                    box.append(i)
                    i-=1
                    j-=1
            res.append(tuple(sorted(map(lambda x: (x, random.randrange(varsizes[x])), box))))
    return res

# Given a sample removes boxes that are not covered by the sample
def updateBoxesCoverage(uncovBoxes, size, sample):
    newUncovBoxes = [] 
    for comb in uncovBoxes:
        if not all(sample[abs(comb[i])-1] == comb[i] for i in range(size)):
            newUncovBoxes.append(comb)
    return newUncovBoxes

# Given a sample remove boxes that are not covered by the sample. Numerical Features case
def updateBoxesCoverage_nf(uncovBoxes, size, sample):
    newUncovBoxes = [] 
    for comb in uncovBoxes:
        if not all(sample[comb[i][0]] == comb[i][1] for i in range(size)):
            newUncovBoxes.append(comb)
    return newUncovBoxes

# Given a set of samples removes boxes that are not covered by the samples.
def updateBoxesCoverageSet(uncovBoxes, size, samples):
    newUncovBoxes = [] 
    for comb in uncovBoxes:
        if all((not all(sample[abs(comb[i])-1] == comb[i] for i in range(size))) for sample in samples):
            newUncovBoxes.append(comb)
    return newUncovBoxes

# Used for --extra-samples option. 
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

# Loading preprocessed combinations
def get_combinations_from_file(combfile):
    with open(combfile, "r") as f:
        if combfile[-5:] == 'acomb':
            total = int(f.readline().split(' ')[1].strip())
        else:
            total = len(f.readlines()) -1
    return total

# Loading MaxCov from file
def getCoverageFromCombFile(combinationsFile):
    if combinationsFile[-5:] == '.comb':
        with open(combinationsFile) as f:
            lines = f.readlines()
            return len(lines)

# Delete file
def rmfile(filename):
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError:
            pass
