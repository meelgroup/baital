# Baital

Baital is a sampler generator for configurable systems that generates a set of testing samples for large configurable systems with high t-wise coverage. The tool takes a set of constaints on features of the configurable system represented as a CNF formula in Dimacs format and provides a set of configurations of a specified size and computes their t-wise coverage. In addition, the tool incorporates novel approximation techniques for the computaion of t-wise coverage. Baital is based on our [FSE-20 Paper](https://www.comp.nus.edu.sg/~meel/Papers/fse20blm.pdf).   

## System Requirements

Linux OS with Python 3.6 or higher, pip3, and git.  
Tested on: Ubuntu 18.10, 20.04 and Debian 11.  

## Installation

1. Install additional libraries: `graphviz`, `libgmp-dev`, `libmpfr-dev`, and `libmpc-dev`.  
    - On Debian-based systems the command is `sudo apt install grahviz libgmp-dev libmpfr-dev libmpc-dev`  
2. Install additional python libraries.  
    - `pip3 install -r requirements.txt`  
3. Install [ApproxMC4](https://github.com/meelgroup/approxmc) (*).  
4. Install [d4](https://github.com/crillab/d4).  
5. Copy d4 binary to `src/bin/` folder and ensure execute permission.  

*Tested on revisions 30c6787 of approxmc and 641f915 of cryptominisat.  


## Benchmarks

Baital expects input files in Dimacs CNF format. [FeatureIDE](https://github.com/FeatureIDE/FeatureIDE/releases/) can be used to generate input files from configurable systems. Benchmarks can be found at [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4022395.svg)](https://doi.org/10.5281/zenodo.4022395) or at [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5883536.svg)](https://doi.org/10.5281/zenodo.5883536).

## Baital Description

Baital uses an adaptive weighted sampling for the test suite generation for configurable systems. Contrary to uniform sampling where all samples are taken uniformly, Baital sampling is performed in rounds: at the beginning of each round a probability distribution for sampling is set by assigning weights to each literal. [WAPS](https://github.com/meelgroup/waps) tool is used for sampling. The selection of weights for each round is controlled by one of the strategies. All strategies compute weights for each literal; the computation is based on parameters listed below.  
  1. Strategy 1: ratio between the number of combinations with a literal in the current sample set and the number of combinations with the literal allowed by constraints of the configurable system.
  2. Strategy 2: ratio between the number of combinations with a literal in the current sample set and choice of twise distinct elements in NVariables.
  3. Strategy 3: ratio between the number of samples the literal appears in the current sample set and the number of models involving the literal.
  4. Strategy 4: the number of samples the literal appears in the current sample set.
  5. Strategy 5: ratio between the approximate number of combinations with a literal in the current sample set and the number of combinations with the literal allowed by constraints of the configurable system.
  6. Strategy 6: ratio between the approximate number of combinations with a literal in the current sample set and choice of twise distinct elements in NVariables.

Baital performs 3 steps:
   1. Step 1: preprocessing. Used for strategies 1, 3, and 5. Has 3 options. The option is controlled with --strategy and --preprocess-approximate options
        (i) Lists the combinations of size <twise> allowed by cnf constraints (could take hours for twise=2, infeasible for large models for twise=3). Results could be reused at step 3. 
            Precomputed file can be provided with --preprocess-file option, expected to have .comb extension. Can be used for strategies 1 and 5.
        (ii) Lists the approximate number of combinations of size <twise> for each literal (Could take 1 hour for twise=2, several hours for twise=3, tens of hours for twise>3). 
            Precomputed file can be provided with --preprocess-file option, expected to have .acomb extension. Can be used for strategies 1 and 5. --preprocess-delta and --preprocess-epsilon set the PAC guarantees.
        (iii) Lists the number of models for each literal (independent of twise, computation could take 1-2 hours).  
            Precomputed file can be provided with --preprocess-file option, expected to have .count extension. Required for strategy 3.  
      Preprocessing results are stored in a file (.comb, .acomb, or .count extensions) and can be reused later.  
   2. Step 2: sampling. Generation of samples with high t-wise coverage. Samples are stored in <outputdir>/<outputfile> (default results/<cnf_filename>.samples). 
        --twise option provides a size of combinations to maximise coverage 
        --strategy defines how the weights are generated between rounds
        --samples number of samples to generate
        --rounds number of rounds for sample generation, weights are updated between rounds. Higher coverage is expected with large number of rounds, however each round requires update of dDNNF annotation that might be long.
        --weight-function a function transforming the ratios computed by strategies 1, 2, 5, and 6 into weights. Varying this parameter might affect the resulted coverage
   3. Step 3: computation of twise coverage. It computes a ratio between the number of distinct combinations in the sample set and the number of distinct feature combinations satisfying the constraints of the system. The latter number is obtained fron the results of Step 1.(i) or runs Step 1.(i)  (could take hours for twise=2, infeasible for large models for twise=3). Alternatively, both elements of the ratio can be computed approximately.  
        --cov-approximate forces approximate computation.  
        Precomputed file can be provided with --maxcov-file (expects .comb extension).   
        --no-maxcov computes only number of distinct combinations in the sample set.  

Each step can be executed separately. Options --preprocess-only, --preprocess-file, and --no-sampling control the execution. Execution of a single step can also be achieved by calling corresponding scripts: `cnf_combinations.py` for step 1, `sampling.py` for step 2, for step 3 elements of the ratio are computed with `sample_set_combinations.py` and `cnf_combinations.py`.  
        
## Running Baital

Run command `python3 baital.py <arguments>` from `src` folder. 

### Arguments

1. Required
    - *cnf_file*.cnf in dimacs format
    
2. Optional

| Argument | Type | Default value | Description | 
| -------- | ---- | ------------- | ----------- |
| --outputdir | str | "./results/" | Output directory |
| --outputfile | str | "" | Output file for samples, will be placed in outputdir, default <cnf_filename>.samples |
| --twise | int | 2 | t value for t-wise coverage |
|-------- | ---- | ------------- | ----------- | 
| --preprocess-file | str | "" | Precomputed file for skipping preprocessing step. Shall have .comb, or .acomb, or .count extension |
| --preprocess-only |  |  | Only perform preprocessing |
| --preprocess-approximate | | | Approximate computation of preprocessing |
| --preprocess-delta | float | 0.25 | Delta for approximate counting at preprocessing. Unused if not --preprocess-approximate | 
| --preprocess-epsilon | float | 0.25 | Epsilon for approximate counting at preprocessing. Unused if not --preprocess-approximate | 
|-------- | ---- | ------------- | ----------- | 
| --strategy | int | 4 | Weight generation strategy |
| --rounds | int | 10 | Number of rounds for sample generation | 
| --samples | int | 500 | Total number of samples to generate | 
| --desired-coverage | float | | Samples are genereted until the desired coverage is reached or --rounds is completed. Cannot be used with --samples |
| --samples-per-round | int | 50| Number of samples generated per round if --desired-coverage is set |
| --weight-function | int | 2 | Function number between 1 and 7 for weight generation, used in strategies 1, 2, 5, and 6 |
|-------- | ---- | ------------- | ----------- | 
| --no-sampling | | | Skip sampling, use to compute the coverage of an existing test suite |
| --samples-file | str | | File with samples to compute the coverage for --no-sampling option. Shall have .samples extension | 
|-------- | ---- | ------------- | ----------- | 
| --maxcov-file | str | | File with pregenerated list of satisfiable feature combinations for the step 3. Shall have .comb extension | 
| --no-maxcov | | | Compute only the number of distinct combinations in a test suite instead of coverage |
| --cov-approximate | | | Compute the coverage approximately |
| --cov-delta | float | 0.05 | Delta for approximate computation of coverage. Unused if not --cov-approximate | 
| --cov-epsilon | float | 0.05 | Epsilon for approximate computation of coverage. Unused if not --cov-approximate | 
|-------- | ---- | ------------- | ----------- | 
| --seed | int | | random seed |
|-------- | ---- | ------------- | ----------- | 



## Input and Output Data

We assume that features are numbered from 1 to nFeatures. Constraints of configurable system are expected in Dimacs CNF format.   

Outputs are located in --outputdir (*./results/* by default). Output file contains the list of generated samples. Each line contains sample index, comma, and a list of space- separated literals. Positive literals correspond to selected features and negative to non-selected. For example, line `2, 1 -2 3` corresponds to a second sample in which variables 1 and 3 are True (selected) and variable 2 is False (non-selected). This format is expected for --samples-file option wiht --no-sampling. *Outputfile.txt* contains the number of combinations in the generated samples and the t-wise coverage if computed.  

Preprocessing can output the following types of files that can be reused with --preprocess-file or --maxcov-file (only .comb file) options:  
1. *cnf_file*_*x*.comb files where *x* in [1, *twise*] contain lists of feature combinations of size *x* that are satisfiable by the input cnf formula. Each line contains a space-separated satisfiable combination of literals.  
2. *cnf_file*_*x*.acomb file contains a list of approximations of the number of feature combinations of size *x* involving a literal for each literal. Each line contains a literal and a number of combinations.  
3. *cnf_file*.count file contains a list of models involving a literal for each literal. Each line contains a literal and a number of models.  

Last lines of the console output contain the following information:
1. Time taken by each step and total time.  
2. (Approximate) number of feature combinations in the sample set.  
3. (Approximate) coverage (skipped if --no-maxcov selected).  



### Note on execution time

Preprocessing step could take large time depending on the type of preprocessing, *twise*, and the number of variables. Several hours are required for exact computation for `twise=2`. 
For large benchmarks and `twise >=3` approximate methods shall be used: for preprocessing --preprocess-approximate option; for sampling - strategies 3, 4, 5, or 6; for computation of coverage --cov-approximate.


### Citing Us

If you use our tool, please cite us with the following bibtex:

```
@inproceedings{BLM20,
  title={Baital: An Adaptive Weighted Sampling Approach for Improved t-wise Coverage},
  author={Baranov, Eduard and Legay, Axel and Meel, Kuldeep S},
  booktitle={Proc. 28th European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
  year={2020}
}
```
```
@inproceedings{BCLMV22,
  title={A Scalable t-wise Coverage Estimator},
  author={Baranov, Eduard and Chakraborty, Sourav and Legay, Axel and Meel, Kuldeep S and Variyam, Vinodchandran N.},
  booktitle={ICSE2022},
  year={2022}
}
```
