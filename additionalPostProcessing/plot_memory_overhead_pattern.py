import pandas as pd
import matplotlib.pyplot as plt
import os

def create_bar_plot_loopbound_indexinrange(csv_file, plot_filename, output_dir):
    plot_filename = plot_filename.replace(".pdf", "_loopbound_indexinrange.pdf")
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Replace fullVec with loopBound
    df['loopBound'] = df['fullVec']
    
    # Remove all columns except loopBound and indexInRange
    df = df[['benchmark', 'loopBound', 'indexInRange']]
    
    # Set the benchmark column as the index
    df.set_index('benchmark', inplace=True)
    
    # Define the plot colors
    plt_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    bar_colors = [plt_colors[0], plt_colors[2], plt_colors[0]]
    
    # Create the bar plot
    ax = df.plot(kind='bar', color=bar_colors, width=0.85, figsize=(10, 6))
    
    # Set y-axis to log scale
    ax.set_yscale('log')
    
    # Customize the plot
    ax.set_xlabel('Benchmark', fontsize=12.5)
    ax.set_ylabel('Overhead', fontsize=12.5)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    
    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Annotate above the bars
    bar_width = 0.85
    value_label_size = 10
    for i, p in enumerate(ax.patches):
        x = p.get_x()
        y = p.get_height()
        ax.annotate(' %.4f' % y, (x + bar_width / (len(df.columns) * 2) + 0.025, y), rotation=90,
                    ha='center', va='bottom', size=value_label_size)
    
    # Move the legend outside the plot
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot to a file
    plot_path = os.path.join(output_dir, plot_filename)
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    
def create_bar_plot_mul_pow(csv_file, plot_filename, output_dir):
    plot_filename = plot_filename.replace(".pdf", "_mul_pow.pdf")
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Replace fullVec with mul
    df['mul'] = df['fullVec']
    
    # Remove all columns except mul and pow
    df = df[['benchmark', 'mul', 'pow']]
    
    # Drop rows with NaN o rempty values
    df.dropna(inplace=True)
        
    
    # Set the benchmark column as the index
    df.set_index('benchmark', inplace=True)
    
    # Define the plot colors
    plt_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    bar_colors = [plt_colors[0], plt_colors[2], plt_colors[0]]
    
    # Create the bar plot
    ax = df.plot(kind='bar', color=bar_colors, width=0.85, figsize=(10, 6))
    
    # Set y-axis to log scale
    ax.set_yscale('log')
    # ax.set_ybound(0.0001, 1000000000)
    
    # Customize the plot
    ax.set_xlabel('Benchmark', fontsize=12.5)
    ax.set_ylabel('Overhead', fontsize=12.5)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    
    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Annotate above the bars
    bar_width = 0.85
    value_label_size = 10
    for i, p in enumerate(ax.patches):
        x = p.get_x()
        y = p.get_height()
        # ax.annotate(' %.4f' % y, (x + bar_width / (len(df.columns) * 2), y), rotation=90,
        ax.annotate(' %.4f' % y, (x + bar_width / (len(df.columns) * 2) + 0.025, y), rotation=90,
                    ha='center', va='bottom', size=value_label_size)
    
    # Move the legend outside the plot
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot to a file
    plot_path = os.path.join(output_dir, plot_filename)
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

def main():
    
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    # avx_types = ["MAVX", "MAVX512"]
    for avx_type in avx_types:
        directory = f"{avx_type}/graphData"
        
        # Iterate over files in the directory
        for filename in os.listdir(directory):
            if "pattern" not in filename:
                continue
            file_path = os.path.join(directory, filename)
            
            # WARNING: REMOVE THIS TO PLOT ALL FILES - ONLY PLOTTING NO_PROFILER FILES BECAUSE I THINK THIS IS ALL WE CARE ABOUT
            # WARNING: ALSO ONLY PLOTTING RATE_NORM CAUSE WE DON'T HAVE ALL VALUES FOR THE OTHER 2
            
            if 'no_profiler' not in file_path or "_gc_" not in file_path or "alloc_rate_norm" not in file_path:
                continue
            
            if os.path.isfile(file_path):
                create_bar_plot_loopbound_indexinrange(file_path, filename.replace('.csv', '.pdf'), f"{avx_type}/figures")
                create_bar_plot_mul_pow(file_path, filename.replace('.csv', '.pdf'), f"{avx_type}/figures")


if __name__ == "__main__":
    main()