#!/usr/bin/env python3
"""Seed the Metrics collection with synthetic assignment_delay_ms documents.

Usage:
  py .\tools\seed_fake_metrics.py --n 200

Options:
  --mongo-uri, --db, --collection, --n

This is intentionally dependency-light (only standard library + pymongo).
"""
from __future__ import annotations
import os
import sys
import argparse
import random
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient


def parse_args():
    p = argparse.ArgumentParser(description="Insert synthetic metrics into MongoDB for testing")
    p.add_argument('--mongo-uri', default=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    p.add_argument('--db', default=os.getenv('MONGODB_DATABASE', 'Ubereats'))
    p.add_argument('--collection', default='Metrics')
    p.add_argument('--n', type=int, default=200, help='Number of synthetic metrics to insert')
    return p.parse_args()


def main():
    args = parse_args()

    try:
        client = MongoClient(args.mongo_uri)
    except Exception as e:
        print(f"Erreur de connexion MongoDB: {e}")
        sys.exit(2)

    db = client[args.db]
    coll = db[args.collection]

    now = datetime.now(timezone.utc)
    docs = []
    for i in range(args.n):
        # simulate delays roughly between 100ms and 5000ms, with occasional larger outliers
        base = int(max(10, random.gauss(800, 400)))
        if random.random() < 0.02:
            base = base + random.randint(1000, 10000)

        assignment_delay_ms = max(0, base)

        # delivery_request_ts a bit before assigned_at
        assigned_at = now - timedelta(seconds=(args.n - i))  # spread timestamps
        delivery_request_ts = assigned_at - timedelta(milliseconds=assignment_delay_ms)

        doc = {
            'numero_commande': f"fake-{int(now.timestamp())}-{i}",
            'delivery_request_ts': delivery_request_ts,
            'assigned_at': assigned_at,
            'assignment_delay_ms': int(assignment_delay_ms),
            'ts': assigned_at
        }
        docs.append(doc)

    if not docs:
        print("Aucun document à insérer")
        client.close()
        return

    try:
        res = coll.insert_many(docs)
        print(f"Insertés {len(res.inserted_ids)} documents dans {args.db}.{args.collection}")
    except Exception as e:
        print(f"Erreur insertion: {e}")
        client.close()
        sys.exit(3)

    client.close()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Seed fake assignment metrics into db.Metrics for testing/visualization.

Usage:
  py .\tools\seed_fake_metrics.py --n 200

This will insert N documents with realistic-looking timestamps and assignment_delay_ms.
"""
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import random
from pathlib import Path

# load .env if present (same convention as other scripts)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except Exception:
    pass


def parse_args():
    p = argparse.ArgumentParser(description="Seed fake assignment metrics into MongoDB")
    p.add_argument('--n', type=int, default=200, help='Number of fake metrics to insert')
    p.add_argument('--min-ms', type=int, default=150, help='Minimum assignment delay in ms')
    p.add_argument('--max-ms', type=int, default=1200, help='Maximum assignment delay in ms')
    p.add_argument('--drop', action='store_true', help='If set, delete existing seeded metrics with prefix before inserting')
    p.add_argument('--prefix', default='seed', help='Prefix for numero_commande to identify seeded documents')
    return p.parse_args()


def main():
    args = parse_args()
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    dbname = os.getenv('MONGODB_DATABASE', 'Ubereats')
    # diagnostic print (mask credentialed URI)
    try:
        if '://' in uri and '@' in uri:
            print(f"Utilisation MongoDB URI: ***masked*** DB: {dbname}")
        else:
            print(f"Utilisation MongoDB URI: {uri} DB: {dbname}")
    except Exception:
        pass

    try:
        client = MongoClient(uri)
        db = client[dbname]
    except Exception as e:
        print(f"Erreur connexion MongoDB: {e}")
        sys.exit(1)

    n = args.n
    now = datetime.now(timezone.utc)

    if args.drop:
        # remove previously seeded docs with this prefix
        deleted = db.Metrics.delete_many({'numero_commande': {'$regex': f'^{args.prefix}-'}})
        print(f"Supprimé {deleted.deleted_count} documents existants avec le préfixe '{args.prefix}-'.")

    docs = []
    # Create documents from oldest to newest so ts ordering is chronological
    for i in range(n):
        # spread assignments in the last n seconds to look realistic
        assigned_at = now - timedelta(seconds=(n - i))
        delay_ms = random.randint(args.min_ms, args.max_ms)
        delivery_request_ts = assigned_at - timedelta(milliseconds=delay_ms)
        doc = {
            'numero_commande': f"{args.prefix}-{i+1}",
            'delivery_request_ts': delivery_request_ts,
            'assigned_at': assigned_at,
            'assignment_delay_ms': delay_ms,
            'ts': assigned_at
        }
        docs.append(doc)

    try:
        res = db.Metrics.insert_many(docs)
        print(f"Inséré {len(res.inserted_ids)} documents dans {dbname}.Metrics")
    except Exception as e:
        print(f"Erreur insertion: {e}")
    finally:
        client.close()


if __name__ == '__main__':
    main()
