# 🚀 GUIDE COMPLET - Simulation Multi-Terminaux

## ✅ État actuel de votre système

```
✅ Python 3.12.0 installé (accessible via 'py')
✅ pymongo 4.15.3 installé
✅ python-dotenv 1.0.0 installé
✅ Fichier .env créé
✅ Scripts de simulation créés (4 fichiers)
✅ Script launcher corrigé (launch_all.bat)

❌ MongoDB non accessible (localhost:27017 refuse connexion)
```

## 🎯 CE QUI VA SE PASSER APRÈS CONFIGURATION

```
┌─────────────────────────────────────────────────┐
│  Vous allez voir 4 TERMINAUX comme ceci:        │
└─────────────────────────────────────────────────┘

╔═══════════════════╗  ╔═══════════════════╗
║ TERMINAL 1        ║  ║ TERMINAL 2        ║
║ CLIENT SIMULATOR  ║  ║ PLATFORM          ║
║                   ║  ║                   ║
║ [CLIENT] Creating ║  ║ [PLATFORM] Detecte║
║ order SIM-...     ║  ║ pending order     ║
║                   ║  ║ Requesting resto  ║
║ [CLIENT] Status:  ║  ║ RES-00001...      ║
║ pending_request   ║  ║                   ║
║                   ║  ║ [PLATFORM] Resto  ║
║ [CLIENT] Status:  ║  ║ accepted!         ║
║ en_cours ✓        ║  ║ Looking for...    ║
╚═══════════════════╝  ╚═══════════════════╝

╔═══════════════════╗  ╔═══════════════════╗
║ TERMINAL 3        ║  ║ TERMINAL 4        ║
║ RESTAURANT        ║  ║ LIVREUR           ║
║                   ║  ║                   ║
║ [RESTO] Request   ║  ║ [LIVREUR] Delivery║
║ received for      ║  ║ request received  ║
║ order SIM-...     ║  ║                   ║
║                   ║  ║ [LIVREUR] Delivery║
║ [RESTO] ACCEPTED  ║  ║ ACCEPTED! Going   ║
║ (80% chance)      ║  ║ en_course         ║
║                   ║  ║ (70% chance)      ║
╚═══════════════════╝  ╚═══════════════════╝
```

## 📋 CHECKLIST - Avant de lancer

### Étape 1: Configurer MongoDB (OBLIGATOIRE) ⚠️

**Choix A - MongoDB Atlas (Recommandé pour débutants)**:
```powershell
# 1. Créez un compte: https://www.mongodb.com/cloud/atlas/register
# 2. Créez un cluster gratuit M0
# 3. Obtenez l'URI de connexion
# 4. Modifiez .env:
notepad .env

# Remplacez par:
MONGODB_URI=mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=Ubereats
```

**Choix B - MongoDB Local**:
```powershell
# 1. Installez: https://www.mongodb.com/try/download/community
# 2. Démarrez le service:
net start MongoDB

# Le .env est déjà bon:
MONGODB_URI=mongodb://localhost:27017/
```

➡️ **Voir détails complets**: `SETUP_MONGODB.md`

### Étape 2: Tester la connexion
```powershell
py test_config.py
```

**Attendu**:
```
✅ Connexion MongoDB OK! Version: 7.x.x
✅ Base de données 'Ubereats' trouvée
⚠️  Collections VIDES → Passez à l'étape 3
```

### Étape 3: Peupler la base de données (OBLIGATOIRE)
```powershell
py simulate.py --count 500
```

**Ce que ça fait**:
```
Création de 500 documents...
✅ 100 Clients créés
✅ 20 Restaurants créés
✅ 200 Menus créés
✅ 50 Livreurs créés
✅ 130 Commandes initiales créées
```

### Étape 4: Re-tester la configuration
```powershell
py test_config.py
```

**Attendu**:
```
✅ Client: 100 documents
✅ Restaurants: 20 documents
✅ Menu: 200 documents
✅ Livreur: 50 documents

🎉 TOUT EST PRÊT !
```

### Étape 5: Lancer la simulation ! 🎬
```powershell
cd sim_flow
.\launch_all.bat
```

**Résultat**: 4 terminaux s'ouvrent et affichent le flux en temps réel !

---

## 🔧 Commandes de dépannage

### Vérifier Python
```powershell
py --version          # Doit afficher: Python 3.12.0
py -m pip list        # Liste les packages
```

### Tester manuellement un simulateur
```powershell
# Si les terminaux se ferment immédiatement, testez:
py sim_flow\client_sim.py

# Vous verrez l'erreur exacte
```

### Vérifier MongoDB
```powershell
# Local
Test-NetConnection -ComputerName localhost -Port 27017

# Atlas: testez avec
py -c "from pymongo import MongoClient; from dotenv import load_dotenv; import os; load_dotenv(); client = MongoClient(os.getenv('MONGODB_URI')); print(client.server_info())"
```

### Réinitialiser la base
```powershell
# Si vous voulez repartir de zéro:
py simulate.py --count 500 --reset
```

---

## 🎮 Comment utiliser la simulation

### Démarrage
```powershell
cd sim_flow
.\launch_all.bat
```

### Disposition recommandée
```
┌──────────┬──────────┐
│ Client   │ Platform │
├──────────┼──────────┤
│ Restau   │ Livreur  │
└──────────┴──────────┘
```

### Arrêter
- Appuyez `Ctrl+C` dans chaque terminal
- OU fermez les fenêtres

### Relancer
```powershell
.\launch_all.bat
```

---

## 📊 Personnalisation

### Modifier le taux d'acceptation

**Fichier**: `sim_flow\restaurant_sim.py`
```python
RESTAURANT_ACCEPT_RATE = 0.80  # 80% → Changez à 0.50 pour 50%
```

**Fichier**: `sim_flow\livreur_sim.py`
```python
LIVREUR_ACCEPT_RATE = 0.70  # 70% → Changez à 0.90 pour 90%
```

### Modifier la fréquence des commandes

**Fichier**: `sim_flow\client_sim.py`
```python
time.sleep(3)  # 3 secondes → Changez à 1 pour plus rapide
```

---

## 📚 Fichiers importants

```
C:\Users\PC\mongodb_archiver\
├─ .env                          ← Configuration MongoDB
├─ test_config.py                ← Test de configuration
├─ simulate.py                   ← Peuple la base de données
├─ SETUP_MONGODB.md              ← Guide MongoDB détaillé
├─ TROUBLESHOOTING_PYTHON.md     ← Guide Python
└─ sim_flow\
   ├─ launch_all.bat             ← Lance les 4 terminaux
   ├─ client_sim.py              ← Simule les clients
   ├─ platform_sim.py            ← Orchestre les requêtes
   ├─ restaurant_sim.py          ← Accepte/refuse commandes
   ├─ livreur_sim.py             ← Accepte/refuse livraisons
   ├─ START_HERE.md              ← Guide de démarrage
   ├─ FLOW_DIAGRAM.md            ← Schéma du flux détaillé
   └─ QUICKSTART.md              ← Guide visuel rapide
```

---

## ⚡ Résumé ultra-rapide

```powershell
# 1. Configurez MongoDB (voir SETUP_MONGODB.md)
notepad .env

# 2. Testez
py test_config.py

# 3. Peuplez
py simulate.py --count 500

# 4. Lancez !
cd sim_flow
.\launch_all.bat
```

---

**🎉 Profitez de votre simulation multi-terminaux !**
