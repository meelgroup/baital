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
