#!/usr/bin/env python3
"""Measure assignment delay from db.Metrics and produce stats + a small bar chart.

Usage:
  py .\tools\measure_assignment_delay.py --n 200 --out assignment_delay_stats.png

Dependencies:
  pip install matplotlib numpy pymongo

The script reads the most recent N metrics documents from the `Metrics` collection
and expects each document to contain an integer field `assignment_delay_ms` and
a timestamp `ts`.
"""
import os
import sys
import argparse
from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt


def parse_args():
    p = argparse.ArgumentParser(description="Measure assignment delay from MongoDB Metrics collection")
    p.add_argument('--n', type=int, default=200, help='Number of latest metrics to read (default: 200)')
    p.add_argument('--out', default='assignment_delay_stats.png', help='Output PNG filename')
    return p.parse_args()


def main():
    args = parse_args()
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    dbname = os.getenv('MONGODB_DATABASE', 'Ubereats')

    try:
        client = MongoClient(uri)
        db = client[dbname]
    except Exception as e:
        print(f"Erreur connexion MongoDB: {e}")
        sys.exit(1)

    docs = list(db.Metrics.find().sort('ts', -1).limit(args.n))
    if not docs:
        print("Aucune métrique trouvée dans la collection 'Metrics'.")
        client.close()
        sys.exit(1)

    # Extract delays (ms), keep only numeric values
    delays = [d.get('assignment_delay_ms') for d in docs if isinstance(d.get('assignment_delay_ms'), (int, float))]
    if not delays:
        print("Aucune valeur 'assignment_delay_ms' numérique trouvée dans les documents récupérés.")
        client.close()
        sys.exit(1)

    # Reverse to chronological order (oldest -> newest)
    delays = delays[::-1]
    n = len(delays)
    min_v = int(min(delays))
    avg_v = float(np.mean(delays))
    max_v = int(max(delays))

    print(f"n = {n} commandes")
    print(f"min : {min_v} ms")
    print(f"moyenne : {avg_v:.1f} ms")
    print(f"max : {max_v} ms")

    # Create a small bar chart
    labels = ['min', 'moyenne', 'max']
    values = [min_v, avg_v, max_v]
    colors = ['#2ca02c', '#1f77b4', '#d62728']

    plt.figure(figsize=(6, 4.2), dpi=100)
    bars = plt.bar(labels, values, color=colors)
    plt.title(f"Délai d'attribution des commandes (n={n})")
    plt.ylabel('Temps (ms)')

    # annotate values
    top = max(values)
    for bar, v in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, v + top * 0.02, f"{v:.1f} ms", ha='center', va='bottom', fontsize=9)

    plt.grid(axis='y', alpha=0.2)
    plt.tight_layout()

    out_path = os.path.abspath(args.out)
    try:
        plt.savefig(out_path)
        print(f"Graphique sauvegardé: {out_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du graphique: {e}")

    client.close()


if __name__ == '__main__':
    main()
