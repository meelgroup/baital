# Baital

Baital is a test suite generator for large configurable systems with high t-wise coverage. The tool takes a set of constraints on features of the configurable system and outputs a set of configurations of a specified size and computes their t-wise coverage. In addition, the tool incorporates novel approximation techniques for the computation of t-wise coverage.  

## (New) Support for Multi-valued/Numerical Features  

In the latest version we have added the support for the multi-valued or numerical features. `baital_nf.py` is the entry point, all optional arguments are identical to the `baital.py`. The description of the input format is provided [below](#mv-format) and its workflow [here](#mv-description).  

## System Requirements

Linux OS with Python 3.6 or higher, pip3, and git.  
Tested on: Ubuntu, Debian, and CentOS.  

## Installation

Detailed instructions can be found in Install.md.  

1. Install libraries required by additional tools: `build-essential` `cmake` `graphviz` `libgmp-dev` `libmpfr-dev` `libmpc-dev` `zlib1g-dev` `libboost-program-options-dev` `libboost-serialization-dev` `libgmp3-dev`.  
    - `sudo apt install` on Debian-based systems 
2. Install additional python libraries.  
    - `pip3 install -r requirements.txt`  
3. Install [ApproxMC4](https://github.com/meelgroup/approxmc) (*).  
4. Install [Cmsgen](https://github.com/meelgroup/cmsgen) with -DSTATICCOMPILE=ON flag.  
5. (Optional) Install [d4](https://github.com/crillab/d4) and copy d4 binary to `bin/` folder and ensure execute permission. (Required only for WAPS sampling).  
6. Install z3: `sudo apt install z3` (Required for Multi-valued/Numerical Features).  

*We do not yet support python interface of the tools, but require their binaries installed.  

### Docker image

An alternative for installation is to build a docker image with:  
`docker build ./ -t baital`  
  
In order to perform sampling using docker, container inputs and outputs has to be passed via volumes. The run command shall be:  
`docker run -v /path/to/inputfile:/baital/src/inputfile -v /path/to/output/results/:/baital/src/results/ baital baital.py inputfile`  
Other arguments can be passed as usual; note that all files in the arguments must be injected with volumes.   


## Benchmarks

For the binary features, Baital expects input files in Dimacs CNF format. [FeatureIDE](https://github.com/FeatureIDE/FeatureIDE/releases/) can be used to generate input files from configurable systems. For configurable systems with multi-valued/numerical features Baital expects constraints described in QF_BV logic. We also partially support Clafer-like format as input that is converted into QF_BV automatically. Benchmarks can be found in [this repository](https://github.com/edbaranov/feature-model-benchmarks) or at [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10220246.svg)](https://doi.org/10.5281/zenodo.10220246) or at [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5883536.svg)](https://doi.org/10.5281/zenodo.5883536).

## Baital Description

Baital uses an adaptive weighted sampling for the test suite generation for configurable systems. Contrary to uniform sampling where all samples are taken uniformly, Baital sampling is performed in rounds: at the beginning of each round a probability distribution for sampling is set by assigning weights to each literal. For an assigned set of weights two sampling tools are supported: [CMSGen](https://github.com/meelgroup/cmsgen) (default) and [WAPS](https://github.com/meelgroup/waps) with option --waps. Note that CMSGen is significantly faster and provides better coverage. The selection of weights for each round is controlled by one of the strategies. All strategies compute weights for each literal; the computation is based on parameters listed below.  
  - Strategy 1: ratio between the number of combinations with a literal in the current sample set and the number of combinations with the literal allowed by constraints of the configurable system.  
  - Strategy 2: ratio between the number of combinations with a literal in the current sample set and choice of twise distinct elements in NVariables.  
  - Strategy 3: ratio between the approximate number of combinations with a literal in the current sample set and the number of combinations with the literal allowed by constraints of the configurable system.  
  - Strategy 4: ratio between the approximate number of combinations with a literal in the current sample set and choice of twise distinct elements in NVariables.  
  - Strategy 5: the number of samples the literal appears in the current sample set.  

Baital performs 3 steps:  
- Step 1: Preprocessing. Used for strategies 1 and 3. Preprocessing results are stored in a file (.comb or .acomb extensions) and can be reused later. Has 2 options that are switched with --preprocess-approximate option:  
    * (i) Lists the combinations of size <twise> allowed by cnf constraints (could take hours for twise=2, infeasible for large models for twise=3). Results could be reused at step 3.
            Precomputed file can be provided with --preprocess-file option, expected to have .comb extension.  
    * (ii) Lists the approximate number of combinations of size <twise> for each literal (Could take 1 hour for twise=2, several hours for twise=3, tens of hours for twise>3). 
            Precomputed file can be provided with --preprocess-file option, expected to have .acomb extension. --preprocess-delta and --preprocess-epsilon set the PAC guarantees.  
- Step 2: Sampling. Generation of samples with high t-wise coverage. Samples are stored in <outputdir>/<outputfile> (default results/<cnf_filename>.samples).   
    * twise option provides a size of combinations to maximize coverage    
    * strategy defines how the weights are generated between rounds  
    * samples number of samples to generate  
    * rounds number of rounds for sample generation, weights are updated between rounds. Higher coverage is expected with large number of rounds, however each round requires additional computations that might affect performance.  
    * weight-function a function transforming the ratios computed by strategies 1, 2, 3, and 4 into weights. Varying this parameter might affect the resulted coverage  
- Step 3: Computation of twise coverage. It computes a ratio between the number of distinct combinations in the sample set and the number of distinct feature combinations satisfying the constraints of the system. The latter number is obtained from the results of Step 1.(i) or runs Step 1.(i)  (could take hours for twise=2, infeasible for large models for twise=3). Alternatively, both elements of the ratio can be computed approximately.
        --cov-approximate forces approximate computation.
        Precomputed file can be provided with --maxcov-file (expects .comb extension). 
        --no-maxcov computes only number of distinct combinations in the sample set.

Each step can be executed separately. Options --preprocess-only, --preprocess-file, and --no-sampling control the execution. Execution of a single step can also be achieved by calling corresponding scripts: `cnf_combinations.py` for step 1, `sampling.py` for step 2, for step 3 elements of the ratio are computed with `sample_set_combinations.py` and `cnf_combinations.py`.  

### Multi-valued/Numerical Features
<a id="mv-description"></a>
The sampling with multi-valued features is performed by converting them into CNF and running baital's sampling. In particular, the first step is the convertation of constraints into CNF with z3. The next steps are Baital's preprocessing (step 1 above) and sampling (step 2 above). Any strategy can be used. The resulted samples are converted back into the original features. The last step is the coverage computation with the generalized algorithms supporting both exact and approximate computations. Note that unlike the binary case, preprocessing results cannot be reused for coverage computation.


## Running Baital

Run command `python3 baital.py <arguments>` or `python3 baital_nf.py <arguments>` from `src` folder for systems with binary and multi-valued features, respectively. 

### Arguments

1. Required
    - *cnf_file*.cnf in dimacs format for `baital.py`
    - *qf_bv_file*.smt or *clafer_file.txt* for `baital_nf.py`
    
2. Optional

| Argument | Type | Default value | Description | 
| -------- | ---- | ------------- | ----------- |
| --outputdir | str | "./results/" | Output directory |
| --outputfile | str | "" | Output file for samples, placed in outputdir, default <cnf_filename>.samples |
| --twise | int | 2 | t value for t-wise coverage |
| --seed | int | | random seed |
| --preprocess-only |  |  | Only perform preprocessing |
| --no-sampling | | | Computes the coverage of an existing test suite. Requires --samples-file argument |
| --preprocess-file | str | "" | Precomputed file for skipping preprocessing step. Shall have .comb, or .acomb extension |
| --preprocess-approximate | | | Approximate computation of preprocessing |
| --preprocess-delta | float | 0.25 | Delta for approximate counting at preprocessing. Unused if not --preprocess-approximate | 
| --preprocess-epsilon | float | 0.25 | Epsilon for approximate counting at preprocessing. Unused if not --preprocess-approximate | 
| --strategy | int | 5 | Weight generation strategy |
| --rounds | int | 10 | Number of rounds for sample generation | 
| --samples | int | 500 | Total number of samples to generate | 
| --desired-coverage | float | | Samples are genereted until the desired coverage is reached or --rounds is completed. Cannot be used with --samples |
| --extra-samples | | | Each round 10x samples are generated and the best are selected |
| --waps | | | Use WAPS instead of CMSGen as a sampling engine. |
| --samples-per-round | int | 50| Number of samples generated per round if --desired-coverage is set |
| --weight-function | int | 2 | Function number between 1 and 7 for weight generation, used in strategies 1, 2, 3, and 4 |
| --samples-file | str | | File with samples to compute the coverage for --no-sampling option. Shall have .samples extension (or .nsamples for baital_nf.py) |
| --maxcov-file | str | | File with pregenerated list of satisfiable feature combinations for the step 3. Shall have .comb extension | 
| --no-maxcov | | | Compute only the number of distinct combinations in a test suite instead of coverage |
| --cov-approximate | | | Compute the coverage approximately |
| --cov-delta | float | 0.05 | Delta for approximate computation of coverage. Unused if not --cov-approximate |  
| --cov-epsilon | float | 0.05 | Epsilon for approximate computation of coverage. Unused if not --cov-approximate |  
| --outputfile-readable | str | "" | Only for baital_nf.py. Output file for samples in readable format, placed in outputdir, default <qf_bv_file>.rsamples|  

## Input and Output Data

We assume that features are numbered from 1 to nFeatures. Constraints of configurable system are expected in Dimacs CNF format.   

Outputs are located in --outputdir (*./results/* by default). Output file contains the list of generated samples. Each line contains sample index, comma, and a list of space-separated literals. Positive literals correspond to selected features and negative to non-selected. For example, line `2, 1 -2 3` corresponds to a second sample in which variables 1 and 3 are True (selected) and variable 2 is False (non-selected). This format is expected for --samples-file option with --no-sampling. *Outputfile.txt* contains the number of combinations in the generated samples and the t-wise coverage if computed.  

Preprocessing can output the following types of files that can be reused with --preprocess-file or --maxcov-file (only .comb file) options:  
1. *cnf_file*_*x*.comb files where *x* in [1, *twise*] contain lists of feature combinations of size *x* that are satisfiable by the input cnf formula. Each line contains a space-separated satisfiable combination of literals.  
2. *cnf_file*_*x*.acomb file contains a list of approximations of the number of feature combinations of size *x* involving a literal for each literal. Each line contains a literal and a number of combinations.  

Last lines of the console output contain the following information:
1. Time taken by each step and total time.  
2. (Approximate) number of feature combinations in the sample set.  
3. (Approximate) coverage (skipped if --no-maxcov selected).  

### Input and Output Format for Multi-valued Features
<a id="mv-format"></a>

The constraints shall be provided with QF_BV logic in SMTLIB2 format. All features that have 2 values have to be declared as Bool, all features that have more values have to be declared with the smallest BitVector. First 3 lines are expected to be comments (starting with `;;`). The first line contains space-separated pairs `feature_name=nValues` where nValues is the number of possible values for the feature. The order of features in the output sample set is the same as in this line. Contents of the second and third comment lines are optional and used to recover original values for numerical features, otherwise it is assumed that they have values between `0` and `nValues-1`.  Second line might contain space-separated pairs `feature_name=minValue` indicating that the original feature take values between `minValue` and `minValue+nValues-1`. Third line might contain space-separated pairs `feature_name=[0:val1,1:val2,...(nValues-1):valn]` indicating that the original feature has a set of values `val1...valn`. Note that constraints should be for the features with values between `0` and `nValues-1`. For example, if feature1 can take values 5, 6, 7, and 8, and feature2 has values 2, 4, 8, and 16, the first lines of the file are:  
```
;; feature1=4 feature2=4 
;; feature1=5
;; feature2=[0:2,1:4,2:8,3:16]
```   


Alternative input is a clafer-like textual description. First line is always `abstract <something> <top-level-feature>`, where top-level feature is binary and always included in any valid configuration. The following lines define features and currently the following options are supported 1) binary feature name; 2) `xor <binary_feature_name>` followed by several lines with binary features that have higher tab level - a selection of `binary_feature_name` implies a selection of an exactly one feature from the next lines; 3) `mv_feature -> integer` - a multi-valued feature 4) `[mv_feature_constraint]` - simple constraint defining possible values for a previously defined multi-valued feature, several types of constraints are supported: i) `[mv_feature </> int_value]` ii) `[mv_feature = v1 || mv_feature_name = v2 || ...]` iii) `[mv_feature1 + mv_feature2  </> int_value]` under assumption that both features have sequential values starting from 0. Examples of supported inputs can be found in benchmarks (Note that Trimesh.txt cannot be automatically converted).

baital_nf.py outputs two files with samples (by default with extensions `.nsamples` and `.rsamples`). `.nsamples` file has in the first line a space-separated list of the number of possible values for each feature in the same order as in the first line of the SMTLIB2 input file. The following lines represent generated samples: sample index, comma, and a list of space-separated values between 0 and the maximum value for each feature (order is the same as in the first line). This file is used for the coverage computation. `.rsamples` contains a readable format: each line starts with sample index, followed by a comma, followed by a space-separated pairs `<feature_name>=value`, where value is the original value of the feature. For the example above, the `.nsamples` file could look like:
```
4 4 
1, 1 2
2, 3 0
```
and `.rsamples`:
```
1, feature1=6 feature2=16
2, feature2=7 feature2=2
```

### Note on execution time

Preprocessing step could take large time depending on the type of preprocessing, *twise*, and the number of variables. Several hours are required for exact computation for `twise=2`.
For large benchmarks and `twise >=3` approximate methods shall be used: for preprocessing --preprocess-approximate option; for sampling - strategies 3, 4, or 5; for computation of coverage --cov-approximate.


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
  booktitle={Proc. 44th International Conference on Software Engineering (ICSE 2022)},
  year={2022}
}
```
```
@inproceedings{BL22,
  title={Baital: an adaptive weighted sampling platform for configurable systems},
  author={Baranov, Eduard and Legay, Axel},
  booktitle={Proceedings of the 26th ACM International Systems and Software Product Line Conference-Volume B},
  pages={46--49},
  year={2022}
}
```
