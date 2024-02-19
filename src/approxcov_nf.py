## /***********[approxcov_nf.py]
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

import time
import argparse
import random
import os
import math
import sys
import utils

### Compute exact coverage 
# File with samples and size of combinations (twise)
def check_coverage_nf(samplefile, size):
    trie = {}
    count = [0]
    with open(samplefile, "r") as f:
        lines = f.readlines()
        for line in lines[1:]:
            s= line.strip().split(',')[1].strip().split(' ')
            s_upd = list(map(lambda x: 'v'+str(x[0])+'.'+x[1], zip(range(len(s)), s)))
            utils.getTuples_rec(s_upd, size, trie, count, [])
    print("Number of combinations " + str(count[0]))
    return count[0]

### Compute approximate coverage

# Compute matrix where matrix[i][j] is the number of combinations of size j-1 with i-1 variables
def compute_total_n(n, k, varsizes):
    matrix = [[0 for _ in range(k)] for _ in range(n)]
    sum =0
    for i in range(n):
        sum += varsizes[i]
        matrix[i][0] = sum
    mult = 1
    for i in range(k):
        mult *= varsizes[i]
        matrix[i][i] = mult
    for i in range(1,n):
        for j in range(1,k):
            if j<i:
                matrix[i][j] = matrix[i-1][j] + matrix[i-1][j-1]*varsizes[i]
    return matrix

# Generates a set of boxes (uniformly distributed), and check which are covered by the samples in samplefile. The approximation is the proportion of the covered boxes.  
def approximate_coverage_nf(samplefile, size, epsilon, delta):
    with open(samplefile, "r") as f:
        lines = f.readlines()
        varsizes = list(map(lambda x : int(x.strip()), lines[0].split(' ')))
        nvars = len(varsizes)     
        matrix = compute_total_n(nvars, size, varsizes)
        total_comb = matrix[nvars-1][size-1]
        choice_comb = utils.cnk(nvars, size)
        nBoxes = math.ceil(3 * math.log(2 / delta) * total_comb / (epsilon*epsilon) / choice_comb)
        if nBoxes > choice_comb*(2**size):                        # If the number of boxes is too large, switch to exact method 
            print("Too many boxes " + str(nBoxes) + '. Using exact computation instead.')
            return check_coverage_nf(samplefile, size)
        boxes = utils.genRandomBoxes_nf(nvars, size, varsizes, nBoxes, matrix)
        nBoxesFinal = len(boxes)
        for line in lines[1:]:
            s = list(map(lambda x : int(x.strip()), line.strip().split(',')[1].strip().split(' ')))
            boxes = utils.updateBoxesCoverage_nf(boxes, size, s)
        
        coveredBoxes = nBoxesFinal - len(boxes)
        if nBoxesFinal < nBoxes:
            countRes = coveredBoxes
        else:
            countRes = int(coveredBoxes *total_comb / nBoxes)
        print("Approximate number of combinations " + str(countRes))
    return countRes

def run(samples, twise, isApprox, epsilon, delta):
    start = time.time()
    if isApprox:
        res = approximate_coverage_nf(samples, twise, epsilon, delta)
    else:
        res = check_coverage_nf(samples, twise)
    print("Time taken: " + str(time.time() - start))
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('samples', type=str, default="", help='Input file with samples')
    parser.add_argument("--twise", type=int, help='The size of combinations', required=True)
    parser.add_argument("--approximate", action='store_true', help="Computes combinations approximately", dest='apprx')
    parser.add_argument("--delta", type=float, default=0.05, help="Delta for approximate counting", dest='delta')
    parser.add_argument("--epsilon", type=float, default=0.05, help="Epsilon for approximate counting", dest='epsilon')
    parser.add_argument("--seed", type=int, help="Random seed. Unused if approximate is not selected", dest='seed')
    
    args = parser.parse_args()
    if args.seed:
        random.seed(args.seed)
    if args.samples == '':
        parser.print_usage()
        sys.exit(1)
    if args.twise <= 0:
        parser.print_usage()
        sys.exit(1)

    run(args.samples, args.twise, args.apprx, args.epsilon, args.delta)
    
