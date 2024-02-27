FROM ubuntu:22.04 as builder

LABEL Description="Baital"

RUN apt-get update && apt-get install --no-install-recommends -y software-properties-common unzip

RUN apt-get install --no-install-recommends -y time make cmake build-essential gcc g++ zlib1g-dev wget libgmp-dev graphviz libmpfr-dev libmpc-dev libboost-program-options-dev libboost-serialization-dev libm4ri-dev libgmp3-dev python3 python3-dev python3-pip z3

# build CMS
WORKDIR /
RUN wget https://github.com/msoos/cryptominisat/archive/refs/tags/5.11.21.zip
RUN unzip 5.11.21.zip
WORKDIR /cryptominisat-5.11.21/
RUN mkdir build
WORKDIR /cryptominisat-5.11.21/build
RUN cmake -DSTATICCOMPILE=ON ..
RUN make -j6 \
    && make install

# build Arjun
WORKDIR /
RUN wget https://github.com/meelgroup/arjun/archive/refs/tags/2.5.4.zip
RUN unzip 2.5.4.zip
WORKDIR /arjun-2.5.4/
RUN mkdir build
WORKDIR /arjun-2.5.4/build
RUN cmake -DSTATICCOMPILE=ON ..
RUN make -j6 \
    && make install
    
   
# build approxmc
WORKDIR /
RUN wget https://github.com/meelgroup/approxmc/archive/refs/tags/4.1.24.zip
RUN unzip 4.1.24.zip
WORKDIR /approxmc-4.1.24/
RUN mkdir build
WORKDIR /approxmc-4.1.24/build
RUN cmake -DSTATICCOMPILE=ON ..
RUN make -j6 \
    && make install

WORKDIR /
RUN wget https://github.com/crillab/d4/archive/9b136b67491443954b0bd300aa15b03697053a7c.zip
RUN unzip 9b136b67491443954b0bd300aa15b03697053a7c.zip
WORKDIR /d4-9b136b67491443954b0bd300aa15b03697053a7c
RUN make -j8 ./d4

# build cmsgen
WORKDIR /
RUN wget https://github.com/meelgroup/cmsgen/archive/refs/tags/6.1.0.zip
RUN unzip 6.1.0.zip
WORKDIR /cmsgen-6.1.0
RUN mkdir build
WORKDIR /cmsgen-6.1.0/build
RUN cmake -DSTATICCOMPILE=ON ..
RUN make \
    && make install


RUN pip install pyparsing gmpy2 numpy pydot psutil pycosat antlr4-python3-runtime

RUN mkdir /baital
RUN mkdir /baital/bin
RUN mkdir /baital/src
RUN mkdir /baital/benchmarks

COPY ./src /baital/src
RUN cp /d4-9b136b67491443954b0bd300aa15b03697053a7c/d4 /baital/bin/
RUN chmod +x /baital/bin/d4
WORKDIR /baital/src

ENTRYPOINT ["/usr/bin/python3"]
