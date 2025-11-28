# ✅ SIMULATION MULTI-TERMINAUX - Prête à l'emploi

## 🎯 Nouveauté : Launcher Python

**Vous n'avez plus besoin des scripts .bat !**

Le nouveau launcher Python (`launcher.py`) est :
- ✅ **Plus fiable** - détection automatique de Python
- ✅ **Plus portable** - fonctionne sur Windows/Linux/Mac  
- ✅ **Plus flexible** - options pour tester individuellement
- ✅ **Meilleurs messages d'erreur**

---

## 🚀 Lancement en 1 commande

```powershell
cd C:\Users\PC\mongodb_archiver\sim_flow
py launcher.py
```

**Résultat** : 4 fenêtres CMD s'ouvrent automatiquement ! 🎬

---

## 📋 Checklist avant de lancer

### ☑️ Étape 1 : Configurer MongoDB

```powershell
# Éditez le fichier .env
cd C:\Users\PC\mongodb_archiver
notepad .env
```

Ajoutez votre URI MongoDB :
```bash
# MongoDB Atlas (cloud, gratuit)
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DATABASE=Ubereats

# OU MongoDB local
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=Ubereats
```

➡️ **Guide complet** : `SETUP_MONGODB.md`

---

### ☑️ Étape 2 : Tester la connexion

```powershell
py test_config.py
```

**Attendu** :
```
✅ pymongo installé
✅ python-dotenv installé
✅ Fichier .env trouvé
✅ Connexion MongoDB OK!
```

---

### ☑️ Étape 3 : Peupler la base de données

```powershell
py simulate.py --count 500
```

**Résultat** :
```
✅ 100 Clients créés
✅ 20 Restaurants créés
✅ 200 Menus créés
✅ 50 Livreurs créés
✅ 130 Commandes créées
```

---

### ☑️ Étape 4 : Lancer la simulation !

```powershell
cd sim_flow
py launcher.py
```

**4 terminaux s'ouvrent** :

```
┌─────────────┬─────────────┐
│  CLIENT     │  PLATFORM   │
│  (crée)     │  (orchestre)│
├─────────────┼─────────────┤
│  RESTAURANT │  LIVREUR    │
│  (accepte)  │  (livre)    │
└─────────────┴─────────────┘
```

---

## 🎮 Options avancées

### Tester un seul simulateur

```powershell
# Dans ce terminal (voir les erreurs)
py launcher_advanced.py --inline client

# Dans une nouvelle fenêtre
py launcher_advanced.py --only platform
```

### Lister les simulateurs

```powershell
py launcher_advanced.py --list
```

### Aide

```powershell
py launcher_advanced.py --help
```

---

## 🐛 Dépannage

### Problème : Les terminaux se ferment immédiatement

**Solution** : Testez dans le terminal actuel pour voir l'erreur

```powershell
py launcher_advanced.py --inline client
```

**Erreurs courantes** :

| Erreur | Solution |
|--------|----------|
| `No module named 'pymongo'` | `py -m pip install pymongo python-dotenv` |
| `Connection refused` | Vérifiez `.env` avec votre URI MongoDB |
| `No clients in DB` | Lancez `py simulate.py --count 500` |

---

### Problème : Python non trouvé

```powershell
# Essayez ces commandes
py --version
python --version
python3 --version

# Installez Python si nécessaire
# https://www.python.org/downloads/
```

---

## 📁 Structure des fichiers

```
mongodb_archiver/
├── .env                         ← Configuration MongoDB
├── test_config.py               ← Test de configuration
├── simulate.py                  ← Peuple la base de données
├── README_SIMULATION.md         ← Guide complet
├── SETUP_MONGODB.md             ← Configuration MongoDB
│
└── sim_flow/
    ├── launcher.py              ← 🎯 LANCEUR PRINCIPAL (nouveau!)
    ├── launcher_advanced.py     ← Options avancées
    ├── LAUNCHER_GUIDE.md        ← Guide du launcher
    │
    ├── client_sim.py            ← Simule les clients
    ├── platform_sim.py          ← Orchestre les requêtes
    ├── restaurant_sim.py        ← Accepte/refuse commandes
    ├── livreur_sim.py           ← Accepte/refuse livraisons
    │
    ├── launch_all.bat           ← Ancien launcher (toujours dispo)
    ├── launch_all.ps1           ← Ancien launcher (toujours dispo)
    │
    └── README.md                ← Documentation technique
```

---

## ⚡ Résumé ultra-rapide

```powershell
# 1. Configuration (une seule fois)
notepad .env                      # Ajoutez votre URI MongoDB
py test_config.py                 # Vérifiez la connexion
py simulate.py --count 500        # Peuplez la base

# 2. Lancement (à chaque fois)
cd sim_flow
py launcher.py                    # Lance les 4 terminaux !

# 3. Arrêt
# Appuyez Ctrl+C dans chaque terminal
```

---

## 📚 Documentation complète

| Fichier | Description |
|---------|-------------|
| `README_SIMULATION.md` | Guide complet de la simulation |
| `SETUP_MONGODB.md` | Configuration MongoDB détaillée |
| `LAUNCHER_GUIDE.md` | Guide du launcher Python |
| `sim_flow/README.md` | Documentation technique |
| `sim_flow/FLOW_DIAGRAM.md` | Schéma du flux complet |
| `sim_flow/QUICKSTART.md` | Démarrage rapide visuel |

---

## 🎉 C'est prêt !

**Le launcher Python remplace les scripts .bat** et rend la simulation beaucoup plus facile à utiliser !

```powershell
# Lancez maintenant :
cd C:\Users\PC\mongodb_archiver\sim_flow
py launcher.py
```

**N'oubliez pas** :
1. ✅ Configurez MongoDB dans `.env`
2. ✅ Testez avec `py test_config.py`
3. ✅ Peuplez avec `py simulate.py --count 500`
4. 🚀 Lancez avec `py launcher.py`
