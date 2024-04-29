import os
import csv
from datetime import datetime

def parse_benchmark_times(file_path):
    benchmark_times = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        benchmark_name = None
        iteration_times = []
        collecting = False

        for line in lines:
            if line.startswith("# Benchmark: "):
                if benchmark_name and iteration_times:
                    benchmark_times[benchmark_name] = iteration_times
                benchmark_name = line.split("# Benchmark: ")[1].strip()
                iteration_times = []
                collecting = True
            elif collecting and line.startswith("Iteration"):
                time = line.split(":")[1].strip().split(" ")[0]
                iteration_times.append(time)
            elif benchmark_name and benchmark_name in line:
                if iteration_times:
                    benchmark_times[benchmark_name] = iteration_times
                collecting = False

        # Add the last benchmark data
        if benchmark_name and iteration_times:
            benchmark_times[benchmark_name] = iteration_times

    return benchmark_times


def find_latest_directory(base_path):
    dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    latest_dir = max(dirs, key=lambda d: datetime.strptime(d, "%Y-%m-%d_%H:%M:%S"))
    return os.path.join(base_path, latest_dir)

def process_benchmarks(directory):
    all_benchmark_results = {}
    for benchmark_dir in os.listdir(directory):
        full_path = os.path.join(directory, benchmark_dir)
        if os.path.isdir(full_path):
            txt_file = next((f for f in os.listdir(full_path) if f.endswith('.txt')), None)
            if txt_file:
                txt_file_path = os.path.join(full_path, txt_file)
                benchmark_results = parse_benchmark_times(txt_file_path)
                all_benchmark_results.update(benchmark_results)
    return all_benchmark_results

def save_results(results, output_dir):
    # Create the directory for the results
    os.makedirs(output_dir, exist_ok=True)
    
    # Organize data by benchmark type
    organized_results = {}
    for key, times in results.items():
        parts = key.split('.')
        benchmark_type = '.'.join(parts[:3])
        variant = parts[-1]
        
        if benchmark_type not in organized_results:
            organized_results[benchmark_type] = {}
        organized_results[benchmark_type][variant] = times
    
    # Write results to CSV files
    for benchmark_type, variants in organized_results.items():
        file_name = f"{benchmark_type.split('.')[-1]}.csv"
        file_path = os.path.join(output_dir, file_name)
        
        # Determine the order of columns based on variant names
        columns = ['Iteration'] + sorted(variants.keys())
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            
            # Assuming all variants have the same number of iterations
            num_iterations = len(next(iter(variants.values())))
            for i in range(num_iterations):
                row = [i + 1]  # Iteration number starts from 1
                for variant in sorted(variants.keys()):
                    row.append(variants[variant][i])
                writer.writerow(row)
                
def parse_execution_times():
    tools = ["pin_vectorial", "pin_total", "performance"]
    types  = ["benchmark", "pattern"]
    output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total", "performance" : "no"}
    for tool in tools:
        for type in types:
            base_directory = f"../output/short/data/jdk19/dockerimg/{type}/{tool}"
            latest_directory = find_latest_directory(base_directory)
            results = process_benchmarks(latest_directory)
            output_dir = f"execution_times_{output_name[tool]}_profiler"
            save_results(results, output_dir)
            
def compute_overheads():
    
        
def main():
    parse_execution_times()
    compute_overheads()
    

if __name__ == "__main__":
    main()
