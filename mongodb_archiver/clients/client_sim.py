"""Client simulator
Creates random orders by selecting existing clients/restaurants/menus from DB
and inserts a new Commande document with status 'pending_request'.
Then listens for notifications (status changes) for that order and prints updates.
"""
import os
import sys
import time
import random
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId
from pathlib import Path

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    # Charger .env depuis le dossier parent
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("⚠️  python-dotenv non installé. Utilisez: pip install python-dotenv")

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

print()
print("=" * 70)
print("  🛒 CLIENT SIMULATOR - Créateur de commandes")
print("=" * 70)
print()
print(f"🔗 Connexion à MongoDB...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
print(f"✅ Connecté à la base: {DB_NAME}")
print()
print("📱 Démarrage du simulateur client...")
print("   • Crée des commandes aléatoires")
print("   • Surveille les changements de statut")
print("   • Affiche les notifications")
print()
print("💡 Appuyez sur Ctrl+C pour arrêter")
print("=" * 70)
print()

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

        # Pick a menu item from that restaurant if Menu documents reference restaurant id_menu etc.
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

        # Listen for updates on this order using a simple polling (for portability)
        current_status = order['status']
        watch_coll = db.Commande
        print(f"👀 Surveillance des mises à jour pour {numero}...")
        print()
        shown_notifications = set()
        while True:
            # Check order document for status changes
            doc = watch_coll.find_one({"numero_commande": numero})
            if not doc:
                print("⚠️  Document de commande introuvable!")
                break
            status = doc.get('status')
            if status != current_status:
                print()
                print(f"🔔 CHANGEMENT DE STATUT")
                print(f"   📦 Commande : {numero}")
                print(f"   ⏮️  Ancien   : {current_status}")
                print(f"   ⏭️  Nouveau  : {status}")
                current_status = status
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

            # Check Notifications collection for messages for this order/client
            notif = db.Notifications.find_one({'numero_commande': numero, 'id_client': order.get('id_client')})
            if notif:
                nid = str(notif.get('_id'))
                if nid not in shown_notifications:
                    print()
                    print("─" * 60)
                    print("📣 NOTIFICATION REÇUE")
                    print("─" * 60)
                    print(f"   📝 Message : {notif.get('message')}")
                    print(f"   ⏱️  Envoyé   : {notif.get('sent_at')}")
                    print("─" * 60)
                    shown_notifications.add(nid)
                    # mark notification as seen
                    db.Notifications.update_one({'_id': notif['_id']}, {'$set': {'seen_at': datetime.now(timezone.utc)}})

            time.sleep(1)

        # Wait a bit before creating a new order
        print("⏳ Attente de 3 secondes avant nouvelle commande...")
        print()
        time.sleep(3)

except KeyboardInterrupt:
    print()
    print("=" * 70)
    print("  ⚠️  SIMULATEUR CLIENT ARRÊTÉ PAR L'UTILISATEUR")
    print("=" * 70)
    print()
finally:
    client.close()
