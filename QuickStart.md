# Baital Quick Start Guide

This document provides a set of examples for the utilization of Baital. In the commands we assume that the current directory is /path/to/baital/src/.  
Note that the output values might differ on your system from the ones illustrated here: execution time depends on hardware and current PC load and the generated samples depend on random. For reproducibility of sampling results, we provide a `--seed` option that sets the random seed.  

### Basic Commands

The most basic command that generates a set of samples from test.cnf (assuming it is located in the same folder) file is 

```
python3 baital.py test.cnf
```

For other options, this command would use default values. test.cnf is expected to be in Dimacs CNF format. Console output would show the execution progress and results statistics in the end. The example of output is shown below.

```
Round 1 started...
Time taken by round 1 :0.005104541778564453
Round 1 finished...
Round 2 started...
Time taken by round 2 :0.0020418167114257812
Round 2 finished...
Round 3 started...
Time taken by round 3 :0.0020897388458251953
Round 3 finished...
Round 4 started...
Time taken by round 4 :0.0020475387573242188
Round 4 finished...
Round 5 started...
Time taken by round 5 :0.0021545886993408203
Round 5 finished...
Round 6 started...
Time taken by round 6 :0.002264738082885742
Round 6 finished...
Round 7 started...
Time taken by round 7 :0.0019304752349853516
Round 7 finished...
Round 8 started...
Time taken by round 8 :0.0023093223571777344
Round 8 finished...
Round 9 started...
Time taken by round 9 :0.0022728443145751953
Round 9 finished...
Round 10 started...
Time taken by round 10 :0.0017478466033935547
Round 10 finished...
Total time taken by sampling: 0.024941205978393555
Number of combinations 402
Time taken for combination counting: 0.011896133422851562
Generating 1-wise combinations
Total combinations to check 34
5% done
10% done
15% done
20% done
25% done
30% done
35% done
40% done
45% done
50% done
55% done
60% done
65% done
70% done
75% done
80% done
85% done
90% done
95% done
Time to get satisfiable combinations 0.0027642250061035156
Generating 2-wise combinations
Total combinations to check 451
5% done
10% done
15% done
20% done
25% done
30% done
35% done
40% done
45% done
50% done
55% done
60% done
65% done
70% done
75% done
80% done
85% done
90% done
95% done
Time to get satisfiable combinations 0.02181100845336914
Total number of combinations is 402
Total time: 0.024678945541381836
Coverage 1.0
----------------------------------------------------------------------------------------------------------------------------------------------------------
Results
Sampling time 0.025266647338867188
Coverage time 0.03690648078918457
Total time 0.06219005584716797
(Approximate) number of combinations 402
(Approximate) 2-wise coverage 1.0
```

By default, there are 10 rounds for sampling (weight distribution for samples is changed between the rounds), and the output contains the execution time for each round. Then it computes the number of configurations and outputs the result and the time taken. Finally, it computes the total number of combinations (progressively from 1-wise to t-wise) and outputs the total number and the time spent. The results section of the output lists major elements: time spent on each part of the execution, the total number of combinations and the resulted coverage.

The command execution generates 3 files in the results folder: test_1.comb, test_2.comb, and test.samples. The first two files list all 1- and 2-wise combinations (and can be reused for the following samplings from test.cnf), and the last file lists selected samples. Each line contains a sample number (starting from 0) and a list of variables either positive (variable is True/ feature is selected) or negative (variable is False/ feature not selected). For example, the first line could be `0,-1 2 -3 -4 -5 -6 -7 8 -9 -10 -11 12 -13 14 -15 -16 17` with selected features 2, 8, 12, 14, and 17.

### Customizing the Execution

#### Number of Samples and Rounds

Default 500 samples are too many for the small example such as test.cnf. To reduce the number of generated samples and the number of rounds, their values can be set up as shown in the following command:

```
python3 baital.py test.cnf --rounds 4 --samples 20
...
Results
Sampling time 0.007356166839599609
Coverage time 0.030012845993041992
Total time 0.037380218505859375
(Approximate) number of combinations 401
(Approximate) 2-wise coverage 0.9975124378109452
```
The test.samples file would contain only 20 lines with samples.

#### Reusing Precomputed Combinations

If the same cnf file is used multiple times for sampling, it is possible to reuse lists of combinations:  
```
python3 baital.py test.cnf --rounds 4 --samples 20 --preprocess-file results/test_2.comb
...
Results
Sampling time 0.006505489349365234
Coverage time 0.0007245540618896484
Total time 0.007239580154418945
(Approximate) number of combinations 402
(Approximate) 2-wise coverage 1.0
```
The comb file must be computed for the correct value of t (in this example test_2.comb can be used but not test_1.comb).   

#### Skipping Total Number of Combinations

Alternatively, if only the number of covered combinations is required, but not the coverage, the computation can be skipped with:  

```
python3 baital.py test.cnf --rounds 4 --samples 20 --no-maxcov
...
Results
Sampling time 0.006346225738525391
Coverage time 0.0006291866302490234
Total time 0.0069904327392578125
(Approximate) number of combinations 393
```

#### Counting Combinations for an Existing Set of Samples

If the set of samples has been computed (by Baital or other tools), Baital can be used to compute the coverage. .samples file should have the same structure as the Baital output.  
```
python3 baital.py test.cnf --rounds 4 --samples 20 --no-sampling --samples-file results/test.samples
...
Results
Coverage time 0.019655466079711914
Total time 0.01966571807861328
(Approximate) number of combinations 393
(Approximate) 2-wise coverage 0.9776119402985075
```

#### Using Approximate Computation of Coverage

To compute the approximate value of coverage the following options are used:  
```
python3 baital.py test.cnf --rounds 4 --samples 20 --cov-approximate
...
Results
Sampling time 0.005902767181396484
Coverage time 0.028800010681152344
Total time 0.03472495079040527
(Approximate) number of combinations 402
(Approximate) 2-wise coverage 1.0
```
Changing approximation parameters with `--epsilon` and `--delta` affects the accuracy of the approximation and its performance.  

#### Using Different Strategies for Sampling

Baital implements several versions of the distribution update between rounds. Description of different strategies can be found in the readme file or with `--help` option.  
```
python3 baital.py test.cnf --rounds 4 --samples 20 --strategy 1
...
Results
Preprocessing time 0.022457599639892578
Sampling time 0.00822305679321289
Coverage time 0.0014634132385253906
Total time 0.032155752182006836
(Approximate) number of combinations 402
(Approximate) 2-wise coverage 1.0
```

Note that strategies 1 and 3 have an additional execution step called preprocessing. During this step the total number of combinations for each variable is computed. In the case of exact computation, this is the same computation as for the total number of combinations and the same file is generated. Therefore, this computation is performed a single time and the same file can be reused for preprocessing and the total number of combinations. In the following command, there is no preprocessing time:

```
python3 baital.py test.cnf --rounds 4 --samples 20 --strategy 1 --preprocess-file results/test_2.comb
...
Results
Sampling time 0.007114410400390625
Coverage time 0.0006983280181884766
Total time 0.007820606231689453
(Approximate) number of combinations 402
(Approximate) 2-wise coverage 1.0
```

Alternatively, the preprocessing can be done with approximate computations.

```
python3 baital.py test.cnf --rounds 4 --samples 20 --strategy 1 --preprocess-approximate
...
Results
Preprocessing time 0.06786727905273438
Sampling time 0.006800413131713867
Coverage time 0.019350290298461914
Total time 0.09402632713317871
(Approximate) number of combinations 402
(Approximate) 2-wise coverage 1.0
```

Approximate preprocessing generates the file results/test_2.acomb. This file can be reused to skip the preprocessing but not for the coverage computation. Approximate preprocessing is expected to be used in combination with either `--cov-approximate` or `no-maxcov` when the total number of combinations computation is too long.  

Please check the section regarding performance.

#### 3-wise, 4-wise ... Sampling

`--twise` option sets the size of combinations.  
```
python3 baital.py test.cnf --rounds 4 --samples 20 --twise 3
...
Results
Sampling time 0.005340099334716797
Coverage time 0.1764087677001953
Total time 0.18175888061523438
(Approximate) number of combinations 2925
(Approximate) 3-wise coverage 0.9737017310252996
```

Please check the section regarding performance.

#### Using WAPS sampling

WAPS sampling shows worse performance than CMSGen and usually achieves worse coverage.  
```
python3 baital.py test.cnf --rounds 4 --samples 20 --waps
...
Results
Sampling time 0.07047700881958008
Coverage time 0.02375483512878418
Total time 0.09425044059753418
(Approximate) number of combinations 402
(Approximate) 2-wise coverage 1.0
```
Note the sampling time difference: ~0.007 with CMSGen vs ~0.07 with WAPS.  

WAPS can be used to perform uniform sampling: WAPS provides stronger guarantees for sampling with a given distribution than CMSGen. The number of rounds must be set to 1 for uniform sampling.  
```
python3 baital.py test.cnf --rounds 4 --samples 20 --waps
...
Results
Sampling time 0.04872012138366699
Coverage time 0.020328044891357422
Total time 0.06905913352966309
(Approximate) number of combinations 401
(Approximate) 2-wise coverage 0.9975124378109452
```


### Multi-valued Features

A different entry script is used for multi-valued features. 
```
python3 baital_nf.py test_nf.smt
...
Sampling time 0.030504226684570312
Coverage time 33.71574330329895
Total time 33.843066453933716
(Approximate) number of combinations 1624
(Approximate) 2-wise coverage 1.0
```

The input file should contain constraints with QF_BV logic in SMTLIB2 format. The first three lines must be comments with information containing the list of features and their possible values. Check the readme and provided benchmarks for more details.  

The output contains 4 files: two .comb files as in binary features case and two files test_nf.nsamples and test_nf.rsamples. Both files contain a list of samples in two different formats. The first one has lines of the format: `0, 1 1 0 0 0 1 1 1 0 1 1 0 1 1 1 0 1 0 1 1 0 0 0 1 1 0 1 1 0 0 0` where the first number is sample number and for the rest the i^th number is the value of the i^th variable assuming that it can take values from 0 to n. .rsamples file contain the same set of samples but showing the original feature name and its value: `0, benchmark_7=1 V0=1 V1=0 V2=0 V3=0 V4=1 V5=1 V6=1 V7=0 V8=1 V9=1 V10=0 V11=1 V12=1 V13=1 V14=0 V15=1 V16=0 V17=1 V18=1 V19=0 V20=0 V21=0 V22=1 V24=1 V25=0 V26=1 V27=1 V28=0 V29=0 MV23=0`. Comment lines in the input file contain the information to recover feature names and original options for values.  

The options for this script are similar to the ones for baital.py. 


### Notes on Performance

The complexity of feature models or configurable systems, in particular, the number of features/variables strongly affects the performance of the tool.  
* Among the strategies, Strategy 5 is the fastest, while Strategies 1 and 3 are the slowest. From our experiments, Strategies 1 and 3 result in the best coverage, while Strategies 2 and 4 achieve the worst coverage.  
* The computation of the total number of combinations is the slowest operation, therefore its results must be reused whenever possible.  
* WAPS sampling is usually slower than CMSGen.  
* For 4-wise coverage (and 3-wise with more than 300 variables) approximate computations should be used: choose options `preprocess-approximate`, `cov-approximate`, and strategies 3, 4, or 5.
* Depending on the strategy, the number of rounds might significantly affect sampling time.  
