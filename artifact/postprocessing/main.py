import os
import cli
import pathlib
import warnings
import data_loader
import numpy as np
import pandas as pd
from utils import overhead, plot

warnings.filterwarnings('ignore')

rename_configs_map = [
    # speedup
    ('serial', 'scalar'),
    ('autoVec', 'auto-vectorized'),
    ('explicitVec', 'vector-api'),
    ('fullVec', 'fully-vectorized'),

    # loopBound and IndexInRange
    ('fullVec', 'loopBound'),

    # mul and pow
    ('fullVec', 'mul'),

    # xor
    ('xorPublic', 'xor'),
    ('xorExtended', 'logical-xor'),
    ('fullVec', 'neq-xor'),

    # fma
    ('fmaScalar', 'scalar-fma'),
    ('fullVec', 'scalar-mul-add/mul-add'),
    ('fullVec', 'fma/mul-add'),
    ('fma', 'scalar-fma/fma'),
]


def rename_configs(data):
    for (config, new_config) in rename_configs_map:
        config_data = data[data['config'] == config].copy()
        config_data['config'] = new_config
        frames = [data, config_data]
        data = pd.concat(frames)
    return data


def postprocess_data(data):
    data = data.copy()
    data = rename_configs(data)
    return data


def intersection(lst1, lst2):
    return set(lst1).intersection(lst2)


def get_overhead_configs():
    prop = 'Score'
    title = 'Speedup factor'
    yscale = 'log'


    return [{
        'prop': prop,
        'title': title,
        'format_minor': False,
        'yscale': yscale,
        'grid_type': None,
        'ylabel_format': 'scalar',
        'value_label_size': 13,
        'fontsize': 15.5,
        'experiment': 'speedup',
        'configs': ['auto-vectorized', 'vector-api', 'fully-vectorized'],
        'baseline_configs': ['scalar', 'scalar', 'scalar'],
    }, {
        'prop': prop,
        'title': title,
        'format_minor': False,
        'yscale': yscale,
        'grid_type': None,
        'ylabel_format': 'scalar',
        'value_label_size': 13,
        'fontsize': 15.5,
        'experiment': 'indexInRange',
        'configs': ['loopBound', 'indexInRange'],
        'baseline_configs': ['scalar', 'scalar'],
    }, {
        'prop': prop,
        'title': title,
        'format_minor': False,
        'yscale': yscale,
        'grid_type': None,
        'ylabel_format': 'scalar',
        'value_label_size': 15,
        'fontsize': 17.5,
        'experiment': 'pow',
        'configs': ['mul', 'pow'],
        'baseline_configs': ['scalar', 'scalar'],
    }, {
        'prop': prop,
        'title': title,
        'format_minor': False,
        'yscale': yscale,
        'grid_type': None,
        'ylabel_format': 'scalar',
        'value_label_size': 17,
        'fontsize': 19.5,
        'experiment': 'fma',
        'configs': ['scalar-mul-add/mul-add', 'scalar-fma/fma', 'fma/mul-add'],
        'baseline_configs': ['scalar', 'scalar-fma', 'fma'],
    }, {
        'prop': prop,
        'title': title,
        'format_minor': False,
        'yscale': yscale,
        'grid_type': None,
        'ylabel_format': 'scalar',
        'value_label_size': 20,
        'fontsize': 22.5,
        'experiment': 'xor',
        'configs': ['logical-xor', 'neq-xor', 'xor'],
        'baseline_configs': ['scalar', 'scalar', 'scalar'],
    }]


def main():
    args = cli.run()

    print('Loading data...')
    data = data_loader.load(args.input)
    data = postprocess_data(data)
    pathlib.Path(args.output).mkdir(parents=True, exist_ok=True)
    data.to_csv(os.path.join(args.output, 'data.csv'))

    print('Generating figures...')
    overhead_configs = get_overhead_configs()

    for overhead_config in overhead_configs:        
        prop = overhead_config['prop']
        title = overhead_config['title']
        format_minor = overhead_config['format_minor']
        yscale = overhead_config['yscale']
        grid_type = overhead_config['grid_type']
        ylabel_format = overhead_config['ylabel_format']
        value_label_size = overhead_config['value_label_size']
        fontsize = overhead_config['fontsize']
        experiment = overhead_config['experiment']
        configs = overhead_config['configs']
        baseline_configs = overhead_config['baseline_configs']

        print('Generating figures for experiment "' + experiment + '"')

        # plot only the benchmarks that have measurements for all the given configurations
        benchmarks = data['benchmark'].to_list()
        for config in configs + baseline_configs:
            benchmarks = intersection(benchmarks,
                                      data[data['config'] == config]['benchmark'].to_list())

        for jdk in data['jdk'].unique():
            for machine in data['machine'].unique():
                filtered_data = data[ \
                    (data['jdk'] == jdk) & \
                    (data['machine'] == machine) \
                ]

                overhead_data = overhead(filtered_data, prop, jdk, machine, configs, baseline_configs,
                                         benchmarks=benchmarks, ci_confidence=args.confidence_intervals,
                                         ci_repetitions=args.confidence_intervals_repetitions)
                if overhead_data is None or overhead_data.empty:
                    continue

                plot(overhead_data, prop, experiment, jdk, machine, configs, ylabel=title,
                        format_minor=format_minor, out_dir=args.output,
                        plot_extensions=args.plot_extensions, plot_prefix=args.plot_prefix,
                        yscale=yscale,
                        grid_type=grid_type, ylabel_format=ylabel_format, value_label_size=value_label_size,
                        fontsize=fontsize)


if __name__ == '__main__':
    main()
