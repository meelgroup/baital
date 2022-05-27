# /***********[weightFunctions.py]
# Copyright (c) 2020 Eduard Baranov, Axel Legay, Kuldeep Meel
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

import math

MAXWEIGHT=0.99
MINWEIGHT = 1-MAXWEIGHT
MAXCOEFF = MAXWEIGHT-0.5

def removeApproxError(i):
    if i > MAXWEIGHT:
        return MAXWEIGHT
    if i < MINWEIGHT:
        return MINWEIGHT
    return i

def weightFormula1(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1
    return removeApproxError(0.5 - (MAXCOEFF * (posN /total[i] - negN /total[-i])))

def weightFormula2(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1
    val = posN /total[i] - negN /total[-i]
    if val >= 0:
        return removeApproxError(0.5 - (MAXCOEFF * math.sqrt(val)))
    else:
        return removeApproxError(0.5 + (MAXCOEFF * math.sqrt(-val)))

def weightFormula3(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1
    val = posN /total[i] - negN /total[-i]
    if val >= 0:
        return removeApproxError(0.5 - (MAXCOEFF * val*val))
    else:
        return removeApproxError(0.5 + (MAXCOEFF * val*val))

def weightFormula4(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1
    val = posN /total[i] - negN /total[-i]
    if val == 0:
        return 0.5    
    if val > 0:
        return removeApproxError(0.5 - (MAXCOEFF * math.e *(math.pow(math.e, -1 /val))))
    else:
        return removeApproxError(0.5 + (MAXCOEFF * math.e *(math.pow(math.e, 1 /val))))
    
def weightFormula5(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1    
    val = posN /total[i] - negN /total[-i]
    return removeApproxError(0.5 - math.tanh(3*val) /2)

def weightFormula6(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1    
    val = posN /total[i] - negN /total[-i]
    if val >= 0:
        return removeApproxError(0.5 - (MAXCOEFF * math.pow(val, 1/3)))
    else:
        return removeApproxError(0.5 + (MAXCOEFF * math.pow(-val, 1/3)))

def weightFormula7(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1
    if posN /total[i] + negN /total[-i] == 0:
        return 0.5
    return removeApproxError(0.5 - (MAXCOEFF * (posN /total[i] - negN /total[-i]) / (posN /total[i] + negN /total[-i])))
    
def weightFormulatStrategy3(posN, negN, total, i):
    if total[i] == 0:
        return 0
    if total[-i] == 0:
        return 1
    if posN == 0 and negN == 0 : 
        return 0.5
    posP = posN / (posN + negN) 
    negP = math.log(total[i]) / (math.log(total[i]) + math.log(total[-i]))
    val = (posP -negP)
    if val >= 0:
        return (0.5 - (MAXCOEFF * math.sqrt(val)))
    else:
        return 0.5 + (MAXCOEFF *math.sqrt(-val))
 
def weightFormulaStrategy4(posN, negN):
    if posN + negN ==0:
        return 0.5
    else: 
        return 0.5 - MAXCOEFF* ((posN -negN) / (posN + negN)) 

#dictionnary of functions for computing weights
functionsDict = {1: weightFormula1, 2: weightFormula2, 3 : weightFormula3, 4: weightFormula4, 5: weightFormula5, 6: weightFormula6, 7: weightFormula7}


def computeWeight(strategy, funcNumber, posN, negN, total, i):
    if strategy == 3:
        return weightFormulatStrategy3(posN, negN, total, i)
    if strategy == 4:
        return weightFormulaStrategy4(posN, negN)
    return functionsDict[funcNumber](posN, negN, total, i)

def generateWeights(count, nvars, strategy, maxComb, weightFile, roundNb, funcNumber):
    f = open(weightFile + str(roundNb)  + '.txt', 'w')
    for i in range(nvars):
        weight = computeWeight(strategy, funcNumber, count[i+1], count[-i-1], maxComb, i+1)
        f.write(str(i+1) + ',' + str(weight) + '\n')
    f.close()
