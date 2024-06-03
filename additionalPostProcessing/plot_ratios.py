from matplotlib import ticker
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import gmean

def custom_formatter(value, pos):
    if value < 1:
        return f'{value:.3f}%'
    else:
        return f'{value:.0f}%'
    
def create_bar_plot(csv_file, output_dir, plot_filename, avx_type):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    df['auto-vectorized'] = df['autoVec']
    df['vector-api'] = df['explicitVec']
    df['fully-vectorized'] = df['fullVec']
    
    df.drop(columns=['autoVec', 'explicitVec', 'fullVec'], inplace=True)
  
    geometric_mean_autoVec = gmean(df['auto-vectorized'])
    geometric_mean_explicitVec = gmean(df['vector-api'])
    geometric_mean_fullVec = gmean(df['fully-vectorized'])
    
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
    if 'ratio' in csv_file:
        ax.set_ylim(top=10000000)
        ax.set_ylabel('Ratio', fontsize=20)
        print(f'{avx_type} Vectorization ratio auto-vectorized geometric mean is: {geometric_mean_autoVec}')
        print(f'{avx_type} Vectorization ratio vector-api geometric mean is: {geometric_mean_explicitVec}')
        print(f'{avx_type} Vectorization ratio fully-vectorized geometric mean is: {geometric_mean_fullVec}')
        # plt.title(f"Vectorization Ratio", fontsize=20, y=1.25)
    else:
        ax.set_ylim(top=100)
        ax.set_ylabel('Percentage', fontsize=20)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
        # print(f'{avx_type} Percentage geometric mean is: {geometric_mean}')
        # plt.title(f"Percentage Of Vectorial Instructions", fontsize=20, y=1.25)
        
        
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
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3)
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.5), ncol=3, fontsize=17.5)
    ax.get_legend().remove()
    
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot to a file
    plot_path = os.path.join(output_dir, plot_filename)
    plt.rcParams['font.size'] = 12.5
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()

def main():
    
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    ratio_files = ["ratio_of_percentage_vectorial_instructions_to_serial", "percentage_vectorial_instructions"]
    for avx_type in avx_types:
        for ratio_file in ratio_files:
            create_bar_plot(f'{avx_type}/graphData/{ratio_file}.csv', f"{avx_type}/figures", f'{ratio_file}_{avx_type}.png', avx_type)


if __name__ == "__main__":
    main()