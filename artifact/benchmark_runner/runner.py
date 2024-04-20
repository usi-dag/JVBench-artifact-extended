import os
import sys
import cli
import json
import subprocess
from datetime import datetime


def capfirst(s):
    return s[:1].upper() + s[1:]


def helper_benchmark_options(execution, jdk_home, jvbench_jar, benchmark, jvm_arguments, args, output_path):
    # TODO se pin la prima, senno la seconda
    # How I run pin personally:
    # pin-3.28-98749-g6643ecee5-gcc-linux/pin -t pin-3.28-98749-g6643ecee5-gcc-linux/source/tools/MyPinTool/obj-intel64/MyPinTool.so -- java -cp plugin/SocketPlugin.jar:JVBench/target/JVBench-1.0.1.jar --add-modules jdk.incubator.vector -Dbenchmark.plugin=jvbench.plugin.SocketPlugin org.openjdk.jmh.Main "AxpyBenchmark"
    if 'pin' in args['name'] and 'xor' not in jvbench_jar.lower():
        # Adds flags for Log Compilation files (first flag is need to use it)
        # And -cp to my plugin etc
        return args['prefix'] + jdk_home + '/bin/java -XX:+UnlockDiagnosticVMOptions -XX:+LogCompilation -XX:LogFile=' + output_path + '/' + benchmark + '_LogCompilation_%p.log' + \
            ' -cp ' + args['classpath'] + ':' + jvbench_jar + \
            ' --add-modules jdk.incubator.vector -Dbenchmark.plugin=jvbench.plugin.SocketPlugin' + \
            jvm_arguments + \
            ' -jar ' + jvbench_jar + ' ' + \
            '-f' + str(execution['fork']) + \
            ' -wi ' + str(execution['warmup_iterations']) + \
            ' -i' + str(execution['iterations']) + \
            ' -bm ' + execution['mode'] + \
            ' ' + '"' + benchmark + '" ' + \
            '-rf csv -rff "' + output_path + '/' + benchmark + '.csv" | tee ' + output_path + '/' + benchmark + '.txt'
        
    return jdk_home + '/bin/java --add-modules jdk.incubator.vector ' + \
        ' -cp ' + jvbench_jar + ' ' + \
        jvm_arguments + \
        ' -jar ' + jvbench_jar + ' ' + \
        '-f' + str(execution['fork']) + \
        ' -wi ' + str(execution['warmup_iterations']) + \
        ' -i' + str(execution['iterations']) + \
        ' ' +  args['options'] + \
        ' -bm ' + execution['mode'] + \
        ' ' + '"' + benchmark + '" ' + \
        '-rf csv -rff "' + output_path + '/' + benchmark + '.csv" | tee ' + output_path + '/' + benchmark + '.txt'
        


def select_profiler(profiler_name, path=None):
    # TODO template da inserire in tutti gli if, aggiungi else per pin
    args = {
        "name": profiler_name,   
        "prefix": '', # solo per pin
        "classpath": '',  # solo per pin
        "options": '' # tutti tranne per pin
    }
    if profiler_name == 'jfr':
        args["options"] = '-prof jfr' if path is None else '-prof jfr:dir="{}"'.format(path)
    elif profiler_name == 'gc':
        args["options"] = '-prof gc'
    elif profiler_name == 'stack':
        args["options"] = '-prof stack'
    elif profiler_name == 'perfasm':
        args["options"] = ' -v EXTRA '
    elif profiler_name == 'pin_vectorial':
        args["prefix"] = '/artifact/pin-3.28-98749-g6643ecee5-gcc-linux/pin -t /artifact/pin-3.28-98749-g6643ecee5-gcc-linux/source/tools/VectorialInstructionsCounter/obj-intel64/VectorialInstructionsCounter.so -- '
        args["classpath"] = '/artifact/SocketPlugin.jar'
    elif profiler_name == 'pin_total':
        args["prefix"] = '/artifact/pin-3.28-98749-g6643ecee5-gcc-linux/pin -t /artifact/pin-3.28-98749-g6643ecee5-gcc-linux/source/tools/TotalInstructionsCounter/obj-intel64/TotalInstructionsCounter.so -- '
        args["classpath"] = '/artifact/SocketPlugin.jar'
    
    return args


def benchmark_configuration(benchmark, jdk_home, jvbench_jar, jvm_arguments, profiler, output, configuration):
    benchmark_input = configuration[benchmark]['input']
    benchmark_execution = configuration[benchmark]['execution']
    benchmark_print_compilation = configuration[benchmark]['printCompilation']
    assembly_output = f"-XX:+UnlockDiagnosticVMOptions -XX:+TieredCompilation '-XX:CompileCommand=print,{benchmark_print_compilation}' -XX:-UseCompressedOops" if profiler == 'perfasm' else ''
    jvm_arguments = jvm_arguments + ' ' + benchmark_input + ' ' + assembly_output
    prof = select_profiler(profiler, output)
    benchmark_name = capfirst(benchmark) + 'Benchmark'
    return [helper_benchmark_options(benchmark_execution, jdk_home, jvbench_jar, benchmark_name, jvm_arguments, prof, output)]


def benchmark_configuration_pattern(benchmark, jdk_home, jvbench_jar, jvm_arguments, profiler, output, configuration, patterns_list):
    benchmark_input = configuration[benchmark]['input']
    benchmark_patterns = [pattern for pattern in configuration[benchmark]['patterns'] for p in patterns_list if p in pattern['name']]

    benchmark_print_compilation = configuration[benchmark]['printCompilation']
    assembly_output = f"-XX:+UnlockDiagnosticVMOptions -XX:+TieredCompilation '-XX:CompileCommand=print,{benchmark_print_compilation}' -XX:-UseCompressedOops" if profiler == 'perfasm' else ''
    jvm_arguments = jvm_arguments + ' ' + benchmark_input + ' ' + assembly_output
    prof = select_profiler(profiler, output)
    patterns = []
    for pattern in benchmark_patterns:
        benchmark_execution = pattern['execution']
        name = pattern['name']
        benchmark_name = capfirst(benchmark) + 'PatternBenchmark.' + name
        patterns.append(helper_benchmark_options(benchmark_execution, jdk_home, jvbench_jar, benchmark_name, jvm_arguments, prof, output))
    return patterns


def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def main():
    args = cli.run()
    
    current_date = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    benchmarks = [benchmark for benchmark in args.benchmark if benchmark not in args.exclude]
    benchmark_path = os.path.join(args.output_dir,
                                  args.profiler if args.profiler is not None else 'performance',
                                  str(current_date)
                                  )

    execution_plan = {
        'total': len(args.benchmark),
        'benchmark': args.benchmark,
        'exclude': args.exclude,
        'completed': [],
        'todo': benchmarks,
        'output_dir': benchmark_path,
        'profiler': args.profiler,
        'pattern': args.pattern,
        'pattern_list': args.pattern_list,
        'jvm_arguments': args.jvm_arguments,
        'configuration_path': args.configuration,
        'jdk_home': args.jdk_home,
        'jvbench_jar': args.jvbench_jar,
    }

    with open(execution_plan['configuration_path'], 'r') as config_file:
        configuration = json.load(config_file)

    create_folder(execution_plan['output_dir'])

    benchmarks = [benchmark for benchmark in execution_plan['todo']]

    for benchmark in benchmarks:
            print('Starting benchmark', benchmark,
                  'with profiler {}'.format(execution_plan['profiler']) if execution_plan['profiler'] is not None else '',
                  '{}/{}'.format(len(execution_plan['completed']) + 1, execution_plan['total'])
                  )

            output = os.path.join(execution_plan['output_dir'], benchmark)
            create_folder(output)

            if execution_plan['pattern']:
                executions = benchmark_configuration_pattern(benchmark, execution_plan['jdk_home'], execution_plan['jvbench_jar'], execution_plan['jvm_arguments'], execution_plan['profiler'], output, configuration, execution_plan['pattern_list'])
            else:
                executions = benchmark_configuration(benchmark, execution_plan['jdk_home'], execution_plan['jvbench_jar'], execution_plan['jvm_arguments'], execution_plan['profiler'], output, configuration)

            for execution in executions:
                print(execution)
                try:
                    subprocess.run(execution, shell=True, check=True)
                except KeyboardInterrupt as e:
                    print('\nInterrupted')
                    sys.exit(1)

            execution_plan['todo'].pop(0)
            execution_plan['completed'].append(benchmark)

if __name__ == '__main__':
    main()
