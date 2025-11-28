# 🚀 Launcher Python - Simulation Multi-Terminaux

## Pourquoi un launcher Python ?

✅ **Plus portable** que les scripts .bat (fonctionne sur Windows/Linux/Mac)
✅ **Plus fiable** - détecte automatiquement Python
✅ **Plus flexible** - options pour tester individuellement
✅ **Meilleurs messages d'erreur**

## 🎯 Utilisation

### Option 1: Lancer les 4 terminaux (RECOMMANDÉ)

```powershell
cd C:\Users\PC\mongodb_archiver\sim_flow
py launcher.py
```

**Résultat**: 4 fenêtres CMD s'ouvrent avec les 4 simulateurs

---

### Option 2: Utiliser le launcher avancé

#### Lancer les 4 terminaux
```powershell
py launcher_advanced.py
```

#### Lister les simulateurs disponibles
```powershell
py launcher_advanced.py --list
```

**Sortie**:
```
Simulateurs disponibles:
  • client       → client_sim.py        (CLIENT SIMULATOR)
  • platform     → platform_sim.py      (PLATFORM SIMULATOR)
  • restaurant   → restaurant_sim.py    (RESTAURANT SIMULATOR)
  • livreur      → livreur_sim.py       (LIVREUR SIMULATOR)
```

#### Tester un seul simulateur (nouvelle fenêtre)
```powershell
py launcher_advanced.py --only client
py launcher_advanced.py --only platform
py launcher_advanced.py --only restaurant
py launcher_advanced.py --only livreur
```

**Utilité**: Débugger un simulateur spécifique

#### Lancer dans le terminal actuel (mode inline)
```powershell
py launcher_advanced.py --inline client
```

**Utilité**: Voir les erreurs directement sans ouvrir une nouvelle fenêtre

---

## 📋 Avant de lancer

### 1. Configurer MongoDB

```powershell
# Éditez le fichier .env
notepad .env

# Ajoutez votre URI MongoDB:
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DATABASE=Ubereats
```

### 2. Tester la configuration

```powershell
cd ..
py test_config.py
```

### 3. Peupler la base de données

```powershell
py simulate.py --count 500
```

---

## 🎬 Exemple complet

```powershell
# Aller dans le dossier
cd C:\Users\PC\mongodb_archiver

# Tester la config
py test_config.py

# Si la base est vide, peupler
py simulate.py --count 500

# Lancer la simulation !
cd sim_flow
py launcher.py
```

**Attendu**: 4 fenêtres CMD s'ouvrent et affichent le flux en temps réel

---

## 🐛 Dépannage

### Les terminaux se ferment immédiatement

**Test 1**: Lancez dans le terminal actuel pour voir l'erreur
```powershell
py launcher_advanced.py --inline client
```

**Erreurs courantes**:

#### "No module named 'pymongo'"
```powershell
py -m pip install pymongo python-dotenv
```

#### "Connection refused"
- Vérifiez `.env` avec votre URI MongoDB
- Testez: `py ../test_config.py`

#### "No clients in DB"
- Base de données vide
- Lancez: `py ../simulate.py --count 500`

---

### Tester un seul simulateur

```powershell
# Test client
py launcher_advanced.py --inline client

# Test platform
py launcher_advanced.py --inline platform

# Test restaurant
py launcher_advanced.py --inline restaurant

# Test livreur
py launcher_advanced.py --inline livreur
```

---

## 📊 Ce que vous verrez

Quand tout fonctionne, les 4 terminaux affichent :

### Terminal 1 - CLIENT
```
===== CLIENT SIMULATOR =====

Client simulator started. Press Ctrl+C to stop.
[CLIENT] Creating order SIM-1729089234-5678
[CLIENT] Order created: SIM-1729089234-5678
[CLIENT] Status: pending_request
...
[CLIENT] Status changed: pending_request -> en_cours
[CLIENT] Final status: en_cours
```

### Terminal 2 - PLATFORM
```
===== PLATFORM SIMULATOR =====

Platform simulator started. Press Ctrl+C to stop.
[PLATFORM] Detected pending order: SIM-1729089234-5678
[PLATFORM] Requesting restaurant RES-00001...
[PLATFORM] Restaurant accepted!
[PLATFORM] Looking for available livreur...
[PLATFORM] Found livreur: LIV-00012
[PLATFORM] Delivery accepted! Order assigned.
```

### Terminal 3 - RESTAURANT
```
===== RESTAURANT SIMULATOR =====

Restaurant simulator started. Press Ctrl+C to stop.
[RESTAURANT] New request: SIM-1729089234-5678 for RES-00001
[RESTAURANT] Decision: ACCEPTED (80% chance)
```

### Terminal 4 - LIVREUR
```
===== LIVREUR SIMULATOR =====

Livreur simulator started. Press Ctrl+C to stop.
[LIVREUR] New delivery request for LIV-00012
[LIVREUR] Order: SIM-1729089234-5678
[LIVREUR] Decision: ACCEPTED (70% chance)
[LIVREUR] Status changed to en_course
```

---

## 🎮 Arrêter la simulation

- **Appuyez `Ctrl+C`** dans chaque terminal
- **OU** fermez les fenêtres

---

## 📁 Fichiers

```
sim_flow/
├── launcher.py              ← Launcher simple (RECOMMANDÉ)
├── launcher_advanced.py     ← Launcher avec options CLI
├── client_sim.py            ← Simule les clients
├── platform_sim.py          ← Orchestre les requêtes
├── restaurant_sim.py        ← Accepte/refuse commandes
├── livreur_sim.py           ← Accepte/refuse livraisons
├── README.md                ← Documentation principale
├── LAUNCHER_GUIDE.md        ← Ce fichier
└── FLOW_DIAGRAM.md          ← Schéma du flux
```

---

## ⚡ Commandes rapides

```powershell
# Lancer tout
py launcher.py

# Tester un seul dans terminal actuel (voir erreurs)
py launcher_advanced.py --inline client

# Lancer un seul dans nouvelle fenêtre
py launcher_advanced.py --only platform

# Liste les options
py launcher_advanced.py --help
```

---

**🎉 Le launcher Python remplace complètement le fichier .bat !**
