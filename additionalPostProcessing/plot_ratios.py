import pandas as pd
import matplotlib.pyplot as plt
import os

def create_bar_plot(csv_file, output_dir='figures', plot_filename='bar_plot.pdf'):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Set the benchmark column as the index
    df.set_index('benchmark', inplace=True)
    
    # Define the plot colors
    plt_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    bar_colors = [plt_colors[3], plt_colors[0], plt_colors[2]]
    
    # Create the bar plot
    ax = df.plot(kind='bar', color=bar_colors, width=0.85, figsize=(10, 6))
    
    # Set y-axis to log scale
    ax.set_yscale('log')
    
    # Customize the plot
    ax.set_xlabel('Benchmark', fontsize=12.5)
    ax.set_ylabel('Percentage Vectorial Instructions', fontsize=12.5)
    # ax.set_title('Benchmark Comparison', fontsize=15)
    # ax.legend(title='Configuration', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot to a file
    plot_path = os.path.join(output_dir, plot_filename)
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# Example usage
create_bar_plot('graphData/merged_mean_ratios.csv')