"""
Plot latency samples from a CSV and save a simple illustrative histogram (PNG).
Usage:
    python tools/plot_latency.py --csv ../latencies_attribution_redis.csv --out tools/latency_histogram.png

This script uses numpy + matplotlib (no pandas required).
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def read_latencies(csv_path):
    latencies = []
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            for cell in row:
                try:
                    val = float(cell)
                    latencies.append(val)
                    break
                except Exception:
                    continue
    return latencies


def compute_stats(data):
    if not data:
        return {}
    arr = np.array(data)
    stats = {
        'count': int(arr.size),
        'mean_ms': float(np.mean(arr)),
        'median_ms': float(np.median(arr)),
        'std_ms': float(np.std(arr, ddof=0)),
        'p50_ms': float(np.percentile(arr, 50)),
        'p90_ms': float(np.percentile(arr, 90)),
        'p99_ms': float(np.percentile(arr, 99)),
        'min_ms': float(np.min(arr)),
        'max_ms': float(np.max(arr)),
    }
    return stats


def make_plot(data, out_path, stats, bins=40):
    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(data, bins=bins, color='#4C72B0', edgecolor='white', alpha=0.9)
    ax.set_xlabel('Latency (ms)')
    ax.set_ylabel('Count')
    ax.set_title("Distribution des latences d'attribution")

    ax.axvline(stats['mean_ms'], color='#DD8452', linestyle='--', linewidth=2, label=f"mean {stats['mean_ms']:.1f} ms")
    ax.axvline(stats['median_ms'], color='#55A868', linestyle='-.', linewidth=2, label=f"median {stats['median_ms']:.1f} ms")
    ax.axvline(stats['p90_ms'], color='#C44E52', linestyle=':', linewidth=2, label=f"P90 {stats['p90_ms']:.1f} ms")

    ax.text(0.98, 0.95, f"n={stats['count']}", transform=ax.transAxes, ha='right', va='top', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.6))

    ax.legend(loc='upper right')
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Plot latency samples from CSV and save an illustrative histogram PNG')
    parser.add_argument('--csv', '-c', default='../data/latencies_attribution_redis.csv', help='Path to CSV with latency samples (first numeric column expected)')
    parser.add_argument('--out', '-o', default='../outputs/latency_histogram.png', help='Output PNG path')
    parser.add_argument('--bins', type=int, default=40, help='Number of histogram bins')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Fichier CSV introuvable: {csv_path}")
        return

    data = read_latencies(csv_path)
    if not data:
        print(f"Aucune donnée lue depuis {csv_path}")
        return

    stats = compute_stats(data)

    print("Statistiques de latence (ms):")
    print(f"  n = {stats['count']}")
    print(f"  mean = {stats['mean_ms']:.2f}")
    print(f"  median = {stats['median_ms']:.2f}")
    print(f"  std = {stats['std_ms']:.2f}")
    print(f"  P90 = {stats['p90_ms']:.2f}")
    print(f"  P99 = {stats['p99_ms']:.2f}")

    out_path = Path(args.out)
    make_plot(data, out_path, stats, bins=args.bins)
    print(f"Graphique sauvegardé dans: {out_path}")


if __name__ == '__main__':
    main()
