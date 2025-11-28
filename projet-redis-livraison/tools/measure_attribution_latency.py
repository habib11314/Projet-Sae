#!/usr/bin/env python3
"""Measure attribution latency for the Redis Pub/Sub manager.

This script supports two modes:
- real (default): uses a real Redis instance and expects a manager to react to
  offers and publish attribution messages.
- --simulate: runs an internal simulated manager that listens to offers and
  publishes attribution messages after a small random delay (no Redis required).

Outputs:
- latencies_attribution_redis.csv : CSV with measured latencies (ms)
- latency_attribution_redis_hist.png : histogram of latencies

Usage:
  python tools/measure_attribution_latency.py --simulate
  python tools/measure_attribution_latency.py --count 200

"""
import argparse
import csv
import json
import os
import random
import statistics
import threading
import time
from uuid import uuid4

try:
    import redis
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False

import matplotlib.pyplot as plt


DEFAULT_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'latencies_attribution_redis.csv')
DEFAULT_PNG = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'latency_attribution_redis_hist.png')


def simulated_manager_worker(pub_queue, stop_event, min_delay=0.001, max_delay=0.020):
    """Thread that simulates a manager reacting to offers.

    It reads offers from a simple in-memory queue (list) and after a short
    random delay publishes an attribution by placing a dict into the same
    queue as a 'notification'. This simulation mode avoids Redis dependency
    and allows quick local rendering of results.
    """
    while not stop_event.is_set():
        try:
            offer = None
            with pub_queue['lock']:
                if pub_queue['offers']:
                    offer = pub_queue['offers'].pop(0)
            if offer is None:
                time.sleep(0.001)
                continue

            # simulate processing delay
            time.sleep(random.uniform(min_delay, max_delay))

            # publish attribution
            notification = {
                'type': 'attribution',
                'id_commande': offer['id_commande'],
                'id_livreur': 'sim-livreur-001',
                'ts': time.time()
            }
            with pub_queue['lock']:
                pub_queue['notifications'].append(notification)

        except Exception:
            time.sleep(0.01)


def measure_simulation(count=200, csv_path=DEFAULT_CSV, png_path=DEFAULT_PNG):
    pub_queue = {'offers': [], 'notifications': [], 'lock': threading.Lock()}
    stop_event = threading.Event()
    t = threading.Thread(target=simulated_manager_worker, args=(pub_queue, stop_event), daemon=True)
    t.start()

    latencies = []
    for i in range(count):
        id_commande = str(uuid4())
        offer = {'id_commande': id_commande, 'test_ts': time.time()}
        with pub_queue['lock']:
            pub_queue['offers'].append(offer)
        sent_at = time.time()

        # wait for notification
        timeout = 5.0
        deadline = time.time() + timeout
        got = False
        while time.time() < deadline:
            with pub_queue['lock']:
                if pub_queue['notifications']:
                    for idx, n in enumerate(pub_queue['notifications']):
                        if n.get('id_commande') == id_commande and n.get('type') == 'attribution':
                            # consume
                            pub_queue['notifications'].pop(idx)
                            attributed_at = n.get('ts', time.time())
                            lat_ms = (attributed_at - sent_at) * 1000.0
                            latencies.append(lat_ms)
                            got = True
                            break
            if got:
                break
            time.sleep(0.001)

        if not got:
            # record a timeout value
            latencies.append(timeout * 1000.0)

        # small pacing to avoid too tight loop
        time.sleep(0.01)

    stop_event.set()
    t.join(timeout=1.0)

    # save CSV and PNG
    _save_and_plot(latencies, csv_path, png_path)
    return latencies


def measure_redis(count=200, redis_host='localhost', redis_port=6379, csv_path=DEFAULT_CSV, png_path=DEFAULT_PNG):
    if not HAS_REDIS:
        raise RuntimeError('redis-py is required for real Redis measurement')

    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    # channels
    offers_channel = 'offres-courses'
    notify_channel = 'notifications-livreur:measure-test'

    pubsub = r.pubsub()
    pubsub.subscribe(notify_channel)

    latencies = []
    for i in range(count):
        id_commande = str(uuid4())
        offer = {'id_commande': id_commande, 'test_ts': time.time()}
        sent_at = time.time()
        r.publish(offers_channel, json.dumps(offer, ensure_ascii=False))

        # wait for notification
        timeout = 5.0
        deadline = time.time() + timeout
        got = False
        while time.time() < deadline:
            message = pubsub.get_message(timeout=0.1)
            if message and message.get('type') == 'message':
                try:
                    payload = json.loads(message['data'])
                    if payload.get('id_commande') == id_commande and payload.get('type') == 'attribution':
                        attributed_at = time.time()
                        lat_ms = (attributed_at - sent_at) * 1000.0
                        latencies.append(lat_ms)
                        got = True
                        break
                except Exception:
                    pass
        if not got:
            latencies.append(timeout * 1000.0)
        time.sleep(0.02)

    _save_and_plot(latencies, csv_path, png_path)
    return latencies


def _save_and_plot(latencies, csv_path, png_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['latency_ms'])
        for v in latencies:
            w.writerow([f"{v:.6f}"])

    mn = min(latencies)
    mx = max(latencies)
    avg = statistics.mean(latencies)

    plt.figure(figsize=(7,4))
    plt.hist(latencies, bins=30, color='tab:green', edgecolor='black')
    plt.title('Distribution des latences d\'attribution (Redis Pub/Sub)')
    plt.xlabel('Latence (ms)')
    plt.ylabel('Nombre de mesures')
    plt.axvline(avg, color='red', linestyle='--', label=f'Moyenne = {avg:.2f} ms')
    plt.legend()
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    plt.close()

    print(f"Saved CSV: {csv_path}")
    print(f"Saved plot: {png_path}")
    print(f"Min={mn:.2f} ms, Max={mx:.2f} ms, Avg={avg:.2f} ms")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulate', action='store_true', help='Run internal simulation (no Redis required)')
    parser.add_argument('--count', type=int, default=200, help='Number of measurements')
    parser.add_argument('--csv', default=DEFAULT_CSV, help='CSV output path')
    parser.add_argument('--png', default=DEFAULT_PNG, help='PNG output path')
    parser.add_argument('--host', default='localhost', help='Redis host')
    parser.add_argument('--port', type=int, default=6379, help='Redis port')
    args = parser.parse_args()

    if args.simulate:
        lat = measure_simulation(count=args.count, csv_path=args.csv, png_path=args.png)
    else:
        lat = measure_redis(count=args.count, redis_host=args.host, redis_port=args.port, csv_path=args.csv, png_path=args.png)

    # brief summary
    print('\nSummary:')
    print(f'  Samples: {len(lat)}')
    print(f'  Min: {min(lat):.2f} ms')
    print(f'  Max: {max(lat):.2f} ms')
    print(f'  Avg: {statistics.mean(lat):.2f} ms')


if __name__ == '__main__':
    main()
