# 📊 Plan de Monitoring - MongoDB Order Archiver

## 🎯 Objectifs du monitoring

1. Assurer que toutes les commandes livrées sont archivées
2. Détecter les anomalies et erreurs rapidement
3. Optimiser les performances
4. Garantir la disponibilité du système

## 📈 Métriques clés

### 1. Métriques d'archivage

#### Mode Batch
| Métrique | Description | Seuil d'alerte | Action |
|----------|-------------|----------------|--------|
| `orders_found` | Nombre de commandes trouvées | - | Tendance |
| `orders_archived` | Commandes archivées avec succès | < 95% de found | Investigation |
| `orders_duplicates` | Doublons détectés | > 10% | Vérifier logique |
| `orders_incomplete` | Données incomplètes | > 5% | Vérifier intégrité DB |
| `orders_errors` | Erreurs d'archivage | > 0 | Alert immédiate |
| `batch_duration` | Temps d'exécution total | > 30 min | Optimisation |

#### Mode Watch (Change Streams)
| Métrique | Description | Seuil d'alerte | Action |
|----------|-------------|----------------|--------|
| `events_processed` | Événements traités | - | Tendance |
| `events_archived` | Archivages réussis | - | Compteur |
| `stream_lag` | Délai de traitement | > 10s | Investigation |
| `connection_errors` | Erreurs de connexion | > 3/heure | Alert |
| `resume_token_age` | Âge du dernier token | > 1h | Vérifier activité |
| `uptime` | Temps d'activité continu | - | Monitoring |

### 2. Métriques MongoDB

```javascript
// Performance des requêtes
db.Commande.find({ status: "livrée" }).explain("executionStats")

// Index utilization
db.Historique.aggregate([
  { $indexStats: {} }
])

// Collection stats
db.Historique.stats()

// Change Stream cursors actifs
db.currentOp({ "command.aggregate": "Commande" })
```

### 3. Métriques système

- **CPU** : Usage du processus Python
- **Mémoire** : Consommation RAM (attention aux batch trop grands)
- **Réseau** : Latence vers MongoDB
- **Disque** : Espace logs

## 📝 Logs structurés

### Format des logs

```
2025-10-16 12:34:56 [INFO] [batch_archiver] 📦 Found 150 delivered orders
2025-10-16 12:35:10 [INFO] [batch_archiver] ✅ Archived 150 orders
2025-10-16 12:35:10 [INFO] [batch_archiver] 📊 Progress: 150/150 processed
```

### Niveaux de log

| Niveau | Usage | Destination |
|--------|-------|-------------|
| DEBUG | Détails techniques | Fichier uniquement |
| INFO | Opérations normales | Console + Fichier |
| WARNING | Situations anormales | Console + Fichier + Alert |
| ERROR | Erreurs critiques | Console + Fichier + Alert immédiate |

### Patterns à monitorer

#### Succès
```
✅ Archived \d+ orders
✅ Change Stream opened successfully
✅ Connected to database
```

#### Warnings
```
⚠️  Order .+ is incomplete
⚠️  Order .+ already archived
⚠️  Could not load resume token
```

#### Erreurs
```
❌ Failed to connect to MongoDB
❌ Error enriching order
❌ Change Stream error
```

## 🚨 Alertes recommandées

### Alertes critiques (P1)

1. **Service down**
   ```
   Condition: Processus watch arrêté > 5 min
   Action: Redémarrage automatique + notification
   ```

2. **Erreurs d'archivage**
   ```
   Condition: errors > 0 sur dernière exécution batch
   Action: Notification équipe + log détaillé
   ```

3. **Connexion MongoDB perdue**
   ```
   Condition: Connection errors > 3 en 10 min
   Action: Vérifier réseau + credentials + status MongoDB
   ```

### Alertes importantes (P2)

4. **Données incomplètes élevées**
   ```
   Condition: incomplete > 10% sur dernière heure
   Action: Vérifier intégrité des collections liées
   ```

5. **Change Stream lag**
   ```
   Condition: Délai traitement > 30s
   Action: Vérifier charge MongoDB + réseau
   ```

6. **Espace disque logs**
   ```
   Condition: logs/ > 1 GB
   Action: Rotation/nettoyage automatique
   ```

### Alertes informatives (P3)

7. **Batch duration élevée**
   ```
   Condition: Durée > 2x baseline
   Action: Monitoring proactif
   ```

8. **Taux de doublons**
   ```
   Condition: duplicates > 20%
   Action: Investigation logique métier
   ```

## 📊 Dashboard recommandé

### Vue en temps réel (Watch mode)

```
┌─────────────────────────────────────────────────────┐
│  🔴 MongoDB Order Archiver - LIVE                   │
├─────────────────────────────────────────────────────┤
│  Uptime: 12h 34m                                    │
│  Status: ✅ Running                                 │
│  Last event: 12:45:23                               │
├─────────────────────────────────────────────────────┤
│  📊 Today's Statistics                              │
│    Archived: 2,345 orders                           │
│    Duplicates: 12 (0.5%)                            │
│    Incomplete: 45 (1.9%)                            │
│    Errors: 0                                        │
├─────────────────────────────────────────────────────┤
│  ⚡ Performance                                      │
│    Avg processing time: 0.8s                        │
│    Stream lag: 2.3s                                 │
│    CPU: 12% | RAM: 245 MB                           │
└─────────────────────────────────────────────────────┘
```

### Vue historique (Batch mode)

```
┌─────────────────────────────────────────────────────┐
│  📦 Batch Archiving - Last 7 days                   │
├─────────────────────────────────────────────────────┤
│  Mon: ████████████████████ 1,234 orders            │
│  Tue: ███████████████████  1,156 orders            │
│  Wed: █████████████████████ 1,389 orders           │
│  Thu: ██████████████████   1,098 orders            │
│  Fri: ████████████████████ 1,245 orders            │
│  Sat: ██████████          567 orders               │
│  Sun: █████████           456 orders               │
├─────────────────────────────────────────────────────┤
│  Success rate: 99.8%                                │
│  Avg duration: 12m 34s                              │
└─────────────────────────────────────────────────────┘
```

## 🛠️ Outils de monitoring

### 1. MongoDB Atlas (si utilisé)

- **Alerts** : Configurer dans Atlas UI
- **Charts** : Visualiser les données archivées
- **Performance Advisor** : Suggestions d'index
- **Real-time Performance Panel**

### 2. Prometheus + Grafana (recommandé pour production)

Exposer les métriques via endpoint :

```python
# metrics_exporter.py (à ajouter si besoin)
from prometheus_client import Counter, Gauge, Histogram

orders_archived = Counter('orders_archived_total', 'Total orders archived')
orders_errors = Counter('orders_errors_total', 'Total archiving errors')
processing_time = Histogram('order_processing_seconds', 'Time to process order')
stream_lag = Gauge('change_stream_lag_seconds', 'Change stream lag')
```

### 3. ELK Stack (Elasticsearch, Logstash, Kibana)

Configuration Filebeat pour logs :

```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - C:/Users/PC/mongodb_archiver/logs/*.log
  fields:
    service: mongodb-archiver
    environment: production

output.elasticsearch:
  hosts: ["localhost:9200"]
```

### 4. Simple monitoring script

```powershell
# monitor.ps1
$logFile = "logs\watcher_latest.log"
$errors = Select-String -Path $logFile -Pattern "ERROR" | Measure-Object
$warnings = Select-String -Path $logFile -Pattern "WARNING" | Measure-Object

if ($errors.Count -gt 0) {
    Write-Host "⚠️  $($errors.Count) errors found!"
    # Send notification
}

Write-Host "✅ Monitoring check complete"
```

## 📋 Checklist de santé quotidienne

- [ ] Service watch actif et uptime > 23h
- [ ] Aucune erreur dans les logs des dernières 24h
- [ ] Taux d'archivage > 99%
- [ ] Lag Change Stream < 10s
- [ ] Espace disque suffisant (> 20% libre)
- [ ] Resume token sauvegardé dans les 10 dernières minutes
- [ ] Nombre de commandes archivées cohérent avec le trafic

## 🔄 Maintenance

### Quotidien
- Vérifier les logs d'erreurs
- Monitorer les alertes

### Hebdomadaire
- Review du taux de complétude des données
- Analyse des duplicates
- Vérification de la performance des index

### Mensuel
- Rotation des logs (> 30 jours)
- Audit des permissions MongoDB
- Review des métriques de performance
- Test de recovery (kill + restart)

### Trimestriel
- Mise à jour des dépendances Python
- Review de la stratégie d'archivage
- Test de disaster recovery complet
- Optimisation des requêtes si besoin

## 📞 Escalade

| Niveau | Délai | Contact |
|--------|-------|---------|
| P1 - Critique | 15 min | On-call engineer + Team lead |
| P2 - Important | 2 heures | Data team |
| P3 - Info | Jour ouvrable | Developer |

## 📚 Ressources

- [MongoDB Change Streams Docs](https://docs.mongodb.com/manual/changeStreams/)
- [MongoDB Performance Best Practices](https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/)
- [Python Logging](https://docs.python.org/3/library/logging.html)

---

**Note** : Adapter ce plan selon votre infrastructure et vos outils de monitoring existants.
