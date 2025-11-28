"""Simple test to check if MongoDB Change Streams are supported"""
import os
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

print("\n" + "="*70)
print("  🧪 TEST SUPPORT CHANGE STREAMS")
print("="*70)
print()

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

print(f"📡 URI MongoDB: {MONGODB_URI[:30]}...")
print(f"📁 Database: {DB_NAME}")
print()

# Try to open a change stream
try:
    print("🔍 Test d'ouverture d'un Change Stream sur la collection Commande...")
    with db.Commande.watch() as stream:
        print("✅ Change Stream ouvert avec succès!")
        print(f"   Resume token: {stream.resume_token}")
        print()
        print("✅ Votre MongoDB supporte les Change Streams!")
        
except Exception as e:
    print(f"❌ ERREUR: Impossible d'ouvrir un Change Stream")
    print(f"   Type: {type(e).__name__}")
    print(f"   Message: {e}")
    print()
    print("⚠️  Causes possibles:")
    print("   1. MongoDB version < 3.6")
    print("   2. Connection pas sur un replica set")
    print("   3. MongoDB Atlas: tier gratuit (M0) ne supporte pas Change Streams")
    print("   4. Configuration du serveur")
    
finally:
    client.close()

print("="*70)
print()
