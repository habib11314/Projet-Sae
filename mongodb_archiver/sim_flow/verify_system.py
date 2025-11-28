"""Test si les simulateurs Change Streams détectent et traitent les commandes"""
import os
import time
from datetime import datetime, timezone
from pymongo import MongoClient
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
except:
    pass

MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

print("\n" + "="*70)
print("  TEST: Les simulateurs Change Streams fonctionnent-ils?")
print("="*70)

# Créer une commande de test
test_num = f"TEST-VERIFY-{int(time.time())}"
client_doc = list(db.Client.aggregate([{"$sample": {"size": 1}}]))[0]
rest_doc = list(db.Restaurants.aggregate([{"$sample": {"size": 1}}]))[0]

order = {
    "numero_commande": test_num,
    "id_client": client_doc.get('id_client'),
    "id_restaurant": rest_doc.get('id_restaurant'),
    "Produit": "Test Product",
    "adresse_livraison": "Test Address",
    "coût_commande": 10.0,
    "status": 'pending_request',
    "date_commande": datetime.now(timezone.utc)
}

print(f"\n📤 Création commande test: {test_num}")
print(f"   Restaurant: {rest_doc.get('id_restaurant')}")
db.Commande.insert_one(order)
print("✅ Commande créée avec status='pending_request'")

print("\n⏱️  Attente 10s pour que la platform la détecte...")
time.sleep(10)

# Vérifier si la platform a créé une requête restaurant
rest_req = db.RestaurantRequests.find_one({'numero_commande': test_num})
if rest_req:
    print(f"✅ PLATFORM FONCTIONNE! Requête restaurant créée")
    print(f"   Status: {rest_req.get('status')}")
else:
    print(f"❌ PLATFORM NE FONCTIONNE PAS - Aucune requête restaurant")
    print("\n💡 Solutions possibles:")
    print("   1. Vérifiez que platform_sim_changestreams.py tourne")
    print("   2. Relancez: py launcher_changestreams.py")
    print("   3. Regardez les erreurs dans le terminal PLATFORM")
    client.close()
    exit(1)

print("\n⏱️  Attente 10s pour réponse restaurant...")
time.sleep(10)

rest_req = db.RestaurantRequests.find_one({'numero_commande': test_num})
if rest_req and rest_req.get('status') in ['accepted', 'rejected']:
    print(f"✅ RESTAURANT FONCTIONNE! Réponse: {rest_req.get('status')}")
    
    if rest_req.get('status') == 'accepted':
        print("\n⏱️  Attente 10s pour requête livreur...")
        time.sleep(10)
        
        deliv_req = db.DeliveryRequests.find_one({'numero_commande': test_num})
        if deliv_req:
            print(f"✅ Requête livreur créée! Status: {deliv_req.get('status')}")
            
            print("\n⏱️  Attente 10s pour réponse livreur...")
            time.sleep(10)
            
            deliv_req = db.DeliveryRequests.find_one({'numero_commande': test_num})
            if deliv_req and deliv_req.get('status') == 'accepted':
                print(f"✅ LIVREUR FONCTIONNE! Livreur a accepté")
                
                # Vérifier statut final
                final_order = db.Commande.find_one({'numero_commande': test_num})
                print(f"\n📊 Statut final commande: {final_order.get('status')}")
                
                if final_order.get('status') == 'en_cours':
                    print("\n🎉 SUCCÈS COMPLET! Tous les simulateurs fonctionnent!")
                    print(f"   Livreur assigné: {final_order.get('id_livreur')}")
                else:
                    print(f"\n⚠️  Statut attendu 'en_cours', reçu '{final_order.get('status')}'")
            else:
                print("⚠️  Livreur n'a pas encore accepté")
        else:
            print("❌ Aucune requête livreur - Platform n'a pas trouvé de livreur")
else:
    print("⚠️  Restaurant n'a pas encore répondu")

print("="*70)
client.close()
