# 🚀 DÉMARRAGE RAPIDE DE LA SIMULATION

## ⚠️ ÉTAPES OBLIGATOIRES AVANT DE LANCER

### Étape 1: Configurer MongoDB URI ✅ FAIT

Le fichier `.env` a été créé dans le dossier parent. 

**ACTION REQUISE**: Ouvrez `C:\Users\PC\mongodb_archiver\.env` et modifiez l'URI MongoDB:

```bash
# Pour MongoDB local:
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=Ubereats

# OU pour MongoDB Atlas:
MONGODB_URI=mongodb+srv://votre_user:votre_password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=Ubereats
```

### Étape 2: Peupler la base de données ⚠️ CRITIQUE

Les simulateurs ont besoin de données existantes. Lancez depuis `C:\Users\PC\mongodb_archiver`:

```powershell
# Installer les dépendances
pip install pymongo python-dotenv faker

# Générer 500 documents de test
python simulate.py --count 500
```

Cela créera:
- ✅ Clients (100)
- ✅ Restaurants (20)
- ✅ Menus (200)
- ✅ Livreurs (50)
- ✅ Commandes initiales (130)

### Étape 3: Lancer la simulation 🎬

```powershell
cd sim_flow
.\launch_all.bat
```

## 🎯 Ce qui va se passer

4 terminaux vont s'ouvrir:

```
┌─────────────────┬─────────────────┐
│  CLIENT         │  PLATFORM       │
│  (crée ordres)  │  (orchestre)    │
├─────────────────┼─────────────────┤
│  RESTAURANT     │  LIVREUR        │
│  (accepte 80%)  │  (accepte 70%)  │
└─────────────────┴─────────────────┘
```

### Si les terminaux s'ouvrent puis se ferment immédiatement:

**Problème**: Fichier `.env` manquant ou URI MongoDB invalide

**Solution**: 
1. Vérifiez que `.env` existe dans `C:\Users\PC\mongodb_archiver`
2. Vérifiez que l'URI MongoDB est correcte
3. Testez la connexion:
   ```powershell
   python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); print('URI:', os.getenv('MONGODB_URI')); client = MongoClient(os.getenv('MONGODB_URI')); print('Connexion OK:', client.server_info()['version'])"
   ```

### Si les terminaux affichent "No clients in DB":

**Problème**: Base de données vide

**Solution**: Exécutez l'étape 2 (peupler la base)

## 📝 Commandes utiles

```powershell
# Vérifier la configuration
cd C:\Users\PC\mongodb_archiver
type .env

# Installer les dépendances
pip install -r requirements.txt

# Tester la connexion MongoDB
python -c "from pymongo import MongoClient; from dotenv import load_dotenv; import os; load_dotenv(); client = MongoClient(os.getenv('MONGODB_URI')); print('Connexion OK! Version:', client.server_info()['version'])"

# Peupler la base
python simulate.py --count 500

# Lancer la simulation
cd sim_flow
.\launch_all.bat
```

## 🐛 Dépannage

### Erreur: "python-dotenv not found"
```powershell
pip install python-dotenv
```

### Erreur: "pymongo not found"
```powershell
pip install pymongo
```

### Erreur: "Connection refused"
- Vérifiez que MongoDB est démarré (si local)
- Vérifiez l'URI dans `.env`
- Testez avec MongoDB Compass

### Les terminaux se ferment immédiatement
- Ouvrez un terminal CMD manuellement et lancez:
  ```cmd
  cd C:\Users\PC\mongodb_archiver
  python sim_flow\client_sim.py
  ```
- Cela affichera l'erreur exacte

---

**🎬 Une fois ces 3 étapes complétées, la simulation fonctionnera parfaitement !**
