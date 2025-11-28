from dotenv import load_dotenv
import os
from pathlib import Path
from pymongo import MongoClient
import sys
import json

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

if len(sys.argv) < 2:
    print('Usage: show_order_status.py <numero_commande>')
    sys.exit(1)

numero = sys.argv[1]
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def pretty(doc):
    try:
        return json.dumps(doc, default=str, ensure_ascii=False, indent=2)
    except Exception:
        return str(doc)

print('--- Commande ---')
cmd = db.Commande.find_one({'numero_commande': numero})
print(pretty(cmd))

print('\n--- RestaurantRequests ---')
rrs = list(db.RestaurantRequests.find({'numero_commande': numero}))
for r in rrs:
    print(pretty(r))

print('\n--- DeliveryRequests ---')
drs = list(db.DeliveryRequests.find({'numero_commande': numero}))
for d in drs:
    print(pretty(d))

print('\n--- Notifications ---')
nts = list(db.Notifications.find({'numero_commande': numero}))
for n in nts:
    print(pretty(n))

print('\n--- Livreurs matching any id in DeliveryRequests ---')
ids = [d.get('id_livreur') for d in drs if d.get('id_livreur')]
for lid in ids:
    l = db.Livreur.find_one({'id_livreur': lid})
    print(pretty(l))

client.close()
