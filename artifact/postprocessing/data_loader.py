import os
import re
import sys
import glob
import pandas as pd


def load(dir):
    file_pattern = re.compile(
        os.sep + 'jdk(\d+)' + os.sep + '(\w+)' + os.sep + '.*?' + os.sep + '(\w+)' + os.sep + '[^' + os.sep + ']*?\\.txt')
    benchmark_folder_pattern = re.compile('(\w+)$')
    benchmark_pattern = re.compile('# Benchmark: ([\.\w]+)')
    benchmark_separator_pattern = re.compile('(?=# Benchmark: [\.\w]+)')
    score_pattern = re.compile('^Iteration\s+(\d+):\s+(?:\(benchmark timed out, interrupted\s+\d+\s+times\)\s+)?(\d+(?:\.\d+)?)\s+', re.MULTILINE)

    data = {
        'Benchmark': [],
        'Score': [],
        'jdk': [],
        'machine': [],
        'benchmark': [],
        'iteration': [],
    }

    pathname = os.path.join(dir, '**', '*.txt')
    files = glob.glob(pathname, recursive=True)
    for file in files:
        match = re.search(file_pattern, file)

        if not match:
            continue

        with open(file) as f:
            file_data = f.read()

            for chunk in benchmark_separator_pattern.split(file_data):
                chunk_match = re.search(benchmark_pattern, chunk)

                if not chunk_match:
                    continue

                Benchmark = chunk_match.group(1)
                jdk = match.group(1)
                machine = match.group(2)
                benchmark = match.group(3)

                for iteration_score in score_pattern.findall(chunk):
                    data['Benchmark'].append(Benchmark)
                    data['Score'].append(float(iteration_score[1]))
                    data['jdk'].append(jdk)
                    data['machine'].append(machine)
                    data['benchmark'].append(benchmark)
                    data['iteration'].append(int(iteration_score[0]))

    df = pd.DataFrame(data)
    df['config'] = df['Benchmark'].apply(lambda x: re.search(benchmark_folder_pattern, x).group(0))
    
    return df
