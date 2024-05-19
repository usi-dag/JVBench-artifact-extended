import os
import csv
import pandas as pd
from datetime import datetime

def parse_benchmark_files(file_path):
    result = {}
    
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            benchmark = row['Benchmark']
            score = row['Score']
            
            if 'gc.count' in benchmark or 'gc.alloc.rate.norm' in benchmark or 'gc.time' in benchmark:
                result[benchmark] = score
                
                # When gc.count is 0, gc.time is absent. 
                # I add it and set it to 0 as to avoid missing values in the resulting csv
                if 'gc.count' in benchmark and float(score) == 0:
                    tmp_benchmark = benchmark.replace('gc.count', 'gc.time')
                    result[tmp_benchmark] = "0.000000" # Thats how they write their zeros

    return result


def find_latest_directory(base_path):
    dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    latest_dir = max(dirs, key=lambda d: datetime.strptime(d, "%Y-%m-%d_%H:%M:%S"))
    return os.path.join(base_path, latest_dir)

def process_benchmarks(directory):
    all_benchmark_results = {}
    for benchmark_dir in os.listdir(directory):
        full_path = os.path.join(directory, benchmark_dir)
        if os.path.isdir(full_path):
            csv_file = next((f for f in os.listdir(full_path) if f.endswith('.csv')), None)
            if csv_file and csv_file:
                csv_file_path = os.path.join(full_path, csv_file)
                benchmark_results = parse_benchmark_files(csv_file_path)
                all_benchmark_results.update(benchmark_results)
    return all_benchmark_results

def save_results(results, file_name, gc_type, avx_type):
    # Create a dictionary to store the parsed results
    parsed_results = {}

    # Iterate over each key-value pair in the results dictionary
    for key, value in results.items():
        # Check if the key contains the specified gc_type
        if gc_type in key:
            # Extract the benchmark name from the key
            benchmark = key.split(":")[0]
            benchmark = benchmark.split('.')[1]
            
            # Initialize the benchmark entry in the parsed_results dictionary if it doesn't exist
            if benchmark not in parsed_results:
                parsed_results[benchmark] = {"autoVec": "", "explicitVec": "", "fullVec": "", "serial": ""}

            # Fill the corresponding column based on the key
            if "autoVec" in key:
                parsed_results[benchmark]["autoVec"] = value
            elif "explicitVec" in key:
                parsed_results[benchmark]["explicitVec"] = value
            elif "fullVec" in key:
                parsed_results[benchmark]["fullVec"] = value
            elif "serial" in key:
                parsed_results[benchmark]["serial"] = value

    # Create the "gc_memory" directory if it doesn't exist
    os.makedirs(f"{avx_type}/gc_memory", exist_ok=True)
    parsed_results = dict(sorted(parsed_results.items()))

    # Write the parsed results to a CSV file in the "gc_memory" directory
    file_path = os.path.join(f"{avx_type}/gc_memory", file_name)
    with open(file_path, "w", newline="") as csv_file:
        fieldnames = ["benchmark", "autoVec", "explicitVec", "fullVec", "serial"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for benchmark, values in parsed_results.items():
            row = {"benchmark": benchmark, **values}
            writer.writerow(row)
        
def parse_memory_values(avx_type):
    tools = ["pin_vectorial", "pin_total", "performance"]
    types  = ["benchmark"]
    # types  = ["benchmark", "pattern"]
    gc_types = ["alloc.rate.norm", "count", "time"]
    output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total", "performance" : "no"}
    for tool in tools:
        print(f"Parsing memory values for {tool}...")
        for type in types:
            base_directory = f"../precollected_data/{avx_type}/short/data/jdk19/dockerimg/{type}/{tool}"
            latest_directory = find_latest_directory(base_directory)
            results = process_benchmarks(latest_directory)
            for gc_type in gc_types:
                file_name = f"{output_name[tool]}_profiler_memory_gc.{gc_type}"
                file_name = file_name.replace(".", "_")
                file_name = file_name + ".csv"
                save_results(results, file_name, gc_type, avx_type)
        # print(f"Saved in {output_dir}")
            
def compute_overheads(avx_type):
    # Check if the source directory exists
    source_dir = f'{avx_type}/gc_memory'
    if not os.path.exists(source_dir):
        print(f"Directory {source_dir} does not exist.")
        return
    
    # Create the target directory if it doesn't exist
    target_dir = f'{avx_type}/graphData'
    os.makedirs(target_dir, exist_ok=True)
    
    # Iterate over each file in the source directory
    for filename in os.listdir(source_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(source_dir, filename)
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Compute overheads
            df['autoVec'] = df['autoVec'] / df['serial']
            df['explicitVec'] = df['explicitVec'] / df['serial']
            df['fullVec'] = df['fullVec'] / df['serial']
            
            # Drop the 'serial' column as it's not needed in the output
            df.drop(columns=['serial'], inplace=True)
            
            # Save the modified DataFrame to a new file in the target directory
            output_name = filename.replace('memory_gc_', 'overhead_gc_')
            output_file_path = os.path.join(target_dir, output_name)
            print(output_file_path)
            df.to_csv(output_file_path, index=False)
            print(f"Processed and saved data to {output_file_path}")

        
def main():
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    for avx_type in avx_types:
        parse_memory_values(avx_type)
        compute_overheads(avx_type)

if __name__ == "__main__":
    main()
