FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

# artifact
ADD artifact/ /artifact
WORKDIR /artifact

# dependencies
RUN apt-get -yq update && \
    apt-get install -y git wget curl \
                       # required to build the JDK
                       zip unzip \
                       gcc make linux-tools-common build-essential \
                       autoconf \
                       libfreetype6-dev libcups2-dev libx11-dev libxext-dev libxrender-dev libxrandr-dev libxtst-dev libxt-dev libasound2-dev \
                       libffi-dev libfontconfig1-dev libpng-dev fakeroot symlinks \
                       # python (runner and figures)
                       python3.9 python3.9-distutils && \
    # required to build JVBench
    wget https://dlcdn.apache.org/maven/maven-3/3.8.8/binaries/apache-maven-3.8.8-bin.tar.gz && \
    tar -xzvf apache-maven-3.8.8-bin.tar.gz && \
    rm -rf apache-maven-3.8.8-bin.tar.gz

ENV PATH $PATH:/artifact/apache-maven-3.8.8/bin

# python dependencies
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.9 get-pip.py && \
    rm -rf get-pip.py

RUN pip3 install setuptools matplotlib numpy scipy pandas

# boot JDK
RUN wget -q https://github.com/adoptium/temurin19-binaries/releases/download/jdk-19.0.1%2B10/OpenJDK19U-jdk_x64_linux_hotspot_19.0.1_10.tar.gz && \
    echo "163da7ea140210bae97c6a4590c757858ab4520a78af0e3e33129863d4087552  OpenJDK19U-jdk_x64_linux_hotspot_19.0.1_10.tar.gz" > SHA256SUMS && \
    sha256sum -c SHA256SUMS && \
    tar -xvzf OpenJDK19U-jdk_x64_linux_hotspot_19.0.1_10.tar.gz && \
    rm -f SHA256SUMS OpenJDK19U-jdk_x64_linux_hotspot_19.0.1_10.tar.gz

ENV PATH /artifact/jdk-19.0.1+10/bin:$PATH

# evaluation JDKs
RUN git clone https://github.com/openjdk/jdk19u.git && \
    cd jdk19u && \
    git checkout 2677dd6d2318afb4afffde46f8e8e20276cb2894 && \
    # regular JDK
    bash configure --with-boot-jdk=/artifact/jdk-19.0.1+10 && \
    make images && \
    mv build/linux-x86_64-server-release/images/jdk /artifact/jdk19 && \
    # xor JDK
    git apply /artifact/public-xor-jdk.patch && \
    cd src/jdk.incubator.vector/share/classes/jdk/incubator/vector/ && \
    ./gen-src.sh && \
    cd /artifact/jdk19u && \
    bash configure --with-boot-jdk=/artifact/jdk-19.0.1+10 && \
    make images && \
    mv build/linux-x86_64-server-release/images/jdk /artifact/jdk19-xor && \
    # cleanup
    cd /artifact && \
    rm -rf public-xor-jdk.patch jdk-19.0.1+10 jdk19u

ENV JVBENCH_JAVA_HOME /artifact/jdk19
ENV JVBENCH_JAVA_HOME_XOR /artifact/jdk19-xor

# JVBench xor
RUN git clone https://github.com/usi-dag/JVBench && \
    cd JVBench && \
    git checkout f337e99618cff402e8dd675481fe298a70b281ca && \
    # xor JVBench
    git apply /artifact/public-xor-jvbench.patch && \
    cp -r ../JVBench-xor/* ./ && \
    JAVA_HOME=$JVBENCH_JAVA_HOME_XOR mvn clean install && \
    mv target/JVBench-1.0.1.jar /artifact/JVBench-xor.jar && \
    # cleanup
    cd /artifact && \
    rm -rf public-xor-jvbench.patch JVBench JVBench-xor

# JVBench mine
RUN git clone https://github.com/usi-dag/counting-vectorial && \
    cd counting-vectorial/JVBench && \
    # regular JVBench
    JAVA_HOME=$JVBENCH_JAVA_HOME mvn clean install && \
    mv target/JVBench-1.0.1.jar /artifact/JVBench.jar && \
    # mv plugin
    cd .. && \
    mv plugin/SocketPlugin.jar /artifact && \
    # pin
    mv pin-3.28-98749-g6643ecee5-gcc-linux /artifact && \
    # instructions
    mv x86_vectorial_instructions.txt /artifact && \
    # create results directory
    cd /artifact && \
    mkdir results && \
    # cleanup
    rm -rf counting-vectorial

ENV JVBENCH_JAR /artifact/JVBench.jar
ENV JVBENCH_XOR_JAR /artifact/JVBench-xor.jar

ENV PIN_SOCKET_PLUGIN /artifact/SocketPlugin.jar

# other
ARG shared_volume
RUN mkdir -p /artifact/$shared_volume

COPY config ./
COPY utils ./
