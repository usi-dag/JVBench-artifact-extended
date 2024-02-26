import os
import argparse


def run():
    BENCHMARKS = [
        'axpy',
        'blackscholes',
        'canneal',
        'jacobi2d',
        'lavaMD',
        'particlefilter',
        'pathfinder',
        'streamcluster',
        'somier',
        'swaptions'
    ]
    PATTERNS = [
        'fma', 
        'indexInRange', 
        'pow', 
        'xor'
    ]

    parser = argparse.ArgumentParser(description='Command line to run Benchmark suite configuration')

    parser.add_argument('-prof', '--profiler', choices=['jfr', 'gc', 'stack', 'perfasm', 'pin'], help='run the benchmark with the '
                                                                                               'selected profiler')
    parser.add_argument('-bm', '--benchmark', nargs='*', help='Run the following benchmarks', default=BENCHMARKS, choices=BENCHMARKS)
    parser.add_argument('-ex', '--exclude', nargs='*', help='exclude the following benchmarks', choices=BENCHMARKS,
                        default=[])
    parser.add_argument('-o', '--output-dir', help='path to save benchmark result', default='result')
    parser.add_argument('-m', '--machine', help='name of the machine', default='local')
    parser.add_argument('-p', '--pattern', help='execute the pattern benchmark', action='store_true')
    parser.add_argument('-pl', '--pattern-list', nargs='*', help='select pattern subset', default=PATTERNS, choices=PATTERNS)
    parser.add_argument('-jA', '--jvm-arguments', help='additional jvm arguments', default='')
    parser.add_argument('-conf', '--configuration', help='path to the benchmark configuration',
                                                    default=os.path.dirname(__file__) + os.sep + 'full' +  os.sep + 'conf.json')
    parser.add_argument('-jdk', '--jdk-home', help='path to the JDK to use', default='$JAVA_HOME')
    parser.add_argument('-jvb', '--jvbench-jar', help='path to JVBench.jar', default='$JVBENCH_JAR')

    args = parser.parse_args()

    if args.pattern:
        args.output_dir = os.path.join(args.output_dir, args.machine, 'pattern')
    else:
        args.output_dir = os.path.join(args.output_dir, args.machine, 'benchmark')

    return args
