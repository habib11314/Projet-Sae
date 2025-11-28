"""
Very small plot showing min, mean, max of latency samples.
Saves PNG to tools/latency_min_mean_max.png by default.
Usage:
    python tools/plot_latency_min_mean_max.py --csv ../latencies_attribution_redis.csv --out tools/latency_min_mean_max.png
"""
import argparse
import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def read_first_numeric_column(csv_path):
    vals = []
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        _ = next(reader, None)
        for row in reader:
            if not row:
                continue
            for cell in row:
                try:
                    v = float(cell)
                    vals.append(v)
                    break
                except Exception:
                    continue
    return vals


def compute_min_mean_max(arr):
    a = np.array(arr)
    return {
        'min': float(np.min(a)),
        'mean': float(np.mean(a)),
        'max': float(np.max(a)),
        'count': int(a.size)
    }


def make_plot(stats, out_path):
    # French labels for clarity
    labels = ['min', 'moyenne', 'max']
    values = [stats['min'], stats['mean'], stats['max']]

    fig, ax = plt.subplots(figsize=(6,4))
    bars = ax.bar(labels, values, color=['#55A868','#4C72B0','#C44E52'])
    ax.set_ylabel('Temps (ms)')
    # Slightly raise the title and make room via pad
    ax.set_title("Délai d'attribution des commandes (ms)", pad=14)

    # Thicken the black frame (spines) a bit so the rectangle is more visible
    try:
        for spine in ax.spines.values():
            spine.set_linewidth(2.2)
    except Exception:
        pass

    # Annotate values on bars with a white background box so they remain readable
    for i, (bar, val) in enumerate(zip(bars, values)):
        h = bar.get_height()
        # smaller offset for the top label so it doesn't collide with the frame
        offset = max(values) * (0.012 if i == 2 else 0.02)
        txt = ax.text(
            bar.get_x() + bar.get_width()/2,
            h + offset,
            f"{val:.1f} ms",
            ha='center', va='bottom', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.85),
            zorder=10,
            clip_on=False,
        )

    # Legend with colored blocks and values (French labels)
    from matplotlib.patches import Patch

    legend_handles = [
        Patch(facecolor='#55A868', label=f"min : {stats['min']:.1f} ms"),
        Patch(facecolor='#4C72B0', label=f"moyenne : {stats['mean']:.1f} ms"),
        Patch(facecolor='#C44E52', label=f"max : {stats['max']:.1f} ms"),
    ]

    # Place legend as a box with colored squares + labels
    # Place legend as a box with colored squares + labels (original sizing)
    ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(0.01, 0.95), fontsize=9, framealpha=0.9)

    # Display sample count below the legend
    ax.text(0.01, 0.70, f"n = {stats['count']} commandes", transform=ax.transAxes, fontsize=9, va='top', ha='left', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # leave a little extra room at the top so the title doesn't collide
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', '-c', default='../data/latencies_attribution_redis.csv')
    parser.add_argument('--out', '-o', default='../outputs/latency_min_mean_max.png')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Fichier CSV introuvable: {csv_path}")
        return

    vals = read_first_numeric_column(csv_path)
    if not vals:
        print("Aucune donnée lue")
        return

    stats = compute_min_mean_max(vals)
    out_path = Path(args.out)
    make_plot(stats, out_path)
    print(f"Graphique min/mean/max sauvegardé: {out_path} (n={stats['count']})")

if __name__ == '__main__':
    main()
