"""Livreur (delivery driver) simulator
Watches `DeliveryRequests` and randomly accepts or rejects.
If accepted, updates request status to 'accepted' and marks the livreur as 'en_course'.
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

ACCEPT_RATE = float(os.getenv('LIVREUR_ACCEPT_RATE', '0.7'))

print("Livreur simulator started. Press Ctrl+C to stop.")

try:
    while True:
        req = db.DeliveryRequests.find_one({'status': 'requested'})
        if not req:
            time.sleep(1)
            continue

        numero = req['numero_commande']
        livreur_id = req.get('id_livreur')

        # Pretty print incoming delivery request
        print()
        print("─" * 60)
        print("🚚 NOUVELLE REQUÊTE LIVREUR")
        print("─" * 60)
        print(f"   📦 Commande : {numero}")
        print(f"   🧑‍🚚 Livreur  : {livreur_id}")
        print("   🎯 Statut   : En cours de décision...")
        print("─" * 60)

        # Simulate decision-making
        accepted = random.random() < ACCEPT_RATE
        status = 'accepted' if accepted else 'rejected'

        db.DeliveryRequests.update_one({'_id': req['_id']}, {'$set': {'status': status, 'responded_at': datetime.now(timezone.utc)}})

        # Response block
        print()
        print("┌" + "─" * 56 + "┐")
        if accepted:
            print(f"│ ✅ ACCEPTÉE PAR LIVREUR{' ' * 29}│")
        else:
            print(f"│ ❌ REFUSÉE PAR LIVREUR{' ' * 29}│")
        print(f"│   Commande : {numero}{' ' * (32 - len(str(numero)))}│")
        print(f"│   Livreur  : {livreur_id}{' ' * (33 - len(str(livreur_id)))}│")
        print(f"│   Time     : {datetime.now(timezone.utc).isoformat()}{' ' * 3}│")
        print("└" + "─" * 56 + "┘")

        if accepted:
            # Mark livreur as en_course and store assigned commande
            db.Livreur.update_one({'id_livreur': livreur_id}, {'$set': {'statut': 'en_course', 'numero_commande': numero}})

            # Pretty assignment banner for livreur
            print()
            print("═" * 60)
            print("🎉 ATTRIBUTION - LIVREUR")
            print("═" * 60)
            print(f"   🧑‍🚚 Livreur : {livreur_id}")
            print(f"   📦 Commande : {numero}")
            print("   ✅ Statut  : en_course")
            print("═" * 60)

            # Optionally watch the livreur document for any further updates (simple poll)
            ldoc = db.Livreur.find_one({'id_livreur': livreur_id})
            if ldoc and ldoc.get('numero_commande'):
                print(f"[LIVREUR] Vous êtes assigné à la commande {ldoc.get('numero_commande')}")
        else:
            print(f"[LIVREUR] Livreur {livreur_id} rejected the request for {numero}")

except KeyboardInterrupt:
    print('\n[LIVREUR] Stopped by user')
finally:
    client.close()
