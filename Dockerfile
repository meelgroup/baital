FROM ubuntu:22.04 as builder

LABEL Description="Baital"

RUN apt-get update && apt-get install --no-install-recommends -y software-properties-common unzip

RUN apt-get install --no-install-recommends -y time make cmake build-essential gcc g++ zlib1g-dev wget libgmp-dev graphviz libmpfr-dev libmpc-dev libboost-program-options-dev libboost-serialization-dev libm4ri-dev libgmp3-dev python3 python3-dev python3-pip z3

# build D4
WORKDIR /
RUN wget https://github.com/crillab/d4/archive/9b136b67491443954b0bd300aa15b03697053a7c.zip
RUN unzip 9b136b67491443954b0bd300aa15b03697053a7c.zip
WORKDIR /d4-9b136b67491443954b0bd300aa15b03697053a7c
RUN make -j8 ./d4

RUN pip install pyparsing gmpy2 numpy pydot psutil pycosat antlr4-python3-runtime pyapproxmc pycmsgen

RUN mkdir /baital
RUN mkdir /baital/bin
RUN mkdir /baital/src
RUN mkdir /baital/benchmarks

COPY ./src /baital/src
RUN cp /d4-9b136b67491443954b0bd300aa15b03697053a7c/d4 /baital/bin/
RUN chmod +x /baital/bin/d4
WORKDIR /baital/src

ENTRYPOINT ["/usr/bin/python3"]
