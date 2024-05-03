import os
import csv
import pandas as pd
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
            elif collecting and line.startswith("  mean ="): # Append the mean value as the last iteration -> Later renamed to "MEAN"
                mean = line.split("=")[1].strip().split(" ")[0]
                iteration_times.append(mean)
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
                if i == num_iterations - 1:
                    row = ["MEAN"]  # Rename the last iteration to "MEAN"
                else:
                    row = [i + 1]  # Iteration number starts from 1
                for variant in sorted(variants.keys()):
                    row.append(variants[variant][i])
                writer.writerow(row)
                
def parse_execution_times():
    tools = ["pin_vectorial", "pin_total", "performance"]
    types  = ["benchmark", "pattern"]
    output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total", "performance" : "no"}
    for tool in tools:
        print(f"Parsing execution times for {tool}...")
        for type in types:
            base_directory = f"../output/short/data/jdk19/dockerimg/{type}/{tool}"
            latest_directory = find_latest_directory(base_directory)
            results = process_benchmarks(latest_directory)
            output_dir = f"execution_times_{output_name[tool]}_profiler"
            save_results(results, output_dir)
        print(f"Saved in {output_dir}")
            
def compute_overheads():
    denominator_dir = "execution_times_no_profiler"
    
    tools = ["pin_vectorial", "pin_total"]
    output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total"}
    
    for tool in tools:
        print(f"Computing execution overheads for profiler {tool} vs no profiler...")
        numerator_dir = f"execution_times_{output_name[tool]}_profiler"
        output_dir = f"overheads_{output_name[tool]}_profiler"

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # List all files in the total profiler directory
        total_files = os.listdir(numerator_dir)

        for file in total_files:
            profiler_file_path = os.path.join(numerator_dir, file)
            no_profiler_file_path = os.path.join(denominator_dir, file)

            # Check if the corresponding file exists in the no_profiler directory
            if os.path.exists(no_profiler_file_path):
                # Read both files
                df_profiler = pd.read_csv(profiler_file_path)
                df_no_profiler = pd.read_csv(no_profiler_file_path)

                # Compute overheads
                overheads = df_profiler.copy()
                for col in df_profiler.columns:
                    if col != 'Iteration':
                        try:
                            overheads[col] = df_profiler[col] / df_no_profiler[col]
                        except:
                            overheads[col] = "N/A" # Sometimes we don't have the same benchmark in both directories e.g. xorPublic in no profiler and indexInRange in total and vectorial profilers

                # Write the result to a new file in the output directory
                output_file_path = os.path.join(output_dir, file)
                overheads.to_csv(output_file_path, index=False)
                
        print(f"Saved in {output_dir}")
    
        
def main():
    parse_execution_times()
    compute_overheads()
    

if __name__ == "__main__":
    main()
