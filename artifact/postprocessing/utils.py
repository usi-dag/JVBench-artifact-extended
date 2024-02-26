import os
import math
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats.mstats import gmean
from matplotlib.ticker import FormatStrFormatter, LogFormatterExponent, FuncFormatter


plt_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
bar_colors = [plt_colors[3], plt_colors[0], plt_colors[2]]


@FuncFormatter
def custom_tick_formatter(x, pos):
    if x == 0.01:
        return ''
    elif x % 1 == 0:
        return '{}'.format(int(x))
    return '{}'.format(x)


def plot(dataset, val, experiment, jdk, machine, configs,
         xlabel='', ylabel='', yscale='linear', ylabel_format=None,
         format_minor=False, plot_extensions=['pdf'], plot_prefix='', out_dir='', value_label_size=10,
         fontsize=12.5, grid_type=None, colors=bar_colors):
    bar_width = 0.85
    plt.rcParams['errorbar.capsize'] = 3
    plt.rcParams['font.size'] = fontsize
    dataset = dataset[(dataset['jdk'] == jdk) & (dataset['machine'] == machine)].sort_values(['benchmark'])
    dataset_configs = [x for x in dataset['config'].unique() if x in configs]

    chart_colors = colors[3 - len(dataset_configs):3]

    dataset = dataset.pivot(index='benchmark', columns='config', values=[val, 'ci_left', 'ci_right'])

    ci_dataset = dataset[['ci_left', 'ci_right']]
    ci_dataset.columns = ci_dataset.columns.swaplevel(0, 1)
    ci_dataset = ci_dataset.sort_index(axis=1, level=0)
    yerr = []
    for config in [x for x in configs if x in dataset_configs]:
        yerr += [[
            np.subtract(dataset[val][config].to_list(), ci_dataset[config]['ci_left'].to_list()),
            np.subtract(ci_dataset[config]['ci_right'].to_list(), dataset[val][config].to_list())
        ]]
    ax = dataset[val].plot(
        y=[x for x in configs if x in dataset_configs],
        yerr=yerr,
        kind='bar',
        width=bar_width,
        xlabel=xlabel,
        ylabel=ylabel,
        color=chart_colors,
        fontsize=fontsize,
        legend=False
    )
    # flatten yerr
    yerr_tmp = []
    for yerr_config in yerr:
        for i in range(0, len(yerr_config[0])):
            yerr_tmp.append([[yerr_config[0][i]], [yerr_config[1][i]]])
    yerr = yerr_tmp

    for i, p in enumerate(ax.patches):
        x = p.get_x()
        y = p.get_height()
        ax.annotate(' %.2f' % y, (x + bar_width / (len(dataset_configs) * 2) + 0.025, y + yerr[i][1][0]), rotation=90,
                    ha='center', va='bottom', size=value_label_size)
    ax.set_axisbelow(True)
    ax.set_yscale(yscale)
    if format_minor:
        ax.yaxis.set_minor_formatter(FormatStrFormatter('%.0f'))
    if ylabel_format == 'log':
        ax.yaxis.set_major_formatter(LogFormatterExponent(base=10.0))
    elif ylabel_format == 'scalar':
        ax.yaxis.set_major_formatter(custom_tick_formatter)
    ax.legend(title=None, prop={'size': 12.5})
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    if grid_type is None:
        plt.grid(False)
    else:
        plt.grid(True, which=grid_type, axis='y', zorder=0, linestyle='--')
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    plt.subplots_adjust(left=0.065)
    plt.axhline(y=1, color='grey', alpha=0.5, zorder=0, linestyle='-')
    for plot_ext in plot_extensions:
        plt.savefig(os.path.join(out_dir, plot_prefix + '_' + experiment + '_' + jdk + '_' + machine + '.' + plot_ext), bbox_inches='tight',
                    pad_inches=0)


def overhead(df, prop, jdk, machine, configs, baseline_configs, benchmarks=[], ci_confidence=0.95, ci_repetitions=1000):
    def confidence_intervals_slowdown(baseline, nonbaseline, confidence=0.95, repetitions=1000):
        def sample_with_replacements(l):
            return random.choices(l, k=len(l))

        sdf = np.mean(nonbaseline) / np.mean(baseline)

        sdf_deltas = []
        for i in range(0, repetitions):
            baseline_mean_sample = np.mean(sample_with_replacements(baseline))
            nonbaseline_mean_sample = np.mean(sample_with_replacements(nonbaseline))
            slowdown_sample = nonbaseline_mean_sample / baseline_mean_sample
            sdf_deltas.append(slowdown_sample - sdf)

        left = sdf - np.quantile(sdf_deltas, (confidence + (1 - confidence) / 2))
        right = sdf - np.quantile(sdf_deltas, (1 - confidence) / 2)

        return [sdf, left, right]

    data = []
    for idx, config in enumerate(configs):
        baseline = df[df['config'] == baseline_configs[idx]]
        nonbaseline = df[df['config'] == config]
        for benchmark in benchmarks:
            local_baseline = baseline[(baseline['benchmark'] == benchmark)][prop].to_list()
            local_nonbaseline = nonbaseline[(nonbaseline['benchmark'] == benchmark)][prop].to_list()

            [sdf, left, right] = confidence_intervals_slowdown(local_nonbaseline, local_baseline,
                                                               confidence=ci_confidence, repetitions=ci_repetitions)

            data.append([benchmark, jdk, machine, config, sdf, left, right])

    return pd.DataFrame(data, columns=['benchmark', 'jdk', 'machine', 'config', prop, 'ci_left', 'ci_right'])
