from dotenv import load_dotenv
import os
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone
from bson import ObjectId
import random
import time

# load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Try to sample an existing client/restaurant/menu
try:
    c = list(db.Client.aggregate([{"$sample": {"size": 1}}]))
    client_doc = c[0] if c else None
except Exception:
    client_doc = None

try:
    r = list(db.Restaurants.aggregate([{"$sample": {"size": 1}}]))
    rest_doc = r[0] if r else None
except Exception:
    rest_doc = None

try:
    m = list(db.Menu.aggregate([{"$sample": {"size": 1}}]))
    menu_doc = m[0] if m else None
except Exception:
    menu_doc = None

numero = f"TEST-{int(time.time())}-{random.randint(100,999)}"
order = {
    "numero_commande": numero,
    "id_commande": str(ObjectId()),
    "id_client": client_doc.get('id_client') if client_doc else 'test_client',
    "id_restaurant": rest_doc.get('id_restaurant') if rest_doc else 'test_rest',
    "id_menu": menu_doc.get('id_menu') if menu_doc else None,
    "Nom": (client_doc.get('Prénom','') + ' ' + client_doc.get('Nom','Client')) if client_doc else 'Client Test',
    "Produit": menu_doc.get('name') if menu_doc else 'Produit Test',
    "adresse_livraison": client_doc.get('Adresse','Adresse Test') if client_doc else 'Adresse Test',
    "coût_commande": float(menu_doc.get('price', 10.0)) if menu_doc else 10.0,
    "rémunération_livreur": 0.0,
    "moyen_de_payement": random.choice(['CB','Espèces']),
    "status": 'pending_request',
    "date_commande": datetime.now(timezone.utc),
    "temps_estimee": int(menu_doc.get('temps_preparation', 20)) if menu_doc else 20
}

res = db.Commande.insert_one(order)
print(f"INSERTED_TEST_ORDER {numero} -> _id={res.inserted_id}")
client.close()
