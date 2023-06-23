# /***********[sampling.py]
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

import time
import os
import waps_upd
import math
import random
import argparse
import sys
import numpy as np
import weightFunctions
import utils
import sample_set_combinations
import textwrap
import shutil

TMPSAMPLEFILE = 'samples_temp.txt'
PICKLEFILE = 'saved.pickle'
WEIGHTFILEPREF = 'weights'
CMSGENCNFFILESUFFIX='_cmsgen.cnf'

NBOXESFORUSEBESTSAMPLES = 4320
USEBESTSAMPLESCOEFF = 10

# For strategies 3 and 4 a coefficient for the number of boxes. Each literal is expected to appear in APPROXCOEFF*(2**(twise-1)) boxes
APPROXCOEFF = 25

#For --desired-coverage option and strategy 5, coverage is computed approximately with the following parameters:
DESCOVDELTA = 0.1
DESCOVEPSILON = 0.1

# For strategies 3 and 4 computes number of boxes each literal is involved
def computeNBoxesLit(varsBoxes, nvars):
    res = {var : 0 for var in [i+1 for i in range(nvars)] + [-i-1 for i in range(nvars)]}
    for box in varsBoxes:
        for var in box:
            res[var] +=1
    for var in res.keys():
        if res[var] ==0:
            res[var] = 1
    return res

# For strategies 3 and 4 estimates current coverage of each literal
def boxesCoveragePerLiteral(boxes, nBoxesLit, nvars, size):
    count ={var : nBoxesLit[var] for var in [i+1 for i in range(nvars)] + [-i-1 for i in range(nvars)]}
    for comb in boxes:
        for var in comb:
            count[var] -=1
    for var in count.keys():
        count[var] = int(utils.cnk(nvars-2, size-1) * count[var] *(2**(size-1)) / nBoxesLit[var])
    return count

# For strategies 2 and 4 maximal number of combinations is over-approximated assuming any combination possible disregarding constraints
def countMaxComb(nvars, twise):
    val = (2**(twise -1)) * utils.cnk(nvars-1, twise-1)
    res = {var : val for var in [i+1 for i in range(nvars)] + [-i-1 for i in range(nvars)]}
    return res

# For --desired-coverage option gets an estimation of the total number of combinations
def getMaxCov(dimacscnf, twise, combinationsFile):
    if combinationsFile[-5:] == '.comb':
        return utils.getCoverageFromCombFile(combinationsFile)
    else:
        return cnf_combination.run(dimacscnf, twise, 2, '', DESCOVEPSILON, DESCOVDELTA)

# Attempts to get the total number of combinations or models from .acomb files.
def loadApproxCount(combinationsFile):
    res = {}
    if not os.path.exists(combinationsFile):
        print(f"File {combinationsFile} not found.")
        sys.exit(1)
    with open(combinationsFile) as f:
        lines = f.readlines()
    try:
        for line in lines[1:]:
            spl = line.strip().split(' ')
            res.update({int(spl[0]): int(spl[1])})
        return res
    except:
        print(f"Wrong format of the file {combinationsFile}. Each line shall have format 'x y' where x is a literal and y is a number of models or combinations with this literal")
        sys.exit(1)

# Attempts to get the total number of combinations from the provided combinationsFile. Expected either .comb or .acomb file
def loadMaxComb(nvars, twise, combinationsFile):
    if not os.path.exists(combinationsFile):
        print(f"File {combinationsFile} not found.")
        sys.exit(1)
    if combinationsFile[-6:] == '.acomb':
        print("Warning: a file with approximate number of combinations given.")
        return loadApproxCount(combinationsFile) 
    res = {var : 0 for var in [i+1 for i in range(nvars)] + [-i-1 for i in range(nvars)]}
    with open(combinationsFile) as f:
        lines = f.readlines()
    try:
        nSize = len(lines[0].split(","))
        if nSize != twise:
            print(f"Wrong size of combinations in {combinationsFile}: expected {twise}, {nSize} is in the file")
            sys.exit(1)
        for line in lines:
            comb = map(lambda x: int(x.strip()), line.split(","))
            for val in comb:
                res[val] +=1
        return res
    except:
        print(f"Exception during the processing of {combinationsFile}. Each line shall contain a comma separated combination of size {twise}. Does {combinationsFile} correspond to the input file?")
        sys.exit(1)

# Attempts to get the total number of combinations or models from .count files.
# not used anymore
def loadModelCount(combinationsFile):
    res = {}
    if not os.path.exists(combinationsFile):
        print(f"File {combinationsFile} not found.")
        sys.exit(1)
    with open(combinationsFile) as f:
        lines = f.readlines()
    if combinationsFile[-6:] == '.acomb':
        lines = lines[1:]
    try:
        for line in lines:
            spl = line.strip().split(' ')
            res.update({int(spl[0]): int(spl[1])})
        return res
    except:
        print(f"Wrong format of the file {combinationsFile}. Each line shall have format 'x y' where x is a literal and y is a number of models or combinations with this literal")
        sys.exit(1)

def runCmsgen(cnffile, outputfile, samples):
    seed = random.randrange(1000000)
    cmd = "../bin/cmsgen --samplefile " + outputfile + " --samples " + str(samples) + " --seed " + str(seed) + " " + cnffile
    try:
        os.system(cmd)
    except Exception as inst:
        print(inst)   
        sys.exit(1)
    
def insertWeights(dimacscnf, cmsfile, weightFile):
    with open(dimacscnf) as fd:
        lines = fd.readlines()
        with open(weightFile) as fw:
            weights = list(map((lambda x : x.strip().split(',')),fw.readlines()))
            with open(cmsfile,'w+') as fc:
                i=0
                while i < len(lines) and (not (lines[i].startswith('p '))):
                    fc.write(lines[i])
                    i +=1
                if i == len(lines):
                    print("No line starting with 'p' found in "+ dimacscnf+". Aborting")
                    sys.exit(1)
                fc.write(lines[i])
                i +=1
                for weight in weights:
                    fc.write("w " + weight[0] + ' '+ weight[1] + '\n')
                while i < len(lines):
                    fc.write(lines[i])
                    i+=1

def selectBestSamples(testBoxes,twise,newSamples,samplesperround):
    samplecov,boxcov = utils.computeBoxesCoverageImprove(testBoxes,twise,newSamples)
    selected = []
    while len(selected) < samplesperround:
        best = max(samplecov)
        samplecov[best[1]] = (-1,best[1],best[2])
        selected.append(best[1])
        for j in best[2]:
            for i in boxcov[j]:
                if i != best[1] and i not in selected:
                    oldval = samplecov[i]
                    oldval[2].remove(j)
                    samplecov[i] = (oldval[0]-1,oldval[1],oldval[2])
    return [newSamples[x] for x in selected]

def run(nSamples, rounds, dimacscnf, outputFile, twise, strategy, descoverage=None, samplesperround=-1, combinationsFile=None, funcNumber=2, cmsgen=False, useBestSamples = False):
    if os.path.exists(TMPSAMPLEFILE):
        os.remove(TMPSAMPLEFILE)
    output = open(outputFile, 'w+')
        
    basename = os.path.splitext(os.path.basename(dimacscnf))[0]
    cmsfile = basename + CMSGENCNFFILESUFFIX
    
    if descoverage:
        nSamples = -1
    else:
        samplesperround = math.ceil(nSamples/rounds)
    
    start = time.time()

    #Get number of variables from DIMACS file
    nvars = 0
    with open(dimacscnf) as cnfFile:
        for line in cnfFile.readlines():
            if line.startswith('p'):
                nvars = int(line.split(' ')[2].strip())
                break
    
    #Load precomputed number of combinations or models or take an upper-approximation
    #if strategy == 3: 
    #    maxComb = loadModelCount(combinationsFile)
    if strategy == 5: 
        maxComb = None
    elif strategy == 1 or strategy == 3: #Strategy 1 - loading feasible combinations; could have approximate number of combinations
        maxComb = loadMaxComb(nvars, twise, combinationsFile)
    elif strategy == 2 or strategy == 4: # take upper-approximation
        maxComb = countMaxComb(nvars, twise)
    else:
        print('Unknown strategy')
        sys.exit(1)
   
   # Estimation of maxCov for --desired-coverage option
    if descoverage:
        maxcov = getMaxCov(dimacscnf, twise, combinationsFile)
   
    ### Stores current (approximated) value of combinations for each liteal for generated samples 
    count = {var : 0 for var in [i+1 for i in range(nvars)] + [-i-1 for i in range(nvars)]}

    # Generation of boxes for approximate strategies
    if strategy == 3 or strategy == 4:
        nBoxes = APPROXCOEFF * (2**twise) *nvars
        varsBoxes = utils.genRandomBoxes(nvars, twise, nBoxes, allowGenerateMoreThanExists=True)
        nBoxesLit = computeNBoxesLit(varsBoxes, nvars)
    elif strategy == 1 or strategy == 2: # initialize trie structure
        trie = {}
    
    # Generation of initial weights, stored in WEIGHTFILEPREF + str(roundN+1)  + '.txt'
    weightFunctions.generateWeights(count, nvars, strategy, maxComb, WEIGHTFILEPREF, 1, funcNumber)

    if useBestSamples:
         ntestBoxes = NBOXESFORUSEBESTSAMPLES * (2**twise)
         testBoxes = utils.genRandomBoxes(nvars, twise, ntestBoxes, allowGenerateMoreThanExists=True)

    gensamplesperround = samplesperround*USEBESTSAMPLESCOEFF if useBestSamples else samplesperround
    # main loop
    for roundN in range(rounds):
        print("Round "  + str(roundN+1) + ' started...')
        round_start = time.time()
        weightFile = WEIGHTFILEPREF + str(roundN+1)  + '.txt'
        # Sampling
        if cmsgen:
            insertWeights(dimacscnf, cmsfile, weightFile)
            runCmsgen(cmsfile, TMPSAMPLEFILE, gensamplesperround)
        else:
            if roundN == 0:
                waps_upd.sample(gensamplesperround, '', dimacscnf, None, weightFile=weightFile, outputfile=TMPSAMPLEFILE, savePickle=PICKLEFILE)
            else:
                waps_upd.sample(gensamplesperround, '', '', PICKLEFILE, weightFile=weightFile, outputfile=TMPSAMPLEFILE)
        # Read new samples and update combination counters
        with open(TMPSAMPLEFILE) as ns:
            newSamplesLines = ns.readlines()
            if cmsgen:
                newSamples = [list(map(int, nsl.strip().split(' ')[:-1]))  for nsl in newSamplesLines]
            else:
                newSamples = [list(map(int, nsl.strip().split(',')[1].strip().split(' '))) for nsl in newSamplesLines]
            if useBestSamples:
                newSamples = selectBestSamples(testBoxes,twise,newSamples,samplesperround)
                #scores = [(utils.computeBoxesCoverageImprove(testBoxes,twise,s),s) for s in newSamples]
                #newSamples = [x[1] for x in (sorted(scores, reverse=True))[:samplesperround]]
                testBoxes = utils.updateBoxesCoverageSet(testBoxes, twise, newSamples)
            for i in range(len(newSamples)):
                if nSamples <0 or roundN != rounds-1 or roundN * samplesperround + i < nSamples: #ignore extra samples in case of non divisible by number of rounds
                    if roundN != rounds-1:
                        if strategy == 3 or strategy == 4:
                            #utils.updateBoxesCoverage(varsBoxes, twise, newSamples[i])
                            varsBoxes = utils.updateBoxesCoverage(varsBoxes, twise, newSamples[i])
                        elif strategy == 5:
                                for val in newSamples[i]:
                                    count[val] +=1
                        elif strategy == 1 or strategy == 2:
                            utils.getTuples_rec(newSamples[i], twise, trie, count, [], True)
                        else:
                            print('Unknown strategy')
                            sys.exit(1)
                        # Copy samples to output file
                    sampleNumber = roundN * samplesperround + i
                    output.write(str(sampleNumber) + ',' + ' '.join(map(str,newSamples[i])) + '\n')

        os.remove(TMPSAMPLEFILE)
        
        # Update counter for strategies 3 and 4 - done once, not after each new sample
        if roundN != rounds-1:
            if strategy == 3 or strategy == 4:
                count = boxesCoveragePerLiteral(varsBoxes, nBoxesLit, nvars, twise)
                print("Current approximation of sampled combinations " + str(sum(count.values()) / twise) )
            
            # Generate weights for next round
            weightFunctions.generateWeights(count, nvars, strategy, maxComb, WEIGHTFILEPREF, roundN+2, funcNumber)
        print("Time taken by round " + str(roundN+1) + " :" +  str(time.time()-round_start))
        print("Round " + str(roundN+1) + ' finished...')
        
        # for --desired-coverage option check if exit condition reached
        if descoverage:
            if strategy == 5:
                currentSample = sample_set_combinations.run(output, twise, True, DESCOVEPSILON, DESCOVDELTA)
            else:    
                currentSample = sum(count.values()) / twise
            currentCov = currentSample/maxcov
            if currentCov> descoverage:
                print(f"Coverage {descoverage} reached")
                break
        
    output.close()

    print("Total time taken by sampling:", time.time()-start)
    #cleanup
    if os.path.exists(PICKLEFILE):
        os.remove(PICKLEFILE)
    for rn in range(roundN+2):
        if os.path.exists(WEIGHTFILEPREF + str(rn+1)  + '.txt'):
            os.remove(WEIGHTFILEPREF + str(rn+1)  + '.txt')
    if os.path.exists(cmsfile):
        os.remove(cmsfile)

    

epilog=textwrap.dedent('''\
Strategies information: strategies define what parameter is used to select weights for the next round. The parameter is computed for each literal. The following lists the parameter for each strategy.
    Strategy 1: ratio between the number of combinations with a literal in current sample set and the number of combinations with the literal allowed by constraints of the configurable system
    Strategy 2: ratio between the number of combinations with a literal in current sample set and choice of twise distinct elements in NVariables
    Strategy 3: ratio between the approximate number of combinations with a literal in current sample set and the number of combinations with the literal allowed by constraints of the configurable system
    Strategy 4: ratio between the approximate number of combinations with a literal in current sample set and choice of twise distinct elements in NVariables
    Strategy 5: the number of samples the literal appears in current sample set
    Note that the number of combinations with the literal allowed by constraints or the number of models involving the literal shall be precomputed and provided in a file with --combinations option. These precomputations can be approximate.
''')

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog=epilog)
    parser.add_argument("--outputfile", type=str, default="samples_full.txt", help="output file for samples", dest='outputfile')
    parser.add_argument("--twise", type=int, default=2, help="t value for t-wise coverage, default 2", dest='twise')
    parser.add_argument("--strategy", type=int, default=5, choices=range(1, 6), help="Strategy, see help for description, default 5 ", dest='strategy')
    parser.add_argument("--function", type=int, default=2, choices=range(1, 8), help="Function number between 1 and 7 for weight generation, used in strategies 1, 2, 3, and 4.", dest='funcNumber')
    end_cond = parser.add_mutually_exclusive_group()
    end_cond.add_argument("--samples", type=int, default=500, help="total number of samples to generate", dest='samples')
    end_cond.add_argument("--desired-coverage", type=float, help="samples are genereted until the coverage reaches the given value or --rounds is completed. Cannot be used with --samples", dest='descoverage')
    parser.add_argument("--samples-per-round", type=int, default = 50, help="number of samples generated per round if --desired-coverage is set", dest='spr')
    parser.add_argument("--rounds", type=int, default=20, help="number of rounds to take samples", dest='rounds')
    parser.add_argument("--combinations", type=str, default='', help="file with the number of combinations with the literal allowed by constraints or the number of models involving the literal. If computed approximately - shall have .acomb extension", dest="combinationsFile")
    parser.add_argument("--extra-samples", action='store_true', help="Each round more samples are generated and the best are selected", dest='generateMoreSamples')
    parser.add_argument("--cmsgen", action='store_true', help="use cmsgen instead of waps", dest='cmsgen')
    parser.add_argument("--seed", type=int, default=None, help="random seed", dest="seed")
    parser.add_argument('DIMACSCNF', nargs='?', type=str, default="", help='input cnf file')
    args = parser.parse_args()
    if args.DIMACSCNF == '':
        parser.print_usage()
        sys.exit(1)

    if args.seed:
        np.random.seed(args.seed)
        random.seed(args.seed)
    run(args.samples, args.rounds, args.DIMACSCNF, args.outputfile, args.twise, args.strategy, args.descoverage, args.spr, args.combinationsFile,  args.funcNumber, cmsgen=args.cmsgen, useBestSamples=args.useBestSamples)

if __name__== "__main__":
    main()
