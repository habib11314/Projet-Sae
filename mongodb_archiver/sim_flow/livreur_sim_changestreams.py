"""Livreur simulator with Change Streams
Watches DeliveryRequests using Change Streams and randomly accepts or rejects.
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
print("  🚚 LIVREUR SIMULATOR (Change Streams)")
print("=" * 70)
print()
print(f"🔗 Connexion à MongoDB...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
def _mask_mongo_uri(uri: str) -> str:
    try:
        if '://' in uri and '@' in uri:
            prefix, rest = uri.split('://', 1)
            userinfo, host = rest.split('@', 1)
            return f"{prefix}://***:***@{host}"
    except Exception:
        pass
    return uri

print(f"✅ Connecté à la base: {DB_NAME} (URI: {_mask_mongo_uri(MONGODB_URI)})")
print()

ACCEPT_RATE = float(os.getenv('LIVREUR_ACCEPT_RATE', '0.7'))

print("🔄 Écoute des requêtes livreur via Change Streams...")
print(f"   Taux d'acceptation: {ACCEPT_RATE*100}%")
print()
print("💡 Appuyez sur Ctrl+C pour arrêter")
print("=" * 70)
print()

# Auto-register this livreur in the Livreur collection so the platform
# can find available livreurs without a separate data population step.
LIVREUR_ID = os.getenv('LIVREUR_ID') or f"LIV-{random.randint(1000,9999)}"
LIVREUR_NAME = os.getenv('LIVREUR_NAME') or f"Livreur {LIVREUR_ID}"
LIVREUR_PRENOM = os.getenv('LIVREUR_PRENOM')
LIVREUR_NOM = os.getenv('LIVREUR_NOM')
LIVREUR_CITY = os.getenv('LIVREUR_CITY')
LIVREUR_COORDS = None
coords_env = os.getenv('LIVREUR_COORDS')
if coords_env:
    try:
        parts = [float(x.strip()) for x in coords_env.split(',')]
        if len(parts) == 2:
            LIVREUR_COORDS = parts
    except Exception:
        LIVREUR_COORDS = None

try:
    upsert_doc = {
        'id_livreur': LIVREUR_ID,
        'statut': 'disponible',
        'last_seen': datetime.now(timezone.utc)
    }
    # prefer explicit prenom/nom env vars; otherwise use LIVREUR_NAME as Nom
    if LIVREUR_PRENOM:
        upsert_doc['Prénom'] = LIVREUR_PRENOM
    if LIVREUR_NOM:
        upsert_doc['Nom'] = LIVREUR_NOM
    if not (LIVREUR_PRENOM or LIVREUR_NOM):
        upsert_doc['Nom'] = LIVREUR_NAME
    if LIVREUR_CITY:
        upsert_doc['city'] = LIVREUR_CITY
    if LIVREUR_COORDS:
        upsert_doc['location'] = {'type': 'Point', 'coordinates': LIVREUR_COORDS}

    db.Livreur.update_one({'id_livreur': LIVREUR_ID}, {'$set': upsert_doc}, upsert=True)
    print(f"🔁 Livreur enregistré / mis à jour: {LIVREUR_ID} (statut=disponible)")
except Exception as e:
    print(f"⚠️ Erreur lors de l'enregistrement du livreur: {e}")

try:
    # Watch for inserts in DeliveryRequests with status='requested'
    pipeline = [
        {
            '$match': {
                'operationType': 'insert',
                'fullDocument.status': 'requested'
            }
        }
    ]
    
    with db.DeliveryRequests.watch(pipeline) as stream:
        for change in stream:
            req = change.get('fullDocument')
            if not req:
                continue

            numero = req['numero_commande']
            livreur_id = req.get('id_livreur')

            # Pretty print incoming delivery request
            print()
            print("─" * 60)
            print("🚚 NOUVELLE REQUÊTE LIVREUR (Change Stream)")
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

                # Optionally watch the livreur document for any further updates
                ldoc = db.Livreur.find_one({'id_livreur': livreur_id})
                if ldoc and ldoc.get('numero_commande'):
                    print(f"   [INFO] Vous êtes assigné à la commande {ldoc.get('numero_commande')}")

except KeyboardInterrupt:
    print('\n[LIVREUR] Stopped by user')
finally:
    client.close()
