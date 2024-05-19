import os
import pandas as pd
import shutil

def compute_ratios():
    # COMPUTE THE SUM OF VECTORIAL INSTRUCTIONS
    print("Computing the sum of vectorial instructions...")
    # Base directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Step 0: Create directory "sum_vectorial_instructions"
    output_dir = os.path.join(base_dir, "sum_vectorial_instructions")
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Path to the directory "../output/short/pin/results_vectorial_instructions"
    input_dir = os.path.join(base_dir, "../output/short/pin/results_vectorial_instructions")

    # Step 2: For every file in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_dir, filename)

            # Read the CSV file
            df = pd.read_csv(file_path)

            # Step 2a: Path for the new file in the directory "sum_vectorial_instructions"
            output_file_path = os.path.join(output_dir, filename)

            # Step 2b: Sum all the values of each row, excluding the "Iteration" column
            df['Total Vectorial Instructions'] = df.drop('Iteration', axis=1).sum(axis=1).astype(int)

            # Step 4: Store the sum in the column "Total Vectorial Instructions"
            df.to_csv(output_file_path, index=False)

    # COMPUTE THE RATIOS
    print("Computing the ratios...")
    # Create the new directory if it doesn't exist
    output_dir = "ratio_vectorial_total_instructions_raw"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Directories containing the CSV files
    dir_vec_instructions = "sum_vectorial_instructions"
    dir_total_instructions = "../output/short/pin/results_total_instructions"

    # Get the list of files in the vectorial instructions directory
    files = os.listdir(dir_vec_instructions)

    for file in files:
        # Construct file paths
        file_path_vec = os.path.join(dir_vec_instructions, file)
        file_path_total = os.path.join(dir_total_instructions, file)
        
        # Read the CSV files
        df_vec = pd.read_csv(file_path_vec)
        df_total = pd.read_csv(file_path_total)
        
        # Compute the ratio of 'Total Vectorial Instructions' to 'Total Number of (any) instructions'
        total_vectorial_instructions_sum = df_vec['Total Vectorial Instructions'].sum()
        total_instructions_sum = df_total['Total Number of (any) instructions'].sum()

        # Calculate the ratio
        ratio = total_vectorial_instructions_sum / total_instructions_sum
        
        # Create a new DataFrame with the computed ratio
        result_df = pd.DataFrame({
            'Ratio': [ratio]
        })
        
        # Write the result to a new CSV file in the output directory
        output_file_path = os.path.join(output_dir, file)
        result_df.to_csv(output_file_path, index=False)

    # MERGE THE RESULTS
    print("Ratios computed, merging results...")

    # Directory containing the CSV files
    input_directory = "ratio_vectorial_total_instructions_raw"
    output_directory = "percentage_vectorial_instructions"

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Dictionary to hold dataframes for each group
    grouped_dataframes = {}

    # Iterate over each file in the directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            # Construct the full path to the file
            filepath = os.path.join(input_directory, filename)
            
            # Extract the part of the filename up to the third dot
            group_key = '.'.join(filename.split('.')[:3])
            
            # Read the CSV file
            df = pd.read_csv(filepath)
            
            # Rename the 'Ratio' column to include the part of the filename from the third dot to the first underscore
            new_ratio_column_name = filename.split('.')[3].split('_')[0]
            df.rename(columns={'Ratio': new_ratio_column_name}, inplace=True)
            
            # If the group key is new, initialize a new dataframe
            if group_key not in grouped_dataframes:
                grouped_dataframes[group_key] = df
            else:
                # Otherwise, merge this dataframe with the existing one for the group
                grouped_dataframes[group_key] = pd.concat([grouped_dataframes[group_key], df], axis=1)
            
            # Delete the file after it has been read
            os.remove(filepath)

    # Save each group's dataframe to a new CSV file
    for group_key, df in grouped_dataframes.items():
        # Construct the output filename
        output_filename = group_key + ".csv"
        output_filepath = os.path.join(output_directory, output_filename)
        
        # Save the dataframe to CSV
        df.to_csv(output_filepath, index=False)
        
        
    # Delete directory "sum_vectorial_instructions"
    print("Deleting directoris 'ratio_vectorial_total_intructions_raw' and 'sum_vectorial_instructions'...")
    shutil.rmtree("ratio_vectorial_total_instructions_raw")
    shutil.rmtree("sum_vectorial_instructions")

# Computes by how many times more vectorial instructions are executed compared to serial instructions, for each vectorization type
def compare_ratios_vs_serial():
    input_dir = "percentage_vectorial_instructions"
    output_dir = "ratio_of_percentage_vectorial_instructions_to_serial"
    
    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Iterate over each file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_dir, filename)
            df = pd.read_csv(filepath)
            
            # Check if the file contains the column "Ratio serial"
            if "serial" not in df.columns:
                print(f"Skipping file {filename} as it does not contain 'serial' column.")
                continue
            
            # Compute the overheads for every column (except "Iteration" and "serial") over "serial"
            overheads = df.copy()
            for col in df.columns:
                if col != "serial":
                    overheads[col] = df[col] / df["serial"]
                    # overheads.drop(columns=[col], inplace=True)
            
            overheads.drop(columns=["serial"], inplace=True)
            
            # Save the results to the output directory
            output_filepath = os.path.join(output_dir, filename)
            overheads.to_csv(output_filepath, index=False)
            
def merge_csv_files(input_directory, output_file, use_percentage):
    # Define the directory containing the CSV files
    output_directory = 'graphData'
    output_file = os.path.join(output_directory, output_file)

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
    percentage = 100 if use_percentage else 1
    merged_df['autoVec'] = (merged_df['autoVec'] * percentage).map('{:.4f}'.format)
    merged_df['explicitVec'] = (merged_df['explicitVec'] * percentage).map('{:.4f}'.format)
    merged_df['fullVec'] = (merged_df['fullVec'] * percentage).map('{:.4f}'.format)

    # Sort the DataFrame by the 'benchmark' column
    merged_df.sort_values(by='benchmark', inplace=True)

    # Save the merged DataFrame to a new CSV file in the output directory
    merged_df.to_csv(output_file, index=False)

    print(f'Merged CSV saved as {output_file}')

def main():
    compute_ratios()
    compare_ratios_vs_serial()
    
    input_directories = ["percentage_vectorial_instructions", "ratio_of_percentage_vectorial_instructions_to_serial"]
    output_files = {"percentage_vectorial_instructions": "percentage_vectorial_instructions.csv", "ratio_of_percentage_vectorial_instructions_to_serial": "ratio_of_percentage_vectorial_instructions_to_serial.csv"}
    
    for dir in input_directories:
        use_percentage = True if dir == "percentage_vectorial_instructions" else False
        merge_csv_files(dir, output_files[dir], use_percentage)
        
    

if __name__ == "__main__":
    main()
