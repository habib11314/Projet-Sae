#!/usr/bin/env python3
"""Compute latency statistics from a CSV of latencies (ms).

Usage:
    python tools/compute_latency.py [path/to/latencies_attribution_redis.csv]

If no path is provided the script looks for '../latencies_attribution_redis.csv' relative to this script.
"""
import csv
import sys
import os
from statistics import mean, median, pstdev


def read_latencies(path):
    lat = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        # optionally skip header if present
        first = next(reader, None)
        try:
            float(first[0])
            lat.append(float(first[0]))
        except Exception:
            # header or invalid, ignore
            pass
        for row in reader:
            if not row:
                continue
            try:
                lat.append(float(row[0]))
            except Exception:
                continue
    return lat


def percentiles(data, ps=(50, 90, 99)):
    if not data:
        return {p: None for p in ps}
    s = sorted(data)
    n = len(s)
    res = {}
    for p in ps:
        # linear interpolation
        k = (p / 100) * (n - 1)
        lo = int(k)
        hi = min(lo + 1, n - 1)
        frac = k - lo
        val = s[lo] * (1 - frac) + s[hi] * frac
        res[p] = val
    return res


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data', 'latencies_attribution_redis.csv')
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(2)

    lat = read_latencies(path)
    if not lat:
        print("No latency data found in file.")
        sys.exit(1)

    cnt = len(lat)
    avg = mean(lat)
    med = median(lat)
    std = pstdev(lat) if cnt > 1 else 0.0
    p = percentiles(lat, (50, 90, 99))

    print("Latency statistics (milliseconds)")
    print("---------------------------------")
    print(f"Samples: {cnt}")
    print(f"Mean:    {avg:.3f} ms")
    print(f"Median:  {med:.3f} ms")
    print(f"StdPop:  {std:.3f} ms")
    print(f"P50:     {p[50]:.3f} ms")
    print(f"P90:     {p[90]:.3f} ms")
    print(f"P99:     {p[99]:.3f} ms")


if __name__ == '__main__':
    main()
