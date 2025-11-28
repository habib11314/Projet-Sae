"""Client simulator with Change Streams
Creates random orders and watches for status changes and notifications using Change Streams.
"""
import os
import sys
import time
import random
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId
from pathlib import Path
import threading

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
print("  🛒 CLIENT SIMULATOR (Change Streams)")
print("=" * 70)
print()
print(f"🔗 Connexion à MongoDB...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
print(f"✅ Connecté à la base: {DB_NAME}")
print()
print("📱 Démarrage du simulateur client...")
print("   • Crée des commandes aléatoires")
print("   • Surveille les changements via Change Streams")
print("   • Affiche les notifications en temps réel")
print()
print("💡 Appuyez sur Ctrl+C pour arrêter")
print("=" * 70)
print()

def watch_order_status(numero, id_client):
    """Watch order status changes using Change Streams"""
    pipeline = [
        {
            '$match': {
                'operationType': 'update',
                'fullDocument.numero_commande': numero,
                'updateDescription.updatedFields.status': {'$exists': True}
            }
        }
    ]
    
    try:
        with db.Commande.watch(pipeline) as stream:
            for change in stream:
                doc = change.get('fullDocument')
                if not doc:
                    continue
                
                status = doc.get('status')
                print()
                print("🔔 CHANGEMENT DE STATUT (Change Stream)")
                print(f"   📦 Commande : {numero}")
                print(f"   ⏭️  Nouveau  : {status}")
                
                if status in ['livrée', 'annulée', 'rejected_by_restaurant']:
                    print()
                    if status == 'livrée':
                        print(f"✅ COMMANDE LIVRÉE avec succès!")
                    elif status == 'rejected_by_restaurant':
                        print(f"❌ COMMANDE REFUSÉE par le restaurant")
                    else:
                        print(f"🚫 COMMANDE ANNULÉE")
                    print()
                    break
    except Exception as e:
        print(f"⚠️  Erreur Change Stream commande: {e}")

def watch_notifications(numero, id_client):
    """Watch for notifications using Change Streams"""
    pipeline = [
        {
            '$match': {
                'operationType': 'insert',
                'fullDocument.numero_commande': numero,
                'fullDocument.id_client': id_client
            }
        }
    ]
    
    try:
        with db.Notifications.watch(pipeline) as stream:
            for change in stream:
                notif = change.get('fullDocument')
                if not notif:
                    continue 
                
                print()
                print("─" * 60)
                print("📣 NOTIFICATION REÇUE (Change Stream)")
                print("─" * 60)
                print(f"   📝 Message : {notif.get('message')}")
                print(f"   ⏱️  Envoyé   : {notif.get('sent_at')}")
                print("─" * 60)
                
                # Mark notification as seen
                db.Notifications.update_one({'_id': notif['_id']}, {'$set': {'seen_at': datetime.now(timezone.utc)}})
    except Exception as e:
        print(f"⚠️  Erreur Change Stream notification: {e}")

try:
    while True:
        # Pick a random existing client
        client_doc = db.Client.aggregate([{"$sample": {"size": 1}}])
        client_doc = list(client_doc)
        if not client_doc:
            print("⚠️  Aucun client dans la base. Attente 5s...")
            time.sleep(5)
            continue
        client_doc = client_doc[0]

        # Pick a random restaurant
        rest_doc = db.Restaurants.aggregate([{"$sample": {"size": 1}}])
        rest_doc = list(rest_doc)
        if not rest_doc:
            print("⚠️  Aucun restaurant dans la base. Attente 5s...")
            time.sleep(5)
            continue
        rest_doc = rest_doc[0]

        # Pick a menu item
        menu_doc = db.Menu.aggregate([{"$sample": {"size": 1}}])
        menu_doc = list(menu_doc)
        menu_doc = menu_doc[0] if menu_doc else None

        numero = f"SIM-{int(time.time())}-{random.randint(1000,9999)}"
        
        client_name = client_doc.get('Prénom', '') + ' ' + client_doc.get('Nom', 'Client')
        resto_name = rest_doc.get('name', rest_doc.get('Nom', 'Restaurant inconnu'))
        produit_name = menu_doc.get('name', 'Produit inconnu') if menu_doc else 'Produit inconnu'
        
        order = {
            "numero_commande": numero,
            "id_commande": str(ObjectId()),
            "id_client": client_doc.get('id_client'),
            "id_restaurant": rest_doc.get('id_restaurant'),
            "id_menu": menu_doc.get('id_menu') if menu_doc else None,
            "Nom": client_name,
            "Produit": produit_name,
            "adresse_livraison": client_doc.get('Adresse', 'Adresse inconnue'),
            "coût_commande": menu_doc.get('price', 10.0) if menu_doc else 10.0,
            "rémunération_livreur": 0.0,
            "moyen_de_payement": random.choice(['CB', 'Espèces']),
            "status": 'pending_request',
            "date_commande": datetime.now(timezone.utc),
            "temps_estimee": menu_doc.get('temps_preparation', 20) if menu_doc else 20
        }

        result = db.Commande.insert_one(order)
        
        print()
        print("─" * 70)
        print(f"🆕 NOUVELLE COMMANDE CRÉÉE")
        print("─" * 70)
        print(f"   📝 Numéro      : {numero}")
        print(f"   👤 Client      : {client_name}")
        print(f"   🍽️  Restaurant  : {resto_name}")
        print(f"   🍕 Produit     : {produit_name}")
        print(f"   💰 Prix        : {order['coût_commande']:.2f} €")
        print(f"   📍 Livraison   : {order['adresse_livraison'][:40]}...")
        print(f"   🔄 Statut      : {order['status']}")
        print("─" * 70)
        print()
        print(f"👀 Écoute via Change Streams pour {numero}...")
        print()

        # Start watching in separate threads
        status_thread = threading.Thread(target=watch_order_status, args=(numero, order.get('id_client')), daemon=True)
        notif_thread = threading.Thread(target=watch_notifications, args=(numero, order.get('id_client')), daemon=True)
        
        status_thread.start()
        notif_thread.start()

        # Wait a bit before creating a new order
        print("⏳ Attente de 10 secondes avant nouvelle commande...")
        print()
        time.sleep(10)

except KeyboardInterrupt:
    print()
    print("=" * 70)
    print("  ⚠️  SIMULATEUR CLIENT ARRÊTÉ PAR L'UTILISATEUR")
    print("=" * 70)
    print()
finally:
    client.close()
