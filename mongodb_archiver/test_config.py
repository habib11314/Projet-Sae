"""Test de configuration avant de lancer la simulation
Ce script vérifie que tout est prêt pour la simulation
"""
import os
import sys

def test_dotenv():
    """Test si python-dotenv est installé"""
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv installé")
        return True
    except ImportError:
        print("❌ python-dotenv manquant")
        print("   Installez avec: pip install python-dotenv")
        return False

def test_pymongo():
    """Test si pymongo est installé"""
    try:
        import pymongo
        print(f"✅ pymongo {pymongo.__version__} installé")
        return True
    except ImportError:
        print("❌ pymongo manquant")
        print("   Installez avec: pip install pymongo")
        return False

def test_env_file():
    """Test si le fichier .env existe"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print(f"✅ Fichier .env trouvé: {env_path}")
        return True
    else:
        print(f"❌ Fichier .env manquant: {env_path}")
        print("   Créez le fichier .env avec MONGODB_URI et MONGODB_DATABASE")
        return False

def test_mongodb_connection():
    """Test la connexion à MongoDB"""
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        
        # Charger .env depuis le dossier parent
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        
        uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DATABASE', 'Ubereats')
        
        if not uri:
            print("❌ MONGODB_URI non défini dans .env")
            return False
        
        print(f"🔗 Test de connexion à: {uri[:30]}...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test la connexion
        info = client.server_info()
        print(f"✅ Connexion MongoDB OK! Version: {info['version']}")
        
        # Liste les collections
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"✅ Base de données '{db_name}' trouvée")
        print(f"   Collections: {', '.join(collections) if collections else 'VIDE'}")
        
        # Compte les documents nécessaires
        needed = {
            'Client': db.Client.count_documents({}),
            'Restaurants': db.Restaurants.count_documents({}),
            'Menu': db.Menu.count_documents({}),
            'Livreur': db.Livreur.count_documents({}),
        }
        
        print("\n📊 Documents dans la base:")
        all_ok = True
        for coll, count in needed.items():
            if count > 0:
                print(f"   ✅ {coll}: {count} documents")
            else:
                print(f"   ⚠️  {coll}: VIDE (lancez python simulate.py --count 500)")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        return False

def main():
    print("=" * 60)
    print("  TEST DE CONFIGURATION - SIMULATION MULTI-TERMINAUX")
    print("=" * 60)
    print()
    
    results = []
    
    print("1️⃣  Vérification des dépendances Python...")
    results.append(test_dotenv())
    results.append(test_pymongo())
    print()
    
    print("2️⃣  Vérification du fichier .env...")
    results.append(test_env_file())
    print()
    
    if all(results):
        print("3️⃣  Test de connexion MongoDB...")
        db_ok = test_mongodb_connection()
        results.append(db_ok)
        print()
    
    print("=" * 60)
    if all(results):
        print("🎉 TOUT EST PRÊT !")
        print()
        print("Lancez la simulation avec:")
        print("  cd sim_flow")
        print("  .\\launch_all.bat")
    else:
        print("⚠️  CONFIGURATION INCOMPLÈTE")
        print()
        print("Actions requises:")
        if not results[0]:
            print("  • pip install python-dotenv")
        if not results[1]:
            print("  • pip install pymongo")
        if not results[2]:
            print("  • Créez le fichier .env avec MONGODB_URI")
        if len(results) > 3 and not results[3]:
            print("  • Vérifiez l'URI MongoDB dans .env")
            print("  • OU lancez: python simulate.py --count 500")
    print("=" * 60)
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
