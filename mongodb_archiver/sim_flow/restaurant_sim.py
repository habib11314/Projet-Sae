"""Restaurant simulator
Watches `RestaurantRequests` and randomly accepts or rejects requests for its restaurant.
If accepted, updates the request status to 'accepted'.
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

print(f"🔗 Connecting to: {MONGODB_URI[:50]}...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
print(f"✅ Connected to database: {DB_NAME}")
print()

# For simplicity this simulator listens for any RestaurantRequests and decides
# Accept/Reject randomly based on a configured acceptance_rate
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
        # Pretty print incoming request
        print()
        print("─" * 60)
        print("📥 NOUVELLE REQUÊTE RESTAURANT")
        print("─" * 60)
        print(f"   📦 Commande : {numero}")
        print(f"   🍽️  Restaurant: {rest_id}")
        print("   🎲 Décision  : En cours...")
        print("─" * 60)

        # Decide accept or reject
        accepted = random.random() < ACCEPTANCE_RATE
        status = 'accepted' if accepted else 'rejected'

        db.RestaurantRequests.update_one({'_id': req['_id']}, {'$set': {'status': status, 'responded_at': datetime.now(timezone.utc)}})

        # Response block
        print()
        print("┌" + "─" * 56 + "┐")
        if accepted:
            print(f"│ ✅ ACCEPTÉE{' ' * 43}│")
        else:
            print(f"│ ❌ REFUSÉE{' ' * 44}│")
        print(f"│   Commande : {numero}{' ' * (32 - len(numero))}│")
        print(f"│   Restaurant: {rest_id}{' ' * (31 - len(str(rest_id)))}│")
        print(f"│   Time      : {datetime.now(timezone.utc).isoformat()}{' ' * 3}│")
        print("└" + "─" * 56 + "┘")

except KeyboardInterrupt:
    print('\n[RESTAURANT] Stopped by user')
finally:
    client.close()
