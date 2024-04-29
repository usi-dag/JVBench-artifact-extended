import os
import pandas as pd
import shutil

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

        # Step 2b: Copy the column "Iteration" from the current file
        df_output = df[['Iteration']].copy()

        # Step 2c: Sum all the values of each row, excluding the "Iteration" column
        df['Total Vectorial Instructions'] = df.drop('Iteration', axis=1).sum(axis=1).astype(int)

        # Step 3: Make a new column called "Total Vectorial Instructions"
        # (This step is effectively done in step 2c)

        # Include the new column in the output DataFrame
        df_output['Total Vectorial Instructions'] = df['Total Vectorial Instructions']

        # Step 4: Store the sum in the column "Total Vectorial Instructions"
        df_output.to_csv(output_file_path, index=False)



# COMPUTE THE RATIONS
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
    ratio = df_vec['Total Vectorial Instructions'] / df_total['Total Number of (any) instructions']
    
    # Create a new DataFrame with 'Iteration' and the computed ratio
    result_df = pd.DataFrame({
        'Iteration': df_vec['Iteration'],
        'Ratio': ratio
    })
    
    # Write the result to a new CSV file in the output directory
    output_file_path = os.path.join(output_dir, file)
    result_df.to_csv(output_file_path, index=False)


# MERGE THE RESULTS
print("Ratios computed, merging results...")

# Directory containing the CSV files
input_directory = "ratio_vectorial_total_instructions_raw"
output_directory = "ratio_vectorial_total_instructions"

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
        new_ratio_column_name = "Ratio " + filename.split('.')[3].split('_')[0]
        df.rename(columns={'Ratio': new_ratio_column_name}, inplace=True)
        
        # If the group key is new, initialize a new dataframe
        if group_key not in grouped_dataframes:
            grouped_dataframes[group_key] = df
        else:
            # Otherwise, merge this dataframe with the existing one for the group
            grouped_dataframes[group_key] = pd.merge(grouped_dataframes[group_key], df, on='Iteration')
        
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
