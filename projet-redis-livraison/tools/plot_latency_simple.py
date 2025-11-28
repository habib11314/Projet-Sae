"""
Very simple latency summary plot: 4 bars (mean, median, P90, P99).
Saves PNG to tools/latency_summary_simple.png by default.
Usage:
    python tools/plot_latency_simple.py --csv ../latencies_attribution_redis.csv --out tools/latency_summary_simple.png
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def read_first_numeric_column(csv_path):
    values = []
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        _ = next(reader, None)
        for row in reader:
            if not row:
                continue
            for cell in row:
                try:
                    v = float(cell)
                    values.append(v)
                    break
                except Exception:
                    continue
    return values


def compute_simple_stats(arr):
    a = np.array(arr)
    return {
        'mean': float(np.mean(a)),
        'median': float(np.median(a)),
        'p90': float(np.percentile(a, 90)),
        'p99': float(np.percentile(a, 99)),
        'count': int(a.size)
    }


def make_simple_bar(stats, out_path):
    labels = ['mean', 'median', 'P90', 'P99']
    values = [stats['mean'], stats['median'], stats['p90'], stats['p99']]

    fig, ax = plt.subplots(figsize=(6,4))
    bars = ax.bar(labels, values, color=['#4C72B0','#55A868','#C44E52','#8172B2'])
    ax.set_ylabel('Latency (ms)')
    ax.set_title('Résumé simple des latences')

    # annotate values on bars
    for bar, val in zip(bars, values):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + max(values)*0.02, f"{val:.1f} ms", ha='center', va='bottom', fontsize=9)

    # small footer with count
    ax.text(0.99, -0.15, f"n={stats['count']}", transform=ax.transAxes, ha='right', va='center', fontsize=9)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', '-c', default='../data/latencies_attribution_redis.csv')
    parser.add_argument('--out', '-o', default='../outputs/latency_summary_simple.png')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Fichier CSV introuvable: {csv_path}")
        return

    vals = read_first_numeric_column(csv_path)
    if not vals:
        print("Aucune donnée lue")
        return

    stats = compute_simple_stats(vals)
    out_path = Path(args.out)
    make_simple_bar(stats, out_path)
    print(f"Graphique simple sauvegardé: {out_path} (n={stats['count']})")

if __name__ == '__main__':
    main()
