# Baital Installation

1. Install libraries required by additional tools: `build-essential`, `cmake`, `graphviz`, `libgmp-dev`, `libmpfr-dev`, `libmpc-dev`, `zlib1g-dev`, `libboost-program-options-dev`, `libboost-serialization-dev`, `z3`.  
    - On Debian-based systems the command is `sudo apt install build-essential cmake graphviz libgmp-dev libmpfr-dev libmpc-dev zlib1g-dev libboost-program-options-dev libboost-serialization-dev z3`
2. Install additional python libraries.  
    - `pip3 install -r requirements.txt`  
3. (Optional) Install [d4](https://github.com/crillab/d4) and copy d4 binary to `bin/` folder and ensure execute permission. (Required only for WAPS sampling).  
3.1 git clone https://github.com/crillab/d4  
3.2 cd d4  
3.3 make -j8  
3.4 cp ./d4 <path/to/baital>/bin/  
3.5 chmod +x <path/to/baital>/bin/d4  

### D4V2
It is possible to use a never version of d4. Step 3 can be replaced with the following:  

4. (Optional) Install a different version of [d4](https://github.com/crillab/d4v2)  
4.1 Install `ninja-build`: `sudo apt install ninja-build`      
4.2 git clone https://github.com/crillab/d4v2  
4.3 Due to missing file in d4v2, download patoh distribution from http://cc.gatech.edu/~umit/software.html and copy files to d4v2/3rdParty/patoh/  
4.4 cd d4v2  
4.5 ./build.sh  
4.6 cp build/d4 <path/to/baital>/bin/  
4.7 chmod +x <path/to/baital>/bin/d4  
4.8 In <path/to/baital>/src/waps_upd.py  
    - Comment line 605 (cmd = "/usr/bin/time -o "+ "/tmp/" + inputFile.split("/")[-1]+".timeout "+ "--verbose ../bin/d4 /tmp/" + inputFile.split("/")[-1] + ".tmp " + " -dDNNF -out=" + dDNNF + ' ' + setSeed)  
    - Uncomment line 604 (cmd = "/usr/bin/time -o "+ "/tmp/" + inputFile.split("/")[-1]+".timeout "+ "--verbose ../bin/d4 -i /tmp/" + inputFile.split("/")[-1] + ".tmp " + "-m ddnnf-compiler --dump-ddnnf " + dDNNF + ' ' + setSeed)  
    
From a few tests we haven't noticed a significant difference in overall performance in comparison with the original version of d4: d4 is called a single time during the execution and its share of overall time consumption is not big.  

## Quick Test

For a quick test of the installation, run `python3 test.py` from `src` folder.   
If d4 is installed, additionally run `python3 test_d4.py`.  
All tests are expected to pass.  
