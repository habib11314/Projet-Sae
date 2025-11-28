#!/usr/bin/env python3
"""Inspect Metrics collection and print distribution + top docs.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import numpy as np
import pprint

def main():
    load_dotenv()
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    dbname = os.getenv('MONGODB_DATABASE', 'Ubereats')
    print('Using URI:', uri)
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[dbname]
    cursor = db.Metrics.find({'assignment_delay_ms': {'$type': ['int','double','long']}})
    vals = [d['assignment_delay_ms'] for d in cursor]
    if not vals:
        print('No numeric assignment_delay_ms found')
        return
    arr = np.array(vals, dtype=float)
    print('n =', len(arr))
    print('min =', arr.min(), 'mean =', arr.mean(), 'max =', arr.max())
    for p in [25,50,75,90,95,99]:
        print(f'p{p} =', np.percentile(arr, p))
    print('\nHistogram (buckets):')
    bins = [0,100,250,500,1000,2000,5000,10000,20000,100000]
    hist, edges = np.histogram(arr, bins=bins)
    for c,e0,e1 in zip(hist, edges[:-1], edges[1:]):
        print(f' {e0:>6.0f} - {e1:>6.0f}: {c}')

    print('\nTop 5 largest docs:')
    docs = list(db.Metrics.find({'assignment_delay_ms': {'$exists': True}}).sort('assignment_delay_ms', -1).limit(5))
    pp = pprint.PrettyPrinter(width=140)
    for d in docs:
        pp.pprint({
            'assignment_delay_ms': d.get('assignment_delay_ms'),
            'numero_commande': d.get('numero_commande'),
            'delivery_request_ts': d.get('delivery_request_ts'),
            'assigned_at': d.get('assigned_at'),
            '_id': d.get('_id')
        })

if __name__ == '__main__':
    main()
