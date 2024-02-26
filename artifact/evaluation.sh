#!/bin/bash

# $1: configuration, one of [short, full].

. config

if [ $# -lt 1 ]; then
    echo -e "\n\nNo evaluation setting parameter provided.\nPlease chose one of [short, full]\n\n"
    exit 2
fi

mode=$1
if [ ! $mode == "short" ] && [ ! $mode == "full" ]; then
    echo -e "\n\nInvalid evaluation setting provided.\nPlease chose one of [short, full]\n\n"
    exit 3
fi

. utils

approximate_time="1.5"
if [ $mode == "full" ]; then
    approximate_time="24"
fi

echo
echo "This command will run the JVBench workloads and then generate the figures from the collected data."
echo "Approximate running time: $approximate_time hours (may vary depending on the underlying hardware capabilities)"
echo
echo "Note: the figures will be generate only after the execution of all the benchmarks. No intermediate figure is generated."
echo
yes_or_no "Do you wish to continue?"
if [ $? -ne 0 ]; then
    echo 
    echo "Aborted"
    echo
    exit 4
fi
echo

LOCAL_VOLUME_OUT_DIR=$SHARED_VOLUME/$mode
VOLUME_OUT_DIR=$(pwd)/$LOCAL_VOLUME_OUT_DIR
RUNNER_OUT_DIR=$VOLUME_OUT_DIR/data/jdk19
FIGURES_OUT_DIR=$VOLUME_OUT_DIR/figures
PIN_RESULTS_DIR=$VOLUME_OUT_DIR/pin

if [[ -d "$VOLUME_OUT_DIR" ]]; then
    echo
    echo "WARNING: The $LOCAL_VOLUME_OUT_DIR folder already exists on your filesystem. If you do not delete its content, data will be merged and figures will be overwritten."
    yes_or_no "Do you wish to delete the $LOCAL_VOLUME_OUT_DIR folder?"

    if [ $? -eq 0 ]; then
        echo 
        echo "Deleting folder $LOCAL_VOLUME_OUT_DIR... (requires sudo)"
        echo
        sudo rm -rf $(pwd)/$VOLUME_OUT_DIR
        echo
        echo "The $LOCAL_VOLUME_OUT_DIR folder has been deleted"
        echo
    fi 
fi

mkdir -p $VOLUME_OUT_DIR
mkdir -p $RUNNER_OUT_DIR
mkdir -p $FIGURES_OUT_DIR

export JAVA_HOME=$JVBENCH_JAVA_HOME
export PATH=$JAVA_HOME/bin:$PATH

benchmark_runner_folder=$(pwd)/benchmark_runner

# python3.9 $benchmark_runner_folder/runner.py -o $RUNNER_OUT_DIR -m dockerimg -conf $benchmark_runner_folder/configurations/$mode/conf.json -jdk $JVBENCH_JAVA_HOME -jvb $JVBENCH_JAR
# python3.9 $benchmark_runner_folder/runner.py -pl fma indexInRange pow -p -o $RUNNER_OUT_DIR -m dockerimg -conf $benchmark_runner_folder/configurations/$mode/conf.json -jdk $JVBENCH_JAVA_HOME -jvb $JVBENCH_JAR

python3.9 $benchmark_runner_folder/runner.py -prof pin -o $RUNNER_OUT_DIR -m dockerimg -conf $benchmark_runner_folder/configurations/$mode/conf.json -jdk $JVBENCH_JAVA_HOME -jvb $JVBENCH_JAR
python3.9 $benchmark_runner_folder/runner.py -prof pin -pl fma indexInRange pow -p -o $RUNNER_OUT_DIR -m dockerimg -conf $benchmark_runner_folder/configurations/$mode/conf.json -jdk $JVBENCH_JAVA_HOME -jvb $JVBENCH_JAR


export JAVA_HOME=$JVBENCH_JAVA_HOME_XOR
export PATH=$JAVA_HOME/bin:$PATH
export JVBENCH_JAR=$JVBENCH_XOR_JAR

python3.9 $benchmark_runner_folder/runner.py -pl xor -p -o $RUNNER_OUT_DIR -m dockerimg -conf $benchmark_runner_folder/configurations/$mode/xor_conf.json -jdk $JVBENCH_JAVA_HOME_XOR -jvb $JVBENCH_XOR_JAR

cd postprocessing
python3.9 main.py -pprx new -i $RUNNER_OUT_DIR -o $FIGURES_OUT_DIR

# Move pin results csv to output folder
mv /artifact/results $PIN_RESULTS_DIR

echo
echo
echo "=============================================="
echo "             Evaluation completed             "
echo "=============================================="
echo
echo
