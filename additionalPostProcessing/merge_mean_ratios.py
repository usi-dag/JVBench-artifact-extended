import os
import pandas as pd

# Define the directory containing the CSV files
input_directory = 'mean_ratio_vectorial_total_instructions'
output_directory = 'graphData'
output_file = os.path.join(output_directory, 'merged_mean_ratios.csv')

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Initialize an empty list to store DataFrames
data_frames = []

# Iterate over all files in the directory
for file_name in os.listdir(input_directory):
    if file_name.endswith('.csv'):
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