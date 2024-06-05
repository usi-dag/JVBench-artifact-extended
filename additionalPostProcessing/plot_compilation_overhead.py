import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker
from scipy.stats import gmean

def create_bar_plot(plot_filename, output_dir, avx_type):
    
    # Read df from compilation_overheads/no_profiler.csv
    df = pd.read_csv(f'{avx_type}/compilation_overheads/no_profiler.csv')
    
    df['autoVec'] = pd.to_numeric(df['autoVec'], errors='coerce')
    df['explicitVec'] = pd.to_numeric(df['explicitVec'], errors='coerce')
    df['fullVec'] = pd.to_numeric(df['fullVec'], errors='coerce')

    df['auto-vectorized'] = df['autoVec']
    df['vector-api'] = df['explicitVec']
    df['fully-vectorized'] = df['fullVec']
    
    if avx_type == "MAVX":
        # Remove this benchmark since we don't have all the data for the other figures
        df = df[~df['benchmark'].isin(['particlefilter'])]
    
    df.drop(columns=['autoVec', 'explicitVec', 'fullVec'], inplace=True)
    
    geometric_mean_autoVec = gmean(df['auto-vectorized'])
    geometric_mean_explicitVec = gmean(df['vector-api'])
    geometric_mean_fullVec = gmean(df['fully-vectorized'])
    print(f'{avx_type} Compilation overhead auto-vectorized geometric mean is: {geometric_mean_autoVec}')
    print(f'{avx_type} Compilation overhead vector-api geometric mean is: {geometric_mean_explicitVec}')
    print(f'{avx_type} Compilation overhead fully-vectorized geometric mean is: {geometric_mean_fullVec}')
    
    # Save as csv in graphData folder
    df.to_csv(f'{avx_type}/graphData/compilation_overhead_no_profiler.csv', index=False)
    
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
    ax.set_ylim(top=10)
    
    # Customize the plot
    ax.set_xlabel('', fontsize=20)
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
    
    # Move the legend above the bars in the free space
    # ax.legend(fontsize=17.5)
    ax.get_legend().remove()
    
    
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
    
def main():
    
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    for avx_type in avx_types:
        create_bar_plot(f"compilation_overhead.png", f"{avx_type}/figures", avx_type)


if __name__ == "__main__":
    main()