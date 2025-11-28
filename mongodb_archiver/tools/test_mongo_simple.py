from pymongo import MongoClient
from urllib.parse import quote_plus
import os

# Lit MONGODB_URI depuis les variables d'environnement ou .env
uri = os.getenv('MONGODB_URI') or os.getenv('MONGO_URI') or ""
if not uri:
    print('ERROR: aucune variable MONGODB_URI trouvée dans l\'environnement')
    raise SystemExit(2)

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # petite opération pour forcer la connexion
    client.admin.command('ping')
    print('✅ MongoDB : connexion OK')
except Exception as e:
    print('❌ MongoDB : échec de connexion —', type(e).__name__, str(e))
    raise
finally:
    try:
        client.close()
    except Exception:
        pass
