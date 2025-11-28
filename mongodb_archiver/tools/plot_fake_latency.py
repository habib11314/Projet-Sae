#!/usr/bin/env python3
"""Quick plot of synthetic assignment latency to produce a PNG immediately.

This avoids MongoDB and is useful to get the visualization done fast.
"""
from __future__ import annotations
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def generate_delays(n=200):
    vals = []
    for _ in range(n):
        v = max(0, int(random.gauss(800, 400)))
        if random.random() < 0.02:
            v += random.randint(1000, 8000)
        vals.append(v)
    return vals


def plot_and_save(min_v: float, avg_v: float, max_v: float, n: int, out_path: str) -> None:
    labels = ['min', 'moyenne', 'max']
    values = [min_v, avg_v, max_v]
    colors = ['#2ca02c', '#1f77b4', '#d62728']

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=100)
    bars = ax.bar(labels, values, color=colors, edgecolor='black')

    ax.set_title("Délai d'attribution des commandes (ms)")
    ax.set_ylabel('Temps (ms)')

    for spine in ax.spines.values():
        spine.set_linewidth(1.8)

    handles = [Patch(facecolor=colors[i], edgecolor='black', label=labels[i]) for i in range(len(labels))]
    handles.append(Patch(facecolor='white', edgecolor='none', label=f'n = {n}'))
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)

    top = max(values) if values else 0
    for bar, v in zip(bars, values):
        cx = bar.get_x() + bar.get_width() / 2
        cy = v
        text = f"{v:.1f} ms"
        ax.text(cx, cy + top * 0.02, text, ha='center', va='bottom', fontsize=9,
                bbox=dict(facecolor='white', edgecolor='none', pad=1.0))

    ax.grid(axis='y', alpha=0.25)
    plt.tight_layout()

    out_abspath = os.path.abspath(out_path)
    plt.savefig(out_abspath)
    print(f"Graphique sauvegardé: {out_abspath}")


def main():
    n = 200
    delays = generate_delays(n)
    delays_arr = np.array(delays)
    min_v = float(np.min(delays_arr))
    avg_v = float(np.mean(delays_arr))
    max_v = float(np.max(delays_arr))
    out = 'assignment_delay_fake.png'
    print(f"Génération de {n} valeurs synthétiques -> min={min_v:.1f} ms, avg={avg_v:.1f} ms, max={max_v:.1f} ms")
    plot_and_save(min_v, avg_v, max_v, n, out)


if __name__ == '__main__':
    main()
