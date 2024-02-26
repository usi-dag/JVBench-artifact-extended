# JVBench Docker Image

This repository contains the scripts used to build a docker image with `JVBench`.

## Requirements

- [docker](https://docs.docker.com/install/)
- [node](https://nodejs.org/)
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

The scripts have been tested on Ubuntu 20.04 and may not work correctly on other operating systems.

## Getting Started

You can build a docker image with `JVBench` using the following command:

```
build.sh
```

Then, you can find a `.tgz` archive with the generated docker image in the `out/release` folder.

## Repository Overview

- `config`: contains the environment variables used by the other commands
- `utils`: bash utils used by the other commands
- `Dockerfile`: the dockerfile used to build the image
- `build.sh`: script used to build the docker image
- `run.sh`: forwards the provided command to a docker container of the generated image (copied in the generated archive)
- `md2pdf/`: contains utilities to convert the `README.md` file of the artifact to `pdf` (used by `build.sh`)
- `artifact/`: contains the code to be copied into the image
    - `benchmark_runner/`: helpers to execute JVBench
    - `postprocessing/`: contains the code to generate the figures
    - `public-xor-jdk.patch`: git patch to build a JVM with the public `xor` method
    - `public-xor-jvbench.patch`: git patch to build JVBench with the public `xor` method
    - `JVBench-xor`: benchmarks and tests using the public `xor` method
    - `precollected_data/`: contains the data used to generate the figures in the paper
    - `evaluation.sh`: executes `JVBench` and generate the figures
    - `generate-figures.sh`: helper script that calls the python code in the `postprocessing` folder to generate the figures
    - `precollected.sh`: generates the figures using the data in `precollected_data`
    - `README.md`: the readme file to be included in artifact
