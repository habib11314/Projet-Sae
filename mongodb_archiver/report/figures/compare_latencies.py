import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

MONGO_CSV = Path(__file__).parent / "assignment_latencies.csv"  # seconds
REDIS_CSV = Path(__file__).parent / "redis_latencies.csv"      # milliseconds
OUT_PNG = Path(__file__).parent / "compare_assignment_latency.png"


def load_csv(path):
    vals = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            try:
                vals.append(float(row[0]))
            except ValueError:
                continue
    return np.array(vals)


def stats(arr):
    return {
        'count': int(arr.size),
        'min': float(np.min(arr)) if arr.size else None,
        'median': float(np.median(arr)) if arr.size else None,
        'mean': float(np.mean(arr)) if arr.size else None,
        'p90': float(np.percentile(arr, 90)) if arr.size else None,
        'p99': float(np.percentile(arr, 99)) if arr.size else None,
        'max': float(np.max(arr)) if arr.size else None,
    }


def pretty(s):
    return (f"count={s['count']}, min={s['min']:.3f}, median={s['median']:.3f}, "
            f"mean={s['mean']:.3f}, p90={s['p90']:.3f}, p99={s['p99']:.3f}, max={s['max']:.3f}")


def main():
    # load
    mongo = load_csv(MONGO_CSV)
    redis = load_csv(REDIS_CSV)

    # normalise: mongo assumed seconds -> convert to ms
    mongo_ms = mongo * 1000.0
    redis_ms = redis  # already ms

    s_mongo = stats(mongo_ms)
    s_redis = stats(redis_ms)

    print("Mongo latencies (ms):", pretty(s_mongo))
    print("Redis latencies (ms):", pretty(s_redis))

    # Plot side-by-side histograms and boxplot
    fig, axes = plt.subplots(1,3, figsize=(15,5), gridspec_kw={'width_ratios':[1,1,0.7]})

    axes[0].hist(mongo_ms, bins=30, color='#4C72B0', alpha=0.9)
    axes[0].axvline(s_mongo['mean'], color='orange', linestyle='--', label=f"mean {s_mongo['mean']:.2f} ms")
    axes[0].set_title('MongoDB (Change Streams)')
    axes[0].set_xlabel('Latency (ms)')
    axes[0].set_ylabel('Count')
    axes[0].legend()

    axes[1].hist(redis_ms, bins=30, color='#55A868', alpha=0.9)
    axes[1].axvline(s_redis['mean'], color='orange', linestyle='--', label=f"mean {s_redis['mean']:.2f} ms")
    axes[1].set_title('Redis (Pub/Sub)')
    axes[1].set_xlabel('Latency (ms)')
    axes[1].legend()

    axes[2].boxplot([mongo_ms, redis_ms], labels=['MongoDB', 'Redis'], vert=True)
    axes[2].set_title('Comparaison (boxplot)')

    plt.suptitle('Comparaison des latences d\'attribution : MongoDB vs Redis')
    plt.tight_layout(rect=[0,0,1,0.95])
    fig.savefig(OUT_PNG, dpi=150)
    print('Saved comparison plot to', OUT_PNG)

if __name__ == '__main__':
    main()
