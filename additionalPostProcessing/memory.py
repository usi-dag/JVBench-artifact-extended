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

def save_results(results, file_name):
    output_dir = "graphData"
    # Create the directory for the results
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)
    
    gc_types = ["alloc.rate.norm", "count", "time"]
    
    for gc_type in gc_types:
        output_file = f"gc_{gc_type}.csv"
        benchmarks = set()
        data = {}
        
        for key in results.keys():
            if gc_type in key:
                benchmark, mode = key.split(":·gc.")
                benchmark = benchmark.split('.')[2].split('Benchmark')[0]
                benchmark = benchmark.lower()
                benchmarks.add(benchmark)
                if benchmark not in data:
                    data[benchmark] = {}
                data[benchmark][mode] = results[key]
        
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["benchmark", "autoVec", "explicitVec", "fullVec", "serial"])
            
            for benchmark in benchmarks:
                row = [benchmark]
                for mode in ["autoVec", "explicitVec", "fullVec", "serial"]:
                    print(data[benchmark])
                    row.append(data[benchmark].get(mode, ""))
                writer.writerow(row)
        
    
            
                
def parse_memory_values():
    tools = ["pin_vectorial", "pin_total", "performance"]
    types  = ["benchmark"]
    # types  = ["benchmark", "pattern"]
    output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total", "performance" : "no"}
    for tool in tools:
        print(f"Parsing memory values for {tool}...")
        for type in types:
            base_directory = f"../output/short/data/jdk19/dockerimg/{type}/{tool}"
            latest_directory = find_latest_directory(base_directory)
            results = process_benchmarks(latest_directory)
            print("\n")
            print(results)
            file_name = f"memory_{output_name[tool]}_profiler.csv"
            save_results(results, file_name)
        # print(f"Saved in {output_dir}")
            
# WARNING: this is a copy of the execution_overheads.py function, haven't changed anything about it yet
# def compute_overheads():
#     denominator_dir = "memory_no_profiler"
    
#     tools = ["pin_vectorial", "pin_total"]
#     output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total"}
    
#     for tool in tools:
#         print(f"Computing execution overheads for profiler {tool} vs no profiler...")
#         numerator_dir = f"memory_{output_name[tool]}_profiler"
#         output_dir = f"overheads_{output_name[tool]}_profiler"

#         # Ensure output directory exists
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)

#         # List all files in the total profiler directory
#         total_files = os.listdir(numerator_dir)

#         for file in total_files:
#             profiler_file_path = os.path.join(numerator_dir, file)
#             no_profiler_file_path = os.path.join(denominator_dir, file)

#             # Check if the corresponding file exists in the no_profiler directory
#             if os.path.exists(no_profiler_file_path):
#                 # Read both files
#                 df_profiler = pd.read_csv(profiler_file_path)
#                 df_no_profiler = pd.read_csv(no_profiler_file_path)

#                 # Compute overheads
#                 overheads = df_profiler.copy()
#                 for col in df_profiler.columns:
#                     if col != 'Iteration':
#                         try:
#                             overheads[col] = df_profiler[col] / df_no_profiler[col]
#                         except:
#                             overheads[col] = "N/A" # Sometimes we don't have the same benchmark in both directories e.g. xorPublic in no profiler and indexInRange in total and vectorial profilers

#                 # Write the result to a new file in the output directory
#                 output_file_path = os.path.join(output_dir, file)
#                 overheads.to_csv(output_file_path, index=False)
                
#         print(f"Saved in {output_dir}")
    
def merge_benchmark_files():
    # Define the directory containing the CSV files
    input_directory = 'percentage_vectorial_instructions'
    output_directory = 'graphData'
    output_file = os.path.join(output_directory, 'merged_memory_data.csv')

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Initialize an empty list to store DataFrames
    data_frames = []

    # Iterate over all files in the directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith('.csv') and 'Pattern' not in file_name:
            # Construct full file path
            file_path = os.path.join(input_directory, file_name)
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            
            # Add a new column for the benchmark (file name without extension)
            benchmark = os.path.splitext(file_name)[0]
            benchmark = benchmark.split('.')[2].split('Benchmark')[0]
            benchmark = benchmark.lower()
            df['benchmark'] = benchmark
            
            # Append the DataFrame to the list
            data_frames.append(df)

    # Concatenate all DataFrames in the list
    merged_df = pd.concat(data_frames, ignore_index=True)

    # Reorder columns to have 'benchmark' first
    merged_df = merged_df[['benchmark', 'autoVec', 'explicitVec', 'fullVec']]

    # Convert values to percentages and format to two decimal places
    merged_df['autoVec'] = (merged_df['autoVec'] * 100).map('{:.4f}'.format)
    merged_df['explicitVec'] = (merged_df['explicitVec'] * 100).map('{:.4f}'.format)
    merged_df['fullVec'] = (merged_df['fullVec'] * 100).map('{:.4f}'.format)

    # Sort the DataFrame by the 'benchmark' column
    merged_df.sort_values(by='benchmark', inplace=True)

    # Save the merged DataFrame to a new CSV file in the output directory
    merged_df.to_csv(output_file, index=False)

    print(f'Merged CSV saved as {output_file}')
        
def merge_csv_files(directory, output_name):
    
    # Output file path
    print(directory)
    output_file = f"graphData/merged_overheads_{output_name}_profiler.csv"
    
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
    
    # Initialize an empty list to store the merged rows
    merged_rows = []
    
    # Iterate over each CSV file
    for file in csv_files:
        file_path = os.path.join(directory, file)
        
        # Read the CSV file
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            
            # Skip the header row
            next(reader)
            
            # Iterate over each row in the CSV file
            for row in reader:
                # Check if the row contains "MEAN" in the "Iteration" column
                if row[0] == "MEAN":
                    # Format the numbers to have only 4 values after the comma
                    formatted_row = [f"{float(value):.4f}" for value in row[1:]]
                    
                    # Get the benchmark name from the file name (excluding the ".csv" extension)
                    benchmark_name = os.path.splitext(file)[0]
                    benchmark_name = benchmark_name.split('Benchmark')[0]
                    benchmark_name = benchmark_name.lower()
                    
                    # Add the benchmark name as the first column
                    formatted_row.insert(0, benchmark_name)
                    
                    merged_rows.append(formatted_row)
    
    merged_rows.sort(key=lambda row: row[0])
    
    # Write the merged rows to the output file
    with open(output_file, "w", newline="") as output_csv:
        writer = csv.writer(output_csv)
        
        # Write the header row (including the "benchmark" column)
        writer.writerow(["benchmark", "autoVec", "explicitVec", "fullVec", "serial"])
        
        # Write the merged rows
        writer.writerows(merged_rows)
    
    print(f"Merged CSV files saved to: {output_file}")
    
def main():
    parse_memory_values()
    # compute_overheads()
    merge_benchmark_files()
    
    input_directories = ["overheads_total_profiler", "overheads_vectorial_profiler"]
    output_name = {"overheads_total_profiler" : "total", "overheads_vectorial_profiler" : "vectorial"}
    for dir in input_directories:
        merge_csv_files(dir, output_name[dir])

if __name__ == "__main__":
    main()
