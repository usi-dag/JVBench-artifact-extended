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
            if txt_file and txt_file:
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
                
    # Delete all Pattern files (remove this part if you want them )
    for file in os.listdir(output_dir):
        if 'Pattern' in file:
            os.remove(os.path.join(output_dir, file))
            
                
def parse_execution_times(avx_type):
    tools = ["pin_vectorial", "pin_total", "performance"]
    # types  = ["benchmark", "pattern"]
    types  = ["benchmark"] # We dont care about pattern benchmarks
    output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total", "performance" : "no"}
    for tool in tools:
        print(f"Parsing execution times for {tool}...")
        for type in types:
            base_directory = f"../precollected_data/{avx_type}/short/data/jdk19/dockerimg/{type}/{tool}"
            latest_directory = find_latest_directory(base_directory)
            results = process_benchmarks(latest_directory)
            output_dir = f"{avx_type}/execution_times_{output_name[tool]}_profiler"
            save_results(results, output_dir)
        print(f"Saved in {output_dir}")
            
def compute_overheads(avx_type):
    denominator_dir = f"{avx_type}/execution_times_no_profiler"
    
    tools = ["pin_vectorial", "pin_total"]
    output_name = {"pin_vectorial" : "vectorial", "pin_total" : "total"}
    
    for tool in tools:
        print(f"Computing execution overheads for profiler {tool} vs no profiler...")
        numerator_dir = f"{avx_type}/execution_times_{output_name[tool]}_profiler"
        output_dir = f"{avx_type}/overheads_{output_name[tool]}_profiler"

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
    
def merge_benchmark_files(avx_type):
    # Define the directory containing the CSV files
    input_directory = f'{avx_type}/percentage_vectorial_instructions'
    output_directory = f'{avx_type}/graphData'
    output_file = os.path.join(output_directory, 'merged_mean_ratios.csv')

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Initialize an empty list to store DataFrames
    data_frames = []

    # Iterate over all files in the directory
    if not os.path.exists(input_directory):
        raise ValueError("Please use ratios.py before using this file")
    else:
        for file_name in os.listdir(input_directory):
            if file_name.endswith('.csv') and 'Pattern' not in file_name:
                # Construct full file path
                file_path = os.path.join(input_directory, file_name)
                
                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path)
                
                # Add a new column for the benchmark (file name without extension)
                benchmark = os.path.splitext(file_name)[0]
                benchmark = benchmark.split('.')[1]
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
        
def merge_csv_files(directory, output_name, avx_type):
    
    # Output file path
    output_file = f"{avx_type}/graphData/merged_overheads_{output_name}_profiler.csv"
    
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
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    for avx_type in avx_types:
        parse_execution_times(avx_type)
        compute_overheads(avx_type)
        merge_benchmark_files(avx_type)
        
        input_directories = ["overheads_total_profiler", "overheads_vectorial_profiler"]
        output_name = {"overheads_total_profiler" : "total", "overheads_vectorial_profiler" : "vectorial"}
        for dir in input_directories:
            merge_csv_files(f"{avx_type}/{dir}", output_name[dir], avx_type)
            

if __name__ == "__main__":
    main()
