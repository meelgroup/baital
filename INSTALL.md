# Baital Installation

1. Install libraries required by additional tools: `build-essential`, `cmake`, `graphviz`, `libgmp-dev`, `libmpfr-dev`, `libmpc-dev`, `zlib1g-dev`, `libboost-program-options-dev`, `libboost-serialization-dev`, `libgmp3-dev`, `z3`.  
    - On Debian-based systems the command is `sudo apt install build-essential cmake graphviz libgmp-dev libmpfr-dev libmpc-dev`
                                             `sudo apt install zlib1g-dev libboost-program-options-dev libboost-serialization-dev libgmp3-dev z3`
2. Install additional python libraries.  
    - `pip3 install -r requirements.txt`  
3. (Optional) Install [d4](https://github.com/crillab/d4) and copy d4 binary to `bin/` folder and ensure execute permission. (Required only for WAPS sampling).  
3.1 git clone https://github.com/crillab/d4  
3.2 cd d4  
3.3 make -j8  
3.4 cp ./d4 <path/to/baital>/bin/  
3.5 chmod +x <path/to/baital>/bin/d4  

3*. (Optional) It is possible to use a different version of [d4](https://github.com/crillab/d4v2)  
3*.1 Install `ninja-build`:  
    - On Debian-based systems the command is `sudo apt install ninja-build`  
3*.2 git clone https://github.com/crillab/d4v2  
3*.3 Due to missing file in d4v2, download patoh distribution from http://cc.gatech.edu/~umit/software.html and copy files to d4v2/3rdParty/patoh/  
3*.4 cd d4v2
3*.5 ./build.sh
3.4 cp build/d4 <path/to/baital>/bin/  
3.5 chmod +x <path/to/baital>/bin/d4  
3.6 in <path/to/baital>/src/waps_upd.py  
    - Comment line 605 (cmd = "/usr/bin/time -o "+ "/tmp/" + inputFile.split("/")[-1]+".timeout "+ "--verbose ../bin/d4 /tmp/" + inputFile.split("/")[-1] + ".tmp " + " -dDNNF -out=" + dDNNF + ' ' + setSeed)  
    - Uncomment line 604 (cmd = "/usr/bin/time -o "+ "/tmp/" + inputFile.split("/")[-1]+".timeout "+ "--verbose ../bin/d4 -i /tmp/" + inputFile.split("/")[-1] + ".tmp " + "-m ddnnf-compiler --dump-ddnnf " + dDNNF + ' ' + setSeed)  
