# 📦 MongoDB Order Archiver

Système professionnel d'archivage automatique des commandes MongoDB avec support de **Change Streams** pour le monitoring en temps réel.

## 🌟 Fonctionnalités

### Mode Batch
- ✅ Archivage par lots avec enrichissement des données (joins via `$lookup`)
- ✅ Détection automatique des doublons
- ✅ Gestion des erreurs avec retry automatique
- ✅ Filtres par date (plage de dates)
- ✅ Mode dry-run pour simuler sans modifier la base
- ✅ Export d'échantillons en JSON
- ✅ Logging structuré (console + fichier)
- ✅ Statistiques détaillées

### Mode Watch (Change Streams) 🔥
- ✅ **Archivage en temps réel** dès qu'une commande passe au statut "livrée"
- ✅ Utilisation des **MongoDB Change Streams** pour détecter les modifications
- ✅ **Resume tokens** pour reprendre après interruption (fault tolerance)
- ✅ Filtrage intelligent des événements
- ✅ Mode simple pour le debugging

### Génération de données de test
- ✅ Création de données réalistes (clients, livreurs, restaurants, menus, commandes)
- ✅ Seed pour reproductibilité
- ✅ Proportions configurables (% de commandes livrées, % de données manquantes)
- ✅ Support de Faker pour données françaises

### Sécurité & Best Practices
- ✅ Credentials via variables d'environnement (jamais en dur)
- ✅ Logs sécurisés (pas d'URI en clair)
- ✅ Index MongoDB automatiques
- ✅ Validation de complétude des données
- ✅ Tests unitaires inclus

## 📋 Prérequis

- Python 3.8+
- MongoDB 4.0+ (avec support des Change Streams pour le mode watch)
- Replica Set configuré (requis pour Change Streams)

## 🚀 Installation

### 1. Cloner/Créer le projet

```powershell
cd C:\Users\PC\mongodb_archiver
```

### 2. Créer un environnement virtuel

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 4. Configuration

Créer un fichier `.env` à partir de l'exemple :

```powershell
copy .env.example .env
```

Éditer `.env` et ajouter votre URI MongoDB :

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=Ubereats
BATCH_SIZE=100
```

**⚠️ IMPORTANT : Ne JAMAIS commiter le fichier `.env` !**

## 📖 Utilisation

### Mode Batch - Archivage de toutes les commandes livrées

#### Archivage réel
```powershell
python main.py batch --run
```

#### Dry-run (simulation)
```powershell
python main.py batch --dry-run
```

#### Avec filtre de dates
```powershell
python main.py batch --run --date-from 2025-01-01 --date-to 2025-01-31
```

#### Export d'échantillons
```powershell
python main.py batch --run --export-sample samples.json --sample-count 10
```

#### Mode verbeux avec logs détaillés
```powershell
python main.py batch --run --verbose
```

### Mode Watch - Archivage en temps réel 🔥

#### Démarrer le watcher
```powershell
python main.py watch
```

Le watcher :
- Détecte automatiquement quand une commande passe au statut "livrée"
- Archive immédiatement la commande
- Sauvegarde sa position (resume token) pour reprendre après interruption
- Tourne en continu jusqu'à Ctrl+C

#### Mode simple (sans resume token, pour debug)
```powershell
python main.py watch --simple
```

#### Démarrer sans reprendre de la dernière position
```powershell
python main.py watch --no-resume
```

### Génération de données de test

#### Générer 1000 commandes avec paramètres par défaut
```powershell
python simulate.py --count 1000
```

#### Avec seed pour reproductibilité
```powershell
python simulate.py --count 500 --seed 42
```

#### 50% de commandes livrées
```powershell
python simulate.py --count 1000 --p-delivered 0.5
```

#### Effacer et regénérer
```powershell
python simulate.py --count 2000 --clear
```

#### Personnaliser les quantités
```powershell
python simulate.py --count 1000 --clients 200 --livreurs 100 --restaurants 50 --menus 300
```

### Tests unitaires

```powershell
pytest -v
```

Avec couverture :
```powershell
pytest --cov=. --cov-report=html
```

### Mode simulation (MongoDB local)

Pour tester sans toucher à la production :

```powershell
python main.py batch --simulation --run
python main.py watch --simulation
python simulate.py --simulation --count 100
```

## 📊 Structure du projet

```
mongodb_archiver/
├── main.py                 # CLI principal (batch & watch)
├── simulate.py             # Générateur de données
├── archiver.py             # Logique d'archivage
├── watcher.py              # Change Streams watcher 🔥
├── generator.py            # Génération de données test
├── config.py               # Configuration
├── logger.py               # Système de logs
├── test_archiver.py        # Tests unitaires
├── requirements.txt        # Dépendances Python
├── .env.example            # Exemple de configuration
├── .gitignore              # Fichiers à ignorer
└── README.md               # Cette documentation
```

## 🔧 Configuration avancée

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `MONGODB_URI` | URI de connexion MongoDB | **Requis** |
| `MONGODB_DATABASE` | Nom de la base de données | `Ubereats` |
| `BATCH_SIZE` | Taille des lots d'archivage | `100` |
| `MAX_RETRIES` | Nombre de tentatives en cas d'erreur | `3` |
| `RETRY_DELAY` | Délai entre tentatives (secondes) | `2` |
| `WATCH_ENABLED` | Activer le mode watch | `true` |

### Index MongoDB recommandés

Le script crée automatiquement ces index :

```javascript
// Collection Historique
db.Historique.createIndex({ "numero_commande": 1 }, { unique: true })

// Collection Commande
db.Commande.createIndex({ "status": 1 })
db.Commande.createIndex({ "date_commande": 1 })
```

## 🎯 Exemple de commande archivée

```json
{
  "numero_commande": "CMD-2025-0001",
  "id_commande": "6718abc123def456...",
  "nom_client": "Jean Dupont",
  "email_client": "jean.dupont@example.com",
  "telephone_client": "+33 6 12 34 56 78",
  "nom_livreur": "Alice Martin",
  "nom_restaurant": "Le Bistrot",
  "adresse_restaurant": "12 rue de Paris, 75001",
  "nom_menu": "Formule Midi",
  "prix_menu": 12.5,
  "adresse_livraison": "45 avenue Victor Hugo, 75116 Paris",
  "coût_commande": 15.5,
  "rémunération_livreur": 3.0,
  "moyen_de_payement": "CB",
  "status": "livrée",
  "date_commande": "2025-10-16T12:02:30Z",
  "temps_estimee": 30,
  "date_archivage": "2025-10-16T12:15:01Z",
  "archived_by": "archive_commandes.py v2.0.0",
  "incomplete": false
}
```

## 📈 Monitoring & Production

### Métriques à surveiller

1. **Nombre d'archivages/jour** : Vérifier que toutes les commandes livrées sont archivées
2. **Erreurs** : Alert si `stats['errors'] > threshold`
3. **Commandes incomplètes** : `stats['incomplete']` (données manquantes)
4. **Latence DB** : Temps de réponse MongoDB
5. **Change Stream lag** : En mode watch, vérifier le délai de traitement

### Logs

Les logs sont écrits dans `logs/` avec horodatage :
- `batch_YYYYMMDD_HHMMSS.log`
- `watcher_YYYYMMDD_HHMMSS.log`
- `generator_YYYYMMDD_HHMMSS.log`

### Sécurité production

1. **Credentials** : Utiliser un gestionnaire de secrets (Azure Key Vault, AWS Secrets Manager)
2. **Permissions MongoDB** : Compte avec permissions minimales
   ```javascript
   // Permissions recommandées
   {
     "Commande": ["find"],
     "Client": ["find"],
     "Livreur": ["find"],
     "Restaurants": ["find"],
     "Menu": ["find"],
     "Historique": ["insert", "find"]
   }
   ```
3. **Network** : Firewall MongoDB avec whitelist IP
4. **Change Streams** : Requiert un **Replica Set** (pas disponible sur standalone)

### Déploiement

#### Docker (recommandé)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mode watch par défaut
CMD ["python", "main.py", "watch"]
```

#### Systemd (Linux)

```ini
[Unit]
Description=MongoDB Order Archiver Watcher
After=network.target

[Service]
Type=simple
User=mongodb-archiver
WorkingDirectory=/opt/mongodb-archiver
Environment="MONGODB_URI=mongodb+srv://..."
ExecStart=/opt/mongodb-archiver/venv/bin/python main.py watch
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Windows Task Scheduler

Créer une tâche planifiée pour le mode batch :
```powershell
python C:\mongodb_archiver\main.py batch --run
```
Déclencher : Quotidiennement à 2h du matin

Pour le mode watch, utiliser un service Windows (NSSM recommandé).

## 🧪 Tests

### Tester localement avec MongoDB local

1. Installer MongoDB Community Edition
2. Démarrer avec replica set :
   ```powershell
   mongod --replSet rs0
   ```
3. Initialiser le replica set :
   ```javascript
   rs.initiate()
   ```
4. Lancer les tests :
   ```powershell
   python simulate.py --simulation --count 100
   python main.py batch --simulation --run
   python main.py watch --simulation
   ```

## 🤝 Contribution

Pour contribuer :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est fourni à titre d'exemple éducatif.

## ⚠️ Sécurité

**NE JAMAIS** :
- Commiter le fichier `.env`
- Partager les credentials MongoDB
- Logger l'URI de connexion
- Utiliser des credentials en dur dans le code

## 🆘 Dépannage

### "MONGODB_URI environment variable is required"
→ Créer un fichier `.env` avec votre URI

### "Change Streams require a replica set"
→ MongoDB standalone ne supporte pas Change Streams. Utiliser Atlas ou configurer un replica set local

### Import errors
→ Vérifier que vous êtes dans le bon répertoire et que le venv est activé

### Connection timeout
→ Vérifier la whitelist IP dans MongoDB Atlas

## 📞 Support

Pour questions ou problèmes : ouvrir une issue GitHub

---

Créé avec ❤️ pour automatiser l'archivage MongoDB avec Change Streams
