import os
import csv

def compute_column_means(csv_file):
    data = []
    header = []
    
    # Read the CSV file
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)[1:]  # Get the header row (excluding the "Iteration" column)
        for row in csv_reader:
            data.append(row[1:])  # Exclude the "Iteration" column
    
    # Convert the data to float
    data = [[float(value) for value in row] for row in data]
    
    # Compute the mean of each column
    num_columns = len(data[0])
    column_means = []
    for col in range(num_columns):
        column_values = [row[col] for row in data]
        mean = sum(column_values) / len(column_values)
        column_means.append(mean)
    
    return header, column_means

# Directory containing the input CSV files
input_directory = 'ratio_vectorial_total_instructions'

# Directory to store the output files with mean values
output_directory = 'mean_ratio_vectorial_total_instructions'

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Process each CSV file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.csv'):
        input_file = os.path.join(input_directory, filename)
        if "Pattern" in input_file:
            continue
        output_file = os.path.join(output_directory, filename)
        
        # Compute the column means for the current file
        header, column_means = compute_column_means(input_file)
        
        # Save the column means to the output file with the same header
        with open(output_file, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            csv_writer.writerow(column_means)
        
        print(f"Processed {filename} and saved results to {output_file}")