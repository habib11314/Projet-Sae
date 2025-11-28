"""Platform simulator
Monitors new orders with status 'pending_request' and sends a request document
for the restaurant (in collection RestaurantRequests). Waits for restaurant response;
if accepted, requests available livreurs by inserting in DeliveryRequests.
Listens for livreur acceptance and updates Commande status accordingly.
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
print("  🏢 PLATFORM SIMULATOR - Orchestrateur de commandes")
print("=" * 70)
print()
print(f"🔗 Connexion à MongoDB...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
print(f"✅ Connecté à la base: {DB_NAME}")
print()
print("🎯 Démarrage de l'orchestrateur...")
print("   • Détecte les commandes en attente")
print("   • Envoie requêtes aux restaurants")
print("   • Cherche des livreurs disponibles")
print("   • Assigne les commandes")
print()
print("💡 Appuyez sur Ctrl+C pour arrêter")
print("=" * 70)
print()

try:
    # Use Change Streams to watch for new orders
    print("🔄 Utilisation de Change Streams pour surveiller les commandes...")
    print()
    
    # Watch for inserts or updates on Commande collection with status='pending_request'
    pipeline = [
        {
            '$match': {
                '$or': [
                    {'operationType': 'insert', 'fullDocument.status': 'pending_request'},
                    {'operationType': 'update', 'updateDescription.updatedFields.status': 'pending_request'}
                ]
            }
        }
    ]
    
    with db.Commande.watch(pipeline) as stream:
        for change in stream:
            order = change.get('fullDocument')
            if not order:
                continue
            
            numero = order['numero_commande']
            rest_id = order.get('id_restaurant')
        
        print()
        print("─" * 70)
        print(f"🔍 NOUVELLE COMMANDE DÉTECTÉE")
        print("─" * 70)
        print(f"   📦 N° Commande  : {numero}")
        print(f"   🍽️  Restaurant  : {rest_id}")
        print(f"   📤 Action      : Envoi requête au restaurant...")
        print("─" * 70)

        # Create restaurant request document
        req = {
            'numero_commande': numero,
            'id_restaurant': rest_id,
            'status': 'requested',
            'requested_at': datetime.now(timezone.utc)
        }
        db.RestaurantRequests.insert_one(req)
        print(f"   ✅ Requête envoyée")

        # Wait for restaurant response (poll)
        print(f"   ⏳ Attente réponse restaurant (max 60s)...")
        response = None
        for i in range(60):  # wait up to 60s
            response = db.RestaurantRequests.find_one({'numero_commande': numero, 'id_restaurant': rest_id})
            if response and response.get('status') in ['accepted', 'rejected']:
                break
            if i % 10 == 0 and i > 0:
                print(f"   ... {i}s écoulées")
            time.sleep(1)

        if not response or response.get('status') != 'accepted':
            # Formatted rejection block
            print()
            print("─" * 70)
            print("🍽️  RÉPONSE RESTAURANT - REFUS / TIMEOUT")
            print("─" * 70)
            print(f"   📦 Commande : {numero}")
            print(f"   🍽️  Restaurant: {rest_id}")
            print(f"   ⏱️  Réponse   : Aucun / rejet")
            print("   📝 Action    : Mise à jour -> rejected_by_restaurant")
            print("─" * 70)
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'rejected_by_restaurant'}})
            continue

        # Formatted acceptance block
        print()
        print("─" * 70)
        print("🍽️  RÉPONSE RESTAURANT - ACCEPTÉE")
        print("─" * 70)
        print(f"   📦 Commande : {numero}")
        print(f"   🍽️  Restaurant: {rest_id}")
        print(f"   ✅ Statut    : accepted")
        print("   📝 Action    : Recherche de livreurs disponibles...")
        print("─" * 70)

        # Find available livreur
        # We assume Livreurs have field 'statut' and 'id_livreur'
        livreur = db.Livreur.find_one({'statut': 'disponible'})
        if not livreur:
            print(f"[PLATFORM] No available livreurs for {numero}. Marking pending")
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'waiting_for_livreur'}})
            continue

        # Create delivery request
        delivery_req = {
            'numero_commande': numero,
            'id_livreur': livreur['id_livreur'],
            'status': 'requested',
            'requested_at': datetime.now(timezone.utc)
        }
        db.DeliveryRequests.insert_one(delivery_req)
        print(f"[PLATFORM] Delivery request sent to livreur {livreur['id_livreur']} for {numero}")

        # Wait for livreur response
        for _ in range(30):
            dr = db.DeliveryRequests.find_one({'numero_commande': numero, 'id_livreur': livreur['id_livreur']})
            if dr and dr.get('status') in ['accepted', 'rejected']:
                break
            time.sleep(1)

        dr = db.DeliveryRequests.find_one({'numero_commande': numero, 'id_livreur': livreur['id_livreur']})
        if not dr or dr.get('status') != 'accepted':
            print(f"[PLATFORM] Livreur did not accept for {numero}. Marking waiting")
            db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'waiting_for_livreur'}})
            continue

        # Livreur accepted -> assign and notify client (enrichi)
        # Re-fetch livreur to get latest details (name, phone, etc.)
        livreur_doc = db.Livreur.find_one({'id_livreur': livreur['id_livreur']}) or livreur
        assigned_livreur = livreur_doc['id_livreur']

        # Update commande and livreur records
        db.Commande.update_one(
            {'numero_commande': numero},
            {'$set': {'status': 'en_cours', 'id_livreur': assigned_livreur}}
        )
        db.Livreur.update_one(
            {'id_livreur': assigned_livreur},
            {'$set': {'statut': 'en_course', 'numero_commande': numero}}
        )

        # Pretty assignment block
        print()
        print("─" * 70)
        print("🚀 ATTRIBUTION DE COMMANDE AU LIVREUR")
        print("─" * 70)
        print(f"   📦 Commande : {numero}")
        print(f"   🧑‍🚚 Livreur  : {assigned_livreur} ({livreur_doc.get('nom', 'nom_inconnu')})")
        if livreur_doc.get('telephone'):
            print(f"   📞 Téléphone: {livreur_doc.get('telephone')}")
        print(f"   ✅ Statut    : en_cours")
        print("   📝 Action    : Commande assignée et livreur notifié")
        print("─" * 70)

        # Send enriched notification to client
        livreur_name = livreur_doc.get('nom') or str(assigned_livreur)
        livreur_phone = livreur_doc.get('telephone')
        message = f"Votre commande {numero} a été prise en charge par le livreur {livreur_name} (id: {assigned_livreur})"
        if livreur_phone:
            message += f" - Tel: {livreur_phone}"

        notification = {
            'numero_commande': numero,
            'id_client': order.get('id_client'),
            'message': message,
            'sent_at': datetime.now(timezone.utc)
        }
        db.Notifications.insert_one(notification)
        print(f"   ✉️ Notification envoyée au client {order.get('id_client')}")

except KeyboardInterrupt:
    print('\n[PLATFORM] Stopped by user')
finally:
    client.close()
