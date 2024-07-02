## /***********[sample_set_coverage.py]
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
import math
import utils
import sys


def check_coverage(samplefile, size):
    trie = {}
    count = [0]
    with open(samplefile, "r") as f:
        for line in f:
            s = list(map(int, line.strip().split(',')[1].strip().split(' ')))
            utils.getTuples_rec(s, size, trie, count, [])
    print("Number of combinations " + str(count[0]))
    return count[0]


def approximate_coverage(samplefile, size, epsilon, delta):
    nBoxes = math.ceil(3 * (2**size) * math.log(2 / delta) / (epsilon*epsilon))
    with open(samplefile, "r") as f:
        nvars = len(f.readline().strip().split(',')[1].strip().split(' '))     
    boxes = utils.genRandomBoxes(nvars, size, nBoxes)
    nBoxesFinal = len(boxes)
    with open(samplefile, "r") as f:
        for line in f:
            s = list(map(int, line.strip().split(',')[1].strip().split(' ')))
            boxes = utils.updateBoxesCoverage(boxes, size, s)
    coveredBoxes = nBoxesFinal - len(boxes)
    if nBoxesFinal < nBoxes:
        countRes = coveredBoxes
    else:
        countRes = int(utils.cnk(nvars, size) * coveredBoxes *(2**size) / nBoxes)
    print("Approximate number of combinations " + str(countRes))
    return countRes

def run(samples, twise, isApprox, epsilon, delta):
    start = time.time()
    if isApprox:
        res = approximate_coverage(samples, twise, epsilon, delta)
    else:
        res = check_coverage(samples, twise)
    print("Time taken for combination counting: " + str(time.time() - start))
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
    if args.samples == '':
        parser.print_usage()
        sys.exit(1)
    if args.twise <= 0:
        parser.print_usage()
        sys.exit(1)
        
    if args.seed:
        random.seed(args.seed)

    run(args.samples, args.twise, args.apprx, args.epsilon, args.delta)

    
