from dotenv import load_dotenv
import os
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone
import sys

# load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

if len(sys.argv) < 2:
    print('Usage: force_accept_delivery.py <numero_commande> [id_livreur(optional)]')
    sys.exit(1)

numero = sys.argv[1]
_id_livreur = sys.argv[2] if len(sys.argv) > 2 else None

query = {'numero_commande': numero, 'status': 'requested'}
if _id_livreur:
    query['id_livreur'] = _id_livreur

res = db.DeliveryRequests.find_one_and_update(query, {
    '$set': {'status': 'accepted', 'responded_at': datetime.now(timezone.utc)}
})

if not res:
    print('Aucune DeliveryRequest trouvée pour', numero)
else:
    print('DeliveryRequest marquée accepted pour', numero, '->', res.get('_id'))

client.close()
