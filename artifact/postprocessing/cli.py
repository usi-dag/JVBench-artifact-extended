import argparse


def validate_confidence(confidence):
    confidence = float(confidence)
    if confidence >= 1:
        raise argparse.ArgumentTypeError('confidence must be < 1')
    if confidence <= 0:
        raise argparse.ArgumentTypeError('confidence must be > 0')
    return confidence


def plot_extensions(exts):
    return [ext for ext in exts.split(',')]


def run():
    parser = argparse.ArgumentParser(description='Command line to generate figures', 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input', type=str, default='./data', help='Input directory path')
    parser.add_argument('-o', '--output', type=str, default='./out', help='Output directory path')
    parser.add_argument('-ci-c', '--confidence-intervals', type=validate_confidence, default=0.95,
                        help='Confidence to compute confidence intervals')
    parser.add_argument('-ci-r', '--confidence-intervals-repetitions', type=int, default=1000,
                        help='Number of repetitions to compute the confidence intervals')
    parser.add_argument('-pexts', '--plot-extensions', type=plot_extensions, default='pdf',
                        help='Comma-separated list of plot extensions to export')
    parser.add_argument('-pprx', '--plot-prefix', type=str, default='',
                        help='File prefix to use when saving plots')
    return parser.parse_args()
