FROM ubuntu:20.04 as builder

LABEL Description="Baital"

RUN apt-get update && apt-get install --no-install-recommends -y software-properties-common unzip

RUN apt-get install --no-install-recommends -y time libboost-program-options-dev gcc g++ make cmake zlib1g-dev wget make libgmp-dev graphviz libmpfr-dev libmpc-dev build-essential libm4ri-dev libgmp3-dev python3 python3-dev python3-pip

# build CMS
WORKDIR /
RUN wget https://github.com/msoos/cryptominisat/archive/641f91597d1292f691d8cc8fd191bed73d004ebf.zip
RUN unzip 641f91597d1292f691d8cc8fd191bed73d004ebf.zip
WORKDIR /cryptominisat-641f91597d1292f691d8cc8fd191bed73d004ebf/
RUN mkdir build
WORKDIR /cryptominisat-641f91597d1292f691d8cc8fd191bed73d004ebf/build
RUN cmake -DSTATICCOMPILE=ON ..
RUN make -j6 \
    && make install

# build approxmc
WORKDIR /
RUN wget https://github.com/meelgroup/approxmc/archive/30c6787e02c9660fd6798d8664f4beda9497495a.zip
RUN unzip 30c6787e02c9660fd6798d8664f4beda9497495a.zip
WORKDIR /approxmc-30c6787e02c9660fd6798d8664f4beda9497495a
RUN mkdir build
WORKDIR /approxmc-30c6787e02c9660fd6798d8664f4beda9497495a/build
RUN cmake -DSTATICCOMPILE=ON ..
RUN make -j6 \
    && make install

WORKDIR /
RUN wget https://github.com/crillab/d4/archive/9b136b67491443954b0bd300aa15b03697053a7c.zip
RUN unzip 9b136b67491443954b0bd300aa15b03697053a7c.zip
WORKDIR /d4-9b136b67491443954b0bd300aa15b03697053a7c
RUN make -j8 ./d4


RUN pip install pyparsing gmpy2 numpy pydot psutil pycosat

RUN mkdir /baital
RUN mkdir /baital/bin
RUN mkdir /baital/src
RUN mkdir /baital/benchmarks

COPY ./src /baital/src
COPY ./bin /baital/bin
RUN cp /d4-9b136b67491443954b0bd300aa15b03697053a7c/d4 /baital/bin/
RUN chmod +x /baital/bin/d4
WORKDIR /baital/src

ENTRYPOINT ["/usr/bin/python3", "baital.py"]
