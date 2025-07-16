import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('statfile', type=Path)
    parser.add_argument(
        '--filter-ids',
        help=
        "If given, only display GPU's with these ids (numbered after bus id).",
        type=int,
        nargs='+')
    args = parser.parse_args()

    stats = pd.read_csv(args.statfile,
                        parse_dates=True,
                        skipinitialspace=True,
                        index_col=0)
    for col_name in ('utilization.gpu [%]', 'utilization.memory [%]'):
        stats[col_name] = stats[col_name].str.rstrip(' %').astype(float) / 100
    stats = stats.dropna()
    bus_ids = {
        bus_id: i
        for i, bus_id in enumerate(sorted(stats['pci.bus_id'].unique()))
    }

    stats['gpu_id'] = [bus_ids[bus_id] for bus_id in stats['pci.bus_id']]
    if args.filter_ids:
        to_drop = set(bus_ids.values()) - set(args.filter_ids)
        for i in to_drop:
            stats = stats.drop(stats[stats['gpu_id'] == i].index)

    if len(stats) < 1:
        raise RuntimeError(
            "No values to display, did you filter out all GPU ids?")

    fig, (ax_compute, ax_mem) = plt.subplots(2,
                                             1,
                                             sharex='col',
                                             figsize=(12, 6))
    plt.suptitle(f'Utilization statistics from {args.statfile.name}')

    stats.groupby('gpu_id')['utilization.gpu [%]'].plot(ax=ax_compute, lw=1)
    ax_compute.set_ylim(-0.01, 1.01)
    ax_compute.set_ylabel('GPU utilization')
    stats.groupby('gpu_id')['utilization.memory [%]'].plot(ax=ax_mem, lw=1)
    ax_mem.set_ylim(-0.01, 1.01)
    ax_mem.set_ylabel('Memory utilization')

    # Are we sure the order of the plots are the same so that the legend is
    # correct for both subplots?
    leg = plt.legend(loc='lower right', fontsize=7)
    for line in leg.get_lines():
        line.set_linewidth(1.0)
    ax_mem.set_ylim(-0.01, 1.01)
    plt.tight_layout()
    fig.savefig('gpu_usage.png',
                dpi=300,
                pad_inches=.05,
                bbox_inches="tight",
                format="png")


if __name__ == '__main__':
    main()
