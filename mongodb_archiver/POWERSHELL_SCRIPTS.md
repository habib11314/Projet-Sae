# 🛠️ Scripts PowerShell utiles - MongoDB Order Archiver

## 📦 Installation et configuration

### Setup initial complet
```powershell
# Créer et activer environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer dépendances
pip install -r requirements.txt

# Créer fichier de configuration
Copy-Item .env.example .env
notepad .env

# Vérifier installation
python -c "import pymongo; print('PyMongo OK')"
python -c "import faker; print('Faker OK')"
python -c "from dotenv import load_dotenv; print('python-dotenv OK')"
```

### Mise à jour des dépendances
```powershell
# Mettre à jour toutes les dépendances
pip install --upgrade -r requirements.txt

# Voir les dépendances obsolètes
pip list --outdated
```

## 🏃 Lancement rapide

### Mode batch
```powershell
# Dry-run rapide
python main.py batch --dry-run

# Archivage réel
python main.py batch --run

# Avec logs détaillés
python main.py batch --run --verbose

# Période spécifique
python main.py batch --run --date-from 2025-01-01 --date-to 2025-01-31
```

### Mode watch
```powershell
# Démarrer le watcher
python main.py watch

# Mode simple (debug)
python main.py watch --simple

# Sans reprendre de la position sauvegardée
python main.py watch --no-resume
```

### Génération de données
```powershell
# Générer 1000 commandes
python simulate.py --count 1000

# Avec seed pour reproductibilité
python simulate.py --count 500 --seed 42

# Effacer et regénérer
python simulate.py --count 2000 --clear --p-delivered 0.5
```

## 🔍 Monitoring et debugging

### Voir les logs en temps réel
```powershell
# Dernières 50 lignes et suivre
Get-Content logs\watcher_*.log -Wait -Tail 50

# Filtrer uniquement les erreurs
Get-Content logs\*.log | Select-String "ERROR"

# Compter les erreurs
(Get-Content logs\*.log | Select-String "ERROR").Count

# Voir les archives réussies
Get-Content logs\*.log | Select-String "archived"
```

### Statistiques des logs
```powershell
# Fonction helper pour analyser les logs
function Get-ArchiverStats {
    $logs = Get-ChildItem logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    $archived = (Select-String -Path $logs -Pattern "Archived: (\d+)" -AllMatches).Matches.Groups[1].Value
    $errors = (Select-String -Path $logs -Pattern "Errors: (\d+)" -AllMatches).Matches.Groups[1].Value
    
    Write-Host "📊 Last run statistics:"
    Write-Host "  Archived: $archived"
    Write-Host "  Errors: $errors"
}

# Utiliser
Get-ArchiverStats
```

### Vérifier l'état du watcher
```powershell
# Vérifier si le processus tourne
Get-Process python | Where-Object {$_.CommandLine -like "*watch*"}

# Vérifier l'âge du resume token
$token = Get-Content .resume_token.json -ErrorAction SilentlyContinue
if ($token) {
    $file = Get-Item .resume_token.json
    $age = (Get-Date) - $file.LastWriteTime
    Write-Host "Resume token age: $($age.TotalMinutes) minutes"
}
```

## 🧪 Tests

### Lancer les tests
```powershell
# Tous les tests
pytest -v

# Tests avec couverture
pytest --cov=. --cov-report=html
Start-Process htmlcov\index.html

# Test spécifique
pytest test_archiver.py::TestOrderArchiver -v

# Tests en parallèle (si pytest-xdist installé)
pytest -n auto
```

### Vérifier la qualité du code
```powershell
# Si vous installez pylint
pip install pylint
pylint archiver.py watcher.py generator.py

# Si vous installez black (formatter)
pip install black
black --check .
```

## 🗄️ MongoDB - Commandes utiles

### Connexion et vérification
```powershell
# Tester la connexion MongoDB (dans mongo shell)
# mongo "mongodb+srv://your-uri"

# Ou avec Python
python -c "from pymongo import MongoClient; from config import Config; c = Config.from_env(); client = MongoClient(c.mongodb_uri); print('Connected:', client.server_info()['version'])"
```

### Statistiques MongoDB (dans mongo shell ou Compass)
```javascript
// Dans mongo shell
use Ubereats

// Compter les commandes par statut
db.Commande.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

// Dernières commandes archivées
db.Historique.find().sort({ date_archivage: -1 }).limit(10)

// Statistiques journalières
db.Historique.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$date_archivage" } },
      count: { $sum: 1 },
      total: { $sum: "$coût_commande" }
    }
  },
  { $sort: { _id: -1 } },
  { $limit: 7 }
])

// Index existants
db.Historique.getIndexes()
```

## 🔄 Maintenance

### Rotation des logs
```powershell
# Archiver les logs de plus de 30 jours
$cutoffDate = (Get-Date).AddDays(-30)
Get-ChildItem logs\*.log | Where-Object { $_.LastWriteTime -lt $cutoffDate } | ForEach-Object {
    Compress-Archive -Path $_.FullName -DestinationPath "logs\archive\$($_.Name).zip"
    Remove-Item $_.FullName
}
```

### Nettoyage
```powershell
# Supprimer les logs de test
Remove-Item logs\*_test_*.log

# Supprimer les fichiers Python compilés
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse

# Nettoyer les samples
Remove-Item *.sample.json
```

### Backup du resume token
```powershell
# Sauvegarder le resume token
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item .resume_token.json "backups\resume_token_$date.json"
```

## 🚀 Déploiement

### Créer un service Windows avec NSSM
```powershell
# Télécharger NSSM depuis https://nssm.cc/download

# Installer le service
.\nssm.exe install MongoDBArchiver "C:\Users\PC\mongodb_archiver\venv\Scripts\python.exe" "main.py watch"
.\nssm.exe set MongoDBArchiver AppDirectory "C:\Users\PC\mongodb_archiver"
.\nssm.exe set MongoDBArchiver AppEnvironmentExtra "MONGODB_URI=your_uri_here"
.\nssm.exe set MongoDBArchiver DisplayName "MongoDB Order Archiver"
.\nssm.exe set MongoDBArchiver Description "Automatic order archiving with Change Streams"
.\nssm.exe set MongoDBArchiver Start SERVICE_AUTO_START

# Démarrer le service
.\nssm.exe start MongoDBArchiver

# Vérifier l'état
.\nssm.exe status MongoDBArchiver

# Arrêter le service
.\nssm.exe stop MongoDBArchiver

# Désinstaller le service
.\nssm.exe remove MongoDBArchiver confirm
```

### Tâche planifiée Windows
```powershell
# Créer une tâche pour archivage quotidien
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "main.py batch --run" -WorkingDirectory "C:\Users\PC\mongodb_archiver"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "MongoDBArchiver-Daily" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Archive MongoDB orders daily"

# Lister les tâches
Get-ScheduledTask -TaskName "MongoDBArchiver*"

# Désactiver la tâche
Disable-ScheduledTask -TaskName "MongoDBArchiver-Daily"

# Supprimer la tâche
Unregister-ScheduledTask -TaskName "MongoDBArchiver-Daily" -Confirm:$false
```

## 📊 Reporting

### Générer un rapport quotidien
```powershell
# Script de rapport
function New-DailyReport {
    $date = Get-Date -Format "yyyy-MM-dd"
    $reportPath = "reports\report_$date.txt"
    
    $report = @"
MongoDB Order Archiver - Daily Report
Date: $date
=====================================

"@
    
    # Stats from latest log
    $latestLog = Get-ChildItem logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestLog) {
        $report += Get-Content $latestLog -Tail 20
    }
    
    # Save report
    New-Item -ItemType Directory -Path reports -Force | Out-Null
    $report | Out-File $reportPath
    
    Write-Host "Report generated: $reportPath"
}

# Utiliser
New-DailyReport
```

### Export des statistiques
```powershell
# Exporter les statistiques en CSV
function Export-ArchiverStats {
    $logs = Get-ChildItem logs\batch_*.log
    
    $stats = foreach ($log in $logs) {
        $content = Get-Content $log -Raw
        
        if ($content -match "Found:\s+(\d+).*Archived:\s+(\d+).*Errors:\s+(\d+)") {
            [PSCustomObject]@{
                Date = $log.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
                Found = $matches[1]
                Archived = $matches[2]
                Errors = $matches[3]
            }
        }
    }
    
    $stats | Export-Csv stats.csv -NoTypeInformation
    Write-Host "Stats exported to stats.csv"
}

# Utiliser
Export-ArchiverStats
```

## 🔐 Sécurité

### Vérifier les permissions du fichier .env
```powershell
# Voir les ACL du fichier .env
Get-Acl .env | Format-List

# Restreindre les permissions (utilisateur courant seulement)
$acl = Get-Acl .env
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl .env $acl
```

### Tester la connexion sans exposer l'URI
```powershell
# Test de connexion sécurisé
python -c "from config import Config; c = Config.from_env(); print('✅ Config loaded successfully')"
```

## 📦 Backup & Restore

### Backup complet
```powershell
# Créer un backup du projet
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "..\backups\mongodb_archiver_$date"

# Copier les fichiers essentiels
Copy-Item -Path @(
    "*.py",
    "*.txt",
    "*.md",
    "*.toml",
    ".env",
    "logs",
    ".resume_token.json"
) -Destination $backupPath -Recurse -Force

Compress-Archive -Path $backupPath -DestinationPath "$backupPath.zip"
Remove-Item $backupPath -Recurse

Write-Host "Backup created: $backupPath.zip"
```

## 🆘 Dépannage

### Redémarrage forcé du watcher
```powershell
# Arrêter tous les processus Python qui tournent
Get-Process python | Where-Object {$_.Path -like "*mongodb_archiver*"} | Stop-Process -Force

# Supprimer le resume token (redémarre from scratch)
Remove-Item .resume_token.json -ErrorAction SilentlyContinue

# Redémarrer
python main.py watch
```

### Vérifier l'environnement
```powershell
# Script de diagnostic
function Test-ArchiverEnvironment {
    Write-Host "🔍 Checking environment..." -ForegroundColor Cyan
    
    # Python version
    $pythonVersion = python --version
    Write-Host "✓ Python: $pythonVersion"
    
    # Virtual env
    if ($env:VIRTUAL_ENV) {
        Write-Host "✓ Virtual environment: Active"
    } else {
        Write-Host "⚠ Virtual environment: Not active" -ForegroundColor Yellow
    }
    
    # .env file
    if (Test-Path .env) {
        Write-Host "✓ .env file: Exists"
    } else {
        Write-Host "✗ .env file: Missing" -ForegroundColor Red
    }
    
    # Dependencies
    $deps = @("pymongo", "python-dotenv", "faker")
    foreach ($dep in $deps) {
        $installed = pip show $dep 2>$null
        if ($installed) {
            Write-Host "✓ $dep: Installed"
        } else {
            Write-Host "✗ $dep: Not installed" -ForegroundColor Red
        }
    }
    
    Write-Host "`n✅ Diagnostic complete"
}

# Utiliser
Test-ArchiverEnvironment
```

## 📞 Aliases utiles

```powershell
# Ajouter à votre profil PowerShell ($PROFILE)

# Aliases
Set-Alias -Name archive-batch -Value { python main.py batch --run }
Set-Alias -Name archive-watch -Value { python main.py watch }
Set-Alias -Name archive-demo -Value { python demo.py }

# Functions
function archive-dry { python main.py batch --dry-run --verbose }
function archive-logs { Get-Content logs\*.log -Wait -Tail 50 }
function archive-stats { Get-Content logs\*.log | Select-String "STATISTICS" -Context 0,10 }
```

---

💡 **Tip** : Sauvegardez ces scripts dans un fichier `scripts.ps1` pour référence rapide !
