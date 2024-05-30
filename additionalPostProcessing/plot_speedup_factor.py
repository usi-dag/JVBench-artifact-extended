from matplotlib.ticker import LogFormatterExponent
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker
def create_bar_plot(df, plot_filename, output_dir):
    df['autoVec'] = pd.to_numeric(df['autoVec'], errors='coerce')
    df['explicitVec'] = pd.to_numeric(df['explicitVec'], errors='coerce')
    df['fullVec'] = pd.to_numeric(df['fullVec'], errors='coerce')
    df['serial'] = pd.to_numeric(df['serial'], errors='coerce')

    df['auto-vectorized'] = df['serial']/df['autoVec']
    df['vector-api'] = df['serial']/df['explicitVec']
    df['fully-vectorized'] = df['serial']/df['fullVec']
    
    df.drop(columns=['autoVec', 'explicitVec', 'fullVec', 'serial'], inplace=True)
    
    # Set the benchmark column as the index
    df.set_index('benchmark', inplace=True)
    
    # Define the plot colors
    plt_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    bar_colors = [plt_colors[3], plt_colors[0], plt_colors[2]]
    
    # Create the bar plot
    
    # Create the bar plot
    ax = df.plot(kind='bar', color=bar_colors, width=0.85, figsize=(10, 6))
    
    # Set y-axis to log scale
    ax.set_yscale('log')
    
    # Set the y-axis limit to 1000 by default
    ax.set_ylim(top=100)
    
    # Customize the plot
    ax.set_xlabel('', fontsize=20)
    ax.set_ylabel('Speedup factor', fontsize=20)
    ax.grid(axis='y', linestyle='', alpha=0.7)
    plt.xticks(rotation=35, ha='right', fontsize=20)
    plt.yticks(fontsize=20)
    
    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Annotate above the bars
    bar_width = 0.85
    value_label_size = 17.5
    for i, p in enumerate(ax.patches):
        x = p.get_x()
        y = p.get_height()
        if y > 10000:
            annotation = f' {y:.1e}'
        elif y < 0.01:
            annotation = f' {y:.4f}'
        else:
            annotation = f' {y:.2f}'
        ax.annotate(annotation, (x + bar_width / (len(df.columns) * 2) + 0.025, y), rotation=90,
                    ha='center', va='bottom', size=value_label_size)
    
    # Move the legend above the bars in the free space
    ax.legend(fontsize=17.5)
    
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    plt.axhline(y=1, color='grey', alpha=0.5, zorder=0, linestyle='-')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    # Save the plot to a file
    plot_path = os.path.join(output_dir, plot_filename)
    plt.subplots_adjust(left=0.065)
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    
def merge_execution_times(avx_type):
    execution_times_dir = f'{avx_type}/execution_times_no_profiler'
    
    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(execution_times_dir) if file.endswith('.csv')]
    
    # Initialize an empty list to store the DataFrames
    dataframes = []
    
    # Iterate over each CSV file
    for file in csv_files:
        file_path = os.path.join(execution_times_dir, file)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Add a column "benchmark" with the file name
        df['benchmark'] = file.split('.')[0].split('Benchmark')[0].lower()
        
        # Append the DataFrame to the list
        dataframes.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Drop rows where the column "Iteration" is not "MEAN"
    merged_df = merged_df[merged_df['Iteration'] == 'MEAN']
    
    # Drop the column "Iteration"
    merged_df = merged_df.drop('Iteration', axis=1)
    
    # Sort the DataFrame by benchmark name
    merged_df = merged_df.sort_values('benchmark')
    
    # Reset the index
    merged_df = merged_df.reset_index(drop=True)
    
    return merged_df

def main():
    
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    for avx_type in avx_types:
        df = merge_execution_times(avx_type)
        create_bar_plot(df, f"speedup_factor.png", f"{avx_type}/figures")


if __name__ == "__main__":
    main()