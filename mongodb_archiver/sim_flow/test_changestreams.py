"""Test script to verify Change Streams flow works end-to-end"""
import os
import time
from datetime import datetime, timezone
from pymongo import MongoClient
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

print("\n" + "="*70)
print("  🧪 TEST CHANGE STREAMS - VERIFICATION DU FLUX COMPLET")
print("="*70)
print()

# Get a random client and restaurant
test_client = db.Client.aggregate([{'$sample': {'size': 1}}]).next()
test_restaurant = db.Restaurants.aggregate([{'$sample': {'size': 1}}]).next()

print(f"📋 Client de test   : {test_client.get('Nom', test_client.get('nom', 'Inconnu'))}")
print(f"📋 Restaurant de test: {test_restaurant.get('Nom', test_restaurant.get('nom', 'Inconnu'))}")
print()

# Create a test order
order_num = f"TEST-{int(time.time())}-{os.getpid()}"
order = {
    'numero_commande': order_num,
    'id_client': test_client.get('id_client', test_client.get('_id')),
    'id_restaurant': test_restaurant.get('id_restaurant', test_restaurant.get('_id')),
    'produit': 'Test Product',
    'prix': 10.0,
    'adresse_livraison': 'Test Address',
    'status': 'pending_request',
    'created_at': datetime.now(timezone.utc)
}

print(f"📤 Création de la commande test: {order_num}")
db.Commande.insert_one(order)
print(f"✅ Commande créée avec statut: pending_request")
print()

print("⏳ Attente de 5 secondes pour que la platform détecte la commande...")
time.sleep(5)

# Check if platform created a restaurant request
rest_req = db.RestaurantRequests.find_one({'numero_commande': order_num})
if rest_req:
    print(f"✅ Platform a créé une requête restaurant (statut: {rest_req.get('status')})")
else:
    print(f"❌ Aucune requête restaurant trouvée pour {order_num}")

print()
print("⏳ Attente de 5 secondes pour la réponse du restaurant...")
time.sleep(5)

# Check restaurant response
rest_req = db.RestaurantRequests.find_one({'numero_commande': order_num})
if rest_req:
    print(f"🍽️  Statut requête restaurant: {rest_req.get('status')}")
    if rest_req.get('status') == 'accepted':
        print("✅ Restaurant a accepté la commande")
    else:
        print(f"⚠️  Restaurant n'a pas encore accepté")
else:
    print("❌ Aucune requête restaurant")

print()
print("⏳ Attente de 5 secondes pour la recherche de livreur...")
time.sleep(5)

# Check if delivery request was created
delivery_req = db.DeliveryRequests.find_one({'numero_commande': order_num})
if delivery_req:
    print(f"✅ Platform a créé une requête livreur (statut: {delivery_req.get('status')})")
    print(f"   ID Livreur: {delivery_req.get('id_livreur')}")
else:
    print(f"❌ Aucune requête livreur trouvée pour {order_num}")

print()
print("⏳ Attente de 5 secondes pour la réponse du livreur...")
time.sleep(5)

# Check delivery response
delivery_req = db.DeliveryRequests.find_one({'numero_commande': order_num})
if delivery_req:
    print(f"🚚 Statut requête livreur: {delivery_req.get('status')}")
    if delivery_req.get('status') == 'accepted':
        print("✅ Livreur a accepté la commande")
    else:
        print(f"⚠️  Livreur n'a pas encore accepté")
else:
    print("❌ Aucune requête livreur")

# Check final order status
final_order = db.Commande.find_one({'numero_commande': order_num})
print()
print("="*70)
print(f"📊 STATUT FINAL DE LA COMMANDE: {final_order.get('status')}")
if final_order.get('status') == 'en_cours':
    print(f"✅ SUCCÈS! Commande assignée au livreur {final_order.get('id_livreur')}")
    
    # Check notification
    notif = db.Notifications.find_one({'numero_commande': order_num})
    if notif:
        print(f"✅ Notification envoyée au client:")
        print(f"   {notif.get('message')}")
    else:
        print("⚠️  Aucune notification trouvée")
else:
    print(f"⚠️  Statut attendu: 'en_cours', reçu: '{final_order.get('status')}'")
print("="*70)
print()

client.close()
