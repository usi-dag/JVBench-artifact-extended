import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_vectorial_instructions(directory):
    # Initialize an empty DataFrame to store all data
    all_data = pd.DataFrame()
    
    # Iterate over all CSV files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            # Load the CSV file
            data = pd.read_csv(file_path)
            # Append the data to the all_data DataFrame
            all_data = pd.concat([all_data, data], ignore_index=True)
    
    # Calculate mean values for each column
    mean_values = all_data.mean()
    
    # Exclude the 'serial' column
    mean_values = mean_values.drop('serial')
    
    # Create a bar plot
    plt.figure(figsize=(10, 6))
    mean_values.plot(kind='bar', color=['blue', 'green', 'red'])
    plt.title('Mean Ratio of Vectorial Total Instructions')
    plt.xlabel('Configuration')
    plt.ylabel('Mean Ratio')
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('bar_plot.pdf', format='pdf', bbox_inches='tight', pad_inches=0)
    plt.close()

# Usage example:
plot_vectorial_instructions('mean_ratio_vectorial_total_instructions')