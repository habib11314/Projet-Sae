"""Simple polling-based restaurant simulator (non-ChangeStream version)
"""
import os
import time
import random
from datetime import datetime, timezone
from pymongo import MongoClient
from pathlib import Path

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("⚠️  python-dotenv non installé")

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

ACCEPTANCE_RATE = float(os.getenv('RESTAURANT_ACCEPT_RATE', '0.8'))

print("Restaurant simulator started. Press Ctrl+C to stop.")

try:
    while True:
        req = db.RestaurantRequests.find_one({'status': 'requested'})
        if not req:
            time.sleep(1)
            continue

        numero = req['numero_commande']
        rest_id = req.get('id_restaurant')

        accepted = random.random() < ACCEPTANCE_RATE
        status = 'accepted' if accepted else 'rejected'

        db.RestaurantRequests.update_one({'_id': req['_id']}, {'$set': {'status': status, 'responded_at': datetime.now(timezone.utc)}})

        if accepted:
            print(f"[RESTAURANT] Accepted {numero} by {rest_id}")
        else:
            print(f"[RESTAURANT] Rejected {numero} by {rest_id}")

except KeyboardInterrupt:
    print('\n[RESTAURANT] Stopped by user')
finally:
    client.close()
