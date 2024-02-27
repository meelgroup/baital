# /***********[baital.py]
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

import argparse
import shutil
import sys
import cnf_combinations
import sampling
import sample_set_combinations
import os
import math
import numpy as np
import time
import textwrap
import utils
import random
from pathlib import Path

#Preprocessing step. Ingnored for strategies 2, 4, and 5
def runPreprocess(inputfile, twise, outputdir, benchmarkName, strategy, preprocessonly, isApprox, epsilon, delta):
    if (strategy == 1 or strategy == 3 or preprocessonly):
        if isApprox:
            cnf_combinations.run(inputfile, twise, 3, outputdir, epsilon, delta)
            combinationsFile = os.path.join(outputdir, benchmarkName + '_' + str(twise) + '.acomb')
        else:
            cnf_combinations.run(inputfile, twise, 1, outputdir, epsilon, delta)
            combinationsFile = os.path.join(outputdir, benchmarkName + '_' + str(twise) + '.comb')
    else: #no need for preprocessing
        combinationsFile = ''
    return combinationsFile

#MaxCov computation
def computeMaxCov(dimacscnf, twise, rescombfile, combinationsFile, outputdir, apprx, epsilon, delta):
    if rescombfile:
        return utils.getCoverageFromCombFile(rescombfile)
    elif combinationsFile[-5:] == '.comb':  # reuse preprocessing results
        return utils.getCoverageFromCombFile(combinationsFile)
    elif apprx:
        return cnf_combinations.run(dimacscnf, twise, 2, '', epsilon, delta)
    else:
        return cnf_combinations.run(dimacscnf, twise, 1, outputdir, epsilon, delta)


def run(dimacscnf, strategy, twise, samples, descoverage, spr, rounds, outputdir, outputfile, nocomb, combfile, papprx, pdelta, pepsilon, funcNumber, rescombfile, nosampling, outersamplefile, apprx, epsilon, delta, preprocessonly, waps, useBestSamples):
    benchmarkName = os.path.basename(dimacscnf).split('.')[0]
    if not outputfile:
        outputfile = benchmarkName + '.samples'
    samplesfile = os.path.join(outputdir, outputfile)
    
    starttime = time.time()
    
    if combfile:
        combinationsFile = combfile
        ptime = -1
    else:
        pstart = time.time()
        combinationsFile = runPreprocess(dimacscnf, twise, outputdir, benchmarkName, strategy, preprocessonly, papprx, pepsilon, pdelta)
        ptime = time.time() - pstart if combinationsFile != '' else -1

    if preprocessonly: #exit after preprocessing
        print("Preprocessing time " + str(ptime))
        return
        
    if not nosampling:
        sstart = time.time()
        sampling.run(samples, rounds, dimacscnf, samplesfile, twise, strategy, descoverage=descoverage, samplesperround=spr, combinationsFile=combinationsFile, funcNumber=funcNumber, waps=waps, useBestSamples=useBestSamples)
        stime = time.time() -sstart
    else:
        samplesfile = outersamplefile
        stime = -1

    cstart = time.time()
    comb = sample_set_combinations.run(samplesfile, twise, apprx, epsilon, delta)    
    if not nocomb:
        maxcov = computeMaxCov(dimacscnf, twise, rescombfile, combinationsFile, outputdir, apprx, epsilon, delta)
        coverage = comb / maxcov
        print("Coverage " + str(coverage))
    else:
        coverage = None
    ctime = time.time() - cstart
        
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\x1b[1;34;40m" + "Results" + "\x1b[0m")
    totaltime = time.time() - starttime
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
 
# quick check of combfile 
def check_combfile(combfile, twise, strategy):
    if strategy == 2 or strategy == 4 or strategy == 5:
        print("Warning: --preprocess-file not used for strategy " + str(strategy))
        return True
    if not os.path.exists(combfile):
        print("File " + combfile + " not found.")
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
The tool executes 3 steps:
    Step 1: preprocessing. Used for strategies 1, and 3. Has 2 options that are controlled by --strategy and --preprocess-approximate options
        (i) Lists the combinations of size <twise> allowed by cnf constraints (Could take hours for twise=2, infeasible for large models for twise=3). Results could be reused at step 3. 
            Precomputed file can be provided with --preprocess-file option, expected to have .comb extension.
        (ii) Lists the approximate number of combinations of size <twise> for each literal (Could take 1 hour for twise=2, several hours for twise=3, tens of hours for twise>3). 
            Precomputed file can be provided with --preprocess-file option, expected to have .acomb extension. --preprocess-delta and --preprocess-epsilon set the PAC guarantees.
    Step 2: sampling. Generation of samples with high twise coverage. Samples are stored in <outputdir>/<outputfile> (default results/<cnf_filename>.samples). 
        --twise option provides a size of combinations to maximise coverage 
        --strategy defines how the weights are generated between rounds
        --samples number of samples to generate
        --rounds number of rounds for sample generation, weights are updated between rounds. Higher coverage is expected with large number of rounds, however each round requires update of dDNNF annotation that might be long.
        --weight-function a function transforming the ratios computed by strategies 1, 2, 3, and 4 into weights. Varying this parameter might affect the resulted coverage
    Step 3: computation of twise coverage. 
        --approximate forces approximate computation. Non-approximate computation uses the result or runs Step 1.(i). 
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
    parser.add_argument("--outputfile", type=str, default="", help="output file for samples, will be placed in outputdir, default <cnf_filename>.samples", dest='outputfile')
    parser.add_argument("--twise", type=int, default=2, help="t value for t-wise coverage, default 2", dest='twise')
    parser.add_argument("--waps", action='store_true', help="use an old version with waps instead of cmsgen", dest='waps')
        
    parser.add_argument("--preprocess-file", type=str, default='', help="precomputed file for skipping preprocessing step. Shall have .comb, or .acomb extension. See help for details", dest="combfile")
    parser.add_argument("--preprocess-delta", type=float, default=0.25, help="delta for approximate counting at preprocessing, default 0.25", dest='pdelta')
    parser.add_argument("--preprocess-epsilon", type=float, default=0.25, help="epsilon for approximate counting at preprocessing, default 0.25", dest='pepsilon')
    parser.add_argument("--preprocess-approximate", action='store_true', help="approximate computation of preprocess", dest='papprx')
    parser.add_argument("--preprocess-only", action='store_true', help="Only perform preprocessing", dest='preprocess')
    
    parser.add_argument("--strategy", type=int, default=5, choices=range(1, 6), help="weight generation strategy, default 5. See help for description", dest='strategy')
    end_cond = parser.add_mutually_exclusive_group()
    end_cond.add_argument("--samples", type=int, default=500, help="total number of samples to generate", dest='samples')
    end_cond.add_argument("--desired-coverage", type=float, help="samples are genereted until the desired coverage is reached or --rounds is completed. Cannot be used with --samples", dest='descoverage')
    parser.add_argument("--rounds", type=int, default=10, help="number of rounds for sample generation", dest='rounds')
    parser.add_argument("--samples-per-round", type=int, default=50, help="number of samples generated per round if --desired-coverage is set", dest='spr')
    parser.add_argument("--extra-samples", action='store_true', help="Each round more samples are generated and the best are selected", dest='generateMoreSamples')
        
    parser.add_argument("--weight-function", type=int, default=2, choices=range(1, 8), help="Function number between 1 and 7 for weight generation, used in strategies 1, 2, 3, and 4", dest='funcNumber')
    parser.add_argument("--no-sampling", action='store_true', help="skip step 2, computes only the coverage of a provided .sample file with --samples-file", dest='nosampling')
    parser.add_argument("--samples-file", type=str, default='', help="file with samples to compute the coverage for --no-sampling option. Shall have .samples extension", dest="externalsamplefile")
        
    parser.add_argument("--maxcov-file", type=str, default='', help="file with pregenerated list of satisfiable feature combinations for the step 3. Shall have .comb extension", dest="rescombfile")
    parser.add_argument("--no-maxcov", action='store_true', help="Compute only number of combinatons in samples, instead of coverage", dest='nocomb')
    parser.add_argument("--cov-approximate", action='store_true', help="Computes combinations and samples approximately", dest='apprx')
    parser.add_argument("--cov-delta", type=float, default=0.05, help="Delta for approximate computation of coverage", dest='delta')
    parser.add_argument("--cov-epsilon", type=float, default=0.05, help="Epsilon for approximate computation of coverage", dest='epsilon')
   
    parser.add_argument("--seed", type=int, default=None, help="random seed", dest="seed")
    parser.add_argument('DIMACSCNF', type=str, help='input cnf file in dimacs format')
    args = parser.parse_args()
    if args.DIMACSCNF == '':
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
        if args.externalsamplefile[-8:] != '.samples':
            print("--samples-file is expected to have '.samples' extension")
            sys.exit(1)
        #TODO verify --samples-file format
    
    if args.descoverage and  (args.descoverage<=0 or args.descoverage >=1):
        print("--desired-coverage shall be in range (0,1)")
        sys.exit(1)
    
    if not args.waps and shutil.which('cmsgen') is None:
        print("cmsgen is not found")
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
    run(args.DIMACSCNF, args.strategy, args.twise, args.samples, args.descoverage, args.spr, args.rounds, args.outputdir, args.outputfile, args.nocomb, args.combfile, args.papprx, args.pdelta, args.pepsilon, args.funcNumber, args.rescombfile, args.nosampling, args.externalsamplefile, args.apprx, args.epsilon, args.delta, args.preprocess, args.waps, args.generateMoreSamples)

if __name__== "__main__":
    main()
