import os
from pymongo import MongoClient
from pprint import pprint

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'Ubereats')

print('Using URI:', 'MONGODB_URI' in os.environ)
print('DB_NAME:', DB_NAME)

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    # connection ping
    client.admin.command('ping')
    print('\n✅ Connected to MongoDB')

    # Count total livreurs
    total = db.Livreur.count_documents({})
    dispo = db.Livreur.count_documents({'statut': 'disponible'})
    print(f"\nLivreur total: {total}")
    print(f"Livreur statut='disponible': {dispo}\n")

    # Show a few examples
    print('Exemples (up to 5) :')
    for doc in db.Livreur.find().limit(5):
        pprint(doc)
    
    # Show any livreur with city field
    print('\nLivreurs with city (up to 5):')
    for doc in db.Livreur.find({'city': {'$exists': True}}).limit(5):
        pprint(doc)

    # Show if location field exists and 2dsphere index
    has_location = db.Livreur.count_documents({'location': {'$exists': True}}) > 0
    print('\nAny document with "location" field?:', has_location)
    print('Indexes on Livreur:')
    pprint(list(db.Livreur.index_information().items()))

    # Try geo query only if location present
    if has_location:
        try:
            sample = db.Livreur.find({'location': {'$exists': True}}).limit(1)[0]
            print('\nSample location coordinates:', sample.get('location'))
        except Exception as e:
            print('\nCould not read sample location:', e)

except Exception as e:
    print('ERROR connecting to MongoDB:', type(e).__name__, str(e))
finally:
    try:
        client.close()
    except Exception:
        pass
