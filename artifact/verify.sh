#!/bin/bash

. utils

echo
echo "This command will verify the installation of the artifact by running other scripts and checking the exit codes."
echo "Approximate running time: 5 minutes"
yes_or_no "Do you wish to continue?"
if [ $? -ne 0 ]; then
    echo 
    echo "Aborted"
    echo
    exit 4
fi
echo


INSTALLATION_ERROR_MESSAGE="\n\n==============================================\n      ERROR : cannot verify installation      \n==============================================\n\n"

echo "Verifying JDKs installation..."
$JVBENCH_JAVA_HOME/bin/java -version
if [ $? -ne 0 ]; then
    echo -e $INSTALLATION_ERROR_MESSAGE
    exit 13
fi
$JVBENCH_JAVA_HOME_XOR/bin/java -version
if [ $? -ne 0 ]; then
    echo -e $INSTALLATION_ERROR_MESSAGE
    exit 13
fi

echo "Verifying JVBench installation..."
$JVBENCH_JAVA_HOME/bin/java --add-modules jdk.incubator.vector -cp $JVBENCH_JAR -jar $JVBENCH_JAR -f 1 -wi 1 -i 1 -bm SingleShotTime "axpy"
if [ $? -ne 0 ]; then
    echo -e $INSTALLATION_ERROR_MESSAGE
    exit 13
fi
$JVBENCH_JAVA_HOME_XOR/bin/java --add-modules jdk.incubator.vector -cp $JVBENCH_XOR_JAR -jar $JVBENCH_XOR_JAR -f 1 -wi 1 -i 1 -bm SingleShotTime "axpy"
if [ $? -ne 0 ]; then
    echo -e $INSTALLATION_ERROR_MESSAGE
    exit 13
fi

echo "Verifying postprocessing scripts installation..."
cd postprocessing
python3.9 main.py --help
if [ $? -ne 0 ]; then
    echo -e $INSTALLATION_ERROR_MESSAGE
    exit 13
fi
cd ..

echo "Verifying benchmark runner scripts installation..."
cd benchmark_runner
python3.9 runner.py --help
if [ $? -ne 0 ]; then
    echo -e $INSTALLATION_ERROR_MESSAGE
    exit 13
fi
cd ..

echo
echo
echo "============================================="
echo "     The artifact is correctly installed     "
echo "============================================="
echo
echo
