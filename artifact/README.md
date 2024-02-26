
# Abstract

`JVBench` is the first open-source benchmark suite for the Java Vector API. It includes several realistic and diversified benchmarks, specifically designed for evaluating vectorization.
This artifact consists of a ready-to-use [Docker](https://www.docker.com/) image embedding `JVBench` together with a set of tools/scripts that can be used to execute the `JVBench` workloads as well as collect, process and plot performance measurements to replicate the evaluation of `JVBench` presented in the paper "*Java Vector API: Benchmarking and Performance Analysis*'' (CC'23). The artifact also contains the complete pre-collected performance measurements used to generated the original figures of the paper. 

# Overview

- Badge we are requesting: “Available” badge, Red badge (evaluated:functional/reusable), and Blue badge (results reproduced).

- Hardware requisites: Please see the [Hardware Requirements](#hardware-requirements) section below.

- Software requisites: Please see the [Software Requirements](#software-requirements) section below.

- Approximate time to install: 5 minutes (section [Installing the Artifact](#installing-the-artifact)).

- Approximate time to reproduce the figures of the paper using pre-collected data: 5 minutes (section [Using the Artifact](#using-the-artifact)).

- Approximate time to reproduce the results: minimum 1.5 hours (setting `evaluation short`) or ideally 24 hours (setting `evaluation full`) for each machine, depending on the number of benchmark runs (section [Using the Artifact](#using-the-artifact)).

# Getting Started Guide

## Requirements

### Hardware Requirements

- Below, we define three different machine types and the requisites that a machine must have to be classified in a type. To evaluate the artifact, a reviewer needs one machine per type:

    - `AVX`: a machine where the CPU *supports* the Intel-defined CPU flags `sse`, `sse2`, `ssse3`, `sse4_1`, `sse4_2`,`avx` but *does not support* the flags `avx2`, `fma`, `avx512f`, `avx512dq`, `avx512cd`, `avx512bw`, `avx512v`, `avx512_vnni`.

    - `AVX2`: a machine where the CPU *supports* the Intel-defined CPU flags `sse`, `sse2`, `ssse3`, `sse4_1`, `sse4_2`,`avx`, `avx2`, `fma` but *does not support* the flags `avx512f`, `avx512dq`, `avx512cd`, `avx512bw`, `avx512v`, `avx512_vnni`.

    - `AVX512` a machine where the CPU *supports*  the Intel-defined CPU flags `sse`, `sse2`, `ssse3`, `sse4_1`, `sse4_2`,`avx`, `avx2`, `fma`, `avx512f`, `avx512dq`, `avx512cd`, `avx512bw`, `avx512v`, `avx512_vnni`.
	
	- Host machines should have at least 16GB of RAM, at least 30GB of free space, bash script support, and an Internet connection.
	
In the following text, following the same terminology of the paper, we will refer to the three machines with the terms `MAVX`, `MAVX2` and `MAVX512`, respectively.

*Note*: On Ubuntu 20.04.5 LTS, one can list the Intel-defined CPU flags supported by the CPU by executing the command : `cat /proc/cpuinfo`.
The CPU flags will be printed on the standard output after the `flags` attribute.

*Note*: We are aware that fully evaluating our artifact requires a variety of machines that is unlikely to be available to all reviewers. We are in contact with our organization to make compatible (potentially virtual) machines available to reviewers to ease the artifact evaluation process. Please let us know if this is needed. 


### Software Requirements

- Host machines should have [Docker](https://www.docker.com/) installed (we have tested Docker version `20.10.18, build b40c2f6` on Ubuntu 20.04.5 LTS).

- We have tested our bash scripts on Ubuntu 20.04.5 LTS. The bash scripts may not work on other operating systems.

## Installing the Artifact

1. Extract the artifact `tgz` available at the following URL: [https://doi.org/10.5281/zenodo.7489683](https://doi.org/10.5281/zenodo.7489683). It includes the ready-to-use `JVBench` evaluation Docker image, a script to run the artifact, and a copy of this `README` file.

2. Verify the installation by executing the `run.sh` script specifying `verify` as argument.

    ```bash
    $ ./run.sh verify
    ```
   If the artifact is correctly installed, you should see a `The artifact is correctly installed` message on the standard output.

*Note*: The artifact `tgz` is available also at [https://github.com/usi-dag/JVBench-artifact/releases](https://github.com/usi-dag/JVBench-artifact/releases).

## Using the Artifact

- The main script to reproduce the evaluation of our paper is `run.sh`, which receives one of the following arguments specifying the run mode:

    - `precollected`: Generates the figures shown in the paper using pre-collected data.

    - `evaluation`: Runs JVBench in the container and then generates the figures from the collected data.

    - `clean`: Cleans the environment by deleting the generated figures and the newly collected data.

### Generating figures with pre-collected data

To generate the figures using pre-collected data (i.e., the same data used to generate the figures that appear in the paper), follow the instructions below:

1. Execute `run.sh` specifying `precollected` as argument.

    ```bash
    $ ./run.sh precollected
    ```

2. The generated figures will be saved in the `output/figures-paper` folder in the host machine.

### Generating figures with newly collected data

In this section, we focus on detailed instructions to generate the figures using newly collected data.
We provide two options for running measurements:

- `short`: Runs a few measurements (i.e., 1 run with 10 steady-state iterations), using all `JVBench` workloads and patterns. Given the large amount of time needed to produce the `full` measurements (see below), we provide this setting to approximate the results obtained in the paper. We note that the accuracy of the results obtained using this setting will be lower.

    1. Execute `run.sh` specifying `evaluation short` as argument.

        ```bash
        $ ./run.sh evaluation short
        ```

    2. After approximately 1.5 hours, the generated figures will be saved in the `output/short/figures` folder in the host machine. The raw data will be saved into the `output/short/data` folder, instead. The figures will be generated only after the execution of all the benchmarks.

- `full`: Runs all `JVBench` workloads and patterns, setting 10 run with 10 steady-state iterations (i.e., 10 measurements). We expect that executing this setting will take around 24 hours.

    1. Execute `run.sh` specifying `evaluation full` as argument.

        ```bash
        $ ./run.sh evaluation full
        ```

    2. After the measurements are completed, the generated figures will be saved in the `output/full/figures` folder in the host machine. The raw data will be saved into the `output/full/data` folder, instead. The figures will be generated only after the execution of all the benchmarks.

*Note*: For more information about the raw output data, please see the [Directory Hierarchy](#directory-hierarchy) section below.

### Cleaning the Environment

To delete the generated figures and the newly collected data, follow the instructions below:

1. Execute `run.sh` specifying `clean` as argument.

    ```bash
    $ ./run.sh clean
    ```

# Overview of Claims

To fully reproduce the claims, we report the list of figures that should be reproduced.
For each figure in the paper, we report a brief description and the list of generated pdfs to be checked when executing both the `precollected` and `evaluation` command.

The `precollected` command generates all the subfigures shown in the paper for machines `MAVX`, `MAVX2`, and `MAVX512`. These figures are saved in folder `output/figures-paper`.

Following the same structure of our paper, the `evaluation` command generates a single subfigure for each figure. This subfigure can be compared with one of the subfigures shown in the paper, depending on the machine on which the subfigure has been generated. For instance, if the subfigure has been generated on `MAVX2`, the subfigure can be compared with the subfigure `MAVX2` in the paper. To generate all the subfigures, the reviewer needs to execute the `evaluation` command on three different machines, one for each type. These figures are saved in folder `output/<mode>/figures` where `<mode>` is either `short` or `full`.

With the goal of easing the evaluation of the artifact by the reviewers, we ported `JVBench` to a containerized environment. Nonetheless, the use of containerization may significantly impact our measurements, particularly on those based on execution time. Moreover, different host machines with different hardware capabilities may yield different execution times. We note that the performance measurements used to generate the figures in the paper have been collected in an isolated environment with minimal perturbation where (almost) no other process was being executed.
Newly collected data may lead to the generation of figures with different numbers w.r.t. those shown in the paper. However, we expect the data trends and the figures generated with newly collected data to be similar to the ones shown in the paper, as detailed below.

## Evaluation of the Java Vector API (Figure 3)

In Figure 3, we use different implementations of our benchmarks to show the speedups enabled by the compiler auto-vectorization (`auto-vectorized` column), by the Java Vector API (`vector-api` column), and by both the compiler auto-vectorization and the Java Vector API simultaneously (`fully-vectorized` column) w.r.t. a scalar implementation of each benchmark.

### Precollected Data

- Figure 3 (a) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX512_speedup.pdf`
- Figure 3 (b) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX2_speedup.pdf`
- Figure 3 (c) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX_speedup.pdf`

### Newly Collected Data

- The generated figure is saved at `output/<mode>/figures/new_19_dockerimg_speedup.pdf`

- We expect the `auto-vectorized` column to be close to 1 for all benchmarks (except `axpy` on `MAVX512`).

- We expect no slowdown, with the exception of benchmarks `particlefilter` and `swaptions` on `MAVX`.

- We expect greater speedups for benchmarks `blackscholes`, `lavaMD`, `particlefilter` (only on `MAVX512`), `pathfinder`, `somier`, and `streamcluster`.

## loopBound and indexInRange APIs (Figure 5)

In Figure 5, we evaluate the performance of two semantically equivalent implementations that use either the `loopBound` or the `indexInRange` API.

### Precollected Data

- Figure 5 (a) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX512_indexInRange.pdf`
- Figure 5 (b) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX2_indexInRange.pdf`
- Figure 5 (c) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX_indexInRange.pdf`

### Newly Collected Data

- The generated figure is saved at `output/<mode>/figures/new_19_dockerimg_indexInRange.pdf`

- In general, we expect `loopBound` to be greater than `indexInRange` (for the same benchmark).

## Pow Pattern (Figure 6)

In Figure 6, we evaluate the performance of the two semantically equivalent expressions: `vector.mul(vector)` and `vector.pow(2)`.

### Precollected Data

- Figure 6 (a) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX512_pow.pdf`
- Figure 6 (b) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX2_pow.pdf`
- Figure 6 (c) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX_pow.pdf`

### Newly Collected Data

- The generated figure is saved at `output/<mode>/figures/new_19_dockerimg_pow.pdf`

- In general, we expect `mul` to be greater than `pow` (for the same benchmark).

## Xor Pattern (Figure 8)

In Figure 8, we evaluate the performance of three different vector mask `xor` implementations, namely `xor`, `neq-xor`, and `logical-xor`.

### Precollected Data

- Figure 8 in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX512_xor.pdf`

### Newly Collected Data

- The generated figure is saved at `output/<mode>/figures/new_19_dockerimg_xor.pdf`

- **Since our paper only considers this analysis on `MAVX512`, the generated figure should be compared with the paper Figure 8 only when produced on a machine of type `AVX512`. On other architectures, figures are generated even though there is no corresponding figure in the paper to be evaluated.** We expect the public `xor` method to yield better performance than `neq-xor`, which in turns should yield better performance than `logical-xor`.

## Fma Pattern (Figure 9)

In Figure 9, we evaluate the performance of the vector `fma(a, b, c)` operation  (`scalar-fma/fma` column) and of the equivalent vector `a.mul(b).add(c)` expression (`scalar-mul-add/mul-add` column). Moreover, we compare the performance of these two implementations (`fma/mul-add` column).

### Precollected Data

- Figure 9 (a) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX512_fma.pdf`
- Figure 9 (b) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX2_fma.pdf`
- Figure 9 (c) in the paper should be compared with the generated figure at `output/figures-paper/precollected_19_MAVX_fma.pdf`

### Newly Collected Data

- The generated figure is saved at `output/<mode>/figures/new_19_dockerimg_fma.pdf`

- We expect `scalar-mul-add/mul-add` to be greater than 1 on all machines.

- We expect `scalar-fma/fma` to be greater than 1 on `MAVX512` and `MAVX2` but not on `MAVX`.

- We expect `fma/mul-add` to be close to 1 on `MAVX512` and `MAVX2` and far greater than 1 on `MAVX`.

# Reusing and Modifying the Artifact

In this section, we report additional notes that are not needed for the "regular" artifact evaluation but help in reusing and extending the artifact. These notes are not needed for reproducing the evaluation of our paper.

## Docker Image Specifications

- The [parent image](https://docs.docker.com/glossary/#parent-image) of our Docker image is [ubuntu:20.04](https://hub.docker.com/layers/library/ubuntu/20.04/images/sha256-8eb87f3d6c9f2feee114ff0eff93ea9dfd20b294df0a0353bd6a4abf403336fe?context=explore).

- Our Docker image contains the following pre-installed `apt-get` packages:
   
   ```
   autoconf
   build-essential
   curl
   fakeroot
   gcc
   git
   libasound2-dev
   libcups2-dev
   libffi-dev
   libfontconfig1-dev
   libfreetype6-dev
   libpng-dev
   libx11-dev
   libxext-dev
   libxrandr-dev
   libxrender-dev
   libxt-dev
   libxtst-dev
   linux-tools-common
   make
   python3.9
   python3.9-distutils
   symlinks
   unzip
   wget
   zip
   ```

- Using `pip3`, we pre-installed the following packages for `python3.9`:

   ```
   matplotlib
   numpy
   pandas
   scipy
   setuptools
   ```

- In our image, the following environment variables are defined:

   ```bash
   # Path to the regular OpenJDK 19 build (commit hash 2677dd6d231)
   JVBENCH_JAVA_HOME=/artifact/jdk19
   # Path to the custom OpenJDK 19 build (from commit hash 2677dd6d231) that that defines the VectorMask.xor(..) method as public (Section 5.4)
   JVBENCH_JAVA_HOME_XOR=/artifact/jdk19-xor
   # Path to the regular JVBench build
   JVBENCH_JAR=/artifact/JVBench.jar
   # Path to the custom JVBench build that uses the VectorMask.xor(..) public method (Section 5.4)
   JVBENCH_XOR_JAR=/artifact/JVBench-xor.jar
   ```

   We do not define the `JAVA_HOME` environment variable, which must be set when needed.

- Our image includes [Apache Maven](https://maven.apache.org/) 3.8.7 at directory `/artifact/apache-maven-3.8.7`. We added directory `/artifact/apache-maven-3.8.7/bin` to the `PATH` environment variable.

## Directory Hierarchy

The directory hierarchy in our Docker image is as follows:

```
/artifact                   <-- working directory
| README.md                 // a copy of this README file
| config                    // environment variables used by the other commands
| utils                     // bash utils used by the other commands
| evaluation.sh             // run benchmarks by calling the python scripts in `benchmark_runner/` and generate the figures by calling the scripts in `postprocessing/`
| generate-figures.sh       // call the python scripts in `postprocessing/` to generate the figures
| precollected.sh           // generate figures using precollected data
| verify.sh                 // verify the installation by running other scripts and checking the exit codes
| JVBench.jar               // regular JVBench build
| JVBench-xor.jar           // custom JVBench build that uses the VectorMask.xor(..) public method (Section 5.4)
> apache-maven-3.8.7/       // apache maven installation
> jdk19/                    // regular OpenJDK 19 build
> jdk19-xor/                // custom OpenJDK 19 build that that defines the VectorMask.xor(..) method as public (Section 5.4)
> benchmark_runner/         // helper python scripts used to execute JVBench workloads
> precollected_data/        // precollected data used to generate the figures of the paper
> postprocessing/           // python scripts to generate the figures using matplotlib
V ↗output                   // link to output folder on the host machine
  V short                      // folder created by executing the `./run.sh evaluation short` command
    > figures                     // contains the figures generated using the data stored in its sibling `data` folder
    V data/jdk19/dockerimg        // contains the newly collected raw data
      V benchmark/performance/<datetime>/<benchmark>        // contains the performance measurements of benchmark <benchmark> for the execution started at <datetime>
        | <javaBenchmarkClassName>.txt                                 // standard output of the execution of benchmark <benchmark>
        | <javaBenchmarkClassName>.csv                                 // performance masurements extracted from the sibling `.txt` file
      V pattern/performance/<datetime>/<benchmark>          // contains the performance measurements of benchmark <benchmark> for the execution started at <datetime>
        | <javaBenchmarkClassName>.<pattern>.txt                       // standard output of the execution of benchmark <benchmark> exercising pattern <pattern>
        | <javaBenchmarkClassName>.<pattern>.csv                       // performance masurements extracted from the sibling `.txt` file
  > full                       // folder created by executing the `./run.sh evaluation full` command, this folder has the same structure as its sibling folder `short`
  > figures-paper              // folder created by executing the `./run.sh precollected` command, contains the figures generated using precollected data
```

*Note*: The `↗` symbol before `output` denotes that such folder is mapped to the `output/` folder in the current path of the host machine. Therefore, you can open files generated in `↗output` in the host machine, from outside the docker container.

## Run Script

The `run.sh` script (stored in the host machine) performs the following actions:

- Checks whether Docker is installed.

- Checks whether the docker service is running,
    - If the docker service is not running, the script tries to start it.

- Checks whether the current user is in the `docker` group.
    - If the current user is not in the `docker` group, the script tries to add it.

- Loads the Docker image of the artifact.

- Creates a container from the docker image and executes the script whose name matches the first parameter, providing the other parameters as arguments to that script. For instance, the `./run.sh evaluation short` command executes the `./evaluation.sh short` command into the newly created container.

## Source Code

### JVBench

The source code of `JVBench` is open-source and publicly available at [https://github.com/usi-dag/JVBench](https://github.com/usi-dag/JVBench).
Reviewers are welcome to download, build, and try `JVBench` on their own machines.
The `README` file in the repository of `JVBench` contains the list of benchmarks and all the instructions to run the workloads.

### Source Code of the Artifact Itself

The source code used to generate this artifact is open-source and publicly available at [https://github.com/usi-dag/JVBench-artifact](https://github.com/usi-dag/JVBench-artifact).
One can fork and modify the source code of this repository to modify the build process of the docker image, for example, to include profilers or use a customized build of `JVBench`.
  
# Troubleshooting

- If you have disk space issues with docker, try running `docker system prune` or restart the docker service.
