# 🚀 Quick Start Guide - MongoDB Order Archiver

## Installation rapide (5 minutes)

### 1. Prérequis
```powershell
# Vérifier Python version
python --version  # Doit être >= 3.8

# Vérifier pip
pip --version
```

### 2. Installation
```powershell
# Aller dans le dossier
cd C:\Users\PC\mongodb_archiver

# Créer environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer dépendances
pip install -r requirements.txt
```

### 3. Configuration
```powershell
# Copier l'exemple de config
copy .env.example .env

# Éditer .env et ajouter votre URI MongoDB
notepad .env
```

Dans `.env`, remplacer :
```env
MONGODB_URI=mongodb+srv://VOTRE_USERNAME:VOTRE_PASSWORD@votre-cluster.mongodb.net/
```

### 4. Premier test
```powershell
# Test avec simulation (MongoDB local)
python main.py batch --simulation --dry-run
```

Si vous voyez ✅ sans erreur, c'est bon !

## 📖 Scénarios d'usage courants

### Scénario 1: Archivage quotidien automatisé

**Objectif**: Archiver toutes les commandes livrées chaque jour à 2h du matin

**Solution**: Tâche planifiée Windows

```powershell
# Créer le script
@echo off
cd C:\Users\PC\mongodb_archiver
call venv\Scripts\activate.bat
python main.py batch --run
```

Sauver comme `archive_daily.bat`, puis :
1. Ouvrir "Planificateur de tâches"
2. Créer une tâche de base
3. Déclencheur : Quotidien à 2:00
4. Action : Démarrer `archive_daily.bat`

### Scénario 2: Monitoring en temps réel

**Objectif**: Archiver automatiquement dès qu'une commande est livrée

**Solution**: Mode Watch avec Change Streams

```powershell
# Démarrer le watcher (tourne en continu)
python main.py watch
```

Pour le faire tourner en arrière-plan comme service, utiliser NSSM:
```powershell
# Installer NSSM (Non-Sucking Service Manager)
# Télécharger depuis https://nssm.cc/

nssm install MongoDBArchiver
# Path: C:\Users\PC\mongodb_archiver\venv\Scripts\python.exe
# Arguments: main.py watch
# Startup directory: C:\Users\PC\mongodb_archiver
```

### Scénario 3: Test avec données simulées

**Objectif**: Tester le système avant de l'utiliser en production

**Solution**: Génération de données + archivage local

```powershell
# 1. Générer 1000 commandes de test
python simulate.py --simulation --count 1000 --seed 42 --p-delivered 0.4

# 2. Archiver en dry-run
python main.py batch --simulation --dry-run

# 3. Archiver réellement (base locale uniquement)
python main.py batch --simulation --run

# 4. Vérifier
python main.py batch --simulation --run --export-sample samples.json
notepad samples.json
```

### Scénario 4: Archivage d'une période spécifique

**Objectif**: Archiver les commandes d'un mois spécifique

**Solution**: Filtres de date

```powershell
# Archiver Janvier 2025
python main.py batch --run --date-from 2025-01-01 --date-to 2025-01-31

# Avec export d'échantillons
python main.py batch --run --date-from 2025-01-01 --date-to 2025-01-31 --export-sample janvier_2025.json
```

### Scénario 5: Migration complète historique

**Objectif**: Archiver toutes les anciennes commandes livrées

**Solution**: Batch sans filtre de date

```powershell
# Dry-run pour voir ce qui sera archivé
python main.py batch --dry-run --verbose

# Archivage réel avec logs détaillés
python main.py batch --run --verbose --batch-size 500

# Vérifier dans les logs
ls logs\
notepad logs\batch_<timestamp>.log
```

## 🔧 Dépannage rapide

### Problème: "MONGODB_URI environment variable is required"
**Solution**: 
```powershell
# Vérifier que le fichier .env existe
ls .env

# Vérifier le contenu
type .env

# Si absent, créer à partir de l'exemple
copy .env.example .env
notepad .env
```

### Problème: "Change Streams require a replica set"
**Solution**: 
- MongoDB standalone ne supporte PAS Change Streams
- Utiliser MongoDB Atlas (support natif)
- OU configurer un replica set local :
  ```powershell
  mongod --replSet rs0
  mongo
  > rs.initiate()
  ```

### Problème: Import errors / module not found
**Solution**:
```powershell
# Vérifier que venv est activé
# Le prompt doit afficher (venv)

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Problème: Connexion timeout / Network error
**Solution**:
```powershell
# Vérifier la connexion
ping votre-cluster.mongodb.net

# Vérifier l'URI (sans espaces, guillemets)
# Dans MongoDB Atlas:
# 1. Aller dans "Database Access"
# 2. Vérifier le mot de passe
# 3. Aller dans "Network Access"
# 4. Ajouter votre IP publique ou 0.0.0.0/0 (dev uniquement)
```

### Problème: "Permission denied" sur MongoDB
**Solution**:
```javascript
// Dans MongoDB, créer un utilisateur avec bonnes permissions
use admin
db.createUser({
  user: "archiver_user",
  pwd: "secure_password",
  roles: [
    { role: "read", db: "Ubereats" },
    { role: "readWrite", db: "Ubereats", collection: "Historique" }
  ]
})
```

## 📊 Commandes utiles

### Vérifier l'état de la base
```powershell
# Dans mongo shell / Atlas Data Explorer
use Ubereats

# Compter les commandes livrées
db.Commande.countDocuments({ status: "livrée" })

# Compter les commandes archivées
db.Historique.countDocuments({})

# Dernière commande archivée
db.Historique.findOne({}, { sort: { date_archivage: -1 } })

# Statistiques par jour
db.Historique.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$date_archivage" } },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: -1 } },
  { $limit: 7 }
])
```

### Monitoring du watcher
```powershell
# Voir les logs en temps réel (Windows)
Get-Content logs\watcher_*.log -Wait -Tail 50

# Vérifier le resume token
type .resume_token.json

# Stats rapides
findstr /C:"archived" logs\watcher_*.log
```

### Tests
```powershell
# Lancer tous les tests
pytest -v

# Avec couverture
pytest --cov=. --cov-report=html
start htmlcov\index.html

# Test spécifique
pytest test_archiver.py::TestOrderArchiver::test_check_completeness_complete -v
```

## 🎓 Tutoriel pas-à-pas complet

### Étape 1: Installation (déjà fait ↑)

### Étape 2: Créer des données de test
```powershell
python simulate.py --simulation --count 500 --seed 123
```

### Étape 3: Voir ce qui serait archivé
```powershell
python main.py batch --simulation --dry-run
```

### Étape 4: Archiver (local)
```powershell
python main.py batch --simulation --run
```

### Étape 5: Vérifier le résultat
```powershell
python main.py batch --simulation --run --export-sample test_samples.json
notepad test_samples.json
```

### Étape 6: Tester le watch mode
```powershell
# Terminal 1: Démarrer le watcher
python main.py watch --simulation --simple

# Terminal 2: Modifier une commande
mongo
> use Ubereats_Test
> db.Commande.updateOne(
    { status: "en_cours" },
    { $set: { status: "livrée" } }
  )

# Terminal 1 devrait afficher l'archivage automatique !
```

### Étape 7: Passer en production
```powershell
# 1. Configurer .env avec vraie URI
notepad .env

# 2. Dry-run en production
python main.py batch --dry-run

# 3. Archiver pour de vrai
python main.py batch --run

# 4. Mettre en place le watcher ou la tâche planifiée
python main.py watch
```

## 📞 Support

- 📖 Documentation complète : `README.md`
- 📊 Plan de monitoring : `MONITORING.md`
- 🎯 Démos interactives : `python demo.py`
- 🧪 Tests : `pytest -v`

## ✅ Checklist de déploiement

- [ ] Python 3.8+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` configuré avec URI MongoDB valide
- [ ] URI MongoDB testée (connexion OK)
- [ ] Permissions MongoDB vérifiées
- [ ] Test dry-run réussi
- [ ] Test archivage réel sur données de test
- [ ] Logs vérifiés (pas d'erreurs)
- [ ] Index MongoDB créés
- [ ] Monitoring configuré (optionnel mais recommandé)
- [ ] Tâche planifiée OU service watcher configuré
- [ ] Documentation lue et comprise

---

🎉 **Félicitations !** Vous êtes prêt à utiliser MongoDB Order Archiver !
