# /***********[baital.py]
# Copyright (c) 2024 Eduard Baranov, Axel Legay
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
import random
import sys
import converter
import approxcov_nf
import approxmaxcov_nf
import sampling
import time
import textwrap
import numpy as np
import baital
import utils
import math
from pathlib import Path

def loadValsFromSMTFile(inputfile):
    with open(inputfile) as f:
        line1 = f.readline()
        line2 = f.readline()
        line3 = f.readline()
    if (not line1.startswith(';; ')) or (not line1.startswith(';; ')) or (not line1.startswith(';; ')):
        print("Comments with required data not found in smt file")
        sys.exit(1)
    nVals = {}
    coverednVals = []
    orderedvars = []
    vars2bv = {}
    valuedvarsfromint = {}
    for el in line1[3:].strip().split(' '): #first line providing varnames and number of values
        parts = el.strip().split('=')
        val = int(parts[1])
        if val==2:                          # boolean var (2 values)
            vars2bv.update({parts[0]:[1,0,2]})
        else:                               # integer var 
            nVals.update({parts[0]:val})   
        orderedvars.append(parts[0])
    if len(line2) > 5:
        for el in line2[3:].strip().split(' '): # second line provide integer vars and smallest value (except smallest value equal to 0); except vars defined with var = x || var =y ...  
            parts = el.strip().split('=')
            vmin = int(parts[1])
            vars2bv.update({parts[0]:[math.ceil(math.log2(nVals[parts[0]])), vmin, vmin+nVals[parts[0]]]})
            coverednVals.append(parts[0])
    if len(line3) > 5:
        for el in line3[3:].strip().split(' '): # third line provides integer vars and the list of values (for vars defined with var = x || var =y ...  )
            parts = el.strip().split('=')
            pairs = parts[1][1:-1].split(',')
            valuedvarsfromint.update({parts[0]:{int(p.split(':')[0]) : int(p.split(':')[1]) for p in pairs}})
    for el in nVals:                       # integer vars not appearing in second line: smallest value is 0
        if el not in coverednVals:
            vars2bv.update({el:[math.ceil(math.log2(nVals[el])), 0, nVals[el]]})
    return vars2bv,orderedvars,valuedvarsfromint

def computeCoverage(nsamplesfile, qfbvfile, outputdir, twise, rescombfile, apprx, epsilon, delta, nocomb, seed):
    cstart = time.time()
    cov = approxcov_nf.run(nsamplesfile, twise, apprx, epsilon, delta)
    if not nocomb:
        if rescombfile:
           with open(rescombfile, "r") as f:
               maxcov = int(f.readline().split(' ')[1].strip())
        else:
            maxcov = approxmaxcov_nf.run(qfbvfile, twise, outputdir, apprx, epsilon, delta, seed)
        tcov = cov/maxcov
    else:
        tcov = None
    ctime = time.time() -cstart 
    return cov,tcov,ctime

# runs preprocessing and sampling from baital
def runBaital(dimacscnf, benchmarkName, samplesfile, strategy, twise, samples, descoverage, spr, rounds, outputdir, combfile, papprx, pdelta, pepsilon, funcNumber, preprocessonly, waps, useBestSamples):
    if combfile:
        combinationsFile = combfile
        ptime = -1
    else:
        pstart = time.time()
        combinationsFile = baital.runPreprocess(dimacscnf, twise, outputdir, benchmarkName, strategy, preprocessonly, papprx, pepsilon, pdelta)
        ptime = time.time() - pstart if combinationsFile != '' else -1

    if preprocessonly:
        return ptime,-1
        
    sstart = time.time()
    sampling.run(samples, rounds, dimacscnf, samplesfile, twise, strategy, descoverage=descoverage, samplesperround=spr, combinationsFile=combinationsFile, funcNumber=funcNumber, waps=waps, useBestSamples=useBestSamples)
    stime = time.time() -sstart        
    return ptime,stime
    

def run(inputfile, strategy, twise, samples, descoverage, spr, rounds, outputdir, outfile1, outfile2, nocomb, combfile, papprx, pdelta, pepsilon, funcNumber, rescombfile, nosampling, externalsamplefile, apprx, epsilon, delta, preprocessonly, waps, useBestSamples, seed):
    benchmarkName = os.path.basename(inputfile).split('.')[0]
    nsamples = externalsamplefile if nosampling else (outfile1 if outfile1 else outputdir + benchmarkName +".nsamples")
    ptime, ctime,stime = (-1,-1,-1)
    starttime = time.time()
    if inputfile.endswith('.smt'):
        qfbvfile = inputfile
        vars2bv,orderedVars,valuedvarsfromint = loadValsFromSMTFile(inputfile)
    else:
        qfbvfile = os.path.join(outputdir, benchmarkName + '.smt')
        vars2bv,orderedVars,valuedvarsfromint = converter.generateZ3file(inputfile, qfbvfile) #  convert input file into qf_bv
    if not nosampling:
        cnffile = outputdir + benchmarkName + '.cnf'
        varsmap, varsretmap = converter.convert4Baital(qfbvfile, cnffile, vars2bv) # convert into cnf
        cnfSamplesFile = os.path.join(outputdir, benchmarkName + '.samples')
        ptime,stime = runBaital(cnffile, benchmarkName, cnfSamplesFile, strategy, twise, samples, descoverage, spr, rounds, outputdir, combfile, papprx, pdelta, pepsilon, funcNumber, preprocessonly, waps, useBestSamples)
    if not preprocessonly:
        if not nosampling:
            rsamples = outfile2 if outfile2 else outputdir + benchmarkName +".rsamples"
            converter.changeVarsBack(cnfSamplesFile, nsamples, rsamples, vars2bv, orderedVars, varsretmap, valuedvarsfromint)
            print("Generated samples can be found in " + nsamples +" and "+ rsamples +" files.")
        comb,coverage,ctime = computeCoverage(nsamples, qfbvfile, outputdir, twise, rescombfile, apprx, epsilon, delta, nocomb, seed)

    totaltime = time.time() - starttime
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\x1b[1;34;40m" + "Results" + "\x1b[0m")
    if ptime >0:
        print("Preprocessing time " + str(ptime))
    if stime >0:
        print("Sampling time " + str(stime))
    if ctime >0:
        print("Coverage time " + str(ctime))
    print("Total time "+ str(totaltime))
    print("(Approximate) number of combinations " + str(comb))
    if coverage:
        print("(Approximate) " + str(twise)+"-wise coverage " + str(coverage))

    #cleanup
    if not nosampling:
        utils.rmfile(cnffile)
        utils.rmfile(cnfSamplesFile)
    
    
# quick check of combfile 
def check_combfile(combfile, twise, strategy):
    if strategy == 2 or strategy == 4 or strategy == 5:
        print("Warning: --preprocess-file not used for strategy " + str(strategy))
        return True
    if not os.path.exists(combfile):
        print("File "+ combfile + " not found.")
        return False
    else:
        with open(combfile) as f:
            line = f.readline()
            if combfile[-6:] == '.acomb':
                try:
                    return int(line.strip()) == twise
                except:
                    return False
            elif combfile[-5:] == '.comb':
                return len(line.split(",")) == twise
            else:
                print("Wrong file extension for --preprocess-file. For strategy 1 or 5 .comb or .acomb is expected")
                return False

# quick check of rescombfile used to get the maxcov results
def check_rescombfile(combinations_file, twise):
    with open(combinations_file) as f:
        line = f.readline()
        return len(line.split(",")) == twise

epilog=textwrap.dedent('''\
The tool executes 5 steps (steps 2 and 3 are identical to steps 1 and 2 from baital.py):
    Step 1: convert input file into cnf.
    Step 2: preprocessing. Used for strategies 1, and 3. Has 2 options that are controlled by --strategy and --preprocess-approximate options
        (i) Lists the combinations of size <twise> allowed by cnf constraints (Could take hours for twise=2, infeasible for large models for twise=3).
            Precomputed file can be provided with --preprocess-file option, expected to have .comb extension.
        (ii) Lists the approximate number of combinations of size <twise> for each literal (Could take 1 hour for twise=2, several hours for twise=3, tens of hours for twise>3). 
            Precomputed file can be provided with --preprocess-file option, expected to have .acomb extension. --preprocess-delta and --preprocess-epsilon set the PAC guarantees.
    Step 3: sampling. Generation of samples with high twise coverage. Samples are stored in <outputdir>/<outputfile> (default results/<cnf_filename>.samples). 
        --twise option provides a size of combinations to maximise coverage 
        --strategy defines how the weights are generated between rounds
        --samples number of samples to generate
        --rounds number of rounds for sample generation, weights are updated between rounds. Higher coverage is expected with large number of rounds, however each round requires update of dDNNF annotation that might be long.
        --weight-function a function transforming the ratios computed by strategies 1, 2, 3, and 4 into weights. Varying this parameter might affect the resulted coverage
    Step 4: convert samples for cnf into samples for the original feature model with numerical features. Returns 2 files: .nsample for twise coverage computation and .rsample in format varname=value 
    Step 5: computation of twise coverage. 
        --approximate forces approximate computation.
        --combinations-file can provide a precomputed result (expects .comb extension). 
    
    
Strategies information: strategies define what parameter is used to select weights for the next round. The parameter is computed for each literal. The following lists the parameter for each strategy.
    Strategy 1: ratio between the number of combinations with a literal in current sample set and the number of combinations with the literal allowed by constraints of the configurable system
    Strategy 2: ratio between the number of combinations with a literal in current sample set and choice of twise distinct elements in NVariables
    Strategy 3: ratio between the approximate number of combinations with a literal in current sample set and the number of combinations with the literal allowed by constraints of the configurable system
    Strategy 4: ratio between the approximate number of combinations with a literal in current sample set and choice of twise distinct elements in NVariables
    Strategy 5: the number of samples the literal appears in current sample set
''')
    

def main():
    parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--outputdir", type=str, default="./results/", help="output directory", dest='outputdir')
    parser.add_argument("--outputfile-readable", type=str, default="", help="output file for samples in format var=value, will be placed in outputdir, default <benchmark_name>.rsamples", dest='outputfile2')
    parser.add_argument("--outputfile", type=str, default="", help="output file for samples, will be placed in outputdir, default <benchmark_name>.nsamples", dest='outputfile1')
    parser.add_argument("--twise", type=int, default=2, help="t value for t-wise coverage, default 2", dest='twise')
    parser.add_argument("--waps", action='store_true', help="use an old version with waps instead of cmsgen", dest='waps')
        
    parser.add_argument("--preprocess-file", type=str, default='', help="precomputed file for skipping preprocessing step. Shall have .comb, or .acomb extension. See help for details", dest="combfile")
    parser.add_argument("--preprocess-delta", type=float, default=0.25, help="delta for approximate counting at preprocessing, default 0.25", dest='pdelta')
    parser.add_argument("--preprocess-epsilon", type=float, default=0.25, help="epsilon for approximate counting at preprocessing, default 0.25", dest='pepsilon')
    parser.add_argument("--preprocess-approximate", action='store_true', help="approximate computation of preprocess", dest='papprx')
    parser.add_argument("--preprocess-only", action='store_true', help="Only perform preprocessing", dest='preprocess')
    
    parser.add_argument("--strategy", type=int, default=5, choices=range(1, 6), help="weight generation strategy, default 5. See help for description", dest='strategy')
    end_cond = parser.add_mutually_exclusive_group()
    end_cond.add_argument("--samples", type=int, default=200, help="total number of samples to generate", dest='samples')
    end_cond.add_argument("--desired-coverage", type=float, help="samples are genereted until the desired coverage is reached or --rounds is completed. Cannot be used with --samples", dest='descoverage')
    parser.add_argument("--rounds", type=int, default=10, help="number of rounds for sample generation", dest='rounds')
    parser.add_argument("--samples-per-round", type=int, default=50, help="number of samples generated per round if --desired-coverage is set", dest='spr')
    parser.add_argument("--extra-samples", action='store_true', help="Each round more samples are generated and the best are selected", dest='generateMoreSamples')
        
    parser.add_argument("--weight-function", type=int, default=2, choices=range(1, 8), help="Function number between 1 and 7 for weight generation, used in strategies 1, 2, 3, and 4", dest='funcNumber')
    parser.add_argument("--no-sampling", action='store_true', help="runs step 5 only, computes the coverage of a provided .nsample file with --samples-file", dest='nosampling')
    parser.add_argument("--samples-file", type=str, default='', help="file with samples to compute the coverage for --no-sampling option. Shall have .nsamples extension", dest="externalsamplefile")
        
    parser.add_argument("--maxcov-file", type=str, default='', help="file with pregenerated list of satisfiable feature combinations for the step 5. Shall have .comb extension", dest="rescombfile")
    parser.add_argument("--no-maxcov", action='store_true', help="Compute only number of combinatons in samples, instead of coverage", dest='nocomb')
    parser.add_argument("--cov-approximate", action='store_true', help="Computes combinations and samples approximately", dest='apprx')
    parser.add_argument("--cov-delta", type=float, default=0.05, help="Delta for approximate computation of coverage", dest='delta')
    parser.add_argument("--cov-epsilon", type=float, default=0.05, help="Epsilon for approximate computation of coverage", dest='epsilon')
   
    parser.add_argument("--seed", type=int, default=None, help="random seed", dest="seed")
    parser.add_argument('inputfile', type=str, help='input file')
    args = parser.parse_args()
    if args.inputfile == '':
        parser.print_usage()
        sys.exit(1)
    if args.rounds <= 0:
        print("Number of rounds must be positive")
        sys.exit(1)
    if args.samples<= 0:
        print("Number of samples must be positive")
        sys.exit(1)
    if args.seed and args.seed<= 0:
        print("Random seed must be positive")
        sys.exit(1)
    if args.twise <=0:
        print("Twise must be positive")
        sys.exit(1)
    if args.rescombfile and not check_rescombfile(args.rescombfile, args.twise):
        print("--combinations-file have wrong size of feature combinations")
        sys.exit(1)
    if args.combfile and not check_combfile(args.combfile, args.twise, args.strategy):
        sys.exit(1)
    if args.delta <=0 or args.delta >=1 or args.epsilon <=0 or args.epsilon >=1 or args.pdelta <=0 or args.pdelta >=1 \
        or args.pepsilon <=0 or args.pepsilon >=1:
        print("Delta and epsilon shall be in range (0,1)")
        sys.exit(1)
    
    if args.nosampling and not args.externalsamplefile:
        print("--args.nosampling must be used with --samples-file")
        sys.exit(1)
        if args.externalsamplefile[-9:] != '.nsamples':
            print("--samples-file is expected to have '.nsamples' extension")
            sys.exit(1)
        #TODO verify --samples-file format
    
    if args.descoverage and  (args.descoverage<=0 or args.descoverage >=1):
        print("--desired-coverage shall be in range (0,1)")
        sys.exit(1)
    
    if not args.waps and not os.path.exists("../bin/cmsgen"):
        print("cmsgen in ../bin/ not found")
        sys.exit(1)
    elif args.waps and not os.path.exists("../bin/d4"):
        print("d4 in ../bin/ not found")
        sys.exit(1)
    
    if not os.path.exists(args.outputdir):
        os.makedirs(args.outputdir)
        
    if args.seed:
        np.random.seed(args.seed)
        random.seed(args.seed)
    
    Path(args.outputdir).mkdir(parents=True, exist_ok=True)
    run(args.inputfile, args.strategy, args.twise, args.samples, args.descoverage, args.spr, args.rounds, args.outputdir, args.outputfile1, args.outputfile2, args.nocomb, args.combfile, args.papprx, args.pdelta, args.pepsilon, args.funcNumber, args.rescombfile, args.nosampling, args.externalsamplefile, args.apprx, args.epsilon, args.delta, args.preprocess, args.waps, args.generateMoreSamples, args.seed)

if __name__== "__main__":
    main()
