import pandas as pd
import matplotlib.pyplot as plt
import os

def create_bar_plot(csv_file, output_dir='figures', plot_filename='bar_plot.pdf'):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    df['auto-vectorized'] = df['autoVec']
    df['vector-api'] = df['explicitVec']
    df['fully-vectorized'] = df['fullVec']
    
    df.drop(columns=['autoVec', 'explicitVec', 'fullVec'], inplace=True)
    
    
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
    if 'ratio' in csv_file:
        ax.set_ylabel('Ratio', fontsize=12.5)
        # plt.title(f"Vectorization Ratio", fontsize=15, y=1.25)
    else:
        ax.set_ylabel('Percentage', fontsize=12.5)
        # plt.title(f"Percentage Of Vectorial Instructions", fontsize=15, y=1.25)
        
        
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

def main():
    
    avx_types = ["MAVX", "MAVX2", "MAVX512"]
    ratio_files = ["ratio_of_percentage_vectorial_instructions_to_serial", "percentage_vectorial_instructions"]
    for avx_type in avx_types:
        for ratio_file in ratio_files:
            create_bar_plot(f'{avx_type}/graphData/{ratio_file}.csv', f"{avx_type}/figures", f'{ratio_file}_{avx_type}.pdf')


if __name__ == "__main__":
    main()