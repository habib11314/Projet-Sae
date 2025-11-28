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
    print('Usage: assign_delivery_manual.py <numero_commande>')
    sys.exit(1)

numero = sys.argv[1]

# find accepted delivery request
dr = db.DeliveryRequests.find_one({'numero_commande': numero, 'status': 'accepted'})
if not dr:
    print('No accepted DeliveryRequest found for', numero)
    client.close()
    sys.exit(1)

assigned_livreur = dr.get('id_livreur')
livreur_doc = db.Livreur.find_one({'id_livreur': assigned_livreur}) or {}
livreur_name = livreur_doc.get('Nom') or livreur_doc.get('nom') or assigned_livreur
livreur_phone = livreur_doc.get('Téléphone') or livreur_doc.get('telephone')

# Update commande and livreur
db.Commande.update_one({'numero_commande': numero}, {'$set': {'status': 'en_cours', 'id_livreur': assigned_livreur}})
db.Livreur.update_one({'id_livreur': assigned_livreur}, {'$set': {'statut': 'en_course', 'numero_commande': numero}})

# Insert notification
message = f"Votre commande {numero} a été prise en charge par le livreur {livreur_name} (id: {assigned_livreur})"
if livreur_phone:
    message += f" - Tel: {livreur_phone}"

notification = {
    'numero_commande': numero,
    'id_client': db.Commande.find_one({'numero_commande': numero}).get('id_client'),
    'message': message,
    'sent_at': datetime.now(timezone.utc)
}
db.Notifications.insert_one(notification)

print('Assigned', numero, 'to', assigned_livreur)
client.close()
