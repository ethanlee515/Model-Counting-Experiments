FROM debian:bookworm

RUN apt-get update
RUN apt-get install -y git git-lfs
RUN apt-get install -y wget tar curl openjdk-17-jdk make g++

WORKDIR /opt
RUN wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2026-03-30/oss-cad-suite-linux-x64-20260330.tgz
RUN tar xvf oss-cad-suite-*.tgz
RUN rm oss-cad-suite-*.tgz
ENV PATH="/opt/oss-cad-suite/bin:${PATH}"

# Stop Verilator from complaining
ENV LC_ALL=C.UTF-8
