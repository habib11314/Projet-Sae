# 🎨 Architecture visuelle - MongoDB Order Archiver

## 📊 Vue d'ensemble du système

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MONGODB ORDER ARCHIVER v2.0                      │
│                                                                     │
│  🎯 Objectif: Archiver automatiquement les commandes livrées       │
└─────────────────────────────────────────────────────────────────────┘

                          ┌──────────────┐
                          │   MongoDB    │
                          │   Atlas/     │
                          │   Cluster    │
                          └──────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────▼─────┐           ┌──────▼─────┐
              │ Collection│           │ Collection │
              │  Commande │           │ Historique │
              │           │           │            │
              │ status:   │           │ Archived   │
              │ - livrée  │           │ Orders     │
              │ - en_cours│           │            │
              │ - annulée │           │            │
              └─────┬─────┘           └──────▲─────┘
                    │                        │
          ┌─────────┴──────────┐            │
          │                    │            │
    ┌─────▼─────┐      ┌──────▼──────┐    │
    │   Mode    │      │    Mode     │    │
    │   Batch   │      │   Watch     │    │
    │           │      │ (Change     │    │
    │  Periodic │      │  Streams)   │    │
    │  Archive  │      │             │    │
    └─────┬─────┘      └──────┬──────┘    │
          │                   │            │
          └───────────┬───────┘            │
                      │                    │
              ┌───────▼────────┐          │
              │   Enrichment   │──────────┘
              │   Pipeline     │
              │                │
              │ $lookup:       │
              │ - Client       │
              │ - Livreur      │
              │ - Restaurant   │
              │ - Menu         │
              └────────────────┘
```

## 🔄 Flux Mode Batch (Archivage périodique)

```
START
  │
  ├─► [1] Connexion MongoDB
  │         │
  │         └─► ✓ Connected / ✗ Error
  │
  ├─► [2] Créer index si nécessaire
  │         │
  │         └─► Historique.numero_commande (unique)
  │
  ├─► [3] Trouver commandes livrées
  │         │
  │         └─► db.Commande.find({ status: "livrée" })
  │                   │
  │                   ├─► Aucune → FIN
  │                   └─► N commandes trouvées
  │
  ├─► [4] Pour chaque commande (batch par 100)
  │         │
  │         ├─► Enrichir via pipeline aggregation
  │         │     │
  │         │     ├─► $lookup Client
  │         │     ├─► $lookup Livreur
  │         │     ├─► $lookup Restaurant
  │         │     ├─► $lookup Menu
  │         │     └─► $project (normalisation)
  │         │
  │         ├─► Vérifier complétude
  │         │     │
  │         │     ├─► Complete → OK
  │         │     └─► Incomplete → Flag + liste champs manquants
  │         │
  │         └─► Ajouter metadata
  │               │
  │               ├─► date_archivage: now()
  │               ├─► archived_by: "script v2.0"
  │               └─► incomplete: true/false
  │
  ├─► [5] Bulk insert dans Historique
  │         │
  │         ├─► Succès → Stats++
  │         ├─► Duplicate → Skip (stats++)
  │         └─► Erreur → Log + Retry
  │
  ├─► [6] Afficher statistiques
  │         │
  │         └─► Found / Archived / Duplicates / Errors
  │
  └─► FIN
```

## ⚡ Flux Mode Watch (Temps réel avec Change Streams)

```
START
  │
  ├─► [1] Connexion MongoDB
  │
  ├─► [2] Charger resume token (si existe)
  │         │
  │         └─► Resume from last position
  │
  ├─► [3] Ouvrir Change Stream
  │         │
  │         └─► db.Commande.watch(pipeline)
  │               │
  │               └─► Pipeline filter:
  │                     - operationType: insert/update
  │                     - status: "livrée"
  │
  ├─► [4] Boucle infinie (jusqu'à Ctrl+C)
  │     │
  │     └─► Pour chaque event:
  │           │
  │           ├─► [A] Vérifier si archivage nécessaire
  │           │     │
  │           │     ├─► Insert avec status="livrée" → OUI
  │           │     ├─► Update vers status="livrée" → OUI
  │           │     └─► Autre → NON (skip)
  │           │
  │           ├─► [B] Si OUI:
  │           │     │
  │           │     ├─► Enrichir commande
  │           │     │     (même pipeline que batch)
  │           │     │
  │           │     ├─► Archive dans Historique
  │           │     │     │
  │           │     │     ├─► Succès → Log ✓
  │           │     │     ├─► Duplicate → Log ⚠
  │           │     │     └─► Erreur → Log ✗
  │           │     │
  │           │     └─► Sauvegarder resume token
  │           │           (pour reprendre après crash)
  │           │
  │           └─► [C] Continuer écoute...
  │
  └─► FIN (Ctrl+C)
        │
        └─► Sauvegarder dernière position
```

## 🔗 Pipeline d'enrichissement détaillé

```
Input: { numero_commande: "CMD-2025-000001", status: "livrée", ... }
  │
  ├─► Stage 1: $match
  │     └─► Filter par numero_commande
  │
  ├─► Stage 2-5: $lookup (joins)
  │     │
  │     ├─► $lookup Client
  │     │     from: "Client"
  │     │     localField: "id_client"
  │     │     foreignField: "id_client"
  │     │     as: "client" (array)
  │     │
  │     ├─► $lookup Livreur
  │     │     from: "Livreur"
  │     │     localField: "id_livreur"
  │     │     foreignField: "id_livreur"
  │     │     as: "livreur" (array)
  │     │
  │     ├─► $lookup Restaurants
  │     │     from: "Restaurants"
  │     │     localField: "id_restaurant"
  │     │     foreignField: "id_restaurant"
  │     │     as: "restaurant" (array)
  │     │
  │     └─► $lookup Menu
  │           from: "Menu"
  │           localField: "id_menu"
  │           foreignField: "id_menu"
  │           as: "menu" (array)
  │
  ├─► Stage 6: $addFields
  │     └─► Transformer arrays → objects
  │           client: { $arrayElemAt: ["$client", 0] }
  │           (idem pour livreur, restaurant, menu)
  │
  └─► Stage 7: $project
        └─► Normaliser et sélectionner champs
              │
              ├─► nom_client: concat(Prénom + Nom) ou fallback
              ├─► email_client: client.Email
              ├─► nom_livreur: concat(Prénom + Nom)
              ├─► nom_restaurant: restaurant.name
              ├─► nom_menu: menu.name
              ├─► prix_menu: menu.price
              ├─► coût_commande: original
              ├─► date_commande: original
              └─► ... autres champs

Output: {
  numero_commande: "CMD-2025-000001",
  nom_client: "Jean Dupont",
  email_client: "jean@example.com",
  nom_livreur: "Alice Martin",
  nom_restaurant: "Le Bistrot",
  nom_menu: "Menu du jour",
  ...
}
```

## 🏗️ Architecture modulaire du code

```
mongodb_archiver/
│
├─► config.py                 ┌──────────────────────┐
│   └─► Config class          │ Configuration        │
│       ├─► from_env()        │ - MongoDB URI        │
│       ├─► for_simulation()  │ - Collections        │
│       └─► settings          │ - Batch size         │
│                              │ - Retry config       │
│                              └──────────────────────┘
│
├─► logger.py                 ┌──────────────────────┐
│   └─► setup_logger()        │ Logging              │
│       ├─► Console handler   │ - Structured logs    │
│       └─► File handler      │ - Rotation           │
│                              │ - Multiple levels    │
│                              └──────────────────────┘
│
├─► archiver.py               ┌──────────────────────┐
│   └─► OrderArchiver         │ Batch Archiving      │
│       ├─► connect()         │ - Find delivered     │
│       ├─► find_delivered()  │ - Enrich pipeline    │
│       ├─► enrich_order()    │ - Check complete     │
│       ├─► archive_batch()   │ - Bulk insert        │
│       └─► stats             │ - Statistics         │
│                              └──────────────────────┘
│
├─► watcher.py ⭐             ┌──────────────────────┐
│   └─► OrderWatcher          │ Real-time Watch      │
│       ├─► watch()           │ - Change Streams     │
│       ├─► should_archive()  │ - Resume tokens      │
│       ├─► process_change()  │ - Event filtering    │
│       └─► resume mgmt       │ - Fault tolerance    │
│                              └──────────────────────┘
│
├─► generator.py              ┌──────────────────────┐
│   └─► DataGenerator         │ Test Data Gen        │
│       ├─► generate_clients()│ - Faker French       │
│       ├─► generate_menus()  │ - Realistic data     │
│       └─► populate_db()     │ - Seeded random      │
│                              └──────────────────────┘
│
├─► main.py                   ┌──────────────────────┐
│   └─► CLI Interface         │ Main CLI             │
│       ├─► batch command     │ - Batch mode         │
│       ├─► watch command     │ - Watch mode         │
│       └─► argparse          │ - Help & options     │
│                              └──────────────────────┘
│
└─► simulate.py               ┌──────────────────────┐
    └─► CLI Interface         │ Simulation CLI       │
        └─► Generate data     │ - Data generation    │
                              └──────────────────────┘
```

## 🔐 Flux de sécurité

```
Application Start
  │
  ├─► [1] Load .env file
  │         │
  │         └─► MONGODB_URI (never logged)
  │
  ├─► [2] Config.from_env()
  │         │
  │         ├─► Parse URI (secure)
  │         └─► Validate settings
  │
  ├─► [3] Create logger
  │         │
  │         └─► Sanitize logs (no credentials)
  │
  ├─► [4] Connect MongoDB
  │         │
  │         ├─► Use secure connection
  │         └─► Test permissions
  │
  └─► [5] Execute task
            │
            └─► All operations logged securely
```

## 📊 Statistiques et monitoring

```
┌──────────────────────────────────────────────────┐
│              STATISTICS OUTPUT                   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Found:       1,234 orders                       │
│  Archived:    1,220 orders  (98.9%)             │
│  Duplicates:      8 orders  (0.6%)              │
│  Incomplete:     45 orders  (3.6%)              │
│  Errors:          6 orders  (0.5%)              │
│                                                  │
├──────────────────────────────────────────────────┤
│  Duration:    12m 34s                            │
│  Rate:        97 orders/min                      │
└──────────────────────────────────────────────────┘

Logs structure:
┌─────────────────────────────────────────────────┐
│ 2025-10-16 14:23:45 [INFO] Found 1234 orders   │
│ 2025-10-16 14:24:10 [INFO] Archived 100 orders │
│ 2025-10-16 14:24:35 [INFO] Archived 100 orders │
│ 2025-10-16 14:25:00 [INFO] Archived 100 orders │
│ ...                                             │
│ 2025-10-16 14:36:19 [INFO] ✅ Complete!        │
│ 2025-10-16 14:36:19 [INFO] Statistics: ...     │
└─────────────────────────────────────────────────┘
```

## 🎯 Cas d'usage en contexte

### Scénario 1: E-commerce classique
```
User orders food → Status: en_attente
                    ↓
Restaurant accepts → Status: en_preparation
                    ↓
Delivery assigned → Status: en_cours
                    ↓
Delivered! → Status: livrée ⭐
             │
             ├─► Mode Batch: Archived at 2am daily
             │                │
             │                └─► Batch job finds & archives
             │
             └─► Mode Watch: Archived immediately!
                              │
                              └─► Change Stream detects change
                                  Archive in real-time (< 2s)
```

### Scénario 2: Monitoring en production
```
Production Environment
  │
  ├─► Service 1: Watcher (24/7)
  │     │
  │     ├─► Listens to Commande collection
  │     ├─► Archives delivered orders in real-time
  │     └─► Saves resume token every 10s
  │
  ├─► Service 2: Daily Batch (backup, 2am)
  │     │
  │     └─► Archives any missed orders
  │
  └─► Monitoring Dashboard
        │
        ├─► Metrics: orders/hour, errors, lag
        ├─► Alerts: errors > 0, lag > 30s
        └─► Logs: Centralized (ELK/Splunk)
```

## 🚀 Déploiement en production

```
Development                Production
    │                          │
    ├─► Local Testing          ├─► Azure/AWS/GCP
    │   - MongoDB local        │   - MongoDB Atlas
    │   - Simulation mode      │   - Replica Set
    │                          │
    └─► Staging                └─► Deployment Options:
        - Atlas Dev Cluster        │
                                   ├─► Option 1: Windows Service
                                   │   └─► NSSM + watcher
                                   │
                                   ├─► Option 2: Docker Container
                                   │   └─► Kubernetes + replicas
                                   │
                                   └─► Option 3: Serverless
                                       └─► Azure Functions
                                           (batch triggered)
```

## 📈 Performance et scalabilité

```
Small Scale (< 1,000 orders/day)
├─► Single instance watcher
└─► Batch job backup

Medium Scale (1,000 - 10,000 orders/day)
├─► Watcher with resume token
├─► Optimized batch size (500)
└─► Index optimization

Large Scale (> 10,000 orders/day)
├─► Multiple watcher instances (sharding)
├─► Load balancer
├─► Distributed processing
└─► Archive to S3/Blob + cold storage
```

---

**Légende:**
- ⭐ = Fonctionnalité clé
- ✓ = Succès
- ✗ = Erreur
- ⚠ = Warning
- 🔥 = Important
- 📊 = Statistiques
- 🔐 = Sécurité
