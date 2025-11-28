"""Restaurant simulator with Change Streams
Watches RestaurantRequests using Change Streams and randomly accepts or rejects.
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

print()
print("=" * 70)
print("  🍽️  RESTAURANT SIMULATOR (Change Streams)")
print("=" * 70)
print()
print(f"🔗 Connexion à MongoDB...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
print(f"✅ Connecté à la base: {DB_NAME}")
print()

ACCEPTANCE_RATE = float(os.getenv('RESTAURANT_ACCEPT_RATE', '0.8'))

print("🔄 Écoute des requêtes restaurant via Change Streams...")
print(f"   Taux d'acceptation: {ACCEPTANCE_RATE*100}%")
print()
print("💡 Appuyez sur Ctrl+C pour arrêter")
print("=" * 70)
print()

try:
    # Watch for inserts in RestaurantRequests with status='requested'
    pipeline = [
        {
            '$match': {
                'operationType': 'insert',
                'fullDocument.status': 'requested'
            }
        }
    ]
    
    with db.RestaurantRequests.watch(pipeline) as stream:
        for change in stream:
            req = change.get('fullDocument')
            if not req:
                continue
            
            numero = req['numero_commande']
            rest_id = req.get('id_restaurant')

            # Pretty print incoming request
            print()
            print("─" * 60)
            print("📥 NOUVELLE REQUÊTE RESTAURANT (Change Stream)")
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
