import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Input CSV expected: one latency value per line (seconds)
CSV_PATH = Path(__file__).parent / "assignment_latencies.csv"
OUT_PNG = Path(__file__).parent / "assignment_latency_hist.png"


def load_latencies(path):
    lat = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            try:
                lat.append(float(row[0]))
            except ValueError:
                continue
    return np.array(lat)


def main():
    lat = load_latencies(CSV_PATH)
    if lat.size == 0:
        print("No data found in", CSV_PATH)
        return

    mean = lat.mean()
    median = np.median(lat)
    p90 = np.percentile(lat, 90)
    p99 = np.percentile(lat, 99)

    fig, ax = plt.subplots(figsize=(8,5))
    ax.hist(lat, bins=30, color='#4C72B0', alpha=0.9)
    ax.axvline(mean, color='orange', linestyle='--', label=f'Mean {mean:.2f}s')
    ax.axvline(median, color='green', linestyle=':', label=f'Median {median:.2f}s')
    ax.set_xlabel("Assignment latency (s)")
    ax.set_ylabel('Count')
    ax.set_title("Distribution des latences d'attribution (MongoDB Change Streams)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(OUT_PNG, dpi=150)
    print("Graph generated:", OUT_PNG)
    print(f"Stats: mean={mean:.2f}s, median={median:.2f}s, p90={p90:.2f}s, p99={p99:.2f}s")


if __name__ == "__main__":
    main()
