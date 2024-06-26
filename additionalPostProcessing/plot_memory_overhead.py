import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gmean
import os

def create_bar_plot(csv_file, plot_filename, output_dir, avx_type):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    df['auto-vectorized'] = df['autoVec']
    df['vector-api'] = df['explicitVec']
    df['fully-vectorized'] = df['fullVec']
    
    df.drop(columns=['autoVec', 'explicitVec', 'fullVec'], inplace=True)
    
    geometric_mean_autoVec = gmean(df['auto-vectorized'])
    geometric_mean_explicitVec = gmean(df['vector-api'])
    geometric_mean_fullVec = gmean(df['fully-vectorized'])
    print(f'{avx_type} Memory Overhead auto-vectorized geometric mean is: {geometric_mean_autoVec}')
    print(f'{avx_type} Memory Overhead vector-api geometric mean is: {geometric_mean_explicitVec}')
    print(f'{avx_type} Memory Overhead fully-vectorized geometric mean is: {geometric_mean_fullVec}')
    
    
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
    ax.set_xlabel('', fontsize=20)
    # ax.set_ylabel('Overhead', fontsize=20)
    ax.set_ylabel('Ratio', fontsize=20)
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
    
    # Move the legend outside the plot
    # ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.45), ncol=3, fontsize=17.5)
    ax.get_legend().remove()
    
    ax.set_ylim(top=10000000)
    plt.axhline(y=1, color='grey', alpha=0.5, zorder=0, linestyle='-')
    
    
    # Make title
    # name = csv_file.split("gc_")[1].split(".")[0]
    # name = name.replace("_", ".")
    # name = "gc." + name
    
    # plt.title(f"{name} overhead w.r.t. serial", fontsize=20, y=1.25)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot to a file
    plot_path = os.path.join(output_dir, plot_filename)
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

def main():
    
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    for avx_type in avx_types:
        directory = f"{avx_type}/graphData"
        
        # Iterate over files in the directory
        for filename in os.listdir(directory):
            if "pattern" in filename:
                continue
            file_path = os.path.join(directory, filename)
            
            # WARNING: REMOVE THIS TO PLOT ALL FILES - ONLY PLOTTING NO_PROFILER FILES BECAUSE I THINK THIS IS ALL WE CARE ABOUT
            # WARNING: ALSO ONLY PLOTTING RATE_NORM CAUSE WE DON'T HAVE ALL VALUES FOR THE OTHER 2
            
            if 'no_profiler' not in file_path or "_gc_" not in file_path or "alloc_rate_norm" not in file_path:
                continue
            
            if os.path.isfile(file_path):
                create_bar_plot(file_path, filename.replace('.csv', f'_{avx_type}.png'), f"{avx_type}/figures", avx_type)


if __name__ == "__main__":
    main()