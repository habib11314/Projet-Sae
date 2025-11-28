#!/usr/bin/env python3
"""Plot latency values (min/mean/max) from a MongoDB collection field and save a PNG.

Usage:
  py .\tools\plot_latency_mongo.py --mongo-uri <URI> --db <DB> --collection <COL> --field <FIELD> --limit 200 --out latency.png

The script connects to MongoDB, reads up to --limit documents from --collection,
extracts numeric values from --field, computes min/mean/max and n, then builds a
3-bar PNG annotated in French.

Dependencies:
  pip install pymongo numpy matplotlib
"""
from __future__ import annotations
import os
import sys
import argparse
from typing import List
from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Load .env automatically when available so scripts that rely on MONGODB_URI work
try:
    from dotenv import load_dotenv
    # load .env from repo root (cwd) if present
    load_dotenv()
except Exception:
    # if python-dotenv is not installed, continue — the script will rely on real env vars
    pass


def parse_args():
    p = argparse.ArgumentParser(description="Génère un PNG avec min/moyenne/max pour un champ numérique stocké dans MongoDB")
    p.add_argument('--mongo-uri', default=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'), help='MongoDB URI')
    p.add_argument('--db', default=os.getenv('MONGODB_DATABASE', 'Ubereats'), help='Nom de la base de données')
    p.add_argument('--collection', default='Metrics', help='Nom de la collection')
    p.add_argument('--field', default='assignment_delay_ms', help='Champ numérique à lire')
    p.add_argument('--out', default='assignment_delay_stats.png', help='Fichier PNG de sortie')
    p.add_argument('--limit', type=int, default=200, help='Nombre maximum de documents à lire (défaut: 200)')
    return p.parse_args()


def fetch_numeric_values(client: MongoClient, dbname: str, coll_name: str, field: str, limit: int) -> List[float]:
    db = client[dbname]
    coll = db[coll_name]
    # Try to sort by 'ts' if present (newest first) to mimic typical metrics behaviour
    try:
        cursor = coll.find({}, {field: 1}).sort('ts', -1).limit(limit)
    except Exception:
        cursor = coll.find({}, {field: 1}).limit(limit)

    values: List[float] = []
    for doc in cursor:
        v = doc.get(field)
        if v is None:
            continue
        # accept int/float and convert other numeric-like values when possible
        try:
            fv = float(v)
        except Exception:
            # skip non-convertible values
            continue
        # skip NaN
        if np.isnan(fv):
            continue
        values.append(fv)

    return values


def plot_and_save(min_v: float, avg_v: float, max_v: float, n: int, out_path: str) -> None:
    labels = ['min', 'moyenne', 'max']
    values = [min_v, avg_v, max_v]
    colors = ['#2ca02c', '#1f77b4', '#d62728']

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=100)
    bars = ax.bar(labels, values, color=colors, edgecolor='black')

    # Title and labels (French)
    ax.set_title(f"Délai d'attribution des commandes (ms)")
    ax.set_ylabel('Temps (ms)')

    # Thick spines (cadre)
    for spine in ax.spines.values():
        spine.set_linewidth(1.8)

    # Legend with small colored blocks + n
    handles = [Patch(facecolor=colors[i], edgecolor='black', label=labels[i]) for i in range(len(labels))]
    handles.append(Patch(facecolor='white', edgecolor='none', label=f'n = {n}'))
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)

    # Annotate bars with rounded values and white bbox
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
    args = parse_args()

    try:
        # Use a short serverSelectionTimeoutMS so failures are reported quickly
        client = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=5000)
        # force a connection attempt to surface auth/network errors early
        client.server_info()
    except Exception as e:
        print(f"Erreur de connexion MongoDB (URI={args.mongo_uri}): {e}")
        sys.exit(2)

    try:
        values = fetch_numeric_values(client, args.db, args.collection, args.field, args.limit)
    except Exception as e:
        print(f"Erreur lors de la lecture des documents: {e}")
        client.close()
        sys.exit(2)

    if not values:
        print(f"Aucun enregistrement numérique trouvé pour le champ '{args.field}' dans {args.db}.{args.collection}.")
        client.close()
        sys.exit(3)

    # Compute stats
    n = len(values)
    min_v = float(np.min(values))
    avg_v = float(np.mean(values))
    max_v = float(np.max(values))

    print(f"n = {n} enregistrements analysés")
    print(f"min = {min_v:.1f} ms, moyenne = {avg_v:.1f} ms, max = {max_v:.1f} ms")

    try:
        plot_and_save(min_v, avg_v, max_v, n, args.out)
    except Exception as e:
        print(f"Erreur lors de la génération du graphique: {e}")
        client.close()
        sys.exit(4)

    client.close()


if __name__ == '__main__':
    main()
