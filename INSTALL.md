# Baital Installation

1. Install libraries required by additional tools: `build-essential`, `cmake`, `graphviz`, `libgmp-dev`, `libmpfr-dev`, `libmpc-dev`, `zlib1g-dev`, `libboost-program-options-dev`, `libboost-serialization-dev`, `libgmp3-dev`.  
    - On Debian-based systems the command is `sudo apt install build-essential cmake graphviz libgmp-dev libmpfr-dev libmpc-dev`
                                             `sudo apt install zlib1g-dev libboost-program-options-dev libboost-serialization-dev libgmp3-dev`
2. Install additional python libraries.  
    - `pip3 install -r requirements.txt`  
3. Install [ApproxMC4](https://github.com/meelgroup/approxmc) (*).  
3.1 git clone https://github.com/msoos/cryptominisat  
3.2 cd cryptominisat  
3.3 mkdir build && cd build  
3.4 cmake ..  
3.5 make  
3.6 sudo make install  
3.7 cd ../..  
3.8 git clone https://github.com/meelgroup/arjun  
3.9 cd arjun  
3.10 mkdir build && cd build  
3.11 cmake ..  
3.12 make  
3.13 sudo make install  
3.14 cd ../..  
3.15 git clone https://github.com/meelgroup/approxmc  
3.16 cd approxmc  
3.17 mkdir build && cd build  
3.18 cmake ..  
3.19 make  
3.20 sudo make install  
4. Install [Cmsgen](https://github.com/meelgroup/cmsgen).  
4.1 git clone https://github.com/meelgroup/cmsgen  
4.2 cd cmsgen  
4.3 mkdir build && cd build  
4.4 cmake ..  
4.5 make  
4.6 sudo make install  
5. (Optional) Install [d4](https://github.com/crillab/d4) and copy d4 binary to `bin/` folder and ensure execute permission. (Required only for WAPS sampling).  
5.1 git clone https://github.com/crillab/d4  
5.2 cd d4  
5.3 make -j8  
5.4 cp ./d4 <path/to/baital>/bin/  
5.5 chmod +x <path/to/baital>/bin/d4  
6. Install z3: `sudo apt install z3` (Required for Multi-valued/Numerical Features)  
