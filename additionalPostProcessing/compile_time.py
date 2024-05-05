import os
import csv
import pandas as pd
from datetime import datetime

def parse_compilation_times(file_path):
    compilation_times = {}
    with open(file_path, 'r') as file:
    # with open('/home/thomas/Documents/JVBench-artifact-extended/additionalPostProcessing/temp.txt', 'r') as file:
        lines = file.readlines()
        benchmark_name = None
        collecting = False

        for line in lines:
            if line.startswith("# Benchmark: "):
                benchmark_name = line.split("# Benchmark: ")[1].strip()
                collecting = True
            elif collecting and line.startswith("    C2 Compile Time:"):
                time = line.split(":")[1].strip().split(" ")[0] # SECONDS
                compilation_times[benchmark_name] = time
                collecting = False

    return compilation_times


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
                benchmark_results = parse_compilation_times(txt_file_path)
                all_benchmark_results.update(benchmark_results)
    return all_benchmark_results

def save_results(results, output_dir):
    # Create the directory for the results
    os.makedirs(output_dir, exist_ok=True)
    
    # Organize data by benchmark type
    organized_results = {}
    for key, time in results.items():
        parts = key.split('.')
        benchmark_type = '.'.join(parts[:3])
        variant = parts[-1]
        
        if benchmark_type not in organized_results:
            organized_results[benchmark_type] = {}
        organized_results[benchmark_type][variant] = time
        
    # Write results to CSV files
    for benchmark_type, variants in organized_results.items():
        file_name = f"{benchmark_type.split('.')[-1]}.csv"
        file_path = os.path.join(output_dir, file_name)
        
        # Determine the order of columns based on variant names
        columns = sorted(variants.keys())

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            
            # Write the times in the predefined order
            row = [variants.get(variant, '') for variant in columns]
            writer.writerow(row)
                
def merge_benchmark_files(directory='.'):
    # List all files in the directory
    files = os.listdir(directory)
    benchmarks = set()

    # Identify all benchmarks
    for file in files:
        if 'Benchmark.csv' in file and 'PatternBenchmark' not in file:
            benchmark_name = file.split('Benchmark.csv')[0]
            benchmarks.add(benchmark_name)

    # Process each benchmark
    for benchmark_name in benchmarks:
        benchmark_file = f"{benchmark_name}Benchmark.csv"
        pattern_file = f"{benchmark_name}PatternBenchmark.csv"
        merged_file = f"{benchmark_name}MergedBenchmark.csv"

        benchmark_path = os.path.join(directory, benchmark_file)
        pattern_path = os.path.join(directory, pattern_file)
        merged_path = os.path.join(directory, merged_file)

        # Check if both files exist
        if os.path.exists(benchmark_path) and os.path.exists(pattern_path):
            # Read data from both files
            with open(benchmark_path, mode='r', newline='') as bf, open(pattern_path, mode='r', newline='') as pf:
                benchmark_reader = csv.reader(bf)
                pattern_reader = csv.reader(pf)
                benchmark_header = next(benchmark_reader)
                pattern_header = next(pattern_reader)

                # Combine headers and prepare to write to the merged file
                combined_header = benchmark_header + pattern_header

                with open(merged_path, mode='w', newline='') as mf:
                    writer = csv.writer(mf)
                    writer.writerow(combined_header)  # Write the combined header

                    # Write benchmark file contents
                    for row in benchmark_reader:
                        pattern_row = next(pattern_reader)
                        combined_row = row + pattern_row
                        writer.writerow(combined_row)

            # Optionally, rename the merged file to replace the original benchmark file
            os.remove(benchmark_path)  # Remove the original benchmark file
            os.remove(pattern_path)
            os.rename(merged_path, benchmark_path)
            print(f"Merged file created as {benchmark_path}")
        else:
            print(f"Failed to merge '{benchmark_path}' and '{pattern_path}'. One or both files for {benchmark_name} do not exist.")


                
def parse_compile_times():
    tools = ["performance"]
    output_name = {"performance" : "no"}
    types = {"benchmark", "pattern"}
    for tool in tools:
        for type in types:
            print(f"Parsing compilation times for {tool}...")
            base_directory = f"../output/short/data/jdk19/dockerimg/{type}/{tool}"
            latest_directory = find_latest_directory(base_directory)
            results = process_benchmarks(latest_directory)
            output_dir = f"compilation_times_{output_name[tool]}_profiler"
            save_results(results, output_dir)
        print(f"Saved parsed times in {output_dir}")
            
def compute_overheads():
    output_dir = "compile_overheads_no_profiler"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    input_dir = "compilation_times_no_profiler"
    for filename in os.listdir(input_dir):
        input_file_path = os.path.join(input_dir, filename)
        
        # Check if the file is a CSV
        if filename.endswith('.csv'):
            with open(input_file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                data = list(reader)

            # Prepare data for the output file
            output_data = []
            for row in data:
                serial_time = float(row['serial'])
                overheads = {}
                for key, value in row.items():
                    if key != 'serial':
                        overheads[key] = float(value) / serial_time
                output_data.append(overheads)

            # Write the overheads to a new CSV file in the output directory
            output_file_path = os.path.join(output_dir, filename)
            with open(output_file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=output_data[0].keys())
                writer.writeheader()
                writer.writerows(output_data)
                
    print(f"Saved overheads in {output_dir}")

    
        
def main():
    parse_compile_times()
    merge_benchmark_files("compilation_times_no_profiler")
    compute_overheads()
    

if __name__ == "__main__":
    main()
